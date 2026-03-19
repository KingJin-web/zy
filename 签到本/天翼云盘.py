#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2025/5/9 9:48
# 原作者：https://www.52pojie.cn/thread-1231190-1-1.html
# 出处：https://github.com/vistal8/tianyiyun
# cron "30 4 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('天翼云盘签到');
# 变量说明：ty_username 用户名 &隔开  ty_password 密码 &隔开
# 5.9变更：更改推送为表格单次推送 打印日志简化 现在抽奖只能抽一次 第二次和第三次已经失效。
# 推送变量需设置 WXPUSHER_APP_TOKEN 和 WXPUSHER_UID（多个UID用&分隔）
# 有图形验证码就是风控了 自己去网页端登陆 输入验证码 等几天
import time
import os
import random
import json
import base64
import hashlib
import rsa
import requests
import re
from urllib.parse import urlparse

BI_RM = list("0123456789abcdefghijklmnopqrstuvwxyz")
B64MAP = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

# 从环境变量获取账号信息
ty_usernames = os.getenv("ty_username").split('&') if os.getenv("ty_username") else []
ty_passwords = os.getenv("ty_password").split('&') if os.getenv("ty_password") else []

# 检查环境变量
if not ty_usernames or not ty_passwords:
    raise ValueError("❌ 请设置环境变量 ty_username 和 ty_password")

# 组合账号信息
accounts = [{"username": u, "password": p} for u, p in zip(ty_usernames, ty_passwords)]

# WxPusher配置
WXPUSHER_APP_TOKEN = os.getenv("WXPUSHER_APP_TOKEN")
WXPUSHER_UIDS = os.getenv("WXPUSHER_UID", "").split('&')

def mask_phone(phone):
    """隐藏手机号中间四位"""
    return phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone[:3] + "****" + phone[-4:]

def int2char(a):
    return BI_RM[a]

def b64tohex(a):
    d = ""
    e = 0
    c = 0
    for i in range(len(a)):
        if list(a)[i] != "=":
            v = B64MAP.index(list(a)[i])
            if 0 == e:
                e = 1
                d += int2char(v >> 2)
                c = 3 & v
            elif 1 == e:
                e = 2
                d += int2char(c << 2 | v >> 4)
                c = 15 & v
            elif 2 == e:
                e = 3
                d += int2char(c)
                d += int2char(v >> 2)
                c = 3 & v
            else:
                e = 0
                d += int2char(c << 2 | v >> 4)
                d += int2char(15 & v)
    if e == 1:
        d += int2char(c << 2)
    return d

def rsa_encode(j_rsakey, string):
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    result = b64tohex((base64.b64encode(rsa.encrypt(f'{string}'.encode(), pubkey))).decode())
    return result

def login(username, password):
    print("🔄 正在执行登录流程...")
    s = requests.Session()
    try:
        urlToken = "https://m.cloud.189.cn/udb/udb_login.jsp?pageId=1&pageKey=default&clientType=wap&redirectURL=https://m.cloud.189.cn/zhuanti/2021/shakeLottery/index.html"
        r = s.get(urlToken)
        match = re.search(r"https?://[^\s'\"]+", r.text)
        if not match:
            print("❌ 错误：未找到动态登录页")
            return None
            
        url = match.group()
        r = s.get(url)
        match = re.search(r"<a id=\"j-tab-login-link\"[^>]*href=\"([^\"]+)\"", r.text)
        if not match:
            print("❌ 错误：登录入口获取失败")
            return None
            
        href = match.group(1)
        r = s.get(href)
        
        captchaToken = re.findall(r"captchaToken' value='(.+?)'", r.text)[0]
        lt = re.findall(r'lt = "(.+?)"', r.text)[0]
        returnUrl = re.findall(r"returnUrl= '(.+?)'", r.text)[0]
        paramId = re.findall(r'paramId = "(.+?)"', r.text)[0]
        j_rsakey = re.findall(r'j_rsaKey" value="(\S+)"', r.text, re.M)[0]
        s.headers.update({"lt": lt})

        username_enc = rsa_encode(j_rsakey, username)
        password_enc = rsa_encode(j_rsakey, password)
        
        data = {
            "appKey": "cloud",
            "accountType": '01',
            "userName": f"{{RSA}}{username_enc}",
            "password": f"{{RSA}}{password_enc}",
            "validateCode": "",
            "captchaToken": captchaToken,
            "returnUrl": returnUrl,
            "mailSuffix": "@189.cn",
            "paramId": paramId
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0',
            'Referer': 'https://open.e.189.cn/',
        }
        
        r = s.post(
            "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do",
            data=data,
            headers=headers,
            timeout=10
        )
        
        if r.json().get('result', 1) != 0:
            print(f"❌ 登录错误：{r.json().get('msg')}")
            return None
            
        s.get(r.json()['toUrl'])
        print("✅ 登录成功")
        return s
        
    except Exception as e:
        print(f"⚠️ 登录异常：{str(e)}")
        return None

def send_wxpusher(msg):
    if not WXPUSHER_APP_TOKEN or not WXPUSHER_UIDS:
        print("⚠️ 未配置WxPusher，跳过消息推送")
        return
    
    url = "https://wxpusher.zjiecode.com/api/send/message"
    headers = {"Content-Type": "application/json"}
    for uid in WXPUSHER_UIDS:
        data = {
            "appToken": WXPUSHER_APP_TOKEN,
            "content": msg,
            "contentType": 3,
            "topicIds": [],
            "uids": [uid],
        }
        try:
            resp = requests.post(url, json=data, headers=headers, timeout=10)
            if resp.json().get('code') == 1000:
                print(f"✅ 消息推送成功 -> UID: {uid}")
            else:
                print(f"❌ 消息推送失败：{resp.text}")
        except Exception as e:
            print(f"❌ 推送异常：{str(e)}")

def main():
    print("\n=============== 天翼云盘签到开始 ===============")
    all_results = []
    
    for acc in accounts:
        username = acc["username"]
        password = acc["password"]
        masked_phone = mask_phone(username)
        account_result = {"username": masked_phone, "sign": "", "lottery": ""}
        
        print(f"\n🔔 处理账号：{masked_phone}")
        
        # 登录流程
        session = login(username, password)
        if not session:
            account_result["sign"] = "❌ 登录失败"
            all_results.append(account_result)
            continue
        
        # 签到流程
        try:
            # 每日签到
            rand = str(round(time.time() * 1000))
            sign_url = f'https://api.cloud.189.cn/mkt/userSign.action?rand={rand}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6',
                "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
                "Host": "m.cloud.189.cn",
            }
            resp = session.get(sign_url, headers=headers).json()
            if resp.get('isSign') == "false":
                account_result["sign"] = f"✅ +{resp['netdiskBonus']}M"
            else:
                account_result["sign"] = f"⏳ 已签到+{resp['netdiskBonus']}M"
            
            # 单次抽奖（原第一次抽奖）
            time.sleep(random.randint(2, 5))
            lottery_url = 'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN'
            resp = session.get(lottery_url, headers=headers).json()
            if "errorCode" in resp:
                account_result["lottery"] = f"❌ {resp.get('errorCode')}"
            else:
                prize = resp.get('prizeName') or resp.get('description')
                account_result["lottery"] = f"🎁 {prize}"
                
        except Exception as e:
            account_result["sign"] = "❌ 操作异常"
            account_result["lottery"] = f"⚠️ {str(e)}"
        
        all_results.append(account_result)
        print(f"  {account_result['sign']} | {account_result['lottery']}")
    
    # 生成汇总表格
    table = "### ⛅ 天翼云盘签到汇总\n\n"
    table += "| 账号 | 签到结果 | 每日抽奖 |\n"
    table += "|:-:|:-:|:-:|\n"
    for res in all_results:
        table += f"| {res['username']} | {res['sign']} | {res['lottery']} |\n"
    
    # 发送汇总推送
    send_wxpusher(table)
    print("\n✅ 所有账号处理完成！")

if __name__ == "__main__":
    main()