"""
OPPO/OnePlus 云服务 - 青龙面板自动化脚本 (Python3)
功能：自动查询任务列表、上报事件、领取奖励

==============================================
  使用说明 - 抓包参数直接填入
==============================================

本脚本支持直接从抓包数据提取参数填入使用，无需逆向签名算法。

1. 在青龙面板 -> 环境变量 中添加以下变量：

   【必填】OCLOUD_TOKEN
   值: 从抓包中获取的完整 token（格式如 TOKEN_eyJhbG...）
   多账号用 @ 分隔

   【必填】OCLOUD_SIGN
   值: 从抓包中获取的 sign 值（32位MD5字符串）
   多账号用 @ 分隔（每个账号对应一个 sign）

   【可选】OCLOUD_TIMESTAMP
   值: 从抓包中获取的 timestamp（13位时间戳）
   多账号用 @ 分隔
   如果不填，脚本会自动生成当前时间戳

   【可选】OCLOUD_NONCE
   值: 从抓包中获取的 nonce（通常和 timestamp 相同）
   多账号用 @ 分隔
   如果不填，使用 timestamp 的值

   【可选】OCLOUD_GUID / OCLOUD_DUID / OCLOUD_OUID
   值: 设备标识信息
   多账号用 @ 分隔

2. 如何获取参数：
   - 打开 HAR 文件，找到 query-home 或 grant-award 请求
   - 查看 POST body，复制 token、sign、timestamp、nonce 字段
   - 填入对应的环境变量

3. cron 建议: 0 8-22/2 * * *  (每天8点到22点，每2小时执行)

==============================================
  注意事项
==============================================

⚠️ 抓包获取的 sign 可能有有效期限制，如果脚本运行失败提示签名错误，
   需要重新抓包获取最新的 sign。

⚠️ 建议每次运行前都使用新鲜的抓包数据，确保 sign 未过期。
"""

import os
import sys
import json
import time
import random
import requests

# ==================== 配置区 ====================

BASE_URL = "https://static-cn01a.ocloud.heytapmobi.com"
API_PATH = "/cloudtask-api/api-cloud/task-wall/v1"

APP_KEY = "C5TcyDg1kGBm4o5R1JJ7rh"
ENTER_ID = 100042
VERSION_CODE = "101107"
VERSION_NAME = "10.11.07"
SOURCE = (
    "banner_renwu_ug_12437*11445*0*0*21732*0*"
    "299ac60ffb424ddc8a8bc4002046cb39*103*0*0*0*0*ZTID_S_1p1cpVLXYyn"
)

# 默认设备信息（从抓包中提取）
DEFAULT_GUID = "847d7d1c3e073c6549fc30d061fa50e9e19200a7387ab298ef09d53a961d0f73"
DEFAULT_DUID = "00B8ECEF49FE4B0D98C7E5F637F948D6EC7D424979CC9C51E210D8DA708841B2"
DEFAULT_OUID = "6ECCF904D2F04A3AAAFCCECBB602A1502d9429949c5f20e5b6814889070682ba"

USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 15; PKG110 Build/UKQ1.231108.001; wv) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/147.0.7727.111 "
    "Mobile Safari/537.36 cloud/10.11.7_5c2e16b_260331 isGesture/true"
)

REFERER_URL = (
    "https://static-cn01a.ocloud.heytapmobi.com/profit/index.html"
    "?OCLOUD-LANG=zh-CN&pageStyle=3"
    f"&source={SOURCE}"
    "&BRAND-SHOW-TYPE=2&OCLOUD-BRAND=OnePlus&OCLOUD-LANG=zh-CN"
    "&OCLOUD-LANGTAG=zh-CN&enter_id=2&OCLOUD-SYSTEM-OS=2"
    "&OCLOUD-EXP=false&statics=true&OCLOUD-THEME-STYLE=2&FLEXIBLE-WINDOW=false"
)

NOTIFY_TITLE = "☁️ OPPO云服务任务"


# ==================== 工具函数 ====================

def parse_multi_env(env_name, default_val=""):
    """解析多账号环境变量，支持 @ 或换行分隔"""
    val = os.environ.get(env_name, default_val)
    if not val:
        return []
    val = val.replace("@", "\n")
    return [v.strip() for v in val.split("\n") if v.strip()]


def get_accounts():
    """
    从环境变量获取账号列表
    支持直接从抓包填入 token、sign、timestamp、nonce
    """
    tokens = parse_multi_env("OCLOUD_TOKEN")
    if not tokens:
        return []

    # 获取其他参数（多账号用 @ 分隔）
    signs = parse_multi_env("OCLOUD_SIGN")
    timestamps = parse_multi_env("OCLOUD_TIMESTAMP")
    nonces = parse_multi_env("OCLOUD_NONCE")
    guids = parse_multi_env("OCLOUD_GUID", DEFAULT_GUID)
    duids = parse_multi_env("OCLOUD_DUID", DEFAULT_DUID)
    ouids = parse_multi_env("OCLOUD_OUID", DEFAULT_OUID)

    accounts = []
    for i, token in enumerate(tokens):
        # 获取对应账号的参数，如果没有则使用第一个或默认值
        sign = signs[i] if i < len(signs) else (signs[0] if signs else "")
        ts = timestamps[i] if i < len(timestamps) else ""
        nonce = nonces[i] if i < len(nonces) else ""
        guid = guids[i] if i < len(guids) else (guids[0] if guids else DEFAULT_GUID)
        duid = duids[i] if i < len(duids) else (duids[0] if duids else DEFAULT_DUID)
        ouid = ouids[i] if i < len(ouids) else (ouids[0] if ouids else DEFAULT_OUID)

        accounts.append({
            "token": token,
            "sign": sign,
            "timestamp": ts,
            "nonce": nonce,
            "guid": guid,
            "duid": duid,
            "ouid": ouid,
        })

    return accounts


def build_headers(account, timestamp):
    """构建请求头（模拟 Android WebView）"""
    guid = account["guid"]
    duid = account["duid"]
    ouid = account["ouid"]
    token = account["token"]

    return {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh_CN",
        "brand": "OnePlus",
        "content-type": "application/json; charset=UTF-8",
        "guid": guid,
        "imei": "",
        "ocloud-brand": "OnePlus",
        "ocloud-build-model": "PKG110",
        "ocloud-coloros": "V15.0.2",
        "ocloud-duid": duid,
        "ocloud-gray": "",
        "ocloud-guid": guid,
        "ocloud-imei": f"OPENID-{guid}-0",
        "ocloud-langtag": "zh-CN",
        "ocloud-location": "zh_CN",
        "ocloud-model": "",
        "ocloud-ouid": ouid,
        "ocloud-package-name": "com.heytap.cloud",
        "ocloud-region-mark": "CN",
        "ocloud-registration-id": "",
        "ocloud-timestamp": str(timestamp),
        "ocloud-token": token,
        "ocloud-version": VERSION_CODE,
        "openid": guid,
        "origin": BASE_URL,
        "packagename": "com.heytap.cloud",
        "referer": REFERER_URL,
        "sec-ch-ua": '"Android WebView";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": USER_AGENT,
        "x-businesssystem": "OnePlus",
        "x-client-guid": guid,
        "x-client-imei": "",
        "x-device": "eyJtb2RlbCI6IlBLRzExMCIsImJyYW5kIjoiT25lUGx1cyJ9",
        "x-requested-with": "com.heytap.cloud",
    }


def build_base_body(account):
    """
    构建基础请求体
    优先使用抓包填入的 timestamp、nonce、sign
    如果没有则自动生成
    """
    # 使用抓包的 timestamp，如果没有则生成当前时间戳
    if account.get("timestamp"):
        ts = int(account["timestamp"])
    else:
        ts = int(time.time() * 1000)

    # 使用抓包的 nonce，如果没有则使用 timestamp
    if account.get("nonce"):
        nonce = account["nonce"]
    else:
        nonce = str(ts)

    # 使用抓包的 sign
    sign = account.get("sign", "")

    return {
        "appKey": APP_KEY,
        "nonce": nonce,
        "timestamp": ts,
        "token": account["token"],
        "sign": sign,
    }


# ==================== API 接口 ====================

def api_query_home(session, headers, account):
    """查询任务首页"""
    url = f"{BASE_URL}{API_PATH}/query-home"
    body = build_base_body(account)
    body.update({
        "enterId": ENTER_ID,
        "singleAppDownSource": "downloadtask",
        "versionCode": VERSION_CODE,
        "versionName": VERSION_NAME,
        "source": SOURCE,
    })

    try:
        resp = session.post(url, headers=headers, json=body, timeout=30)
        data = resp.json()
        if data.get("success"):
            return data.get("data", {})
        else:
            err = data.get('error', '未知错误')
            print(f"  ❌ 查询失败: {err}")
            # 如果是签名错误，提示用户
            if "sign" in str(err).lower():
                print(f"  💡 提示: sign 可能已过期，请重新抓包获取最新 sign")
            return None
    except Exception as e:
        print(f"  ❌ 请求异常: {e}")
        return None


def api_report_event(session, headers, account, task_id, resource_info_list):
    """上报任务完成事件"""
    url = f"{BASE_URL}{API_PATH}/report-event"
    body = build_base_body(account)
    body.update({
        "taskId": task_id,
        "eventId": "FINISH_EVENT",
        "resourceInfoList": json.dumps(resource_info_list, ensure_ascii=False),
    })

    try:
        resp = session.post(url, headers=headers, json=body, timeout=30)
        data = resp.json()
        if data.get("success"):
            return data.get("data", {})
        else:
            err = data.get('error', '未知错误')
            print(f"  ❌ 上报失败: {err}")
            if "sign" in str(err).lower():
                print(f"  💡 提示: sign 可能已过期")
            return None
    except Exception as e:
        print(f"  ❌ 请求异常: {e}")
        return None


def api_grant_award(session, headers, account, task_id, task_record_id):
    """领取任务奖励"""
    url = f"{BASE_URL}{API_PATH}/grant-award"
    body = build_base_body(account)
    body.update({
        "taskId": str(task_id),
        "taskRecordId": str(task_record_id),
    })

    try:
        resp = session.post(url, headers=headers, json=body, timeout=30)
        data = resp.json()
        if data.get("success"):
            return data.get("data", {})
        else:
            err = data.get('error', '未知错误')
            print(f"  ❌ 领取失败: {err}")
            if "sign" in str(err).lower():
                print(f"  💡 提示: sign 可能已过期")
            return None
    except Exception as e:
        print(f"  ❌ 请求异常: {e}")
        return None


# ==================== 通知 ====================

def notify(title, content):
    """发送通知（兼容青龙面板）"""
    try:
        from notify import send
        send(title, content)
        return
    except ImportError:
        pass
    print(f"\n📢 [{title}] {content}")


# ==================== 核心逻辑 ====================

def run_account(account, index):
    """执行单个账号的任务流程"""
    token_preview = account["token"][:30] + "..." if len(account["token"]) > 30 else account["token"]
    sign_preview = account.get("sign", "")[:16] + "..." if len(account.get("sign", "")) > 16 else account.get("sign", "未设置")

    print(f"\n{'='*60}")
    print(f"📱 账号 {index} 开始执行")
    print(f"   Token: {token_preview}")
    print(f"   Sign: {sign_preview}")
    print(f"{'='*60}")

    # 检查 sign 是否设置
    if not account.get("sign"):
        print("⚠️ 警告: 未设置 OCLOUD_SIGN，请求可能会失败！")
        print("   请从抓包中获取 sign 值并填入环境变量")

    session = requests.Session()

    # 获取时间戳（用于 headers）
    if account.get("timestamp"):
        timestamp = int(account["timestamp"])
    else:
        timestamp = int(time.time() * 1000)

    headers = build_headers(account, timestamp)

    # 随机延迟
    time.sleep(random.uniform(1, 3))

    # ---- Step 1: 查询任务列表 ----
    print("\n📋 [Step 1] 查询任务列表...")
    home_data = api_query_home(session, headers, account)
    if not home_data:
        return f"账号{index}: 查询任务列表失败，token 可能已过期或 sign 错误"

    task_wall = home_data.get("taskWallData", {})
    task_infos = task_wall.get("taskInfos", [])
    award_info = home_data.get("awardInfo", [])

    print(f"  ✅ 获取到 {len(task_infos)} 个任务")

    # 显示可兑换奖励
    if award_info:
        print(f"\n  🎁 可兑换奖励:")
        for aw in award_info[:5]:
            print(f"    - {aw.get('awardName', '')}: "
                  f"{aw.get('amount', 0)} 碎片 ({aw.get('desc', '')})")

    # ---- Step 2: 遍历任务并执行 ----
    total_debris = 0
    success_count = 0
    skip_count = 0
    fail_count = 0
    details = []

    for task in task_infos:
        task_id = task.get("id")
        task_name = task.get("mainTitle", task.get("name", "未知"))
        task_type = task.get("taskType", "")
        task_status = task.get("taskStatus", "")

        # 计算奖励碎片数
        award_infos = task.get("awardInfos", [])
        debris = 0
        for a in award_infos:
            try:
                debris += int(a.get("amount", 0))
            except (ValueError, TypeError):
                pass

        print(f"\n  📌 任务[{task_id}] {task_name}")
        print(f"     类型: {task_type} | 状态: {task_status} | 奖励: {debris}碎片")

        # 跳过已完成的任务
        if task_status in ("COMPLETED", "RECEIVED", "FINISHED"):
            print(f"     ⏭️ 已完成，跳过")
            details.append(f"  ⏭️ {task_name}: 已完成")
            skip_count += 1
            continue

        # 获取可用资源
        task_feature = task.get("taskFeature", {})
        resource_list = task_feature.get("resourceInfoList", [])

        if not resource_list:
            print(f"     ⚠️ 无可用资源")
            details.append(f"  ⚠️ {task_name}: 无资源")
            skip_count += 1
            continue

        # 随机选择一个资源
        resource = random.choice(resource_list)
        res_id = resource.get("id", "")
        res_name = resource.get("name", "未知")
        res_type = resource.get("type", "")
        res_ext = resource.get("ext", {})

        print(f"     📦 资源: {res_name} (ID:{res_id})")

        # 构造 resourceInfoList
        resource_info = [{
            "id": str(res_id),
            "type": res_type,
            "name": res_name,
            "ext": res_ext,
        }]

        # ---- Step 2a: 上报完成事件 ----
        time.sleep(random.uniform(2, 5))
        print(f"     🔄 [Step 2] 上报完成事件...")

        report_result = api_report_event(
            session, headers, account, task_id, resource_info
        )

        if not report_result:
            details.append(f"  ❌ {task_name}: 上报失败")
            fail_count += 1
            continue

        action_status = report_result.get("taskActionStatus", "")
        record_id = report_result.get("taskRecordId", "")
        print(f"     ✅ 上报成功 | 状态: {action_status}")

        # ---- Step 2b: 领取奖励 ----
        if action_status == "WAIT_REWARD" and record_id:
            time.sleep(random.uniform(1, 3))
            print(f"     🎁 [Step 3] 领取奖励...")

            award_result = api_grant_award(
                session, headers, account, task_id, record_id
            )

            if award_result:
                coin = award_result.get("coinAmount", 0)
                total_debris += coin
                print(f"     ✅ 获得 {coin} 碎片!")
                details.append(f"  ✅ {task_name}: +{coin}碎片")
                success_count += 1
            else:
                details.append(f"  ❌ {task_name}: 领取失败")
                fail_count += 1
        else:
            print(f"     ℹ️ 状态: {action_status}，无需领取")
            details.append(f"  ℹ️ {task_name}: {action_status}")
            skip_count += 1

    # ---- 汇总 ----
    print(f"\n{'─'*60}")
    print(f"📊 账号{index} 执行汇总:")
    print(f"   总任务: {len(task_infos)}")
    print(f"   ✅ 成功: {success_count}")
    print(f"   ⏭️ 跳过: {skip_count}")
    print(f"   ❌ 失败: {fail_count}")
    print(f"   💎 本次获得碎片: {total_debris}")
    print(f"{'─'*60}")

    return (
        f"账号{index} 执行完成\n"
        f"总任务: {len(task_infos)} | 成功: {success_count} | "
        f"跳过: {skip_count} | 失败: {fail_count}\n"
        f"本次获得碎片: {total_debris}\n\n"
        + "\n".join(details)
    )


def main():
    """主入口"""
    print(f"\n{'='*60}")
    print(f"☁️ OPPO云服务自动化任务")
    print(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    accounts = get_accounts()
    if not accounts:
        msg = (
            "❌ 未配置 OCLOUD_TOKEN 环境变量！\n\n"
            "请在青龙面板 -> 环境变量中添加:\n"
            "  OCLOUD_TOKEN = 你的token（从抓包获取）\n"
            "  OCLOUD_SIGN = 你的sign（从抓包获取）\n\n"
            "多账号用 @ 分隔"
        )
        print(msg)
        notify(NOTIFY_TITLE, msg)
        sys.exit(1)

    print(f"🔑 检测到 {len(accounts)} 个账号")

    results = []
    for idx, acct in enumerate(accounts, 1):
        try:
            result = run_account(acct, idx)
            results.append(result)
        except Exception as e:
            err = f"账号{idx} 异常: {e}"
            print(f"❌ {err}")
            results.append(err)

        # 多账号间延迟
        if idx < len(accounts):
            delay = random.uniform(5, 10)
            print(f"\n⏳ 等待 {delay:.1f}s ...")
            time.sleep(delay)

    # 发送通知
    summary = f"共 {len(accounts)} 个账号执行完毕\n\n" + "\n\n".join(results)
    notify(NOTIFY_TITLE, summary)

    print(f"\n🎉 全部执行完毕！")


if __name__ == "__main__":
    main()
