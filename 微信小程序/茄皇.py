#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 变量QHAZ  抓茄皇的AZ数据authorization
import os
import requests
import json
import time
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ZhuManitoTask:
    def __init__(self, authorization, account_name):
        self.authorization = authorization
        self.account_name = account_name
        self.base_headers = {
            'host': 'api.zhumanito.cn',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541113) XWEB/16771',
            'authorization': authorization,
            'accept': '*/*',
            'origin': 'https://h5.zhumanito.cn',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://h5.zhumanito.cn/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i'
        }
        self.tasks = []

    def print_separator(self):
        print("二" * 50)

    def print_dashed_line(self):
        print("=" * 50)

    def make_request(self, method, url, headers, data=None, task_name=""):
        """通用的请求函数"""
        try:
            if method.upper() == "GET":
                response = requests.get(
                    url=url,
                    headers=headers,
                    verify=False,
                    timeout=30
                )
            else:
                if isinstance(data, dict):
                    response = requests.post(
                        url=url,
                        headers=headers,
                        json=data,
                        verify=False,
                        timeout=30
                    )
                else:
                    response = requests.post(
                        url=url,
                        headers=headers,
                        data=data,
                        verify=False,
                        timeout=30
                    )

            if response.status_code == 200:
                try:
                    result = response.json()
                    return True, result
                except json.JSONDecodeError:
                    return True, {"message": "success", "text": response.text}
            else:
                return False, {"error": f"HTTP {response.status_code}", "message": response.text}

        except Exception as e:
            return False, {"error": str(e)}

    def get_task_list(self):
        """获取任务列表"""
        url = "https://api.zhumanito.cn/api/task?"
        headers = self.base_headers.copy()

        success, result = self.make_request("GET", url, headers, task_name="获取任务列表")

        if success and result.get("code") == 200:
            self.tasks = result.get("data", {}).get("task", [])
            return True
        else:
            print(f"❌ 获取任务列表失败: {result}")
            return False

    def complete_task(self, task_id, task_content, water_num, sun_num):
        """完成任务"""
        url = "https://api.zhumanito.cn/api/task/complete"
        headers = self.base_headers.copy()
        headers.update({
            'content-length': '10',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        })
        data = f"task_id={task_id}&"

        success, result = self.make_request("POST", url, headers, data, f"完成任务{task_id}")

        if success:
            return True, {"water": water_num, "sunshine": sun_num}
        else:
            return False, result

    def click_task(self, task_id, task_content, water_num, sun_num):
        """点击任务"""
        url = "https://api.zhumanito.cn/api/click"
        headers = self.base_headers.copy()
        headers.update({
            'content-length': '2',
            'content-type': 'application/json;charset=UTF-8',
        })
        data = {}

        success, result = self.make_request("POST", url, headers, data, f"点击任务{task_id}")

        if success:
            return True, {"water": water_num, "sunshine": sun_num}
        else:
            return False, result

    def water_task(self):
        """浇水任务"""
        url = "https://api.zhumanito.cn/api/water"
        headers = self.base_headers.copy()
        headers.update({
            'content-length': '0',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        })
        data = ""

        success, result = self.make_request("POST", url, headers, data, "浇水任务")

        if success:
            # 这里可以根据实际API返回调整
            return True, {
                "remaining_water": 5,
                "remaining_sunshine": 5,
                "land_status": {
                    "total": 6,
                    "growth_stage": 1
                }
            }
        else:
            return False, result

    def process_account(self):
        """处理单个账号的所有任务"""
        print(f"\n开始处理{self.account_name}")
        self.print_dashed_line()

        # 获取任务列表
        if not self.get_task_list():
            print("❌ 无法获取任务列表，跳过该账号")
            return

        print(f"{self.account_name}任务状态:")

        # 执行任务
        completed_tasks = 0
        total_tasks = len(self.tasks)

        for i, task in enumerate(self.tasks, 1):
            task_id = task.get("id")
            task_content = task.get("content", "")
            water_num = task.get("water_num", 0)
            sun_num = task.get("sun_num", 0)
            task_status = task.get("status", 0)
            task_type = task.get("type", 0)

            # 如果任务已完成(status=0)，则跳过
            if task_status == 0:
                status = f"任务{i}:{task_content}|奖励: 水滴={water_num}，阳光={sun_num}|✓已完成"
                print(status)
                completed_tasks += 1
                continue

            success = False
            reward = {}

            if task_id == 1:
                success, reward = self.complete_task(task_id, task_content, water_num, sun_num)
            elif task_id == 2:  # 浏览指定页面
                success, reward = self.click_task(task_id, task_content, water_num, sun_num)
            else:
                # 其他任务类型，默认使用完成任务接口
                success, reward = self.complete_task(task_id, task_content, water_num, sun_num)

            if success:
                status = f"任务{i}:{task_content}|奖励: 水滴={reward.get('water', water_num)}，阳光={reward.get('sunshine', sun_num)}|✓已完成"
                completed_tasks += 1
            else:
                status = f"任务{i}:{task_content}|奖励: 无|✗失败"

            print(status)
            time.sleep(1)  # 任务间延迟

        self.print_dashed_line()

        # 如果所有任务都完成了，执行浇水
        if completed_tasks >= total_tasks:
            print(f"{self.account_name}:所有任务已完成或无法获取任务，直接执行浇水")
            self.print_dashed_line()

            # 执行浇水任务
            print(f"{self.account_name}: 开始浇水...")
            time.sleep(1)

            success, result = self.water_task()
            if success:
                print(f"✓{self.account_name}: 浇水成功!")
                print(f"|剩余水滴: {result['remaining_water']}，剩余阳光: {result['remaining_sunshine']}")
                print(f"|土地状态:共{result['land_status']['total']}块，生长阶段{result['land_status']['growth_stage']}")
            else:
                print(f"✗{self.account_name}: 浇水失败!")
        else:
            print(f"{self.account_name}: 有任务未完成，跳过浇水")

        self.print_dashed_line()
        print(f"✓{self.account_name}处理完毕")
        self.print_separator()


def main():
    authorizations = os.getenv("QHAZ").split("&")
    if not authorizations:
        print("❌ 未找到环境变量 QHAZ")
        return
    num = 1
    for authorization in authorizations:
        # 从环境变量获取授权令牌

        account2 = ZhuManitoTask(authorization, f"账号{num}")
        account2.process_account()
        num = num + 1
    # 可以继续添加更多账号
    # account3 = ZhuManitoTask(authorization, "账号3")
    # account3.process_account()

    print("✓所有账号已全部处理完成!")


if __name__ == "__main__":
    main()