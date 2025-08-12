# 提醒：此脚本只适配插件提交或编码后的URL运行！
# 提醒：此脚本只适配插件提交或编码后的URL运行！
# 提醒：此脚本只适配插件提交或编码后的URL运行！

# 【常规变量】
# 账号变量名：sfsyUrl  （多号新建变量或者&）
# 代理变量名：SF_PROXY_API_URL  （支持代理API或代理池）

# 【采蜜活动相关变量】
# 兑换区间设置：SFSY_DHJE  （例如 "23-15" 表示优先兑换23元，换不了就换20元，最后换15元，如果只兑换23元，填写“23”即可，其余额度请自行看活动页面）
# 是否强制兑换：SFSY_DH  （填写 "true" 或 "false"  开启后 运行脚本则会进行兑换  关闭后 只有活动结束当天运行才进行兑换   默认为关闭状态）
# 面额兑换次数：SFSY_DHCS  （默认为3次，相当于23的卷会尝试兑换3次）


import hashlib
import json
import os
import random
import time
from datetime import datetime, timedelta
from sys import exit
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import unquote

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
EXCHANGE_RANGE = os.getenv('SFSY_DHJE', '23')  # 默认：23-15
FORCE_EXCHANGE = os.getenv('SFSY_DH', 'false').lower() == 'true'  # 默认：false
MAX_EXCHANGE_TIMES = int(os.getenv('SFSY_DHCS', '3'))  # 默认：3
PROXY_API_URL = os.getenv('SF_PROXY_API_URL', '')  # 从环境变量获取代理API地址
AVAILABLE_AMOUNTS = ['23元', '20元', '15元', '10元', '5元', '3元', '2元', '1元']


def parse_exchange_range(exchange_range):
    if '-' in exchange_range:
        try:
            start_val, end_val = exchange_range.split('-')
            start_val = int(start_val.strip())
            end_val = int(end_val.strip())

            target_amounts = []
            for amount in AVAILABLE_AMOUNTS:
                amount_val = int(amount.replace('元', ''))
                if end_val <= amount_val <= start_val:
                    target_amounts.append(amount)

            return target_amounts
        except:
            print(f"❌ 兑换区间配置错误: {exchange_range}")
            return ['23元']  # 默认返回23元
    else:
        if exchange_range.endswith('元'):
            return [exchange_range]
        else:
            return [f"{exchange_range}元"]


def get_proxy():
    try:
        if not PROXY_API_URL:
            print('⚠️ 未配置代理API地址，将不使用代理')
            return None

        response = requests.get(PROXY_API_URL, timeout=10)
        if response.status_code == 200:
            proxy_text = response.text.strip()
            if ':' in proxy_text:
                proxy = f'http://{proxy_text}'
                return {
                    'http': proxy,
                    'https': proxy
                }
        print(f'❌ 获取代理失败: {response.text}')
        return None
    except Exception as e:
        print(f'❌ 获取代理异常: {str(e)}')
        return None


send_msg = ''
one_msg = ''


def Log(cont=''):
    global send_msg, one_msg
    print(cont)
    if cont:
        one_msg += f'{cont}\n'
        send_msg += f'{cont}\n'


inviteId = ['']


class RUN:
    def __init__(self, info, index):
        global one_msg
        one_msg = ''
        split_info = info.split('@')
        url = split_info[0]
        len_split_info = len(split_info)
        last_info = split_info[len_split_info - 1]
        self.send_UID = None
        if len_split_info > 0 and "UID_" in last_info:
            self.send_UID = last_info
        self.index = index + 1

        self.proxy = get_proxy()
        if self.proxy:
            print(f"✅ 成功获取代理: {self.proxy['http']}")

        self.s = requests.session()
        self.s.verify = False
        if self.proxy:
            self.s.proxies = self.proxy

        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090551) XWEB/6945 Flue',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'zh-CN,zh',
            'platform': 'MINI_PROGRAM',
        }

        self.login_res = self.login(url)
        self.all_logs = []
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.member_day_black = False
        self.member_day_red_packet_drew_today = False
        self.member_day_red_packet_map = {}
        self.max_level = 8
        self.packet_threshold = 1 << (self.max_level - 1)
        self.is_last_day = False
        self.auto_exchanged = False
        self.exchange_count = 0
        self.force_exchange = FORCE_EXCHANGE
        self.totalPoint = 0
        self.usableHoney = 0
        self.activityEndTime = ""
        self.target_amounts = parse_exchange_range(EXCHANGE_RANGE)

    def get_deviceId(self, characters='abcdef0123456789'):
        result = ''
        for char in 'xxxxxxxx-xxxx-xxxx':
            if char == 'x':
                result += random.choice(characters)
            elif char == 'X':
                result += random.choice(characters).upper()
            else:
                result += char
        return result

    def login(self, sfurl):
        try:
            decoded_url = unquote(sfurl)
            ress = self.s.get(decoded_url, headers=self.headers)
            self.user_id = self.s.cookies.get_dict().get('_login_user_id_', '')
            self.phone = self.s.cookies.get_dict().get('_login_mobile_', '')
            self.mobile = self.phone[:3] + "*" * 4 + self.phone[7:] if self.phone else ''

            if self.phone:
                Log(f'👤 账号{self.index}:【{self.mobile}】登陆成功')
                return True
            else:
                Log(f'❌ 账号{self.index}获取用户信息失败')
                return False
        except Exception as e:
            Log(f'❌ 登录异常: {str(e)}')
            return False

    def getSign(self):
        timestamp = str(int(round(time.time() * 1000)))
        token = 'wwesldfs29aniversaryvdld29'
        sysCode = 'MCS-MIMP-CORE'
        data = f'token={token}&timestamp={timestamp}&sysCode={sysCode}'
        signature = hashlib.md5(data.encode()).hexdigest()
        data = {
            'sysCode': sysCode,
            'timestamp': timestamp,
            'signature': signature
        }
        self.headers.update(data)
        return data

    def do_request(self, url, data={}, req_type='post', max_retries=3):
        self.getSign()
        retry_count = 0

        while retry_count < max_retries:
            try:
                if req_type.lower() == 'get':
                    response = self.s.get(url, headers=self.headers, timeout=30)
                elif req_type.lower() == 'post':
                    response = self.s.post(url, headers=self.headers, json=data, timeout=30)
                else:
                    raise ValueError('Invalid req_type: %s' % req_type)

                response.raise_for_status()

                try:
                    res = response.json()
                    return res
                except json.JSONDecodeError as e:
                    print(f'JSON解析失败: {str(e)}, 响应内容: {response.text[:200]}')
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f'正在进行第{retry_count + 1}次重试...')
                        time.sleep(2)
                        continue
                    return None

            except requests.exceptions.RequestException as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f'请求失败，正在切换代理重试 ({retry_count}/{max_retries}): {str(e)}')
                    self.proxy = get_proxy()
                    if self.proxy:
                        print(f"✅ 成功获取新代理: {self.proxy['http']}")
                        self.s.proxies = self.proxy
                    time.sleep(2)
                else:
                    print('请求最终失败:', e)
                    return None

        return None

    def sign(self):
        print(f'🎯 开始执行签到')
        json_data = {"comeFrom": "vioin", "channelFrom": "WEIXIN"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~automaticSignFetchPackage'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            count_day = response.get('obj', {}).get('countDay', 0)
            if response.get('obj') and response['obj'].get('integralTaskSignPackageVOList'):
                packet_name = response["obj"]["integralTaskSignPackageVOList"][0]["packetName"]
                Log(f'✨ 签到成功，获得【{packet_name}】，本周累计签到【{count_day + 1}】天')
            else:
                Log(f'📝 今日已签到，本周累计签到【{count_day + 1}】天')
        else:
            print(f'❌ 签到失败！原因：{response.get("errorMessage")}')

    def superWelfare_receiveRedPacket(self):
        print(f'🎁 超值福利签到')
        json_data = {
            'channel': 'czflqdlhbxcx'
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberActLengthy~redPacketActivityService~superWelfare~receiveRedPacket'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            gift_list = response.get('obj', {}).get('giftList', [])
            if response.get('obj', {}).get('extraGiftList', []):
                gift_list.extend(response['obj']['extraGiftList'])
            gift_names = ', '.join([gift['giftName'] for gift in gift_list])
            receive_status = response.get('obj', {}).get('receiveStatus')
            status_message = '领取成功' if receive_status == 1 else '已领取过'
            Log(f'🎉 超值福利签到[{status_message}]: {gift_names}')
        else:
            error_message = response.get('errorMessage') or json.dumps(response) or '无返回'
            print(f'❌ 超值福利签到失败: {error_message}')

    def get_SignTaskList(self, END=False):
        if not END: print(f'🎯 开始获取签到任务列表')
        json_data = {
            'channelType': '1',
            'deviceId': self.get_deviceId(),
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~queryPointTaskAndSignFromES'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True and response.get('obj') != []:
            self.totalPoint = response["obj"]["totalPoint"]
            if END:
                Log(f'💰 当前积分：【{self.totalPoint}】')
                return
            Log(f'💰 执行前积分：【{self.totalPoint}】')
            for task in response["obj"]["taskTitleLevels"]:
                self.taskId = task["taskId"]
                self.taskCode = task["taskCode"]
                self.strategyId = task["strategyId"]
                self.title = task["title"]
                status = task["status"]
                skip_title = ['用行业模板寄件下单', '去新增一个收件偏好', '参与积分活动']
                if status == 3:
                    print(f'✨ {self.title}-已完成')
                    continue
                if self.title in skip_title:
                    print(f'⏭️ {self.title}-跳过')
                    continue
                else:
                    # print("taskId:", taskId)
                    # print("taskCode:", taskCode)
                    # print("----------------------")
                    self.doTask()
                    time.sleep(3)
                self.receiveTask()

    def doTask(self):
        print(f'🎯 开始去完成【{self.title}】任务')
        json_data = {
            'taskCode': self.taskCode,
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonRoutePost/memberEs/taskRecord/finishTask'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'✨ 【{self.title}】任务-已完成')
        else:
            print(f'❌ 【{self.title}】任务-{response.get("errorMessage")}')

    def receiveTask(self):
        print(f'🎁 开始领取【{self.title}】任务奖励')
        json_data = {
            "strategyId": self.strategyId,
            "taskId": self.taskId,
            "taskCode": self.taskCode,
            "deviceId": self.get_deviceId()
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~fetchIntegral'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'✨ 【{self.title}】任务奖励领取成功！')
        else:
            print(f'❌ 【{self.title}】任务-{response.get("errorMessage")}')

    def do_honeyTask(self):
        # 做任务
        json_data = {"taskCode": self.taskCode}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'>【{self.taskType}】任务-已完成')
        else:
            print(f'>【{self.taskType}】任务-{response.get("errorMessage")}')

    def receive_honeyTask(self):
        print('>>>执行收取丰蜜任务')
        # 收取
        self.headers['syscode'] = 'MCS-MIMP-CORE'
        self.headers['channel'] = 'wxwdsj'
        self.headers['accept'] = 'application/json, text/plain, */*'
        self.headers['content-type'] = 'application/json;charset=UTF-8'
        self.headers['platform'] = 'MINI_PROGRAM'
        json_data = {"taskType": self.taskType}
        # print(json_data)
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~receiveHoney'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'收取任务【{self.taskType}】成功！')
        else:
            print(f'收取任务【{self.taskType}】失败！原因：{response.get("errorMessage")}')

    def get_coupom(self, goods):
        json_data = {
            "from": "Point_Mall",
            "orderSource": "POINT_MALL_EXCHANGE",
            "goodsNo": goods['goodsNo'],
            "quantity": 1,
            "taskCode": self.taskCode
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~createOrder'

        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            return True
        else:
            return False

    def get_coupom_list(self):
        json_data = {
            "memGrade": 2,
            "categoryCode": "SHTQ",
            "showCode": "SHTQWNTJ"
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~mallGoodsLifeService~list'

        response = self.do_request(url, data=json_data)

        if response.get('success') == True:
            all_goods = []
            for obj in response.get("obj", []):
                goods_list = obj.get("goodsList", [])
                all_goods.extend(goods_list)

            for goods in all_goods:
                exchange_times_limit = goods.get('exchangeTimesLimit', 0)

                if exchange_times_limit >= 1:
                    if self.get_coupom(goods):
                        print('✨ 成功领取券，任务结束！')
                        return
            print('📝 所有券尝试完成，没有可用的券或全部领取失败。')
        else:
            print(f'> 获取券列表失败！原因：{response.get("errorMessage")}')

    def get_honeyTaskListStart(self):
        print('🍯 开始获取采蜜换大礼任务列表')
        json_data = {}
        self.headers['channel'] = 'wxwdsj'
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~taskDetail'

        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            for item in response["obj"]["list"]:
                self.taskType = item["taskType"]
                status = item["status"]
                if status == 3:
                    print(f'✨ 【{self.taskType}】-已完成')
                    continue
                if "taskCode" in item:
                    self.taskCode = item["taskCode"]
                    if self.taskType == 'DAILY_VIP_TASK_TYPE':
                        self.get_coupom_list()
                    else:
                        self.do_honeyTask()
                if self.taskType == 'BEES_GAME_TASK_TYPE':
                    self.honey_damaoxian()
                time.sleep(2)

    def honey_damaoxian(self):
        print('>>>执行大冒险任务')
        gameNum = 5
        for i in range(1, gameNum):
            json_data = {
                'gatherHoney': 20,
            }
            if gameNum < 0: break
            print(f'>>开始第{i}次大冒险')
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeGameService~gameReport'
            response = self.do_request(url, data=json_data)
            stu = response.get('success')
            if stu:
                gameNum = response.get('obj')['gameNum']
                print(f'>大冒险成功！剩余次数【{gameNum}】')
                time.sleep(2)
                gameNum -= 1
            elif response.get("errorMessage") == '容量不足':
                print(f'> 需要扩容')
                self.honey_expand()
            else:
                print(f'>大冒险失败！【{response.get("errorMessage")}】')
                break

    def honey_expand(self):
        print('>>>容器扩容')
        gameNum = 5

        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~expand'
        response = self.do_request(url, data={})
        stu = response.get('success', False)
        if stu:
            obj = response.get('obj')
            print(f'>成功扩容【{obj}】容量')
        else:
            print(f'>扩容失败！【{response.get("errorMessage")}】')

    def honey_indexData(self, END=False):
        if not END: print('--------------------------------\n🍯 开始执行采蜜换大礼任务')
        random_invite = random.choice([invite for invite in inviteId if invite != self.user_id])
        self.headers['channel'] = 'wxwdsj'
        json_data = {"inviteUserId": random_invite}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~indexData'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            self.usableHoney = response.get('obj').get('usableHoney')
            activityEndTime = response.get('obj').get('activityEndTime', '')

            if activityEndTime:
                try:
                    self.activityEndTime = activityEndTime.split()[0] if ' ' in activityEndTime else activityEndTime
                    activity_end_time = datetime.strptime(activityEndTime, "%Y-%m-%d %H:%M:%S")
                    current_time = datetime.now()

                    if current_time.date() == activity_end_time.date():
                        self.is_last_day = True
                        if not END:
                            Log(f"⏳ 本期活动今日结束，尝试自动兑换券！目标：{' > '.join(self.target_amounts)}")
                            if not self.auto_exchanged:
                                exchange_success = self.exchange_23_coupon()
                                if exchange_success:
                                    self.auto_exchanged = True
                except Exception as e:
                    print(f'处理活动时间异常: {str(e)}')
                    self.activityEndTime = activityEndTime

            if not END:
                Log(f'🍯 执行前丰蜜：【{self.usableHoney}】')
                if activityEndTime and not self.is_last_day:
                    print(f'📅 本期活动结束时间【{activityEndTime}】')

                taskDetail = response.get('obj').get('taskDetail')
                if taskDetail != []:
                    for task in taskDetail:
                        self.taskType = task['type']
                        self.receive_honeyTask()
                        time.sleep(2)
            else:
                Log(f'🍯 执行后丰蜜：【{self.usableHoney}】')
                return

    def EAR_END_2023_TaskList(self):
        print('\n🎭 开始年终集卡任务')
        json_data = {
            "activityCode": "YEAREND_2024",
            "channelType": "MINI_PROGRAM"
        }
        self.headers['channel'] = '24nzdb'
        self.headers['platform'] = 'MINI_PROGRAM'
        self.headers['syscode'] = 'MCS-MIMP-CORE'

        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'

        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            for item in response["obj"]:
                self.title = item["taskName"]
                self.taskType = item["taskType"]
                status = item["status"]
                if status == 3:
                    print(f'✨ 【{self.taskType}】-已完成')
                    continue
                if self.taskType == 'INTEGRAL_EXCHANGE':
                    print(f'⚠️ 积分兑换任务暂不支持')
                elif self.taskType == 'CLICK_MY_SETTING':
                    self.taskCode = item["taskCode"]
                    self.addDeliverPrefer()
                if "taskCode" in item:
                    self.taskCode = item["taskCode"]
                    self.doTask()
                    time.sleep(3)
                    self.receiveTask()
                else:
                    print(f'⚠️ 暂时不支持【{self.title}】任务')

    def addDeliverPrefer(self):
        print(f'>>>开始【{self.title}】任务')
        json_data = {
            "country": "中国",
            "countryCode": "A000086000",
            "province": "北京市",
            "provinceCode": "A110000000",
            "city": "北京市",
            "cityCode": "A111000000",
            "county": "东城区",
            "countyCode": "A110101000",
            "address": "1号楼1单元101",
            "latitude": "",
            "longitude": "",
            "memberId": "",
            "locationCode": "010",
            "zoneCode": "CN",
            "postCode": "",
            "takeWay": "7",
            "callBeforeDelivery": 'false',
            "deliverTag": "2,3,4,1",
            "deliverTagContent": "",
            "startDeliverTime": "",
            "selectCollection": 'false',
            "serviceName": "",
            "serviceCode": "",
            "serviceType": "",
            "serviceAddress": "",
            "serviceDistance": "",
            "serviceTime": "",
            "serviceTelephone": "",
            "channelCode": "RW11111",
            "taskId": self.taskId,
            "extJson": "{\"noDeliverDetail\":[]}"
        }
        url = 'https://ucmp.sf-express.com/cx-wechat-member/member/deliveryPreference/addDeliverPrefer'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print('新增一个收件偏好，成功')
        else:
            print(f'>【{self.title}】任务-{response.get("errorMessage")}')

    def member_day_index(self):
        print('🎭 会员日活动')
        try:
            invite_user_id = random.choice([invite for invite in inviteId if invite != self.user_id])
            payload = {'inviteUserId': invite_user_id}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayIndexService~index'

            response = self.do_request(url, data=payload)
            if response.get('success'):
                lottery_num = response.get('obj', {}).get('lotteryNum', 0)
                can_receive_invite_award = response.get('obj', {}).get('canReceiveInviteAward', False)
                if can_receive_invite_award:
                    self.member_day_receive_invite_award(invite_user_id)
                self.member_day_red_packet_status()
                Log(f'🎁 会员日可以抽奖{lottery_num}次')
                for _ in range(lottery_num):
                    self.member_day_lottery()
                if self.member_day_black:
                    return
                self.member_day_task_list()
                if self.member_day_black:
                    return
                self.member_day_red_packet_status()
            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'📝 查询会员日失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_receive_invite_award(self, invite_user_id):
        try:
            payload = {'inviteUserId': invite_user_id}

            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayIndexService~receiveInviteAward'

            response = self.do_request(url, payload)
            if response.get('success'):
                product_name = response.get('obj', {}).get('productName', '空气')
                Log(f'🎁 会员日奖励: {product_name}')
            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'📝 领取会员日奖励失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_lottery(self):
        try:
            payload = {}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayLotteryService~lottery'

            response = self.do_request(url, payload)
            if response.get('success'):
                product_name = response.get('obj', {}).get('productName', '空气')
                Log(f'🎁 会员日抽奖: {product_name}')
            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'📝 会员日抽奖失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_task_list(self):
        try:
            payload = {'activityCode': 'MEMBER_DAY', 'channelType': 'MINI_PROGRAM'}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'

            response = self.do_request(url, payload)
            if response.get('success'):
                task_list = response.get('obj', [])
                for task in task_list:
                    if task['status'] == 1:
                        if self.member_day_black:
                            return
                        self.member_day_fetch_mix_task_reward(task)
                for task in task_list:
                    if task['status'] == 2:
                        if self.member_day_black:
                            return
                        if task['taskType'] in ['SEND_SUCCESS', 'INVITEFRIENDS_PARTAKE_ACTIVITY', 'OPEN_SVIP',
                                                'OPEN_NEW_EXPRESS_CARD', 'OPEN_FAMILY_CARD', 'CHARGE_NEW_EXPRESS_CARD',
                                                'INTEGRAL_EXCHANGE']:
                            pass
                        else:
                            for _ in range(task['restFinishTime']):
                                if self.member_day_black:
                                    return
                                self.member_day_finish_task(task)
            else:
                error_message = response.get('errorMessage', '无返回')
                Log('📝 查询会员日任务失败: ' + error_message)
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_finish_task(self, task):
        try:
            payload = {'taskCode': task['taskCode']}

            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'

            response = self.do_request(url, payload)
            if response.get('success'):
                Log('📝 完成会员日任务[' + task['taskName'] + ']成功')
                self.member_day_fetch_mix_task_reward(task)
            else:
                error_message = response.get('errorMessage', '无返回')
                Log('📝 完成会员日任务[' + task['taskName'] + ']失败: ' + error_message)
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_fetch_mix_task_reward(self, task):
        try:
            payload = {'taskType': task['taskType'], 'activityCode': 'MEMBER_DAY', 'channelType': 'MINI_PROGRAM'}

            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~fetchMixTaskReward'

            response = self.do_request(url, payload)
            if response.get('success'):
                Log('🎁 领取会员日任务[' + task['taskName'] + ']奖励成功')
            else:
                error_message = response.get('errorMessage', '无返回')
                Log('📝 领取会员日任务[' + task['taskName'] + ']奖励失败: ' + error_message)
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_receive_red_packet(self, hour):
        try:
            payload = {'receiveHour': hour}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayTaskService~receiveRedPacket'

            response = self.do_request(url, payload)
            if response.get('success'):
                print(f'🎁 会员日领取{hour}点红包成功')
            else:
                error_message = response.get('errorMessage', '无返回')
                print(f'📝 会员日领取{hour}点红包失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_red_packet_status(self):
        try:
            payload = {}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayPacketService~redPacketStatus'
            response = self.do_request(url, payload)
            if response.get('success'):
                packet_list = response.get('obj', {}).get('packetList', [])
                for packet in packet_list:
                    self.member_day_red_packet_map[packet['level']] = packet['count']

                for level in range(1, self.max_level):
                    count = self.member_day_red_packet_map.get(level, 0)
                    while count >= 2:
                        self.member_day_red_packet_merge(level)
                        count -= 2
                packet_summary = []
                remaining_needed = 0

                for level, count in self.member_day_red_packet_map.items():
                    if count == 0:
                        continue
                    packet_summary.append(f"[{level}级]X{count}")
                    int_level = int(level)
                    if int_level < self.max_level:
                        remaining_needed += 1 << (int_level - 1)

                Log("📝 会员日合成列表: " + ", ".join(packet_summary))

                if self.member_day_red_packet_map.get(self.max_level):
                    Log(f"🎁 会员日已拥有[{self.max_level}级]红包X{self.member_day_red_packet_map[self.max_level]}")
                    self.member_day_red_packet_draw(self.max_level)
                else:
                    remaining = self.packet_threshold - remaining_needed
                    Log(f"📝 会员日距离[{self.max_level}级]红包还差: [1级]红包X{remaining}")

            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'📝 查询会员日合成失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_red_packet_merge(self, level):
        try:
            # for key,level in enumerate(self.member_day_red_packet_map):
            #     pass
            payload = {'level': level, 'num': 2}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayPacketService~redPacketMerge'

            response = self.do_request(url, payload)
            if response.get('success'):
                Log(f'🎁 会员日合成: [{level}级]红包X2 -> [{level + 1}级]红包')
                self.member_day_red_packet_map[level] -= 2
                if not self.member_day_red_packet_map.get(level + 1):
                    self.member_day_red_packet_map[level + 1] = 0
                self.member_day_red_packet_map[level + 1] += 1
            else:
                error_message = response.get('errorMessage', '无返回')
                Log(f'📝 会员日合成两个[{level}级]红包失败: {error_message}')
                if '没有资格参与活动' in error_message:
                    self.member_day_black = True
                    Log('📝 会员日任务风控')
        except Exception as e:
            print(e)

    def member_day_red_packet_draw(self, level):
        try:
            payload = {'level': str(level)}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayPacketService~redPacketDraw'
            response = self.do_request(url, payload)
            if response and response.get('success'):
                coupon_names = [item['couponName'] for item in response.get('obj', [])] or []

                Log(f"🎁 会员日提取[{level}级]红包: {', '.join(coupon_names) or '空气'}")
            else:
                error_message = response.get('errorMessage') if response else "无返回"
                Log(f"📝 会员日提取[{level}级]红包失败: {error_message}")
                if "没有资格参与活动" in error_message:
                    self.memberDay_black = True
                    print("📝 会员日任务风控")
        except Exception as e:
            print(e)

    def exchange_coupon(self, coupon_amount):
        """兑换指定面额的券"""
        self.getSign()
        exchange_headers = {
            'authority': 'mcs-mimp-web.sf-express.com',
            'origin': 'https://mcs-mimp-web.sf-express.com',
            'referer': 'https://mcs-mimp-web.sf-express.com/inboxPresentCouponList',
            'content-type': 'application/json;charset=UTF-8',
            'channel': 'wxwdsj',
            'sw8': '1-ZDRlNjQwZjUtNmViYi00NmRhLThiZTMtZWEyZTUzYTlhOWFm-ZDM4MjIzM2YtMDQ1NC00ZDJlLWIwMDUtYTQyZmE1ZGE4ZTI5-0-ZmI0MDgxNzA4NWJlNGUzOThlMGI2ZjRiMDgxNzc3NDY=-d2Vi-L2luYm94UHJlc2VudENvdXBvbkxpc3Q=-L21jcy1taW1wL2NvbW1vblBvc3Qvfm1lbWJlck5vbmAjdGl2aXR5fnJlY2VpdmVFeGNoYW5nZUdpZnRCYWdTZXJ2aWNlfmxpc3Q='
        }
        headers = {**self.headers, **exchange_headers}

        for attempt in range(1, MAX_EXCHANGE_TIMES + 1):
            try:
                list_url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeGiftBagService~list'
                list_data = {"exchangeType": "EXCHANGE_SFC"}
                list_res = self.s.post(list_url, headers=headers, json=list_data, timeout=10)
                list_res.raise_for_status()
                list_json = list_res.json()

                if not list_json.get('success'):
                    return False, f"获取礼品列表失败"

                coupon = next(
                    (g for g in list_json.get('obj', [])
                     if coupon_amount in g.get('giftBagName', '')),
                    None
                )

                if not coupon:
                    return False, f"未找到{coupon_amount}券"

                required_honey = coupon.get('exchangeHoney')
                if self.usableHoney < required_honey:
                    return False, f"丰蜜不足：需要{required_honey}，当前{self.usableHoney}"

                exchange_url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeGiftBagService~exchange'
                exchange_data = {
                    "giftBagCode": coupon['giftBagCode'],
                    "ruleCode": coupon['ruleCode'],
                    "exchangeType": "EXCHANGE_SFC",
                    "memberNo": self.user_id,
                    "channel": "wxwdsj"
                }

                exchange_res = self.s.post(exchange_url, headers=headers, json=exchange_data, timeout=10)
                exchange_res.raise_for_status()
                exchange_json = exchange_res.json()

                if exchange_json.get('success'):
                    self.usableHoney -= required_honey
                    self.exchange_count += 1
                    return True, f"成功兑换{coupon_amount}券"
                else:
                    return False, exchange_json.get('errorMessage', '兑换失败')

            except Exception as e:
                if attempt == MAX_EXCHANGE_TIMES:
                    return False, f"兑换异常：{str(e)}"
                time.sleep(2)

        return False, "多次尝试失败"

    def execute_exchange_range(self):
        """按照优先级执行兑换区间"""
        Log(f"🎯 兑换目标：{' > '.join(self.target_amounts)}")

        for coupon_amount in self.target_amounts:
            Log(f"💰 尝试兑换 {coupon_amount} 券...")
            success, message = self.exchange_coupon(coupon_amount)

            if success:
                Log(f"🎉 {message}")
                time.sleep(3)
                return True
            else:
                Log(f"❌ {coupon_amount} - {message}")

        return False

    def exchange_23_coupon(self):
        """兑换功能（兼容原方法名）"""
        return self.execute_exchange_range()

    def main(self):
        global one_msg
        wait_time = random.randint(1000, 3000) / 1000.0
        time.sleep(wait_time)
        one_msg = ''
        if not self.login_res: return False

        self.sign()
        self.superWelfare_receiveRedPacket()
        self.get_SignTaskList()
        self.get_SignTaskList(True)

        self.get_honeyTaskListStart()
        self.honey_indexData()
        self.honey_indexData(True)

        activity_end_date = get_quarter_end_date()
        days_left = (activity_end_date - datetime.now()).days
        if days_left == 0:
            message = f"⏰ 今天采蜜活动截止兑换还有{days_left}天，请及时进行兑换！！"
            Log(message)
        else:
            message = f"⏰ 今天采蜜活动截止兑换还有{days_left}天，请及时进行兑换！！\n--------------------------------"
            Log(message)

        if not self.is_last_day and self.force_exchange:
            Log(f"⚡ 强制兑换模式已开启，兑换目标：{' > '.join(self.target_amounts)}")
            exchange_success = self.exchange_23_coupon()
            if not exchange_success:
                Log("❌ 强制兑换失败，所有目标券都无法兑换")

        current_date = datetime.now().day
        if 26 <= current_date <= 28:
            self.member_day_index()
        else:
            print('⏰ 未到指定时间不执行会员日任务\n==================================\n')

        return True


def get_quarter_end_date():
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    next_quarter_first_day = datetime(current_year, ((current_month - 1) // 3 + 1) * 3 + 1, 1)
    quarter_end_date = next_quarter_first_day - timedelta(days=1)

    return quarter_end_date


def is_activity_end_date(end_date):
    current_date = datetime.now().date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    return current_date == end_date


def main():
    APP_NAME = '顺丰速运'
    ENV_NAME = 'sfsyUrl'
    CK_NAME = 'url'
    local_script_name = os.path.basename(__file__)
    local_version = '2025.06.23'
    target_amounts = parse_exchange_range(EXCHANGE_RANGE)
    token = os.getenv(ENV_NAME)
    if not token:
        print(f"❌ 未找到环境变量 {ENV_NAME}，请检查配置")
        return
    tokens = token.split('&')
    tokens = [t.strip() for t in tokens if t.strip()]
    if len(tokens) == 0:
        print(f"❌ 环境变量 {ENV_NAME} 为空或格式错误")
        return

    print(f"==================================")
    print(f"🎉 呆呆粉丝后援会：996374999")
    print(f"🚚 顺丰速运脚本 v{local_version}")
    print(f"📱 共获取到{len(tokens)}个账号")
    print(f"🎯 兑换配置:")
    print(f"  └ 兑换区间: {EXCHANGE_RANGE} → {' > '.join(target_amounts)}")
    print(f"  └ 强制兑换: {'开启' if FORCE_EXCHANGE else '关闭'}")
    print(f"  └ 最大次数: {MAX_EXCHANGE_TIMES}")
    print(f"😣 修改By:呆呆呆呆")
    print(f"==================================")

    for index, infos in enumerate(tokens):
        run_result = RUN(infos, index).main()
        if not run_result: continue


if __name__ == '__main__':
    main()