#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
WorkBuddy 每日积分自动签到 —— 青龙面板版 (纯标准库, 无第三方依赖, 支持多账号)
================================================================================
部署到青龙面板的步骤:
  1) 把本文件上传到青龙的 scripts 目录
  2) 环境变量:WORKBUDDY:
     格式:ACCESS_TOKEN#UID#备注
	   多账号用换行隔开, 例如:
	   eyJxxx.aaa.bbb#u_123456#主号
	   eyJyyy.ccc.ddd#u_654321#小号A
	   eyJzzz.eee.fff#u_111222#小号B

     (ACCESS_TOKEN / UID 在 Windows 本机文件里:
      %LOCALAPPDATA%\CodeBuddyExtension\Data\Public\auth\workbuddy-desktop.info
      的 auth.accessToken 与 account.uid)
  3) 在"定时任务"里新建, 命令填本脚本路径, 定时规则例如: 30 9 * * *


说明:
  - accessToken 是 JWT, 约 60 天有效; 过期后对应账号会报 401, 重新粘贴最新值到
    WORKBUDDY 对应行即可。
  - 签到接口是幂等的(重复跑不重复发), 多账号挂上去不用担心。
"""

import json
import os
import sys
import base64
import datetime
import logging
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# 青龙环境变量名(在面板"环境变量"里设置)
ENV_MULTI = "WORKBUDDY"                 # 多账号: 每行 ACCESS_TOKEN#UID#备注
ENV_TOKEN = "WORKBUDDY_ACCESS_TOKEN"    # 旧单账号兜底
ENV_UID = "WORKBUDDY_UID"               # 旧单账号兜底
ENV_WXPUSHER_TOKEN = "WXPUSHER_APP_TOKEN"
ENV_WXPUSHER_UID = "WXPUSHER_UID"

WXPUSHER_API = "https://wxpusher.zjiecode.com/api/send/message"

# ---------- 日志: 输出到 stdout(青龙会捕获) ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("wb-checkin")


def token_file_candidates():
    env = os.environ
    return [c for c in [
        os.path.join(env.get("LOCALAPPDATA", ""), "CodeBuddyExtension", "Data", "Public", "auth", "workbuddy-desktop.info"),
        os.path.join(env.get("APPDATA", ""), "CodeBuddyExtension", "Data", "Public", "auth", "workbuddy-desktop.info"),
        os.path.expanduser("~/Library/Application Support/CodeBuddyExtension/Data/Public/auth/workbuddy-desktop.info"),
        os.path.expanduser("~/.config/CodeBuddyExtension/Data/Public/auth/workbuddy-desktop.info"),
    ] if c]


ENDPOINT_CHECKIN = "https://copilot.tencent.com/v2/billing/meter/daily-checkin"
ENDPOINT_RESOURCE = "https://copilot.tencent.com/v2/billing/meter/get-user-resource"
RESOURCE_BODY = {"PageNumber": 1, "PageSize": 100, "ProductCode": "p_tcaca", "Status": [0, 3], "OnlyValidPeriod": True}


def parse_account_line(line):
    """解析单行: ACCESS_TOKEN#UID#备注 -> dict。备注可省略, 可含 '#'。"""
    line = (line or "").strip()
    if not line:
        return None
    parts = line.split("#")
    token = parts[0].strip()
    uid = parts[1].strip() if len(parts) > 1 else ""
    remark = "#".join(parts[2:]).strip() if len(parts) > 2 else ""
    if not token or not uid:
        return None
    return {"token": token, "uid": uid, "remark": remark or "(未备注)"}


def load_accounts():
    """优先级: WORKBUDDY 多账号 > 旧单账号环境变量 > 本机文件。返回账号列表。"""
    raw = (os.environ.get(ENV_MULTI) or "").strip()
    accounts = []
    if raw:
        for line in raw.splitlines():
            acc = parse_account_line(line)
            if acc:
                acc["src"] = "<env:%s>" % ENV_MULTI
                accounts.append(acc)
    if accounts:
        return accounts

    # 兜底 1: 旧单账号环境变量
    token = (os.environ.get(ENV_TOKEN) or "").strip()
    uid = (os.environ.get(ENV_UID) or "").strip()
    if token and uid:
        return [{"token": token, "uid": uid, "remark": "(env单账号)", "src": "<env:%s>" % ENV_TOKEN}]

    # 兜底 2: 本机文件(单账号)
    for p in token_file_candidates():
        if not (p and os.path.isfile(p)):
            continue
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            auth = data.get("auth", {}) or {}
            t = auth.get("accessToken")
            u = (data.get("account", {}) or {}).get("uid")
            if t and u:
                return [{"token": t, "uid": u, "remark": "(本机文件)", "src": p}]
        except Exception as e:
            log.warning("读取令牌文件失败 %s: %s", p, e)
    return []


def decode_exp(token):
    """从 JWT 解析 exp 字段, 失败返回 None。"""
    try:
        part = token.split(".")[1]
        part += "=" * (-len(part) % 4)
        payload = json.loads(base64.urlsafe_b64decode(part).decode("utf-8", "replace"))
        return payload.get("exp")
    except Exception:
        return None


def wxpusher_send(title, content, log_cb=None):
    app_token = (os.environ.get(ENV_WXPUSHER_TOKEN) or "").strip()
    uid = (os.environ.get(ENV_WXPUSHER_UID) or "").strip()
    if not app_token or not uid:
        if log_cb:
            log_cb("WxPusher 未配置(无 %s/%s 环境变量), 跳过" % (ENV_WXPUSHER_TOKEN, ENV_WXPUSHER_UID))
        return False
    try:
        html = content.replace("\n", "<br>")
        payload = {
            "appToken": app_token,
            "uids": [uid],
            "topicIds": [],
            "summary": title,
            "content": html,
            "contentType": 1,
            "verifyPay": False,
        }
        req = Request(WXPUSHER_API, data=json.dumps(payload).encode("utf-8"),
                      headers={"Content-Type": "application/json;charset=utf-8"}, method="POST")
        with urlopen(req, timeout=10) as resp:
            rj = json.loads(resp.read().decode("utf-8", "replace"))
        if rj.get("code") == 1000:
            if log_cb:
                log_cb("WxPusher 通知发送成功")
            return True
        if log_cb:
            log_cb("WxPusher 返回异常: %s" % rj.get("msg"))
        return False
    except Exception as e:
        if log_cb:
            log_cb("WxPusher 通知失败: %s" % e)
        return False


def ql_notify(title, content):
    """优先用青龙面板内置默认通知(sendNotify / notify.py), 失败则回退 WxPusher。"""
    notified = False

    # 1) 青龙默认通知模块 sendNotify(底层 sendNotify.js)
    if not notified:
        try:
            from sendNotify import sendNotify as _SN
            try:
                _SN().send(title, content)
            except Exception:
                _SN.send(title, content)
            notified = True
        except Exception:
            pass

    # 2) 青龙默认通知模块 notify.py
    if not notified:
        try:
            from notify import send_notify
            send_notify(title, content)
            notified = True
        except Exception:
            pass
    if not notified:
        try:
            from notify import send
            send(title, content)
            notified = True
        except Exception:
            pass

    # 3) 兜底 WxPusher
    if not notified:
        wxpusher_send(title, content, log_cb=lambda m: log.info("[通知] %s", m))
    else:
        log.info("[通知] 已通过青龙内置推送")


def post_json(url, token, uid, body_obj=None):
    data = b"{}" if body_obj is None else json.dumps(body_obj).encode("utf-8")
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "X-User-Id": uid,
        "User-Agent": "WorkBuddyCheckin/1.4-ql",
    }
    req = Request(url, data=data, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=25) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except URLError as e:
        return 0, "URLError: %s" % e


def parse_result(status, body):
    code = None
    msg = ""
    awarded = None
    streak = None
    try:
        obj = json.loads(body)
        code = obj.get("code")
        msg = obj.get("msg") or obj.get("message") or ""
        data = obj.get("data") or {}
        if isinstance(data, dict):
            if data.get("credit") is not None:
                try:
                    awarded = int(data.get("credit"))
                except Exception:
                    awarded = None
            if data.get("streak_days") is not None:
                try:
                    streak = int(data.get("streak_days"))
                except Exception:
                    streak = None
    except Exception:
        pass

    if status == 200 and code in (0, None):
        extra = (" (连续 %d 天)" % streak) if streak is not None else ""
        return True, False, "签到成功" + extra + ((" | " + msg) if msg else ""), awarded, streak
    if code == 10001 or ("已签到" in body) or ("already" in body.lower()):
        return True, True, "今日已签到(幂等命中)" + ((" | code=%s" % code) if code is not None else ""), 0, streak
    if status == 401:
        return False, False, "令牌失效(401), 请在青龙环境变量 %s 对应行更新令牌" % ENV_MULTI, None, None
    return False, False, "签到失败 status=%s code=%s msg=%s" % (status, code, msg), None, None


def query_balance(token, uid):
    status, body = post_json(ENDPOINT_RESOURCE, token, uid, RESOURCE_BODY)
    if status != 200:
        return None, None
    try:
        obj = json.loads(body)
        accts = (obj.get("data", {}) or {}).get("Response", {}) or {}
        accts = (accts.get("Data", {}) or {}).get("Accounts", []) or []
        total = 0.0
        for a in accts:
            v = a.get("CycleCapacityRemainPrecise")
            if v is None:
                v = a.get("CycleCapacityRemain")
            if v is None:
                v = a.get("CapacityRemainPrecise")
            if v is None:
                v = a.get("CapacityRemain")
            try:
                total += float(v)
            except (TypeError, ValueError):
                pass
        return int(round(total)), obj
    except Exception:
        return None, None


def fmt_credits(v):
    return "—" if v is None else str(v)


def run_account(acc, dry):
    """处理单个账号, 返回汇总字典(含备注与积分信息)。"""
    remark = acc["remark"]
    token = acc["token"]
    uid = acc["uid"]
    src = acc["src"]

    exp = decode_exp(token)
    if exp:
        remain = datetime.datetime.fromtimestamp(exp) - datetime.datetime.now()
        log.info("账号[%s] 已加载登录态(来源 %s, uid=%s, 令牌剩余 ~%s)", remark, src, uid, remain)
    else:
        log.info("账号[%s] 已加载登录态(来源 %s, uid=%s)", remark, src, uid)

    if dry:
        log.info("账号[%s] [dry-run] 跳过实际请求", remark)
        return {"remark": remark, "ok": None, "dry": True,
                "msg": "[dry-run] 未执行", "before": None, "after": None, "gained": None}

    before, _ = query_balance(token, uid)
    if before is None:
        log.warning("账号[%s] 签到前总积分查询失败(接口无响应), 仍继续执行签到", remark)
    else:
        log.info("账号[%s] 签到前总积分: %s", remark, fmt_credits(before))

    status, body = post_json(ENDPOINT_CHECKIN, token, uid)
    ok, already, msg, awarded, streak = parse_result(status, body)
    log.info("账号[%s] 签到接口返回: %s", remark, msg)

    after, _ = query_balance(token, uid)
    if after is None:
        log.warning("账号[%s] 签到后总积分查询失败(接口无响应)", remark)
    else:
        log.info("账号[%s] 签到后总积分: %s", remark, fmt_credits(after))

    if awarded is not None:
        gained = awarded
    elif before is not None and after is not None:
        gained = after - before
    else:
        gained = None

    if ok:
        log.info("账号[%s] ✅ %s", remark, msg)
    else:
        log.error("账号[%s] ❌ %s | 响应: %s", remark, msg, body[:300])

    return {"remark": remark, "ok": ok, "dry": False, "msg": msg,
            "before": before, "after": after, "gained": gained}


def main():
    dry = "--dry-run" in sys.argv
    no_notify = "--no-notify" in sys.argv
    accounts = load_accounts()
    if not accounts:
        log.error("未找到任何登录态: 请在青龙环境变量设置 %s (每行 ACCESS_TOKEN#UID#备注), "
                  "或设置旧变量 %s/%s, 或确保本机 workbuddy-desktop.info 存在。",
                  ENV_MULTI, ENV_TOKEN, ENV_UID)
        return 2

    log.info("共加载 %d 个账号, 开始签到%s", len(accounts), " [dry-run]" if dry else "")
    results = [run_account(acc, dry) for acc in accounts]

    # 汇总
    ok_count = sum(1 for r in results if r.get("ok") is True)
    fail_count = sum(1 for r in results if r.get("ok") is False)
    dry_count = sum(1 for r in results if r.get("dry"))

    date_str = datetime.date.today().strftime("%Y-%m-%d")
    if dry:
        title = "WorkBuddy 签到 [dry-run]"
    elif fail_count == 0:
        title = "WorkBuddy 签到 全部成功 (%d/%d)" % (ok_count, len(results))
    else:
        title = "WorkBuddy 签到 %d成功 %d失败" % (ok_count, fail_count)

    lines = ["📅 %s 每日签到 (共 %d 个账号)" % (date_str, len(results)), "─" * 28]
    for r in results:
        remark = r["remark"]
        lines.append("【%s】" % remark)
        if r.get("dry"):
            lines.append("  结果: %s" % r["msg"])
            continue
        lines.append("  结果: %s" % ("✅ " + r["msg"] if r["ok"] else "❌ " + r["msg"]))
        lines.append("  总积分(签到前→后): %s → %s" % (fmt_credits(r["before"]), fmt_credits(r["after"])))
        gained = r["gained"]
        if gained is not None:
            lines.append("  本次获得: %s" % ("0 (今日已签到/无增量)" if gained == 0 else "+%d" % gained))
        if not r["ok"]:
            lines.append("  状态: 失败, 请检查该账号令牌是否有效")
    content = "\n".join(lines)
    log.info("已生成通知内容(%d 个账号)", len(results))

    if not no_notify:
        ql_notify(title, content)
    else:
        log.info("已指定 --no-notify, 跳过推送")

    # 退出码: 有真实失败则非 0(仅 dry-run 视为成功)
    if dry:
        return 0
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
