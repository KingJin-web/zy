"""
环境变量：
dxcx=手机号#密码&手机号#密码
也兼容：
chinaTelecomAccount=手机号#密码&手机号@密码&手机号 密码

可选：
DX517_CHANNEL=HGOKHD
DX517_PROMOID=8515cc44b636746c
DX517_GAME_ID=10000
DX517_MY_AWARD_CONCURRENCY=5
DX517_MY_AWARD_PRINT_RAW=0
"""

import asyncio
import base64
import binascii
import datetime
import json
import os
import random
import re
import ssl
import threading
import urllib.parse
from http import cookiejar

import requests


CK517_CHANNEL = os.environ.get("DX517_CHANNEL", "HGOKHD")
CK517_PROMOID = os.environ.get("DX517_PROMOID", "8515cc44b636746c")
CK517_GAME_ID = os.environ.get("DX517_GAME_ID", "10000")
CONCURRENCY = max(int(os.environ.get("DX517_MY_AWARD_CONCURRENCY", "5") or 5), 1)
TOKEN_FILE = "chinaTelecom_cache.json"
HUAFEI_COMMODITY_IDS = {"280367", "280368", "280369"}

KEY = b"1234567`90koiuyhgtfrdews"
IV = 8 * b"\0"
PUBLIC_KEY_B64 = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----"""

AES = None
DES3 = None
RSA = None
PKCS1_V1_5 = None
pad = None
unpad = None
TOKEN_LOCK = threading.Lock()
PRINT_LOCK = threading.Lock()
LOG_LOCAL = threading.local()


def printn(message):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {message}"
    lines = getattr(LOG_LOCAL, "lines", None)
    if lines is not None:
        lines.append(line)
        return
    with PRINT_LOCK:
        print(line, flush=True)


def flush_lines(lines):
    if not lines:
        return
    with PRINT_LOCK:
        for line in lines:
            print(line, flush=True)


def env_enabled(name, default="0"):
    return str(os.environ.get(name, default)).strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
        "disable",
        "disabled",
    )


def mask_phone(phone):
    return f"{phone[:3]}****{phone[7:]}" if isinstance(phone, str) and len(phone) == 11 else phone


def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_account_info(raw):
    """
    支持：
    1. 手机号#密码
    2. 手机号@密码
    3. 手机号 密码
    多账号可用 &、换行或 @ 分隔。密码按常见电信脚本用法处理为非空白短字段。
    """
    raw = raw or ""
    patterns = (
        re.compile(r"(1\d{10})#([^\s&#@]+)"),
        re.compile(r"(1\d{10})@([^\s&#@]+)"),
        re.compile(r"(1\d{10})[ \t,，]+([^\s&#@]+)"),
    )
    matches = []
    for pattern in patterns:
        for match in pattern.finditer(raw):
            matches.append((match.start(), match.group(1), match.group(2)))

    phone_matches = [(match.start(), match.group(0)) for match in re.finditer(r"1\d{10}", raw)]
    matched_starts = {start for start, _, _ in matches}
    accounts = []
    seen = set()
    duplicates = []
    for _, phone, password in sorted(matches, key=lambda item: item[0]):
        key = (phone, password)
        if key in seen:
            duplicates.append((phone, password))
            continue
        seen.add(key)
        accounts.append((phone, password))

    unmatched_phones = [phone for start, phone in phone_matches if start not in matched_starts]
    return {
        "accounts": accounts,
        "phone_count": len(phone_matches),
        "matched_count": len(matches),
        "duplicate_count": len(duplicates),
        "duplicates": duplicates,
        "unmatched_phones": unmatched_phones,
    }


def parse_accounts(raw):
    return parse_account_info(raw)["accounts"]


def response_preview(response, limit=200):
    try:
        text = response.text
    except Exception:
        content = getattr(response, "content", b"")
        text = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else str(content)
    return re.sub(r"[\r\n\t]+", " ", str(text).strip())[:limit]


def response_text_variants(response):
    variants = []

    def add(text):
        if text is None:
            return
        text = str(text)
        if text and text not in variants:
            variants.append(text)

    try:
        add(response.text)
    except Exception:
        pass

    content = getattr(response, "content", b"")
    if isinstance(content, bytes) and content:
        for encoding in (
            getattr(response, "encoding", None),
            getattr(response, "apparent_encoding", None),
            "utf-8-sig",
            "utf-8",
            "gb18030",
        ):
            if not encoding:
                continue
            try:
                add(content.decode(encoding, errors="replace"))
            except LookupError:
                pass
    return variants


def parse_json_relaxed(response):
    try:
        return response.json()
    except ValueError:
        pass

    decoder = json.JSONDecoder(strict=False)
    last_error = None
    for text in response_text_variants(response):
        text = str(text).lstrip("\ufeff \t\r\n")
        for candidate in (text, text.replace("\x00", "")):
            if not candidate:
                continue
            try:
                return json.loads(candidate, strict=False)
            except ValueError as exc:
                last_error = exc

            starts = [idx for idx in (candidate.find("{"), candidate.find("[")) if idx >= 0]
            if not starts:
                continue
            try:
                data, _ = decoder.raw_decode(candidate[min(starts):])
                return data
            except ValueError as exc:
                last_error = exc
    raise ValueError(last_error or "response is not JSON")


def ensure_crypto():
    global AES, DES3, RSA, PKCS1_V1_5, pad, unpad
    if AES and DES3 and RSA and PKCS1_V1_5 and pad and unpad:
        return True
    try:
        from Crypto.Cipher import AES as _AES
        from Crypto.Cipher import DES3 as _DES3
        from Crypto.Cipher import PKCS1_v1_5 as _PKCS1_v1_5
        from Crypto.PublicKey import RSA as _RSA
        from Crypto.Util.Padding import pad as _pad
        from Crypto.Util.Padding import unpad as _unpad
    except ModuleNotFoundError:
        printn("缺少依赖 pycryptodome，请先安装：pip install pycryptodome")
        return False

    AES = _AES
    DES3 = _DES3
    RSA = _RSA
    PKCS1_V1_5 = _PKCS1_v1_5
    pad = _pad
    unpad = _unpad
    return True


class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.set_ciphers("DEFAULT@SECLEVEL=1")
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE
requests.packages.urllib3.disable_warnings()


class DESAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = SSL_CONTEXT
        return super().init_poolmanager(*args, **kwargs)


def load_token_cache():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def save_token_cache(cache):
    with open(TOKEN_FILE, "w", encoding="utf-8") as file:
        json.dump(cache, file, indent=2, ensure_ascii=False)


TOKEN_CACHE = load_token_cache()


def build_login_session():
    session = requests.Session()
    session.headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36"
        ),
        "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html",
    }
    session.mount("https://", DESAdapter())
    session.cookies.set_policy(BlockAll())
    return session


def encrypt_3des(text):
    if not ensure_crypto():
        raise RuntimeError("missing pycryptodome")
    cipher = DES3.new(KEY, DES3.MODE_CBC, IV)
    return cipher.encrypt(pad(text.encode(), DES3.block_size)).hex()


def decrypt_3des(text):
    if not ensure_crypto():
        raise RuntimeError("missing pycryptodome")
    cipher = DES3.new(KEY, DES3.MODE_CBC, IV)
    return unpad(cipher.decrypt(bytes.fromhex(text)), DES3.block_size).decode()


def rsa_b64(text):
    if not ensure_crypto():
        raise RuntimeError("missing pycryptodome")
    public_key = RSA.import_key(PUBLIC_KEY_B64)
    cipher = PKCS1_V1_5.new(public_key)
    return base64.b64encode(cipher.encrypt(text.encode())).decode()


def encode_phone(text):
    return "".join(chr(ord(char) + 2) for char in text)


def user_login_normal(phone, password, login_session):
    if not ensure_crypto():
        return False

    alphabet = "abcdef0123456789"
    uuid_parts = [
        "".join(random.sample(alphabet, 8)),
        "".join(random.sample(alphabet, 4)),
        "4" + "".join(random.sample(alphabet, 3)),
        "".join(random.sample(alphabet, 4)),
        "".join(random.sample(alphabet, 12)),
    ]
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    login_auth = (
        "iPhone 14 15.4."
        + uuid_parts[0]
        + uuid_parts[1]
        + phone
        + timestamp
        + password[:6]
        + "0$$$0."
    )

    try:
        response = login_session.post(
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
                        "loginAuthCipherAsymmertric": rsa_b64(login_auth),
                        "deviceUid": uuid_parts[0] + uuid_parts[1] + uuid_parts[2],
                        "phoneNum": encode_phone(phone),
                        "isChinatelecom": "0",
                        "systemVersion": "15.4.0",
                        "authentication": encode_phone(password),
                    },
                },
            },
            timeout=20,
        )
        data = parse_json_relaxed(response).get("responseData", {}).get("data", {})
        login_result = data.get("loginSuccessResult") if isinstance(data, dict) else None
        if not login_result:
            printn(f"   - 登录失败: {data}")
            return False

        with TOKEN_LOCK:
            TOKEN_CACHE[phone] = login_result
            save_token_cache(TOKEN_CACHE)
        return get_ticket(phone, login_result["userId"], login_result["token"], login_session)
    except Exception as exc:
        printn(f"   - 登录请求异常: {exc}")
        return False


def get_ticket(phone, user_id, token, login_session):
    if not ensure_crypto():
        return False
    try:
        response = login_session.post(
            "https://appgologin.189.cn:9031/map/clientXML",
            data=(
                "<Request><HeaderInfos><Code>getSingle</Code><Timestamp>"
                + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                + "</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken>"
                + "<ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType>"
                + "<ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword>"
                + "<Token>"
                + token
                + "</Token><UserLoginName>"
                + phone
                + "</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>"
                + encrypt_3des(user_id)
                + "</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>"
            ),
            headers={
                "user-agent": "CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1",
                "Content-Type": "application/xml;charset=utf-8",
            },
            verify=False,
            timeout=20,
        )
        tickets = re.findall("<Ticket>(.*?)</Ticket>", response.text)
        return decrypt_3des(tickets[0]) if tickets else False
    except Exception as exc:
        printn(f"   - 获取 Ticket 失败: {exc}")
        return False


def get_account_ticket(phone, password):
    login_session = build_login_session()
    with TOKEN_LOCK:
        cached = TOKEN_CACHE.get(phone)

    if cached:
        ticket = get_ticket(phone, cached.get("userId", ""), cached.get("token", ""), login_session)
        if ticket:
            return ticket
    return user_login_normal(phone, password, login_session)


def build_session():
    session = requests.Session()
    session.mount("https://", DESAdapter())
    session.verify = False
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36"
            )
        }
    )
    return session


def get_set_cookie_header(response):
    set_cookie = response.headers.get("Set-Cookie", "")
    raw_headers = getattr(getattr(response, "raw", None), "headers", None)
    if raw_headers:
        get_all = getattr(raw_headers, "get_all", None) or getattr(raw_headers, "getlist", None)
        cookies = get_all("Set-Cookie") if get_all else None
        if cookies:
            set_cookie = "; ".join(cookies)
    return set_cookie


def extract_reqparam(location):
    match = re.search(r"[?&]reqparam=([^&]+)", location or "")
    return urllib.parse.unquote(match.group(1)) if match else ""


def extract_newmallsession(set_cookie):
    match = re.search(r"(newmallsession=[^;]+;)", set_cookie or "")
    return match.group(1) if match else ""


def get_query_param(url, key):
    query = urllib.parse.parse_qs(urllib.parse.urlparse(url or "").query, keep_blank_values=True)
    values = query.get(key)
    return values[0] if values else ""


def normalize_cookie(cookie):
    return (cookie or "").strip().rstrip(";")


def request_merchants_dock(reqparam, session, headers, location=""):
    if not reqparam:
        return None
    kwargs = {"headers": headers, "allow_redirects": False, "timeout": 15}
    if location:
        response = session.get(location, **kwargs)
    else:
        response = session.get(
            "https://m.telefen.com/MobileSSOv2/MerchantsDock.aspx",
            params={"appcode": CK517_CHANNEL, "reqparam": reqparam},
            **kwargs,
        )
    return {"status": response.status_code, "location": response.headers.get("Location", "")}


def build_api_context(newmallsession, referer):
    token = get_query_param(referer, "Token")
    channel = get_query_param(referer, "channel") or CK517_CHANNEL
    cookie = normalize_cookie(newmallsession)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "appcode": channel,
        "appCode": channel,
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Cookie": cookie,
        "Host": "apps.telefen.com",
        "Origin": "https://apps.telefen.com",
        "Referer": referer,
        "ssotoken": token,
        "SSOToken": token,
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
    }
    return {"channel": channel, "token": token, "referer": referer, "cookie": cookie, "headers": headers}


def request_ck517_page(session, api_context, referer=""):
    if not api_context.get("referer"):
        return
    response = session.get(
        api_context["referer"],
        headers={
            "User-Agent": api_context["headers"]["User-Agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Cookie": api_context["headers"]["Cookie"],
            "Referer": referer,
            "Upgrade-Insecure-Requests": "1",
        },
        allow_redirects=True,
        timeout=15,
    )
    newmallsession = extract_newmallsession(get_set_cookie_header(response))
    if newmallsession:
        cookie = normalize_cookie(newmallsession)
        api_context["cookie"] = cookie
        api_context["headers"]["Cookie"] = cookie


def request_account_check(session, api_context):
    try:
        response = session.get(
            "https://apps.telefen.com/mallactive/api/account/check",
            params={"noload": "true"},
            headers=api_context["headers"],
            timeout=15,
        )
        data = parse_json_relaxed(response)
        return bool(isinstance(data, dict) and (data.get("data") or {}).get("deviceNo"))
    except Exception:
        return False


def ck517_login(ticket, session):
    try:
        params = {
            "channel": CK517_CHANNEL,
            "action": "2",
            "rdurl": f"https://apps.telefen.com/mallactive/ck517?channel={CK517_CHANNEL}",
            "promoid": CK517_PROMOID,
            "ticket": ticket,
            "utm_scha": "utm_ch-010001002009.utm_sch-hg_sy_yxtc-1.utm_af-1000000037.utm_as-456876200001.utm_sd1-S0076579",
        }
        headers = {
            "User-Agent": "CtClient;13.2.0;Android;14;22021211RC;",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "X-Requested-With": "com.ct.client",
        }
        response = session.get(
            "https://apps.telefen.com/middleparse/api/access/ticket",
            params=params,
            headers=headers,
            allow_redirects=False,
            timeout=15,
        )
        if response.status_code not in (301, 302, 303, 307, 308):
            printn(f"   - 517 登录失败: status={response.status_code} {response_preview(response)}")
            return None

        location = response.headers.get("Location", "")
        reqparam = extract_reqparam(location)
        newmallsession = extract_newmallsession(get_set_cookie_header(response))
        dock = request_merchants_dock(reqparam, session, headers, location)
        if not dock or not dock.get("location"):
            printn("   - 517 登录失败: 未获取活动页地址")
            return None

        api_context = build_api_context(newmallsession, dock["location"])
        request_ck517_page(session, api_context, location)
        request_account_check(session, api_context)
        return api_context
    except Exception as exc:
        printn(f"   - 517 登录异常: {exc}")
        return None


def has_award_payload(data):
    if isinstance(data, bool):
        return data
    if not isinstance(data, dict):
        return False
    return bool(
        data.get("hasCompositeRecord")
        or data.get("isComposite")
        or data.get("isComposited")
        or data.get("compositeRecord")
        or data.get("compositeRecordId") is not None
        or data.get("id") is not None
        or data.get("compositeTime")
        or data.get("commodityId")
        or data.get("commodityName")
    )


def extract_award_record(data):
    if not isinstance(data, dict):
        return None
    record = data.get("data")
    if not has_award_payload(record):
        return None
    if isinstance(record, dict) and record.get("isWon") in (0, "0", False):
        return None
    return record if isinstance(record, dict) else {}


def award_type(record):
    value = record.get("commodityType") if isinstance(record, dict) else None
    return {
        1: "实物",
        2: "权益/虚拟奖品",
        3: "卡券",
        4: "资格券",
        11: "兑换码/直充类",
    }.get(to_int(value, -1), f"type={value}")


def award_status(record):
    value = record.get("receivedStatus") if isinstance(record, dict) else None
    status = to_int(value, -1)
    if status == 0:
        return "待领取"
    if status == 1:
        return "已领取/可查看"
    return f"receivedStatus={value}"


def award_action(record):
    status = to_int(record.get("receivedStatus"), -1)
    kind = to_int(record.get("commodityType"), -1)
    commodity_id = str(record.get("commodityId") or record.get("useCommodityId") or "")
    if status == 0 and kind == 1:
        return "待领取：回活动页填写地址"
    if status == 0:
        return "待领取：回活动页点领取"
    if kind in (3, 4):
        return "已领取：卡券/优惠券中心查看"
    if commodity_id in HUAFEI_COMMODITY_IDS:
        return "已领取：话费券预计活动结束后到账"
    if status == 1:
        return "已领取：个人中心/全部订单查看"
    return "处理方式未知"


def build_award(record):
    name = (
        record.get("commodityName")
        or record.get("prizeName")
        or record.get("productName")
        or record.get("awardName")
        or "未返回奖品名称"
    )
    record_id = record.get("id") or record.get("recordId") or record.get("compositeRecordId") or ""
    commodity_id = record.get("commodityId") or record.get("useCommodityId") or ""
    return {
        "kind": "award",
        "name": str(name),
        "type": award_type(record),
        "status": award_status(record),
        "action": award_action(record),
        "record_id": str(record_id) if record_id else "",
        "commodity_id": str(commodity_id) if commodity_id else "",
    }


def query_my_award(session, api_context):
    response = session.post(
        "https://apps.telefen.com/mallactive/api/fragment/getCompositeRecord",
        json={"gameId": CK517_GAME_ID},
        headers=api_context["headers"],
        timeout=15,
    )
    try:
        data = parse_json_relaxed(response)
    except ValueError:
        return {"kind": "error", "error": f"非 JSON status={response.status_code} {response_preview(response)}"}

    if env_enabled("DX517_MY_AWARD_PRINT_RAW"):
        printn("   - 原始返回: " + json.dumps(data, ensure_ascii=False))

    record = extract_award_record(data)
    biz_data = data.get("data") if isinstance(data, dict) else None
    err_msg = data.get("errMsg", "") if isinstance(data, dict) else ""

    if record is None:
        if has_award_payload(biz_data):
            return {"kind": "no_win", "message": err_msg or "已有合成记录，但暂无中奖奖品"}
        return {"kind": "empty", "message": err_msg or "暂无奖品记录"}
    return build_award(record)


def with_account(result, phone):
    result = dict(result if isinstance(result, dict) else {"kind": "unknown"})
    result["phone"] = phone
    result["masked_phone"] = mask_phone(phone)
    return result


def award_line(result):
    extras = []
    if result.get("record_id"):
        extras.append(f"recordId={result['record_id']}")
    if result.get("commodity_id"):
        extras.append(f"commodityId={result['commodity_id']}")
    suffix = "，" + "，".join(extras) if extras else ""
    return (
        f"{result['masked_phone']}: {result.get('name', '')}，"
        f"{result.get('type', '')}，{result.get('status', '')}，{result.get('action', '')}{suffix}"
    )


def query_one_account(phone, password):
    LOG_LOCAL.lines = []
    try:
        masked = mask_phone(phone)
        printn(f"============== 查询账号 {masked} ==============")

        ticket = get_account_ticket(phone, password)
        if not ticket:
            printn(f"   - {masked}: 登录失败")
            return with_account({"kind": "login_failed", "error": "登录失败"}, phone)

        session = build_session()
        api_context = ck517_login(ticket, session)
        if not api_context:
            printn(f"   - {masked}: 517 活动登录失败")
            return with_account({"kind": "ck517_failed", "error": "517 活动登录失败"}, phone)

        result = with_account(query_my_award(session, api_context), phone)
        if result.get("kind") == "award":
            printn("   - " + award_line(result))
        elif result.get("kind") == "empty":
            printn(f"   - {masked}: 暂无奖品")
        elif result.get("kind") == "no_win":
            printn(f"   - {masked}: 合成未中奖")
        else:
            printn(f"   - {masked}: 查询失败，{result.get('error', result.get('kind', '未知错误'))}")
        return result
    except Exception as exc:
        printn(f"   - {mask_phone(phone)}: 查询异常，{exc}")
        return with_account({"kind": "error", "error": str(exc)}, phone)
    finally:
        lines = getattr(LOG_LOCAL, "lines", [])
        if hasattr(LOG_LOCAL, "lines"):
            del LOG_LOCAL.lines
        flush_lines(lines)


async def query_worker(semaphore, phone, password):
    async with semaphore:
        return await asyncio.to_thread(query_one_account, phone, password)


def prize_counts(awards):
    counts = {}
    for item in awards:
        counts[item["name"]] = counts.get(item["name"], 0) + 1
    return sorted(counts.items())


def print_summary(results):
    valid = [item for item in results if isinstance(item, dict)]
    awards = [item for item in valid if item.get("kind") == "award"]
    empty_count = sum(1 for item in valid if item.get("kind") == "empty")
    no_win_count = sum(1 for item in valid if item.get("kind") == "no_win")
    failed = [item for item in valid if item.get("kind") not in ("award", "empty", "no_win")]
    success_count = len(valid) - len(failed)

    printn("============== 517 我的奖品汇总 ==============")
    printn(
        f"   - 查询成功 {success_count}/{len(valid)}，"
        f"有奖品 {len(awards)}，暂无奖品 {empty_count}，合成未中奖 {no_win_count}，失败 {len(failed)}"
    )
    if awards:
        printn("   - 奖品统计:")
        for name, count in prize_counts(awards):
            printn(f"   - {name}x{count}")
        for item in awards:
            printn("   - " + award_line(item))
    if failed:
        printn(f"   - 异常/失败账号: {len(failed)} 个")
        for item in failed:
            printn(f"   - {item.get('masked_phone', '')}: {item.get('error', item.get('kind', '未知错误'))}")


async def main():
    raw = os.environ.get("dxcx") or os.environ.get("chinaTelecomAccount") or ""
    account_info = parse_account_info(raw)
    accounts = account_info["accounts"]
    if not accounts:
        printn("未找到有效账号。支持格式：手机号#密码、手机号@密码、手机号 密码")
        return

    printn(
        f"检测到手机号 {account_info['phone_count']} 个，"
        f"格式有效 {account_info['matched_count']} 条，"
        f"重复 {account_info['duplicate_count']} 条，"
        f"实际查询 {len(accounts)} 个，并发数 {CONCURRENCY}"
    )
    if account_info["duplicate_count"]:
        dup_preview = "；".join(
            f"{mask_phone(phone)}" for phone, _ in account_info["duplicates"][:5]
        )
        if dup_preview:
            printn(f"   - 重复账号: {dup_preview}")
    if account_info["unmatched_phones"]:
        unmatched_preview = "；".join(account_info["unmatched_phones"][:5])
        printn(f"   - 未匹配手机号: {unmatched_preview}")
    semaphore = asyncio.Semaphore(CONCURRENCY)
    results = await asyncio.gather(
        *(query_worker(semaphore, phone, password) for phone, password in accounts),
        return_exceptions=True,
    )
    normalized = []
    for result in results:
        if isinstance(result, Exception):
            normalized.append({"kind": "error", "error": str(result), "masked_phone": ""})
        else:
            normalized.append(result)
    print_summary(normalized)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        printn("电信517我的奖品查询结束")
