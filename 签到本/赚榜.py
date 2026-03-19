"""
项目名: 赚榜

注册地址: https://app.zhuanbang.net/invite/24721
推荐一个挣零花钱利器【赚榜】App，每天一两个小时，轻松赚取50元零花钱，我已提现到账了，3元起提，安全可靠！
①我的邀请链接是 https://app.zhuanbang.net/invite/24721 从我链接注册后下载自动建立邀请关系~
②在应用商店下载后，注册时输入邀请码“ 8024721”才会建立邀请关系哦~
③复制邀请口令“￥JZTFz0XYk9XC￥”再下载打开App注册也会自动建立邀请关系~
如果上面链接打不开，请运行下脚本就可以获取最新的注册地址
脚本功能:
    自动播放视频广告

配置参数:
    - `变量名：zhuanbang_accounts` 格式: 手机号#密码#账户备注，以`&`或换行符分隔或者多个同名环境变量。

不会配置？可以付费咨询 🤪

==================================================

广告区域（预留）:  服务器618大促 https://mp.weixin.qq.com/s/QwIEx-bDkk3QzBQar596TQ

仅用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断；您必须在下载后的24小时内从计算机或手机中完全删除以上内容。

如果任何单位或个人认为该项目的脚本可能涉嫌侵犯其权利，则应及时通知并提供身份证明，所有权证明，我们将在收到认证文件后删除相关脚本。

==================================================

脚本依赖：

    - Python依赖如下：
        - requests

---------------------------------------------------
"""

import os
import urllib3
import time
import random
import hashlib
from concurrent.futures import ThreadPoolExecutor
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

moreTip = "\n服务器618大促 https://mp.weixin.qq.com/s/QwIEx-bDkk3QzBQar596TQ"
inviteMsg = "注册地址: https://app.zhuanbang.net/invite/24721"


class ZBClient:
    def __init__(self, phone, password, nick_name):
        self._phone = phone
        self._password = password
        self._nick_name = nick_name
        self._cookie = ""
        self._headers = self._initialize_headers()
        self._session = requests.Session()
        self._session.verify = False
        self._session.headers.update(self._headers)
        self._csrf_token = ""
        self._session_id = ""
        self._time = ""

    def _initialize_headers(self):
        return {
            "Host": "app.zhuanbang.net",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "application/json, image/webp",
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; M2011K2C Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.74 Mobile Safari/537.36 HuoNiuFusion/1.26.0_240361",
            "X-Requested-With": "app.zhuanbang.com",
            "Referer": "https://app.zhuanbang.net/user/home",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cookie": f"NiuToken={self._cookie}" if self._cookie else None,
        }

    def _extract_middle_text(self, source, before_text, after_text, all_matches=False):
        results = []
        start_index = 0
        while True:
            start_index = source.find(before_text, start_index)
            if start_index == -1:
                break
            end_index = source.find(after_text, start_index + len(before_text))
            if end_index == -1:
                break
            results.append(source[start_index + len(before_text) : end_index])
            start_index = end_index + len(after_text)
            if not all_matches:
                break
        return results if all_matches else results[0] if results else ""

    def _make_sign(self):
        sha_str = hashlib.sha1(
            f"{self._csrf_token}#{self._session_id}#{self._time}".encode("utf-8")
        )
        return sha_str.hexdigest()

    def _login(self):
        try:
            login_url = "https://app.zhuanbang.net/cas/login"
            init_response = self._session.get(login_url)
            self._csrf_token = self._extract_middle_text(
                init_response.text,
                '<input type="hidden" name="_csrf_token" value="',
                '"',
            )
            self._cookie = init_response.cookies.get("NiuToken")
            if self._cookie and self._csrf_token:
                login_data = {
                    "_csrf_token": self._csrf_token,
                    "_target_path": "",
                    "_username": self._phone,
                    "_password": self._password,
                }
                login_url = f"https://app.zhuanbang.net/cas/login?_random={int(time.time() * 1000)}"
                login_response = self._session.post(
                    login_url, data=login_data, headers=self._headers
                )
                try:
                    loginKeys = login_response.cookies.keys()
                    if len(loginKeys):
                        print(f"[{self._nick_name}] 登录成功~")
                        return True
                    else:
                        print(f"[{self._nick_name}] 登录失败！")
                        return False
                except Exception as e:
                    # 如果解析JSON失败或响应中没有预期的键，这里会捕获异常
                    error_message = str(e)
                    error_message = (
                        self._extract_middle_text(
                            login_response.text, "<title>", "</title>"
                        )
                        or "登录请求结果异常"
                    )
                    print(f"[{self._nick_name}] 登录时发生错误：{error_message}")
                    return False
            print(f'[{self._nick_name}] 初始化登录失败：{init_response.json()["msg"]}')
            return False
        except Exception as e:
            print("登录请求异常：", e)

    def _video(self, key):
        i = 0
        while True:
            i += 1
            launch_url = f"https://app.zhuanbang.net/{key}/launch?_random={int(time.time() * 1000)}&type=slide"
            launch_response = self._session.get(launch_url).json()
            if launch_response.get("code") == 0:
                self._csrf_token = launch_response["data"]["extArgs"]["csrfToken"]
                self._session_id = launch_response["data"]["extArgs"]["sessionId"]
                self._time = int(time.time())
                award_url = (
                    f"https://app.zhuanbang.net/{key}/award/grant?_t={self._time}"
                )
                award_data = {
                    "csrfToken": self._csrf_token,
                    "deviceId": self._session_id,
                    "timestamp": str(self._time),
                    "sign": self._make_sign(),
                }
                award_response = self._session.post(award_url, data=award_data).json()
                if award_response.get("code") == 0:
                    print(
                        f"[{self._nick_name}] 领取第[{i}]个红包成功,获得[{award_response['data']['awardMoney']}]元"
                    )
                else:
                    print(
                        f"[{self._nick_name}] 领取第[{i}]个红包失败---[{award_response['msg']}]"
                    )
                    break
            else:
                print(
                    f"[{self._nick_name}] 领取第[{i}]个红包失败---[{launch_response['msg']}]"
                )
                break
            time.sleep(random.randint(20, 48))

    def _execute_task(self, task_key):
        self._headers = self._initialize_headers()
        self._video(task_key)

    def run_tasks(self, tasks):
        for task in tasks:
            print(
                f'[{self._nick_name}] 开始执行任务[{"快手视频任务" if tasks == "kwai_video" else "抖音视频任务"}]'
            )
            self._execute_task(task)


def process_account(phone_password):
    client = ZBClient(*phone_password.split("#"))
    if client._login():
        client.run_tasks(["kwai_video", "pangle_video"])


if __name__ == "__main__":
    accounts = os.getenv("zhuanbang_accounts", "").split("&")
    print(
        f"\n======== ▷ 开始启动脚本 ◁ ========\n\n当前脚本版本：赚榜 V1.00 \n幻生提示：获取到 {len(accounts) or 0} 个账号 {moreTip}\n{inviteMsg}\n不会配置？可以付费咨询 🤪\n\n{'-' * 36}\n"
    )
    if accounts and len(accounts):
        print(f"一共获取到{len(accounts)}个账号")
        for account in accounts:
            process_account(account)
        # 报错看不到，不好排错，注释
        # with ThreadPoolExecutor(max_workers=5) as executor:
        #     for account in accounts:
        #         executor.submit(process_account, account)
        print(f"\n======== ▷ 脚本运行完毕 ◁ ========\n")
    else:
        print(f"当前无账号，请先配置下 账号！")