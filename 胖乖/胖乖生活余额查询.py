"""
 * 胖乖生活积分余额查询
 * 设置变量 PGSH_TOKEN ,多号使用回车隔开，青龙直接新建变量即可 ，网页获取ck：https://bigostk.github.io/pg/
 * cron：02 12 * * 6
"""

##############################
ck = ''
ckurl1 = ""  # 数据库地址，适配部分群友要求
jh = False  # 聚合ck模式，开启即所有环境模式ck都生效，都会合成为一个ck列表，关闭则优先处理环境变量，默认为True，False为关闭

#############################
# -----运行模式配置区，自行配置------

bf1 = True  # True开启并发，False关闭并发
bfsum1 = 3  # 并发数,开启并发模式生效
lljf = 1  # 运行新版浏览任务，22金币,只有10天

# -------推送配置区，自行填写-------

ts1 = False  # True开启推送，False关闭推送

# -------代理配置区，自行填写-------

dl1 = False  # True开启代理，False关闭代理
dl_url = 'http://api.xiequ.cn/VAD/GetIp.aspx?act=getturn82&uid=150098&vkey=617AF361D1745BECBC40DD5707FF3C27&num=1&time=6&plat=1&re=0&type=7&so=1&group=51&ow=1&spl=4&addr=&db=1'  # 代理池api

# -----代理时间配置区，秒为单位------

dl_sleep = 30  # 代理切换时间
qqtime = 6  # 请求超时时间

# -----时间配置区，默认即可------

a = "1"
b = "23"  # 表示6-22点之间才执行任务

#############################
# ---------勿动区----------

# 已隐藏乾坤于此区域

###########################
# ---------代码块---------

import requests
import time
import random
import string
import os
import json
import hashlib
import threading
from functools import partial
from urllib.parse import urlparse
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib3.exceptions import InsecureRequestWarning
from requests_toolbelt import MultipartEncoder

dl = os.environ.get('pg_dl', dl1)
proxy_api_url = os.environ.get('pg_dlurl', dl_url)
bf = os.environ.get('pg_bf', bf1)
bfsum = os.environ.get('pg_bfsum', bfsum1)
ts = os.environ.get('pg_ts', ts1)
ckurl = os.environ.get('pg_ckurl', ckurl1)
WxPusher_uid = os.environ.get('pg_WxPusher_uid')
WxPusher_token = os.environ.get('pg_WxPusher_token')
pushplus_token = os.environ.get('pg_pushplus_token')

# def check_yl():
#     lb = ['requests', 'urllib3']
#     for yl in lb:
#         try:
#             subprocess.check_call(["pip", "show", yl], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#         except subprocess.CalledProcessError:
#             print(f"{yl} 未安装，开始安装...")
#             subprocess.check_call(["pip", "install", yl, "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#             print(f"{yl} 安装完成")
# check_yl()

v = '6.6.6'

global_proxy = {
    'http': None,
    'https': None
}


def start_dlapi():
    dlstart = threading.Thread(target=get_proxy, args=(stop_event,))
    dlstart.start()


stop_event = threading.Event()


def get_proxy(stop_event):
    global global_proxy, ipp
    a = 0
    while not stop_event.is_set():
        a += 1
        response = requests.get(proxy_api_url)
        if response.status_code == 200:
            proxy1 = response.text.strip()
            if "白名单" not in proxy1:
                print(f'✅第{a}次获取代理成功: {proxy1}')
                ipp = proxy1.split(':')[0]
                global_proxy = {
                    'http': proxy1,
                    'https': proxy1,
                }
                start_time = time.time()
                while time.time() - start_time < dl_sleep:
                    if ip():
                        print("✅代理检测通过,可以使用")
                        time.sleep(2)
                    else:
                        print(f'❎当前ip不可用，第{a}次重新获取！')
                        break
                continue
            else:
                print(f"请求代理池: {proxy1}")
                print("响应中存在白名单字样，结束运行")
                os._exit(0)
        else:
            print(f'❎第{a}次获取代理失败！重新获取！')
            time.sleep(dl_sleep)
            continue


def ip():
    try:
        if global_proxy:
            r = requests.get('http://httpbin.org/ip', proxies=global_proxy, timeout=10, verify=False)
        else:
            r = requests.get('http://httpbin.org/ip')
        if r.status_code == 200:
            ip = r.json()["origin"]
            print(f"当前IP: {ip}")
            return ip
        else:
            print(f"❎查询ip失败")
            return None
    except requests.RequestException as e:
        print(f"❎查询ip错误")
        return None
    except Exception as e:
        print(f"❎查询ip错误")
        return None


def p(p):
    if len(p) == 11:
        return p[:3] + '****' + p[7:]
    else:
        return p


class PGSH:
    def __init__(self, cki):
        self.msg = None
        self.messages = []
        self.title = None
        self.phone = None
        self.token = cki.split('#')[0]
        self.cook = cki
        self.total_amount = 0
        self.id = None
        self.hd = {
            'User-Agent': "okhttp/3.14.9",
            'Accept': 'application/json, text/plain, */*',
            'Version': "1.57.2",
            'Content-Type': "application/x-www-form-urlencoded;charset=UTF-8",
            'Authorization': self.token,
            'channel': "android_app"
        }
        self.hd1 = {
            'User-Agent': "okhttp/3.14.9",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': self.token,
            'Version': "1.57.2",
            'channel': "android_app",
            'phoneBrand': "Redmi",
            'Content-Type': "application/x-www-form-urlencoded;charset=UTF-8"
        }
        self.listUrl = 'https://userapi.qiekj.com/task/list'
        self.phone_url = 'https://userapi.qiekj.com/user/info'
        self.check_url = 'https://userapi.qiekj.com/user/balance'
        self.rcrw_url = 'https://userapi.qiekj.com/task/completed'
        self.sign_url = 'https://userapi.qiekj.com/signin/doUserSignIn'
        self.jrjf_url = "https://userapi.qiekj.com/integralRecord/pageList"
        self.dkbm_url = 'https://userapi.qiekj.com/markActivity/doApplyTask'
        self.dkbm_url1 = 'https://userapi.qiekj.com/markActivity/doMarkTask'
        self.shop_url = 'https://userapi.qiekj.com/integralUmp/rewardIntegral'
        self.jtjl_url = 'https://userapi.qiekj.com/ladderTask/applyLadderReward'
        self.dkbm_url2 = "https://userapi.qiekj.com/markActivity/markTaskReward"
        self.bmcodeurl = 'https://userapi.qiekj.com/markActivity/queryMarkTaskByStartTime'

    # 签名
    def sg(self, y):
        timestamp = str(int(time.time() * 1000))
        parsed_url = urlparse(y)
        path = parsed_url.path
        data = f"appSecret=nFU9pbG8YQoAe1kFh+E7eyrdlSLglwEJeA0wwHB1j5o=&channel=android_app&timestamp={timestamp}&token={self.token}&version=1.57.2&{path}"
        data1 = f"appSecret=Ew+ZSuppXZoA9YzBHgHmRvzt0Bw1CpwlQQtSl49QNhY=&channel=alipay&timestamp={timestamp}&token={self.token}&{path}"
        sign = hashlib.sha256(data.encode()).hexdigest()
        sign1 = hashlib.sha256(data1.encode()).hexdigest()
        return sign, sign1, timestamp

    # 读取指定值是否存在
    def duqu(self, aa, rw, dk, dt):
        try:
            if not os.path.exists("./pgsh.json"):
                with open("./pgsh.json", "w") as file:
                    json.dump({}, file)

            with open("./pgsh.json", "r") as file:
                try:
                    data = json.load(file)
                except json.decoder.JSONDecodeError:
                    data = {}
            if rw == 1:
                if str(aa) in data:
                    return data[str(aa)]["rw"]
                else:
                    return False
            elif dk == 1:
                if str(aa) in data:
                    return data[str(aa)]["dk"]
                else:
                    return False
            elif dt == 1:
                if str(aa) in data:
                    return data[str(aa)]["dt"]
                else:
                    return False
        except Exception as e:
            print(f"读取记录文件出现错误,初始化文件内容")
            with open("./pgsh.json", "w") as file:
                json.dump({}, file)

    # 今日积分
    def jrjf(self, i, token1 ,source):
        token = token1.split('#')[0]
        try:
            hd1 = {
                'User-Agent': "okhttp/3.14.9",
                'Accept': 'application/json, text/plain, */*',
                'Version': "1.57.2",
                'Content-Type': "application/x-www-form-urlencoded;charset=UTF-8",
                'Authorization': token,
                'channel': "android_app"
            }
            data = {'token': token}
            sign, sign1, timestamp = self.sg(self.phone_url)
            self.hd['sign'] = sign
            self.hd['timestamp'] = timestamp
            r = requests.post(self.phone_url, data=data, headers=hd1).json()
            if r['code'] == 0:
                try:
                    sign, sign1, timestamp = self.sg(self.check_url)
                    self.hd['sign'] = sign
                    self.hd['timestamp'] = timestamp
                    r1 = requests.post(self.check_url, data=data, headers=hd1).json()
                    coin_code = r1['code']
                    balance = r1['data']['integral'] if coin_code == 0 else 'N/A'
                except Exception as e:
                    print(f"获取积分失败: {e}")
                    balance = 'N/A'

                try:
                    phone = p(r['data']['phone'])
                    data = {
                        'page': (None, '1'),
                        'pageSize': (None, '100'),
                        'type': (None, '100'),
                        'receivedStatus': (None, '1'),
                        'token': (None, token),
                    }
                    hd = {
                        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; 23117RK66C Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/118.0.0.0 Mobile Safari/537.36 AgentWeb/5.0.0 UCBrowser/11.6.4.950 com.qiekj.QEUser',
                        'Accept': 'application/json, text/plain, */*',
                        'channel': 'android_app',
                    }
                    re_response = requests.post(self.jrjf_url, headers=hd, files=data).json()
                    current_date = datetime.now().strftime('%Y-%m-%d')
                    total_amount = 0
                    xieru_tips = ''
                    default_num = 170
                    for item in re_response['data']['items']:
                        received_date = item['receivedTime'][:10]
                        if received_date == current_date:
                            total_amount += item['amount']
                    if source == 2:
                        if total_amount >= default_num and self.name(2):
                            print(f"写入日志状态：{self.xieru(1, 0, 0)}")
                        else:
                            print(f"写入日志状态：未达标写入目标{default_num}积分")
                    else:
                        print(f"[{phone}] ✅今日获得积分: {total_amount},账户总积分:{balance}")
                    return {
                        '序号': i + 1,
                        '用户': phone,
                        'arg1': balance,
                        'arg2': total_amount
                    }
                except Exception as e:
                    print(f"[账号{i + 1}] ❎查询当日积分出现错误: {e}")
                    return {
                        '序号': i + 1,
                        '用户': i + 1,
                        'arg1': f"❎",
                        'arg2': f"❎"
                    }
            else:
                print(f"[账号{i + 1}] ❎登录失败: {r['msg']}")
                return {
                    '序号': i + 1,
                    '用户': i + 1,
                    'arg1': f"{r['msg']}",
                    'arg2': f"{r['msg']}"
                }
        except requests.exceptions.RequestException as e:
            print(f"[账号{i + 1}] ❎网络请求错误: {e}")
            return {
                '序号': i + 1,
                '用户': i + 1,
                'arg1': f"❎",
                'arg2': f"❎"
            }
        except Exception as e:
            print(f"[账号{i + 1}] ❎查询当日积分出现错误: {e}")
            return {
                '序号': i + 1,
                '用户': i + 1,
                'arg1': f"❎",
                'arg2': f"❎"
            }

    def jf(self):
        try:
            msg_list = []
            print(f"======开始查询所有账号当日收益======")
            for n, yy in enumerate(cookies):
                msg = self.jrjf(n, yy,1)
                msg_list.append(msg)
            sorted_data = sorted(msg_list, key=lambda x: x['序号'])
            table_content = ''
            for row in sorted_data:
                table_content += f"<tr><td style='border: 1px solid #ccc; padding: 6px;'>{row['序号']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['用户']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['arg1']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['arg2']}</td></tr>"

            self.msg = f"<table style='border-collapse: collapse;'><tr style='background-color: #f2f2f2;'><th style='border: 1px solid #ccc; padding: 8px;'>🆔</th><th style='border: 1px solid #ccc; padding: 8px;'>用户名</th><th style='border: 1px solid #ccc; padding: 8px;'>总积分</th><th style='border: 1px solid #ccc; padding: 8px;'>今日积分</th></tr>{table_content}</table>"
            if ts:
                self.send_msg()
        except Exception as e:
            print(f"查询所有账号当日收益出现错误: {e}")

    def send_msg(self):
        if 'WxPusher_token' in os.environ and os.environ['WxPusher_token'] is not None:
            self.WxPusher_ts()
        if 'PUSH_PLUS_TOKEN' in os.environ and os.environ['PUSH_PLUS_TOKEN'] is not None:
            self.pushplus_ts()
        else:
            print("❎推送失败，未配置推送")

    def WxPusher_ts(self):
        try:
            url = 'https://wxpusher.zjiecode.com/api/send/message'
            params = {
                'appToken': WxPusher_token,
                'content': self.msg,
                'summary': '胖乖生活',
                'contentType': 3,
                'uids': [WxPusher_uid]
            }
            re = requests.post(url, json=params)
            msg = re.json().get('msg', None)
            print(f'WxPusher推送结果：{msg}\\\n')
        except Exception as e:
            print(f"WxPusher推送出现错误: {e}")

    def pushplus_ts(self):
        try:
            url = 'https://www.pushplus.plus/send/'
            data = {
                "token": pushplus_token,
                "title": '胖乖生活',
                "content": self.msg
            }
            re = requests.post(url, json=data)
            msg = re.json().get('msg', None)
            print(f'pushplus推送结果：{msg}\\\n')
        except Exception as e:
            print(f"pushplus推送出现错误: {e}")

    def start(self):
        if self.name(1):
            print("-----执行领取时间段奖励-----")
            self.timejl()

if __name__ == '__main__':
    print(f"当前版本: {v}")
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    print = partial(print, flush=True)
    if jh:
        print("当前聚合ck模式，所有模式ck生效")
        ck1 = []
        if 'PGSH_TOKEN' in os.environ:
            ck1.append(os.environ.get('PGSH_TOKEN'))
        if ckurl != "":
            r = requests.get(ckurl)
            ck1.append(r.text.strip())
        if ck != "":
            ck1.append(ck)
        if not ck1:
            print("变量为空，请设置其中一个变量后再运行")
            exit(-1)
        cookie = '\n'.join(ck1)
    else:
        if 'PGSH_TOKEN' in os.environ:
            cookie = os.environ.get('PGSH_TOKEN')
        else:
            print("环境变量中不存在[PGSH_TOKEN],启用本地或数据库地址模式")
            if ckurl != "":
                r = requests.get(ckurl)
                cookie = r.text.strip()
            else:
                cookie = ck
        if cookie == "":
            print("本地及数据库地址变量为空，请设置其中一个变量后再运行")
            exit(-1)
    cookies = cookie.split("\n")
    print(f"胖乖生活共获取到 {len(cookies)} 个账号")
    now_time = datetime.now().hour
    if dl:
        start_dlapi()
    i = 1
    if bf:
        print("✅开启并发模式")
        if dl:
            print("✅开启代理模式")
            with ThreadPoolExecutor(max_workers=int(bfsum)) as executor:
                futures = [executor.submit(PGSH(ck).start) for ck in cookies]
                for i, future in enumerate(as_completed(futures)):
                    print(f"======执行第{i + 1}个账号======")
                    future.result()
            stop_event.set()
            time.sleep(2)
            PGSH(ck).jf()
        else:
            print("❎未开启代理模式")
            with ThreadPoolExecutor(max_workers=int(bfsum)) as executor:
                futures = [executor.submit(PGSH(ck).start) for ck in cookies]
                for _ in as_completed(futures):
                    pass
            time.sleep(2)
            PGSH(ck).jf()
    else:
        print("✅常规运行模式")
        if dl:
            print("✅开启代理模式")
            for i, ck in enumerate(cookies):
                print(f"======开始第{i + 1}个账号======")
                now_time = datetime.now().hour
                PGSH(ck).start()
                print("2s后进行下一个账号")
                time.sleep(2)
            stop_event.set()
            time.sleep(2)
            PGSH(ck).jf()
        else:
            print("❎未开启代理模式")
            for i, ck in enumerate(cookies):
                print(f"======开始第{i + 1}个账号======")
                now_time = datetime.now().hour
                PGSH(ck).start()
                print("2s后进行下一个账号")
                time.sleep(2)
            time.sleep(2)
            PGSH(ck).jf()