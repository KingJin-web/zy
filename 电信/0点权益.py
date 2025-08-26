#!/usr/bin/env python3
import os
import re
import sys
import ssl
import time
import json
import base64
import random
import certifi
import aiohttp
import asyncio
import datetime
import requests
import binascii
from http import cookiejar
from Crypto.Cipher import DES3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from aiohttp import ClientSession, TCPConnector

# 在全局变量区域添加停止事件
stop_all_event = asyncio.Event()  # 控制所有任务停止

# 🌸 标题 🌸
LOGO = f'''
  ✧･ﾟ: *✧･ﾟ:*  电信金豆换话费脚本  ✧･ﾟ: *✧･ﾟ:*
'''

run_num = os.environ.get('reqNUM') or "50"
MAX_RETRIES = 3
RATE_LIMIT = 15  # 每秒请求数限制

# 🌸 日志相关设置 🌸
yf = datetime.datetime.now().strftime("%Y%m")
try:
    with open('电信金豆换话费.log') as fr:
        dhjl = json.load(fr)
except:
    dhjl = {}
if yf not in dhjl:
    dhjl[yf] = {}


class RateLimiter:
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.tokens = rate_limit
        self.updated_at = time.monotonic()

    async def acquire(self):
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(0.1)
        self.tokens -= 1

    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.rate_limit
        if new_tokens > 1:
            self.tokens = min(self.tokens + new_tokens, self.rate_limit)
            self.updated_at = now


class AsyncSessionManager:
    def __init__(self):
        self.session = None
        self.connector = None

    async def __aenter__(self):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        self.connector = TCPConnector(ssl=ssl_context, limit=1000)
        self.session = ClientSession(connector=self.connector)
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        await self.connector.close()


async def retry_request(session, method, url, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            await asyncio.sleep(1)
            async with session.request(method, url, **kwargs) as response:
                return await response.json()

        except (aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError) as e:
            print(f"{Color.LIGHT_PINK}💔 请求失败，第 {attempt + 1} 次重试: {e}{Color.ENDC}")
            if attempt == MAX_RETRIES - 1:
                raise
            await asyncio.sleep(2 ** attempt)


class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


# 🌸 输出函数 🌸
def printn(m):
    current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f'\n🌸 [{current_time} {m}]')


context = ssl.create_default_context()
context.set_ciphers('DEFAULT@SECLEVEL=1')  # 低安全级别0/1
context.check_hostname = False  # 禁用主机
context.verify_mode = ssl.CERT_NONE  # 禁用证书


class DESAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)


requests.packages.urllib3.disable_warnings()
ss = requests.session()
ss.headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
    "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"}
ss.mount('https://', DESAdapter())
ss.cookies.set_policy(BlockAll())
runTime = 0
key = b'1234567`90koiuyhgtfrdews'
iv = 8 * b'\0'

public_key_b64 = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----'''

public_key_data = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----'''


def get_first_three(value):
    if isinstance(value, (int, float)):
        return f"{str(value)[:3]}****{str(value)[-4:]}"
    elif isinstance(value, str):
        return f"{value[:3]}****{value[-4:]}"
    else:
        raise TypeError("error")


def run_Time(hour, miute, second):
    date = datetime.datetime.now()
    date_zero = datetime.datetime.now().replace(year=date.year, month=date.month, day=date.day, hour=hour, minute=miute,
                                                second=second)
    date_zero_time = int(time.mktime(date_zero.timetuple()))
    return date_zero_time


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
    ciphertext = b''
    for i in range(0, len(plaintext_bytes), max_chunk_size):
        chunk = plaintext_bytes[i:i + max_chunk_size]
        encrypted_chunk = cipher.encrypt(chunk)
        ciphertext += encrypted_chunk
    return binascii.hexlify(ciphertext).decode()


def encode_phone(text):
    encoded_chars = []
    for char in text:
        encoded_chars.append(chr(ord(char) + 2))
    return ''.join(encoded_chars)


def getApiTime(api_url):
    try:
        with requests.get(api_url) as response:
            if (not response or not response.text):
                return time.time()
            json_data = json.loads(response.text)
            if (json_data.get("api") and json_data.get("api") not in ("time")):
                timestamp_str = json_data.get('data', {}).get('t', '')
            else:
                timestamp_str = json_data.get('currentTime', {})
            timestamp = int(timestamp_str) / 1000.0  # 将毫秒转为秒
            difftime = time.time() - timestamp
            return difftime;
    except Exception as e:
        print(f"💔 获取时间失败: {e}")
        return 0;


def userLoginNormal(phone, password):
    alphabet = 'abcdef0123456789'
    uuid = [''.join(random.sample(alphabet, 8)), ''.join(random.sample(alphabet, 4)),
            '4' + ''.join(random.sample(alphabet, 3)), ''.join(random.sample(alphabet, 4)),
            ''.join(random.sample(alphabet, 12))]
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = 'iPhone 14 15.4.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'
    try:
        r = ss.post('https://appgologin.189.cn:9031/login/client/userLoginNormal', json={
            "headerInfos": {"code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "",
                            "clientType": "#11.3.0#channel35#Xiaomi Redmi K30 Pro#", "shopId": "20002",
                            "source": "110003", "sourcePassword": "Sid98s", "token": "",
                            "userLoginName": encode_phone(phone)}, "content": {"attach": "test",
                                                                               "fieldData": {"loginType": "4",
                                                                                             "accountType": "",
                                                                                             "loginAuthCipherAsymmertric": b64(
                                                                                                 loginAuthCipherAsymmertric),
                                                                                             "deviceUid": uuid[0] +
                                                                                                          uuid[1] +
                                                                                                          uuid[2],
                                                                                             "phoneNum": encode_phone(
                                                                                                 phone),
                                                                                             "isChinatelecom": "0",
                                                                                             "systemVersion": "12",
                                                                                             "authentication": encode_phone(
                                                                                                 password)}}}).json()
        l = r['responseData']['data']['loginSuccessResult']
        if l:
            ticket = get_ticket(phone, l['userId'], l['token'])
            return ticket
        return False
    except Exception as e:
        print(f"💔 登录失败: {e}")
        return False


async def exchangeForDay(phone, session, run_num, rid, stime, accId):
    async def delayed_conversion(delay):
        await asyncio.sleep(delay)
        await conversionRights(phone, rid, session, accId)

    tasks = [asyncio.create_task(delayed_conversion(i * stime)) for i in range(int(run_num))]
    await asyncio.gather(*tasks)


def get_ticket(phone, userId, token):
    try:
        r = ss.post('https://appgologin.189.cn:9031/map/clientXML',
                    data='<Request><HeaderInfos><Code>getSingle</Code><Timestamp>' + datetime.datetime.now().strftime(
                        "%Y%m%d%H%M%S") + '</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>' + token + '</Token><UserLoginName>' + phone + '</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>' + encrypt(
                        userId) + '</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>',
                    headers={'user-agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1'},
                    verify=certifi.where())
        tk = re.findall('<Ticket>(.*?)</Ticket>', r.text)
        if len(tk) == 0:
            return False
        return decrypt(tk[0])
    except Exception as e:
        print(f"💔 获取ticket失败: {e}")
        return False


async def exchange(s, phone, title, aid, jsexec, ckvalue):
    try:
        url = "https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange"
        get_url = await asyncio.to_thread(jsexec.call, "getUrl", "POST", url)
        async with s.post(get_url, cookies=ckvalue, json={"activityId": aid}) as response:
            pass
    except Exception as e:
        print(f"💔 兑换出错: {e}")


async def check(s, item, ckvalue):
    checkGoods = s.get('https://wapact.189.cn:9001/gateway/stand/detailNew/check?activityId=' + item,
                       cookies=ckvalue).json()
    return checkGoods


async def conversionRights(phone, aid, session, accId):
    try:
        value = {
            "id": aid,
            "accId": accId,
            "showType": "9003",
            "showEffect": "8",
            "czValue": "0"
        }
        paraV = encrypt_para(value)

        printn(f"{get_first_three(phone)}: 开始兑换啦～ ✨")

        response = await asyncio.to_thread(
            session.post,
            'https://wappark.189.cn/jt-sign/paradise/receiverRights',
            json={"para": paraV}
        )

        login = response.json()
        printn(f"💔 {get_first_three(phone)}: 结果是 {login} 💬")
        if '兑换成功' in response.text:
            printn(f"{Color.MINT}🎉 恭喜呀！{get_first_three(phone)} 兑换成功啦！🎉")
            dhjl[yf]['等级话费'] += "#" + phone
            with open('电信金豆换话费.log', 'w') as f:
                json.dump(dhjl, f, ensure_ascii=False)
            return
        elif '已兑换' in response.text:
            printn(f"💖 {get_first_three(phone)} 已经兑换过咯～")
            dhjl[yf]['等级话费'] += "#" + phone
            with open('电信金豆换话费.log', 'w') as f:
                json.dump(dhjl, f, ensure_ascii=False)
            return

    except Exception as e:
        printn(f"💔 {get_first_three(phone)} 兑换时出错了: {str(e)}")


async def getLevelRightsList(phone, session, accId):
    try:
        value = {
            "type": "hg_qd_djqydh",
            "accId": accId,
            "shopId": "20001"
        }
        paraV = encrypt_para(value)

        response = session.post(
            'https://wappark.189.cn/jt-sign/paradise/queryLevelRightInfo',
            json={"para": paraV}
        )

        data = response.json()
        if data.get('code') == 401:
            print(f"💔 获取失败: {data}, 可能是sign过期了呢")
            return None

        current_level = int(data['currentLevel'])
        key_name = 'V' + str(current_level)
        ids = [item['activityId'] for item in data.get(key_name, []) if '话费' in item.get('title', '')]
        return ids

    except Exception as e:
        print(f"💔 获取失败, 重试一次: {str(e)}")
        try:
            paraV = encrypt_para(value)
            response = session.post(
                'https://wappark.189.cn/jt-sign/paradise/queryLevelRightInfo',
                json={"para": paraV}
            )

            data = response.json()
            if data.get('code') == 401:
                print(f"💔 重试获取失败: {data}, 可能是sign过期了呢")
                return None

            current_level = int(data['currentLevel'])
            key_name = 'V' + str(current_level)
            ids = [item['id'] for item in data.get(key_name, []) if item.get('name') == '话费']
            return ids

        except Exception as e:
            print(f"💔 重试也失败了: {str(e)}")
            return None


async def getSign(ticket, session):
    try:
        response = session.get(
            'https://wappark.189.cn/jt-sign/ssoHomLogin?ticket=' + ticket,
            headers={
                'User-Agent': "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36"}
        ).json()

        if response.get('resoultCode') == '0':
            sign = response.get('sign')
            accId = response.get('accId')
            return sign, accId
        else:
            print(f"💔 获取sign失败[{response.get('resoultCode')}]: {response}")
    except Exception as e:
        print(f"💔 getSign 出错了: {str(e)}")
    return None, None


async def qgNight(phone, ticket, timeDiff, isTrue):
    if isTrue:
        runTime = run_Time(23, 58, 30)
    else:
        runTime = 0

    if runTime > (time.time() + timeDiff):
        difftime = runTime - time.time() - timeDiff
        print(f"⏰ 当前时间: {str(datetime.datetime.now())[11:23]}, 要等一会儿哦～ 还要等 {difftime:.2f} 秒")
        await asyncio.sleep(difftime)

    session = requests.Session()
    session.mount('https://', DESAdapter())
    session.verify = False  # 禁用证书验证
    sign, accId = await getSign(ticket, session)

    if sign:
        session.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
            "sign": sign}
        printn(f"{get_first_three(phone)} 获取到sign啦～ 太好了！😊")
    else:
        print(f"{get_first_three(phone)} 💔 没有获取到sign呢...")
        return

    rightsId = await getLevelRightsList(phone, session, accId)
    if rightsId:
        printn(f"{get_first_three(phone)} 找到rightsId了: {rightsId[0]} 🌟")
    else:
        print(f"{get_first_three(phone)} 💔 没找到rightsId呢...")
        return

    if isTrue:
        runTime2 = run_Time(23, 59, 59) + 0.5
        difftime = runTime2 - time.time() - timeDiff
        printn(f"再等 {difftime:.2f} 秒就开始啦～ ⏳")
        await asyncio.sleep(difftime)
    else:
        # 测试模式：不等待，直接执行
        printn(f"测试模式，执行兑换测试～ 🧪")

    await exchangeForDay(phone, session, run_num, rightsId[0], 0.05, accId)


async def qgDay(phone, ticket, timeDiff, isTrue):
    async with AsyncSessionManager() as s:
        pass


async def main(timeDiff, isTRUE, hour):
    print(LOGO)
    print(f"✨ 脚本启动中～ 准备开始兑换话费啦！✨\n")

    tasks = []
    accounts = []
    for key, value in os.environ.items():
     if key == 'chinaTelecomAccount':
        accounts.extend(re.split(r'@|&',value))
    if not accounts:
        print(f"💔 错误: 没有设置 chinaTelecomAccount 环境变量哦～ 要写成 账号#密码 的格式呀 多账号用@分开～")
        return
    account_count = len(accounts)
    print(f"💖 发现 {len(accounts)} 个账号呢，准备开始处理啦～")

    for phoneV in accounts:
        value = phoneV.split('#')
        if len(value) != 2:
            print(f"💔 跳过无效格式: {phoneV}，要写成 账号#密码 哦 多账号用@分开～")
            continue

        phone, password = value[0], value[1]
        if '等级话费' not in dhjl[yf]:
            dhjl[yf]['等级话费'] = ""
        if phone in dhjl[yf]['等级话费']:
            printn(f"{get_first_three(phone)} 的等级话费已经兑换过啦～ 不用再弄咯～ 💖")
            continue

        printn(f'{get_first_three(phone)} 开始登录啦～ 🌸')
        ticket = userLoginNormal(phone, password)
        if ticket:
            printn(f'{get_first_three(phone)} 登录成功！太棒啦！🎉')
            if hour > 15:
                tasks.append(qgNight(phone, ticket, timeDiff, isTRUE))
            else:
                tasks.append(qgNight(phone, ticket, timeDiff, isTRUE))
        else:
            printn(f'{get_first_three(phone)} 登录失败了... 有点小伤心呢 💔')
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    h = datetime.datetime.now().hour
    print(f"⏰ 当前时间是 {h} 点哦～")

    if 10 > h > 0:
        print(f"☀️ 现在是 {h} 点，准备抢十点场次的话费啦～")
        wttime = run_Time(9, 59, 8)  # 抢十点场次
    elif 14 >= h >= 10:
        print(f"☀️ 现在是 {h} 点，准备抢十四点场次的话费啦～")
        wttime = run_Time(13, 59, 8)  # 抢十四点场次
    else:
        print(f"🌙 现在是 {h} 点，准备抢凌晨场次的话费啦～")
        wttime = run_Time(23, 57, 57)  # 抢凌晨场次

    isTRUE = True  # 实际用的时候设为True，测试的时候可以设为False哦

    if wttime > time.time():
        wTime = wttime - time.time()
        print(f"⏳ 还要等 {wTime:.2f} 秒才到时间呢～ 耐心等一下下哦～")
        if isTRUE:
            print(f"💡 小贴士: 记得先测试一下哦～ 要根据自己的网络调整参数呢～")
            print(f"💤 开始等待啦... 不要关掉窗口哦～")
            time.sleep(wTime)

    timeValue = 0  # 时间获取
    timeDiff = timeValue if timeValue > 0 else 0

    try:
        asyncio.run(main(timeDiff, isTRUE, h))
    except Exception as e:
        print(f"💔 脚本运行的时候出错了: {str(e)}")
    finally:
        print(f"\n💖 所有任务都完成啦～ 💖")