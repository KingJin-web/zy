"""
📖 小阅阅_V5.5   ♻20250813

✅ 新增：支持多渠道推送，请在青龙配置文件 config.sh 中添加必要的推送参数，并将变量中的token参数设置为000(详见下方参数说明)。(建议使用脚本自带pushplus推送，更稳定)。
✅ 完善检测文章。
✅ 修改bug，完善多渠道推送。

🔔阅读赚金币，金币可提现，每天1—2元，本脚本自动推送检测文章到微信，需要用户手动阅读过检测，过检测后脚本自动完成剩余任务，不需要下载app，在微信打开下方链接即可进入到活动页。(打开活动页时请无视微信的安全提示)

👉活动入口 微信打开：http://2121430.k4f1.sanming0.cn/yyiyase/f56fb7c54f55edd1b77d23b3577da92b?ukd=88     备用链接：https://tinyurl.com/5t3yhsfm     https://tinyurl.com/2tc96zpc    最新地址获取：https://tinyurl.com/27y64eve

👉建议将链接添加至微信收藏(微信_我_收藏_⊕_粘贴)，并添加到悬浮窗，方便进入活动主页。

⚠️进入后点击永久入口，保存二维码，当链接失效时扫码获取最新链接！

⚠️本脚本会通过(pushplus推送加或其他渠道)发送检测文章到用户手机过检测。为什么要读检测文章？因为活动方要通过个别检测文章阅读数的增加来判断用户阅读的有效性，所以必须真机阅读，脚本的模拟阅读不会增加阅读数。每个账号每天180篇中可能有3篇左右的检测文章。

⚠️用于阅读检测文章的微信号，每天运行脚本前务必从公众号(订阅号)阅读两篇文章，否则可能会触发微信风控，导致阅读无效过检测失败。禁止用真机+自动点击器阅读，否则同样触发微信风控，导致阅读无效。(当触发微信风控导致阅读无效后可能要几周或几个月解封，期间可以将检测文章推送至其他微信号过检测)

⚠️收到消息不弹窗？在pushplus回复“激活消息”将在48小时内连续5条消息以“客服消息”形式发送，此时可以收到微信弹窗提醒，否则将以“模板消息”形式发送消息，此时只有在微信主页或pushplus主页才能收到消息提醒。(详情点击“激活消息有什么用？”)。🔔当收到5条(客服消息)形式弹窗后重新发送“激活消息”可再次激活(客服消息)。

⚠️如微信没有接收到检测文章消息或消息延迟，可以把链接粘贴到微信的“文件传输助手”或“收藏”再点击阅读!

❗❗❗重要提示：本脚本只限新用户通过上方链接绑定指定id使用，或老用户上级id尾号为4981，其他非受邀用户均不可使用。

❗❗❗期间要时常用真机访问活动主页并阅读，同时每天任务不建议跑满，避免被活动方查出异常封号！

参数：
1、用“pushplus推送加”接收检测文章，微信公众号关注“pushplus推送加”，点击pushplus进入到官网首页注册实名并激活消息，获取您的token口令填写到变量。
2、打开抓包软件并用小阅阅读文章，抓出Cookie里的ysmuid和请求体里的unionid，以及请求头中的User-Agent参数。
3、如果您使用其他平台作为推送渠道请将token参数设置为000，例：5a68xxx&oZdBpxxx&000。如果使用pushplus推送正常填写token参数即可。

变量名：xyy
变量值：5a68xxxxxxx&oZdBpxxxxxxx&ff2cdxxxxxxx

变量格式：ysmuid & unionid & token
多账号格式：ysmuid & unionid & token @ ysmuid & unionid & token

多账号：账号1@账号2@账号3
例：5a68xxx&oZdBpxxx&ff2cdxxx@5a68xxx&oZdBpxxx&ff2cdxxx

变量名: UA  (为请求头中的User-Agent参数)
变量值：Mozilla/5.0 iPhonexxxxxxx

变量名：xyytx
变量值：1
自动提现 1开启 0关闭 (不配置变量默认不自动提现，开启后满5000金币自动提现)

定时:
自动定时规则cron： 0 7-23/3 * * *   (每天7-23点每3小时一次)，期间注意接收微信通知，阅读检测文章
手动定时规则cron： 0                手动运行脚本，期间注意接收微信通知，阅读检测文章

更多脚本关注仓库：https://wwgz.lanzoue.com/b0ec064he   密码：2580

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

# 实时日志
def log_message(message, flush=False):
    print(f"{message}", flush=flush)

# 主程序
def process_account(account, i):
    max_retries = 1
    uas = account.split("&")[0][-3:]
    token = account.split("&")[2]
    ysmuid, unionid = account.split("&")[:2]
    # 获取域名
    current_url = requests.get("https://www.filesmej.cn/waidomain.php", timeout=5).json()["data"]["luodi"]
    session = requests.Session()
    headers = {
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": f"{UA} {uas}",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/tpg,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "X-Requested-With": "com.tencent.mm",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": f"ysmuid={ysmuid}"
    }
    for _ in range(11):
        try:
            parsed = urlparse(current_url)
            headers["Host"] = parsed.netloc
            response = session.get(current_url, headers=headers, allow_redirects=False, timeout=10)
            if response.status_code in (301, 302, 303, 307, 308):
                current_url = urljoin(current_url, response.headers.get("Location", ""))
            else:
                break
        except (requests.RequestException, requests.exceptions.InvalidURL) as e:
            print(f"❗重定向错误: {e}", flush=True)
            break
        try:
            parsed_domain = urlparse(current_url).netloc.lstrip("www.")
        except Exception as e:
            print(f"❗域名获取失败: {e}", flush=True)
    # 上级id
    codeid = lambda: (
        (match.group(1) if (match := re.compile(r'codeid\s*=\s*"(\d+)"').search(
            requests.get(
                f"http://{parsed_domain}/?inviteid=0",
                headers = {
                    "Host": f"{parsed_domain}",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": f"{UA} {uas}",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/tpg,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "X-Requested-With": "com.tencent.mm",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Cookie": f"ysmuid={ysmuid}"
                },
                timeout=10
            ).text
        )) else print(f"❗警告：未找到codeid \n❗检查活动页面是否正常，切勿反复运行", flush=True))
        if not any([
            print(f"❗网络请求失败: {e}", flush=True) if isinstance(e, requests.RequestException) else
            print(f"❗正则错误: {e}", flush=True) if isinstance(e, re.error) else
            print(f"❗未知错误: {e}", flush=True) for e in [Exception][:0]
        ]) else None
    )
    codeid = codeid()
    # 用户id
    extract_dynamic_id = lambda: (
        (match.group(1) if (match := re.compile(r'我的id:(\d+)').search(
            requests.get(
                f"http://{parsed_domain}/?inviteid=0",
                headers = {
                    "Host": f"{parsed_domain}",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": f"{UA} {uas}",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/tpg,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "X-Requested-With": "com.tencent.mm",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Cookie": f"ysmuid={ysmuid}"
                },
                timeout=10
            ).text
        )) else print("❗警告：未找到ID", flush=True))
        if not any([
            print(f"❗网络请求失败: {e}", flush=True) if isinstance(e, requests.RequestException) else
            print(f"❗正则错误: {e}", flush=True) if isinstance(e, re.error) else
            print(f"❗未知错误: {e}", flush=True) for e in [Exception][:0]
        ]) else None
    )
    # 开始阅读
    print(f"\n{'=' * 10}🔰开始执行账号{i}🔰{'=' * 10}\n", flush=True)
    exit(print("❗您不是受邀用户，程序终止", flush=True)) if not codeid or int(codeid) not in {693874981} else print("👌 账号验证成功", flush=True)
    time.sleep(1)
    url = f"http://{parsed_domain}/yunonline/v1/gold"
    headers = {
        "Host": f"{parsed_domain}",
        "Connection": "keep-alive",
        "User-Agent": f"{UA} {uas}",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"http://{parsed_domain}/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": f"ysmuid={ysmuid}; ejectCode=1"
    }
    params = {
        "unionid": f"{unionid}",
        "time": int(time.time() * 1000)
    }
    response = requests.get(url, headers=headers, params=params).json()
    if response["errcode"] == 0:
        day_gold = response["data"]["day_gold"]
        day_read = response["data"]["day_read"]
        last_gold = response["data"]["last_gold"]
        remain_read = response["data"]["remain_read"]
        print(f"🙍 ID:{extract_dynamic_id()}", flush=True)
        print(f"💰 当前金币:{last_gold}\n📖 今日已读:{day_read}  剩余:{remain_read}", flush=True)
        print("🔔 自动提现已关闭" if money_Withdrawal == 0 else "🔔 自动提现已开启", flush=True)
        print(f"{'=' * 10}📖开始阅读文章📖{'=' * 10}\n", flush=True)
        for i in range(33):
            current_timestamp = int(time.time() * 1000)
            checkDict = [
                "MzkzMTYyMDU0OQ==",
                "Mzk0NDcxMTk2MQ==",
                "MzkzNTYxOTgyMA==",
                "MzkzNDYxODY5OA==",
                "MzkwNzYwNDYyMQ==",
                "MzkyNjY0MTExOA==",
                "MzkwMTYwNzcwMw==",
                "Mzg4NTcwODE1NA==",
                "MzkyMjYxNzQ2NA==",
                "Mzk4ODQzNjU1OQ==",
                "MzkyMTc0MDU5Nw==",
                "Mzk5MDc1MDQzOQ==",
                "Mzk4ODQzNzU3NA==",
            ]
            time.sleep(1)
            url = f"http://{parsed_domain}/wtmpdomain2"
            headers = {
                "Host": f"{parsed_domain}",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "User-Agent": f"{UA} {uas}",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": f"http://{parsed_domain}",
                "Referer": f"http://{parsed_domain}/?inviteid=0",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": f"ysmuid={ysmuid};ejectCode=1"
            }
            data = {
                "unionid": unionid
            }
            for retry in range(max_retries):
                try:
                    response = requests.post(url, headers=headers, data=data, timeout=7).json()
                    break
                except (ConnectionError, Timeout):
                    if retry < max_retries - 1:
                        time.sleep(2.5)
                        continue
                    else:
                        print("❗网络异常退出", flush=True)
                        break
                except Exception as e:
                    print(e, flush=True)
                    if retry < max_retries - 1:
                        print("❗状态1异常，尝试重新发送请求...", flush=True)
                        time.sleep(2.5)
                        continue
                    else:
                        print("❗达到最大重试次数，退出", flush=True)
                        break
            if response["errcode"] == 0:
                time.sleep(1)
                parsed_url = response['data']['domain']
                url_parts = urlparse(parsed_url)
                gt = parse_qs(url_parts.query).get('gt', [''])[0]
                new_url = f"{url_parts.scheme}://{url_parts.netloc}/sdaxeryy?gt={gt}&time={current_timestamp}&psgn=168&vs=120"
                headers = {
                    "Host": f"{url_parts.netloc}",
                    "Connection": "keep-alive",
                    "User-Agent": f"{UA} {uas}",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"{url_parts.scheme}://{url_parts.netloc}/xsysy.html?{url_parts.query}",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept-Encoding": "gzip, deflate"
                }
                for retry in range(max_retries):
                    try:
                        response = requests.get(new_url, headers=headers, timeout=7).json()
                        break
                    except (ConnectionError, Timeout):
                        if retry < max_retries - 1:
                            time.sleep(2.5)
                            continue
                        else:
                            print("❗网络异常退出", flush=True)
                            break
                    except Exception as e:
                        print(e, flush=True)
                        if retry < max_retries - 1:
                            print("❗状态2异常，尝试重新发送请求...", flush=True)
                            time.sleep(2.5)
                            continue
                        else:
                            print("❗达到最大重试次数，退出", flush=True)
                            break
                if response["errcode"] == 0:
                    link = response['data']['link']
                    if link:
                        biz_match = re.search(r'__biz=([^&]+)', link)
                        biz = biz_match.group(1) if biz_match else "❗未知来源文章"
                        sleep = random.randint(8, 25)
                        delay = random.randint(120, 135)
                        print(f"✅ 第{int(day_read)+ i + 1}篇文章获取成功---文章来源--- {biz}", flush=True)
                        print(f"📖 开始阅读: {link}", flush=True)
                        if biz == "❗未知来源文章" or biz in checkDict:
                            print(f"❗❗❗发现检测文章--- {biz}", flush=True)
                            if token == "000":
                                config_ret = os.system("source /ql/config/config.sh")
                                if config_ret != 0:
                                    print("⚠️ 错误：加载配置文件失败！")
                                else:
                                    notify_cmd = f'notify "⚠️ 小阅阅检测文章！请在120s内完成阅读！" \'<a href="\n{link}\n"target="_blank">👉点击阅读8s以上并返回\n{link}\n\''
                                    notify_ret = os.system(notify_cmd)
                                    if notify_ret == 0:
                                        print("❗❗❗检测文章已推送至微信，请到微信完成阅读…\n🕗120s后继续运行…", flush=True)
                                    else:
                                        print(f"❌ 通知发送失败，错误码: {notify_ret}")
                            else:
                                url = "http://www.pushplus.plus/send"
                                data = {
                                    "token": token,
                                    "title": "⚠️ 小阅阅检测文章！请在120s内完成阅读！",
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
                            url = f"{url_parts.scheme}://{url_parts.netloc}/jinbicp?gt={gt}&time={sleep}&timestamp={current_timestamp}"
                            headers = {
                                "Host": f"{url_parts.netloc}",
                                "Connection": "keep-alive",
                                "User-Agent": f"{UA} {uas}",
                                "Accept": "application/json, text/javascript, */*; q=0.01",
                                "X-Requested-With": "XMLHttpRequest",
                                "Referer": f"{url_parts.scheme}://{url_parts.netloc}/xsysy.html?{url_parts.query}",
                                "Accept-Encoding": "gzip, deflate",
                                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
                            }
                            for retry in range(max_retries):
                                try:
                                    response = requests.get(url, headers=headers, timeout=7).json()
                                    break
                                except (ConnectionError, Timeout):
                                    if retry < max_retries - 1:
                                        time.sleep(2.5)
                                        continue
                                    else:
                                        print("❗网络异常退出", flush=True)
                                        break
                                except Exception as e:
                                    print('❗提交状态异常', flush=True)
                                    print(e)
                            if response["errcode"] == 0:
                                gold = response['data']['gold']
                                print(f"✅ 第{i + 1}次阅读检测文章成功---获得金币:💰{gold}💰", flush=True)
                                print(f"{'-' * 60}\n")
                            else:
                                print(f"❗❗❗过检测失败\n{response}", flush=True)
                                break
                        else:
                            time.sleep(sleep)
                            url = f"{url_parts.scheme}://{url_parts.netloc}/jinbicp?gt={gt}&time={sleep}&timestamp={current_timestamp}"
                            headers = {
                                "Host": f"{url_parts.netloc}",
                                "Connection": "keep-alive",
                                "User-Agent": f"{UA} {uas}",
                                "Accept": "application/json, text/javascript, */*; q=0.01",
                                "X-Requested-With": "XMLHttpRequest",
                                "Referer": f"{url_parts.scheme}://{url_parts.netloc}/xsysy.html?{url_parts.query}",
                                "Accept-Encoding": "gzip, deflate",
                                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
                            }
                            for retry in range(max_retries):
                                try:
                                    response = requests.get(url, headers=headers, timeout=7).json()
                                    break
                                except (ConnectionError, Timeout):
                                    if retry < max_retries - 1:
                                        time.sleep(2.5)
                                        continue
                                    else:
                                        print("❗网络异常退出", flush=True)
                                        break
                                except Exception as e:
                                    print("❗提交状态异常", flush=True)
                                    print(e)
                            if response["errcode"] == 0:
                                gold = response["data"]["gold"]
                                print(f"📖 本次模拟阅读{sleep}秒", flush=True)
                                print(f"✅ 第{i + 1}次阅读成功---获得金币:💰{gold}💰", flush=True)
                                print(f"{'-' * 60}\n")
                            else:
                                print(f"❗阅读文章失败，请尝试重新运行\n{response}", flush=True)
                                break
                    else:
                        print("❗未找到link")
                elif response["errcode"] == 405:
                    print(f"❗{response}", flush=True)
                    print(f"❗请尝试重新运行", flush=True)
                    break
                elif response["errcode"] == 407:
                    if '<br />1、' in response["msg"]:
                        first_part = response["msg"].split('<br />1、', 1)[0]
                        first_rule = response["msg"].split('<br />1、', 1)[1].split('<br />')[0].strip()
                        print(f"❗{first_part}", flush=True)
                        print(f"❗{first_rule}", flush=True)
                        break
                    else:
                        print(f"❗{response['msg']}", flush=True)
                        break
                else:
                    print(f"⚠️ 未知错误 {response['errcode']}: {response}", flush=True)
                    break
            else:
                print(f"❗获取文章失败{response}", flush=True)
                break
        # 提现
        if money_Withdrawal == 1:
            if int(last_gold) > 5000:
                print(f"{'=' * 12}💰开始提现💰{'=' * 12}\n", flush=True)
                url = f"http://{parsed_domain}"
                headers = {
                    "Host": f"{parsed_domain}",
                    "Connection": "keep-alive",
                    "Cache-Control": "max-age=0",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": f"{UA} {uas}",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/tpg,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "X-Requested-With": "com.tencent.mm",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Cookie": f"ysmuid={ysmuid}"
                }
                response = requests.get(url, headers=headers).text
                res1 = re.sub('\s', '', response)
                exchangeUrl = re.findall('"target="_blank"href="(.*?)">提现<', res1)
                eurl = exchangeUrl[0]
                query_dict = parse_qs(urlparse(exchangeUrl[0]).query)
                unionids = query_dict.get('unionid', [''])[0]
                request_id = query_dict.get('request_id', [''])[0]
                b = urlparse(eurl)
                host=b.netloc
                url = f"http://{host}/yunonline/v1/gold"
                headers = {
                    "Host": f"{host}",
                    "Connection": "keep-alive",
                    "User-Agent": f"{UA} {uas}",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"{eurl}",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Cookie": f"ysmuid={ysmuid}; ejectCode=1"
                }
                params = {
                    "unionid": f"{unionid}",
                    "time": int(time.time() * 1000)
                }
                response = requests.get(url, headers=headers, params=params).json()
                if response["errcode"] == 0:
                    last_gold = response["data"]["last_gold"]
                    gold = int(int(last_gold) / 1000) * 1000
                url = f"http://{host}/yunonline/v1/user_gold"
                headers = {
                    "Host": f"{host}",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": f"{UA} {uas}",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Origin": f"http://{host}",
                    "Referer": f"{eurl}",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Cookie": f"ysmuid={ysmuid}"
                }
                data = {
                    "unionid": unionids,
                    "request_id": request_id,
                    "gold": gold,
                }
                response = requests.post(url, headers=headers, data=data).json()
                print(f"💰 当前可提现:{gold}", flush=True)
                url = f"http://{host}/yunonline/v1/withdraw"
                headers = {
                    "Host": f"{host}",
                    "Connection": "keep-alive",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": f"{UA} {uas}",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Origin": f"http://{host}",
                    "Referer": f"{eurl}",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Cookie": f"ysmuid={ysmuid}"
                }
                data = {
                    "unionid": unionids,
                    "signid": request_id,
                    "ua": "2",
                    "ptype": "0",
                    "paccount": "",
                    "pname": ""
                }
                response = requests.post(url, headers=headers, data=data)
                data = response.json()
                if data["errcode"] == 0:
                    print("💰 恭喜您，提现成功！\n", flush=True)
                else:
                    print(f"❗{response}", flush=True)
            else:
                print(f"{'=' * 17}{'=' * 17}", flush=True)
                print("🔔 金币不足5000，不执行提现\n", flush=True)
        elif money_Withdrawal == 0:
            print(f"{'=' * 17}{'=' * 17}", flush=True)
            print(f"🔔 自动提现已关闭，不执行提现\n", flush=True)
    else:
        print(f"❗获取用户信息失败", flush=True)
        exit()


def notice():
    try:
        print(requests.get("https://gitee.com/gngkj/wxyd/raw/master/label.txt", timeout=5).text)
    except requests.RequestException as e:
        print(f"❗网络异常，获取通知时出错: {e}")


if __name__ == "__main__":
    notice()
    accounts = os.getenv("xyy")
    money_Withdrawal = 0 if os.getenv("xyytx", "0") == "0" else 1
    UA = os.getenv("UA"); None if UA is not None else (print("❗未找到变量UA", flush=True), exit())
    if accounts is None: print("❗未找到变量xyy", flush=True); exit()
    else:
        accounts_list = accounts.split("@")
        num_of_accounts = len(accounts_list)
        print(f"\n获取到 {num_of_accounts} 个账号", flush=True)
        for i, account in enumerate(accounts_list, start=1):
            process_account(account, i)
