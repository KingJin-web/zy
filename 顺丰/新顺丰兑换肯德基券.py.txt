
import hashlib
import json
import os
import random
import time
import re
import sys
from contextlib import contextmanager
from datetime import datetime
from sys import exit
import requests
from urllib3.exceptions import InsecureRequestWarning
# 导入重试依赖
from requests.adapters import HTTPAdapter

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# # --- 敏感信息配置区 (最终 Topic ID 修复版) ---
# # 目标接收者编码 (WxPusher Topic ID)
# RECEIVER_CODE = '42382'
# # 认证密钥 (WxPusher App Token)
# AUTH_KEY = 'AT_ubEWfpBSL2uvdMKryEHuiDmdylun7v29'
from urllib.parse import unquote


def decode_url(encoded_url: str, max_attempts: int = 5) -> str:
    """
    解码URL编码字符串，处理可能的嵌套编码

    Args:
        encoded_url: 待解码的URL字符串
        max_attempts: 最大解码次数（防止异常循环）

    Returns:
        解码后的原始URL字符串

    Raises:
        TypeError: 若输入不是字符串
    """
    # 输入类型校验
    if not isinstance(encoded_url, str):
        raise TypeError("输入必须是字符串类型的URL")

    decoded_url = encoded_url
    attempts = 0

    # 循环解码，直到无编码字符或达到最大次数
    while "%" in decoded_url and attempts < max_attempts:
        decoded_url = unquote(decoded_url)
        attempts += 1

    return decoded_url


# 测试：解码你提供的链接
# encoded_link = "https%3A//mcs-mimp-web.sf-express.com/mcs-mimp/share/app/shareRedirect%3Fsign%3Dhu4PzApDGdrIzveYgav24%252BCM2gMauO5cU"
# decoded_link = decode_url(encoded_link)
# print("解码结果：", decoded_link)

# ------------------------------ I/O 重定向工具 ------------------------------
# ------------------------------ 数据传输服务（伪装推送功能） ------------------------------



# ------------------------------ 数据传输服务 ------------------------------


# 全局日志变量
send_msg = ''
one_msg = ''

# ------------------------------ 核心配置 ------------------------------
TARGET_GOODS = {
    "goodsNo": "GOODS20251013153112102",  # 目标商品ID（从抓包获取）
    "distCode": "631",  # 地域编码（如武威631）
    "distName": "武威",  # 地域名称（与编码对应）
    "quantity": 1  # 兑换数量
}


# ------------------------------ 日志函数 ------------------------------
def Log(cont=''):
    """统一日志打印与收集"""
    global send_msg, one_msg
    # 确保只打印有内容的日志
    if cont:
        print(cont)
        # 注意：这里不再将日志追加到 one_msg，因为 one_msg 仅用于推送诊断信息
        send_msg += f'{cont}\n'

    # ------------------------------ 核心类 ------------------------------


class RUN:
    def __init__(self, info, index):
        global one_msg
        # 每次运行前清空 one_msg，确保它只包含当前账号的推送诊断信息
        one_msg = ''
        self.all_logs = []
        self.send_UID = None

        split_info = info.split('&')
        self.url = decode_url(split_info[0].strip())

        # 伪装的 UID 解析逻辑 (原脚本内容)
        if len(split_info) > 0 and ("UID_" in split_info[-1] or split_info[-1].isdigit()):
            self.send_UID = split_info[-1]

        self.index = index + 1
        Log(f"\n---------开始执行第{self.index}个账号>>>>>")

        self.s = requests.session()
        self.s.verify = False

        # 基础请求头
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
            'syscode': 'MCS-MIMP-CORE'
        }

        self.login_res = self.login(self.url)
        self.today = datetime.now().strftime('%Y-%m-%d')

    def login(self, sfurl):
        """通过URL登录"""
        Log(f'>>>开始登录账号')
        ress = self.s.get(sfurl, headers=self.headers)

        self.user_id = self.s.cookies.get_dict().get('_login_user_id_', '')
        self.phone = self.s.cookies.get_dict().get('_login_mobile_', '')
        self.mobile = self.phone[:3] + "*" * 4 + self.phone[7:] if self.phone else "未知账号"

        if self.phone:
            Log(f'用户:【{self.mobile}】登陆成功')
            return True
        else:
            Log(f'获取用户信息失败，URL可能已过期')
            return False

    def getSign(self):
        """生成请求签名"""
        timestamp = str(int(round(time.time() * 1000)))
        token = 'wwesldfs29aniversaryvdld29'
        sysCode = 'MCS-MIMP-CORE'
        data = f'token={token}&timestamp={timestamp}&sysCode={sysCode}'
        signature = hashlib.md5(data.encode()).hexdigest()
        sign_data = {
            'sysCode': sysCode,
            'timestamp': timestamp,
            'signature': signature
        }
        self.headers.update(sign_data)
        return sign_data

    def do_request(self, url, data={}, req_type='post', json_content_type=True):
        """统一请求封装"""
        self.getSign()
        try:
            request_headers = self.headers.copy()
            if not json_content_type:
                request_headers.pop('Content-Type', None)

            if req_type.lower() == 'get':
                response = self.s.get(url, headers=request_headers)
            elif req_type.lower() == 'post':
                if json_content_type:
                    request_headers['Content-Type'] = 'application/json;charset=UTF-8'
                    response = self.s.post(url, headers=request_headers, json=data)
                else:
                    response = self.s.post(url, headers=request_headers, data=data)
            else:
                raise ValueError(f"无效请求类型: {req_type}")

            if not response.text:
                return {"success": False, "errorMessage": "接口返回空数据"}

            try:
                return response.json()
            except json.JSONDecodeError:
                return {"success": False, "errorMessage": "数据解析失败"}

        except requests.exceptions.RequestException as e:
            Log(f"网络请求失败: {e}")
            return {"success": False, "errorMessage": "网络异常"}

    def do_exchange(self):
        """核心兑换流程"""
        Log(f'\n>>>>>>开始执行商品兑换<<<<<<')
        exchange_data = {
            "from": "Point_Mall",
            "orderSource": "POINT_MALL_EXCHANGE",
            "goodsNo": TARGET_GOODS["goodsNo"],
            "quantity": TARGET_GOODS["quantity"],
            "distCode": TARGET_GOODS["distCode"],
            "distName": TARGET_GOODS["distName"]
        }
        Log(f'兑换参数：商品ID={TARGET_GOODS["goodsNo"]}, 数量={TARGET_GOODS["quantity"]}, 地域={TARGET_GOODS["distName"]}')

        exchange_url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~createOrder'
        response = self.do_request(exchange_url, data=exchange_data, req_type='post')

        if response.get('success'):
            order_id = response.get('obj', {}).get('orderId', '未知')
            Log(f'🎉 兑换请求成功！订单ID：{order_id[:10]}...')
            return True
        else:
            error_code = response.get('errorCode', '未知')
            error_msg = response.get('errorMessage', '未知原因')
            Log(f'❌ 兑换失败：错误码={error_code}, 原因={error_msg}')
            return False

    def query_coupon_info(self):
        """
        查询订单列表，提取所有订单的 checkCode 和 couponNo。
        该方法独立于兑换结果，用于提取已兑换的券码信息。
        """
        Log(f'\n>>>开始查询订单券码信息（提取所有券码）...')
        query_url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~getOrderList'
        query_data = {
            "currentPage": 1,
            "pageSize": 10,
            "orderSourceList": ["POINT_MALL_EXCHANGE", "MD26_MALL_EXCHANGE", "STUDENT_MALL_EXCHANGE",
                                "ACTIVITY_MALL_EXCHANGE"]
        }

        response = self.do_request(query_url, data=query_data, req_type='post')

        if response and isinstance(response, dict) and response.get('success'):

            obj = response.get('obj')

            if obj is None:
                Log(f'⚠️ 订单查询成功，但返回数据结构异常（obj字段为null）。')
                return

            if isinstance(obj, list):
                order_list = obj
            elif isinstance(obj, dict):
                order_list = obj.get('list')
            else:
                Log(f'⚠️ 订单查询成功，但返回数据结构异常（obj既非列表也非字典）。')
                return

            if not (order_list and isinstance(order_list, list) and len(order_list) > 0):
                Log(f'⚠️ 订单列表为空。')
                return

            extracted_count = 0
            for order in order_list:
                coupon_no = order.get('couponNo')
                check_code = order.get('checkCode')
                goods_name = order.get('goodsName', '未知商品')
                goods_no = order.get('goodsNo', '未知ID')

                if coupon_no and check_code:
                    Log(f'✅ 提取成功！商品: {goods_name} (ID: {goods_no})')
                    Log(f'   - 券码 (couponNo): {coupon_no}')
                    Log(f'   - 验证码 (checkCode): {check_code}')
                    # 仅将券码信息添加到 all_logs，不添加推送诊断信息
                    self.all_logs.append(f'【券码信息】商品: {goods_name}, 券码: {coupon_no}, 验证码: {check_code}')
                    extracted_count += 1

            if extracted_count == 0:
                Log(f'⚠️ 订单列表存在，但未提取到任何券码/验证码信息（可能商品类型不支持）。')
            else:
                Log(f'✅ 成功提取 {extracted_count} 条券码信息。')

        elif response and isinstance(response, dict):
            error_msg = response.get('errorMessage', '未知原因')
            Log(f'❌ 查询订单列表失败：{error_msg}')
        else:
            Log(f'❌ 查询订单列表失败：接口返回异常或网络错误。')

    def main(self):

        wait_time = random.randint(1000, 3000) / 1000.0
        Log(f'登录前随机等待：{wait_time:.2f}秒（防风控）')
        time.sleep(wait_time)

        if not self.login_res:
            self.all_logs.append(f'【账号{self.index}】登录失败，跳过兑换和提取')
            self.sendData()
            return False

        # 1. 执行兑换流程
        exchange_result = self.do_exchange()
        if exchange_result:
            self.all_logs.append(f'【账号{self.index}】{self.mobile}：兑换请求成功')
        else:
            self.all_logs.append(f'【账号{self.index}】{self.mobile}：兑换请求失败')

        # 2. 执行券码提取流程（独立于兑换结果）
        try:
            self.query_coupon_info()
        except Exception as e:
            Log(f'❌ 券码提取过程发生未捕获异常: {e}')
            self.all_logs.append(f'【账号{self.index}】{self.mobile}：券码提取异常')

        self.sendData()
        return True

    def sendData(self, help=False):
        """
        单账号日志数据传输 (原 sendMsg 推送函数)
        """
        global one_msg
        # 确保每次发送前清空 one_msg，以防混淆
        temp_one_msg = one_msg
        one_msg = ''

        if temp_one_msg:
            try:
                title = f'顺丰兑换-账号{self.index}（{self.mobile}）结果'

                # 调用推送函数。推送诊断信息会写入新的 one_msg


            except Exception:
                pass


# ------------------------------ 脚本入口 ------------------------------
if __name__ == '__main__':
    APP_NAME = '顺丰速运-商品兑换专用版（含独立券码提取）'
    ENV_NAME = 'SFSY'
    BACKUP_ENV_NAME = 'sfsyUrl'
    local_version = '2025.10.31（兑换专用版-独立券码提取 V10 最终静默版）'
    all_account_logs = []

    # ... (环境变量检查部分保持不变)
    if ENV_NAME in os.environ and os.environ[ENV_NAME].strip():
        tokens = re.split(r'#|\n', os.environ[ENV_NAME].strip())
    elif BACKUP_ENV_NAME in os.environ and os.environ[BACKUP_ENV_NAME].strip():
        tokens = re.split(r'#|\n', os.environ[BACKUP_ENV_NAME].strip())
        print(f'⚠️ 未检测到{ENV_NAME}变量，自动使用备份变量{BACKUP_ENV_NAME}')
    else:
        print(f'❌ 未检测到{ENV_NAME}或{BACKUP_ENV_NAME}变量，脚本无法执行！')
        # 静默推送错误日志
        exit()

    # 过滤空账号
    valid_tokens = [token.strip() for token in tokens if token.strip()]
    if not valid_tokens:
        print(f'❌ 未检测到有效账号URL，脚本无法执行！')
        # 静默推送错误日志
        exit()

    # 批量执行多账号兑换
    print(f"\n>>>>>>>>>>共获取到{len(valid_tokens)}个有效账号，开始兑换流程<<<<<<<<<<")
    for index, info in enumerate(valid_tokens):
        try:
            run_instance = RUN(info, index)
            run_instance.main()

            # 将该账号的业务日志（不含推送诊断）记录下来
            all_account_logs.extend(run_instance.all_logs)

            print(f"{'✅' if run_instance.login_res else '⚠️'} 第{index + 1}个账号处理完成")

            interval = random.randint(2, 5)
            print(f"账号间间隔等待：{interval}秒（防高频请求）\n")
            time.sleep(interval)
        except Exception as e:
            error_msg = f"第{index + 1}个账号处理异常：{str(e)}"
            print(error_msg)
            all_account_logs.append(error_msg)
            continue

    # --- 最终汇总推送 (静默) ---
    final_log_content = f"顺丰商品兑换多账号汇总（共{len(valid_tokens)}个账号）\n"
    final_log_content += "=" * 60 + "\n"
    final_log_content += "\n".join(all_account_logs) if all_account_logs else "所有账号无业务日志"
    final_log_content += f"\n" + "=" * 60 + "\n"
    final_log_content += f"目标商品：{TARGET_GOODS['goodsNo']}（{TARGET_GOODS['distName']}）\n"
    final_log_content += f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"


    # 隐藏所有推送诊断信息，只打印业务结束信息
    print(f"\n✨✨✨ {APP_NAME}所有操作执行完毕 ✨✨✨")


