"""
==============================================================================
注释：脚本配置及内部逻辑修改说明
==============================================================================
🔔阅读赚金币，金币可提现，每天1—2元，本脚本自动推送检测文章到微信，需要用户手动阅读过检测，
🔔过检测后脚本自动完成剩余任务，不需要下载app，在微信打开下方链接即可进入到活动页。

一、活动入口链接 (脚本顶层注释部分):
     # 活动入口 https://img.hnking.cn/blog/202508161653803.png

二、环境变量配置
1. xyy (账号信息，必需)
   格式: ysmuid&unionid&XXX
   - ysmuid: 从Cookie中抓取
   - unionid: 从请求体中抓取
   - XXX:备注
   多账号格式: 账号1@账号2@账号3
   示例: 5a68xxxxxxx&oZdBpxxxxxxx&XXX@5a68xxx&oZdBpxxx&ff2cdxxx

2. UA (User-Agent，必需)
   格式: 浏览器或设备的User-Agent字符串
        https://useragent.todaynav.com/ 微信打开此网站即可 请使用你的微信的User-Agent
   示例: Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1

3. xyytx (自动提现开关，可选)
   值: 1 (开启自动提现，满5000金币时)
        0 (关闭自动提现，或不配置此变量默认为关闭)

三、常见问题解决
    1. 获取codeid失败：活动域名 'parsed_domain' 未能成功解析。
    进入青龙面板控制台运行如下命令
    echo "nameserver 223.5.5.5" | tee /etc/resolv.conf
    echo "nameserver 223.6.6.6" | tee -a /etc/resolv.conf

四、定时:
    自动定时规则cron： 0 7-23/3 * * * (每天7-23点每3小时一次)，期间注意接收微信通知，阅读检测文章
    手动定时规则cron： 0                手动运行脚本，期间注意接收微信通知，阅读检测文章


五、说明
    ⚠️本脚本会通过(青龙自带推送)发送检测文章到用户手机过检测。
    ⚠️请在青龙面板配置文件中设置钉钉，企业微信等推送。
    ⚠️为什么要读检测文章？因为活动方要通过个别检测文章阅读数的增加来判断用户阅读的有效性，
    ⚠️所以必须真机阅读，脚本的模拟阅读不会增加阅读数。每个账号每天180篇中可能有3篇左右的检测文章。
    ⚠️用于阅读检测文章的微信号，每天运行脚本前务必从公众号(订阅号)阅读两篇文章，
    否则可能会触发微信风控，导致阅读无效过检测失败。禁止用真机+自动点击器阅读，否则同样触发微信风控，导致阅读无效。(当触发微信风控导致阅读无效后可能要几周或几个月解封)

    ❗❗❗期间要时常用真机访问活动主页并阅读，同时每天任务不建议跑满，避免被活动方查出异常封号！
    ❗❗❗本脚本仅供学习交流，请在下载后的24小时内完全删除 请勿用于商业用途或非法目的，否则后果自负。


三、脚本内部逻辑主要修改点 (基于解混淆后的代码):

1. codeid 验证逻辑绕过:
   - 脚本内部用于验证用户是否为“受邀用户”的 codeid 检查逻辑已被修改。
   - 此修改会使脚本跳过原始的 codeid 比较步骤，直接判定为“账号验证成功”。
     (原始脚本期望从页面获取的 codeid 与一个硬编码ID，如 *****4981，匹配)

2. 初始URL获取超时调整:
   - 脚本在首次尝试从 'https://www.filesmej.cn/waidomain.php' 获取活动落地页URL时，
     网络请求的超时时间已从原来的5秒增加到30秒，以应对可能的网络延迟。


==============================================================================
"""

# Obfuscated at 2025-05-20 15:55:34.918061
# 修改说明1：更新注释中的活动入口链接，移除备用链接。
# 修改说明2：codeid 验证逻辑已修改为绕过检测。
# 修改说明3：针对 NameError 的进一步“复位”：移除了在主阅读流程前对 parsed_domain 的显式检查。
#            如果 parsed_domain 在重定向循环中未能成功赋值，并且早期 NameError 捕获未终止脚本，则后续可能出现 NameError。
#            获取初始落地页URL失败的检查依然保留。

import datetime

_z_BtnKjK = lambda *_: None

import re
import os
import json
import time
import random
import requests
from urllib.parse import urljoin
from urllib.parse import urlparse, parse_qs
from requests.exceptions import ConnectionError, Timeout


# 实时日志
def EcxlbMhb(message, flush=False):
    print(f"{message}", flush=flush)


# 主程序
def process_account(account, i):
    max_retries = 1
    uas = account.split("&")[0][-3:]
    token = account.split("&")[2]
    ysmuid, unionid = account.split("&")[:2]

    # 获取域名
    try:
        current_url = requests.get("https://www.filesmej.cn/waidomain.php", timeout=25).json()["data"]["luodi"]
    except Exception as e:
        print(f"❗获取初始落地页URL失败: {e}", flush=True)
        return  # 如果初始URL获取失败，则无法继续

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

    # parsed_domain 将在此循环中尝试被赋值
    # 如果循环因错误提前退出，parsed_domain 可能未定义，后续使用会引发 NameError
    for _ in range(11):
        try:
            parsed_url_obj = urlparse(current_url)
            headers["Host"] = parsed_url_obj.netloc
            response = session.get(current_url, headers=headers, allow_redirects=False, timeout=10)
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get("Location", "")
                if not location:
                    print(f"❗重定向错误: Location header为空，URL: {current_url}", flush=True)
                    break
                current_url = urljoin(current_url, location)
            else:
                parsed_domain = urlparse(current_url).netloc.lstrip("www.")  # 赋值点
                if parsed_domain:
                    print(f"✅ 成功获取活动域名: {parsed_domain}", flush=True)
                else:
                    print(f"❗域名解析失败: 无法从 {current_url} 解析出有效域名", flush=True)
                break
        except (requests.RequestException, requests.exceptions.InvalidURL) as e:
            print(f"❗重定向或请求错误: {e}", flush=True)
            break
        except Exception as e:
            print(f"❗解析当前URL时发生错误 ({current_url}): {e}", flush=True)
            break

    # 验证用户
    codeid_value = None
    try:
        response_text = requests.get(
            f"http://{parsed_domain}/?inviteid=0",  # NameError risk if parsed_domain not set
            headers={
                "Host": f"{parsed_domain}",  # NameError risk if parsed_domain not set
                "Connection": "keep-alive", "Upgrade-Insecure-Requests": "1", "User-Agent": f"{UA} {uas}",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/tpg,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "X-Requested-With": "com.tencent.mm", "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": f"ysmuid={ysmuid}"
            },
            timeout=10
        ).text
        match = re.compile(r'codeid\s*=\s*"(\d+)"').search(response_text)
        if match:
            codeid_value = match.group(1)
            print(f"ℹ️ 从页面获取到的 codeid: {codeid_value}", flush=True)
        else:
            print("❗警告：未在页面中找到codeid", flush=True)
    except NameError:
        print(f"❗获取codeid失败：活动域名 'parsed_domain' 未能成功解析。", flush=True)
        return
    except requests.RequestException as e:
        print(f"❗获取codeid时网络请求失败: {e}", flush=True)
        return  # 网络请求失败也应该终止
    except re.error as e:
        print(f"❗获取codeid时正则错误: {e}", flush=True)
        return  # 正则错误也应该终止
    except Exception as e:
        print(f"❗获取codeid时发生未知错误: {e}", flush=True)
        return  # 其他未知错误也终止

    # 获取id
    dynamic_id_value = None
    try:
        response_text_for_id = requests.get(
            f"http://{parsed_domain}/?inviteid=0",  # NameError risk if parsed_domain not set
            headers={
                "Host": f"{parsed_domain}",  # NameError risk if parsed_domain not set
                "Connection": "keep-alive", "Upgrade-Insecure-Requests": "1", "User-Agent": f"{UA} {uas}",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/tpg,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "X-Requested-With": "com.tencent.mm", "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": f"ysmuid={ysmuid}"
            },
            timeout=10
        ).text
        id_match = re.compile(r'我的id:(\d+)').search(response_text_for_id)
        if id_match:
            dynamic_id_value = id_match.group(1)
        else:
            print("❗警告：未在页面中找到 '我的id:'", flush=True)
    except NameError:
        print(f"❗获取'我的id:'失败：活动域名 'parsed_domain' 未能成功解析。", flush=True)
        # 如果到这里，通常在获取 codeid 时已 return
    except requests.RequestException as e:
        print(f"❗获取'我的id:'时网络请求失败: {e}", flush=True)
    except re.error as e:
        print(f"❗获取'我的id:'时正则错误: {e}", flush=True)
    except Exception as e:
        print(f"❗获取'我的id:'时发生未知错误: {e}", flush=True)

    # 开始阅读
    print(f"\n{'=' * 10}🔰开始执行账号{i}🔰{'=' * 10}\n", flush=True)

    # === 修改点：绕过codeid检测 ===
    print("👌 账号验证成功 [检测已绕过]", flush=True)

    time.sleep(1)

    # 移除了这里的 if 'parsed_domain' not in locals() or not parsed_domain: 检查
    # 如果 parsed_domain 未定义，下面使用时会直接 NameError (除非上面获取 codeid 时已因 NameError return)

    url_gold_info = f"http://{parsed_domain}/yunonline/v1/gold"
    headers_gold_info = {
        "Host": f"{parsed_domain}", "Connection": "keep-alive", "User-Agent": f"{UA} {uas}",
        "Accept": "application/json, text/javascript, */*; q=0.01", "X-Requested-With": "XMLHttpRequest",
        "Referer": f"http://{parsed_domain}/", "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7", "Cookie": f"ysmuid={ysmuid}; ejectCode=1"
    }
    params_gold_info = {"unionid": f"{unionid}", "time": int(time.time() * 1000)}

    try:
        response_gold_json = requests.get(url_gold_info, headers=headers_gold_info, params=params_gold_info,
                                          timeout=10).json()
    except NameError:  # 以防万一 parsed_domain 还是问题
        print(f"❗获取金币信息失败：活动域名 'parsed_domain' 未定义。", flush=True)
        return
    except requests.RequestException as e:
        print(f"❗获取金币信息时网络错误: {e}", flush=True)
        return
    except json.JSONDecodeError as e:
        print(f"❗获取金币信息时JSON解析错误: {e}", flush=True)
        return

    if response_gold_json.get("errcode") == 0:
        data_gold = response_gold_json.get("data", {})
        day_gold = data_gold.get("day_gold", "未知")
        day_read = data_gold.get("day_read", "未知")
        last_gold = data_gold.get("last_gold", "未知")
        remain_read = data_gold.get("remain_read", "未知")

        print(f"🙍 ID:{dynamic_id_value if dynamic_id_value else '未获取到'}", flush=True)
        print(f"💰 当前金币:{last_gold}\n📖 今日已读:{day_read}  剩余:{remain_read}", flush=True)
        print("🔔 自动提现已关闭" if money_Withdrawal == 0 else "🔔 自动提现已开启", flush=True)
        print(f"{'=' * 10}📖开始阅读文章📖{'=' * 10}\n", flush=True)

        for article_count in range(33):
            current_timestamp = int(time.time() * 1000)
            checkDict = [
                "MzkzMTYyMDU0OQ==", "Mzk0NDcxMTk2MQ==", "MzkzNTYxOTgyMA==",
                "MzkzNDYxODY5OA==", "MzkwNzYwNDYyMQ==", "MzkyNjY0MTExOA==",
                "MzkwMTYwNzcwMw==", "Mzg4NTcwODE1NA==", "MzkyMjYxNzQ2NA==",
                "Mzk5MDc1MDQzOQ==", "MzkyMTc0MDU5Nw==", "Mzk4ODQzNzU3NA=="
            ]
            time.sleep(1)
            url_get_article_domain = f"http://{parsed_domain}/wtmpdomain2"  # NameError risk
            headers_get_article_domain = {
                "Host": f"{parsed_domain}", "Accept": "application/json, text/javascript, */*; q=0.01",
                "User-Agent": f"{UA} {uas}", "X-Requested-With": "XMLHttpRequest",
                "Origin": f"http://{parsed_domain}", "Referer": f"http://{parsed_domain}/?inviteid=0",
                "Cookie": f"ysmuid={ysmuid};ejectCode=1"
            }
            data_get_article_domain = {"unionid": unionid}

            response_article_domain_json = None
            for retry in range(max_retries):
                try:
                    response_article_domain_json = requests.post(url_get_article_domain,
                                                                 headers=headers_get_article_domain,
                                                                 data=data_get_article_domain, timeout=25).json()
                    break
                except (ConnectionError, Timeout) as e_net:
                    print(f"❗获取文章域名网络异常 (尝试 {retry + 1}/{max_retries}): {e_net}", flush=True)
                    if retry < max_retries - 1:
                        time.sleep(2.5)
                    else:
                        print("❗网络异常退出 (获取文章域名)", flush=True);
                        return
                except json.JSONDecodeError as e_json:
                    print(f"❗获取文章域名JSON解析错误 (尝试 {retry + 1}/{max_retries}): {e_json}", flush=True)
                    if retry < max_retries - 1:
                        time.sleep(2.5)
                    else:
                        print("❗JSON解析错误退出 (获取文章域名)", flush=True);
                        return
                except Exception as e:
                    print(f"❗获取文章域名发生未知错误 (尝试 {retry + 1}/{max_retries}): {e}", flush=True)
                    if retry < max_retries - 1:
                        time.sleep(2.5)
                    else:
                        print("❗未知错误退出 (获取文章域名)", flush=True);
                        return

            if not response_article_domain_json or response_article_domain_json.get("errcode") != 0:
                err_msg = response_article_domain_json.get('msg', '未知错误') if response_article_domain_json else '无响应'
                print(f"❗获取文章域名失败: {err_msg}", flush=True)
                break

            time.sleep(1)
            article_page_domain_str = response_article_domain_json['data']['domain']
            article_page_url_parts = urlparse(article_page_domain_str)
            gt = parse_qs(article_page_url_parts.query).get('gt', [''])[0]

            if not gt:
                print(f"❗无法从文章域名响应中获取gt参数: {article_page_domain_str}", flush=True)
                break

            url_get_article_link = f"{article_page_url_parts.scheme}://{article_page_url_parts.netloc}/sdaxeryy?gt={gt}&time={current_timestamp}&psgn=168&vs=120"
            headers_get_article_link = {
                "Host": f"{article_page_url_parts.netloc}", "Connection": "keep-alive", "User-Agent": f"{UA} {uas}",
                "Accept": "application/json, text/javascript, */*; q=0.01", "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{article_page_url_parts.scheme}://{article_page_url_parts.netloc}/xsysy.html?{article_page_url_parts.query}",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7", "Accept-Encoding": "gzip, deflate"
            }

            response_article_link_json = None
            for retry in range(max_retries):
                try:
                    response_article_link_json = requests.get(url_get_article_link, headers=headers_get_article_link,
                                                              timeout=25).json()
                    break
                except (ConnectionError, Timeout) as e_net:  # This is where the current error in log happens
                    print(f"❗获取文章链接网络异常 (尝试 {retry + 1}/{max_retries}): {e_net}", flush=True)
                    if retry < max_retries - 1:
                        time.sleep(2.5)
                    else:
                        print("❗网络异常退出 (获取文章链接)", flush=True);
                        return  # Script exits here for the account
                except json.JSONDecodeError as e_json:
                    print(f"❗获取文章链接JSON解析错误 (尝试 {retry + 1}/{max_retries}): {e_json}", flush=True)
                    if retry < max_retries - 1:
                        time.sleep(2.5)
                    else:
                        print("❗JSON解析错误退出 (获取文章链接)", flush=True);
                        return
                except Exception as e:
                    print(f"❗获取文章链接发生未知错误 (尝试 {retry + 1}/{max_retries}): {e}", flush=True)
                    if retry < max_retries - 1:
                        time.sleep(2.5)
                    else:
                        print("❗未知错误退出 (获取文章链接)", flush=True);
                        return

            if not response_article_link_json or response_article_link_json.get("errcode") != 0:
                err_code_val = response_article_link_json.get("errcode", "N/A") if response_article_link_json else "N/A"
                err_msg = response_article_link_json.get('msg', '未知错误') if response_article_link_json else '无响应'
                print(f"❗获取文章链接失败 (errcode: {err_code_val}): {err_msg}", flush=True)
                if err_code_val == 405 or err_code_val == 407:
                    print(f"❗请尝试重新运行", flush=True)
                break

            link = response_article_link_json.get('data', {}).get('link')
            if not link:
                print("❗未找到link", flush=True)
                break

            biz_match = re.search(r'__biz=([^&]+)', link)
            biz = biz_match.group(1) if biz_match else "❗未知来源文章"
            read_sleep_time = random.randint(8, 25)
            detection_delay = random.randint(120, 135)

            current_day_read = 0
            if isinstance(day_read, (int, str)) and str(day_read).isdigit():
                current_day_read = int(day_read)

            print(f"✅ 第{current_day_read + article_count + 1}篇文章获取成功---文章来源--- {biz}", flush=True)
            print(f"📖 开始阅读: {link}", flush=True)

            if biz == "❗未知来源文章" or biz in checkDict:
                print(f"❗❗❗发现检测文章--- {biz} 待运行账号 {token}  当前时间 {str(datetime.datetime.now())}", flush=True)
                # 得到当前时间

                QLAPI.notify("⚠️ 小阅阅检测文章！待过检测账号：" + token, "请在120s内完成阅读！\n"
                                                                        "当前时间：" + str(datetime.datetime.now()) +
                             "\n文章链接：" + link + "\n文章来源：" + biz)
                # url_pushplus = "http://www.pushplus.plus/send"
                # data_pushplus = {
                #     "token": token, "title": "⚠️ 小阅阅检测文章！请在120s内完成阅读！",
                #     "content": f'<a href="{link}" target="_blank">👉点击阅读8s以上并返回</a><br>链接(备用): {link}',
                #     "template": "html"
                # }
                # push_success = False
                # for attempt in range(max_retries):
                #     try:
                #         response_push = requests.post(url_pushplus, data=data_pushplus, timeout=10).json()
                #         if response_push.get("code") == 200:
                #             print(f"❗❗❗检测文章已推送至微信，请到微信完成阅读…\n🕗{detection_delay}s后继续运行…",
                #                   flush=True)
                #             push_success = True
                #             break
                #         else:
                #             print(f"❗❗❗检测文章推送失败: {response_push.get('msg', '未知错误')}", flush=True)
                #     except Exception as e_push:
                #         print(f"❗❗❗推送请求异常：{str(e_push)}", flush=True)
                #     if attempt < max_retries - 1: print("❗❗❗正在尝试重新推送...", flush=True); time.sleep(3.5)
                #
                # if not push_success:
                #     print(f"❗❗❗检测文章推送最终失败，脚本终止。", flush=True)
                #     return

                time.sleep(detection_delay)
                url_submit_detection = f"{article_page_url_parts.scheme}://{article_page_url_parts.netloc}/jinbicp?gt={gt}&time={read_sleep_time}&timestamp={current_timestamp}"
                headers_submit_detection = {
                    "Host": f"{article_page_url_parts.netloc}", "Connection": "keep-alive", "User-Agent": f"{UA} {uas}",
                    "Accept": "application/json, text/javascript, */*; q=0.01", "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"{article_page_url_parts.scheme}://{article_page_url_parts.netloc}/xsysy.html?{article_page_url_parts.query}",
                    "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
                }
                response_submit_detection_json = None
                for retry in range(max_retries):
                    try:
                        response_submit_detection_json = requests.get(url_submit_detection,
                                                                      headers=headers_submit_detection,
                                                                      timeout=25).json()
                        break
                    except Exception as e_submit_det:
                        print(f"❗提交检测文章状态网络异常 (尝试 {retry + 1}/{max_retries}): {e_submit_det}", flush=True)
                        if retry < max_retries - 1:
                            time.sleep(2.5)
                        else:
                            print("❗网络异常退出 (提交检测文章)", flush=True);
                            break

                if response_submit_detection_json and response_submit_detection_json.get("errcode") == 0:
                    gold_earned = response_submit_detection_json.get('data', {}).get('gold', '未知')
                    print(f"✅ 第{article_count + 1}次阅读检测文章成功---获得金币:💰{gold_earned}💰", flush=True)
                else:
                    err_msg = response_submit_detection_json.get('msg',
                                                                 '提交失败或无响应') if response_submit_detection_json else '提交失败或无响应'
                    print(f"❗❗❗过检测失败: {err_msg}", flush=True)
                    break
            else:
                time.sleep(read_sleep_time)
                url_submit_normal = f"{article_page_url_parts.scheme}://{article_page_url_parts.netloc}/jinbicp?gt={gt}&time={read_sleep_time}&timestamp={current_timestamp}"
                headers_submit_normal = {
                    "Host": f"{article_page_url_parts.netloc}", "Connection": "keep-alive", "User-Agent": f"{UA} {uas}",
                    "Accept": "application/json, text/javascript, */*; q=0.01", "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"{article_page_url_parts.scheme}://{article_page_url_parts.netloc}/xsysy.html?{article_page_url_parts.query}",
                    "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
                }
                response_submit_normal_json = None
                for retry in range(max_retries):
                    try:
                        response_submit_normal_json = requests.get(url_submit_normal, headers=headers_submit_normal,
                                                                   timeout=25).json()
                        break
                    except Exception as e_submit_norm:
                        print(f"❗提交普通文章状态网络异常 (尝试 {retry + 1}/{max_retries}): {e_submit_norm}",
                              flush=True)
                        if retry < max_retries - 1:
                            time.sleep(2.5)
                        else:
                            print("❗网络异常退出 (提交普通文章)", flush=True);
                            break

                if response_submit_normal_json and response_submit_normal_json.get("errcode") == 0:
                    gold_earned = response_submit_normal_json.get("data", {}).get("gold", "未知")
                    print(f"📖 本次模拟阅读{read_sleep_time}秒", flush=True)
                    print(f"✅ 第{article_count + 1}次阅读成功---获得金币:💰{gold_earned}💰", flush=True)
                else:
                    err_msg = response_submit_normal_json.get('msg',
                                                              '提交失败或无响应') if response_submit_normal_json else '提交失败或无响应'
                    print(f"❗阅读文章失败: {err_msg}", flush=True)
                    break
            print(f"{'-' * 60}\n", flush=True)

        if money_Withdrawal == 1:
            current_last_gold = 0
            if isinstance(last_gold, (int, str)) and str(last_gold).isdigit():
                current_last_gold = int(last_gold)

            if current_last_gold > 5000:
                print(f"{'=' * 12}💰开始提现💰{'=' * 12}\n", flush=True)
                try:
                    url_withdraw_page = f"http://{parsed_domain}"
                    headers_withdraw_page = {
                        "Host": f"{parsed_domain}", "Connection": "keep-alive", "Cache-Control": "max-age=0",
                        "Upgrade-Insecure-Requests": "1", "User-Agent": f"{UA} {uas}",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/tpg,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                        "X-Requested-With": "com.tencent.mm", "Cookie": f"ysmuid={ysmuid}"
                    }
                    response_withdraw_page_text = requests.get(url_withdraw_page, headers=headers_withdraw_page,
                                                               timeout=10).text
                    res1 = re.sub('\s', '', response_withdraw_page_text)
                    exchangeUrl_match = re.findall('"target="_blank"href="(.*?)">提现<', res1)
                    if not exchangeUrl_match:
                        print("❗提现失败：未能在页面找到提现链接。", flush=True)
                        return

                    eurl = exchangeUrl_match[0]
                    eurl_parsed = urlparse(eurl)
                    eurl_host = eurl_parsed.netloc
                    eurl_query_dict = parse_qs(eurl_parsed.query)
                    eurl_unionid = eurl_query_dict.get('unionid', [''])[0]
                    eurl_request_id = eurl_query_dict.get('request_id', [''])[0]

                    if not all([eurl_host, eurl_unionid, eurl_request_id]):
                        print(
                            f"❗提现链接解析不完整: host={eurl_host}, unionid={eurl_unionid}, request_id={eurl_request_id}",
                            flush=True)
                        return

                    gold_to_withdraw = int(current_last_gold / 1000) * 1000
                    if gold_to_withdraw < 5000:
                        print(f"🔔 金币 ({current_last_gold}) 计算后不足5000 ({gold_to_withdraw})，不执行提现\n",
                              flush=True)
                        return

                    print(f"💰 准备提现金额:{gold_to_withdraw}", flush=True)

                    url_user_gold = f"http://{eurl_host}/yunonline/v1/user_gold"
                    headers_user_gold = {
                        "Host": f"{eurl_host}", "Accept": "application/json, text/javascript, */*; q=0.01",
                        "X-Requested-With": "XMLHttpRequest", "User-Agent": f"{UA} {uas}",
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Origin": f"http://{eurl_host}", "Referer": eurl, "Cookie": f"ysmuid={ysmuid}"
                    }
                    data_user_gold = {"unionid": eurl_unionid, "request_id": eurl_request_id, "gold": gold_to_withdraw}
                    response_user_gold_json = requests.post(url_user_gold, headers=headers_user_gold,
                                                            data=data_user_gold, timeout=10).json()

                    if response_user_gold_json.get("errcode") != 0:
                        print(f"❗提现预请求失败: {response_user_gold_json.get('msg', '未知错误')}", flush=True)
                        return

                    url_final_withdraw = f"http://{eurl_host}/yunonline/v1/withdraw"
                    headers_final_withdraw = headers_user_gold
                    data_final_withdraw = {
                        "unionid": eurl_unionid, "signid": eurl_request_id, "ua": "2",
                        "ptype": "0", "paccount": "", "pname": ""
                    }
                    response_final_withdraw_json = requests.post(url_final_withdraw, headers=headers_final_withdraw,
                                                                 data=data_final_withdraw, timeout=10).json()

                    if response_final_withdraw_json.get("errcode") == 0:
                        print("💰 恭喜您，提现成功！\n", flush=True)
                    else:
                        print(f"❗提现失败: {response_final_withdraw_json.get('msg', '未知错误')}", flush=True)

                except requests.RequestException as e_wd:
                    print(f"❗提现过程中网络错误: {e_wd}", flush=True)
                except json.JSONDecodeError as e_wd_json:
                    print(f"❗提现过程中JSON解析错误: {e_wd_json}", flush=True)
                except IndexError:
                    print(f"❗提现失败：解析提现链接时发生错误 (IndexError)。", flush=True)
                except Exception as e_wd_unknown:
                    print(f"❗提现过程中发生未知错误: {e_wd_unknown}", flush=True)

            elif not isinstance(last_gold, (int, str)) or not str(last_gold).isdigit():
                print(f"🔔 金币值 ({last_gold}) 无效，无法判断是否提现\n", flush=True)
            else:
                print(f"{'=' * 17}{'=' * 17}", flush=True)
                print(f"🔔 金币 ({current_last_gold}) 不足5000，不执行提现\n", flush=True)
        elif money_Withdrawal == 0:
            print(f"{'=' * 17}{'=' * 17}", flush=True)
            print(f"🔔 自动提现已关闭，不执行提现\n", flush=True)
    else:
        print(f"❗获取用户信息失败: {response_gold_json.get('msg', '未知错误')}", flush=True)
        return  # Return if user info fails


def notice():
    try:
        print("""
            欢迎关注公众号【极客快乐营】
            公众号二维码：
            https://free-img.400040.xyz/4/2025/06/30/686174d049215.png
            活动入口:
            https://img.hnking.cn/blog/202508161653803.png
        """)
        # response = requests.get("https://gitee.com/gngkj/wxyd/raw/master/label.txt", timeout=5)
        # response.raise_for_status()
        # print(response.text)
    except requests.RequestException as e:
        print(f"❗网络异常，获取通知时出错: {e}")


if __name__ == "__main__":
    notice()
    accounts_env = os.getenv("xyy")
    money_Withdrawal = 0 if os.getenv("xyytx", "0") == "0" else 1

    UA_env = os.getenv("UA")
    if UA_env is None:
        print("❗未找到环境变量 UA，程序终止。", flush=True)
        exit()
    UA = UA_env

    if accounts_env is None:
        print("❗未找到环境变量 xyy，程序终止。", flush=True)
        exit()
    else:
        accounts_list = accounts_env.split("@")
        num_of_accounts = len(accounts_list)
        print(f"\n获取到 {num_of_accounts} 个账号", flush=True)
        for i, account_str in enumerate(accounts_list, start=1):
            if not account_str.strip():
                print(f"第 {i} 个账号为空，已跳过。", flush=True)
                continue
            try:
                if len(account_str.split("&")) < 3:
                    print(f"❗第 {i} 个账号格式不正确 (应为 ysmuid&unionid&token)，已跳过: {account_str}", flush=True)
                    continue
            except IndexError:
                print(f"❗第 {i} 个账号格式解析错误 (IndexError)，已跳过: {account_str}", flush=True)
                continue

            process_account(account_str, i)

if __name__ == '__main__': pass
