# 变量xlck  换行分开    抓取https://a2aev2.h5.sagx.net/api-user/v2/getToken域名下的wx_openid
# 变量xlid    每天自己抓取
# 变量xlhost  域名可能会变换  当变换的时候自己更改域名  当前域名 a2aev2.h5.sagx.net
# 每天定时一次既可  多了可能会报错  等有问题在修改

# host = "a2aev2.h5.sagx.net"

import time
import os
import requests
import json

import random
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

token_list = os.environ.get("xlck").split("\n")
xlid = os.environ.get("xlid")
host = os.environ.get("xlhost")
num_tokens = len(token_list)
print("当前获取到", num_tokens, "个账号 \n")
n = 0
if token_list or xlid or host:
    print("变量获取成功")
else:
    print("不填变量玩个蛋")
    exit()
for token in token_list:
    id = xlid
    code = "051IMzll2wDJOe4Vxwml2DpN2d1IMzlX"
    n += 1
    print(f"第{n}个账号执行中")
    # print(token_json)
    openid = token
    headers = {"Host": f"{host}", "Connection": "keep-alive", "Content-Length": "84", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090c11) XWEB/11581 Flue", "Content-Type": "application/json", "Accept": "*/*", "Origin": f"https://{host}", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": f"https://{host}/activity/index.html?id={id}&code=0&state=STATE", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "zh-CN,zh;q=0.9"}
    url = f"https://{host}/api-user/v2/getToken"
    data = {"wx_openid": openid, "id": id}
    data = json.dumps(data, separators=(',', ':'))
    response = requests.post(url, headers=headers, data=data, verify=False)
    if response.status_code == 200:
        response = response.json()
        try:
            token = response["data"]["token"]
            print(f"token获取成功，token为{token}")
        except:
            print(response)
            continue

    else:
        print(response)
        print("填写信息错误")
        continue

    headers = {"Host": f"{host}", "Connection": "keep-alive", "Accept": "application/json", "Authorization": f"Bearer {token}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090c11) XWEB/11581 Flue", "Content-Type": "application/json", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": f"https://{host}/activity/index.html?id={id}&code=0&state=STATE", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "zh-CN,zh;q=0.9"}
    url = f"https://{host}/api-user/v2/activityDetatil"
    params = {"id": id, "withMaterial": "1"}


    def find_result_one(data):
        for index, item in enumerate(data):  # 使用 enumerate 函数同时获取元素的索引和元素本身
            if item.get('result') == '1':  # 使用 get 方法获取 result 键的值
                return index, item
        return None, None


    response = requests.get(url, headers=headers, params=params, verify=False)
    if response.status_code == 200:
        response = response.json()
        # print(response)
        userActivityId = response["meta"]["joinInfo"]["userActivityId"]
        activity_id = response["data"]["activity_id"]
        # print(activity_id)
        daan11 = response["data"]["materialDetail"]["questions"][0]["answer"]
        # print(daan11)
        index, item = find_result_one(daan11)
        # print(f"结果为 1 的元素索引是: {index}, 元素是: {item}")
        daan1 = f"0_{index}"
        print(daan1)
        questions = response.get("data", {}).get("materialDetail", {}).get("questions", [])
        if len(questions) > 1 and questions[1]:
            # 这里是满足条件时的操作
            daan12 = response["data"]["materialDetail"]["questions"][1]["answer"]
            index, item = find_result_one(daan12)
            daan2 = f"1_{index}"
            print(daan2)
        else:
            daan2 = ""

    else:
        print("获取答案错误")
        continue


    # def suijisecong():
    #     suijishu = np.random.randint(3700, 5600)
    #     return suijishu



    def suijisecong():
        suijishu = random.randint(3700, 5600)
        return suijishu

    time_url = f"https://{host}/api-user/v1/activityWatchVideo"
    time_data = {"userActivityId": userActivityId, "second": suijisecong()  # 设置一个很大的播放时间
                 }
    response = requests.post(time_url, json=time_data, headers=headers, verify=False).json()
    if response['status'] == "success":
        print("时间上报成功")
    else:
        print("错误")
        continue

    finish_url = f"https://{host}/api-user/v1/activityWatchVideoOver"
    finish_data = {"userActivityId": userActivityId}

    response = requests.post(finish_url, json=finish_data, headers=headers, verify=False).json()
    # print(response)
    if response['status'] == "success":
        print("时间设置成功")
    else:
        print("错误")
        continue

    headers = {"Host": f"{host}", "Connection": "keep-alive", "Content-Length": "46", "sec-ch-ua-platform": "\"Android\"", "Authorization": f"Bearer {token}", "User-Agent": "Mozilla/5.0 (Linux; Android 14; 2311DRK48C Build/UP1A.230905.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.103 Mobile Safari/537.36 XWEB/1300259 MMWEBSDK/20241103 MMWEBID/9654 MicroMessenger/8.0.55.2780(0x28003734) WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64", "Accept": "application/json", "sec-ch-ua": "\"Chromium\";v=\"130\", \"Android WebView\";v=\"130\", \"Not?A_Brand\";v=\"99\"", "Content-Type": "application/json", "sec-ch-ua-mobile": "?1", "Origin": f"https://{host}", "X-Requested-With": "com.tencent.mm", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": f"https://{host}/activity/index.html?id={id}", "Accept-Encoding": "gzip, deflate, br, zstd", "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"}
    url = f"https://{host}/api-user/v1/receiveAwardAndWatchOver"
    if daan2 != "":
        data = {"activity_id": activity_id, "answers": [f"{daan1}", f"{daan2}"]}
    else:
        data = {"activity_id": activity_id, "answers": [f"{daan1}"]}
    data = json.dumps(data, separators=(',', ':'))
    response = requests.post(url, headers=headers, data=data, verify=False).json()
    if response['status_code'] == 200:
        red_money = response["data"]["red_money"]
        print(f"答题成功，获得奖励{red_money}")
        time.sleep(15)
    else:
        msg = response["message"]
        print("答题失败")
        print(msg)
        time.sleep(10)
        continue