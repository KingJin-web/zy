## #实物收益参考:实物
#1.先各大应用市场下载江淮卡友，然后先注册账户。
#2.然后打开抓包软件抓域名http://jacwxmp.starnetah.com:18280/v2driver/v2/login下请求表单中的全部值。
#提交格式示列:备注#{"phone":"XXX","password":
# "67cb9aa7f8aec884f54592e911aeXXX","sendMessageKey":"default",
# "deviceType":"1","appType":"0","sign":
# "GwtKVy8XKB2T0vTecTUpZw9zlBCf7MDFGcVJw88/
# u3p3vDLGMzq0zDuEJa6BZc6gdJBNTNT4FAnP0jnRwrxzH
# +usO7AEaverTnF0SjR59MkC5qJjJ39ufWKP9ziSJWKcmV0Kn3Xj8dYt+CJzruVLEeKI3dqtN7H9FQ3rXXX="}

#import notify
import requests, json, re, os, sys, time, random, datetime, threading, execjs
environ = "jhky"
name = "꧁༺ 江淮༒卡友 ༻꧂"
session = requests.session()
#---------------------主代码区块---------------------

def run(body):
    header = {
        "Connection": "keep-alive",
        "Content-Length": "309",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "remoteToken": "",
        "lon":"117.233674",
        "deviceModel":"MI 8",
        "versionType":"1",
        "appType": "0",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.101 Mobile Safari/537.36",
        "Content-Type": "application/json",
        "version":"",
        "lat":"31.826972",
        "osName":"Android 10",
        "token":"",
        "deviceType":"0",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "X-Requested-With": "com.esvtek.jac.driver",
    }
    try:
        url = f'http://jacwxmp.starnetah.com:18280/v2driver/v2/login'
        response = session.post(url=url, headers=header,data=body).json()
        #print(response)
        if response["resultCode"] == 200:
            ucId = response["data"]["userId"]
            token = response["data"]["token"]
            remoteToken = response["data"]["remoteToken"]
            remoteUserId = response["data"]["remoteUserId"]
        else:
            return
        header["remoteToken"] = remoteToken
        header["token"] = token
        url = f'http://jacwxmp.starnetah.com:18280/v2driver/signIn'
        response = session.post(url=url, headers=header,json={"ucId":ucId}).json()
        plcount = 0
        ftcount = 0
        count = 4
        url = f'http://jacwxmp.starnetah.com:18280/v2driver/queryIntegralHistory'
        response = session.post(url=url, headers=header,json={"ucId":ucId}).json()
        #print(response)
        if response["resultCode"] == 200:
            for item in response["data"]["list"]:
                credits = item["credits"]
                integralItem = item["integralItem"]
                createTime = int(int(item["createTime"])/1000)
                createTime_date = datetime.datetime.fromtimestamp(createTime)
                if createTime_date.day == datetime.datetime.now().day:
                    if "评论" in integralItem:
                        plcount = plcount + 1
                        #print(plcount)
                    if "发帖" in integralItem:
                        ftcount = ftcount + 1
                        #print(ftcount)
        if (count-ftcount) != 0:
            #for i in range(1):
            for i in range(count-ftcount):
                headers = {
                    "Connection": "keep-alive",
                    "Content-Length": "185",
                    "Pragma": "no-cache",
                    "Cache-Control": "no-cache",
                    "deviceType":"0",
                    "osName":"Android 10",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.101 Mobile Safari/537.36",
                    "Content-Type": "application/json",
                    "version":"",
                    "deviceModel":"MI 8",
                    "versionType":"1",
                    "appType": "0",
                    "token":token,
                    "Accept": "*/*",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "X-Requested-With": "com.esvtek.jac.driver",
                }
                #print(token)
                urlft = f'http://jacwxmp.starnetah.com:18180/jac/bbs/api/invitationInfo/newInvitationImage'
                responseft = session.post(url=urlft, headers=headers,json={"atUserIdList":[],"content":"打卡","displayPhoto":"","forumId":0,"imageList":[],"newTopicList":[],"releaseType":0,"title":"打卡","topicList":[],"vehicleBrandName":"","videoUrl":""}).json()
                #print(responseft)
                time.sleep(5)
                urlftid = 'http://jacwxmp.starnetah.com:18180/jac/bbs/api/invitationInfo/myInvitationList'
                responseftid = session.post(url=urlftid, headers=headers,json={"page":1,"size":10,"bbsType":"image"}).json()
                #print(responseftid)
                ftid = responseftid["data"][0]["id"]
                time.sleep(5)
                urlftpl = f'http://jacwxmp.starnetah.com:18180/jac/bbs/api/invitationComment/newInvitationComment'
                responseftpl = session.post(url=urlftpl, headers=headers,json={"commentContent":"打卡评论一天","invitationId":ftid}).json()
                #print(responseftpl)
                time.sleep(5)
                urlftst = f'http://jacwxmp.starnetah.com:18180/jac/bbs/api/invitationInfo/deleteMyInvitation'
                responseftst = session.post(url=urlftst, headers=headers,json={"invitationId":ftid}).json()
                #print(responseftst)
                time.sleep(5)
        plcount = 0
        plpoint = 0
        ftcount = 0
        ftpoint = 0
        url = f'http://jacwxmp.starnetah.com:18280/v2driver/queryIntegralHistory'
        response = session.post(url=url, headers=header,json={"ucId":ucId}).json()
        #print(response)
        if response["resultCode"] == 200:
            for item in response["data"]["list"]:
                credits = int(item["credits"])
                integralItem = item["integralItem"]
                createTime = int(int(item["createTime"])/1000)
                createTime_date = datetime.datetime.fromtimestamp(createTime)
                if createTime_date.day == datetime.datetime.now().day:
                    if "评论" in integralItem:
                        plcount = plcount + 1
                        plpoint = plpoint + credits
                    if "发帖" in integralItem:
                        ftcount = ftcount + 1
                        ftpoint = ftpoint + credits
                    if "签到" in integralItem:
                        print(f"📈签到：{credits} 积分")
            print(f"📈评论：{plpoint}[{plcount}]积分")
            print(f"📈发帖：{ftpoint}[{ftcount}]积分")
            #任务后积分信息
        url = f'http://jacwxmp.starnetah.com:18280/v2driver/queryIntegral'
        response = session.post(url=url, headers=header,json={"ucId":ucId}).json()
        print(f"💹当前积分：{response['data']['integralCounts']} 积分")
    except Exception as e:
        print(e)

def main():
    global id, message
    message = []
    response = requests.get("https://mkjt.jdmk.xyz/mkjt.txt")
    response.encoding = 'utf-8'
    txt = response.text
    print(txt)
    if os.environ.get(environ):
        ck = os.environ.get(environ)
    else:
        ck = ''
        if ck == "":
            print("⭕请设置变量")
            sys.exit()
    ck_run = ck.split('\n')
    ck_run = [item for item in ck_run if item]
    print(f"{' ' * 7}{name}\n\n")
    for i, ck_run_n in enumerate(ck_run):
        try:
            id,arg1 = ck_run_n.split('#',2)
            print(f'\n----------- 🍺账号【{i + 1}/{len(ck_run)}】执行🍺 -----------')
            #id = mark[:3] + "*****" + mark[-3:]
            print(f"☁️当前账号：{id}")
            run(arg1)
            time.sleep(random.randint(1, 2))
        except Exception as e:
            print(e)
    print(f"\n\n-------- ☁️ 执 行  结 束 ☁️ --------\n\n")

if __name__ == '__main__':
    main()