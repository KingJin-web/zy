# cron: 10 */2 * * *
# new Env('更新IP代理白名单');
import os

# 长期套餐大额流量电话卡办理地址：https://img.hnking.cn//blog/202504141427660.png

## 携趣代理地址 https://www.xiequ.cn/index.html?d630539f
## 星空代理地址 https://www.xkdaili.com/
## 巨量代理地址 https://www.juliangip.com/user/reg?inviteCode=1040216
# 携趣环境变量 export XIEQU='UID=xxx;UKEY=xxx'
# 星空环境变量 export XK='APIKEY=xxx;SIGN=xxx'
# 巨量环境变量 export JULIANG='KEY=xxx;TRADE_NO=xxx'

import requests
import hashlib
import urllib.parse



class SignKit:

    @staticmethod
    def md5_sign(params, secret):
        sign_content = SignKit.get_sign_content(params)
        return hashlib.md5((sign_content + '&key=' + secret).encode('utf-8')).hexdigest()

    @staticmethod
    def get_sign_content(params):
        params.pop('sign', None)  # 删除 sign
        sorted_params = sorted(params.items())
        sign_content = '&'.join(
            [f"{k}={str(v)}" for k, v in sorted_params if str(v) is not None and not str(v).startswith('@')])
        return sign_content


# def get_current_ip():
#     response = requests.get('https://myip.ipip.net/json')
#     data = response.json()
#     return data['data']['ip']
def get_current_ip():
    """获取当前 IP 地址"""
    try:
        response = requests.get('https://httpbin.org/ip')
        response.raise_for_status()
        res = response.json().get('origin')
        return res
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the current IP: {e}")
        return get_current_ip2()


# https://ip.3322.net

def get_current_ip2():
    api_url = f"https://ip.3322.net"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch information for IP: {e}")


def update_juliang_white_list(ip, JULIANG_KEY, JULIANG_TRADE_NO):
    if JULIANG_KEY and JULIANG_TRADE_NO:
        params = {
            'new_ip': ip,
            'reset': '1',
            'trade_no': JULIANG_TRADE_NO
        }
        sign = SignKit.md5_sign(params, JULIANG_KEY)
        query_string = urllib.parse.urlencode(params) + "&sign=" + sign

        url = f'http://v2.api.juliangip.com/dynamic/replaceWhiteIp?{query_string}'
        response = requests.get(url)
        return response.text


def update_xk_white_list(ip, XK_APIKEY, XK_SIGN):
    if XK_APIKEY and XK_SIGN:
        url = f'http://api2.xkdaili.com/tools/XApi.ashx?apikey={XK_APIKEY}&type=addwhiteip&sign={XK_SIGN}&flag=8&ip={ip}'
        response = requests.get(url)
        return response.text


def update_xiequ_white_list(ip, XIEQU_UID, XIEQU_UKEY):
    if XIEQU_UID and XIEQU_UKEY:
        url = f'http://op.xiequ.cn/IpWhiteList.aspx?uid={XIEQU_UID}&ukey={XIEQU_UKEY}&act=get'
        response = requests.get(url)
        data = response.text
        print(data)
        arr = data.split(',')
        print(arr)
        if ip in arr:
            return '携趣白名单ip未变化'
        if ip not in arr:
            requests.get(f'http://op.xiequ.cn/IpWhiteList.aspx?uid={XIEQU_UID}&ukey={XIEQU_UKEY}&act=del&ip=all')
            response = requests.get(
                f'http://op.xiequ.cn/IpWhiteList.aspx?uid={XIEQU_UID}&ukey={XIEQU_UKEY}&act=add&ip={ip}')
            return '更新xiequ白名单成功' if response.status_code == 200 else '更新xiequ白名单出错'
        else:
            return '携趣白名单ip未变化'


def main():
    ip = get_current_ip()


    print('当前ip地址：', ip)
    print('''#长期套餐大额流量电话卡办理地址：https://img.hnking.cn//blog/202504141427660.png
## 携趣代理地址 https://www.xiequ.cn/index.html?d630539f
## 星空代理地址 https://www.xkdaili.com/
## 巨量代理地址 https://www.juliangip.com/user/reg?inviteCode=1040216
# 携趣环境变量 export XIEQU='UID=xxx;UKEY=xxx' 
# 星空环境变量 export XK='APIKEY=xxx;SIGN=xxx'
# 巨量环境变量 export JULIANG='KEY=xxx;TRADE_NO=xxx'
    ''')
    # 从青龙面板 获取变量
    # export XIEQU='UID=xxx;UKEY=xxx'
    # export XK='APIKEY=xxx;SIGN=xxx'
    # export JULIANG='KEY=xxx;TRADE_NO=xxx'
    JULIANG_KEY = ''  # 填入巨量的 Key
    JULIANG_TRADE_NO = ''  # 填入巨量的 Trade No
    XK_APIKEY = ''  # 填入星空的 API Key
    XK_SIGN = ''  # 填入星空的 Sign
    XIEQU_UID = ''  # 填入携趣的 UID
    XIEQU_UKEY = ''  # 填入携趣的 UKEY

    JULIANG = os.getenv('JULIANG')
    XK = os.getenv('XK')
    XIEQU = os.getenv('XIEQU')
    if XIEQU != None:
        XIEQU_UID = XIEQU.split(';')[0].split('=')[1]
        XIEQU_UKEY = XIEQU.split(';')[1].split('=')[1]
    if JULIANG != None:
        JULIANG_KEY = JULIANG.split(';')[0].split('=')[1]
        JULIANG_TRADE_NO = JULIANG.split(';')[1].split('=')[1]
    if XK != None:
        XK_APIKEY = XK.split(';')[0].split('=')[1]
        XK_SIGN = XK.split(';')[1].split('=')[1]

    print('更新当前IP：', ip)
    if JULIANG_KEY != None and JULIANG_TRADE_NO != None:
        print('更新巨量白名单结果：', update_juliang_white_list(ip, JULIANG_KEY, JULIANG_TRADE_NO))
    if XK_APIKEY != None and XK_SIGN != None:
        print('更新星空白名单结果：', update_xk_white_list(ip, XK_APIKEY, XK_SIGN))
    if XIEQU_UID != None and XIEQU_UKEY != None:
        print('更新携趣白名单结果：', update_xiequ_white_list(ip, XIEQU_UID, XIEQU_UKEY))


if __name__ == "__main__":
    main()
