"""
cron: 17 9 * * *
new Env('电信517换新礼不停');

"""
import os
import re
import sys
import ssl
import time
import json
import execjs
import base64
import random
import certifi
import asyncio
import datetime
import requests
import binascii
import httpx
import urllib.parse
import subprocess
from bs4 import BeautifulSoup, Tag
from http import cookiejar
from http.cookies import SimpleCookie
from functools import partial
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Cipher import DES3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
import random
def mask_phone(phone):
    if isinstance(phone, str) and len(phone) == 11:
        return f"{phone[:3]}****{phone[7:]}"
    return phone
def printn(m):
    current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{current_time}] {m}")

class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = (
        lambda self, *args, **kwargs: False
    )
    netscape = True
    rfc2965 = hide_cookie2 = False


context = ssl.create_default_context()
context.set_ciphers("DEFAULT@SECLEVEL=1")
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE


class DESAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)

requests.packages.urllib3.disable_warnings()
ss = requests.session()
ss.headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
    "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html",
}
ss.mount("https://", DESAdapter())
ss.cookies.set_policy(BlockAll())
key = b"1234567`90koiuyhgtfrdews"
iv = 8 * b"\0"

public_key_b64 = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----"""

public_key_data = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----"""

public_key_xbk = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIPOHtjs6p4sTlpFvrx+ESsYkEvyT4JB/dcEbU6C8+yclpcmWEvwZFymqlKQq89laSH4IxUsPJHKIOiYAMzNibhED1swzecH5XLKEAJclopJqoO95o8W63Euq6K+AKMzyZt1SEqtZ0mXsN8UPnuN/5aoB3kbPLYpfEwBbhto6yrwIDAQAB",
-----END PUBLIC KEY-----"""

jsCache = "Cache.js"
fileContent = ""

subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")


def get_first_three(value):
    if isinstance(value, (int, float)):
        return int(str(value)[:3])
    elif isinstance(value, str):
        return str(value)[:3]
    else:
        raise TypeError("error")

def encrypt(text):
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(text.encode(), DES3.block_size))
    return ciphertext.hex()

def decrypt(text):
    ciphertext = bytes.fromhex(text)
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), DES3.block_size)
    return plaintext.decode()

def b64(plaintext):
    public_key = RSA.import_key(public_key_b64)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return base64.b64encode(ciphertext).decode()

def encrypt_para(plaintext):
    if not isinstance(plaintext, str):
        plaintext = json.dumps(plaintext)
    public_key = RSA.import_key(public_key_data)
    cipher = PKCS1_v1_5.new(public_key)
    key_size = public_key.size_in_bytes()
    max_chunk_size = key_size - 11
    plaintext_bytes = plaintext.encode()
    ciphertext = b""
    for i in range(0, len(plaintext_bytes), max_chunk_size):
        chunk = plaintext_bytes[i : i + max_chunk_size]
        encrypted_chunk = cipher.encrypt(chunk)
        ciphertext += encrypted_chunk
    return binascii.hexlify(ciphertext).decode()

def encode_phone(text):
    encoded_chars = []
    for char in text:
        encoded_chars.append(chr(ord(char) + 2))
    return "".join(encoded_chars)

def xbkb64(plaintext):
    public_key = RSA.import_key(public_key_xbk)
    cipher = PKCS1_v1_5.new(public_key)
    key_size = public_key.size_in_bytes()
    max_chunk = key_size - 11
    ciphertext = b""
    for i in range(0, len(plaintext.encode()), max_chunk):
        chunk = plaintext.encode()[i : i + max_chunk]
        ciphertext += cipher.encrypt(chunk)
    return base64.b64encode(ciphertext).decode()

def aes_encrypt(data, key="34d7cb0bcdf07523"):
    if type(data) == dict:
        data = json.dumps(data)
    key_bytes = key.encode("utf-8")
    data_bytes = data.encode("utf-8")
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    ct_bytes = cipher.encrypt(pad(data_bytes, AES.block_size))
    return ct_bytes.hex()

def aes_ecb_encrypt(plaintext, key):
    # 确保密钥长度为16/24/32字节
    if len(key) not in [16, 24, 32]:
        raise ValueError("密钥长度必须为16/24/32字节")
    key_bytes = key.encode('utf-8') if isinstance(key, str) else key
    plaintext_bytes = plaintext.encode('utf-8') if isinstance(plaintext, str) else plaintext
    padded = pad(plaintext_bytes, AES.block_size)
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(encrypted).decode('utf-8')

def userLoginNormal(phone, password):
    alphabet = "abcdef0123456789"
    uuid = [
        "".join(random.sample(alphabet, 8)),
        "".join(random.sample(alphabet, 4)),
        "4" + "".join(random.sample(alphabet, 3)),
        "".join(random.sample(alphabet, 4)),
        "".join(random.sample(alphabet, 12)),
    ]
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = (
        "iPhone 14 15.4."
        + uuid[0]
        + uuid[1]
        + phone
        + timestamp
        + password[:6]
        + "0$$$0."
    )
    try:
        r = ss.post(
            "https://appgologin.189.cn:9031/login/client/userLoginNormal",
            json={
                "headerInfos": {
                    "code": "userLoginNormal",
                    "timestamp": timestamp,
                    "broadAccount": "",
                    "broadToken": "",
                    "clientType": "#12.2.0#channel50#iPhone 14 Pro Max#",
                    "shopId": "20002",
                    "source": "110003",
                    "sourcePassword": "Sid98s",
                    "token": "",
                    "userLoginName": encode_phone(phone),
                },
                "content": {
                    "attach": "test",
                    "fieldData": {
                        "loginType": "4",
                        "accountType": "",
                        "loginAuthCipherAsymmertric": b64(loginAuthCipherAsymmertric),
                        "deviceUid": uuid[0] + uuid[1] + uuid[2],
                        "phoneNum": encode_phone(phone),
                        "isChinatelecom": "0",
                        "systemVersion": "15.4.0",
                        "authentication": encode_phone(password),
                    },
                },
            },
        ).json()
        if "responseData" in r and r["responseData"].get("data"):
            l = r["responseData"]["data"]
            if l and l.get("loginSuccessResult"):
                l_res = l.get("loginSuccessResult")
                load_token[phone] = l_res
                with open(load_token_file, "w", encoding="utf-8") as f:
                    json.dump(load_token, f, indent=2, ensure_ascii=False)
                ticket = get_ticket(phone, l_res["userId"], l_res["token"])
                return ticket
        printn(f"   - 登录响应异常: {r}")
    except Exception as e:
        printn(f"   - 登录请求失败: {e}")
    return False

def get_ticket(phone, userId, token):
    try:
        r = ss.post(
            "https://appgologin.189.cn:9031/map/clientXML",
            data="<Request><HeaderInfos><Code>getSingle</Code><Timestamp>"
            + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            + "</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>"
            + token
            + "</Token><UserLoginName>"
            + phone
            + "</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>"
            + encrypt(userId)
            + "</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>",
            headers={
              "user-agent": "CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1",
               'Content-Type': 'application/xml;charset=utf-8'
            },
            verify=False,
        )
        tk = re.findall("<Ticket>(.*?)</Ticket>", r.text)
        if len(tk) == 0:
            return False
        return decrypt(tk[0])
    except Exception as e:
        printn(f"   - 获取Ticket失败: {e}")
        return False


HX_ACTIVITY_CODE = "ACTCODE20260428MHYUSYAK"
HX_ACTIVITY_ID = "ACTIVITY20260428DPFOWR0X"
HX_TASK_GROUP_ID = "3519"
HX_REFERRER_ID = ""
HX_BASE_UI = "https://wapmas.189.cn/mas-pub-ui"
HX_BASE_API = "https://wapmas.189.cn/mas-pub-web"
HX_UTM_SCHA = (
    "utm_ch-010001002009.utm_sch-hg_fw_yyytpyx-1."
    "utm_af-1000000037.utm_as-464459700001.utm_sd1-default"
)
HX_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 "
    "Mobile/15E148 Safari/604.1"
)
HX_SEC_CH_UA = '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"'


def get_set_cookie_header(response):
    set_cookie = response.headers.get("Set-Cookie", "")
    raw_headers = getattr(getattr(response, "raw", None), "headers", None)
    if raw_headers:
        get_all = getattr(raw_headers, "get_all", None) or getattr(
            raw_headers, "getlist", None
        )
        if get_all:
            cookies = get_all("Set-Cookie")
            if cookies:
                set_cookie = "; ".join(cookies)
    return set_cookie


def build_hx_activity_url(ticket):
    params = {
        "activityCode": HX_ACTIVITY_CODE,
        "yxai": HX_ACTIVITY_CODE,
        "ticket": ticket,
        "isshare": "0",
        "utm_scha": HX_UTM_SCHA,
    }
    return (
        f"{HX_BASE_UI}/spm/newActivity/{HX_ACTIVITY_CODE}?"
        + urllib.parse.urlencode(params)
    )


def build_hx_api_headers(ticket, activity_url):
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://wapmas.189.cn",
        "Pragma": "no-cache",
        "Priority": "u=1, i",
        "Referer": activity_url,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": HX_UA,
        "activityCode": HX_ACTIVITY_CODE,
        "activityId": "",
        "id": "",
        "kdticket": "",
        "masEnv": "wap",
        "sec-ch-ua": HX_SEC_CH_UA,
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"iOS"',
        "ticket": ticket,
        "wxFlag": "0",
        "wyDataStr": "",
        "wycorpId": "",
        "wyopenid": "",
        "yxai": HX_ACTIVITY_CODE,
    }


def hx_cookie_names(session):
    return [cookie.name for cookie in session.cookies]


def hx_cookie_header(session):
    return "; ".join(f"{cookie.name}={cookie.value}" for cookie in session.cookies)


def hx_apply_cookie_header(session, cookie_header):
    if not cookie_header:
        return []
    simple = SimpleCookie()
    try:
        simple.load(cookie_header)
    except Exception:
        return []

    names = []
    for name, morsel in simple.items():
        session.cookies.set(name, morsel.value, domain="wapmas.189.cn", path="/")
        names.append(name)
    return names


def parse_json_response(response, name):
    try:
        return response.json()
    except Exception:
        printn(f"   - 换新{name}: 非JSON响应 status={response.status_code}")
        printn(f"   - 换新{name}: {response.text[:300]}")
        return None


def hx_code(data):
    if isinstance(data, dict):
        return data.get("code")
    return None


def hx_msg(data):
    if not isinstance(data, dict):
        return ""
    return (
        data.get("msg")
        or data.get("message")
        or data.get("errMsg")
        or data.get("resultMsg")
        or ""
    )


def hx_success(data):
    code = hx_code(data)
    return code in (1, "1", "0000") or (
        code is None and isinstance(data, dict) and data.get("data") is not None
    )


def safe_int(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def task_title(task, index=None):
    for key_name in (
        "copywriting2",
        "copywriting",
        "title",
        "name",
        "contentName",
        "taskName",
        "text",
    ):
        value = task.get(key_name)
        if value:
            return str(value).strip()
    return f"任务{index}" if index is not None else "未知任务"


def collect_task_items(node, result=None, seen=None):
    if result is None:
        result = []
    if seen is None:
        seen = set()

    if isinstance(node, dict):
        task_id = node.get("taskId")
        if task_id and task_id not in seen:
            seen.add(task_id)
            result.append(node)
        for value in node.values():
            collect_task_items(value, result, seen)
    elif isinstance(node, list):
        for item in node:
            collect_task_items(item, result, seen)
    return result


def hx_login_activity(session, ticket):
    activity_url = build_hx_activity_url(ticket)
    injected_cookie_names = hx_apply_cookie_header(session, os.environ.get("HX_COOKIE", ""))
    if injected_cookie_names:
        printn(f"   - 换新注入Cookie: {', '.join(injected_cookie_names)}")

    api_headers = build_hx_api_headers(ticket, activity_url)
    context = {
        "activity_url": activity_url,
        "api_headers": api_headers,
        "activity_id": HX_ACTIVITY_ID,
        "page_id": "",
        "set_cookie": "",
        "page_data": None,
        "user_ticket": None,
    }

    page_data = hx_set_redis_pages_json(session, context)
    context["page_data"] = page_data
    if isinstance(page_data, dict):
        activity_id = page_data.get("activityId") or HX_ACTIVITY_ID
        page_id = page_data.get("nestPageId") or page_data.get("pageId") or ""
        context["activity_id"] = activity_id
        context["page_id"] = page_id
        if os.environ.get("HX_DEBUG") == "1":
            printn(
                f"   - 换新页面JSON: code={page_data.get('code')} "
                f"isLogin={page_data.get('isLogin')} activityId={activity_id} pageId={page_id}"
            )
            cookie_names = hx_cookie_names(session)
            if cookie_names:
                printn(f"   - 换新页面JSON后Cookie: {', '.join(cookie_names)}")
        if str(page_data.get("isLogin")).lower() != "true":
            printn(f"   - 换新页面JSON未登录: {page_data.get('msg', '')}")

    user_ticket_resp = session.get(
        f"{HX_BASE_API}/userInfo/getUserTicket",
        headers=api_headers,
        timeout=15,
    )
    user_ticket = parse_json_response(user_ticket_resp, "getUserTicket")
    if isinstance(user_ticket, dict):
        printn(
            f"   - 换新getUserTicket: status={user_ticket_resp.status_code} "
            f"code={hx_code(user_ticket)} msg={hx_msg(user_ticket)}"
        )
    if os.environ.get("HX_DEBUG") == "1":
        printn(f"   - 换新Cookie明细: {hx_cookie_header(session)}")

    context["user_ticket"] = user_ticket
    return context


def hx_set_redis_pages_json(session, context):
    response = session.get(
        f"{HX_BASE_API}/spm/restful",
        params={
            "method": "setRedisPagesJson",
            "activityCode": HX_ACTIVITY_CODE,
            "pageId": "",
            "activityId": "",
            "phoneNum": "",
            "previewType": "",
            "subPageLinkCode": "",
            "isPreview": "",
        },
        headers=context["api_headers"],
        timeout=20,
    )
    data = parse_json_response(response, "页面JSON")
    if not hx_success(data):
        printn(
            f"   - 换新页面JSON异常: status={response.status_code} "
            f"code={hx_code(data)} msg={hx_msg(data)}"
        )
        return data
    return data

def hx_query_share_state(session, context):
    response = session.get(
        f"{HX_BASE_API}/shareLottery/query/shareState",
        params={"referrerId": HX_REFERRER_ID},
        headers=context["api_headers"],
        timeout=15,
    )
    data = parse_json_response(response, "分享状态")
    printn(
        f"   - 换新分享状态: status={response.status_code} "
        f"code={hx_code(data)} msg={hx_msg(data)}"
    )
    return data


def hx_query_tasks(session, context):
    response = session.get(
        f"{HX_BASE_API}/componentContent/queryComponentContent",
        params={"isProvOrCityFlag": "2", "groupId": HX_TASK_GROUP_ID},
        headers=context["api_headers"],
        timeout=15,
    )
    data = parse_json_response(response, "任务列表")
    if not hx_success(data):
        printn(
            f"   - 换新任务列表异常: status={response.status_code} "
            f"code={hx_code(data)} msg={hx_msg(data)}"
        )
        return []

    tasks = collect_task_items(data)
    printn(f"   - 换新任务列表: status={response.status_code} 共{len(tasks)}个")
    return tasks


def hx_compare_task(session, context, task_id):
    payload = {"activityId": context.get("activity_id") or HX_ACTIVITY_ID, "taskId": task_id}
    response = session.post(
        f"{HX_BASE_API}/taskRecord/compareTaskComplete",
        json=payload,
        headers=context["api_headers"],
        timeout=15,
    )
    data = parse_json_response(response, "任务状态")
    if not hx_success(data):
        printn(
            f"   - 换新任务状态异常: status={response.status_code} "
            f"code={hx_code(data)} msg={hx_msg(data)}"
        )
    return data


def hx_task_status_info(data):
    status = data.get("data") if isinstance(data, dict) else {}
    if not isinstance(status, dict):
        status = {}

    completion_times = safe_int(status.get("completionTimes"), 0)
    remaining_times = safe_int(status.get("remainingTimes"), 0)
    is_draw_lottery = status.get("isDrawLottery")
    finished = str(is_draw_lottery).lower() == "false"
    if completion_times and remaining_times <= 0:
        finished = True
    done_times = max(completion_times - remaining_times, 0) if completion_times else 0
    submit_times = 0 if finished else max(remaining_times, 1)
    if completion_times:
        submit_times = min(submit_times, completion_times)
    return {
        "finished": finished,
        "completion_times": completion_times,
        "remaining_times": remaining_times,
        "done_times": done_times,
        "submit_times": min(submit_times, 5),
        "raw": status,
    }


def hx_save_task(session, context, task_id):
    payload = {"activityId": context.get("activity_id") or HX_ACTIVITY_ID, "taskId": task_id}
    response = session.post(
        f"{HX_BASE_API}/taskRecord/saveTaskRecord",
        json=payload,
        headers=context["api_headers"],
        timeout=15,
    )
    data = parse_json_response(response, "完成任务")
    printn(
        f"   - 换新完成任务: status={response.status_code} "
        f"code={hx_code(data)} msg={hx_msg(data)}"
    )
    return data


async def hx_finish_tasks(session, context):
    tasks = hx_query_tasks(session, context)
    if not tasks:
        printn("   - 换新任务: 未获取到任务")
        return

    for index, task in enumerate(tasks, 1):
        task_id = task.get("taskId")
        title = task_title(task, index)
        status_data = hx_compare_task(session, context, task_id)
        if not hx_success(status_data):
            printn(f"   - 换新任务跳过: {title} 状态接口未成功")
            continue
        status = hx_task_status_info(status_data)
        total = status["completion_times"] or 1
        done = status["done_times"]
        printn(
            f"   - 换新任务状态: {title} "
            f"{done}/{total} finished={status['finished']}"
        )
        if status["finished"]:
            continue

        submit_times = status["submit_times"] or 1
        for submit_index in range(submit_times):
            printn(f"   - 换新提交任务: {title} 第{submit_index + 1}/{submit_times}次")
            hx_save_task(session, context, task_id)
            await asyncio.sleep(random.uniform(2.0, 4.0))

        status_data = hx_compare_task(session, context, task_id)
        status = hx_task_status_info(status_data)
        printn(
            f"   - 换新复查任务: {title} "
            f"{status['done_times']}/{status['completion_times'] or 1} "
            f"finished={status['finished']}"
        )
        await asyncio.sleep(random.uniform(1.0, 2.0))


def hx_prize_remaining_times(session, context):
    response = session.get(
        f"{HX_BASE_API}/spm/restful",
        params={
            "activityId": context.get("activity_id") or HX_ACTIVITY_ID,
            "method": "prizeRemainingTimes",
        },
        headers=context["api_headers"],
        timeout=15,
    )
    data = parse_json_response(response, "抽奖次数")
    if not hx_success(data):
        printn(
            f"   - 换新抽奖次数异常: status={response.status_code} "
            f"code={hx_code(data)} msg={hx_msg(data)}"
        )
        return 0
    times = safe_int((data or {}).get("data"), 0)
    printn(f"   - 换新剩余抽奖次数: {times}")
    return times


def hx_lottery(session, context):
    response = session.get(
        f"{HX_BASE_API}/lotteryActivity/lottery",
        params={
            "activityId": context.get("activity_id") or HX_ACTIVITY_ID,
            "source": "JinDouMall",
        },
        headers=context["api_headers"],
        timeout=15,
    )
    data = parse_json_response(response, "抽奖")
    if not hx_success(data):
        printn(
            f"   - 换新抽奖异常: status={response.status_code} "
            f"code={hx_code(data)} msg={hx_msg(data)}"
        )
        return {
            "success": False,
            "prize_name": hx_msg(data) or f"抽奖失败({response.status_code})",
            "response": data,
        }

    prize = data.get("data") if isinstance(data, dict) else None
    if isinstance(prize, dict):
        prize_name = (
            prize.get("goodsName")
            or prize.get("prizeName")
            or prize.get("goodsTitle")
            or prize.get("name")
            or hx_msg(data)
        )
        printn(f"   - 换新抽奖结果: {prize_name}")
    else:
        prize_name = hx_msg(data) or prize
        printn(f"   - 换新抽奖结果: {prize_name}")
    return {
        "success": True,
        "prize_name": str(prize_name or "未知奖品"),
        "response": data,
    }


async def hx_draw_all(session, context):
    times = hx_prize_remaining_times(session, context)
    results = []
    if times <= 0:
        printn("   - 换新抽奖: 暂无可用次数")
        return results

    for index in range(min(times, 5)):
        printn(f"   - 换新开始抽奖: 第{index + 1}/{times}次")
        result = hx_lottery(session, context)
        if result:
            results.append(result)
        await asyncio.sleep(1)
    hx_prize_remaining_times(session, context)
    return results


async def ks(phone, ticket, gift_only=False, compose_from_gifts=False):
    session = requests.Session()
    session.mount("https://", DESAdapter())
    session.verify = False
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36"
    }
    session.headers.update(headers)
    context = hx_login_activity(session, ticket)
    if not context:
        printn("   - 换新活动: 初始化失败，无法继续")
        return {"phone": phone, "draw_results": [], "success": False}
    
    hx_query_share_state(session, context)
    await hx_finish_tasks(session, context)
    draw_results = await hx_draw_all(session, context)
    return {"phone": phone, "draw_results": draw_results, "success": True}
        



async def main():

    phone_list = [acc for acc in re.split(r"[&\n@]", PHONES) if acc.strip()]
    printn(f"   - ✨ 检测到 {len(phone_list)} 个账号，准备开始执行任务...")
    print("-" * 50)

    successful_accounts = []
    draw_summaries = []

    for index, phoneV in enumerate(phone_list):
        printn(f"   - 👤 开始处理第 {index + 1} / {len(phone_list)} 个账号...")
        value = phoneV.split("#")
        if len(value) < 2:
            printn(f"   - ❌ 账号格式错误, 跳过: {phoneV}")
            print("-" * 50)
            continue

        phone, password = value[0], value[1]
        masked_phone = mask_phone(phone)
        max_retries = 3
        retry_count = 0
        ticket = False

        while retry_count < max_retries and not ticket:
            retry_count += 1
            printn(f"   - 🔄 账号 {masked_phone} 第 {retry_count} 次登录尝试...")

            if phone in load_token:
                printn(f"   - 🎨 尝试使用缓存Token登录...")
                ticket = get_ticket(
                    phone, load_token[phone]["userId"], load_token[phone]["token"]
                )

            if not ticket:
                printn(f"   - 🎨 缓存无效或不存在，尝试使用密码登录...")
                ticket = userLoginNormal(phone, password)

            if ticket:
                printn(f"   - 🔑 账号 {masked_phone} 登录成功 ✅")
                break
            else:
                printn(f"   - ❌ 账号 {masked_phone} 第 {retry_count} 次登录失败")
                if retry_count < max_retries:
                    await asyncio.sleep(2)

        if ticket:
            result = await ks(phone, ticket)
            draw_summaries.append(result or {
                "phone": phone,
                "draw_results": [],
                "success": False,
            })
            printn(f"   - ✅ 第 {index + 1} 个账号 {masked_phone} 的所有任务执行完毕。")
        else:
            printn(
                f"   - ❌ 账号 {masked_phone} 登录失败，已达最大重试次数，跳过此账号。"
            )

        print("-" * 50)
        if index < len(phone_list) - 1:
            await asyncio.sleep(3)

    printn("🎁 换新抽奖结果汇总")
    if not draw_summaries:
        printn("   - 暂无账号执行抽奖")
    for item in draw_summaries:
        phone = mask_phone(item.get("phone", ""))
        results = item.get("draw_results") or []
        if not item.get("success"):
            printn(f"   - {phone}: 初始化失败/未完成")
        elif not results:
            printn(f"   - {phone}: 无抽奖次数或未抽中")
        else:
            prize_names = [result.get("prize_name", "未知奖品") for result in results]
            printn(f"   - {phone}: {'、'.join(prize_names)}")


load_token_file = "chinaTelecom_cache.json"
try:
    with open(load_token_file, "r") as f:
        load_token = json.load(f)
except:
    load_token = {}

PHONES = os.environ.get("chinaTelecomAccount")
if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        printn("电信任务结束")
