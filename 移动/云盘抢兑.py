# cron 
import os
import random
import time
import json
import requests

cookies = os.getenv("ydypCK")
def getUA():
    safari_version = f'{random.randint(600, 700)}.{random.randint(1, 4)}.{random.randint(1, 5)}'
    ios_version = f'{random.randint(12, 15)}.{random.randint(0, 6)}.{random.randint(0, 9)}'
    ua_string = f'Mozilla/5.0 (iPhone; CPU iPhone OS {ios_version} like Mac OS X) AppleWebKit/{safari_version} (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.20(0x16001422) NetType/WIFI Language/zh_CN'
    return ua_string

class YP:
    token = None
    jwtToken = None
    notebook_id = None
    draw = 1
    num = 100
    timestamp = str(int(round(time.time() * 1000)))
    cookies = {'sensors_stay_time': timestamp}

    def __init__(self, cookie):
        parts = cookie.split("#")
        self.Authorization = parts[0]
        self.account = parts[1]
        if len(parts) > 2:
            self.cash = parts[2]
            self.convertible = True
        else:
            self.cash = None
            self.convertible = False
            print("未检测到商品ID，该账号不执行兑换！")
        self.jwtHeaders = {
            'User-Agent': getUA(),
            'Accept': '*/*',
            'Host': 'caiyun.feixin.10086.cn:7071',
        }

    def run(self):
        self.sso()
        self.jwt()
        # self.get_shop()
        self.rob_cash()

    def send_request(self, url, headers, data=None, method='GET', cookies=None):
        with requests.Session() as session:
            session.headers.update(headers)
            if cookies is not None:
                session.cookies.update(cookies)

            try:
                if method == 'GET':
                    response = session.get(url, timeout = 10)
                elif method == 'POST':
                    response = session.post(url, json = data, timeout = 10)
                else:
                    raise ValueError('Invalid HTTP method.')

                response.raise_for_status()
                return response.json()

            except requests.Timeout as e:
                print("请求超时:", str(e))

            except requests.RequestException as e:
                print("请求错误:", str(e))

            except Exception as e:
                print("其他错误:", str(e))

    # 随机延迟默认1-1.5s
    def sleep(self, min_delay=1, max_delay=1.5):
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    # 刷新令牌
    def sso(self):
        url = 'https://orches.yun.139.com/orchestration/auth-rebuild/token/v1.0/querySpecToken'
        headers = {
            'Authorization': self.Authorization,
            'User-Agent': getUA(),
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': 'orches.yun.139.com'
        }
        data = {"account": self.account, "toSourceId": "001005"}
        return_data = self.send_request(url, headers = headers, data = data, method = 'POST')
        # self.sleep()
        if 'success' in return_data:
            if return_data['success']:
                self.token = return_data['data']['token']
            else:
                print(return_data['message'])
        else:
            print("出现未知错误")

    # 获取jwttoken
    def jwt(self):
        url = f"https://caiyun.feixin.10086.cn:7071/portal/auth/tyrzLogin.action?ssoToken={self.token}"
        return_data = self.send_request(url = url, headers = self.jwtHeaders, method = 'POST')
        # self.sleep()
        if return_data['code'] != 0:
            return print(return_data['msg'])
        self.jwtToken = return_data['result']['token']
        # print(str(return_data['result']['token']))
        self.jwtHeaders['jwtToken'] = self.jwtToken
        self.cookies['jwtToken'] = self.jwtToken
    
    # 获取可兑换商品列表
    def get_shop(self):
        url = "https://mrp.mcloud.139.com/market/signin/page/exchangeList?client=app&clientVersion=11.3.2"
        return_data = self.send_request(url, headers = self.jwtHeaders, cookies = self.cookies)
        self.sleep()
        if 'result' in return_data:
            # 提取并打印商品ID和商品名
            for key, item_list in return_data['result'].items():
                for item in item_list:
                    oid = item['oid']
                    pOrder = item['pOrder']
                    prize_name = item['prizeName']
                    print(f'商品ID: {oid}, 商品名: {prize_name}, 兑换所需数量: {pOrder}')


    # 兑换商品
    def rob_cash(self):
        # print(f'第三次状态为：{self.convertible}')
        if not self.convertible:
            return "兑换状态不可用"
        url = f'https://mrp.mcloud.139.com/market/signin/page/exchange?prizeId={self.cash}&client=app&clientVersion=11.3.2&smsCode='
        
        response = self.send_request(url, headers=self.jwtHeaders, cookies=self.cookies)
        print(response)
        # print('111')
        if response['msg'] == 'success':
            serv_number = response['result']['servNumber']
            prize_name = response['result']['prizeName']
            hidden_serv_number = f"{serv_number[:3]}****{serv_number[7:]}"
            success_message = f"✅️用户{hidden_serv_number}兑换{prize_name}成功"
            print(success_message)
            return success_message
        else:
            print(response.get('msg'))
            return response.get('msg')
        
if __name__ == "__main__":
    cookies = cookies.split("@")
    ydypqd = f"移动云盘共获取到{len(cookies)}个账号"
    print(ydypqd)
    for i, cookie in enumerate(cookies, start = 1):
        try:
            print(f"\n======== ▷ 第 {i} 个账号 ◁ ========")
            YP(cookie).run()
                # print("\n随机等待5-10s进行下一个账号")
                # time.sleep(random.randint(5, 10))
        except:
            print("开始下个账号...")