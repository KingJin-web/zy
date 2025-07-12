# cron: 10 */2 * * *
# new Env('携趣IP白名单');
import os

# 长期套餐大额流量电话卡办理地址：https://img.hnking.cn//blog/202504141427660.png
## 携趣代理地址 https://www.xiequ.cn/index.html?d630539f

# 携趣环境变量 export XIEQU='UID=xxx;UKEY=xxx'


import requests
import hashlib
import urllib.parse




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
# 携趣环境变量 export XIEQU='UID=xxx;UKEY=xxx' 

    ''')
    # 从青龙面板 获取变量
    # export XIEQU='UID=xxx;UKEY=xxx'

    XIEQU_UID = ''  # 填入携趣的 UID
    XIEQU_UKEY = ''  # 填入携趣的 UKEY


    XIEQU = os.getenv('XIEQU')
    if XIEQU != None:
        XIEQU_UID = XIEQU.split(';')[0].split('=')[1]
        XIEQU_UKEY = XIEQU.split(';')[1].split('=')[1]


    print('更新当前IP：', ip)
    if XIEQU_UID != None and XIEQU_UKEY != None:
        print('更新携趣白名单结果：', update_xiequ_white_list(ip, XIEQU_UID, XIEQU_UKEY))


if __name__ == "__main__":
    main()
