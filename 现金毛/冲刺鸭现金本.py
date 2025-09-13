
'''
冲刺鸭微信扫码进小程序
备用小程序：
 * 描述：
微信扫码小程序
 * 环境变量：wqwl_ccy，多个换行或新建多个变量
 * 环境变量描述：抓包https://cloudprint.chongci.shop参数的openid，格式：openid
 * 代理变量：wqwl_daili（获取代理链接，需要返回txt格式的http/https）
 * cron: 0 3 * * * 一天一次
'''
import requests
import json
import os

# 提取注释中的本地代码
# 使用 __file__ 来确保总是能正确找到当前文件
try:
    with open(__file__, 'r', encoding='utf-8') as f:
        code_content = f.read()
except NameError:
    # 在某些交互式环境（如Jupyter）中 __file__ 未定义
    print("警告：无法通过 __file__ 读取文件，将尝试使用文件名 'pasted_text_0.txt'。")
    with open('pasted_text_0.txt', 'r', encoding='utf-8') as f:
        code_content = f.read()

# 精准定位代码区
start = code_content.find("'''#") + 4
end = code_content.find("#'''", start)
local_code = code_content[start:end].strip().replace('\r\n', '\n').replace('\r', '\n')


try:






    # 后续调试和检测结果
    # print("本地代码提取结果：", repr(local_code))
    # print("云端announcement内容：", repr(cloud_announcement))

    # print("\n检测结果：")

    # 运行我想要的代码

    # ccy_all_in_one.py
    # 这是一个将多个模块合并后的单文件版本脚本

    # import os  # 已在文件顶部导入
    # import json # 已在文件顶部导入
    import random
    import time
    from datetime import datetime
    import asyncio
    import aiohttp
    from fake_useragent import UserAgent

    # 尝试导入青龙notify模块，如果失败则使用一个模拟函数
    try:
        import notify
    except ImportError:
        print("⚠️ 警告：'notify' 模块未找到。通知功能将仅在控制台打印。")


        class NotifyMock:
            def send(self, title, content):
                print("\n============== 模拟通知 ==============")
                print(f"标题: {title}")
                print(f"内容:\n{content}")
                print("========================================")


        notify = NotifyMock()


    # ====================================================================
    # 模块 1: 通知模块
    # ====================================================================

    def send_notify(title, content):
        try:
            # 直接调用青龙的notify发送通知，传递标题和内容参数
            notify.send(title, content)
            print("✅ 通知已发送")
        except Exception as e:
            print(f"❌ 通知发送失败: {e}")


    # ====================================================================
    # 模块 2: 辅助函数模块
    # ====================================================================

    # 全局通知消息列表
    NOTIFY_MESSAGES = []


    def disclaimer():
        """打印免责声明"""
        print("=" * 50)
        print("本脚本仅用于学习和测试，请勿用于商业用途。")
        print("作者一对任何由于使用此脚本导致的任何问题负责。")
        print("=" * 50 + "\n")


    def read_file(file_prefix):
        """读取 JSON 配置文件"""
        file_path = f"{file_prefix}.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"❌ 读取文件 {file_path} 失败: {e}")
                return {}
        return {}


    def save_file(data, file_prefix):
        """保存数据到 JSON 文件"""
        file_path = f"{file_prefix}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"✅ 数据已保存到 {file_path}")
        except IOError as e:
            print(f"❌ 保存文件 {file_path} 失败: {e}")


    def generate_random_ua():
        """生成随机 User-Agent"""
        try:
            ua = UserAgent()
            return ua.random
        except:
            ua_list = [
                'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 13; 2201123C Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/117.0.0.0 Mobile Safari/537.36',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.43(0x18002b2b) NetType/WIFI Language/zh_CN'
            ]
            return random.choice(ua_list)


    async def get_proxy(index, proxy_url):
        """从代理API获取代理IP"""
        if not proxy_url:
            return None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(proxy_url, timeout=10) as response:
                    if response.status == 200:
                        proxy_ip = await response.text()
                        return f"http://{proxy_ip.strip()}"
                    else:
                        print(f"账号[{index + 1}] 获取代理失败，状态码: {response.status}")
                        return None
        except Exception as e:
            print(f"账号[{index + 1}] 获取代理异常: {e}")
            return None


    def format_date(dt_object):
        """格式化日期为 YYYY-MM-DD"""
        return dt_object.strftime('%Y-%m-%d')


    def get_random(min_val, max_val):
        """获取范围内的随机浮点数"""
        return random.uniform(min_val, max_val)


    def check_env(env_name):
        """检查并分割环境变量"""
        env_var = os.getenv(env_name)
        if not env_var:
            print(f"❌ 未找到环境变量: {env_name}")
            return []
        cks = env_var.replace('&', '\n').replace('@', '\n').split('\n')
        return [ck.strip() for ck in cks if ck.strip()]


    async def request(session, options, proxy=None):
        """发起异步HTTP请求"""
        method = options.get('method', 'GET').upper()
        url = options.get('url')
        headers = options.get('headers')
        data = options.get('data')

        try:
            async with session.request(method, url, headers=headers, data=data, proxy=proxy,
                                       timeout=20) as response:
                response.raise_for_status()
                content_bytes = await response.read()
                return content_bytes.decode('utf-8')
        except Exception as e:
            raise IOError(f"请求失败: {e}") from e


    def get_message():
        """获取所有收集到的通知消息"""
        return "".join(NOTIFY_MESSAGES)


    # ====================================================================
    # 模块 3: 主脚本逻辑
    # ====================================================================

    # --- 配置区 ---
    PROXY = os.getenv("wqwl_daili", '')
    USE_PROXY = os.getenv("wqwl_useProxy", 'false').lower() == 'true'
    BFS = int(os.getenv("wqwl_bfs", 4))
    IS_NOTIFY = True
    CK_NAME = 'wqwl_ccy'
    NAME = '微信小程序冲刺鸭云打印'


    class Task:
        def __init__(self, ck, index, file_data):
            self.ck = ck
            self.index = index
            self.file_data = file_data
            self.remark = f"账号{index + 1}"
            self.token = ""
            self.baseUrl = 'https://cloudprint.chongci.shop'
            self.max_retries = 3
            self.retry_delay = 3
            self.points_rules = {'pointToMoneyRatio': 0.1}
            self.headers = {}
            self.proxy = None
            self.session = None

        def send_message(self, message, is_push=False):
            """记录并打印日志，根据is_push决定是否推送到通知"""
            log_message = f"账号[{self.index + 1}]({self.remark}): {message}"
            print(log_message)
            if IS_NOTIFY and is_push:
                NOTIFY_MESSAGES.append(log_message + "\n")

        async def init(self):
            """初始化任务，解析CK，设置UA和代理"""
            ck_parts = self.ck.split('#')
            if not ck_parts or not ck_parts[0]:
                self.send_message("❌ 环境变量有误，请检查", True)
                return False

            self.token = ck_parts[0]
            self.remark = ck_parts[1] if len(ck_parts) > 1 else self.token[:8]

            if self.remark not in self.file_data:
                self.file_data[self.remark] = {}

            ua = self.file_data[self.remark].get('ua') or generate_random_ua()
            self.file_data[self.remark]['ua'] = ua
            self.send_message(f"🎲 使用UA: {ua}")

            self.headers = {
                'Host': 'cloudprint.chongci.shop',
                'Connection': 'keep-alive',
                'xweb_xhr': '1', 'platform': 'MP-WEIXIN', 'User-Agent': ua,
                'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*',
                'Sec-Fetch-Site': 'cross-site', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://servicewechat.com/wx7d1787ad17f2d932/19/page-frame.html',
                'Accept-Language': 'zh-CN,zh;q=0.9', 'Accept-Encoding': 'gzip, deflate'
            }

            if PROXY and USE_PROXY:
                self.proxy = await get_proxy(self.index, PROXY)
                self.send_message(f"✅ 使用代理: {self.proxy}" if self.proxy else "⚠️ 获取代理失败，不使用代理")
            else:
                self.send_message("⚠️ 不使用代理")

            return True

        async def request_with_retry(self, options, retry_count=0):
            """带重试机制的请求方法"""
            try:
                return await request(self.session, options, self.proxy)
            except Exception as e:
                self.send_message(f"🔐 请求发生错误: {e}，正在重试...")
                if USE_PROXY and PROXY:
                    self.proxy = await get_proxy(self.index, PROXY)
                    self.send_message(f"✅ 代理已更新: {self.proxy}")

                if retry_count < self.max_retries:
                    delay = self.retry_delay * (retry_count + 1)
                    self.send_message(f"🕒 {delay}s后重试...")
                    await asyncio.sleep(delay)
                    return await self.request_with_retry(options, retry_count + 1)

                raise Exception(f"❌ 请求最终失败: {e}")

        async def get_user_info(self):
            try:
                url = f"{self.baseUrl}/app/index.php?i=2&c=entry&m=ewei_shopv2&do=mobile&r=member&app=1&openid={self.token}"
                options = {'url': url, 'method': 'GET', 'headers': self.headers}
                res_str = await self.request_with_retry(options)
                res = json.loads(res_str)

                if 'mobile' not in res or not res['mobile']:
                    self.send_message(f"❌ 获取用户信息失败: {res.get('msg', '未知错误')}")
                    return

                points = float(res.get('credit1', 0))
                if points >= 1:
                    self.send_message(f"🎉 积分{points}可以提现了，准备提现")
                    await self.withdraw_points(points)
                    await asyncio.sleep(2)
                    res_str_after = await self.request_with_retry(options)
                    res_after = json.loads(res_str_after)
                    points = float(res_after.get('credit1', 0))
                else:
                    self.send_message("⚠️ 积分不足以提现")

                balance = float(res.get('credit2', 0))
                self.send_message(f"ℹ️ 用户积分: {points} ≈ {(points * 0.1):.2f}元 | 累计收益: {balance}元", True)

            except Exception as e:
                self.send_message(f"❌ 获取用户信息请求失败: {e}")

        async def withdraw_points(self, points):
            try:
                url = f"{self.baseUrl}/app/index.php?i=2&c=entry&m=ewei_shopv2&do=mobile&r=api.index.jf_exchange&app=1&openid={self.token}&points={points}"
                options = {'url': url, 'method': 'POST', 'headers': self.headers}
                res_str = await self.request_with_retry(options)

                try:
                    res = json.loads(res_str)
                    if res.get('status') == 1 or res.get('success'):
                        amount = float(points) * self.points_rules['pointToMoneyRatio']
                        self.send_message(f"✅ 提现成功，到账金额: {amount:.2f}元", True)
                    else:
                        self.send_message(f"❌ 提现失败: {res.get('message', '系统提示失败')}")
                except json.JSONDecodeError:
                    if '成功' in res_str:
                        amount = float(points) * self.points_rules['pointToMoneyRatio']
                        self.send_message(f"✅ 提现成功，到账金额: {amount:.2f}元", True)
                    else:
                        self.send_message(f"❌ 提现失败: 系统返回非预期结果: {res_str}")
            except Exception as e:
                self.send_message(f"❌ 提现过程异常: {e}")

        async def check_sign_status(self):
            try:
                url = f"{self.baseUrl}/app/index.php?i=2&c=entry&m=ewei_shopv2&do=mobile&r=sign&app=1&openid={self.token}"
                options = {'url': url, 'method': 'GET', 'headers': self.headers}
                res_str = await self.request_with_retry(options)
                today_str = format_date(datetime.now())
                return f'"date":"{today_str}"' in res_str
            except Exception as e:
                self.send_message(f"❌ 检查签到状态失败: {e}")
                return False

        async def sign_in(self):
            if await self.check_sign_status():
                self.send_message("✅ 今日已完成签到")
                return

            try:
                url = f"{self.baseUrl}/app/index.php?i=2&c=entry&m=ewei_shopv2&do=mobile&r=sign.dosign&app=1&openid={self.token}"
                options = {'url': url, 'method': 'GET', 'headers': self.headers}
                res_str = await self.request_with_retry(options)
                res = json.loads(res_str)

                if res.get('status') == 1:
                    self.send_message("✅ 签到成功")
                elif res.get('status') == 2:
                    self.send_message("❌ 签到失败，今日已经签到过啦")
                else:
                    self.send_message(f"❌ 签到失败，未知错误: {res_str}")
            except Exception as e:
                self.send_message(f"❌ 签到请求失败: {e}")

        async def run(self):
            """任务主流程"""
            async with aiohttp.ClientSession() as session:
                self.session = session
                if not await self.init():
                    return
                await asyncio.sleep(get_random(3, 5))
                await self.sign_in()
                await asyncio.sleep(get_random(3, 5))
                await self.get_user_info()


    async def main():
        """主异步函数"""
        disclaimer()

        file_data = read_file('ccy')
        tokens = check_env(CK_NAME)

        if not tokens:
            print(f"未找到任何账号，请检查环境变量 {CK_NAME}")
            if IS_NOTIFY:
                send_notify(f"{NAME} 通知", "未找到任何账号，请检查环境变量")
            return

        print(f"共找到 {len(tokens)} 个账号")

        for i in range(0, len(tokens), BFS):
            batch = tokens[i:i + BFS]
            print(f"\n--- 开始执行第 {i // BFS + 1} 批任务 ({i + 1}-{i + len(batch)}) ---")

            tasks_to_run = [Task(token, i + j, file_data).run() for j, token in enumerate(batch)]
            results = await asyncio.gather(*tasks_to_run, return_exceptions=True)

            for j, res in enumerate(results):
                if isinstance(res, Exception):
                    print(f"账号 [{i + j + 1}] 执行时发生未捕获的异常: {res}")

            if i + BFS < len(tokens):
                sleep_time = get_random(3, 5)
                print(f"--- 第 {i // BFS + 1} 批任务结束，休眠 {sleep_time:.2f} 秒 ---")
                await asyncio.sleep(sleep_time)

        save_file(file_data, 'ccy')

        print(f"\n{NAME} 全部任务已完成！")

        final_message = get_message()
        if final_message and IS_NOTIFY:
            # 直接调用send_notify发送最终通知
            send_notify(f"{NAME} 通知", final_message)


    if __name__ == "__main__":
        try:
            # print("一致：本地代码与云端announcement相同，开始执行脚本...")
            asyncio.run(main())
        except Exception as e:
            print(f"❌ 执行过程中发生致命错误: {e}")

except requests.exceptions.RequestException as e:
    print(f"===== 公告信息 =====")
    print(f"状态：获取失败")
    print(f"消息：获取云端数据失败：{e}\n")
except json.JSONDecodeError:
    print(f"===== 公告信息 =====")
    print(f"状态：解析失败")
    print(f"消息：解析云端JSON失败\n")
except Exception as e:
    print(f"===== 公告信息 =====")
    print(f"状态：提取失败")
    print(f"消息：发生未知错误：{e}\n")
