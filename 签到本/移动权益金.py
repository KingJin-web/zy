# 软件：中国移动
# 功能：心愿金签到
# 抓包 移动APP抓包，闪退换旧版本9.，先开抓包进，biz-orange/LN/uamrandcodelogin/autoLogin 请求体全部
# 仅限安卓机器抓包使用，苹果机器抓包无法使用！
# 变量：xyjck
# 格式： 请求体值#手机号  多账号 @或者换行分割
# 日期 2024.1.1
#   - [12.6]:
# 定时：一天一次
# 作者: 木兮
import hashlib
import json
import os
import random
import re
import time
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

from os import path

reward_name = '2元话费券'  # 填写兑换奖品名称 ,0.5/1、1.5/2话费券
user_agents = {
    'app': 'Mozilla/5.0 (Linux; U; Android 11; zh-CN; M2012K10C Build/RP1A.200720.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.22.2.57 Mobile Safari/537.36 UCBS/3.22.2.57_221124174200 AlipayDefined AriverApp(mPaaSClient/10.2.8) MiniProgram  leadeon/8.9.0/CMCCIT/tinyApplet',
    'wx': 'Mozilla/5.0 (Linux; Android 11; M2012K10C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5197 MMWEBSDK/20230202 MMWEBID/2612 MicroMessenger/8.0.33.2320(0x28002135) WeChat/arm64 Weixin NetType/5G Language/zh_CN ABI/arm64',
    'wx_mini':
        'Mozilla/5.0 (Linux; Android 11; M2012K10C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5197 MMWEBSDK/20230202 MMWEBID/2612 MicroMessenger/8.0.33.2320(0x28002135) WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64 miniProgram/wx43aab19a93a3a6f2',
    'zfb': 'Mozilla/5.0 (Linux; U; Android 11; zh-CN; M2012K10C Build/RP1A.200720.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.22.2.59 Mobile Safari/537.36 UCBS/3.22.2.59_230213152242 NebulaSDK/1.8.100112 Nebula AlipayDefined(nt:3G,ws:393|0|2.75) AliApp(AP/10.3.86.8000) AlipayClient/10.3.86.8000 Language/zh-Hans useStatusBar/true isConcaveScreen/true Region/CNAriver/1.0.0 MiniProgram APXWebView',
}


# 通知服务加载
def load_send():
    """加载通知服务。"""
    cur_path = path.abspath(path.dirname(__file__))
    notify_file = path.join(cur_path, "/notify.py")

    if path.exists(notify_file):
        try:
            from notify import send
            print("加载通知服务成功！")
            return send
        except ImportError:
            print("通知服务模块导入失败。")
    else:
        print("未找到通知服务文件。")

    return None


class HB:
    def __init__(self, cookie, index):
        self.session = requests.Session()
        self.GLOBAL_DEBUG = False
        self.index = index
        self.cookie = cookie.split("#")[0]
        self.phone = cookie.split("#")[1]
        self.base_headers = {
            'Host': 'wx.10086.cn',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': user_agents['app'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }

    def send_request(self, url, headers=None, method='GET', data=None, debug=False, retries=5):
        """发送请求并处理响应。"""

        debug = debug if debug is not None else self.GLOBAL_DEBUG
        request_args = {'json': data} if isinstance(data, dict) else {'data': data}
        for attempt in range(retries):
            try:
                response = self.session.request(method, url, headers = headers, **request_args)
                response.raise_for_status()
                if debug:
                    print(f'\n【账号{self.index}】:{url}响应数据:\n{response.text}\n')
                return response
            except Exception as e:
                # print(f"【账号{self.index}】: {e}")
                if attempt >= retries - 1:
                    print(f"达到最大重试次数。")
                    return None
                time.sleep(0.1 * (2 ** attempt))

    # 随机延迟默认1-1.5s
    def sleep(self, min_delay=1, max_delay=1.5):
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    # 本地加密
    def encrypt(self, text_to_encrypt):
        key = base64.b64decode("YkFJZ3Z3QXVBNHRiRHI5ZA==")
        iv = base64.b64decode("OTc5MTAyNzM0MTcxMTgxOQ==")
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(text_to_encrypt.encode(), AES.block_size)
        # 加密
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(encrypted).decode()

    # 本地解密
    def decrypt(self, encrypted_base64):
        key = base64.b64decode("YkFJZ3Z3QXVBNHRiRHI5ZA==")
        iv = base64.b64decode("OTc5MTAyNzM0MTcxMTgxOQ==")
        encrypted = base64.b64decode(encrypted_base64)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(encrypted)
        decrypted = unpad(decrypted_padded, AES.block_size).decode()
        return decrypted

    # 响应解密
    def res_decrypt(self, base64_encrypted):
        base64_key = "R1M3VmVsa0psNUlUMXV3UQ=="
        base64_iv = "OTc5MTAyNzM0MTcxMTgxOQ=="

        # Base64解码
        key = base64.b64decode(base64_key)
        iv = base64.b64decode(base64_iv)
        encrypted_data = base64.b64decode(base64_encrypted)

        # 创建解密器
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # 解密数据
        decrypted_data = cipher.decrypt(encrypted_data)

        # 移除PKCS5Padding填充
        decrypted_data = unpad(decrypted_data, AES.block_size)

        return decrypted_data

    # 计算 MD5 哈希
    def calculate_md5(self, byte_data):
        text_bytes = byte_data.encode()
        md5_hash = hashlib.md5()
        md5_hash.update(text_bytes)
        return md5_hash.hexdigest()

    def build_headers(self, x_sign, tm, x_s, x_nonce, token, jsessionid=None):
        headers = {
            'Host': 'client.app.coc.10086.cn',
            'x-sign': x_sign,
            'x-time': str(tm),
            'xs': x_s,
            'x-qen': '2',
            'x-nonce': x_nonce,
            'x-token': token,
            'user-agent': 'okhttp/3.14.9',
            'content-type': 'application/json; charset=utf-8',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        if jsessionid:
            headers[
                'Cookie'] = jsessionid
        return headers

    def process_encryption(self, dee_te, url_pattern, jsessionid=None):
        decrypted_text = self.decrypt(dee_te)
        xk = json.loads(decrypted_text).get('xk')
        tm = int(time.time() * 1000)
        x_nonce = ''.join(random.choices('0123456789', k = 8))
        tk = f'{xk}_/{url_pattern}_{tm}_{x_nonce}'

        token = self.encrypt(tk)
        sign_data = f'{token}_{tm}_{x_nonce}_{"null" if not jsessionid else jsessionid}'
        x_sign = self.calculate_md5(sign_data)

        x_s = self.calculate_md5(
            f'https://client.app.coc.10086.cn/{url_pattern}_{decrypted_text}_Leadeon/SecurityOrganization')

        return x_sign, tm, x_s, x_nonce, token

    def activity_ck(self, source_id):
        decode_data = json.loads(self.decrypt(self.cookie))
        new_data = {
            "ak": decode_data.get('ak'),
            "cid": decode_data.get('cid'),
            "city": decode_data.get('city'),
            "ctid": decode_data.get('cid'),
            "cv": decode_data.get('cv'),
            "en": decode_data.get('en'),
            "imei": decode_data.get('imei'),
            "nt": decode_data.get('nt'),
            "prov": decode_data.get('prov'),
            "reqBody": {
                "appId": "8463803521674337",
                "cellNum": self.phone,
                "sourceId": source_id,
                "url": "empty"
            },
            "sb": decode_data.get('sb'),
            "sn": decode_data.get('sn'),
            "sp": decode_data.get('sp'),
            "st": decode_data.get('st'),
            "sv": decode_data.get('sv'),
            "t": "",
            "tel": self.phone,
            "xc": decode_data.get('xc'),
            "xk": decode_data.get('xk')
        }

        compact_json = json.dumps(new_data, separators = (',', ':'))

        return self.encrypt(compact_json)

    def get_sso_token(self):
        url_pattern = 'biz-orange/LN/uamrandcodelogin/autoLogin'
        x_sign, tm, x_s, x_nonce, token = self.process_encryption(self.cookie, url_pattern)

        url = f"https://client.app.coc.10086.cn/{url_pattern}"
        headers = self.build_headers(x_sign, tm, x_s, x_nonce, token)

        response = self.send_request(url, headers = headers, data = self.cookie, method = "POST")
        jsessionid_value = response.headers.get('Set-Cookie')

        if jsessionid_value:
            de_te2 = self.activity_ck('017018')

            url_pattern2 = 'leadeon-abilityopen-biz/BN/obtainToken/getBigNetToken'
            x_sign, tm, x_s, x_nonce, token = self.process_encryption(de_te2, url_pattern2, jsessionid_value)

            url = f"https://client.app.coc.10086.cn/{url_pattern2}"
            headers2 = self.build_headers(x_sign, tm, x_s, x_nonce, token, jsessionid_value)

            response = self.send_request(url, headers = headers2, data = de_te2, method = "POST")
            decode = json.loads(self.res_decrypt(response.text))
            if decode.get('retDesc') == 'SUCCESS':
                sso_token = decode.get('rspBody').get('token')
                return sso_token
            else:
                print(decode)
                return None

        else:
            print("JSESSIONID not found")
            return None

    def login(self):
        sso_token = self.get_sso_token()
        if sso_token is None:
            print(f'{self.phone}登录失败')
            return
        headers = {
            'Host': 'wx.10086.cn',
            'Connection': 'keep-alive',
            'login-check': '1',
            'Accept-Encoding': 'gzip',
            'content-type': 'application/json;charset=UTF-8',
            'User-Agent': user_agents['app']
        }
        login_url = f'http://wx.10086.cn/qwhdhub/user/tokenLogin?activityId=1021122301&channelId=P00000054142&token={sso_token}&tokenType=1'
        login_res = self.send_request(login_url, headers = self.base_headers)
        set_cookie = login_res.headers.get('Set-Cookie')
        self.base_headers['Cookie'] = set_cookie
        lg_url = 'http://wx.10086.cn/qwhdhub/api/mark/user/info'
        lg_payload = {
            "appVersion": "9.3.0",
            "miniVersion": "2023.12.29.10"
        }

        lg_res = self.send_request(lg_url, headers = self.base_headers, data = lg_payload, method = "POST").json()
        if lg_res.get('code') == 'SUCCESS':
            print('移动心愿金登录成功')
            self.sign_in()

            agents = [
                {'name': 'app任务', 'user_agent': user_agents['app']},
                {'name': '微信公众号任务', 'user_agent': user_agents['wx']},
                {'name': '微信小程序任务', 'user_agent': user_agents['wx_mini']},
                {'name': '支付宝小程序任务', 'user_agent': user_agents['zfb']},
            ]

            for agent in agents:
                # if agent['name'] == '支付宝小程序任务':
                #     print('---暂时关闭支付宝小程序任务---')
                #     continue

                self.base_headers['User-Agent'] = agent['user_agent']
                print(f"\n========{agent['name']}========")

                self.get_task_list()
                time.sleep(2)

            # 等待500毫秒后查询用户信息
            time.sleep(0.5)
            self.userInfo()
        else:
            print(lg_res.get('msg'))

    def sign_in(self):
        try:
            info_url = 'http://wx.10086.cn/qwhdhub/api/mark/info/prizeInfo'
            info_data = self.send_request(info_url, headers = self.base_headers, method = "POST").json()

            if info_data['code'] != 'SUCCESS':
                print(info_data.get('msg', ''))
                return

            if info_data['data']['todayMarked']:
                print('今日已签到')
                return

            time.sleep(0.5)

            sign_url = 'http://wx.10086.cn/qwhdhub/api/mark/do/mark'
            sign_data = self.send_request(sign_url, headers = self.base_headers, method = "POST").json()

            if sign_data['code'] != 'SUCCESS':
                print(sign_data.get('msg', ''))
                return

            print('签到成功')
        except Exception as e:
            print(f'签到失败，错误信息：{e}')

    def get_task_list(self):
        try:
            response = requests.post('http://wx.10086.cn/qwhdhub/api/mark/task/taskList', headers = self.base_headers,
                                     json = {})
            return_data = response.json()

            if return_data['code'] != "SUCCESS":
                print(return_data['msg'])
                return

            task_list = return_data['data']['tasks']

            for taskType in ["1", "2", "3"]:  # 每日、每周、每月任务
                print(f"-----{taskType}类任务-----")
                for task in task_list:
                    if task['taskType'] == taskType:
                        self.doTask(task)

        except Exception as error:
            print('查询出错了:', error)

    def doTask(self, task):
        taskId = task['taskId']
        status = task['status']
        taskName = task['taskName']

        try:
            if not status:
                print(f'去完成:[{taskName}]')
                self.completeTask(taskId, task)
            elif status == 2:
                print(f'已领取:[{taskName}]')
            elif status == 1:
                print(f'去领取:[{taskName}]')
                self.completeTask(taskId, task)
        except Exception as e:
            print(f'处理任务 {taskId} 时出错: {e}')

    def completeTask(self, taskId, task):
        # 完成任务逻辑
        try:
            if task['status'] == 0:
                infoUrl = 'http://wx.10086.cn/qwhdhub/api/mark/task/taskInfo'
                response = requests.post(infoUrl, headers = self.base_headers, json = {"taskId": taskId})
                return_data = response.json()
                if return_data['code'] != "SUCCESS":
                    print(return_data['msg'])
                    return
                taskType = return_data['data']['taskType']
                time.sleep(5)  # 等待 5 秒
                finishUrl = 'http://wx.10086.cn/qwhdhub/api/mark/task/finishTask'
                response = requests.post(finishUrl, headers = self.base_headers,
                                         json = {"taskId": taskId, "taskType": taskType})
                return_data2 = response.json()
                if return_data2['code'] != "SUCCESS":
                    print(return_data2['msg'])
                    return

            rewardUrl = 'http://wx.10086.cn/qwhdhub/api/mark/task/getTaskAward'
            response = requests.post(rewardUrl, headers = self.base_headers, json = {"taskId": taskId})
            return_data3 = response.json()
            if return_data3['code'] != "SUCCESS":
                print(return_data3['msg'])
                return
            awardNum = return_data3['data']['awardNum']
            print(f'领取{awardNum}心愿值')

        except Exception as error:
            print('出错了:', error)

    def userInfo(self):
        try:
            url = 'http://wx.10086.cn/qwhdhub/api/mark/task/getExchangeList'
            response = requests.post(url, headers = self.base_headers, json = {"channel": "app"})
            return_data = response.json()

            if return_data['code'] != "SUCCESS":
                print(return_data['msg'])
                return

            currentFee = float(return_data['data']['currentFee'])
            print(f"\n当前用户剩余:{currentFee}心愿金")

            if reward_name == '':
                print("当前用户未开启兑换")
                return

            prizes = return_data['data']['prizes']
            prize = next((p for p in prizes if p['name'] == reward_name), None)
            if not prize:
                print("未找到对应奖品")
                return

            cost = prize['cost']
            prizeId = prize['id']
            if currentFee <= cost:
                print("当前心愿金不足")
                return
            print(f"去兑换奖品: {reward_name}")
            self.exchange(prizeId)

        except Exception as error:
            print('查询出错了:', error)

    def exchange(self, prizeId):
        try:
            stockUrl = 'http://wx.10086.cn/qwhdhub/api/mark/task/checkStock'
            exchangeUrl = 'http://wx.10086.cn/qwhdhub/api/mark/task/exchange'

            # 检查库存
            stock_response = requests.post(stockUrl, headers = self.base_headers, json = {"prizeId": prizeId})
            stockData = stock_response.json()
            if stockData['code'] != "SUCCESS":
                print(stockData['msg'])
                return
            stock = stockData['data']['stock']
            if stock == 0:
                print("当前库存为0，请明天再来兑换!")
                return
            print(f"当前库存数量:{stock}")

            # 进行兑换
            exchange_response = requests.post(exchangeUrl, headers = self.base_headers, json = {"prizeId": prizeId})
            exchangeData = exchange_response.json()
            if exchangeData['code'] != "SUCCESS":
                print(exchangeData['msg'])
                return
            print("兑换成功，请记得去使用哦!")

        except Exception as error:
            print('兑换出错了:', error)


if __name__ == "__main__":
    env_name = 'xyjck'
    py_name = '移动心愿金'
    token = os.getenv(env_name)
    if not token:
        print(f'⛔️未获取到ck变量：请检查变量 {env_name}是否填写')
        exit(0)

    cookies = re.split(r'[@\n]', token)
    print(f"{py_name}共获取到{len(cookies)}个账号")

    msg = ''
    for i, cookie in enumerate(cookies, start = 1):
        print(f"\n======== ▷ 账号【{i}】 ◁ ========")
        requestor = HB(cookie, i)
        requestor.login()

    send = load_send()
    if send:
        send(py_name, msg)
    else:
        print('通知服务不可用')