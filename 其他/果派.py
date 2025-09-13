import os
import json
import time
import requests


class Run:
    def __init__(self, openid, task_id):
        self.TaskId = task_id
        self.openid = openid
        self.token = ''
        self.header = {
            'Host': 'api.vip.xvnn.cn',
            'Connection': 'keep-alive',
            'Content-Length': '84',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090719) XWEB/8431 Flue',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Origin': 'https://fqzw0h.vip.xvnn.cn',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://fqzw0h.vip.xvnn.cn/',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }

    def do_post(self, url, data):
        response = requests.post(url=url, data=json.dumps(data), headers=self.header)
        return response.json()

    def do_get(self, url):
        response = requests.get(url=url, headers=self.header, timeout=5)
        return response.json()
    def task_ok(self):
        # 获取userActivityId
        url = f'http://api.vip.xvnn.cn/api-user/v2/activityDetatil?id={self.TaskId}&withMaterial=1'
        response = self.do_get(url=url)
        if response["status"] == 'success':
            userActivityId = response["meta"]["joinInfo"]["userActivityId"]
            activity_id = response["data"]['activity_id']
            question = response["data"]["materialDetail"]["questions"][0]["question"]
            answers = response["data"]["materialDetail"]["questions"][0]["answer"]
            for index, answer in enumerate(answers):
                if answer["result"] == "1":
                    item = index
                    break
            right_answer_text = "0_" + str(item)
            right_answer = [right_answer_text]
            print(f"本期答题得题目为: {question}, 正确答案为: {right_answer}")
            print(f"获取到了userActivityId为{userActivityId}, activity_id为{activity_id}")
            time.sleep(1)
            url = 'https://api.vip.xvnn.cn/api-user/v1/activityWatchVideoOver'
            body ={"userActivityId":userActivityId}
            response = self.do_post(url=url, data=body)
            if response["status"] == 'success':
                print("观看视频成功，1S后领取奖励")
                time.sleep(1)
                url = "https://api.vip.xvnn.cn/api-user/v1/receiveAwardAndWatchOver"
                body = {"activity_id": activity_id, "answers": right_answer}
                response = self.do_post(url=url, data=body)
                if response["status_code"] == 200:
                    money = response["data"]["red_money"]
                    print(f"领取奖励成功->{money}")
                else:
                    print(f"领取奖励失败->{response}")
            else:
                print("观看视频失败")
        else:
            print("获取参数失败了")

        pass

    def do_task(self):
        # 登录获取token
        url = "https://api.vip.xvnn.cn/api-user/v2/getToken"
        body = {
            "wx_openid": self.openid,
            "id": self.TaskId
        }
        response = self.do_post(url=url, data=body)
        if response["status"] == 'success':
            data = response["data"]
            self.token = data["token"]
            self.header["Authorization"] = 'Bearer ' + self.token
            print(f"获取到了token->{self.token}")
            self.task_ok()
        else:
            print("获取token失败")

if __name__ == '__main__':
    # openid
    users = os.environ.get("GuoUser")
    task_id = os.environ.get("GuoTaskId")
    # users = 'ojF6x6r86Ap-QMigu_Ia6NhQ-yps' + "\n" + "ojF6x6uvbWNHCMFQYZDaKIrb6i_A"
    # task_id = '3ef20677234150b7dca48ab44056ec6d'
    print("免费脚本发布QQ群:575922391 ")
    if users:
        user_list = users.split("\n")
        for openid in user_list:
            run = Run(openid=openid, task_id=task_id).do_task()
    else:
        print("暂未识别出用户信息")
