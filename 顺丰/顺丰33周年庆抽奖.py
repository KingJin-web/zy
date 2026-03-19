"""
顺丰33周年活动 - 集齐5勋章抽大奖
只抽5张卡的大奖池（大疆/金条/iPhone等），4张不抽

Author: 爱学习的呆子
Version: 1.0.0
Date: 2026-03-17

"""

import hashlib
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

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ==================== 配置常量 ====================
PROXY_TIMEOUT = 15
MAX_PROXY_RETRIES = 5
CONCURRENT_NUM = int(os.getenv('SFBF', '1'))
if CONCURRENT_NUM > 20:
    CONCURRENT_NUM = 20
elif CONCURRENT_NUM < 1:
    CONCURRENT_NUM = 1

output_lock = Lock()

TOKEN = 'wwesldfs29aniversaryvdld29'
SYS_CODE = 'MCS-MIMP-CORE'

# 5种勋章
CARD_CURRENCIES = ['FA_CAI', 'GAN_FAN', 'GAO_YA', 'KAI_XIANG', 'DAN_GAO']
CARD_NAMES = {
    'FA_CAI': '马上有钱',
    'GAN_FAN': '全能吃货',
    'GAO_YA': '高雅人士',
    'KAI_XIANG': '拆箱达人',
    'DAN_GAO': '甜度超标',
}


# ==================== 日志缓冲 ====================
class LogBuffer:
    """收集日志，最后一次性输出，避免并发时交叉"""
    def __init__(self):
        self.lines: List[str] = []

    def log(self, msg: str):
        self.lines.append(msg)

    def flush(self):
        text = '\n'.join(self.lines)
        with output_lock:
            print(text)
        self.lines.clear()


# ==================== 代理管理器 ====================
class ProxyManager:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """返回代理字典，获取失败返回None"""
        try:
            if not self.api_url:
                return None
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                proxy_text = response.text.strip()
                if ':' in proxy_text:
                    proxy = proxy_text if proxy_text.startswith('http') else f'http://{proxy_text}'
                    return {'http': proxy, 'https': proxy}
            return None
        except Exception:
            return None

    @staticmethod
    def display_proxy(proxy_dict: Optional[Dict[str, str]]) -> str:
        """返回脱敏的代理地址用于日志"""
        if not proxy_dict:
            return '无代理'
        proxy = proxy_dict.get('http', '')
        if '@' in proxy:
            parts = proxy.split('@')
            return f"http://***@{parts[-1]}"
        return proxy


# ==================== HTTP客户端 ====================
class SFHttpClient:
    def __init__(self, proxy_manager: ProxyManager):
        self.proxy_manager = proxy_manager
        self.session = requests.Session()
        self.session.verify = False
        self.current_proxy_display = '无代理'

        proxy = self.proxy_manager.get_proxy()
        if proxy:
            self.session.proxies = proxy
            self.current_proxy_display = ProxyManager.display_proxy(proxy)

        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254173b) XWEB/19027',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'channel': 'xcxpart',
            'platform': 'MINI_PROGRAM',
            'accept-language': 'zh-CN,zh;q=0.9',
        }

    def _generate_sign(self) -> Dict[str, str]:
        timestamp = str(int(round(time.time() * 1000)))
        data = f'token={TOKEN}&timestamp={timestamp}&sysCode={SYS_CODE}'
        signature = hashlib.md5(data.encode()).hexdigest()
        return {'syscode': SYS_CODE, 'timestamp': timestamp, 'signature': signature}

    def request(self, url: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """请求失败直接切换代理，最多切换MAX_PROXY_RETRIES次"""
        for attempt in range(MAX_PROXY_RETRIES + 1):
            sign_data = self._generate_sign()
            headers = {**self.headers, **sign_data}

            try:
                resp = self.session.post(url, headers=headers, json=data or {}, timeout=PROXY_TIMEOUT)
                resp.raise_for_status()
                result = resp.json()
                if result is not None:
                    return result
            except Exception:
                pass

            # 请求失败，切换代理重试
            if attempt < MAX_PROXY_RETRIES:
                new_proxy = self.proxy_manager.get_proxy()
                if new_proxy:
                    self.session.proxies = new_proxy
                    self.current_proxy_display = ProxyManager.display_proxy(new_proxy)
                time.sleep(1)

        return None

    def login(self, url: str) -> tuple:
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
        except Exception:
            return False, '', ''


# ==================== 抽奖执行器 ====================
class LotteryExecutor:
    def __init__(self, http: SFHttpClient, phone: str, log: LogBuffer):
        self.http = http
        self.phone = phone
        self.masked_phone = phone[:3] + "****" + phone[7:] if len(phone) >= 7 else phone
        self.log = log

    def get_card_status(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2026CardService~cardStatus'
        resp = self.http.request(url, data={})
        if resp and resp.get('success'):
            return resp.get('obj', {})
        return None

    def get_prize_pool(self) -> Optional[List]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2026LotteryService~prizePool'
        resp = self.http.request(url, data={})
        if resp and resp.get('success'):
            return resp.get('obj', [])
        return None

    def prize_draw(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2026LotteryService~prizeDraw'
        data = {"currencyList": CARD_CURRENCIES}
        resp = self.http.request(url, data=data)
        if resp and resp.get('success'):
            return resp.get('obj', {})
        else:
            error_msg = resp.get('errorMessage', '未知错误') if resp else '请求失败'
            self.log.log(f"   ❌ 抽奖失败: {error_msg}")
            return None

    def get_card_balances(self, card_status: Dict) -> Dict[str, int]:
        balances = {}
        for acc in card_status.get('currentAccountList', []):
            currency = acc.get('currency', '')
            if currency in CARD_CURRENCIES:
                balances[currency] = acc.get('balance', 0)
        return balances

    def can_draw_5(self, balances: Dict[str, int]) -> bool:
        return all(balances.get(c, 0) >= 1 for c in CARD_CURRENCIES)

    def format_card_status(self, balances: Dict[str, int]) -> str:
        parts = []
        for c in CARD_CURRENCIES:
            name = CARD_NAMES.get(c, c)
            bal = balances.get(c, 0)
            parts.append(f"{name}:{bal}")
        return ' | '.join(parts)

    def run(self) -> List[Dict]:
        prizes = []
        log = self.log

        log.log(f"\n{'='*50}")
        log.log(f"📱 {self.masked_phone} | 🌐 {self.http.current_proxy_display}")
        log.log(f"{'='*50}")

        # 获取勋章状态
        card_status = self.get_card_status()
        if not card_status:
            log.log("   ❌ 获取勋章状态失败")
            return prizes

        balances = self.get_card_balances(card_status)
        log.log(f"   🎴 {self.format_card_status(balances)}")

        remain_sets = card_status.get('remainCardSet', 0)
        log.log(f"   📊 可抽大奖次数(5卡): {remain_sets}")

        if not self.can_draw_5(balances):
            log.log("   ⚠️ 勋章不足5种，无法抽奖")
            return prizes

        # 获取奖品池信息
        pool = self.get_prize_pool()
        if pool:
            for p in pool:
                if p.get('shouldNum') == 5:
                    lottery_num = p.get('lotteryNum', 0)
                    limit = p.get('limitLotteryNum', 0)
                    log.log(f"   🎰 5卡奖池: 已抽{lottery_num}/{limit}次")

        # 循环抽奖
        draw_count = 0
        while self.can_draw_5(balances):
            draw_count += 1
            time.sleep(random.uniform(1, 2))

            result = self.prize_draw()
            if not result:
                break

            gift_name = result.get('giftBagName', '未知奖品')
            gift_worth = result.get('giftBagWorth', 0)
            gift_desc = result.get('giftBagDesc', '')

            prizes.append({
                'phone': self.phone,
                'masked_phone': self.masked_phone,
                'gift_name': gift_name,
                'gift_worth': gift_worth,
                'gift_desc': gift_desc,
                'gift_code': result.get('giftBagCode', ''),
            })

            log.log(f"   🎲 第{draw_count}次 → 🎉 {gift_name} (价值{gift_worth}元)")

            # 重新获取勋章状态
            time.sleep(1)
            card_status = self.get_card_status()
            if not card_status:
                log.log("   ❌ 获取勋章状态失败，停止")
                break

            balances = self.get_card_balances(card_status)

            if not self.can_draw_5(balances):
                log.log(f"   🎴 {self.format_card_status(balances)} → 勋章不足，结束")

        log.log(f"   📊 本账号共抽奖 {draw_count} 次")
        return prizes


# ==================== 账号执行 ====================
def run_account(account_url: str, index: int) -> Dict[str, Any]:
    log = LogBuffer()
    proxy_url = os.getenv('SF_PROXY_API_URL', '')
    proxy_manager = ProxyManager(proxy_url)

    http = SFHttpClient(proxy_manager)
    retry_count = 0
    login_success = False
    phone = ''

    while retry_count < MAX_PROXY_RETRIES and not login_success:
        try:
            if retry_count > 0:
                http = SFHttpClient(proxy_manager)
            success, _, phone = http.login(account_url)
            if success:
                login_success = True
                break
        except Exception:
            pass
        retry_count += 1
        if retry_count < MAX_PROXY_RETRIES:
            time.sleep(1)

    if not login_success:
        log.log(f"❌ 账号{index + 1} 登录失败")
        log.flush()
        return {'success': False, 'phone': '', 'index': index, 'prizes': []}

    executor = LotteryExecutor(http, phone, log)
    prizes = executor.run()

    # 一次性输出该账号所有日志
    log.flush()

    return {'success': True, 'phone': phone, 'index': index, 'prizes': prizes}


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

    print("=" * 60)
    print(f"🎰 顺丰33周年 - 集齐5勋章抽大奖")
    print(f"👨‍💻 作者: 爱学习的呆子")
    print(f"📱 共 {len(account_urls)} 个账号")
    print(f"⚙️ 并发数量: {CONCURRENT_NUM}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📌 规则: 只抽5卡大奖池，4卡不抽")
    print("=" * 60)

    all_results = []

    if CONCURRENT_NUM <= 1:
        for idx, url in enumerate(account_urls):
            result = run_account(url, idx)
            all_results.append(result)
            if idx < len(account_urls) - 1:
                time.sleep(2)
    else:
        with ThreadPoolExecutor(max_workers=CONCURRENT_NUM) as pool:
            futures = {pool.submit(run_account, url, idx): idx for idx, url in enumerate(account_urls)}
            for future in as_completed(futures):
                all_results.append(future.result())

    all_results.sort(key=lambda x: x['index'])

    # ==================== 汇总报告 ====================
    print(f"\n{'='*60}")
    print(f"📊 抽奖汇总报告")
    print(f"{'='*60}")

    total_draws = 0
    all_prizes = []

    for r in all_results:
        phone = r['phone']
        masked = phone[:3] + "****" + phone[7:] if phone and len(phone) >= 7 else phone or '未登录'
        prizes = r.get('prizes', [])
        total_draws += len(prizes)
        all_prizes.extend(prizes)

        if not r['success']:
            print(f"❌ {masked}: 登录失败")
        elif not prizes:
            print(f"⚠️ {masked}: 勋章不足，未抽奖")
        else:
            for p in prizes:
                print(f"🎉 {masked}: {p['gift_name']} (价值{p['gift_worth']}元)")

    print(f"\n{'─'*60}")
    print(f"📱 总账号: {len(all_results)}")
    print(f"🎲 总抽奖: {total_draws} 次")
    print(f"🎁 总奖品: {len(all_prizes)} 个")

    if all_prizes:
        total_worth = sum(p['gift_worth'] for p in all_prizes)
        print(f"💰 总价值: {total_worth} 元")

        gift_count = {}
        for p in all_prizes:
            name = p['gift_name']
            gift_count[name] = gift_count.get(name, 0) + 1
        print(f"\n📋 奖品统计:")
        for name, count in sorted(gift_count.items(), key=lambda x: -x[1]):
            print(f"   {name} x{count}")

    # 高价值奖品（免单券、6/7/8折券）
    HIGH_VALUE_KEYWORDS = ['免单', '6折', '7折', '8折']
    high_value_prizes = [p for p in all_prizes if any(k in p['gift_name'] for k in HIGH_VALUE_KEYWORDS)]

    if high_value_prizes:
        print(f"\n🏆 高价值奖品明细:")
        print(f"{'─'*60}")
        for p in high_value_prizes:
            masked = p.get('masked_phone', p.get('phone', '未知')[:3] + "****" + p.get('phone', '')[7:])
            print(f"  📞 {masked}: {p['gift_name']} (价值{p['gift_worth']}元)")

    print(f"{'='*60}")
    print("🎊 抽奖完成!")


if __name__ == '__main__':
    main()
