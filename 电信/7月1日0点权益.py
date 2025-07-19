"""
新电信抢话费

群里发的，未测试好，自测
修改内容如下“
1.删除内置的一个手机账号
2.修改环境变量名保持和拉菲电信金豆本环境变量一致
3.恢复瑞数通杀.js调用地址，确实也不知道是啥。398、399行注释

环境变量chinaTelecomAccount，值为：账号#密码

cron: 57 9,13,23 * * *
const $ = new Env("新电信抢话费");

"""
#!/usr/bin/env python3

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
import aiohttp
import asyncio
import certifi
import datetime
import requests
import binascii
from lxml import etree
from http import cookiejar
from Crypto.Cipher import AES
from Crypto.Cipher import DES3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from aiohttp import ClientSession, TCPConnector
from concurrent.futures import ThreadPoolExecutor
import subprocess

sys.stdout.reconfigure(encoding='utf-8')
import _locale
_locale._getdefaultlocale = (lambda *args: ['zh_CN', 'utf8'])

run_num=os.environ.get('reqNUM') or "1"

MAX_RETRIES = 3
RATE_LIMIT = 10  # 每秒请求数限制

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
                # return await response.json()

        except (aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError) as e:
            print(f"请求失败，第 {attempt + 1} 次重试: {e}")
            if attempt == MAX_RETRIES - 1:
                raise
            await asyncio.sleep(2 ** attempt)

class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False

def printn(m):
    current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f'\n[{current_time}] {m}')

context = ssl.create_default_context()
context.set_ciphers('DEFAULT@SECLEVEL=1')  # 低安全级别0/1
context.check_hostname = False  # 禁用主机
context.verify_mode = ssl.CERT_NONE  # 禁用证书

class DESAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

requests.packages.urllib3.disable_warnings()
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ss = requests.session()
ss.headers={"User-Agent":"Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36","Referer":"https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"}
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
    # 处理数字情况
    if isinstance(value, (int, float)):
        return int(str(value)[:3])
    elif isinstance(value, str):
        return str(value)[:3]
    else:
        raise TypeError("error")

def run_Time(hour,miute,second):
    date = datetime.datetime.now()
    date_zero = datetime.datetime.now().replace(year=date.year, month=date.month, day=date.day, hour=hour, minute=miute, second=second)
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
    ciphertext = cipher.encrypt(plaintext.encode())
    return binascii.hexlify(ciphertext).decode()

def encrypt_paraNew(p):
    k = RSA.import_key(public_key_data)
    c = PKCS1_v1_5.new(k)
    s = k.size_in_bytes() - 11
    d = p.encode() if isinstance(p, str) else json.dumps(p).encode()
    return binascii.hexlify(b''.join(c.encrypt(d[i:i+s]) for i in range(0, len(d), s))).decode()

def encode_phone(text):
    encoded_chars = []
    for char in text:
        encoded_chars.append(chr(ord(char) + 2))
    return ''.join(encoded_chars)


def getApiTime(api_url):
        try:
             with requests.get(api_url) as response:
                if(not response or not response.text):
                    return time.time()
                json_data = json.loads(response.text)
                if (json_data.get("api")and json_data.get("api")not in("time") ):
                    timestamp_str = json_data.get('data', {}).get('t', '')
                else:
                    timestamp_str = json_data.get('currentTime', {})
                timestamp = int(timestamp_str) / 1000.0  # 将毫秒转为秒
                difftime=time.time()-timestamp
                return difftime;
        except Exception as e:
            print(f"获取时间失败: {e}")
            return 0;


def userLoginNormal(phone,password):
    alphabet = 'abcdef0123456789'
    uuid = [''.join(random.sample(alphabet, 8)),''.join(random.sample(alphabet, 4)),'4'+''.join(random.sample(alphabet, 3)),''.join(random.sample(alphabet, 4)),''.join(random.sample(alphabet, 12))]
    timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = 'iPhone 14 15.4.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'
    #r = ss.post('https://appgologin.189.cn:9031/login/client/userLoginNormal',json={"headerInfos": {"code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "", "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "token": "", "userLoginName": phone}, "content": {"attach": "test", "fieldData": {"loginType": "4", "accountType": "", "loginAuthCipherAsymmertric": b64(loginAuthCipherAsymmertric), "deviceUid": uuid[0] + uuid[1] + uuid[2], "phoneNum": encode_phone(phone), "isChinatelecom": "0", "systemVersion": "15.4.0", "authentication": password}}},verify=certifi.where()).json()
    r = ss.post('https://appgologin.189.cn:9031/login/client/userLoginNormal',json={"headerInfos": {"code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "", "clientType": "#11.3.0#channel35#Xiaomi Redmi K30 Pro#", "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "token": "", "userLoginName": encode_phone(phone)}, "content": {"attach": "test", "fieldData": {"loginType": "4", "accountType": "", "loginAuthCipherAsymmertric": b64(loginAuthCipherAsymmertric), "deviceUid": uuid[0] + uuid[1] + uuid[2], "phoneNum": encode_phone(phone), "isChinatelecom": "0", "systemVersion": "12", "authentication": encode_phone(password)}}},verify=certifi.where()).json()
    l = r['responseData']['data']['loginSuccessResult']
    if l:
        ticket = get_ticket(phone,l['userId'],l['token'])
        return ticket
    return False

async def exchangeForDay(phone, session, run_num, rid, stime, accId):
    async def delayed_conversion(delay):
        await asyncio.sleep(delay)
        await conversionRights(phone, rid, session, accId)
    tasks = [asyncio.create_task(delayed_conversion(i * stime)) for i in range(int(run_num))]
    await asyncio.gather(*tasks)
def get_ticket(phone,userId,token):
    r = ss.post('https://appgologin.189.cn:9031/map/clientXML',data='<Request><HeaderInfos><Code>getSingle</Code><Timestamp>'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>'+token+'</Token><UserLoginName>'+phone+'</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>'+encrypt(userId)+'</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>',headers={'user-agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1'},verify=certifi.where())
    tk = re.findall('<Ticket>(.*?)</Ticket>',r.text)
    if len(tk) == 0:
        return False
    return decrypt(tk[0])

async def exchange(s, phone, title, rid,jsexec, ckvalue):
    try:
        url="https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange"

        get_url = await asyncio.to_thread(jsexec.call,"getUrl", "POST",url)
        async with s.post(get_url, cookies=ckvalue, json={"activityId": rid}) as response:
            pass
    except Exception as e:
        print(e)



async def check(s,item,ckvalue):
    checkGoods = s.get('https://wapact.189.cn:9001/gateway/stand/detailNew/check?activityId=' + item, cookies=ckvalue).json()
    return checkGoods

async def conversionRights(phone, rid, session, accId):
    try:
        # 获取 Ruishu cookies
        ruishu_cookies = get_ruishu_cookies()
        if not ruishu_cookies:
            print(f"{get_first_three(phone)}: 无法获取 Ruishu cookies")
            return

        value = {
            "id": rid,
            "accId": accId,
            "showType": "9003",
            "showEffect": "8",
            "czValue": "0"
        }
        paraV = encrypt_paraNew(value)

        printn(f"{get_first_three(phone)}:开始兑换")

        # 使用 Ruishu cookies 发送请求
        response = session.post(
            'https://wappark.189.cn/jt-sign/paradise/receiverRights',
            json={"para": paraV},
            cookies=ruishu_cookies
        )

        login = response.json()
        printn(f"{get_first_three(phone)}:{login}")

        if '兑换成功' in response.text:
            QLAPI.notify(get_first_three(phone), login['resoultMsg'])
            exit(0)

    except Exception as e:
        printn(f"{get_first_three(phone)}: 兑换请求发生错误: {str(e)}")
        # 可以选择是否在这里添加重试逻辑

async def getLevelRightsList(phone, session, accId):
    try:
        # 获取 Ruishu cookies
        ruishu_cookies = get_ruishu_cookies()
        if not ruishu_cookies:
            print("无法获取 Ruishu cookies")
            return None

        value = {
            "type": "hg_qd_djqydh",
            "accId": accId,
            "shopId": "20001"
        }
        paraV = encrypt_paraNew(value)

        # 使用 Ruishu cookies 发送请求
        response = session.post(
            'https://wappark.189.cn/jt-sign/paradise/queryLevelRightInfo',
            json={"para": paraV},
            cookies=ruishu_cookies
        )

        data = response.json()
        if data.get('code') == 401:
            print(f"获取失败:{data},原因大概是sign过期了")
            return None

        current_level = int(data['currentLevel'])
        key_name = 'V' + str(current_level)
        ids = [item['activityId'] for item in data.get(key_name, []) if '话费' in item.get('title',"")]
        return ids

    except Exception as e:
        print(f"获取失败,重试一次: {str(e)}")
        try:
            # 重试时重新获取 Ruishu cookies
            ruishu_cookies = get_ruishu_cookies()
            if not ruishu_cookies:
                print("重试时无法获取 Ruishu cookies")
                return None

            paraV = encrypt_para(value)
            response = session.post(
                'https://wappark.189.cn/jt-sign/paradise/getLevelRightsList',
                json={"para": paraV},
                cookies=ruishu_cookies
            )

            data = response.json()
            if data.get('code') == 401:
                print(f"重试获取失败:{data},原因大概是sign过期了")
                return None

            current_level = int(data['currentLevel'])
            key_name = 'V' + str(current_level)
            ids = [item['activityId'] for item in data.get(key_name, []) if '话费' in item.get('title',"")]
            return ids

        except Exception as e:
            print(f"重试也失败了: {str(e)}")
            return None

def get_ruishu_cookies():
    try:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ruishu_path = os.path.join(current_dir, 'Ruishu.py')

        # 执行 Ruishu.py 并获取输出
        result = subprocess.run([sys.executable, ruishu_path],
                              capture_output=True,
                              text=True)

        if result.returncode != 0:
            print(f"Ruishu.py 执行错误: {result.stderr}")
            return None

        # 解析输出的 JSON
        cookies = json.loads(result.stdout.strip())
        return cookies

    except Exception as e:
        print(f"获取 Ruishu cookies 时发生错误: {str(e)}")
        return None

async def getSign(ticket, session):
    try:
        # 获取 Ruishu cookies
        ruishu_cookies = get_ruishu_cookies()
        if not ruishu_cookies:
            print("无法获取 Ruishu cookies")
            return None

        # 合并现有的 cookies 和 Ruishu cookies
        cookies = {**ruishu_cookies}

        # 使用合并后的 cookies 发送请求
        response = session.get(
            'https://wappark.189.cn/jt-sign/ssoHomLogin?ticket=' + ticket,
            cookies=cookies,headers = {'User-Agent': "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36"}
        ).json()

        if response.get('resoultCode') == '0':
            sign = response.get('sign')
            accId = response.get('accId')
            return sign ,accId
        else:
            print(f"获取sign失败[{response.get('resoultCode')}]: {response}")
    except Exception as e:
        print(f"getSign 发生错误: {str(e)}")
    return None

async def qgNight(phone, ticket, timeDiff,isTrue):
    if isTrue:
        runTime = run_Time(23,59,3)
    else:
        # runTime = run_Time(0,0,0) + 0.65
        runTime = 0

    if runTime >(time.time()+timeDiff):
        difftime = runTime - time.time() - timeDiff
        print(f"当前时间:{str(datetime.datetime.now())[11:23]},跟设定的时间不同,等待{difftime}秒开始兑换每天一次的")
        await asyncio.sleep(difftime)
    session = requests.Session()
    session.mount('https://', DESAdapter())
    session.verify = False  # 禁用证书验证
    signx =await getSign(ticket,session)
    sign =signx[0]
    accId =signx[1]
    if sign:
        # print(f"当前时间:{str(datetime.datetime.now())[11:23]}获取到了Sign:"+sign)
        session.headers={"User-Agent":"Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36","sign":sign}
    else:
        print("未获取sign。")
        return
    rightsId =await getLevelRightsList(phone,session,accId)
    if rightsId:
        print("获取到了rightsId:"+rightsId[0])
    else:
        print("未能获取rightsId。")
        return
    # await asyncio.sleep(10)直接延迟也行，或者用下面的等待一段时间。之所以这样是要先获取sign省一些步骤。
    if isTrue:
        runTime2 = run_Time(23,59,59) + 0.3
        difftime = runTime2 - time.time() - timeDiff
        printn(f"等待{difftime}s")
        await asyncio.sleep(difftime)
    await exchangeForDay(phone,session,run_num,rightsId[0],0.1,accId)
async def qgDay(phone, ticket,  timeDiff, isTrue):
    async with AsyncSessionManager() as s:
      pass
async def main(timeDiff,isTRUE,hour):
    tasks = []
    PHONES=os.environ.get('chinaTelecomAccount')
    phone_list = PHONES.split('&')
    for phoneV in phone_list:
        value = phoneV.split('#')
        phone, password = value[0], value[1]
        printn(f'{get_first_three(phone)}开始登录')
        
        # 添加重试逻辑
        max_retries = 3
        retry_count = 0
        ticket = None
        
        while retry_count < max_retries and not ticket:
            ticket = userLoginNormal(phone,password)
            if not ticket:
                printn(f'{get_first_three(phone)} 第{retry_count+1}次登录失败，准备重试')
                retry_count += 1
                await asyncio.sleep(1)  # 添加1秒延迟避免频繁请求

        if ticket:
            # hour=datetime.datetime.now().hour
            # hour=23
            if hour > 15:
                tasks.append(qgNight(phone, ticket, timeDiff, isTRUE))
            else: #十点//十四点场次
                tasks.append(qgNight(phone, ticket, timeDiff, isTRUE))
        else:
            printn(f'{get_first_three(phone)} 登录失败，已达最大重试次数{max_retries}次')
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    h = datetime.datetime.now().hour
    #h=20                           #手动设置场次的时间
    print("当前小时为: "+str(h))
    if 10 >h >0:
        print("当前小时为: "+str(h)+"已过0点但未到10点开始准备抢十点场次")
        wttime= run_Time(9,59,8) #抢十点场次
    elif 14 >= h >=10:
        print("当前小时为: "+str(h) +"已过10点但未到14点开始准备抢十四点场次")
        wttime= run_Time(13,59,8) #抢十四点场次
    else:
        print("当前小时为: "+str(h)+"已过14点开始准备抢凌晨")
        wttime= run_Time(23,58,58) #抢凌晨
    #isTRUE=False
    isTRUE=True
    #isTRUE等于False则表示忽略所有限制直接运行。这个参数一般用于测试。实际生产一定要设置为True。
    if(wttime >time.time()) :
        wTime=wttime-time.time()
        print("未到时间,计算后差异:"+str(wTime)+"秒")
        if isTRUE:
            print("一定要先测试，根据自身 设定的重发和多号，不然会出问题，抢购过早或者过晚。")
            print("开始等待:")
            time.sleep(wTime)
    # timeValue = getApiTime("https://f.m.suning.com/api/ct.do")
    timeValue = 0
    timeDiff = timeValue if timeValue > 0 else 0
    asyncio.run(main(timeDiff, isTRUE,h))
    print("所有任务都已执行完毕!")