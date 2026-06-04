"""

顺丰2026端午活动 - 砸粽子赢金币
Author: 爱学习的呆子 (改造自周年活动脚本)
Version: 1.0.0
Date: 2026-06-04

"""

import hashlib
import json
import os
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
inviteId = ['C6E5C3BDD7624520AB869D2AF9E75D95']

# ==================== 配置常量 ====================
PROXY_TIMEOUT = 15
MAX_PROXY_RETRIES = 5
REQUEST_RETRY_COUNT = 3
CONCURRENT_NUM = int(os.getenv('SFBF', '1'))
if CONCURRENT_NUM > 20:
    CONCURRENT_NUM = 20
elif CONCURRENT_NUM < 1:
    CONCURRENT_NUM = 1

print_lock = Lock()

# 端午活动配置
ACTIVITY_CODE = "DRAGONBOAT_2026"
TOKEN = 'wwesldfs29aniversaryvdld29'  # 与周年活动共用token
SYS_CODE = 'MCS-MIMP-CORE'

# 货币显示名称映射
CURRENCY_NAMES = {'GOLD_COIN': '金币', 'GOLD_ZONGZI': '次数'}

# 端午活动channel和platform
CHANNEL = '26dwapp1'
PLATFORM = 'SFAPP'

# 城市代码（每日礼物需要）
CITY_CODE = '021'

# 需要跳过的任务类型（需要实际操作的）
SKIP_TASK_TYPES = [
    'BUY_ADD_VALUE_SERVICE_PACKET',     # 通过服务套餐寄件
    'SEND_INTERNATIONAL_PACKAGE',       # 寄一单国际件
    'LOOK_BIG_PACKAGE_GET_CASH',        # 寄大件重货
    'SEND_SUCCESS_RECALL',              # 去寄快递
    'CHARGE_NEW_EXPRESS_CARD',          # 充值新速运通全国卡
    'CHARGE_COLLECT_ALL',               # 充值1000元一键集齐
    'OPEN_FAMILY_HOME_MUTUAL',          # 开通家庭8折互寄权益
    'BUY_DRAGONBOAT_LIMITED_PACKET',    # 端午限时券包
]


# ==================== 日志 ====================
class Logger:
    def __init__(self):
        self.messages: List[str] = []
        self.lock = Lock()

    def _log(self, icon: str, msg: str):
        line = f"{icon} {msg}"
        with print_lock:
            print(line)
        with self.lock:
            self.messages.append(line)

    def info(self, msg): self._log('📝', msg)
    def success(self, msg): self._log('✅', msg)
    def warning(self, msg): self._log('⚠️', msg)
    def error(self, msg): self._log('❌', msg)
    def task(self, msg): self._log('🎯', msg)
    def zongzi(self, msg): self._log('🫔', msg)


# ==================== 代理管理器 ====================
class ProxyManager:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def get_proxy(self) -> Optional[Dict[str, str]]:
        try:
            if not self.api_url:
                return None
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                proxy_text = response.text.strip()
                if ':' in proxy_text:
                    proxy = proxy_text if proxy_text.startswith('http') else f'http://{proxy_text}'
                    # 隐藏认证信息用于显示
                    display = proxy
                    if '@' in proxy:
                        parts = proxy.split('@')
                        display = f"http://***:***@{parts[-1]}"
                    with print_lock:
                        print(f"✅ 获取代理: {display}")
                    return {'http': proxy, 'https': proxy}
            with print_lock:
                print(f"❌ 获取代理失败: HTTP {response.status_code}")
            return None
        except Exception as e:
            with print_lock:
                print(f"❌ 获取代理异常: {str(e)[:100]}")
            return None


# ==================== HTTP客户端 ====================
class SFHttpClient:
    def __init__(self, proxy_manager: ProxyManager):
        self.proxy_manager = proxy_manager
        self.session = requests.Session()
        self.session.verify = False

        proxy = self.proxy_manager.get_proxy()
        if proxy:
            self.session.proxies = proxy
        else:
            if self.proxy_manager.api_url:
                with print_lock:
                    print("⚠️ 代理获取失败，将不使用代理")

        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 mediaCode=SFEXPRESSAPP-iOS-ML',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'channel': CHANNEL,
            'platform': PLATFORM,
            'accept-language': 'zh-CN,zh;q=0.9',
        }

    def _generate_sign(self) -> Dict[str, str]:
        timestamp = str(int(round(time.time() * 1000)))
        data = f'token={TOKEN}&timestamp={timestamp}&sysCode={SYS_CODE}'
        signature = hashlib.md5(data.encode()).hexdigest()
        return {
            'sysCode': SYS_CODE,
            'timestamp': timestamp,
            'signature': signature,
        }

    def request(self, url: str, data: Optional[Dict] = None, method: str = 'POST') -> Optional[Dict]:
        retry_count = 0
        proxy_retry_count = 0

        while proxy_retry_count < MAX_PROXY_RETRIES:
            # 每次请求重新生成签名
            sign_data = self._generate_sign()
            headers = {**self.headers, **sign_data}

            try:
                if method == 'POST':
                    resp = self.session.post(url, headers=headers, json=data or {}, timeout=PROXY_TIMEOUT)
                else:
                    resp = self.session.get(url, headers=headers, timeout=PROXY_TIMEOUT)
                resp.raise_for_status()

                try:
                    result = resp.json()
                    if result is None:
                        retry_count += 1
                        if retry_count < REQUEST_RETRY_COUNT:
                            time.sleep(2)
                            continue
                        return None
                    return result
                except (json.JSONDecodeError, ValueError):
                    retry_count += 1
                    if retry_count < REQUEST_RETRY_COUNT:
                        time.sleep(2)
                        continue
                    return None

            except requests.exceptions.RequestException as e:
                retry_count += 1
                error_str = str(e)

                # 代理相关错误，切换代理
                if 'ProxyError' in error_str or 'SSLError' in error_str or 'ConnectionError' in error_str:
                    proxy_retry_count += 1
                    if proxy_retry_count < MAX_PROXY_RETRIES:
                        new_proxy = self.proxy_manager.get_proxy()
                        if new_proxy:
                            self.session.proxies = new_proxy
                        retry_count = 0  # 换代理后重置请求重试计数
                    time.sleep(2)
                    continue

                # 普通请求错误，重试
                if retry_count < REQUEST_RETRY_COUNT:
                    time.sleep(2)
                    continue
                return None

            except Exception:
                return None

        return None

    def login(self, url: str) -> tuple:
        """登录（兼容URL和CK格式）"""
        try:
            decoded_input = unquote(url)
            if decoded_input.startswith('sessionId=') or '_login_mobile_=' in decoded_input:
                cookie_dict = {}
                for item in decoded_input.split(';'):
                    item = item.strip()
                    if '=' in item:
                        k, v = item.split('=', 1)
                        cookie_dict[k] = v
                for k, v in cookie_dict.items():
                    self.session.cookies.set(k, v, domain='mcs-mimp-web.sf-express.com')
                user_id = cookie_dict.get('_login_user_id_', '')
                phone = cookie_dict.get('_login_mobile_', '')
                return (True, user_id, phone) if phone else (False, '', '')
            else:
                self.session.get(unquote(url), headers=self.headers, timeout=PROXY_TIMEOUT)
                cookies = self.session.cookies.get_dict()
                user_id = cookies.get('_login_user_id_', '')
                phone = cookies.get('_login_mobile_', '')
                return (True, user_id, phone) if phone else (False, '', '')
        except Exception as e:
            print(f'登录异常: {str(e)}')
            return False, '', ''


# ==================== 端午活动任务执行器 ====================
class DragonBoatExecutor:
    BASE_URL = 'https://mcs-mimp-web.sf-express.com/mcs-mimp'

    def __init__(self, http: SFHttpClient, logger: Logger, user_id: str):
        self.http = http
        self.logger = logger
        self.user_id = user_id

    # ---------- API 方法 ----------

    def _post(self, path: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """通用POST请求"""
        url = f'{self.BASE_URL}{path}'
        return self.http.request(url, data=data or {})

    def get_activity_index(self) -> Optional[Dict]:
        """获取端午活动首页信息"""
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026IndexService~index')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_task_list(self) -> Optional[List[Dict]]:
        """获取端午活动任务列表"""
        data = {
            "activityCode": ACTIVITY_CODE,
            "channelType": PLATFORM
        }
        resp = self._post('/commonPost/~memberNonactivity~activityTaskService~taskList', data)
        if resp and resp.get('success'):
            return resp.get('obj', [])
        else:
            error_msg = resp.get('errorMessage', '未知错误') if resp else '请求失败'
            self.logger.error(f'获取任务列表失败: {error_msg}')
            return None

    def finish_task(self, task_code: str) -> bool:
        """完成任务（浏览类）"""
        url = f'{self.BASE_URL}/commonRoutePost/memberEs/taskRecord/finishTask'
        data = {"taskCode": task_code}
        resp = self.http.request(url, data=data)
        if resp and resp.get('success'):
            return True
        return False

    def fetch_task_reward(self) -> Optional[Dict]:
        """领取已完成任务的奖励"""
        data = {
            "channelType": PLATFORM,
            "activityCode": ACTIVITY_CODE
        }
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026TaskService~fetchTaskReward', data)
        if resp and resp.get('success'):
            return resp.get('obj', {})
        else:
            error_msg = resp.get('errorMessage', '未知错误') if resp else '请求失败'
            self.logger.warning(f'领取任务奖励失败: {error_msg}')
            return None

    def get_accrued_task_award(self) -> Optional[Dict]:
        """获取累计任务奖励"""
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026TaskService~getAccruedTaskAward')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_task_invite_list(self) -> Optional[Dict]:
        """获取邀请任务列表"""
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026TaskService~taskInviteList')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def query_zongzi_status(self) -> Optional[Dict]:
        """查询粽子状态（含金币、次数余额及累计砸粽次数）
        响应示例:
        {"success":true,"obj":{
            "currentAccountList":[
                {"currency":"GOLD_COIN","totalAmount":1680,"balance":1680},  -> 金币
                {"currency":"GOLD_ZONGZI","totalAmount":6,"balance":3}      -> 次数(砸粽材料)
            ],
            "totalCrushTimes":3
        }}
        """
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026ZongziService~queryStatus')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def crush_zongzi(self) -> Optional[Dict]:
        """砸粽子（抽奖/获得金币）"""
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026ZongziService~crush')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        else:
            error_msg = resp.get('errorMessage', '未知错误') if resp else '请求失败'
            self.logger.error(f'砸粽子失败: {error_msg}')
            return None

    def query_extra_reward_cards(self) -> Optional[Dict]:
        """查询额外奖励卡"""
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026ZongziService~queryExtraRewardCards')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_daily_gift_status(self) -> Optional[Dict]:
        """查询每日礼物状态"""
        data = {"cityCode": CITY_CODE}
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026DailyService~getDailyGiftStatus', data)
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def receive_daily_gift(self) -> Optional[Dict]:
        """领取每日礼物"""
        data = {"cityCode": CITY_CODE}
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026DailyService~receiveDailyGift', data)
        if resp and resp.get('success'):
            return resp.get('obj', {})
        else:
            error_msg = resp.get('errorMessage', '未知错误') if resp else '请求失败'
            self.logger.warning(f'领取每日礼物失败: {error_msg}')
            return None

    def get_express_info(self) -> Optional[Dict]:
        """获取快递特惠活动信息"""
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026ExpressService~getExpressSpecialActivityInfo')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_family_status(self) -> Optional[Dict]:
        """获取家庭状态"""
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026FamilyService~familyStatus')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_widget_status(self) -> Optional[Dict]:
        """获取组件状态"""
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026DilateService~getWidgetStatus')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_dilate_change(self) -> Optional[Dict]:
        """获取组件变化"""
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026DilateService~getDilateChange')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_prize_pool(self) -> Optional[Dict]:
        """获取奖池信息"""
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026LotteryService~prizePool')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_paid_coupon_list(self) -> Optional[Dict]:
        """获取付费券包列表"""
        resp = self._post('/commonPost/~memberNonactivity~dragonBoat2026PaidCouponService~paidCouponPkgList')
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_user_rest_integral(self) -> int:
        """查询用户剩余积分"""
        resp = self._post('/commonPost/~memberNonactivity~activityTaskService~getUserRestIntegral')
        if resp and resp.get('success'):
            points = resp.get('obj', 0)
            self.logger.info(f'当前可用积分: {points}')
            return points
        return 0

    # ---------- 邀请初始化 ----------
    def do_invite(self):
        """发送邀请初始化请求"""
        try:
            available_invites = [inv for inv in inviteId if inv != self.user_id]
            if not available_invites:
                self.logger.warning("没有可用的邀请码（排除自身后为空），跳过邀请")
                return
            random_invite = random.choice(available_invites)
            url = f'{self.BASE_URL}/commonPost/~memberNonactivity~dragonBoat2026IndexService~index'
            data = {"inviteType": 1, "inviteUserId": random_invite}
            self.http.request(url, data=data)
        except Exception as e:
            self.logger.error(f"邀请初始化异常: {str(e)}")

    # ---------- 业务逻辑 ----------

    def do_daily_gift(self, result: Dict) -> None:
        """领取每日礼物"""
        self.logger.task('[每日礼物] 检查状态...')
        time.sleep(1)

        status = self.get_daily_gift_status()
        if status is None:
            self.logger.warning('[每日礼物] 获取状态失败')
            return

        can_receive = status.get('canReceive', False)
        received = status.get('received', False)

        if received:
            self.logger.success('[每日礼物] 今日已领取')
            return

        if not can_receive:
            self.logger.info('[每日礼物] 今日不可领取')
            return

        self.logger.task('[每日礼物] 尝试领取...')
        gift_result = self.receive_daily_gift()
        if gift_result:
            self.logger.success('[每日礼物] 领取成功')
            result['daily_gift'] = True
        else:
            self.logger.warning('[每日礼物] 领取失败')

    def do_tasks(self, result: Dict) -> None:
        """执行所有可自动完成的任务"""
        self.logger.info('正在获取端午活动任务列表...')
        tasks = self.get_task_list()
        if tasks is None:
            return

        self.logger.info(f'共发现 {len(tasks)} 个任务')

        for task in tasks:
            task_name = task.get('taskName', '未知')
            task_type = task.get('taskType', '')
            task_code = task.get('taskCode', '')
            status = task.get('status')
            process = task.get('process', '')
            rest_finish = task.get('restFinishTime', 0)
            virtual_token = task.get('virtualTokenNum', 0)

            # status=3 表示已完成且已领奖，status=1且restFinishTime=0表示已完成待领奖
            if status == 3 or (status == 1 and rest_finish <= 0):
                can_receive = task.get('canReceiveTokenNum', 0)
                if can_receive > 0:
                    self.logger.info(f'[{task_name}] 已完成，待领取 {can_receive} 次砸粽子机会')
                else:
                    self.logger.success(f'[{task_name}] 已完成 ({process})')
                continue

            if task_type in SKIP_TASK_TYPES:
                continue

            # 有taskCode的任务尝试自动完成（通用接口）
            if task_code:
                self.logger.task(f'[{task_name}] 尝试完成任务 (taskCode: {task_code})')
                if self.finish_task(task_code):
                    self.logger.success(f'[{task_name}] 完成成功，可获得 {virtual_token} 次砸粽子机会')
                    result['tasks_completed'] += 1
                else:
                    self.logger.warning(f'[{task_name}] 完成失败')
                time.sleep(1)

    def do_fetch_rewards(self, result: Dict) -> None:
        """领取所有已完成任务的奖励"""
        self.logger.info('领取任务奖励...')
        time.sleep(1)
        reward_resp = self.fetch_task_reward()
        if reward_resp:
            received = reward_resp.get('receivedAccountList', [])
            if received:
                for item in received:
                    currency = item.get('currency', '')
                    amount = item.get('amount', 0)
                    self.logger.success(f'领取奖励: {currency} x{amount}')
            else:
                self.logger.info('无新的任务奖励可领取')

        # 显示累计进度
        accrued_resp = self.get_accrued_task_award()
        if accrued_resp:
            progress = accrued_resp.get('currentProgress', 0)
            config = accrued_resp.get('progressConfig', {})
            if config:
                milestones = ', '.join([f'{k}个任务得{v}次' for k, v in sorted(config.items(), key=lambda x: int(x[0]))])
                self.logger.info(f'累计完成任务数: {progress} (里程碑: {milestones})')

    def do_crush_zongzi(self, result: Dict) -> None:
        """砸粽子直到没有次数"""
        # 先查看当前状态
        zongzi_status = self.query_zongzi_status()
        if zongzi_status:
            # 显示当前账户状态
            current_accounts = zongzi_status.get('currentAccountList', [])
            total_crush = zongzi_status.get('totalCrushTimes', 0)
            self.logger.info(f'累计砸粽次数: {total_crush}')

            for acc in current_accounts:
                currency = acc.get('currency', '')
                balance = acc.get('balance', 0)
                total_amount = acc.get('totalAmount', 0)
                name = CURRENCY_NAMES.get(currency, currency)
                self.logger.info(f'  {name}: 当前{balance} / 累计获得{total_amount}')

            # 检查是否有次数可以用来砸
            gold_zongzi_balance = 0
            for acc in current_accounts:
                if acc.get('currency') == 'GOLD_ZONGZI':
                    gold_zongzi_balance = acc.get('balance', 0)
                    break

            if gold_zongzi_balance <= 0:
                self.logger.info('无次数可砸，跳过')
                return

            self.logger.info(f'当前次数: {gold_zongzi_balance}，开始砸粽子...')

        # 开始砸粽子
        crush_count = 0
        max_crush = 50

        while crush_count < max_crush:
            time.sleep(1)
            crush_result = self.crush_zongzi()
            if crush_result is None:
                break

            received = crush_result.get('receivedAccountList', [])
            current_accounts = crush_result.get('currentAccountList', [])
            total_crush = crush_result.get('totalCrushTimes', 0)
            extra_card = crush_result.get('extraCardType', '')

            if received:
                for item in received:
                    currency = item.get('currency', '未知')
                    amount = item.get('amount', 0)
                    name = CURRENCY_NAMES.get(currency, currency)
                    self.logger.zongzi(f'砸到奖励: {name} x{amount}')
                    result['zongzi_detail'].append({'type': name, 'amount': amount})
                    result['gold_coins'] += amount if currency == 'GOLD_COIN' else 0
                crush_count += 1
            else:
                self.logger.info('没有砸到奖励或无次数')
                break

            # 检查剩余次数
            gold_zongzi_balance = 0
            for acc in current_accounts:
                if acc.get('currency') == 'GOLD_ZONGZI':
                    gold_zongzi_balance = acc.get('balance', 0)
                    break

            result['zongzi_balance'] = gold_zongzi_balance
            self.logger.info(f'剩余次数: {gold_zongzi_balance}，累计砸粽: {total_crush}次')

            if extra_card:
                card_names = {'DAILY': '每日额外奖励', 'FAMILY': '家庭额外奖励'}
                name = card_names.get(extra_card, extra_card)
                self.logger.info(f'触发额外奖励卡: {name}')

            if gold_zongzi_balance <= 0:
                break

        self.logger.info(f'砸粽子完成，本次共获得 {result["gold_coins"]} 金币')

    def show_status_summary(self) -> None:
        """展示端午活动状态汇总"""
        self.logger.info('=' * 20 + '  端午活动状态  ' + '=' * 20)

        # 粽子状态
        zongzi_status = self.query_zongzi_status()
        if zongzi_status:
            current_accounts = zongzi_status.get('currentAccountList', [])
            total_crush = zongzi_status.get('totalCrushTimes', 0)
            self.logger.info(f'累计砸粽次数: {total_crush}')
            for acc in current_accounts:
                currency = acc.get('currency', '')
                balance = acc.get('balance', 0)
                total_amount = acc.get('totalAmount', 0)
                name = CURRENCY_NAMES.get(currency, currency)
                self.logger.info(f'  {name}: 当前{balance} / 累计获得{total_amount}')

        # 每日礼物状态
        daily_status = self.get_daily_gift_status()
        if daily_status:
            can_receive = daily_status.get('canReceive', False)
            received = daily_status.get('received', False)
            status_str = '已领取' if received else ('可领取' if can_receive else '不可领取')
            self.logger.info(f'每日礼物: {status_str}')

        # 组件状态
        widget_status = self.get_widget_status()
        if widget_status:
            dilate = widget_status.get('dilateWidget', {})
            receive_status = dilate.get('receiveStatus', 0)
            self.logger.info(f'组件领取状态: {receive_status}')

        self.logger.info('=' * 56)

    def run(self) -> Dict[str, Any]:
        """执行端午活动全流程"""
        result = {
            'tasks_completed': 0,
            'gold_coins': 0,
            'zongzi_detail': [],
            'zongzi_balance': 0,
            'zongzi_total': 0,
            'gold_coin_balance': 0,
            'gold_coin_total': 0,
            'daily_gift': False,
        }

        # 邀请初始化
        self.do_invite()

        # 0. 获取活动首页信息
        index_info = self.get_activity_index()
        if index_info:
            self.logger.info(f'活动首页获取成功')

        # 1. 领取每日礼物
        self.do_daily_gift(result)

        # 2. 执行任务
        self.do_tasks(result)

        # 3. 领取任务奖励（获得砸粽子机会）
        self.do_fetch_rewards(result)

        # 4. 砸粽子
        self.do_crush_zongzi(result)

        # 5. 获取最终状态
        final_status = self.query_zongzi_status()
        if final_status:
            for acc in final_status.get('currentAccountList', []):
                if acc.get('currency') == 'GOLD_COIN':
                    result['gold_coin_balance'] = acc.get('balance', 0)
                    result['gold_coin_total'] = acc.get('totalAmount', 0)
                elif acc.get('currency') == 'GOLD_ZONGZI':
                    result['zongzi_balance'] = acc.get('balance', 0)
                    result['zongzi_total'] = acc.get('totalAmount', 0)

        return result


# ==================== 账号执行 ====================
def run_account(account_url: str, index: int) -> Dict[str, Any]:
    """执行单个账号"""
    logger = Logger()
    proxy_url = os.getenv('SF_PROXY_API_URL', '')
    proxy_manager = ProxyManager(proxy_url)

    # 登录
    http = SFHttpClient(proxy_manager)
    retry_count = 0
    login_success = False
    phone = ''
    user_id = ''

    while retry_count < MAX_PROXY_RETRIES and not login_success:
        try:
            if retry_count > 0:
                http = SFHttpClient(proxy_manager)
            success, user_id, phone = http.login(account_url)
            if success:
                login_success = True
                break
        except Exception as e:
            pass
        retry_count += 1
        if retry_count < MAX_PROXY_RETRIES:
            time.sleep(2)

    if not login_success:
        logger.error(f'账号{index + 1} 登录失败')
        return {'success': False, 'phone': '', 'index': index,
                'tasks_completed': 0, 'gold_coins': 0, 'zongzi_detail': [],
                'zongzi_balance': 0, 'zongzi_total': 0,
                'gold_coin_balance': 0, 'gold_coin_total': 0, 'daily_gift': False}

    masked_phone = phone[:3] + "****" + phone[7:] if len(phone) >= 7 else phone
    logger.success(f'账号{index + 1}: 【{masked_phone}】登录成功')

    # 随机延迟
    time.sleep(random.uniform(1, 3))

    executor = DragonBoatExecutor(http, logger, user_id)
    activity_result = executor.run()

    return {
        'success': True,
        'phone': phone,
        'index': index,
        **activity_result,
    }


# ==================== 主程序 ====================
def main():
    env_name = 'sfsyUrl'
    env_value = os.getenv(env_name)
    if not env_value:
        print(f"❌ 未找到环境变量 {env_name}，请检查配置")
        return

    account_urls = [url.strip() for url in env_value.split('&') if url.strip()]
    if not account_urls:
        print(f"❌ 环境变量 {env_name} 为空或格式错误")
        return

    random.shuffle(account_urls)

    print("=" * 60)
    print(f"🫔 顺丰2026端午活动 - 砸粽子赢金币")
    print(f"👨‍💻 作者: 爱学习的呆子 (改造自周年活动脚本)")
    print(f"📱 共获取到 {len(account_urls)} 个账号")
    print(f"⚙️ 并发数量: {CONCURRENT_NUM}")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    all_results = []

    if CONCURRENT_NUM <= 1:
        for idx, url in enumerate(account_urls):
            result = run_account(url, idx)
            all_results.append(result)
            if idx < len(account_urls) - 1:
                print("-" * 60)
                time.sleep(2)
    else:
        with ThreadPoolExecutor(max_workers=CONCURRENT_NUM) as pool:
            futures = {pool.submit(run_account, url, idx): idx for idx, url in enumerate(account_urls)}
            for future in as_completed(futures):
                all_results.append(future.result())

    all_results.sort(key=lambda x: x['index'])

    # 汇总
    print(f"\n" + "=" * 90)
    print(f"📊 端午活动汇总")
    print("=" * 90)
    print(f"{'序号':<6} {'手机号':<15} {'金币':<20} {'次数':<15} {'每日礼物':<10}")
    print("-" * 90)

    total_tasks = 0
    total_coins = 0

    for r in all_results:
        idx = r['index'] + 1
        phone = r['phone'][:3] + "****" + r['phone'][7:] if r.get('phone') and len(r['phone']) >= 7 else r.get('phone', '未登录')
        tasks = r.get('tasks_completed', 0)
        daily = '✅' if r.get('daily_gift', False) else '❌'

        coin_balance = r.get('gold_coin_balance', 0)
        coin_total = r.get('gold_coin_total', 0)
        zongzi_balance = r.get('zongzi_balance', 0)
        zongzi_total = r.get('zongzi_total', 0)

        total_tasks += tasks
        total_coins += coin_balance

        print(f"{idx:<6} {phone:<15} 当前{coin_balance}/累计{coin_total:<12} 当前{zongzi_balance}/累计{zongzi_total:<8} {daily:<10}")

    print("-" * 90)
    print(f"{'汇总':<6} {'账号: ' + str(len(all_results)):<15} 总金币: {total_coins}")
    print("=" * 90)
    print("\n🎊 所有账号执行完成!")


if __name__ == '__main__':
    main()
