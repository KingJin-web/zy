# Obfuscated at 2025-06-01 12:40:09.512315
_WIqodQfs = lambda *_: None
"""
💰 可乐阅读_半自动版_V5.22   ♻202505022

🔔每次运行都要抓包，有能力的自己改，每天跑100篇就行，跑多容易黑号，第1篇和第101或102篇是检测文章。

🔔阅读赚金币，金币可提现，每天1—2元，本脚本自动推送检测文章到微信，需要用户手动阅读过检测，过检测后脚本自动完成剩余任务，不需要下载app，在微信打开下方链接即可进入到活动页。

👉活动入口 微信打开：https://img.hnking.cn//blog/202507192347464.png

👉建议将链接添加至微信收藏(微信_我_收藏_⊕_粘贴)，并添加到悬浮窗，方便进入活动主页

⚠️进入后点击永久入口，保存二维码，当链接失效时扫码获取最新链接！

参数：
1、打开抓包软件并用可乐读书读文章，文章加载完成后开启抓包软件然后阅读返回等待加载下一篇，下一篇加载完成关闭抓包软件，在抓包数据中下翻到底部在响应码302附近找到“http://u599…”响应码为200的包。打开后复制域名，点击最上方的url，复制iu数据，响应体中复制jkey数据。分别粘贴到变量中。
2、为了方便修改变量，每个变量按两次回车，中间正好空一行
3、最后一个是推送token，本脚本不需要，随便填几个数字即可

变量名：klyd
变量值：
MD123……

MD456……

u599……

ffcgu……

变量格式：iu 两次换行 jkey 两次换行 host 两次换行 token
多账号格式：不支持多账号

定时:
手动定时规则cron： 0                手动运行脚本

本脚本仅供学习交流，请在下载后的24小时内完全删除 请勿用于商业用途或非法目的，否则后果自负。
"""

import re
import os
import json
import time
import random
import requests
import threading
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlparse, parse_qs
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError, Timeout

def FtyxTOuJ(message, flush=False):
    print(f"{message}", flush=flush)

def process_account(account, i):
    max_retries = 1
    token = account.split("\n\n")[3]
    iu, jkeys,host = account.split("\n\n")[:3]
    jkey = jkeys
    checkDict = ["MzkwNTY1MzYxOQ=="]
    print(f"\n{'=' * 10}🔰开始执行账号{i}🔰{'=' * 10}\n", flush=True)
    print(f"{'=' * 10}📖开始阅读文章📖{'=' * 10}\n", flush=True)
    print(f"✅ 开始第1次阅读，使用环境变量jkey:\n{jkey}")
    url = f"http://{host}/dodoaa/mmaa"
    headers = {
        "Host": host,
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.20 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.2.50.2800(0x28000) NetType/WIFI Language/zh_CN",
        "X-Requested-With": "com.tencent.mm",
        "Referer": f"http://{host}/dodoaa/ttdd/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    for i in range(32):
        num = round(random.random(), 16)
        params = {
            "iu": f"{iu}",
            "t": f"{num:.16f}",
            "jkey": f"{jkey}",
        }
        #print(f"🔔 第{i+1}次阅读，使用jkey: {jkey}", flush=True)
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10).json()
            time.sleep(1)
            if {"success_msg", "jkey", "url"}.issubset(response):
                success = response["success_msg"]
                jkey = response['jkey']
                link = response["url"]
                sleep = random.randint(8, 25)
                delay = random.randint(120, 135)
                print(f"📖 第{i+1}次模拟阅读{sleep}秒", flush=True)
                print(f"✅ {success}\n", flush=True)
                #print(f"✅jkey获取成功: {jkey}", flush=True)
                if link:
                    su_match = re.search(r'第(\d+)篇', success)
                    su_number = (su_match.group(1) if su_match else "000")
                    biz_match = re.search(r'__biz=([^&]+)', link)
                    biz = biz_match.group(1) if biz_match else "❗未知来源文章"
                    print(f"✅ 第 {int(su_number) + 1} 篇文章获取成功---文章来源--- {biz}", flush=True)
                    print(f"📖 开始阅读: {link}", flush=True)
                    if biz == "❗未知来源文章" or biz in checkDict:
                        print(f"❗❗❗发现检测文章--- {biz}", flush=True)
                        print("❗明天再来吧！")
                        break
                        url = "http://www.pushplus.plus/send"
                        data = {
                            "token": token,
                            "title": "⚠️ 可乐检测文章！请在120s内完成阅读！",
                            "content": f'<a href="\n{link}\n"target="_blank">👉点击阅读8s以上并返回\n{link}\n',  
                            "template": "html"
                        }
                        for attempt in range(max_retries):
                            try:
                                response = requests.post(url, data=data).json()
                                if response.get("code") == 200:
                                    print("❗❗❗检测文章已推送至微信，请到微信完成阅读…\n🕗120s后继续运行…", flush=True)
                                    break
                                else:
                                    print(f"❗❗❗检测文章推送失败", flush=True)
                            except Exception as e:
                                print(f"❗❗❗推送请求异常：{str(e)}", flush=True)
                                response = None
                            if attempt < max_retries - 1 and (not response or response.get("code") != 200):
                                print("❗❗❗正在尝试重新推送...", flush=True)
                                time.sleep(3.5)
                            else:
                                print(f"❗❗❗推送失败原因：{response.get('msg')}", flush=True)
                                exit()
                        time.sleep(delay)
                    else:
                        time.sleep(sleep)
                else:
                    print("❗未找到link，程序终止", flush=True)
            elif "success_msg" in response:
                print(f"🔔 {response['success_msg']}", flush=True)
                break
            else:
                print(f"❗{response}", flush=True)
                break
        except requests.exceptions.Timeout:
            print("❗请求超时，请检查网络或稍后重试", flush=True)
        except Exception as e:
            print(f"❗请求失败: {str(e)}", flush=True)
            break


def notice():
    try:
        print(requests.get("https://gitee.com/gngkj/wxyd/raw/master/label.txt", timeout=5).text)
    except requests.RequestException as e:
        print(f"❗网络异常，获取通知时出错: {e}")


if __name__ == "__main__":
    notice()
    accounts = os.getenv("klyd")
    if accounts is None: print("❗未找到变量klyd", flush=True); exit()
    else:
        accounts_list = accounts.split("@")
        num_of_accounts = len(accounts_list)
        print(f"\n获取到 {num_of_accounts} 个账号", flush=True)
        for i, account in enumerate(accounts_list, start=1):
            process_account(account, i)

if __name__ == '__main__': pass