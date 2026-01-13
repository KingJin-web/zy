#入口:聚赏圈
#抓包mini.nxqingchuangkeji.com域名下的token填到环境变量JSQ中，多账号使用&分割

import requests
import os
import json
import time
import random
from datetime import datetime


def get_proclamation():
    print("a")
    # primary_url = "https://github.com/3288588344/toulu/raw/refs/heads/main/tl.txt"
    # backup_url = "https://tfapi.cn/TL/tl.json"
    #
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    # }
    #
    # for url in [primary_url, backup_url]:
    #     try:
    #         response = requests.get(url, headers=headers, timeout=20)
    #         if response.status_code == 200:
    #
    #             print("📢 公告信息")
    #             print("=" * 45)
    #             print(response.text)
    #             print("=" * 45 + "\n")
    #             print(f"公告获取成功，开始执行任务...\n")
    #             return
    #     except requests.exceptions.RequestException as e:
    #         print(f"获取公告时发生错误 (链接: {url}): {e}, 继续尝试下一个链接...")
    #
    # print("所有公告获取尝试均失败，继续执行任务...")


def get_tokens_from_env():

    tokens = os.getenv('JSQ', '').split('&')
    return tokens


def fetch_user_info(token):
    
    url = "https://mini.nxqingchuangkeji.com/api/Useraectype/userBasicsInfo"
    headers = {
        "Host": "mini.nxqingchuangkeji.com",
        "token": token,
        "content-type": "application/json",
        "charset": "utf-8",
        "referer": "https://servicewechat.com/wx5804e8877027009c/10/page-frame.html",
        "accept-encoding": "gzip, deflate, br"
    }
    payload = {}

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get("code") == 1:  # 如果获取成功
                data = user_data.get("data", {})
                nickname = data.get("nickname", "未知账户")
                money = data.get("money", "未知余额")
                return nickname, money
        return "未知账户", "未知余额"
    except Exception:
        return "未知账户", "未知余额"


def send_sign_request(token):
    
    headers = {
        'Host': 'mini.nxqingchuangkeji.com',
        'token': token,
        'content-type': 'application/json',
        'charset': 'utf-8',
        'referer': 'https://servicewechat.com/wx5804e8877027009c/10/page-frame.html',
    }

    data = '{"time": ' + str(int(time.time())) + '}'

    try:
        response = requests.post('https://mini.nxqingchuangkeji.com/api/sign/sign', headers=headers, data=data)
        return response.json()
    except Exception:
        return {"code": -1, "msg": "签到失败"}


def claim_gold(token):
    
    data = {
        'start_time': 1750994743,
        'end_time': 1750994760,
        'sign': '95b3cc356f28859b13178d76818595fa'
    }
    headers = {
        'Host': 'mini.nxqingchuangkeji.com',
        'token': token,
        'content-type': 'application/json',
        'charset': 'utf-8',
        'referer': 'https://servicewechat.com/wx5804e8877027009c/10/page-frame.html',
    }
    try:
        response = requests.post('https://mini.nxqingchuangkeji.com/api/Advertising/keepAdvertisingGold', headers=headers, data=json.dumps(data))
        return response.json()
    except Exception:
        return {"code": -1, "msg": "广告请求失败"}


def main():
    """主函数"""
    tokens = get_tokens_from_env()
    if not tokens:
        print("未设置JSQ环境变量")
        print("=" * 45)
        return
    
    for token in tokens:
        if not token:
            continue

        # 获取账户信息
        nickname, money = fetch_user_info(token)
        account_info = f"账户: {nickname}, 余额: {money}"

        # 执行签到
        sign_result = send_sign_request(token)
        if sign_result.get('code') == 1:
            print(f"{account_info} - 签到成功")
            print("=" * 45)
        else:
            print(f"{account_info} - 签到失败，原因：{sign_result.get('msg', '未知错误')}")
            print("=" * 45)

        # 执行看广告获取金币（20次，随机延迟）
        success_count = 0
        for i in range(20):
            ad_result = claim_gold(token)
            if ad_result.get('code') == 1 and ad_result.get('msg') == '领取奖励成功':
                success_count += 1
                print(f"{account_info} - 广告任务第 {i+1} 次成功")
                print("=" * 45)
            else:
                print(f"{account_info} - 广告任务第 {i+1} 次失败，原因：{ad_result.get('msg', '未知错误')}")
            time.sleep(random.uniform(5, 320))  

        print(f"{account_info} - 广告任务完成，成功 {success_count}/20 次")
        print("=" * 45)

if __name__ == "__main__":
    start_time = datetime.now()
    
    
    get_proclamation()
    main()
    
    end_time = datetime.now()
    

  