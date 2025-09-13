import requests
import random
import time
import json
import threading
from queue import Queue


#牛牛短剧APP 抓包抓token和deviceId值填到下方运行即可。
# 多用户配置列表
USERS = [
    {
        "token": "XpmJF7eh8F8NeWB63w8reEiu",
        "deviceId": "74315e49cbc043ae8",
        "name": "账号1"
    }#,
    #{
        #"token": "CLZ4P2GnLlnNDH4=",
        #"deviceId": "def6e6202c256273",
        #"name": "账号2"
    #}
    # 可以按上面格式添加更多用户...
]

# 基础配置
BASE_URL = 'https://new.tianjinzhitongdaohe.com/api/v1/app'
COMMON_DATA = {"pageSize": "15"}

class UserSession:
    """用户会话类，封装单个用户的所有操作"""
    def __init__(self, user_config):
        self.name = user_config["name"]
        self.token = user_config["token"]
        self.deviceId = user_config["deviceId"]
        self.headers = self._create_headers()
        self.last_treasure_time = 0
        
    def _create_headers(self):
        """创建用户特定的请求头"""
        return {
            'User-Agent': 'niu niu duan ju/1.5.8 (iPhone; iOS 16.6; Scale/3.00)',
            'Content-Type': 'application/json',
            'deviceType': 'iOS',
            'Accept-Language': 'zh-Hans-CN;q=1',
            'token': self.token,
            'deviceId': self.deviceId,
            'client': 'app',
            'Cookie': 'JSESSIONID=767F1CFB5FB471A4F2871314C74F14B6'
        }
    
    def make_request(self, url, data=None, method='POST', params=None):
        """通用请求函数"""
        try:
            if method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, params=params)
            else:
                response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[{self.name}] 请求失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"[{self.name}] 请求异常: {str(e)}")
            return None
    
    def sign_in(self):
        """每日签到"""
        url = f'{BASE_URL}/welfare/sign'
        return self.make_request(url, data=COMMON_DATA)
    
    def check_repair_sign(self):
        """检查补签需求"""
        url = f'{BASE_URL}/welfare/list'
        return self.make_request(url, data=COMMON_DATA)
    
    def repair_sign(self, config_id):
        """执行补签"""
        time.sleep(5)
        url = f'{BASE_URL}/welfare/repairSign?configId={config_id}'
        return self.make_request(url, data=COMMON_DATA)
    
    def watch_ad(self, times=20, interval=5):
        """看视频领金币"""
        results = []
        data = {
            "adId": "58274289-127E-48FF-910F-9B96118908F3u2283",
            "pageSize": "15"
        }
        
        for i in range(times):
            url = f'{BASE_URL}/welfare/watchAd'
            result = self.make_request(url, data=data)
            results.append(result)
            
            if i < times - 1:
                time.sleep(interval)
        
        return results
    
    def watch_drama(self):
        """看短剧领金币"""
        url = f'{BASE_URL}/play/historyMovie'
        data = {
            "id": 77834,
            "typeId": "S1",
            "watchDuration": 3600,
            "pageSize": "15",
            "episode": ""
        }
        return self.make_request(url, data=data)
    
    def sign_eat(self):
        """吃饭看剧补贴"""
        url = f'{BASE_URL}/welfare/signEat'
        return self.make_request(url, data=COMMON_DATA)
    
    def repair_sign_eat(self, config_id):
        """吃饭看剧补领"""
        time.sleep(5)
        url = f'{BASE_URL}/welfare/repairSignEat?configId={config_id}'
        return self.make_request(url, data=COMMON_DATA)
    
    def open_treasure(self):
        """开宝箱"""
        url = f'{BASE_URL}/welfare/treasureOpen'
        return self.make_request(url, data=COMMON_DATA)
    
    def new_user_seven(self):
        """新用户奖励"""
        url = f'{BASE_URL}/welfare/newUserSeven'
        return self.make_request(url, data=COMMON_DATA)
    
    def praise_movie(self, times=2):
        """点赞剧集"""
        results = []
        for _ in range(times):
            url = f'{BASE_URL}/play/praiseMovie'
            data = {
                "movieId": random.randint(1, 70000),
                "typeId": "S1",
                "episodeIndex": 0,
                "source": 0,
                "pageSize": "15",
                "action": "1"
            }
            results.append(self.make_request(url, data=data))
        return results
    
    def collect_movie(self, times=2):
        """收藏剧集"""
        results = []
        for _ in range(times):
            url = f'{BASE_URL}/play/collectMovie'
            data = {
                "id": random.randint(1, 70000),
                "typeId": "S1",
                "pageSize": "15",
                "action": "1"
            }
            results.append(self.make_request(url, data=data))
        return results
    
    def share_movie(self, times=2):
        """分享剧集"""
        results = []
        for _ in range(times):
            time.sleep(3)
            movie_id = random.randint(1, 70000)
            url = f'{BASE_URL}/welfare/addShare?typeId=S1&movieId={movie_id}'
            results.append(self.make_request(url, data=COMMON_DATA))
        return results
    
    def process_sign_repair(self, check_result):
        """处理签到补签逻辑"""
        if not check_result or 'data' not in check_result:
            print(f"[{self.name}] 未获取到有效的补签检查结果")
            return
        
        # 查找每日签到任务
        sign_task = None
        for task in check_result['data']:
            if task.get('flag') == 'SIGN':
                sign_task = task
                break
        
        if sign_task and 'taskList' in sign_task:
            for task_item in sign_task['taskList']:
                if task_item.get('isDone') is False:
                    config_id = task_item.get('configId')
                    if config_id:
                        print(f"[{self.name}] 发现需要补签的任务: {task_item.get('number')}天")
                        repair_result = self.repair_sign(config_id)
                        if repair_result and repair_result.get('code') == 200:
                            print(f"[{self.name}] 补签成功 (configId={config_id}): {repair_result.get('msg')}")
                        else:
                            print(f"[{self.name}] 补签失败 (configId={config_id}): {repair_result.get('msg') if repair_result else '未知错误'}")
                    else:
                        print(f"[{self.name}] 未找到有效的configId")
    
    def process_eat_repair(self, check_result):
        """处理吃饭看剧补贴补领逻辑"""
        if not check_result or 'data' not in check_result:
            print(f"[{self.name}] 未获取到有效的补签检查结果")
            return
        
        # 查找吃饭看剧补贴任务
        eat_task = None
        for task in check_result['data']:
            if task.get('flag') == 'WATCH_EAT_COIN':
                eat_task = task
                break
        
        if eat_task and 'taskList' in eat_task:
            for task_item in eat_task['taskList']:
                if task_item.get('isDone') is False and task_item.get('isReceive') is False:
                    config_id = task_item.get('configId')
                    if config_id:
                        print(f"[{self.name}] 发现需要补领的吃饭看剧补贴任务: 时段{task_item.get('number')}")
                        repair_result = self.repair_sign_eat(config_id)
                        if repair_result and repair_result.get('code') == 200:
                            print(f"[{self.name}] 吃饭补贴补领成功 (configId={config_id}): {repair_result.get('msg')}")
                        else:
                            print(f"[{self.name}] 吃饭补贴补领失败 (configId={config_id}): {repair_result.get('msg') if repair_result else '未知错误'}")
                    else:
                        print(f"[{self.name}] 未找到有效的configId")
    
    def auto_sign(self):
        """自动签到完整流程"""
        print(f"[{self.name}] {'='*50}")
        print(f"[{self.name}] 开始执行自动签到任务")
        print(f"[{self.name}] {'='*50}")
        
        # 1. 执行签到
        print(f"[{self.name}] >>> 执行每日签到")
        sign_result = self.sign_in()
        if sign_result and sign_result.get('code') == 200:
            print(f"[{self.name}] 签到成功: {sign_result.get('msg')}")
        else:
            print(f"[{self.name}] 签到失败: {sign_result.get('msg') if sign_result else '请求失败'}")
        
        # 2. 检查补签需求
        print(f"[{self.name}] >>> 检查补签需求")
        check_result = self.check_repair_sign()
        
        # 3. 处理签到补签
        if check_result and check_result.get('code') == 200:
            print(f"[{self.name}] 补签检查结果获取成功")
            self.process_sign_repair(check_result)
            self.process_eat_repair(check_result)
        else:
            print(f"[{self.name}] 补签检查失败: {check_result.get('msg') if check_result else '请求失败'}")
        
        # 4. 看视频领金币
        print(f"[{self.name}] >>> 开始看视频领金币 (20次)")
        ad_results = self.watch_ad(times=20, interval=5)
        success_count = sum(1 for r in ad_results if r and r.get('code') == 200)
        print(f"[{self.name}] 看视频完成: 成功 {success_count}/20 次")
        
        # 5. 看短剧
        print(f"[{self.name}] >>> 看短剧领金币")
        drama_result = self.watch_drama()
        if drama_result and drama_result.get('code') == 200:
            print(f"[{self.name}] 看短剧成功: {drama_result.get('msg')}")
        else:
            print(f"[{self.name}] 看短剧失败: {drama_result.get('msg') if drama_result else '请求失败'}")
        
        # 6. 吃饭补贴
        print(f"[{self.name}] >>> 吃饭看剧补贴")
        eat_result = self.sign_eat()
        if eat_result and eat_result.get('code') == 200:
            print(f"[{self.name}] 吃饭补贴成功: {eat_result.get('msg')}")
        else:
            print(f"[{self.name}] 吃饭补贴失败: {eat_result.get('msg') if eat_result else '请求失败'}")
        
        # 7. 开宝箱
        print(f"[{self.name}] >>> 开启宝箱")
        treasure_result = self.open_treasure()
        if treasure_result and treasure_result.get('code') == 200:
            print(f"[{self.name}] 宝箱开启成功: {treasure_result.get('msg')}")
        else:
            print(f"[{self.name}] 宝箱开启失败: {treasure_result.get('msg') if treasure_result else '请求失败'}")
        self.last_treasure_time = time.time()
        
        # 8. 新用户奖励
        print(f"[{self.name}] >>> 新用户奖励")
        new_user_result = self.new_user_seven()
        if new_user_result and new_user_result.get('code') == 200:
            print(f"[{self.name}] 新用户奖励成功: {new_user_result.get('msg')}")
        else:
            print(f"[{self.name}] 新用户奖励失败: {new_user_result.get('msg') if new_user_result else '请求失败'}")
        
        # 9. 点赞
        print(f"[{self.name}] >>> 点赞剧集 (2次)")
        praise_results = self.praise_movie(times=2)
        success_count = sum(1 for r in praise_results if r and r.get('code') == 200)
        print(f"[{self.name}] 点赞完成: 成功 {success_count}/2 次")
        
        # 10. 收藏
        print(f"[{self.name}] >>> 收藏剧集 (2次)")
        collect_results = self.collect_movie(times=2)
        success_count = sum(1 for r in collect_results if r and r.get('code') == 200)
        print(f"[{self.name}] 收藏完成: 成功 {success_count}/2 次")
        
        # 11. 分享
        print(f"[{self.name}] >>> 分享剧集 (2次)")
        share_results = self.share_movie(times=2)
        success_count = sum(1 for r in share_results if r and r.get('code') == 200)
        print(f"[{self.name}] 分享完成: 成功 {success_count}/2 次")
        
        print(f"[{self.name}] " + "="*50)
        print(f"[{self.name}] 自动签到任务执行完毕")
        print(f"[{self.name}] " + "="*50)

def user_worker(user_config):
    """用户任务线程函数"""
    user = UserSession(user_config)
    
    # 执行主签到任务
    user.auto_sign()
    
    # 持续执行宝箱任务
    while True:
        current_time = time.time()
        if current_time - user.last_treasure_time >= 185:  # 3分钟
            print(f"[{user.name}] {time.strftime('%Y-%m-%d %H:%M:%S')} 执行宝箱任务")
            treasure_result = user.open_treasure()
            if treasure_result and treasure_result.get('code') == 200:
                print(f"[{user.name}] 宝箱开启成功: {treasure_result.get('msg')}")
            else:
                print(f"[{user.name}] 宝箱开启失败: {treasure_result.get('msg') if treasure_result else '请求失败'}")
            user.last_treasure_time = current_time
        
        # 等待一段时间再检查
        time.sleep(30)

def main():
    """主函数，启动多线程处理所有用户"""
    print("启动多用户签到任务...")
    
    # 创建并启动所有用户线程
    threads = []
    for user_config in USERS:
        thread = threading.Thread(target=user_worker, args=(user_config,))
        thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        thread.start()
        threads.append(thread)
        print(f"已启动线程: {user_config['name']}")
    
    # 等待所有线程完成（实际上主线程会一直运行）
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n程序被用户中断，正在退出...")

if __name__ == "__main__":
    main()