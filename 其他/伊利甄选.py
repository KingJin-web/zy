"""
实物收益参考:免单卷虚拟会员卷
1.#小程序://甄稀冰淇淋/Zr6Cnm6ShD5Z6up,进入活动授权登陆。
2.然后打开抓包软件,抓包之前关闭小程序重新进入下抓域名msmarket.msx.digitalyili.com的参数值。
提交格式:mobile#access-token 格式不对系统是无法提交的。
*提交格式示列:150xxx192#xka9vTYME6TOoeGUjszAPJwwR70Vdwx1xbJnZHXYPz/p2+ZEvIMfn9Sw2n8GMc0nY8ZZPTlqf2Dwl2r76bGnWj88IkS8hLk9Un9jxxx
export ylzx="mark#access-token"
#小程序://甄稀冰淇淋/Zr6Cnm6ShD5Z6up
"""
#import notify
import requests, json, re, os, sys, time, random, datetime, threading, execjs
environ = "ylzx"
name = "꧁༺ 伊利༒甄稀 ༻꧂"
session = requests.session()
#---------------------主代码区块---------------------

def run(arg1):
    header = {
        "Host": "msmarket.msx.digitalyili.com",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090b13)XWEB/11581",
        "access-token": arg1,
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    try:
        url = 'https://msmarket.msx.digitalyili.com/gateway/api/auth/account/user/info'
        response = session.get(url=url, headers=header).json()
        if not response["data"]:
            print(f'⭕异常：需更新token')
            return
        else:
            openId = response["data"]["openId"]
        headeract = {
            "Host": "zhenxiapp-admin.msxapi.digitalyili.com",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "x-requested-with": "com.tencent.mm",
            "priority": "u=1, i",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.103 Mobile Safari/537.36 XWEB/1300473 MMWEBSDK/20250201 MMWEBID/6533 MicroMessenger/8.0.57.2820(0x2800393F) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wx21fd8b5d6d4cf1ca",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "Android",
            "sec-ch-ua": '"Chromium";v="130", "Android WebView";v="130", "Not?A_Brand";v="99"',
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        for i in range(3):
            url = ' https://zhenxiapp-admin.msxapi.digitalyili.com/api/draw_wh'
            response = session.post(url=url, headers=headeract,json={"openid":openId}).json()
            print(f'☁️抽奖：{response["data"]["prize_name"]}')
        url = 'https://zhenxiapp-admin.msxapi.digitalyili.com/api/draw_records_wh'
        response = session.post(url=url, headers=headeract,json={"openid":openId,"page":1,"pageSize":100}).json()
        if response["data"]:
            for item in response["data"]["data"]:
                prizeid =  item["id"]
                status = item["status"]
                prize_name = item["prize_name"]
                if status == 1:
                    url = 'https://zhenxiapp-admin.msxapi.digitalyili.com/api/set_coupon_wh'
                    response = session.post(url=url, headers=headeract,json={"openid":openId,"record_id":prizeid}).json()
                    if response["msg"] != 'success':
                        print(f'⭕领取：{response["msg"]}')
                if not ("199-120" in prize_name):
                    print(f'好券：{prize_name}')
    except Exception as e:
        print(e)

def main():


    global id, message
    message = []
    if os.environ.get(environ):
        ck = os.environ.get(environ)
    else:
        ck = ""
        if ck == "":
            print("⭕请设置变量")
            sys.exit()
    ck_run = ck.split('\n')
    ck_run = [item for item in ck_run if item]
    print(f"{' ' * 7}{name}\n\n")
    for i, ck_run_n in enumerate(ck_run):
        try:
            mark,arg1 = ck_run_n.split('#',2)
            id = mark[:3] + "*****" + mark[-3:]
            print(f"账号 [{i + 1}/{len(ck_run)}]：{id}")
            run(arg1)
            time.sleep(random.randint(1, 2))
        except Exception as e:
            print(e)
    print(f"\n\n-------- ☁️ 执 行  结 束 ☁️ --------\n\n")
    if message:
        output = '\n'.join(num for num in message)
        notify.send(name, output)

if __name__ == '__main__':
    main()