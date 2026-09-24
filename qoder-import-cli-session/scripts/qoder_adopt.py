#!/usr/bin/env python3
"""把终端 qodercli 会话注册进 Qoder 桌面 App，让 App 从 JSONL 自己投影出对话。

子命令：
  status    只读：源会话、App 库、进程占用、能否安全动手
  adopt     备份 + 向 chat_sessions 插一行（唯一写操作）
  verify    只读：看 App 有没有投影出 source='cli-import' 的消息
  rollback  退出 App 后删掉这一行（CASCADE 清掉投影消息）

安全设计：adopt/rollback 要求 Qoder App 未运行且 main.sqlite 没有 -wal/-shm，
且源 transcript 不能被活着的进程写；不满足就中止，不提供 --force 绕过写库门槛。
"""

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

APP_SUPPORT_DEFAULT = os.path.expanduser("~/Library/Application Support/com.qoder.app.stable")
CONFIG_DIR_DEFAULT = os.path.expanduser(os.environ.get("QODER_CONFIG_DIR") or "~/.qoder")
APP_PROC_PATTERN = "Qoder.app/Contents/MacOS"
LIVE_WINDOW_SECONDS = 180  # transcript 在这个窗口内被改过就认为会话还活着


def die(msg, code=2):
    print(f"ABORT: {msg}", file=sys.stderr)
    sys.exit(code)


def ok(msg):
    print(f"  ok    {msg}")


def bad(msg):
    print(f"  FAIL  {msg}")


def pgrep(pattern):
    try:
        out = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
    except FileNotFoundError:
        return []
    return [p for p in out.stdout.split() if p]


def iso_to_ms(text):
    return int(datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp() * 1000)


class Target:
    """一次操作涉及的所有路径与源数据。"""

    def __init__(self, session_id, app_support, config_dir, cwd=None):
        self.session_id = session_id
        if not re.fullmatch(r"[0-9a-fA-F-]{36}", session_id):
            die(f"session-id 形状不对：{session_id}")
        self.app_support = Path(app_support)
        # 进程检查是为了保护真实 App 库；指向别的目录（fixture/沙箱）时不该被它挡住，否则没法测。
        self.live_store = self.app_support == Path(APP_SUPPORT_DEFAULT)
        self.db = self.app_support / "main.sqlite"
        self.config_dir = Path(config_dir)
        projects = self.config_dir / "projects"
        if not projects.is_dir():
            die(f"找不到 CLI transcript 根目录 {projects}")
        self.jsonl = None
        self.project_dir = None
        for candidate in sorted(projects.glob(f"*/{session_id}.jsonl")):
            if candidate.stat().st_size > 0:
                self.jsonl = candidate
                self.project_dir = candidate.parent
                break
        if self.jsonl is None:
            die(f"{projects} 下没有非空的 {session_id}.jsonl，这条会话不在这台机器上")
        state = self.project_dir / session_id / "state.json"
        self.state = json.loads(state.read_text()) if state.exists() else {}
        self.cwd = cwd or (self.state.get("workspaceDirectories") or [None])[0]
        if not self.cwd:
            die("无法确定 cwd（state.json 里没有 workspaceDirectories），请用 --cwd 指定")

    # ---- 源侧事实 -------------------------------------------------
    def mtime(self):
        return self.jsonl.stat().st_mtime

    def size(self):
        return self.jsonl.stat().st_size

    def title(self):
        """优先用 CLI 自己写过的标题记录，省得 App 起 runtime 再回写。"""
        found = None
        with self.jsonl.open(errors="replace") as fh:
            for line in fh:
                if '"ai-title"' not in line and '"custom-title"' not in line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("type") in ("ai-title", "custom-title"):
                    found = rec.get("customTitle") or rec.get("aiTitle") or found
        return (found or "").strip() or None

    def stamps(self):
        created = self.state.get("createdAt")
        updated = self.state.get("updatedAt")
        now_ms = int(time.time() * 1000)
        try:
            return (iso_to_ms(created), iso_to_ms(updated)) if created and updated else (now_ms, now_ms)
        except ValueError:
            return (now_ms, now_ms)

    # ---- App 侧事实 -----------------------------------------------
    def connect(self, read_only=False):
        if not self.db.exists():
            die(f"App 主库不存在：{self.db}")
        wal = Path(str(self.db) + "-wal")
        shm = Path(str(self.db) + "-shm")
        if read_only:
            # 有 -wal/-shm 说明别的连接活着，WAL 里可能有未 checkpoint 的新行 → 用 mode=ro 才看得见；
            # 两个文件都没有则是干净 checkpoint 状态，用 immutable=1 直读主文件，且不会自己造出 -shm/-wal。
            uri = f"file:{self.db}?mode=ro" if (wal.exists() or shm.exists()) else f"file:{self.db}?immutable=1"
            return sqlite3.connect(uri, uri=True)
        if wal.exists() or shm.exists():
            die("main.sqlite 旁边还有 -wal/-shm，说明有进程正连着库（多半是 App 没退干净）；先退出 App")
        if self.live_store and pgrep(APP_PROC_PATTERN):
            die(f"Qoder App 正在运行（pid {' '.join(pgrep(APP_PROC_PATTERN))}），先完全退出 App 再动手")
        return sqlite3.connect(self.db)

    def row(self, conn):
        cur = conn.execute("SELECT * FROM chat_sessions WHERE session_id=?", (self.session_id,))
        cols = [d[0] for d in cur.description]
        vals = cur.fetchone()
        return dict(zip(cols, vals)) if vals else None

    def template_row(self, conn):
        """同 cwd 的现成 local 行 —— 抄它的 workspace_id / execution_target_json。"""
        cur = conn.execute(
            """SELECT * FROM chat_sessions
                WHERE cwd=? AND deleted_at IS NULL AND archived=0
                  AND session_kind='standard' AND execution_kind='local'
                  AND session_id<>?
                ORDER BY updated_at DESC LIMIT 1""",
            (self.cwd, self.session_id),
        )
        cols = [d[0] for d in cur.description]
        vals = cur.fetchone()
        return dict(zip(cols, vals)) if vals else None

    def projected(self):
        conn = self.connect(read_only=True)
        try:
            msgs = conn.execute(
                "SELECT source, count(*) FROM chat_session_messages WHERE session_id=? GROUP BY 1",
                (self.session_id,),
            ).fetchall()
            segs = conn.execute(
                "SELECT count(*) FROM chat_session_search_segments WHERE session_id=?", (self.session_id,)
            ).fetchone()[0]
            rev = conn.execute(
                "SELECT revision FROM chat_session_history_revisions WHERE session_id=?", (self.session_id,)
            ).fetchone()
            row = self.row(conn)
        except sqlite3.OperationalError as exc:
            die(f"读库失败：{exc}")
        finally:
            conn.close()
        return {"messages": dict(msgs), "search_segments": segs, "revision": rev[0] if rev else None, "row": row}


def gate_write(t, extra_live_check=True):
    """写库前的硬门槛。返回 (conn, 模板行 session_id)。"""
    conn = t.connect()  # 内含 App 未运行 + 无 -wal/-shm 的检查
    try:
        existing = t.row(conn)
        if existing:
            die(f"chat_sessions 里已经有 {t.session_id} 了（title={existing.get('title')}），不重复插")
        template = t.template_row(conn)
        if template is None:
            conn.close()
            die(
                f"该 cwd（{t.cwd}）在 App 里没有任何现存会话，抄不到 workspace_id/execution_target_json；"
                "先在 App 里对这个目录开一条会话，再来 adopt"
            )
        if extra_live_check:
            age = time.time() - t.mtime()
            if age < LIVE_WINDOW_SECONDS:
                conn.close()
                die(f"transcript {int(age)}s 前还被写过，终端会话可能在跑；先退出它（确认无进程后再加 --assume-idle）")
            holders = pgrep(f"qodercli.*{t.session_id}")
            if holders:
                conn.close()
                die(f"有进程按 id resume 了这条会话（pid {' '.join(holders)}），先退出它")
        print(f"  gate    模板行 {template['session_id']}（workspace_id={template['workspace_id']}）")
        return conn, template["session_id"]
    except Exception:
        conn.close()
        raise


def backup(t):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    db_bak = Path(f"/tmp/qoder-main-backup-{stamp}.sqlite")
    jsonl_bak = Path(f"/tmp/{t.session_id}.jsonl.bak")
    shutil.copy2(t.db, db_bak)
    shutil.copy2(t.jsonl, jsonl_bak)
    check = sqlite3.connect(f"file:{db_bak}?mode=ro", uri=True)
    integrity = check.execute("pragma integrity_check").fetchone()[0]
    total = check.execute("select count(*) from chat_sessions").fetchone()[0]
    check.close()
    if integrity != "ok":
        die(f"备份完整性检查为 {integrity}，停止（备份留在 {db_bak}）")
    return {"db": str(db_bak), "db_sessions": total, "jsonl": str(jsonl_bak)}


COLUMNS = (
    "session_id", "origin_session_id", "session_kind", "conversation_mode", "product_mode",
    "title", "cwd", "execution_kind", "workspace_id", "git_branch", "model", "permission_mode",
    "additional_direcotries", "extra_json", "created_at", "updated_at", "execution_target_json",
    "archived", "unread", "deleted_at", "registration_json", "sidebar_custom_order", "owner_session_id",
)

SQL = f"""INSERT INTO chat_sessions ({", ".join(COLUMNS)})
SELECT ?, NULL, 'standard', 'normal', 'coding',
       ?, cwd, execution_kind, workspace_id, NULL, model, permission_mode,
       additional_direcotries, '{{"cliSessionReady":false}}', ?, ?, execution_target_json,
       0, 0, NULL, NULL, NULL, NULL
  FROM (SELECT * FROM chat_sessions WHERE session_id=?) AS t
 WHERE NOT EXISTS (SELECT 1 FROM chat_sessions WHERE session_id=?)"""


def cmd_status(t):
    print(f"session   {t.session_id}")
    print(f"jsonl     {t.jsonl}  ({t.size():,} B, mtime {datetime.fromtimestamp(t.mtime()):%Y-%m-%d %H:%M:%S})")
    created, updated = t.stamps()
    print(f"state     cwd={t.cwd} created={created} updated={updated} title={t.title()!r}")
    app = pgrep(APP_PROC_PATTERN)
    if t.live_store:
        (ok if not app else bad)(f"Qoder App {'未运行' if not app else '正在运行 pid=' + ','.join(app)}")
    else:
        print(f"  info    Qoder App {'在运行 pid=' + ','.join(app) if app else '未运行'}（进程检查只保护真实库，沙箱不拦）")
    wal = Path(str(t.db) + "-wal").exists() or Path(str(t.db) + "-shm").exists()
    (ok if not wal else bad)(f"main.sqlite {'无' if not wal else '仍有'} -wal/-shm")
    age = time.time() - t.mtime()
    (ok if age >= LIVE_WINDOW_SECONDS else bad)(f"transcript {int(age)}s 未修改（阈值 {LIVE_WINDOW_SECONDS}s）")
    holders = pgrep(f"qodercli.*{t.session_id}")
    (ok if not holders else bad)(f"没有进程按 id 持有该会话{'' if not holders else ' pid=' + ','.join(holders)}")
    conn = t.connect(read_only=True)
    try:
        row = t.row(conn)
        (bad if row else ok)("chat_sessions 已有该行（adopt 会拒绝）" if row else "chat_sessions 尚无该行")
        tpl = t.template_row(conn)
        (ok if tpl else bad)(f"同 cwd 模板行 {'有：' + tpl['session_id'] if tpl else '没有（adopt 会拒绝）'}")
        total = conn.execute("select count(*) from chat_sessions").fetchone()[0]
        print(f"db        {t.db}  chat_sessions={total}")
    finally:
        conn.close()


def cmd_adopt(t, title, assume_idle, do_backup):
    conn, template_id = gate_write(t, extra_live_check=not assume_idle)
    snap = backup(t) if do_backup else None
    if snap:
        print(f"  backup  {snap['db']}（{snap['db_sessions']} 行，integrity ok）")
        print(f"  backup  {snap['jsonl']}")
    created, updated = t.stamps()
    final_title = (title or t.title() or f"终端会话 {t.session_id[:8]}")[:120]
    try:
        conn.execute("BEGIN IMMEDIATE")
        cur = conn.execute(SQL, (t.session_id, final_title, created, updated, template_id, t.session_id))
        changed = cur.rowcount
        if changed != 1:
            conn.rollback()
            die(f"INSERT 影响 {changed} 行（要求恰好 1），已回滚，库未改动")
        conn.commit()
    finally:
        conn.close()
    print(f"  done    插入 1 行：title={final_title!r} created={created} updated={updated}")
    print("下一步：启动 Qoder App → 对应工作区侧栏应出现该会话 → 点开它触发投影 → 跑 verify")


def cmd_verify(t):
    info = t.projected()
    msgs = info["messages"]
    print(f"row           {'在' if info['row'] else '不在'} chat_sessions"
          + (f"  cliSessionReady={json.loads(info['row'].get('extra_json') or '{}').get('cliSessionReady')}" if info["row"] else ""))
    print(f"messages      {msgs or '（空）'}")
    print(f"search_segments {info['search_segments']}   history_revision {info['revision']}")
    imported = msgs.get("cli-import", 0)
    if imported > 0:
        ok(f"App 已投影 {imported} 条 cli-import 消息，迁移成功")
        return 0
    bad("还没有 cli-import 消息：要么还没在 App 里点开该会话，要么投影条件不止 hasMessages")
    print("提示：先在 App 侧栏点开这条会话，再重跑 verify；仍为 0 就跑 rollback")
    return 1


def cmd_rollback(t):
    # 回滚的门槛和 adopt 不同：只要求"没有别的进程连着库"，不要求模板行、也不因为"行存在"而拒绝
    conn = t.connect()
    try:
        row = t.row(conn)
        if not row:
            print("该行不存在，无需回滚")
            return 0
        conn.execute("BEGIN IMMEDIATE")
        for table in ("chat_session_messages", "chat_session_search_segments", "chat_sessions"):
            exists = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
            if exists:
                conn.execute(f"DELETE FROM {table} WHERE session_id=?", (t.session_id,))
        conn.commit()
    finally:
        conn.close()
    print(f"  done    已删 {t.session_id}：投影消息与检索片段一并删掉"
          "（SQLite 默认不启用外键，CASCADE 在命令行里不生效，所以显式删了三张表）")
    print("整库恢复（可选）：退出 App → rm main.sqlite-wal -shm → cp <备份文件> main.sqlite")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["status", "adopt", "verify", "rollback"])
    ap.add_argument("--session-id", required=True)
    ap.add_argument("--cwd", help="覆盖自动推断的 cwd")
    ap.add_argument("--title", help="侧栏标题，默认取 transcript 里最后一条 ai-title/custom-title")
    ap.add_argument("--app-support", default=os.environ.get("QODER_APP_SUPPORT", APP_SUPPORT_DEFAULT))
    ap.add_argument("--config-dir", default=os.environ.get("QODER_CONFIG_DIR_ROOT", CONFIG_DIR_DEFAULT))
    ap.add_argument("--assume-idle", action="store_true", help="跳过 transcript 新鲜度检查（仍需 App 未运行）")
    ap.add_argument("--no-backup", action="store_true", help="跳过备份（只建议在 fixture 测试时用）")
    args = ap.parse_args()

    t = Target(args.session_id, args.app_support, args.config_dir, args.cwd)
    if args.action == "status":
        return cmd_status(t) or 0
    if args.action == "adopt":
        return cmd_adopt(t, args.title, args.assume_idle, not args.no_backup) or 0
    if args.action == "verify":
        return cmd_verify(t)
    return cmd_rollback(t)


if __name__ == "__main__":
    sys.exit(main())
