#大国医道羌医探秘答题领现金红包！
#下方""中间填写授权码！
sqm = "1f8748bc243704c12bd3bd107ff638a288a165f571d2b54a25efd0ace1032f09"

#使用方法:
#抓包只需要抓openid和课程id
#每个微信的openid只需要抓一次即可，不用每天都抓！
#微信的openid要填入环境变量里，课程id填入脚本第25行的id中
#抓包后搜索openid或者wx_openid即可找到。

#环境变量创建变量
#变量名称:QingLongBaiHu_dgyd_qytm
#变量值格式:备注#openid
#变量值的备注随便写 只是为了方便区分不同的微信
#多号请用@隔开
#多号变量值示例:备注#openid@备注#openid@备注#openid

#填写当天的题目id
#复制抓包url中activityV2?id= 的值填到下方id=的""中间
#或者复制抓包url中activityDetatil?id= 的值填到下方id=的""中间
#如果你不同的号在不同的群 起线不同 则多个不同的课程id用#隔开
#id = "f06ad2c1b2594b2b351986ac240c491d"
#id = "e5deace96222d913d2fd20fa54112422"
id = "eb5b5d68bc9f1bd937e99520e17b22b2"

#host根据你抓包的url修改即可，非必要请勿修改
host = "api.h5.sagx.net"
#填写host不需要带http://或https://

import requests
import json
import time
import os
accounts_list = os.environ.get("QingLongBaiHu_dgyd_qytm").split("@")
num_of_accounts = len(accounts_list)
print(__import__('base64').b64decode("6Z2S6b6Z55m96JmO5o+Q56S677ya6I635Y+W5Yiw").decode('utf-8'),num_of_accounts,__import__('base64').b64decode("5Liq6LSm5Y+3Cg==").decode('utf-8'))
time.sleep(1)
id_list = id.split("#")
time.sleep(1)
for id in id_list:
    for dgyd_ck in accounts_list:
        dgyd_qytm_ck = dgyd_ck.split("#")
        time.sleep(2)
        print("-" * 40)
        name = dgyd_qytm_ck[0]
        print("正在运行的账号:",name)
        url = f"http://125.122.14.177:8000/qytm?openid={dgyd_qytm_ck[1]}&id={id}&host={host}&ck={sqm}"
        headers = {
          'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/125.3  Mobile/15E148 Safari/605.1.15",
          'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          'Accept-Encoding': "gzip, deflate",
          'Pragma': "no-cache",
          'Proxy-Connection': "keep-alive",
          'Upgrade-Insecure-Requests': "1",
          'Accept-Language': "zh-CN,zh-Hans;q=0.9",
          'Cache-Control': "no-cache",
          'Cookie': "72756147c9fc44336c4efb53e47fb97a=bd4e5d78-5ecc-49fc-b380-cdc5e5ea2ac8.bLgI2g6bC-PHmksej6uzxG1l8TE"
        }
        fh = requests.get(url, headers=headers)
        fh_json = fh.json()
        print(fh_json)
        status = fh_json.get("status")
        if status == "error":
            print(fh_json["message"]) 
            continue
        gettoken_status = fh_json.get("gettoken")
        if gettoken_status == "参数错误！":
            print("课程id不正确，请检查！")
            continue
        elif gettoken_status == "该微信号未注册，请先注册！":
            print("变量值openid不正确，请检查！")
            continue
        elif gettoken_status == "活动已结束，请参与其它活动！":
            print("课程已过期！请抓最新课程id")
            continue
        if fh_json.get("getqs") is not None:
            print("当前期数:",fh_json.get("getqs"))
        if fh_json.get("dt") is not None:
            print(fh_json.get("dt"))
