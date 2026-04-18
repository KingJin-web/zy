"""
依赖：requests curl_cffi pycryptodome
账号变量：chinaTelecomAccount 格式"手机号#密码"，多个账号用 & 或换行分隔
变量不可用直接创建accounts.txt（格式同上）
"""
import os
import time
import json
import base64
import hashlib
import random
import string
import urllib.parse
import re
import datetime
from collections import OrderedDict
import requests as sync_requests

try:
    from curl_cffi import requests

    CURL_CFFI_IMPORT_ERROR = None
except ModuleNotFoundError as exc:
    requests = None
    CURL_CFFI_IMPORT_ERROR = exc
from Crypto.Cipher import AES, DES3, PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA

TEST_ACCOUNTS = ""
ACCOUNTS_STR = os.environ.get("chinaTelecomAccount") or os.environ.get("CAILING_ACCOUNTS", TEST_ACCOUNTS)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(SCRIPT_DIR, "accounts.txt")
MAX_EXPIRY_DATE = datetime.date(2026, 6, 30)
CHANNEL_ID = "156000008427"
ACTIVITY_ID = "ai096"
TEMPLATE_ID = "ve_3949"
TEMPLATE_CONF_ID = "2JCg"
FAKE_VIDEO_ID = "" 
LOTTERY_COST_SCORE = 20
POINT_REDEEM_COST_SCORE = 1000
POINT_REDEEM_RETRY_LIMIT = 3
PHONE_BILL_CLAIM_RETRY_LIMIT = 3
POINT_AWARD_PAGE_SIZE = 50
ACCOUNT_PROXY_RETRY_LIMIT = int(os.environ.get("AI096_ACCOUNT_PROXY_RETRY_LIMIT", "2"))
MAX_AUTO_MAKE_ATTEMPTS = int(os.environ.get("AI096_MAX_AUTO_MAKE_ATTEMPTS", "10"))
ASSIST_MODE = os.environ.get("AI096_ASSIST_MODE", "off").strip().lower()
ASSIST_TARGETS = [
    item.strip()
    for item in os.environ.get("AI096_ASSIST_TARGETS", "").replace("&", ",").split(",")
    if item.strip()
]
PRE_ASSIST_TARGETS_RAW = os.environ.get("AI096_PRE_ASSIST_TARGETS", "")

FIXED_PRE_ASSIST_INVITATION_CODES = [
    "2799914b8a4760a45a155cdb44c595917729b5b7eb2c111f7856d33bb552acce",  # 1
]

PRE_ASSIST_RANDOM_MODE = os.environ.get("AI096_PRE_ASSIST_RANDOM_MODE", "different").strip().lower()

FIXED_PRE_ASSIST_INVITATION_LINKS = [
    f"https://ai.imusic.cn/h5v/fusion/ai-luck-win?cc=156000008427&isshare=0&invitationCode={code}"
    for code in FIXED_PRE_ASSIST_INVITATION_CODES
]


DEFAULT_PROXY_API = os.environ.get("AI096_PROXY_API", "").strip()
DEFAULT_DRAW_LIMIT = os.environ.get("AI096_DRAW_LIMIT", "3").strip()


def md5(t): return hashlib.md5(t.encode()).hexdigest()


def rsa_encrypt(t):
    pub = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----"""
    return base64.b64encode(PKCS1_v1_5.new(RSA.import_key(pub)).encrypt(t.encode())).decode()


def des3_op(t, decrypt=False):
    key = b"1234567`90koiuyhgtfrdews"
    c = DES3.new(key, DES3.MODE_CBC, b"\x00" * 8)
    if decrypt:
        try:
            return unpad(c.decrypt(bytes.fromhex(t)), 8).decode()
        except:
            return t
    return c.encrypt(pad(t.encode(), 8)).hex()


class ImCrypto:
    def __init__(self):
        self.ts = str(int(time.time() * 1000))
        self.rdm = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        m_ts = md5(self.ts)
        self.key_h = md5(base64.b64encode((m_ts + self.rdm).encode()).decode() + self.rdm)
        self.e_k = md5(base64.b64encode(self.rdm.encode()).decode() + m_ts + self.key_h)[:16]
        self.e_i = md5(base64.b64encode(self.ts.encode()).decode() + md5(self.rdm) + self.key_h)[:16]

    def encrypt(self, d):
        s = json.dumps(d, separators=(',', ':'), ensure_ascii=False)
        c = AES.new(self.e_k.encode(), AES.MODE_CBC, self.e_i.encode())
        return base64.b64encode(c.encrypt(pad(s.encode('utf-8'), 16))).decode()

    def decrypt(self, t):
        try:
            d_k = md5(base64.b64encode(self.ts.encode()).decode() + self.key_h + md5(self.rdm))[:16]
            d_i = md5(base64.b64encode(self.rdm.encode()).decode() + self.key_h + md5(self.ts))[:16]
            c = AES.new(d_k.encode(), AES.MODE_CBC, d_i.encode())
            return unpad(c.decrypt(base64.b64decode(t)), 16).decode('utf-8')
        except:
            return t


def check_and_update_token(res, current_token):
    new_auth = res.headers.get("authorization") or res.headers.get("Authorization")
    if new_auth:
        new_token = new_auth.replace("Bearer ", "").strip()
        if new_token and new_token != current_token:
            return new_token
    return current_token


def get_headers(crypto_inst, token="", is_share=False):
    ref = f"https://ai.imusic.cn/h5v/fusion/ai-luck-win-share?videoId={FAKE_VIDEO_ID}&cc={CHANNEL_ID}" if is_share else f"https://ai.imusic.cn/h5v/fusion/ai-luck-win?cc={CHANNEL_ID}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://ai.imusic.cn",
        "Referer": ref,
        "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "imencrypt": "1",
        "imtimestamp": crypto_inst.ts,
        "imrandomnum": crypto_inst.rdm,
        "imencryptkey": crypto_inst.key_h,
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


class ProxyManager:
    SOURCE_NONE = "none"
    SOURCE_API = "api"
    SOURCE_MANUAL = "manual"

    def __init__(self):
        self.proxy_source = self.SOURCE_NONE
        self.proxy_api = ""
        self.manual_proxies = []
        self.valid_proxies = []
        self.max_accounts_per_proxy = 1

    @staticmethod
    def parse_proxy_entries(raw_text):
        proxies = []
        for line in raw_text.replace("\r", "\n").split("\n"):
            line = line.strip()
            if not line:
                continue
            for sep in [",", ";", " ", "\t"]:
                if sep in line:
                    parts = [item.strip() for item in line.split(sep) if item.strip()]
                    proxies.extend(parts)
                    break
            else:
                proxies.append(line)
        return proxies

    @staticmethod
    def looks_like_proxy_entry(value):
        return bool(re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}", value))

    def interactive_setup(self):
        print("\n" + "=" * 55)
        print("  🌐 代理设置")
        print("=" * 55)
        print("  1. 直连（不使用代理）")
        print("  2. 输入代理API提取链接")
        print("  3. 手动输入 IP:端口（支持多个）")
        print("=" * 55)

        while True:
            choice = input("\n请选择 [1/2/3]（默认1）: ").strip()
            if choice == "" or choice == "1":
                self.proxy_source = self.SOURCE_NONE
                print("✅ 已选择: 直连模式\n")
                return
            if choice == "2":
                api_or_proxy = input("请输入代理API链接或直接输入代理IP:端口: ").strip()
                if api_or_proxy:
                    proxies = self.parse_proxy_entries(api_or_proxy)
                    if proxies and all(
                            self.looks_like_proxy_entry(item) for item in proxies) and "://" not in api_or_proxy:
                        self.proxy_source = self.SOURCE_MANUAL
                        self.manual_proxies = proxies
                        print(f"✅ 已识别为直填代理，共 {len(proxies)} 个:")
                        for proxy in proxies:
                            print(f"   • {proxy}")
                    else:
                        self.proxy_source = self.SOURCE_API
                        self.proxy_api = api_or_proxy
                        print(f"✅ 已设置API链接: {api_or_proxy[:60]}...")
                    return
                print("⚠️  链接为空，请重新选择")
                continue
            if choice == "3":
                print("请输入代理IP:端口（每行一个，输入空行结束）:")
                print("格式示例: 123.45.67.89:8080")
                proxies = []
                seen = set()
                while True:
                    line = input("  > ").strip()
                    if not line:
                        break
                    for sep in [",", ";", " ", "\t"]:
                        if sep in line:
                            proxies.extend([p.strip() for p in line.split(sep) if p.strip()])
                            break
                    else:
                        proxies.append(line)
                if proxies:
                    self.proxy_source = self.SOURCE_MANUAL
                    self.manual_proxies = proxies
                    print(f"✅ 已添加 {len(proxies)} 个代理:")
                    for proxy in proxies:
                        print(f"   • {proxy}")
                    return
                print("⚠️  未输入任何代理，请重新选择")
                continue
            print("⚠️  无效选择，请输入 1、2 或 3")

    def test_proxy(self, proxy_ip, timeout=10):
        proxy_url = normalize_proxy_url(proxy_ip)
        try:
            response = sync_requests.get(
                "https://ai.imusic.cn",
                proxies={"http": proxy_url, "https": proxy_url},
                timeout=timeout,
                verify=False,
            )
            if response.ok:
                print(f"  ✅ 代理 {proxy_ip} 可用")
                return True
        except Exception as e:
            print(f"  ❌ 代理 {proxy_ip} 不可用: {e}")
        return False

    def get_proxies_from_api(self, count=1):
        if not self.proxy_api:
            return []
        try:
            response = sync_requests.get(self.proxy_api, timeout=15, verify=False)
            if response.ok:
                proxies = []
                seen = set()
                for line in response.text.replace("\r\n", "\n").split("\n"):
                    line = line.strip()
                    if line and ":" in line and line not in seen:
                        seen.add(line)
                        proxies.append(line)
                print(f"  📡 API返回 {len(proxies)} 个代理IP")
                return proxies[:count]
        except Exception as e:
            print(f"  ❌ 获取代理失败: {e}")
        return []

    def get_valid_proxies(self, account_count):
        self.valid_proxies = []
        if self.proxy_source == self.SOURCE_NONE:
            print("📡 模式: 直连（无代理）")
            return []
        if self.proxy_source == self.SOURCE_MANUAL:
            print(f"\n📡 模式: 手动代理，验证 {len(self.manual_proxies)} 个...")
            for proxy in self.manual_proxies:
                if self.test_proxy(proxy):
                    self.valid_proxies.append(proxy)
            print(f"✅ {len(self.valid_proxies)}/{len(self.manual_proxies)} 个可用")
            return self.valid_proxies
        if self.proxy_source == self.SOURCE_API:
            proxy_count = max(1, account_count)
            print(f"\n📡 模式: API提取，一号一IP，需要约 {proxy_count} 个代理")
            max_rounds = max(3, min(account_count * 2, 20))
            for retry in range(max_rounds):
                needed = proxy_count - len(self.valid_proxies)
                if needed <= 0:
                    break
                print(f"\n🔄 第{retry + 1}次获取，还需 {needed} 个...")
                for proxy in self.get_proxies_from_api(needed):
                    if proxy in self.valid_proxies:
                        continue
                    if self.test_proxy(proxy):
                        self.valid_proxies.append(proxy)
                if len(self.valid_proxies) < proxy_count:
                    time.sleep(2)
            print(f"\n🎯 最终获得 {len(self.valid_proxies)} 个有效代理")
            return self.valid_proxies
        return []

    def assign_proxies_to_accounts(self, accounts):
        if not self.valid_proxies:
            return {i: None for i in range(len(accounts))}
        assignment = {i: None for i in range(len(accounts))}
        total_accounts = len(accounts)
        usable_count = min(total_accounts, len(self.valid_proxies))
        for account_index in range(usable_count):
            assignment[account_index] = self.valid_proxies[account_index]
        if usable_count < total_accounts:
            print(f"⚠️  可用代理不足，一号一IP仅分配到前 {usable_count} 个账号，其余账号将直连")
        return assignment

    def acquire_fresh_proxy(self, exclude=None):
        exclude_set = {item for item in (exclude or set()) if item}

        for proxy in self.valid_proxies:
            if proxy and proxy not in exclude_set:
                return proxy

        if self.proxy_source != self.SOURCE_API:
            return None

        for _ in range(5):
            candidates = self.get_proxies_from_api(5)
            for proxy in candidates:
                if not proxy or proxy in exclude_set or proxy in self.valid_proxies:
                    continue
                if self.test_proxy(proxy):
                    self.valid_proxies.append(proxy)
                    return proxy
            time.sleep(1)
        return None


proxy_manager = ProxyManager()


def display_width(text):
    width = 0
    for char in text:
        width += 2 if ord(char) > 127 else 1
    return width


def pad_to_width(text, target_width, align="left"):
    current_width = display_width(text)
    padding = max(0, target_width - current_width)
    if align == "right":
        return " " * padding + text
    if align == "center":
        left = padding // 2
        right = padding - left
        return " " * left + text + " " * right
    return text + " " * padding


def mask_phone(phone):
    return f"{phone[:3]}****{phone[-4:]}" if len(phone) >= 7 else phone


def create_template_accounts_file():
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as file:
        file.write("# 格式: 手机号#密码#有效期\n\n")


def parse_expiry(expiry_text, today):
    expiry_text = expiry_text.strip()
    if expiry_text.isdigit():
        expiry_date = today + datetime.timedelta(days=max(1, int(expiry_text)) - 1)
        return min(expiry_date, MAX_EXPIRY_DATE), True
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            parsed_date = datetime.datetime.strptime(expiry_text, fmt).date()
            return min(parsed_date, MAX_EXPIRY_DATE), False
        except ValueError:
            continue
    return today, True


def parse_accounts(raw_text):
    accounts = []
    normalized = raw_text.replace("\r", "\n").replace("&", "\n")
    for part in normalized.split("\n"):
        item = part.strip()
        if not item:
            continue
        if "#" in item:
            phone, password = item.split("#", 1)
        elif "@" in item:
            phone, password = item.split("@", 1)
        else:
            continue
        phone = phone.strip()
        password = password.strip()
        if not phone or not password:
            continue
        accounts.append((phone, password))
    if not accounts:
        raise ValueError("未解析到有效账号，请按 手机号#密码 输入，多个账号可用 & 或换行分隔，也支持 手机号@密码")
    return accounts


def parse_accounts_from_env(raw_text):
    accounts = []
    for part in raw_text.replace("\n", "&").replace("\r", "").split("&"):
        item = part.strip()
        if "#" in item:
            phone, password = item.split("#", 1)
        elif "@" in item:
            phone, password = item.split("@", 1)
        else:
            continue
        phone = phone.strip()
        password = password.strip()
        if phone and password:
            accounts.append(
                (
                    phone,
                    password,
                    MAX_EXPIRY_DATE,
                    (MAX_EXPIRY_DATE - datetime.date.today()).days,
                    True,
                    None,
                )
            )
    return accounts


def load_accounts_from_file():
    today = datetime.date.today()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    if not os.path.exists(ACCOUNTS_FILE):
        print("未找到账号文件，已创建模板")
        create_template_accounts_file()
        return []
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as file:
        raw_lines = file.readlines()

    accounts = []
    need_rewrite = False
    new_lines = []
    skipped = []
    anchored = []

    for line_number, raw_line in enumerate(raw_lines, 1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(raw_line)
            continue
        parts = stripped.split("#")
        if len(parts) < 2:
            skipped.append((line_number, stripped, "格式错误"))
            new_lines.append(raw_line)
            continue
        phone, password = parts[0].strip(), parts[1].strip()
        if not phone or not password:
            skipped.append((line_number, stripped, "空值"))
            new_lines.append(raw_line)
            continue

        anchor_time = None
        already_anchored = False
        if len(parts) >= 4 and parts[3].strip().startswith("锚定:"):
            already_anchored = True
            anchor_time = parts[3].strip().replace("锚定:", "")

        if len(parts) >= 3 and parts[2].strip():
            raw_expiry = parts[2].strip()
            if already_anchored:
                expiry_date, _ = parse_expiry(raw_expiry, today)
                new_lines.append(raw_line)
            else:
                expiry_date, was_days = parse_expiry(raw_expiry, today)
                if was_days:
                    need_rewrite = True
                    expiry_str = expiry_date.strftime("%Y-%m-%d")
                    new_lines.append(f"{phone}#{password}#{expiry_str}#锚定:{now_str}\n")
                    anchor_time = now_str
                    anchored.append(
                        {
                            "phone": phone,
                            "days": raw_expiry,
                            "date": expiry_str,
                            "at": now_str,
                        }
                    )
                else:
                    new_lines.append(raw_line)
        else:
            expiry_date = MAX_EXPIRY_DATE
            new_lines.append(raw_line)

        days_remain = (expiry_date - today).days
        accounts.append((phone, password, expiry_date, days_remain, days_remain >= 0, anchor_time))

    if need_rewrite:
        try:
            with open(ACCOUNTS_FILE, "w", encoding="utf-8") as file:
                file.writelines(new_lines)
            print("-" * 65)
            print("首次锚定（天数 -> 固定日期）")
            for item in anchored:
                print(f"  {mask_phone(item['phone'])}: #{item['days']} -> #{item['date']}  (锚定于 {item['at']})")
            print("-" * 65)
        except Exception as e:
            print(f"回写失败: {e}")

    total_accounts = len(accounts)
    valid_count = sum(1 for account in accounts if account[4])
    expired_count = total_accounts - valid_count

    print("")
    print("=" * 65)
    print(f"账号文件: {ACCOUNTS_FILE}")
    print("=" * 65)
    print(f"  总: {total_accounts}  有效: {valid_count}  过期: {expired_count}  上限: {MAX_EXPIRY_DATE}")
    if skipped:
        for line_number, content, reason in skipped:
            print(f"  第{line_number}行跳过: {content[:40]} -> {reason}")

    print("")
    print(
        "  "
        + pad_to_width("#", 4)
        + pad_to_width("手机号", 13)
        + pad_to_width("到期日", 12)
        + pad_to_width("剩余", 9, "right")
        + pad_to_width("状态", 12)
        + "锚定时间"
    )
    print("  " + "─" * 4 + "─" * 13 + "─" * 12 + "─" * 9 + "─" * 12 + "─" * 18)

    for index, (phone, _, expiry_date, days_remain, is_valid, anchor_time) in enumerate(accounts):
        masked_phone = mask_phone(phone)
        expiry_str = expiry_date.strftime("%Y-%m-%d")
        anchor_str = anchor_time or "-"
        if not is_valid:
            status = "已过期"
            remain_str = f"过期{abs(days_remain)}天"
        elif days_remain == 0:
            status = "最后1天"
            remain_str = "今天到期"
        elif days_remain <= 3:
            status = "即将到期"
            remain_str = f"剩{days_remain}天"
        elif days_remain <= 7:
            status = f"{days_remain}天"
            remain_str = f"剩{days_remain}天"
        else:
            status = "正常"
            remain_str = f"剩{days_remain}天"
        print(
            "  "
            + pad_to_width(str(index + 1), 4)
            + pad_to_width(masked_phone, 13)
            + pad_to_width(expiry_str, 12)
            + pad_to_width(remain_str, 9, "right")
            + pad_to_width(status, 12)
            + anchor_str
        )

    if expired_count > 0:
        print("")
        print("  过期跳过:")
        for phone, _, expiry_date, days_remain, is_valid, _ in accounts:
            if not is_valid:
                print(f"    - {mask_phone(phone)} ({expiry_date}, 过期{abs(days_remain)}天)")
    print("=" * 65)
    return accounts


def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        return [(phone, password, expiry_date, days_remain, is_valid) for
                phone, password, expiry_date, days_remain, is_valid, _ in load_accounts_from_file()]
    if ACCOUNTS_STR:
        print("从环境变量加载")
        return [(phone, password, expiry_date, days_remain, is_valid) for
                phone, password, expiry_date, days_remain, is_valid, _ in parse_accounts_from_env(ACCOUNTS_STR)]
    print("无账号")
    create_template_accounts_file()
    return []


def parse_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def parse_iso_date(date_text):
    if not date_text:
        return None
    date_part = str(date_text).split("T")[0].strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.datetime.strptime(date_part, fmt).date()
        except ValueError:
            continue
    return None


def parse_encrypted_json(crypto_inst, response):
    dec_text = crypto_inst.decrypt(response.text)
    try:
        return dec_text, json.loads(dec_text)
    except Exception:
        return dec_text, {}


def extract_response_code(dec_text):
    try:
        return str(json.loads(dec_text).get("code", ""))
    except Exception:
        match = re.search(r'"code"\s*:\s*"?(?P<code>\d+)"?', dec_text)
        return match.group("code") if match else ""


def extract_response_desc(dec_text):
    try:
        data = json.loads(dec_text)
        return str(data.get("desc") or data.get("message") or "")
    except Exception:
        match = re.search(r'"(?:desc|message)"\s*:\s*"(?P<msg>[^"]*)"', dec_text)
        return match.group("msg") if match else dec_text


def mask_or_plain(phone):
    return mask_phone(phone) if phone and len(phone) >= 7 else str(phone)


def extract_invitation_code(raw_value):
    if not raw_value:
        return ""

    value = raw_value.strip()
    if not value:
        return ""

    if "invitationCode=" in value:
        parsed = urllib.parse.urlparse(value if "://" in value else f"https://dummy.local/{value.lstrip('?')}")
        query = urllib.parse.parse_qs(parsed.query)
        invitation_code = query.get("invitationCode", [""])[0].strip()
        if invitation_code:
            return invitation_code

    if value.startswith("?"):
        query = urllib.parse.parse_qs(value.lstrip("?"))
        invitation_code = query.get("invitationCode", [""])[0].strip()
        if invitation_code:
            return invitation_code

    if not re.fullmatch(r"\d{11}", value) and not (value.isdigit() and len(value) < 11):
        return value
    return ""


def split_target_specs(raw_text):
    if not raw_text:
        return []
    return [item.strip() for item in re.split(r"[\r\n,，;；]+", raw_text) if item.strip()]


def build_invitation_link(invitation_code):
    return f"https://ai.imusic.cn/h5v/fusion/ai-luck-win?cc={CHANNEL_ID}&invitationCode={invitation_code}"


def parse_pre_assist_targets(target_specs):
    targets = []
    seen_codes = set()
    for target_spec in target_specs:
        invitation_code = extract_invitation_code(target_spec)
        if not invitation_code or invitation_code in seen_codes:
            continue
        seen_codes.add(invitation_code)
        targets.append({
            "code": invitation_code,
            "label": target_spec,
            "link": build_invitation_link(invitation_code),
        })
    return targets


def normalize_account_target_spec(target_spec, accounts):
    if not target_spec:
        return None
    if target_spec.isdigit() and len(target_spec) < 11:
        account_index = int(target_spec) - 1
        if 0 <= account_index < len(accounts):
            return accounts[account_index][0]
        return None
    for phone, _ in accounts:
        if phone == target_spec:
            return phone
    return None


def resolve_assist_targets(accounts):
    return resolve_assist_targets_with_config(accounts, ASSIST_MODE, ASSIST_TARGETS)


def resolve_assist_targets_with_config(accounts, assist_mode, assist_target_specs):
    if assist_mode not in {"off", "random", "specified"}:
        print(f"助力模式无效，已关闭: {assist_mode}")
        return "off", []
    if assist_mode != "specified":
        return assist_mode, []

    resolved_targets = []
    for target_spec in assist_target_specs:
        target_phone = normalize_account_target_spec(target_spec, accounts)
        if target_phone and target_phone not in resolved_targets:
            resolved_targets.append(target_phone)

    if not resolved_targets:
        print("指定助力模式下未匹配到任何目标账号，已关闭助力")
        return "off", []
    return "specified", resolved_targets


def pick_assist_phone(helper_phone, assist_mode, target_phones, invitation_codes, make_index):
    if assist_mode == "off":
        return None

    if assist_mode == "specified":
        candidates = [phone for phone in target_phones if phone != helper_phone and invitation_codes.get(phone)]
        if not candidates:
            return None
        return candidates[make_index % len(candidates)]

    candidates = [phone for phone in invitation_codes if phone != helper_phone and invitation_codes.get(phone)]
    if not candidates:
        return None
    return random.choice(candidates)


def normalize_proxy_url(proxy_url):
    if not proxy_url:
        return None
    return proxy_url if "://" in proxy_url else f"http://{proxy_url}"


def ensure_runtime_ready():
    if CURL_CFFI_IMPORT_ERROR is None:
        return True
    print("缺少运行依赖: curl_cffi")
    print("请先安装后再运行:")
    print("  python -m pip install curl_cffi")
    print(f"原始报错: {CURL_CFFI_IMPORT_ERROR}")
    return False


def build_session(proxy_url=None):
    if not ensure_runtime_ready():
        raise RuntimeError("curl_cffi not installed")
    session_kwargs = {"impersonate": "chrome120"}
    normalized_proxy = normalize_proxy_url(proxy_url)
    if normalized_proxy:
        session_kwargs["proxies"] = {
            "http": normalized_proxy,
            "https": normalized_proxy,
        }
    return requests.Session(**session_kwargs)


def do_login(session, crypto_inst, phone, password):
    print("--- 1. 电信登录 & 获取凭证 ---")
    ts_l = time.strftime("%Y%m%d%H%M%S")
    en_p = "".join(chr(ord(c) + 2) for c in phone)
    en_pwd = "".join(chr(ord(c) + 2) for c in password)

    login_body = {
        "headerInfos": {"code": "userLoginNormal", "timestamp": ts_l, "shopId": "20002", "source": "110003",
                        "sourcePassword": "Sid98s", "userLoginName": en_p,
                        "clientType": "#11.3.0#channel50#iPhone 14 Pro Max#"},
        "content": {"fieldData": {"loginType": "4", "loginAuthCipherAsymmertric": rsa_encrypt(
            f"iPhone 14 15.4.{crypto_inst.rdm[:12]}{phone}{ts_l}{password}0$$$0."), "deviceUid": crypto_inst.rdm,
                                  "phoneNum": en_p, "authentication": en_pwd}}
    }
    res_l = session.post("https://appgologin.189.cn:9031/login/client/userLoginNormal", json=login_body).json()

    if res_l.get("responseData", {}).get("resultCode") != "0000":
        print(f"❌ 电信账密登录失败: {res_l}")
        raise Exception("Telecom Login Fail")

    l_succ = res_l["responseData"]["data"]["loginSuccessResult"]
    tk_val, uid = l_succ['token'], l_succ['userId']
    print("✓ 账密验证通过，正在换取 Ticket...")

    xml = f"<Request><HeaderInfos><Code>getSingle</Code><Timestamp>{ts_l}</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>{tk_val}</Token><UserLoginName>{phone}</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>{des3_op(str(uid))}</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>"
    res_xml = session.post("https://appgologin.189.cn:9031/map/clientXML", data=xml,
                           headers={"Content-Type": "application/xml"}).text

    tk_match = re.search(r'<Ticket>(.*?)</Ticket>', res_xml)
    if not tk_match:
        print("❌ Ticket 获取失败！")
        raise Exception("Ticket Regex Match Fail")

    ticket = des3_op(tk_match.group(1), decrypt=True)

    print("--- 2. SSO 登录 & 身份指纹激活 ---")
    sso_data = {"portal": "45", "channelId": CHANNEL_ID, "ticket": ticket, "user118100cn": "user118100cn"}
    res_sso = session.post("https://ai.imusic.cn/vapi/vue_login/sso_login_v2", json=sso_data).json()

    return res_sso.get("token"), res_sso.get("mobile"), res_sso.get("enDataCode"), ticket


def warmup_session(session, crypto_inst, token, mobile):
    print("--- 3. 环境全量模拟 (Warmup) ---")
    active_token = token

    h_share = get_headers(crypto_inst, active_token, is_share=True)
    res1 = session.post(
        f"https://ai.imusic.cn/vapi/new_member/get_user_info?channelId={CHANNEL_ID}&portal=45&mobile={mobile}",
        headers=h_share, data="")
    active_token = check_and_update_token(res1, active_token)

    h_share = get_headers(crypto_inst, active_token, is_share=True)
    res2 = session.post(
        f"https://ai.imusic.cn/vapi/vrbt/check_user_state?mobile={mobile}&is4G=1&is5G=1&isDX=1&channelId={CHANNEL_ID}&portal=45",
        headers=h_share, data="")
    active_token = check_and_update_token(res2, active_token)

    en_init = crypto_inst.encrypt({"channelId": CHANNEL_ID, "portal": "45", "mobile": mobile, "method": "init"})
    h_share = get_headers(crypto_inst, active_token, is_share=True)
    res3 = session.post(f"https://ai.imusic.cn/hapi/en/api?formData={urllib.parse.quote(en_init)}", headers=h_share,
                        data="")
    active_token = check_and_update_token(res3, active_token)

    ugc_p = crypto_inst.encrypt({"channelId": CHANNEL_ID, "portal": "45", "mobile": mobile})
    h_share = get_headers(crypto_inst, active_token, is_share=True)
    res4 = session.post(f"https://ai.imusic.cn/hapi/diy_ugc/imu/get_ugc_info?formData={urllib.parse.quote(ugc_p)}",
                        headers=h_share, data="")
    active_token = check_and_update_token(res4, active_token)

    time.sleep(0.5)
    return active_token


def query_template_meta(session, token):
    h = get_headers(ImCrypto(), token, is_share=False)
    res = session.post(
        f"https://ai.imusic.cn/hapi/de/api?pageNo=1&pageSize=50&activityId={ACTIVITY_ID}&apiName=diy%2FDiyVideoApi%2FqueryActRecommendTemplateList&channelId={CHANNEL_ID}&portal=45",
        headers=h,
        data=""
    )
    data = res.json()
    for item in data.get("data", {}).get("list", []):
        if item.get("templateId") == TEMPLATE_ID:
            return {
                "templateConfId": item.get("templateConfId") or TEMPLATE_CONF_ID,
                "userWords": item.get("userWords") or "古风插画，姐姐坐在秋千上。",
                "videoName": item.get("videoName") or "创作",
                "background": item.get("background") or "",
                "isAI": 1 if str(item.get("isAI", 0)) == "1" else 0,
                "arrangeId": item.get("arrangeId") or "",
            }
    return {
        "templateConfId": TEMPLATE_CONF_ID,
        "userWords": "古风插画，姐姐坐在秋千上。",
        "videoName": "创作",
        "background": "",
        "isAI": 0,
        "arrangeId": "",
    }


def query_template_list(session, token, page_no=1, page_size=50):
    h = get_headers(ImCrypto(), token, is_share=False)
    res = session.post(
        f"https://ai.imusic.cn/hapi/de/api?pageNo={page_no}&pageSize={page_size}&activityId={ACTIVITY_ID}&apiName=diy%2FDiyVideoApi%2FqueryActRecommendTemplateList&channelId={CHANNEL_ID}&portal=45",
        headers=h,
        data=""
    )
    data = res.json()
    templates = []
    for item in data.get("data", {}).get("list", []) or []:
        template_id = item.get("templateId") or ""
        template_conf_id = item.get("templateConfId") or ""
        if not template_id or not template_conf_id:
            continue
        templates.append({
            "templateId": template_id,
            "templateConfId": template_conf_id,
            "userWords": item.get("userWords") or "古风插画，姐姐坐在秋千上。",
            "videoName": item.get("videoName") or "创作",
            "background": item.get("background") or "",
            "isAI": 1 if str(item.get("isAI", 0)) == "1" else 0,
            "arrangeId": item.get("arrangeId") or "",
            "imageCount": parse_int(item.get("imageCount"), 0),
            "wordCount": parse_int(item.get("wordCount"), 0),
            "imagePutTip": item.get("imagePutTip") or "",
        })
    return templates


def is_template_compatible_for_auto_make(template_meta):
    return parse_int(template_meta.get("imageCount"), 0) <= 0


def post_encrypted_api(session, crypto_inst, token, api_path, payload, is_share=False):
    enc_str = crypto_inst.encrypt(payload)
    api_url = f"https://ai.imusic.cn{api_path}?formData={urllib.parse.quote(enc_str)}"
    h = get_headers(crypto_inst, token, is_share=is_share)
    res = session.post(api_url, headers=h, data="")
    return res, check_and_update_token(res, token)


def send_stat_message(session, crypto_inst, token, mobile, actname, actparam):
    payload = OrderedDict([
        ("channelId", CHANNEL_ID),
        ("portal", "45"),
        ("mobile", mobile),
        ("actname", actname),
        ("actparam", actparam),
        ("sid", "")
    ])
    return post_encrypted_api(session, crypto_inst, token, "/vapi/vue_stat/sendMessage", payload, is_share=False)


def query_fun_play_score(session, crypto_inst, token, mobile):
    res, active_token = post_encrypted_api(
        session,
        crypto_inst,
        token,
        "/hapi/en/api",
        OrderedDict([
            ("activityId", ACTIVITY_ID),
            ("mobile", mobile),
            ("apiName", "act/LaborApi/getFunPlayTotalScoreOrRemainingScore"),
            ("channelId", CHANNEL_ID),
            ("portal", "45")
        ]),
        is_share=False
    )
    dec_text = crypto_inst.decrypt(res.text)
    score_data = {}
    try:
        score_data = json.loads(dec_text).get("data", {}) or {}
        # 积分信息不再单独打印，最后统一输出
    except Exception:
        pass
    return active_token, score_data


def query_fun_play_points_award_page(session, crypto_inst, token, mobile, page_no=1, page_size=POINT_AWARD_PAGE_SIZE):
    res, active_token = post_encrypted_api(
        session,
        crypto_inst,
        token,
        "/hapi/en/api",
        OrderedDict([
            ("activityId", ACTIVITY_ID),
            ("mobile", mobile),
            ("pageNo", page_no),
            ("pageSize", page_size),
            ("apiName", "act/LaborApi/funPlayFestivalPointsAwardList"),
            ("channelId", CHANNEL_ID),
            ("portal", "45")
        ]),
        is_share=False
    )
    dec_text, data = parse_encrypted_json(crypto_inst, res)
    return active_token, data.get("data", {}) or {}, dec_text


def query_all_fun_play_points_awards(session, crypto_inst, token, mobile, page_size=POINT_AWARD_PAGE_SIZE):
    active_token = token
    page_no = 1
    total_pages = 1
    all_awards = []

    while page_no <= total_pages:
        active_token, award_page, dec_text = query_fun_play_points_award_page(
            session,
            crypto_inst,
            active_token,
            mobile,
            page_no=page_no,
            page_size=page_size,
        )
        # 中奖记录总数不再单独打印

        page_items = award_page.get("list", []) or []
        if not isinstance(page_items, list):
            page_items = []
        all_awards.extend(page_items)

        parsed_pages = parse_int(award_page.get("pages"), total_pages)
        if parsed_pages <= 0:
            parsed_pages = 1 if page_items else 0
        total_pages = parsed_pages
        if total_pages == 0:
            break
        page_no += 1

    return active_token, all_awards


def redeem_fun_play_phone_bill_by_points(session, crypto_inst, token, mobile):
    res, active_token = post_encrypted_api(
        session,
        crypto_inst,
        token,
        "/hapi/en/api",
        OrderedDict([
            ("activityId", ACTIVITY_ID),
            ("mobile", mobile),
            ("apiName", "act/LaborApi/funPlayFestivalRedeemPrize"),
            ("channelId", CHANNEL_ID),
            ("portal", "45")
        ]),
        is_share=False
    )
    dec_text, data = parse_encrypted_json(crypto_inst, res)
    return active_token, data, dec_text


def claim_fun_play_award_by_id(session, crypto_inst, token, mobile, award_id):
    res, active_token = post_encrypted_api(
        session,
        crypto_inst,
        token,
        "/hapi/en/api",
        OrderedDict([
            ("mobile", mobile),
            ("awardId", award_id),
            ("activityId", ACTIVITY_ID),
            ("apiName", "act/LaborApi/funPlayEggCostRedeem"),
            ("channelId", CHANNEL_ID),
            ("portal", "45")
        ]),
        is_share=False
    )
    dec_text, data = parse_encrypted_json(crypto_inst, res)
    return active_token, data, dec_text


def is_phone_bill_award(item):
    award_name = str(item.get("awardName") or "")
    return "话费" in award_name


def collect_pending_phone_bill_awards(awards):
    pending_awards = []
    for item in awards:
        award_id = item.get("awardId")
        status_value = item.get("status")
        status = "" if status_value is None else str(status_value).strip()
        if not award_id or not is_phone_bill_award(item):
            continue
        if status == "0":
            pending_awards.append(item)
    return pending_awards


def auto_redeem_phone_bill_by_points(session, crypto_inst, token, mobile, remaining_score):
    redeem_count = max(0, remaining_score // POINT_REDEEM_COST_SCORE)
    if redeem_count <= 0:
        return token, True, 0

    active_token = token
    success_count = 0

    for redeem_index in range(1, redeem_count + 1):
        redeemed = False
        for retry in range(1, POINT_REDEEM_RETRY_LIMIT + 1):
            try:
                active_token, response_data, dec_text = redeem_fun_play_phone_bill_by_points(
                    session,
                    crypto_inst,
                    active_token,
                    mobile,
                )
                if str(response_data.get("code")) == "0000":
                    success_count += 1
                    redeemed = True
                    time.sleep(0.5)
                    break
            except Exception:
                pass
            time.sleep(0.5)

        if not redeemed:
            return active_token, False, success_count

    return active_token, True, success_count


def auto_claim_pending_phone_bill_awards(session, crypto_inst, token, mobile):
    active_token, awards = query_all_fun_play_points_awards(session, crypto_inst, token, mobile)
    pending_awards = collect_pending_phone_bill_awards(awards)
    if not pending_awards:
        return active_token, 0

    claimed_count = 0

    for item in pending_awards:
        award_id = item.get("awardId")
        claimed = False

        for retry in range(1, PHONE_BILL_CLAIM_RETRY_LIMIT + 1):
            try:
                active_token, response_data, dec_text = claim_fun_play_award_by_id(
                    session,
                    crypto_inst,
                    active_token,
                    mobile,
                    award_id,
                )
                if str(response_data.get("code")) == "0000":
                    claimed_count += 1
                    claimed = True
                    time.sleep(0.3)
                    break
            except Exception:
                pass
            time.sleep(0.3)

    return active_token, claimed_count


def query_make_pkg_info(session, crypto_inst, token, mobile, template_id=TEMPLATE_ID):
    res, active_token = post_encrypted_api(
        session,
        crypto_inst,
        token,
        "/hapi/en/api",
        OrderedDict([
            ("channelId", CHANNEL_ID),
            ("portal", "45"),
            ("mobile", mobile),
            ("templateId", template_id),
            ("aid", ACTIVITY_ID),
            ("apiName", "ismp/IsmpApi/queryAiMakePkgInfo")
        ]),
        is_share=False
    )
    _, data = parse_encrypted_json(crypto_inst, res)
    return active_token, data.get("data", {}) or {}


def query_fun_play_invitation_code(session, crypto_inst, token, value, query_type):
    res, active_token = post_encrypted_api(
        session,
        crypto_inst,
        token,
        "/hapi/en/api",
        OrderedDict([
            ("activityId", ACTIVITY_ID),
            ("mobile", value),
            ("type", query_type),
            ("apiName", "act/LaborApi/getFunPlayEncOrDecPhone"),
            ("channelId", CHANNEL_ID),
            ("portal", "45")
        ]),
        is_share=False
    )
    _, data = parse_encrypted_json(crypto_inst, res)
    return active_token, data.get("data") or ""


def request_fun_play_invitation_action(session, crypto_inst, token, value, query_type):
    res, active_token = post_encrypted_api(
        session,
        crypto_inst,
        token,
        "/hapi/en/api",
        OrderedDict([
            ("activityId", ACTIVITY_ID),
            ("mobile", value),
            ("type", query_type),
            ("apiName", "act/LaborApi/getFunPlayEncOrDecPhone"),
            ("channelId", CHANNEL_ID),
            ("portal", "45")
        ]),
        is_share=False
    )
    dec_text, data = parse_encrypted_json(crypto_inst, res)
    return active_token, dec_text, data


def query_current_issue_info(session, crypto_inst):
    res, _ = post_encrypted_api(
        session,
        crypto_inst,
        "",
        "/hapi/en/api",
        OrderedDict([
            ("activityId", ACTIVITY_ID),
            ("apiName", "act/LaborApi/getFunPlayCurrentIssueInfo"),
            ("channelId", CHANNEL_ID),
            ("portal", "45")
        ]),
        is_share=False
    )
    _, data = parse_encrypted_json(crypto_inst, res)
    return data.get("data", {}) or {}


def format_issue_day(issue_info):
    issue_name = issue_info.get("issueName") or "未知期数"
    start_date = parse_iso_date(issue_info.get("startTime"))
    end_date = parse_iso_date(issue_info.get("endTime"))
    today = datetime.date.today()

    if start_date and end_date:
        total_days = max(1, (end_date - start_date).days + 1)
        current_day = (today - start_date).days + 1
        return issue_name, max(1, current_day), total_days, start_date, end_date
    return issue_name, None, None, start_date, end_date


def prompt_lottery_limit():
    while True:
        raw_value = input("请输入本次每个账号最多抽几次（回车=全抽，0=不抽）: ").strip()
        if raw_value == "":
            return None
        if raw_value.isdigit():
            return int(raw_value)
        print("请输入数字，例如 0、5、10")


def show_current_issue_summary(proxy_url=None):
    try:
        session = build_account_session(proxy_url)
        crypto_inst = ImCrypto()
        issue_info = query_current_issue_info(session, crypto_inst)
        issue_name, current_day, total_days, start_date, end_date = format_issue_day(issue_info)
        print("\n当前活动期数信息:")
        print(f"  期数: {issue_name}")
        if start_date and end_date:
            print(f"  时间: {start_date} ~ {end_date}")
        if current_day and total_days:
            print(f"  进度: 第 {current_day} 天 / 共 {total_days} 天")
        issued_tickets = issue_info.get("issuedCouponsNum") or issue_info.get("ticketNum")
        if issued_tickets not in (None, ""):
            print(f"  已发券/票数: {issued_tickets}")
        return True
    except Exception as e:
        print(f"\n当前活动期数信息获取失败: {e}")


def get_random_pre_assist_link():
    """随机获取一个预助力链接"""
    import random
    return random.choice(FIXED_PRE_ASSIST_INVITATION_LINKS)


def get_pre_assist_targets_for_account(account_index=0, total_accounts=1):
    """
    为指定账号获取预助力目标
    模式:
    - "same": 所有账号使用同一个随机链接
    - "different": 每个账号各自随机选择链接
    """
    import random

    if PRE_ASSIST_RANDOM_MODE == "same":
        # 所有账号使用同一个随机链接，只在第一个账号时随机选择
        if account_index == 0:
            selected_link = random.choice(FIXED_PRE_ASSIST_INVITATION_LINKS)
            return parse_pre_assist_targets([selected_link])
        else:
            # 其他账号使用相同链接
            return None  # 表示使用相同的链接
    else:
        # 每个账号各自随机
        selected_link = random.choice(FIXED_PRE_ASSIST_INVITATION_LINKS)
        return parse_pre_assist_targets([selected_link])


def prompt_pre_assist_targets():
    env_targets = parse_pre_assist_targets(split_target_specs(PRE_ASSIST_TARGETS_RAW))
    if env_targets:
        print("\n本次登录后预助力目标（来自 AI096_PRE_ASSIST_TARGETS）:")
        for entry in env_targets:
            print(f"  - {entry['link']}")
        return env_targets

    while True:
        raw_value = input("请输入登录后先助力的邀请链接/邀请码（多个用逗号分隔，回车跳过）: ").strip()
        if raw_value == "":
            print("\n本次未配置登录后预助力目标")
            return []

        target_entries = parse_pre_assist_targets(split_target_specs(raw_value))
        if target_entries:
            print("\n本次登录后预助力目标:")
            for entry in target_entries:
                print(f"  - {entry['link']}")
            return target_entries

        print("未解析到有效邀请链接或邀请码，请重新输入")


def run_pre_assist_actions(session, crypto_inst, token, mobile, ticket, template_list, pre_assist_targets):
    if not pre_assist_targets:
        return token

    active_token = token
    for target_entry in pre_assist_targets:
        invitation_code = target_entry.get("code") or ""
        invitation_link = target_entry.get("link") or build_invitation_link(invitation_code)
        if not invitation_code:
            continue

        try:
            session.get(invitation_link, timeout=15)
        except Exception:
            pass

        active_token, decode_text, decode_data = request_fun_play_invitation_action(
            session,
            crypto_inst,
            active_token,
            invitation_code,
            2,
        )
        decode_code = str(decode_data.get("code", "")) if isinstance(decode_data, dict) else ""
        if decode_code != "0000":
            continue

        assist_success = False
        bad_template_keys = set()
        for template_meta in template_list:
            template_key = (template_meta["templateId"], template_meta["templateConfId"])
            if template_key in bad_template_keys:
                continue

            active_token, make_success, make_text = submit_make_once(
                session,
                crypto_inst,
                active_token,
                mobile,
                invitation_code,
                template_meta,
                ticket,
            )

            if make_success:
                assist_success = True
                break

            response_code = extract_response_code(make_text)
            response_desc = extract_response_desc(make_text)
            if response_code == "10001" or "浼犲叆鍙傛暟寮傚父" in response_desc:
                bad_template_keys.add(template_key)
                continue

            break

        time.sleep(0.8)

    return active_token


def run_lottery(session, crypto_inst, token, mobile, max_count=None):
    active_token, score_data = query_fun_play_score(session, crypto_inst, token, mobile)
    try:
        remaining_score = int(score_data.get("remainingScore") or 0)
    except Exception:
        remaining_score = 0

    lottery_count = remaining_score // LOTTERY_COST_SCORE
    if max_count is not None:
        lottery_count = min(lottery_count, max_count)
    if lottery_count <= 0:
        return active_token
    print(f"🎰 抽奖 {lottery_count} 次")

    for index in range(1, lottery_count + 1):
        res, active_token = post_encrypted_api(
            session,
            crypto_inst,
            active_token,
            "/hapi/en/api",
            OrderedDict([
                ("activityId", ACTIVITY_ID),
                ("mobile", mobile),
                ("apiName", "act/LaborApi/funPlayFestivalLottery"),
                ("channelId", CHANNEL_ID),
                ("portal", "45")
            ]),
            is_share=False
        )
        time.sleep(0.2)

    return active_token


def premake_prepare(session, crypto_inst, token, mobile, template_meta):
    active_token = token

    active_token, pkg_info = query_make_pkg_info(
        session,
        crypto_inst,
        active_token,
        mobile,
        template_meta.get("templateId", TEMPLATE_ID),
    )

    stat_events = [
        ("page_vring_index", f"玩转AI赢手机_activityID_{ACTIVITY_ID}_entrance_{CHANNEL_ID}"),
        ("activity_vring_make_1.9",
         f"_activityID_{ACTIVITY_ID}_templateID_{template_meta['templateId']}_entrance_{CHANNEL_ID}_templateconfID_{template_meta['templateConfId']}"),
        ("activity_2603AI-meet_25.1",
         f"activityID_{ACTIVITY_ID}_undefined_templateID_{template_meta['templateId']}_entrance_{CHANNEL_ID}_templateconfID_{template_meta['templateConfId']}"),
        ("page_2511AI-makeonekey_9",
         f"activityID_{ACTIVITY_ID}_templateID_{template_meta['templateId']}_entrance_{CHANNEL_ID}_templateConfID_{template_meta['templateConfId']}"),
        ("page_2511AI-makeonekey_3",
         f"activityID_{ACTIVITY_ID}_templateID_{template_meta['templateId']}_entrance_{CHANNEL_ID}_templateConfID_{template_meta['templateConfId']}"),
    ]
    for actname, actparam in stat_events:
        _, active_token = send_stat_message(session, crypto_inst, active_token, mobile, actname, actparam)
        time.sleep(0.08)

    return active_token, pkg_info


def make_request(session, crypto_inst, token, mobile, en_code, template_meta):
    rand_name = f"{template_meta['videoName']}{random.randint(100000, 999999)}"
    background_value = template_meta.get("background") or template_meta["templateId"]
    payload = OrderedDict([
        ("channelId", CHANNEL_ID), ("portal", "45"), ("mobile", mobile),
        ("openId", ""), ("makeId", ""), ("background", background_value), ("userPhotos", ""),
        ("userWords", template_meta["userWords"]),
        ("templateName", rand_name), ("videoName", rand_name),
        ("templateId", template_meta["templateId"]), ("templateConfId", template_meta["templateConfId"]),
        ("aid", ACTIVITY_ID),
        ("inviterMobile", en_code), ("isAI", 1), ("aiPack", 0), ("arrangeId", template_meta.get("arrangeId", "")),
        ("autoOrderUgc", 0), ("aiGatewayImagMakeId", ""), ("fromType", ""),
        ("sessionId", ""), ("voice", ""), ("invitationCode", en_code)
    ])
    # 模板参数不再打印
    enc_str = crypto_inst.encrypt(payload)
    api_url = f"https://ai.imusic.cn/hapi/diy_video/au/template_make_add_v2?formData={urllib.parse.quote(enc_str)}"

    h = get_headers(crypto_inst, token, is_share=False)
    return session.post(api_url, headers=h, data="")


def build_account_session(proxy_url=None):
    session = build_session(proxy_url)
    session.cookies.set('cc', CHANNEL_ID, domain='ai.imusic.cn')
    session.cookies.set('imusic', f'118100{int(time.time() * 1000)}', domain='ai.imusic.cn')
    session.cookies.set('loginState', 'true', domain='ai.imusic.cn')
    return session


def login_account_context(phone, password, proxy_url=None):
    session = build_account_session(proxy_url)
    crypto_inst = ImCrypto()
    token, mobile, en_code, ticket = do_login(session, crypto_inst, phone, password)
    active_token = warmup_session(session, crypto_inst, token, mobile)
    return session, crypto_inst, active_token, mobile, ticket, en_code


def determine_make_count(pkg_info, templates):
    remaining_make_times = parse_int(pkg_info.get("privilegeVrbtAIVideoLeftNum"), 0)
    if remaining_make_times > 0:
        return min(remaining_make_times, MAX_AUTO_MAKE_ATTEMPTS)
    return min(MAX_AUTO_MAKE_ATTEMPTS, max(1, len(templates)))


def is_success_code(dec_text, expected_code="0000"):
    try:
        return str(json.loads(dec_text).get("code")) == expected_code
    except Exception:
        return f'"code":"{expected_code}"' in dec_text or f'"code": "{expected_code}"' in dec_text


def submit_make_once(session, crypto_inst, token, mobile, invitation_code, template_meta, ticket):
    active_token, _ = premake_prepare(session, crypto_inst, token, mobile, template_meta)
    response = make_request(session, crypto_inst, active_token, mobile, invitation_code, template_meta)
    active_token = check_and_update_token(response, active_token)
    response_text = crypto_inst.decrypt(response.text)

    if "10013" not in response_text:
        return active_token, is_success_code(response_text), response_text

    try:
        trace_id = json.loads(response_text).get("imuTraceId")
    except Exception:
        trace_id = ""
    if not trace_id:
        return active_token, False, response_text

    h_remedy = get_headers(crypto_inst, active_token, True)
    _, active_token = send_stat_message(
        session,
        crypto_inst,
        active_token,
        mobile,
        "page_vring_index",
        f"玩转AI赢手机_activityID_{ACTIVITY_ID}_entrance_{CHANNEL_ID}"
    )
    time.sleep(0.05)
    _, active_token = send_stat_message(
        session,
        crypto_inst,
        active_token,
        mobile,
        "activity_vring_make_1.9",
        f"_activityID_{ACTIVITY_ID}_entrance_{CHANNEL_ID}"
    )

    remedy_payload = crypto_inst.encrypt({"method": "remedy", "traceId": trace_id, "mobile": mobile})
    remedy_response = session.post(
        f"https://ai.imusic.cn/hapi/en/api?formData={urllib.parse.quote(remedy_payload)}",
        headers=h_remedy,
        data=""
    )
    active_token = check_and_update_token(remedy_response, active_token)

    refresh_response = session.post(
        "https://ai.imusic.cn/vapi/vue_login/sso_login_v2",
        json={"portal": "45", "channelId": CHANNEL_ID, "ticket": ticket, "user118100cn": "user118100cn"}
    ).json()
    active_token = refresh_response.get("token") or active_token
    active_token, _ = premake_prepare(session, crypto_inst, active_token, mobile, template_meta)

    time.sleep(1)

    final_response = make_request(session, crypto_inst, active_token, mobile, invitation_code, template_meta)
    active_token = check_and_update_token(final_response, active_token)
    final_text = crypto_inst.decrypt(final_response.text)
    return active_token, is_success_code(final_text), final_text


def collect_invitation_codes(accounts, proxy_assignment):
    invitation_codes = {}
    print("\n开始预取账号邀约码...")
    for index, (phone, password) in enumerate(accounts, start=1):
        proxy_url = proxy_assignment.get(index - 1)
        try:
            session, crypto_inst, active_token, mobile, _, login_code = login_account_context(phone, password,
                                                                                              proxy_url)
            active_token, invitation_code = query_fun_play_invitation_code(session, crypto_inst, active_token, mobile,
                                                                           1)
            invitation_code = invitation_code or login_code or ""
            if invitation_code:
                invitation_codes[phone] = invitation_code
                print(f"  {index}. {mask_or_plain(phone)} -> 邀约码已获取")
            else:
                print(f"  {index}. {mask_or_plain(phone)} -> 未拿到邀约码")
        except Exception as e:
            print(f"  {index}. {mask_or_plain(phone)} -> 邀约码获取失败: {e}")
    return invitation_codes


def run_single_account(phone, password, proxy_url=None, assist_mode="off", assist_targets=None, invitation_codes=None, pre_assist_targets=None, draw_limit=None, enable_lottery=True):
    print(f"\n{'=' * 20} 开始处理账号 {phone} {'=' * 20}")
    print(f"当前代理: {proxy_url or '直连'}")

    session = None
    try:
        session, crypto_inst, active_token, mobile, ticket, login_code = login_account_context(phone, password, proxy_url)
        template_list = query_template_list(session, active_token)
        if not template_list:
            template_list = [query_template_meta(session, active_token)]
        compatible_templates = [item for item in template_list if is_template_compatible_for_auto_make(item)]
        if compatible_templates:
            print(f"可自动创作模板数: {len(compatible_templates)}/{len(template_list)}")
            template_list = compatible_templates
        else:
            print("未筛到纯文本模板，回退使用原模板列表")

        active_token = run_pre_assist_actions(
            session,
            crypto_inst,
            active_token,
            mobile,
            ticket,
            template_list,
            pre_assist_targets or [],
        )

        own_invitation_code = invitation_codes.get(phone) if invitation_codes else ""
        if not own_invitation_code:
            active_token, own_invitation_code = query_fun_play_invitation_code(session, crypto_inst, active_token, mobile, 1)
            if own_invitation_code and invitation_codes is not None:
                invitation_codes[phone] = own_invitation_code
        if not own_invitation_code:
            own_invitation_code = login_code or ""

        active_token, before_score_data = query_fun_play_score(session, crypto_inst, active_token, mobile)
        before_points = parse_int(before_score_data.get("remainingScore"), 0)

        active_token, pkg_info = query_make_pkg_info(session, crypto_inst, active_token, mobile)
        make_count = determine_make_count(pkg_info, template_list)
        total_score = before_score_data.get('totalScore', 0)
        remaining_score = before_score_data.get('remainingScore', 0)
        print(f"📊 当前积分: totalScore={total_score}, remainingScore={remaining_score}")
        print(f"计划创作次数: {make_count}")

        success_count = 0
        attempt_count = 0
        bad_template_keys = set()
        max_attempts = max(make_count * 3, len(template_list))
        last_response = ""
        while success_count < make_count and attempt_count < max_attempts:
            candidates = [
                item for item in template_list
                if (item["templateId"], item["templateConfId"]) not in bad_template_keys
            ]
            if not candidates:
                break
            template_meta = candidates[attempt_count % len(candidates)]
            assist_phone = pick_assist_phone(phone, assist_mode, assist_targets or [], invitation_codes or {}, success_count)
            invitation_code = (invitation_codes or {}).get(assist_phone) if assist_phone else ""
            if not invitation_code:
                invitation_code = ""

            print(f"\n--- 创作第 {success_count + 1}/{make_count} 次（尝试 {attempt_count + 1}）---")
            print(f"模板: {template_meta['templateId']} / {template_meta['templateConfId']}")
            if assist_phone:
                print(f"本次助力目标: {mask_or_plain(assist_phone)}")
            else:
                print("本次助力目标: 无")

            active_token, make_success, make_text = submit_make_once(
                session,
                crypto_inst,
                active_token,
                mobile,
                invitation_code,
                template_meta,
                ticket
            )
            last_response = make_text
            print(f"创作响应: {make_text}")
            if not make_success:
                if "10001" in make_text or "传入参数异常" in make_text:
                    bad_template_keys.add((template_meta["templateId"], template_meta["templateConfId"]))
                    attempt_count += 1
                    continue
                print("本次创作未成功，停止继续创作")
                break
            success_count += 1
            attempt_count += 1
            time.sleep(0.8)

        print(f"\n创作完成次数: {success_count}")

        active_token, after_score_data = query_fun_play_score(session, crypto_inst, active_token, mobile)
        after_points = parse_int(after_score_data.get("remainingScore"), 0)
        active_token, point_redeem_ok, point_redeem_count = auto_redeem_phone_bill_by_points(
            session,
            crypto_inst,
            active_token,
            mobile,
            after_points,
        )
        active_token, claimed_before_lottery = auto_claim_pending_phone_bill_awards(
            session,
            crypto_inst,
            active_token,
            mobile,
        )
        print(f"点数变化: {before_points} -> {after_points}")
        print(f"📊 当前积分: totalScore={after_score_data.get('totalScore', 0)}, remainingScore={after_points}")

        if not point_redeem_ok:
            print(f"✅ 账号 {phone} 处理完成")
            return True

        if enable_lottery:
            active_token = run_lottery(session, crypto_inst, active_token, mobile, max_count=draw_limit)
            active_token, claimed_after_lottery = auto_claim_pending_phone_bill_awards(
                session,
                crypto_inst,
                active_token,
                mobile,
            )
        print(f"✅ 账号 {phone} 处理完成")
        return True
    except Exception as e:
        print(f"💥 账号 {phone} 处理失败，原因: {str(e)}")
        return False



def run():
    if not ensure_runtime_ready():
        return
    loaded_accounts = load_accounts()
    accounts = [(phone, password) for phone, password, _, _, is_valid in loaded_accounts if is_valid]
    if not accounts:
        raise ValueError("没有可用账号，请检查 accounts.txt")
    print(f"共解析到 {len(accounts)} 个账号")

    proxy_manager.interactive_setup()
    if proxy_manager.proxy_source == proxy_manager.SOURCE_API:
        valid_proxies = []
        proxy_assignment = {i: None for i in range(len(accounts))}
        print("\n📡 API代理模式: 获取一个代理就立即跑一个账号")
    else:
        valid_proxies = proxy_manager.get_valid_proxies(len(accounts))
        proxy_assignment = proxy_manager.assign_proxies_to_accounts(accounts)

    if valid_proxies and proxy_manager.proxy_source != proxy_manager.SOURCE_API:
        print("\n📋 代理分配详情:")
        for index, (phone, _) in enumerate(accounts, start=1):
            assigned_proxy = proxy_assignment.get(index - 1)
            masked_phone = f"{phone[:3]}****{phone[-4:]}" if len(phone) >= 7 else phone
            print(f"  {index}. {masked_phone} -> {assigned_proxy or '直连'}")

    issue_proxy = valid_proxies[0] if valid_proxies else None
    show_current_issue_summary(issue_proxy)
    draw_limit = prompt_lottery_limit()
    used_proxies = {proxy for proxy in proxy_assignment.values() if proxy}
    print(f"\n本次抽奖设置: {'全抽' if draw_limit is None else draw_limit}")

    shared_pre_assist_targets = None  # 用于"same"模式共享链接

    for idx, (phone, password) in enumerate(accounts, start=1):
        print(f"\n#### [{idx}/{len(accounts)}] ####")

        # 为当前账号获取预助力目标
        if PRE_ASSIST_RANDOM_MODE == "same":
            if shared_pre_assist_targets is None:
                shared_pre_assist_targets = get_pre_assist_targets_for_account(0, len(accounts))
            pre_assist_targets = shared_pre_assist_targets
        else:
            pre_assist_targets = get_pre_assist_targets_for_account(idx - 1, len(accounts))

        current_proxy = proxy_assignment.get(idx - 1)
        if proxy_manager.proxy_source == proxy_manager.SOURCE_API:
            current_proxy = proxy_manager.acquire_fresh_proxy(exclude=used_proxies)
            if not current_proxy:
                masked_phone = f"{phone[:3]}****{phone[-4:]}" if len(phone) >= 7 else phone
                print(f"  ⚠️  {masked_phone} 当前未获取到可用代理，跳过该账号")
                continue
            used_proxies.add(current_proxy)
            print(f"  🚀 当前账号使用新代理: {current_proxy}")
        success = run_single_account(
            phone,
            password,
            current_proxy,
            assist_mode="off",
            assist_targets=[],
            invitation_codes={},
            pre_assist_targets=pre_assist_targets,
            draw_limit=draw_limit,
            enable_lottery=True,
        )
        if success or proxy_manager.proxy_source != proxy_manager.SOURCE_API:
            continue

        masked_phone = f"{phone[:3]}****{phone[-4:]}" if len(phone) >= 7 else phone
        for retry_round in range(2, ACCOUNT_PROXY_RETRY_LIMIT + 1):
            replacement_proxy = proxy_manager.acquire_fresh_proxy(
                exclude=used_proxies | ({current_proxy} if current_proxy else set()))
            if not replacement_proxy:
                print(f"  ⚠️  {masked_phone} 未获取到新的可用代理，不再重试")
                break
            used_proxies.add(replacement_proxy)
            current_proxy = replacement_proxy
            print(f"  🔁 {masked_phone} 更换新代理重试 {retry_round}/{ACCOUNT_PROXY_RETRY_LIMIT}: {replacement_proxy}")
            success = run_single_account(
                phone,
                password,
                current_proxy,
                assist_mode="off",
                assist_targets=[],
                invitation_codes={},
                pre_assist_targets=pre_assist_targets,
                draw_limit=draw_limit,
                enable_lottery=True,
            )
            if success:
                break


def input(prompt=""):
    return ""


def get_env_draw_limit():
    raw_value = str(DEFAULT_DRAW_LIMIT).strip()
    if raw_value == "":
        return 3
    if raw_value.lower() in {"all", "full", "none"}:
        return None
    if raw_value.isdigit():
        return int(raw_value)
    print(f"\nAI096_DRAW_LIMIT 配置无效，已回退默认值 3: {raw_value}")
    return 3


def prompt_lottery_limit():
    draw_limit = get_env_draw_limit()
    print(f"\n本次抽奖设置来自环境变量 AI096_DRAW_LIMIT: {'全抽' if draw_limit is None else draw_limit}")
    return draw_limit


def run():
    if not ensure_runtime_ready():
        return

    loaded_accounts = load_accounts()
    accounts = [(phone, password) for phone, password, _, _, is_valid in loaded_accounts if is_valid]
    if not accounts:
        raise ValueError("没有可用账号，请检查 accounts.txt")

    print(f"共解析到 {len(accounts)} 个账号")

    proxy_manager.proxy_source = proxy_manager.SOURCE_API if DEFAULT_PROXY_API else proxy_manager.SOURCE_NONE
    proxy_manager.proxy_api = DEFAULT_PROXY_API
    proxy_manager.manual_proxies = []
    proxy_manager.valid_proxies = []

    if proxy_manager.proxy_source == proxy_manager.SOURCE_API:
        valid_proxies = []
        proxy_assignment = {i: None for i in range(len(accounts))}
        print("\n青龙模式: 已从环境变量 AI096_PROXY_API 启用代理 API")
    else:
        valid_proxies = []
        proxy_assignment = {i: None for i in range(len(accounts))}
        print("\n青龙模式: 未配置 AI096_PROXY_API，当前使用直连运行")

    show_current_issue_summary(None)
    draw_limit = prompt_lottery_limit()
    used_proxies = set()
    print(f"\n本次抽奖设置: {'全抽' if draw_limit is None else draw_limit}")

    shared_pre_assist_targets = None  # 用于"same"模式共享链接

    for idx, (phone, password) in enumerate(accounts, start=1):
        print(f"\n#### [{idx}/{len(accounts)}] ####")

        # 为当前账号获取预助力目标
        if PRE_ASSIST_RANDOM_MODE == "same":
            if shared_pre_assist_targets is None:
                shared_pre_assist_targets = get_pre_assist_targets_for_account(0, len(accounts))
            pre_assist_targets = shared_pre_assist_targets
        else:
            pre_assist_targets = get_pre_assist_targets_for_account(idx - 1, len(accounts))

        current_proxy = None
        if proxy_manager.proxy_source == proxy_manager.SOURCE_API:
            current_proxy = proxy_manager.acquire_fresh_proxy(exclude=used_proxies)
            if not current_proxy:
                masked_phone = f"{phone[:3]}****{phone[-4:]}" if len(phone) >= 7 else phone
                print(f"  未获取到可用代理，跳过账号: {masked_phone}")
                continue
            used_proxies.add(current_proxy)
            print(f"  当前账号使用代理: {current_proxy}")

        success = run_single_account(
            phone,
            password,
            current_proxy,
            assist_mode="off",
            assist_targets=[],
            invitation_codes={},
            pre_assist_targets=pre_assist_targets,
            draw_limit=draw_limit,
            enable_lottery=True,
        )

        if success or proxy_manager.proxy_source != proxy_manager.SOURCE_API:
            continue

        masked_phone = f"{phone[:3]}****{phone[-4:]}" if len(phone) >= 7 else phone
        for retry_round in range(2, ACCOUNT_PROXY_RETRY_LIMIT + 1):
            replacement_proxy = proxy_manager.acquire_fresh_proxy(
                exclude=used_proxies | ({current_proxy} if current_proxy else set()))
            if not replacement_proxy:
                print(f"  {masked_phone} 未获取到新的可用代理，不再重试")
                break
            used_proxies.add(replacement_proxy)
            current_proxy = replacement_proxy
            print(f"  {masked_phone} 更换代理重试 {retry_round}/{ACCOUNT_PROXY_RETRY_LIMIT}: {replacement_proxy}")
            success = run_single_account(
                phone,
                password,
                current_proxy,
                assist_mode="off",
                assist_targets=[],
                invitation_codes={},
                pre_assist_targets=pre_assist_targets,
                draw_limit=draw_limit,
                enable_lottery=True,
            )
            if success:
                break


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"程序异常退出: {e}")
        raise
    finally:
        input("\n按回车键退出...")