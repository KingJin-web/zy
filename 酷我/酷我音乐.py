"""
使用说明:
1. 环境变量使用 `kwyy`。
2. 单账号格式: 手机号#密码
3. 备注格式: 备注#手机号#密码
4. 多账号用 `&` 分隔:
   kwyy="备注#1手机号1#密码1&备注2#手机号2#密码2"
"""

import os
import base64
import random
import string
import uuid
from urllib.parse import quote
import time
import re
import requests
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SIGN_BASE = 'https://integralapi.kuwo.cn/api/v1/online/sign'
URL_NEW_USER_SIGN_LIST = SIGN_BASE + '/v1/earningSignIn/newUserSignList'
URL_USER_ASSET = SIGN_BASE + '/v1/earningSignIn/earningUserSignList'
URL_NEW_DO_LISTEN = SIGN_BASE + '/v1/earningSignIn/newDoListen'
URL_EVERYDAY_DO_LISTEN = SIGN_BASE + '/v1/earningSignIn/everydaymusic/doListen'
URL_BOX_RENEW = SIGN_BASE + '/new/boxRenew'
URL_NEW_BOX_LIST = SIGN_BASE + '/new/newBoxList'
URL_NEW_BOX_FINISH = SIGN_BASE + '/new/newBoxFinish'
FREEMIUM_SWITCH_URL = 'https://wapi.kuwo.cn/openapi/v1/user/freemium/h5/switches'

DONE_KEYWORDS = [
    '今天已完成任务',
    '已完成',
    '已领取',
    '已签到',
    '已达到当日观看额外视频次数',
    '已达',
    '上限',
    '次数用完',
    '免费次数用完了',
    '视频次数用完了',
]

static_c = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432, 67108864, 134217728, 268435456, 536870912, 1073741824, 2147483648, 4294967296, 8589934592, 17179869184, 34359738368, 68719476736, 137438953472, 274877906944, 549755813888, 1099511627776, 2199023255552, 4398046511104, 8796093022208, 17592186044416, 35184372088832, 70368744177664, 140737488355328, 281474976710656, 562949953421312, 1125899906842624, 2251799813685248, 4503599627370496, 9007199254740992, 18014398509481984, 36028797018963968, 72057594037927936, 144115188075855872, 288230376151711744, 576460752303423488, 1152921504606846976, 2305843009213693952, 4611686018427387904, -9223372036854775808]
static_i = [56, 48, 40, 32, 24, 16, 8, 0, 57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18, 10, 2, 59, 51, 43, 35, 62, 54, 46, 38, 30, 22, 14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 60, 52, 44, 36, 28, 20, 12, 4, 27, 19, 11, 3]
static_e = [31, 0, 1, 2, 3, 4, -1, -1, 3, 4, 5, 6, 7, 8, -1, -1, 7, 8, 9, 10, 11, 12, -1, -1, 11, 12, 13, 14, 15, 16, -1, -1, 15, 16, 17, 18, 19, 20, -1, -1, 19, 20, 21, 22, 23, 24, -1, -1, 23, 24, 25, 26, 27, 28, -1, -1, 27, 28, 29, 30, 31, 30, -1, -1]
static_l = [0, 1048577, 3145731]
static_g = [15, 6, 19, 20, 28, 11, 27, 16, 0, 14, 22, 25, 4, 17, 30, 9, 1, 7, 23, 13, 31, 26, 2, 8, 18, 12, 29, 5, 21, 10, 3, 24]
static_f = [[14, 4, 3, 15, 2, 13, 5, 3, 13, 14, 6, 9, 11, 2, 0, 5, 4, 1, 10, 12, 15, 6, 9, 10, 1, 8, 12, 7, 8, 11, 7, 0, 0, 15, 10, 5, 14, 4, 9, 10, 7, 8, 12, 3, 13, 1, 3, 6, 15, 12, 6, 11, 2, 9, 5, 0, 4, 2, 11, 14, 1, 7, 8, 13], [15, 0, 9, 5, 6, 10, 12, 9, 8, 7, 2, 12, 3, 13, 5, 2, 1, 14, 7, 8, 11, 4, 0, 3, 14, 11, 13, 6, 4, 1, 10, 15, 3, 13, 12, 11, 15, 3, 6, 0, 4, 10, 1, 7, 8, 4, 11, 14, 13, 8, 0, 6, 2, 15, 9, 5, 7, 1, 10, 12, 14, 2, 5, 9], [10, 13, 1, 11, 6, 8, 11, 5, 9, 4, 12, 2, 15, 3, 2, 14, 0, 6, 13, 1, 3, 15, 4, 10, 14, 9, 7, 12, 5, 0, 8, 7, 13, 1, 2, 4, 3, 6, 12, 11, 0, 13, 5, 14, 6, 8, 15, 2, 7, 10, 8, 15, 4, 9, 11, 5, 9, 0, 14, 3, 10, 7, 1, 12], [7, 10, 1, 15, 0, 12, 11, 5, 14, 9, 8, 3, 9, 7, 4, 8, 13, 6, 2, 1, 6, 11, 12, 2, 3, 0, 5, 14, 10, 13, 15, 4, 13, 3, 4, 9, 6, 10, 1, 12, 11, 0, 2, 5, 0, 13, 14, 2, 8, 15, 7, 4, 15, 1, 10, 7, 5, 6, 12, 11, 3, 8, 9, 14], [2, 4, 8, 15, 7, 10, 13, 6, 4, 1, 3, 12, 11, 7, 14, 0, 12, 2, 5, 9, 10, 13, 0, 3, 1, 11, 15, 5, 6, 8, 9, 14, 14, 11, 5, 6, 4, 1, 3, 10, 2, 12, 15, 0, 13, 2, 8, 5, 11, 8, 0, 15, 7, 14, 9, 4, 12, 7, 10, 9, 1, 13, 6, 3], [12, 9, 0, 7, 9, 2, 14, 1, 10, 15, 3, 4, 6, 12, 5, 11, 1, 14, 13, 0, 2, 8, 7, 13, 15, 5, 4, 10, 8, 3, 11, 6, 10, 4, 6, 11, 7, 9, 0, 6, 4, 2, 13, 1, 9, 15, 3, 8, 15, 3, 1, 14, 12, 5, 11, 0, 2, 12, 14, 7, 5, 10, 8, 13], [4, 1, 3, 10, 15, 12, 5, 0, 2, 11, 9, 6, 8, 7, 6, 9, 11, 4, 12, 15, 0, 3, 10, 5, 14, 13, 7, 8, 13, 14, 1, 2, 13, 6, 14, 9, 4, 1, 2, 14, 11, 13, 5, 0, 1, 10, 8, 3, 0, 11, 3, 5, 9, 4, 15, 2, 7, 8, 12, 15, 10, 7, 6, 12], [13, 7, 10, 0, 6, 9, 5, 15, 8, 4, 3, 10, 11, 14, 12, 5, 2, 11, 9, 6, 15, 12, 0, 3, 4, 1, 14, 13, 1, 2, 7, 8, 1, 2, 12, 15, 10, 4, 0, 3, 13, 14, 6, 9, 7, 8, 9, 6, 15, 1, 5, 12, 3, 10, 14, 5, 8, 7, 11, 0, 4, 13, 2, 11]]
static_h = [39, 7, 47, 15, 55, 23, 63, 31, 38, 6, 46, 14, 54, 22, 62, 30, 37, 5, 45, 13, 53, 21, 61, 29, 36, 4, 44, 12, 52, 20, 60, 28, 35, 3, 43, 11, 51, 19, 59, 27, 34, 2, 42, 10, 50, 18, 58, 26, 33, 1, 41, 9, 49, 17, 57, 25, 32, 0, 40, 8, 48, 16, 56, 24]
static_d = [57, 49, 41, 33, 25, 17, 9, 1, 59, 51, 43, 35, 27, 19, 11, 3, 61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7, 56, 48, 40, 32, 24, 16, 8, 0, 58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4, 62, 54, 46, 38, 30, 22, 14, 6]
static_k = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
static_j = [13, 16, 10, 23, 0, 4, -1, -1, 2, 27, 14, 5, 20, 9, -1, -1, 22, 18, 11, 3, 25, 7, -1, -1, 15, 6, 26, 19, 12, 1, -1, -1, 40, 51, 30, 36, 46, 54, -1, -1, 29, 39, 50, 44, 32, 47, -1, -1, 43, 48, 38, 55, 33, 52, -1, -1, 45, 41, 49, 35, 28, 31, -1, -1]

def func_a1(iArr, i2, j2):
    j3 = 0
    for i3 in range(i2):
        if iArr[i3] >= 0:
            jArr = static_c
            if (jArr[iArr[i3]] & j2) != 0:
                j3 |= jArr[i3]
    return j3

def func_a2(j2, jArr, i2):
    a2 = func_a1(static_i, 56, j2)
    for i3 in range(16):
        jArr2 = static_l
        iArr = static_k
        a2 = ((a2 & ~jArr2[iArr[i3]]) >> iArr[i3]) | ((jArr2[iArr[i3]] & a2) << (28 - iArr[i3]))
        jArr[i3] = func_a1(static_j, 64, a2)
    if i2 == 1:
        for i4 in range(8):
            j3 = jArr[i4]
            i5 = 15 - i4
            jArr[i4] = jArr[i5]
            jArr[i5] = j3

def func_a3(jArr, j2):
    p = [0] * 2
    q = [0] * 8
    m = func_a1(static_d, 64, j2)
    iArr = p
    j3 = m
    iArr[0] = int(j3 & 4294967295)
    iArr[1] = int((j3 & -4294967296) >> 32)
    for i2 in range(16):
        o = iArr[1]
        o = func_a1(static_e, 64, o)
        o ^= jArr[i2]
        for i3 in range(8):
            q[i3] = int((o >> (i3 * 8)) & 255)
        r = 0
        i4 = 7
        while True:
            t = i4
            i5 = t
            if i5 >= 0:
                i6 = r
                i6 <<= 4
                if i6 > 2147483647:
                    i6 = -4294967296 + i6
                i6 |= static_f[i5][q[i5]]
                r = i6
                i4 = i5 - 1
            else:
                break
        o = r
        o = func_a1(static_g, 32, o)
        iArr2 = p
        n = iArr2[0]
        iArr2[0] = iArr2[1]
        xor_val = n ^ o
        if -2147483648 < xor_val < 2147483647:
            iArr2[1] = int(xor_val)
            continue
        if xor_val >= 2147483647:
            iArr2[1] = xor_val - 4294967296
        else:
            iArr2[1] = xor_val + 4294967296
    iArr3 = p
    s = iArr3[0]
    iArr3[0] = iArr3[1]
    iArr3[1] = s
    m = ((iArr3[1] << 32) & -4294967296) | (4294967295 & iArr3[0])
    m = func_a1(static_h, 64, m)
    return m

def generate_q(bArr, bArr2):
    length = len(bArr)
    jArr = [0] * 16
    j2 = 0
    j3 = 0
    for i3 in range(8):
        j3 |= bArr2[i3] << (i3 * 8)
    func_a2(j3, jArr, 0)
    i4 = length // 8
    jArr2 = [0] * i4
    for i5 in range(i4):
        for i6 in range(8):
            jArr2[i5] = jArr2[i5] | ((bArr[i5 * 8 + i6] & 255) << (i6 * 8))
    jArr3 = [0] * (((i4 + 1) * 8 + 1) // 8)
    for i7 in range(i4):
        jArr3[i7] = func_a3(jArr, jArr2[i7])
    i8 = length % 8
    i9 = i4 * 8
    i10 = length - i9
    r12 = [None] * i10
    r12[0:i10] = bArr[i9:i9 + i10]
    for i11 in range(i8):
        j2 |= (r12[i11] & 255) << (i11 * 8)
    jArr3[i4] = func_a3(jArr, j2)
    bArr3 = [None] * (len(jArr3) * 8)
    i12 = 0
    i13 = 0
    while i12 < len(jArr3):
        i14 = i13
        for i15 in range(8):
            bArr3[i14] = 255 & (jArr3[i12] >> (i15 * 8))
            i14 += 1
        i12 += 1
        i13 = i14
    return base64.b64encode(bytearray(bArr3)).decode()

def create_sx():
    timestamp = int(time.time() * 1000)
    combined_string = str(timestamp) + '12345678'
    result = combined_string[:8]
    return result

def encrypt_devid(dev_id):
    padded_id = dev_id.ljust(16, '0')[:16]
    return base64.b64encode(padded_id.encode()).decode()

def get_q(username, password):
    dev_id = ''.join([random.choice(string.digits) for _ in range(10)])
    dev_name = '安卓设备'
    devType = 'arr'
    data = f"username={quote(username)}&password={quote(base64.b64encode(password.encode()).decode())}&dev_id={dev_id}&user={str(uuid.uuid4()).replace('-', '')}&dev_name={quote(dev_name)}&urlencode=0&src=kwplayer_ar11.1.4.1_40.apk&devResolution=720*1080&&from=android&devType={devType}&sx={create_sx()}&version=11.1.4.1"
    q_value = generate_q(data.encode('UTF-8'), 'kwks&@69'.encode('UTF-8'))
    encrypted_dev_id = encrypt_devid(dev_id)
    return q_value, encrypted_dev_id

def encrypt_phone(phone):
    key = b'ysiVkLJHHnvMWCHq'
    iv = b'ichYooX+Mb1gRetP'
    if isinstance(phone, str):
        phone = phone.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plaintext = pad(phone, AES.block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    ciphertext_base64 = base64.b64encode(ciphertext).decode('utf-8')
    return ciphertext_base64

def decrypt_phone(encrypted_phone):
    key = b'ysiVkLJHHnvMWCHq'
    iv = b'ichYooX+Mb1gRetP'
    aes = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
    encrypted_data = base64.b64decode(encrypted_phone)
    decrypted_data = unpad(aes.decrypt(encrypted_data), AES.block_size, style='pkcs7')
    return decrypted_data.decode('UTF-8')

def generate_kuwo_token(device_id, timestamp):
    raw_string = str(device_id) + 'KUWO_COMIC' + str(timestamp)
    token = hashlib.md5(raw_string.encode('utf-8')).hexdigest()
    return token

def parse_account_item(account_str):
    parts = [x.strip() for x in account_str.split('#')]
    if len(parts) < 2:
        return None
    if len(parts) == 2:
        phone, password = parts[0], parts[1]
        if not phone or not password:
            return None
        return {'phone': phone, 'password': password}
    phone = parts[1]
    password = '#'.join(parts[2:])
    if not phone or not password:
        return None
    return {'phone': phone, 'password': password}

def get_accounts_from_env():
    env_value = os.getenv('kwyy', '').strip()
    if not env_value:
        return []
    accounts = []
    account_strings = env_value.split('&')
    for account_str in account_strings:
        account_str = account_str.strip()
        if not account_str:
            continue
        parsed = parse_account_item(account_str)
        if parsed:
            accounts.append(parsed)
    return accounts

def login(username, password):
    try:
        q, encrypted_dev_id = get_q(username, password)
        url = 'http://ar.i.kuwo.cn/US_NEW/kuwo/login_kw'
        headers = {
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; MI 8 MIUI/V12.5.2.0.QEACNXM)',
            'Accept': '*/*',
            'Host': 'ar.i.kuwo.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }
        params = {'f': 'ar', 'q': q}
        response = requests.get(url, headers=headers, params=params)
        set_cookie = response.headers.get('Set-Cookie', '')
        username_match = re.search(r'uname3=([^;]+)', set_cookie)
        sid_match = re.search(r'websid=([^;]+)', set_cookie)
        uid_match = re.search(r'userid=([^;]+)', set_cookie)
        account_match = re.search(r't3kwid=([^;]+)', set_cookie)
        if all([username_match, sid_match, uid_match, account_match]):
            loginUid = uid_match.group(1)
            loginSid = sid_match.group(1)
            username_ret = username_match.group(1)
            appUid = account_match.group(1)
            return loginUid, loginSid, username_ret, appUid, encrypted_dev_id
        print('❌ 登录失败: Cookie解析失败')
        return None
    except Exception as e:
        print('❌ 登录异常: ' + str(e))
        return None

def open_treasure_box(loginUid, loginSid, appUid, encrypted_dev_id, gold_num=20, verbose=True):
    try:
        url = 'https://integralapi.kuwo.cn/api/v1/online/sign/new/newBoxFinish'
        r_value = random.random()
        params = {
            'apiversion': '46',
            'loginUid': loginUid,
            'loginSid': loginSid,
            'devId': encrypted_dev_id,
            'jfencv': 'devId',
            'appUid': appUid,
            'source': 'kwplayer_ar_12.0.4.1_newpcguanwangmobile.apk',
            'version': 'kwplayer_ar_12.0.4.1',
            'dynamicVer': '46',
            'kver': '1',
            'verifyStr': '',
            'adverSpace': '',
            'r': str(r_value),
            'action': 'new',
            'time': '',
            'goldNum': str(gold_num),
            'baseTaskGold': '0',
            'extraGoldnum': '0',
            'clickExtraGoldNum': '0',
            'yyzdSecondRewardFlag': '0',
            'secondRewardFlag': '0',
            'apiv': '6',
        }
        headers = {
            'Host': 'integralapi.kuwo.cn',
            'Connection': 'keep-alive',
            'sec-ch-ua-platform': '"Android"',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 4a Build/TQ3A.230805.001.S2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/134.0.6998.135 Mobile Safari/537.36/ kuwopage',
            'Accept': 'application/json, text/plain, */*',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Android WebView";v="134"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://h5app.kuwo.cn',
            'X-Requested-With': 'cn.kuwo.player',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://h5app.kuwo.cn/',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        response = requests.get(url, headers=headers, params=params, timeout=30, verify=False)
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                data = result.get('data', {})
                status = data.get('status', 0)
                if status == 1:
                    obtain = data.get('obtain', 0)
                    extra_num = data.get('extraNum', 0)
                    if verbose:
                        print('✅ 开宝箱成功: 获得 ' + str(obtain) + ' 金币' + ((' (额外 ' + str(extra_num) + ' 金币)') if extra_num else ''))
                    return {'success': True, 'obtain': obtain, 'extra_num': extra_num, 'description': '成功'}
                description = data.get('description', '未知错误')
                if verbose:
                    print('⚠️  开宝箱失败: ' + description)
                return {'success': False, 'obtain': 0, 'description': description}
            error_msg = result.get('msg', '未知错误')
            if verbose:
                print('❌ 开宝箱请求失败: ' + error_msg)
            return {'success': False, 'obtain': 0, 'description': error_msg}
        if verbose:
            print('❌ 请求失败，状态码: ' + str(response.status_code))
        return {'success': False, 'obtain': 0, 'description': 'HTTP ' + str(response.status_code)}
    except Exception as e:
        if verbose:
            print('❌ 开宝箱异常: ' + str(e))
        return {'success': False, 'obtain': 0, 'description': str(e)}

def open_guanggao(loginUid, loginSid, appUid, encrypted_dev_id, gold_num, phone, verbose=True):
    try:
        url = 'https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen'
        params = {
            'apiversion': '46',
            'adverSpace': '20130101',
            'loginUid': loginUid,
            'loginSid': loginSid,
            'appUid': appUid,
            'terminal': 'ar',
            'from': 'videoadver',
            'taskId': '',
            'goldNum': '208',
            'baseTaskGold': '0',
            'adverId': '',
            'mobile': phone,
            'listenTime': 0,
            'apiv': 10,
            'unit': '',
            'dynamicVer': 46,
            'kver': 1,
            'rewardType': 0,
            'pFrom': 'HTTP/1.1',
        }
        headers = {
            'Host': 'integralapi.kuwo.cn',
            'Connection': 'keep-alive',
            'sec-ch-ua-platform': '"Android"',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 4a Build/TQ3A.230805.001.S2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/134.0.6998.135 Mobile Safari/537.36/ kuwopage',
            'Accept': 'application/json, text/plain, */*',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Android WebView";v="134"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://h5app.kuwo.cn',
            'X-Requested-With': 'cn.kuwo.player',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://h5app.kuwo.cn/',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        response = requests.get(url, headers=headers, params=params, timeout=30, verify=False)
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                data = result.get('data', {})
                status = data.get('status', 0)
                if status == 1:
                    obtain = data.get('obtain', 0)
                    description = data.get('description', '成功')
                    if verbose:
                        print('✅ 广告观看成功: 获得 ' + str(obtain) + ' 金币 - ' + description)
                    return {'success': True, 'obtain': obtain, 'description': description}
                description = data.get('description', '未知错误')
                if verbose:
                    print('⚠️  广告观看失败: ' + description)
                return {'success': False, 'obtain': 0, 'description': description}
            error_msg = result.get('msg', '未知错误')
            if verbose:
                print('❌ 广告观看请求失败: ' + error_msg)
            return {'success': False, 'obtain': 0, 'description': error_msg}
        if verbose:
            print('❌ 请求失败，状态码: ' + str(response.status_code))
        return {'success': False, 'obtain': 0, 'description': 'HTTP ' + str(response.status_code)}
    except Exception as e:
        if verbose:
            print('❌ 广告观看异常: ' + str(e))
        return {'success': False, 'obtain': 0, 'description': str(e)}

def clock_bonus(loginUid, loginSid, appUid, encrypted_dev_id, phone, verbose=True):
    clock_gold_num = 59
    try:
        task_payload = fetch_dynamic_task_payload(loginUid, loginSid, appUid, {})
        data_list = task_payload.get('dataList', [])
        if not isinstance(data_list, list):
            data_list = []
        for item in data_list:
            if not isinstance(item, dict):
                continue
            subtitle = str(item.get('subTitle') or '')
            task_type = str(item.get('taskType') or '')
            if '打卡' in subtitle or task_type == 'clock':
                gold_num = to_int(item.get('goldNum'))
                if gold_num > 0:
                    clock_gold_num = gold_num
                    break
    except Exception:
        pass

    return run_new_do_listen_task(
        '整点领金币',
        loginUid,
        loginSid,
        appUid,
        phone,
        {'from': 'clock', 'goldNum': str(clock_gold_num)},
        verbose=verbose,
    )

def watch_dada_ad(loginUid, loginSid, appUid, encrypted_dev_id, phone):
    timestamp = str(int(time.time() * 1000))
    dynamic_token = generate_kuwo_token(encrypted_dev_id, timestamp)
    url = 'https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen'
    token_parts = '1,2,20130401,' + f'{loginUid},' + f'{dynamic_token}'
    params = {
        'apiversion': '46',
        'adverSpace': '20130401',
        'verifyStr': '',
        'loginUid': loginUid,
        'loginSid': loginSid,
        'appUid': appUid,
        'terminal': 'ar',
        'from': 'videofix',
        'taskId': '',
        'goldNum': '50',
        'baseTaskGold': '0',
        'adverId': '',
        'token': '',
        'extraGoldNum': '0',
        'clickExtraGoldNum': '0',
        'secondRewardFlag': '0',
        'yyzdSecondRewardFlag': '0',
        'surpriseType': '',
        'mobile': phone,
        'apiv': '10',
        'dynamicVer': '46',
        'kver': '1',
        'rewardType': '0',
        'pFrom': '',
    }
    headers = {
        'Host': 'integralapi.kuwo.cn',
        'Connection': 'keep-alive',
        'sec-ch-ua-platform': '"Android"',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 4a Build/TQ3A.230805.001.S2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.146 Mobile Safari/537.36/ kuwopage',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua': '"Android WebView";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'Origin': 'https://h5app.kuwo.cn',
        'X-Requested-With': 'cn.kuwo.player',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://h5app.kuwo.cn/',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30, verify=False)
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                data = result.get('data', {})
                status = data.get('status', 0)
                if status == 1:
                    obtain = data.get('obtain', 0)
                    description = data.get('description', '成功')
                    print('✅ 广告观看成功: 获得 ' + str(obtain) + ' 金币 - ' + description)
                    return {'success': True, 'obtain': obtain, 'description': description}
                description = data.get('description', '未知错误')
                print('⚠️  广告观看失败: ' + description)
                return {'success': False, 'obtain': 0, 'description': description}
            error_msg = result.get('msg', '未知错误')
            print('❌ 广告观看请求失败: ' + error_msg)
            return {'success': False, 'obtain': 0, 'description': error_msg}
        print('❌ 请求失败，状态码: ' + str(response.status_code))
        return {'success': False, 'obtain': 0, 'description': 'HTTP ' + str(response.status_code)}
    except Exception as e:
        print('❌ 广告观看异常: ' + str(e))
        return {'success': False, 'obtain': 0, 'description': str(e)}

def lottery_draw(loginUid, loginSid, appUid, source='kwplayer_ar_12.0.4.1_newpcguanwangmobile.apk', lottery_type='free', verbose=True):
    try:
        url = 'https://integralapi.kuwo.cn/api/v1/online/sign/loterry/getLucky'
        params = {'loginUid': loginUid, 'loginSid': loginSid, 'appUid': appUid, 'source': source, 'type': lottery_type}
        headers = {
            'Host': 'integralapi.kuwo.cn',
            'Connection': 'keep-alive',
            'sec-ch-ua-platform': '"Android"',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 4a Build/TQ3A.230805.001.S2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.146 Mobile Safari/537.36/ kuwopage',
            'Accept': 'application/json, text/plain, */*',
            'sec-ch-ua': '"Android WebView";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://h5app.kuwo.cn',
            'X-Requested-With': 'cn.kuwo.player',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://h5app.kuwo.cn/',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        response = requests.get(url, headers=headers, params=params, timeout=30, verify=False)
        if response.status_code == 200:
            result = response.json()
            code = result.get('code', 0)
            msg = result.get('msg', '未知')
            if code == 200:
                data = result.get('data', {})
                if not isinstance(data, dict):
                    data = {}
                reward_name = str(data.get('loterryname') or data.get('lotteryName') or msg)
                obtain = to_int(data.get('goldNum') or data.get('obtain') or data.get('awardScore') or data.get('score') or 0)
                if obtain <= 0:
                    match = re.search(r'(\d+)\s*金币', reward_name + ' ' + msg)
                    if match:
                        obtain = to_int(match.group(1))
                if verbose:
                    if obtain > 0:
                        print('🎉 抽奖成功: ' + reward_name + ' (+' + str(obtain) + ' 金币)')
                    else:
                        print('🎉 抽奖成功: ' + reward_name)
                return {'success': True, 'message': msg, 'reward_name': reward_name, 'obtain': obtain, 'data': data}
            if code == 11:
                if verbose:
                    print('❌ 抽奖失败: ' + msg)
                return {'success': False, 'message': msg, 'data': {}}
            if verbose:
                print('❌ 抽奖失败: ' + msg)
            return {'success': False, 'message': msg, 'data': {}}
        if verbose:
            print('❌ 请求失败，状态码: ' + str(response.status_code))
        return {'success': False, 'message': 'HTTP ' + str(response.status_code), 'data': {}}
    except Exception as e:
        if verbose:
            print('❌ 抽奖异常: ' + str(e))
        return {'success': False, 'message': str(e), 'data': {}}

def run_activity_box_task(loginUid, loginSid, verbose=True):
    params = {
        'loginUid': loginUid,
        'loginSid': loginSid,
        'from': 'sign',
        'extraGoldNum': '110',
    }
    try:
        response = requests.get(URL_NEW_BOX_LIST, headers=build_common_headers(), params=params, timeout=30, verify=False)
        if response.status_code != 200:
            if verbose:
                print('❌ 活动宝箱列表请求失败: HTTP ' + str(response.status_code))
            return {'success': False, 'obtain': 0, 'description': 'HTTP ' + str(response.status_code)}

        result = response.json()
        if result.get('code') != 200:
            msg = str(result.get('msg', '未知错误'))
            if verbose:
                print('❌ 活动宝箱列表请求失败: ' + msg)
            return {'success': False, 'obtain': 0, 'description': msg}

        data = result.get('data', {})
        if not isinstance(data, dict):
            data = {}
        gold_num = to_int(data.get('goldNum') or 0)
        if gold_num <= 0:
            if verbose:
                print('⏭️ 活动宝箱: 暂无可领取金币')
            return {'success': True, 'done': True, 'obtain': 0, 'description': '暂无可领取金币'}

        finish_params = {
            'loginUid': loginUid,
            'loginSid': loginSid,
            'action': 'new',
            'goldNum': gold_num,
        }
        finish_resp = requests.get(URL_NEW_BOX_FINISH, headers=build_common_headers(), params=finish_params, timeout=30, verify=False)
        if finish_resp.status_code != 200:
            if verbose:
                print('❌ 活动宝箱领取请求失败: HTTP ' + str(finish_resp.status_code))
            return {'success': False, 'obtain': 0, 'description': 'HTTP ' + str(finish_resp.status_code)}

        finish_result = finish_resp.json()
        if finish_result.get('code') == 200:
            if verbose:
                print('✅ 活动宝箱成功: 获得 ' + str(gold_num) + ' 金币')
            return {'success': True, 'obtain': gold_num, 'description': '成功'}

        msg = str(finish_result.get('msg', '未知错误'))
        if verbose:
            print('⚠️  活动宝箱领取失败: ' + msg)
        return {'success': False, 'obtain': 0, 'description': msg}
    except Exception as e:
        if verbose:
            print('❌ 活动宝箱异常: ' + str(e))
        return {'success': False, 'obtain': 0, 'description': str(e)}

def run_box_renew_tasks(loginUid, loginSid, gold_num=30, verbose=True):
    time_windows = ['00-08', '08-10', '10-12', '12-14', '14-16', '16-18', '18-20', '20-24']
    success_count = 0
    total_count = len(time_windows) * 2
    run_index = 0
    stop_all = False
    for time_window in time_windows:
        for action, action_name in [('new', '新宝箱'), ('old', '补宝箱')]:
            run_index += 1
            params = {
                'loginUid': loginUid,
                'loginSid': loginSid,
                'action': action,
                'time': time_window,
                'goldNum': str(gold_num),
            }
            try:
                response = requests.get(URL_BOX_RENEW, headers=build_common_headers(), params=params, timeout=30, verify=False)
                if response.status_code != 200:
                    if verbose:
                        print('  第' + str(run_index) + '/' + str(total_count) + '次 ❌ ' + action_name + '(' + time_window + '): HTTP ' + str(response.status_code))
                    continue
                result = response.json()
                if result.get('code') == 200:
                    success_count += 1
                    if verbose:
                        print('  第' + str(run_index) + '/' + str(total_count) + '次 ✅ ' + action_name + '(' + time_window + ')')
                else:
                    msg = str(result.get('msg', '未知错误'))
                    if verbose:
                        print('  第' + str(run_index) + '/' + str(total_count) + '次 ❌ ' + action_name + '(' + time_window + '): ' + msg)
                    if is_done_like(msg):
                        stop_all = True
            except Exception as e:
                if verbose:
                    print('  第' + str(run_index) + '/' + str(total_count) + '次 ❌ ' + action_name + '(' + time_window + '): ' + str(e))
            if stop_all:
                break
        if stop_all:
            break
    if verbose:
        print('  汇总: 成功 ' + str(success_count) + '/' + str(total_count))
    return {'success_count': success_count, 'total_count': total_count}

def watch_surprise_ad(loginUid, loginSid, appUid, encrypted_dev_id, phone, verbose=True):
    try:
        url = 'https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen'
        params = {
            'apiversion': '46',
            'adverSpace': '20130702',
            'verifyStr': '',
            'loginUid': loginUid,
            'loginSid': loginSid,
            'appUid': appUid,
            'terminal': 'ar',
            'from': 'surprise',
            'taskId': '',
            'goldNum': '68',
            'baseTaskGold': '0',
            'adverId': '20130702-77797065644-101',
            'token': '',
            'clickExtraGoldNum': '0',
            'secondRewardFlag': '0',
            'yyzdSecondRewardFlag': '0',
            'verificationId': '',
            'surpriseType': '',
            'mobile': phone,
            'apiv': '10',
            'dynamicVer': '46',
            'kver': '1',
            'rewardType': '0',
            'pFrom': '',
        }
        headers = {
            'Host': 'integralapi.kuwo.cn',
            'Connection': 'keep-alive',
            'sec-ch-ua-platform': '"Android"',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 4a Build/TQ3A.230805.001.S2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.146 Mobile Safari/537.36/ kuwopage',
            'Accept': 'application/json, text/plain, */*',
            'sec-ch-ua': '"Android WebView";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://h5app.kuwo.cn',
            'X-Requested-With': 'cn.kuwo.player',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://h5app.kuwo.cn/',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        response = requests.get(url, headers=headers, params=params, timeout=30, verify=False)
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                data = result.get('data', {})
                status = data.get('status', 0)
                if status == 1:
                    obtain = data.get('obtain', 0)
                    description = data.get('description', '成功')
                    if verbose:
                        print('✅ 惊喜广告观看成功: 获得 ' + str(obtain) + ' 金币 - ' + description)
                    return {'success': True, 'obtain': obtain, 'description': description}
                description = data.get('description', '未知错误')
                if verbose:
                    print('⚠️  惊喜广告观看失败: ' + description)
                return {'success': False, 'obtain': 0, 'description': description}
            error_msg = result.get('msg', '未知错误')
            if verbose:
                print('❌ 惊喜广告观看请求失败: ' + error_msg)
            return {'success': False, 'obtain': 0, 'description': error_msg}
        if verbose:
            print('❌ 请求失败，状态码: ' + str(response.status_code))
        return {'success': False, 'obtain': 0, 'description': 'HTTP ' + str(response.status_code)}
    except Exception as e:
        if verbose:
            print('❌ 惊喜广告观看异常: ' + str(e))
        return {'success': False, 'obtain': 0, 'description': str(e)}

def build_common_headers():
    return {
        'Host': 'integralapi.kuwo.cn',
        'Connection': 'keep-alive',
        'sec-ch-ua-platform': '"Android"',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 4a Build/TQ3A.230805.001.S2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/134.0.6998.135 Mobile Safari/537.36/ kuwopage',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Android WebView";v="134"',
        'sec-ch-ua-mobile': '?1',
        'Origin': 'https://h5app.kuwo.cn',
        'X-Requested-With': 'cn.kuwo.player',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://h5app.kuwo.cn/',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    }

def is_done_like(text):
    if not text:
        return False
    for keyword in DONE_KEYWORDS:
        if keyword in str(text):
            return True
    return False

def is_video_limit_like(text):
    if not text:
        return False
    value = str(text)
    keywords = [
        '已达到当日观看额外视频次数',
        '视频次数用完了',
        '免费次数用完了',
        '观看额外视频次数',
    ]
    for keyword in keywords:
        if keyword in value:
            return True
    return False

def to_int(value):
    try:
        if value is None:
            return 0
        text = str(value).strip()
        if text == '' or text.lower() == 'null':
            return 0
        if '.' in text:
            return int(float(text))
        return int(text)
    except Exception:
        return 0

def run_generic_task(title, url, params, verbose=True):
    try:
        response = requests.get(url, headers=build_common_headers(), params=params, timeout=30, verify=False)
        if response.status_code != 200:
            if verbose:
                print('❌ ' + title + '请求失败: HTTP ' + str(response.status_code))
            return {'success': False, 'obtain': 0, 'description': 'HTTP ' + str(response.status_code), 'data': {}}

        result = response.json()
        if result.get('code') != 200:
            msg = str(result.get('msg', '未知错误'))
            if verbose:
                print('❌ ' + title + '请求失败: ' + msg)
            return {'success': False, 'obtain': 0, 'description': msg, 'data': {}}

        data = result.get('data', {})
        if not isinstance(data, dict):
            data = {}
        status = data.get('status', 1)
        if isinstance(status, str) and status.isdigit():
            status = int(status)
        obtain = to_int(data.get('obtain') or data.get('goldNum') or 0)
        description = str(data.get('description') or result.get('msg') or '成功')

        if status == 1:
            if verbose:
                print('✅ ' + title + '成功: +' + str(obtain) + ' 金币 - ' + description)
            return {'success': True, 'obtain': obtain, 'description': description, 'data': data}

        if is_done_like(description):
            if verbose:
                print('⏭️ ' + title + ': ' + description)
            return {'success': True, 'done': True, 'obtain': obtain, 'description': description, 'data': data}

        if verbose:
            print('⚠️  ' + title + '失败: ' + description)
        return {'success': False, 'obtain': 0, 'description': description, 'data': data}
    except Exception as e:
        if verbose:
            print('❌ ' + title + '异常: ' + str(e))
        return {'success': False, 'obtain': 0, 'description': str(e), 'data': {}}

def run_new_do_listen_task(title, loginUid, loginSid, appUid, phone, extra_params, verbose=True):
    params = {
        'apiversion': '46',
        'adverSpace': '',
        'verifyStr': '',
        'loginUid': loginUid,
        'loginSid': loginSid,
        'appUid': appUid,
        'terminal': 'ar',
        'from': '',
        'taskId': '',
        'goldNum': '',
        'baseTaskGold': '0',
        'adverId': '',
        'token': '',
        'extraGoldNum': '0',
        'clickExtraGoldNum': '0',
        'secondRewardFlag': '0',
        'yyzdSecondRewardFlag': '0',
        'surpriseType': '',
        'mobile': phone,
        'listenTime': 0,
        'apiv': '10',
        'unit': '',
        'dynamicVer': '46',
        'kver': '1',
        'rewardType': '0',
        'pFrom': '',
    }
    params.update(extra_params or {})
    clean_params = {}
    for key, value in params.items():
        if value is None:
            continue
        clean_params[key] = value
    return run_generic_task(title, URL_NEW_DO_LISTEN, clean_params, verbose=verbose)

def run_everyday_do_listen_task(title, loginUid, loginSid, appUid, extra_params, verbose=True):
    params = {
        'loginUid': loginUid,
        'loginSid': loginSid,
        'appUid': appUid,
    }
    params.update(extra_params or {})
    clean_params = {}
    for key, value in params.items():
        if value is None:
            continue
        clean_params[key] = value
    return run_generic_task(title, URL_EVERYDAY_DO_LISTEN, clean_params, verbose=verbose)

def query_user_asset(loginUid, loginSid, appUid, verbose=True):
    params = {'loginUid': loginUid, 'loginSid': loginSid, 'appUid': appUid}
    try:
        response = requests.get(URL_USER_ASSET, headers=build_common_headers(), params=params, timeout=30, verify=False)
        if response.status_code != 200:
            if verbose:
                print('❌ 资产查询失败: HTTP ' + str(response.status_code))
            return {'success': False, 'score': 0}
        result = response.json()
        if result.get('code') != 200:
            msg = str(result.get('msg', '未知错误'))
            if verbose:
                print('❌ 资产查询失败: ' + msg)
            return {'success': False, 'score': 0}
        data = result.get('data', {})
        if not isinstance(data, dict):
            data = {}
        score = to_int(data.get('remainScore') or result.get('remainScore') or 0)
        if verbose:
            print('✅ 资产查询成功: 剩余金币 ' + str(score))
        return {'success': True, 'score': score}
    except Exception as e:
        if verbose:
            print('❌ 资产查询异常: ' + str(e))
        return {'success': False, 'score': 0}

def fetch_sign_list(loginUid, loginSid, appUid, extra_params=None, tag='签到列表'):
    params = {'loginUid': loginUid, 'loginSid': loginSid, 'appUid': appUid}
    params.update(extra_params or {})
    try:
        response = requests.get(URL_NEW_USER_SIGN_LIST, headers=build_common_headers(), params=params, timeout=30, verify=False)
        if response.status_code != 200:
            print('❌ ' + tag + '请求失败: HTTP ' + str(response.status_code))
            return {'success': False, 'data': {}}
        result = response.json()
        if result.get('code') != 200:
            msg = str(result.get('msg', '未知错误'))
            print('❌ ' + tag + '请求失败: ' + msg)
            return {'success': False, 'data': {}}
        payload = result.get('data', {})
        if not isinstance(payload, dict):
            payload = {}
        return {'success': True, 'data': payload}
    except Exception as e:
        print('❌ ' + tag + '异常: ' + str(e))
        return {'success': False, 'data': {}}

def fetch_dynamic_task_payload(loginUid, loginSid, appUid, first_payload):
    if has_listen_task_config(first_payload):
        return first_payload

    dynamic_info = fetch_sign_list(
        loginUid,
        loginSid,
        appUid,
        extra_params={
            'dynamicVer': '39',
            'q36': '0302c7dcfc6616225938b018100018b19319',
        },
        tag='动态任务列表',
    )
    if dynamic_info.get('success'):
        payload = dynamic_info.get('data', {})
        dynamic_list = payload.get('dataList', [])
        if has_listen_task_config(payload) or (isinstance(dynamic_list, list) and dynamic_list):
            return payload

    return first_payload

def has_listen_task_config(task_payload):
    data_list = task_payload.get('dataList', [])
    if not isinstance(data_list, list):
        return False

    for item in data_list:
        if not isinstance(item, dict):
            continue
        task_type = str(item.get('taskType') or '').strip().lower()
        title = str(item.get('title') or '')
        listen_list = item.get('listenList')
        if task_type == 'listen' and isinstance(listen_list, list):
            return True
        if '听歌' in title and isinstance(listen_list, list):
            return True
        if isinstance(listen_list, list) and listen_list:
            return True
    return False

def extract_listen_segment_candidates(task_payload):
    data_list = task_payload.get('dataList', [])
    if not isinstance(data_list, list):
        return []

    candidates = []
    seen = set()

    for item in data_list:
        if not isinstance(item, dict):
            continue
        title = str(item.get('title') or '')
        task_type = str(item.get('taskType') or '').strip().lower()
        listen_list = item.get('listenList')
        if not isinstance(listen_list, list):
            continue
        if not (task_type == 'listen' or '听歌' in title or listen_list):
            continue

        for idx, listen_item in enumerate(listen_list, 1):
            if not isinstance(listen_item, dict):
                continue
            listen_time = listen_item.get('time')
            unit = listen_item.get('unit')
            gold = listen_item.get('goldNum')
            extra_gold = listen_item.get('extraGoldNum')

            if gold and str(gold).lower() != 'null':
                key = ('g', str(listen_time or ''), str(unit or ''), str(gold))
                if key not in seen:
                    seen.add(key)
                    candidates.append({
                        'kind': 'gold',
                        'idx': idx,
                        'params': {
                            'from': 'listen',
                            'goldNum': gold,
                            'listenTime': listen_time,
                            'unit': unit,
                        },
                    })

            if extra_gold and str(extra_gold).lower() != 'null':
                key = ('eg', str(listen_time or ''), '', str(extra_gold))
                if key not in seen:
                    seen.add(key)
                    candidates.append({
                        'kind': 'extra',
                        'idx': idx,
                        'params': {
                            'from': 'listen',
                            'extraGoldNum': extra_gold,
                            'listenTime': listen_time,
                        },
                    })

    return candidates

def run_creative_dynamic_tasks(loginUid, loginSid, appUid, encrypted_phone, reward_golds, verbose=True, stop_on_video_limit=False):
    summary = {'total': 0, 'success': 0, 'done': 0, 'fail': 0, 'skip': 0, 'obtain': 0, 'video_limited': bool(stop_on_video_limit)}
    unique_golds = []
    for gold in reward_golds:
        gold_value = to_int(gold)
        if gold_value > 0 and gold_value not in unique_golds:
            unique_golds.append(gold_value)

    for idx, gold in enumerate(unique_golds, 1):
        if summary['video_limited']:
            summary['skip'] += 1
            continue

        summary['total'] += 1
        result = run_new_do_listen_task(
            '创意视频动态#' + str(idx),
            loginUid,
            loginSid,
            appUid,
            encrypted_phone,
            {
                'from': 'videoadver',
                'adverSpace': '20130101',
                'goldNum': str(gold),
                'secondRewardFlag': '0',
                'dynamicVer': '39',
            },
            verbose=verbose,
        )
        if result.get('success'):
            if result.get('done'):
                summary['done'] += 1
            else:
                summary['success'] += 1
                summary['obtain'] += to_int(result.get('obtain') or 0)
        else:
            summary['fail'] += 1

        description = str(result.get('description') or '')
        if is_video_limit_like(description):
            summary['video_limited'] = True
        time.sleep(3)
    return summary

def run_missing_listen_tasks(loginUid, loginSid, appUid, encrypted_phone, verbose=True):
    base_result = run_new_do_listen_task(
        '每日听歌奖励',
        loginUid,
        loginSid,
        appUid,
        encrypted_phone,
        {'goldNum': 18},
        verbose=verbose,
    )
    extra_result = run_new_do_listen_task(
        '每日听歌额外奖励',
        loginUid,
        loginSid,
        appUid,
        encrypted_phone,
        {'extraGoldNum': 60},
        verbose=verbose,
    )
    return {'base': base_result, 'extra': extra_result}

def run_sign_task_chain(loginUid, loginSid, appUid, encrypted_phone):
    sign_info = fetch_sign_list(loginUid, loginSid, appUid)
    if not sign_info['success']:
        return

    payload = sign_info.get('data', {})
    sign_flag = payload.get('isSign')
    signed_today = sign_flag is True or str(sign_flag).strip().lower() in ['1', 'true', 'yes']

    if signed_today:
        print('⏭️ 今日已签到，跳过签到主链')
    else:
        run_new_do_listen_task('签到视频奖励(new)', loginUid, loginSid, appUid, encrypted_phone, {'from': 'sign', 'extraGoldNum': 110}, verbose=True)
        run_everyday_do_listen_task('签到视频奖励(old)', loginUid, loginSid, appUid, {'from': 'sign', 'extraGoldNum': 110}, verbose=True)

    base_results = run_missing_listen_tasks(loginUid, loginSid, appUid, encrypted_phone, verbose=True)
    extra_video_limited = is_video_limit_like(base_results.get('extra', {}).get('description', ''))

    task_payload = fetch_dynamic_task_payload(loginUid, loginSid, appUid, payload)
    candidates = extract_listen_segment_candidates(task_payload)
    if not candidates:
        print('⏭️ 听歌分段任务: 未发现分段配置（listenList为空或结构变更）')
        return

    attempt_count = 0
    for candidate in candidates:
        if candidate.get('kind') == 'extra' and extra_video_limited:
            continue

        attempt_count += 1
        title = '听歌任务#' + str(candidate.get('idx'))
        if candidate.get('kind') == 'extra':
            title = '听歌额外#' + str(candidate.get('idx'))
        result = run_new_do_listen_task(
            title,
            loginUid,
            loginSid,
            appUid,
            encrypted_phone,
            candidate.get('params') or {},
            verbose=True,
        )
        if candidate.get('kind') == 'extra' and is_video_limit_like(result.get('description')):
            extra_video_limited = True

    if attempt_count == 0:
        print('⏭️ 听歌分段任务: 可尝试项仅含额外视频奖励，当前视频次数受限')

def run_coin_accumulation_tasks(loginUid, loginSid, appUid, encrypted_phone):
    for task_id in [1, 2, 3]:
        run_new_do_listen_task(
            '累计奖励任务' + str(task_id),
            loginUid,
            loginSid,
            appUid,
            encrypted_phone,
            {'from': 'coinAccumulationTask', 'taskId': task_id},
        )
        time.sleep(2)

def run_freemium_watch(loginUid, verbose=True):
    summary = {'success_count': 0, 'rounds': 0, 'total_minutes': 0, 'last_expiry': ''}
    if not str(loginUid).isdigit():
        if verbose:
            print('  ❌ loginUid 非数字，已跳过')
        return summary

    rounds = to_int(os.getenv('KUWO_FREEMIUM_LOOP', '1'))
    if rounds <= 0:
        rounds = 1
    if rounds > 10:
        rounds = 10
    summary['rounds'] = rounds

    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 4a Build/TQ3A.230805.001.S2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/134.0.6998.135 Mobile Safari/537.36/ kuwopage',
        'Accept': 'application/json, text/plain, */*',
    }

    for idx in range(rounds):
        req_id = ''.join(random.choices(string.hexdigits.lower(), k=32))
        url = FREEMIUM_SWITCH_URL + '?reqId=' + req_id
        body = {'loginUid': int(loginUid), 'status': 1}
        try:
            response = requests.post(url, headers=headers, json=body, timeout=30, verify=False)
            if response.status_code != 200:
                if verbose:
                    print('  第' + str(idx + 1) + '/' + str(rounds) + '次 ❌ HTTP ' + str(response.status_code))
                continue
            result = response.json()
            if result.get('code') == 200:
                data = result.get('data', {})
                if not isinstance(data, dict):
                    data = {}
                single_time = to_int(data.get('singleTime') or 0)
                end_time = to_int(data.get('endTime') or 0)
                expiry_text = ''
                if end_time > 0:
                    if end_time < 10**12:
                        end_time *= 1000
                    expiry_text = datetime.fromtimestamp(end_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    summary['last_expiry'] = expiry_text
                summary['success_count'] += 1
                summary['total_minutes'] += single_time
                if verbose:
                    if expiry_text:
                        print('  第' + str(idx + 1) + '/' + str(rounds) + '次 ✅ +' + str(single_time) + ' 分钟, 到期 ' + expiry_text)
                    else:
                        print('  第' + str(idx + 1) + '/' + str(rounds) + '次 ✅ +' + str(single_time) + ' 分钟')
            else:
                msg = str(result.get('msg', '未知错误'))
                if verbose:
                    print('  第' + str(idx + 1) + '/' + str(rounds) + '次 ❌ ' + msg)
                if is_done_like(msg):
                    break
        except Exception as e:
            if verbose:
                print('  第' + str(idx + 1) + '/' + str(rounds) + '次 ❌ ' + str(e))

    if verbose:
        summary_line = '  汇总: 成功 ' + str(summary['success_count']) + '/' + str(rounds) + ', 累计 ' + str(summary['total_minutes']) + ' 分钟'
        if summary['last_expiry']:
            summary_line += ', 到期 ' + summary['last_expiry']
        print(summary_line)
    return summary

def print_banner():
    print('\n        免责声明:\n仅供学习与接口研究，请在法律法规允许范围内使用并自行承担风险。\n    ')

def check_expiration():
    expiration_time = datetime(2026, 5, 1, 19, 0, 0)
    current_time = datetime.now()
    if current_time > expiration_time:
        print('\n============================================================')
        print('脚本已过期，请更新到新版本后再运行')
        print('============================================================')
        return False
    return True

if __name__ == '__main__':
    print('============================================================')
    print_banner()
    print('============================================================')
    if not check_expiration():
        exit()
    accounts = get_accounts_from_env()
    if not accounts:
        print('\n❌ 未读取到有效账号，请设置环境变量 kwyy')
        print('格式1: kwyy="手机号#密码"')
        print('格式2: kwyy="备注#手机号#密码"')
        print('多账号: kwyy="手机号1#密码1&手机号2#密码2"')
        exit()
    print('\n📱 获取到 ' + str(len(accounts)) + ' 个账号')
    for i, account in enumerate(accounts, 1):
        phone = account['phone']
        password = account['password']
        print('\n' + '==================================================')
        print('👤 账号 ' + str(i) + '/' + str(len(accounts)) + ': ' + str(phone))
        print('==================================================')
        encrypted_phone = encrypt_phone(phone)
        q_value, test_encrypted_dev_id = get_q(phone, password)
        print('用户名: ' + str(phone))
        result = login(phone, password)
        if result:
            loginUid, loginSid, username, appUid, encrypted_dev_id = result
            print('✅ 登录成功!')
            print('\n【1】资产查询:')
            asset_result = query_user_asset(loginUid, loginSid, appUid, verbose=False)
            if asset_result.get('success'):
                print('  结果: ✅ 剩余金币 ' + str(asset_result.get('score', 0)))
            else:
                print('  结果: ❌ 查询失败')
            print('\n【2】签到听歌任务链:')
            run_sign_task_chain(loginUid, loginSid, appUid, encrypted_phone)
            print('\n【3】累计奖励任务:')
            run_coin_accumulation_tasks(loginUid, loginSid, appUid, encrypted_phone)
            print('\n【4】开宝箱:')
            box_result = open_treasure_box(loginUid, loginSid, appUid, encrypted_dev_id, gold_num=20, verbose=False)
            if box_result['success']:
                print('  结果: ✅ +' + str(box_result.get('obtain', 0)) + ' 金币')
            else:
                print('  结果: ❌ ' + str(box_result['description']))
            print('\n【4.1】活动宝箱:')
            activity_box_result = run_activity_box_task(loginUid, loginSid, verbose=False)
            if activity_box_result.get('success'):
                if activity_box_result.get('done'):
                    print('  结果: ⏭️ ' + str(activity_box_result.get('description', '已完成')))
                else:
                    print('  结果: ✅ +' + str(activity_box_result.get('obtain', 0)) + ' 金币')
            else:
                print('  结果: ❌ ' + str(activity_box_result.get('description', '失败')))
            print('\n【4.2】时段宝箱补领:')
            run_box_renew_tasks(loginUid, loginSid, gold_num=30, verbose=True)
            print('\n【5】看视频拆红包:')
            ad_success_count = 0
            ad_total_gold = 0
            for j in range(30):
                ad_result = open_guanggao(loginUid, loginSid, appUid, encrypted_dev_id, 208, encrypted_phone, verbose=False)
                round_idx = j + 1
                if ad_result['success']:
                    obtain = to_int(ad_result.get('obtain') or 0)
                    ad_success_count += 1
                    ad_total_gold += obtain
                    print('  第' + str(round_idx) + '/30次 ✅ +' + str(obtain) + ' 金币')
                else:
                    print('  第' + str(round_idx) + '/30次 ❌ ' + str(ad_result['description']))
                    if is_done_like(ad_result.get('description')):
                        break
                time.sleep(5)
            print('  汇总: 成功 ' + str(ad_success_count) + '/30, 累计 ' + str(ad_total_gold) + ' 金币')
            print('\n【6】整点领金币:')
            clock_result = clock_bonus(loginUid, loginSid, appUid, encrypted_dev_id, encrypted_phone, verbose=False)
            if clock_result['success']:
                if clock_result.get('done'):
                    print('  结果: ⏭️ ' + str(clock_result.get('description', '已完成')))
                else:
                    print('  结果: ✅ +' + str(clock_result.get('obtain', 0)) + ' 金币')
            else:
                print('  结果: ❌ ' + str(clock_result['description']))
            print('\n【8】免费抽奖:')
            lottery_result = lottery_draw(loginUid, loginSid, appUid, verbose=False)
            if lottery_result['success']:
                reward_name = str(lottery_result.get('reward_name') or lottery_result.get('message') or '成功')
                free_obtain = to_int(lottery_result.get('obtain') or 0)
                if free_obtain > 0:
                    print('  结果: ✅ ' + reward_name + ' (+' + str(free_obtain) + ' 金币)')
                else:
                    print('  结果: ✅ ' + reward_name)
            else:
                print('  结果: ❌ ' + str(lottery_result['message']))
            print('\n【9】广告抽奖:')
            lottery_video_success = 0
            lottery_video_total_gold = 0
            for j in range(9):
                lottery_result = lottery_draw(loginUid, loginSid, appUid, lottery_type='video', verbose=False)
                round_idx = j + 1
                if lottery_result['success']:
                    reward_name = str(lottery_result.get('reward_name') or lottery_result.get('message') or '成功')
                    obtain = to_int(lottery_result.get('obtain') or 0)
                    lottery_video_success += 1
                    lottery_video_total_gold += obtain
                    if obtain > 0:
                        print('  第' + str(round_idx) + '/9次 ✅ ' + reward_name + ' (+' + str(obtain) + ' 金币)')
                    else:
                        print('  第' + str(round_idx) + '/9次 ✅ ' + reward_name)
                else:
                    print('  第' + str(round_idx) + '/9次 ❌ ' + str(lottery_result['message']))
                    if is_done_like(lottery_result.get('message')):
                        break
                time.sleep(5)
            print('  汇总: 成功 ' + str(lottery_video_success) + '/9, 累计 ' + str(lottery_video_total_gold) + ' 金币')
            print('\n【10】观看惊喜广告:')
            surprise_success_count = 0
            surprise_total_gold = 0
            for j in range(5):
                surprise_result = watch_surprise_ad(loginUid, loginSid, appUid, encrypted_dev_id, encrypted_phone, verbose=False)
                round_idx = j + 1
                if surprise_result['success']:
                    obtain = to_int(surprise_result.get('obtain') or 0)
                    surprise_success_count += 1
                    surprise_total_gold += obtain
                    print('  第' + str(round_idx) + '/5次 ✅ +' + str(obtain) + ' 金币')
                else:
                    print('  第' + str(round_idx) + '/5次 ❌ ' + str(surprise_result['description']))
                    if is_done_like(surprise_result.get('description')):
                        break
                time.sleep(5)
            print('  汇总: 成功 ' + str(surprise_success_count) + '/5, 累计 ' + str(surprise_total_gold) + ' 金币')
            print('\n【11】免费听歌时长任务:')
            run_freemium_watch(loginUid, verbose=True)
        else:
            print('❌ 登录失败，跳过后续测试')
        if i < len(accounts):
            print('\n⏳ 账号切换等待 10 秒...')
            time.sleep(5)
    print('\n============================================================')
    print('全部账号任务执行结束')
    print('============================================================')
