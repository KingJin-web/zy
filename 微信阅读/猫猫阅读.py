
#
# 阅读入口：https://img.hnking.cn/blog/202508070115447.png微信扫码打开
# 配置说明：
# 1. 环境变量 mmyd_ck: 配置cookie账号信息bbus值，支持多账号分隔符：换行符、@、& 例如eyxxxxxxxxx 不要前面的bbus=
# 2. 环境变量 mmyd_ua: 配置UA信息      https://useragent.todaynav.com/ 微信打开此网站即可 请使用你的微信的User-Agent
# 3. 环境变量 mmyd_url: 检测文章提交接口的URL（可选，如http://192.168.124.201:9900/check_read）请使用自己的这个只是例子
# 4. 环境变量 mmyd_token: PushPlus推送加token（可选）
# 5. 环境变量 mmyd_tx: PushPlus推送加token（可选）
#
# 使用说明：
# - 首账号采用固定邀请码，请wx点击阅读入口。
# - 支持多账号批量运行，自动刷新Cookie
# - 自动检测文章并推送通知（需配置mmyd_token）
# - 自动提现功能，满足5000金币自动提现
# - 如果配置了mmyd_url，会先尝试自动过检，失败则推送通知
#
# 本脚本仅供学习交流，请在下载后的24小时内完全删除
# 请勿用于商业用途或非法目的，否则后果自负

"""获取当前 IP 地址"""
import requests
response = requests.get('https://httpbin.org/ip')
response.raise_for_status()
res = response.json().get('origin')
print(f"你的IP地址为：{res}")

# 测试区
# 临时设置环境变量
# os.environ["mmyd_ck"] = ""
#
# os.environ["mmyd_ua"] = ""
# os.environ["mmyd_url"] = ""
# os.environ["mmyd_token"] = ""

# 固定注释内容
fixed_comments = """# 猫猫阅读脚本 4.0
#
# 阅读入口：https://img.hnking.cn/blog/202508070115447.png 微信扫码打开
# 
# 配置说明：
# 1. 环境变量 mmyd_ck: 配置cookie账号信息bbus值，支持多账号分隔符：换行符、@、&
# 2. 环境变量 mmyd_ua: 配置UA信息      https://useragent.todaynav.com/ 微信打开此网站即可 请使用你的微信的User-Agent
# 3. 环境变量 mmyd_url: 检测文章提交接口的URL（可选，如http://192.168.124.201:9900/check_read）
# 4. 环境变量 mmyd_token: PushPlus推送加token（可选）
#
# 使用说明：
# - 首账号采用固定邀请码，请wx点击阅读入口。
# - 支持多账号批量运行，自动刷新Cookie
# - 自动检测文章并推送通知（需配置mmyd_token）
# - 自动提现功能，满足5000金币自动提现
# - 如果配置了mmyd_url，会先尝试自动过检，失败则推送通知
#
# 本脚本仅供学习交流，请在下载后的24小时内完全删除
# 请勿用于商业用途或非法目的，否则后果自负"""



import requests
import json
import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import re
import time
import random
from requests.exceptions import RequestException




# 创建全局 session




# 新增: PushPlus通知函数
def send_pushplus_notification(token, title, content):
    """使用PushPlus发送通知"""
    try:
        url_pushplus = "http://www.pushplus.plus/send"
        data_pushplus = {
            "token": token,
            "title": title,
            "content": content,
            "template": "html"
        }
        response = requests.post(url_pushplus, data=data_pushplus, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get("code") == 200:
            print(f"✅ PushPlus通知发送成功", flush=True)
        else:
            print(f"❗ PushPlus通知发送失败: {result.get('msg', '未知错误')}", flush=True)
    except Exception as e:
        print(f"❗ PushPlus通知请求异常: {str(e)}", flush=True)


def fetch_luodi_url(session):
    url = "http://thr.zuoanai.cn/baobaocode.php"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "Host": "thr.zuoanai.cn",
        "Referer": "http://thr.zuoanai.cn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
        "X-Requested-With": "XMLHttpRequest"
    }
    resp = session.get(url, headers=headers, timeout=15, proxies=proxies)
    resp.raise_for_status()
    data = resp.json()
    luodi_url = data.get("data", {}).get("luodi")
    print(f"获取到活动地址: {luodi_url}")
    return luodi_url


def get_first_redirect(luodi_url,session):
    parsed = urlparse(luodi_url)
    host = parsed.hostname
    path = parsed.path + (f"?{parsed.query}" if parsed.query else "")
    headers = {
        "Host": host,
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": UA_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/tpg,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "X-Requested-With": "com.tencent.mm",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    url = f"http://{host}{path}"
    resp = session.get(url, headers=headers, allow_redirects=False, timeout=15)
    if resp.status_code == 302:
        location = resp.headers.get('Location')
        # print(f"302跳转地址: {location}")
        parsed2 = urlparse(location)
        new_host = parsed2.hostname
        m = re.search(r'/haobaobao/([^/?]+)', parsed2.path)
        cid = m.group(1) if m else None
        # print(f"新域名: {new_host}, cid: {cid}")
        return new_host, cid
    else:
        print(f"未返回302，状态码: {resp.status_code}")
        print(resp.text)
        return None, None


def get_redirect_url(code, cid,session):
    url = f"http://soicq.hzyunyan.cn/blank_ground.html?type=bao&cid={cid}&code={code}&state=1"
    headers = {
        "Host": "soicq.hzyunyan.cn",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": UA_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "X-Requested-With": "com.tencent.mm",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    resp = session.get(url, headers=headers, allow_redirects=False, timeout=15)
    if resp.status_code == 302:
        location = resp.headers.get('Location')
        # print(f"redirect接口302 Location: {location}")
        return location
    else:
        print(f"redirect接口未返回302，状态码: {resp.status_code}")
        print(resp.text)
        return None


def get_bbus_from_url(bbus_url):
    # 处理q参数，去掉v前缀
    parsed = urlparse(bbus_url)
    qs = parse_qs(parsed.query)
    # 处理q参数
    if 'q' in qs and qs['q']:
        qval = qs['q'][0]
        if qval.startswith('v') and len(qval) > 1:
            qs['q'][0] = qval[1:]
    # 处理v参数，替换为当前时间戳减6小时2秒
    if 'v' in qs and qs['v']:
        now = int(time.time())
        v_new = now - (6 * 3600)
        qs['v'][0] = str(v_new)
    new_query = urlencode(qs, doseq=True)
    bbus_url = urlunparse(parsed._replace(query=new_query))
    headers = {
        "Host": parsed.hostname,
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": UA_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive"
    }
    resp = session.get(bbus_url, headers=headers, timeout=15)
    # print(resp.text)
    print(f"请求: {bbus_url}")
    print("--- 响应标头 ---")
    for k, v in resp.headers.items():
        print(f"{k}: {v}")
    set_cookie = resp.headers.get('Set-Cookie', '')
    m = re.search(r'bbus=([^;]+)', set_cookie)
    bbus = m.group(1) if m else None
    print(f"bbus: {bbus}")
    return bbus


def get_location_domain(cid, bbus, new_host,session):
    """
    1. GET /haobaobao/v{cid}?v=xxx，带 bbus cookie，获取 302 Location 域名
    返回 (location_url, location_domain)
    """
    v = int(time.time())
    url = f"http://{new_host}/haobaobao/v{cid}?v={v}"
    headers = {
        "Host": new_host,
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": UA_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/tpg,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "X-Requested-With": "com.tencent.mm",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": f"bbus={bbus}"
    }
    resp = session.get(url, headers=headers, allow_redirects=False, timeout=15)
    location = resp.headers.get('Location')
    if not location:
        print(f"未获取到Location，状态码: {resp.status_code}")
        return None, None
    # 提取域名
    parsed = urlparse(location)
    location_domain = parsed.hostname
    # print(f"Location: {location}\nLocation域名: {location_domain}")
    return location, location_domain


def post_mwtmpdomain(location_domain, bbus,session):
    """
    2. POST /mwtmpdomain，带 bbus cookie，返回 domain/sk
    """
    url = f"http://{location_domain}/mwtmpdomain"
    headers = {
        "Host": location_domain,
        "Connection": "keep-alive",
        "Content-Length": "0",
        "User-Agent": UA_USER_AGENT,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": f"http://{location_domain}",
        "Referer": f"http://{location_domain}/haobaobao/home?v=1751880944",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": f"bbus={bbus}"
    }
    resp = session.post(url, headers=headers, timeout=15)
    try:
        data = resp.json()
        domain_url = data['data']['domain']
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(domain_url)
        qs = parse_qs(parsed.query)
        sk = qs.get('sk', [None])[0]
        # print(f"domain: {domain_url}\nsk: {sk}")
        return domain_url, sk
    except Exception as e:
        print(f"解析domain/sk失败: {e}")
        return None, None


def get_user_url(cid, bbus, new_host,session):
    """
    综合流程：
    1. 通过 get_location_domain 获取 Location 域名
    2. 通过 post_mwtmpdomain 获取 domain/sk
    返回 domain_url, sk
    """
    location_url, location_domain = get_location_domain(cid, bbus, new_host,session)
    if not location_domain:
        return None, None
    domain_url, sk = post_mwtmpdomain(location_domain, bbus,session)
    return domain_url, sk


def get_article_link(host, sk,session):
    """
    获取文章link
    """
    now_ms = int(time.time() * 1000)
    mysign = random.randint(100, 999)
    vs = random.randint(100, 200)
    rmemakdk_url = f"http://{host}/smkrdeas?time={now_ms}&mysign={mysign}&vs={vs}&sk={sk}"
    headers = {
        "Host": host,
        "Connection": "keep-alive",
        "User-Agent": UA_USER_AGENT,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    # print(f"\n📖 请求文章任务: {rmemakdk_url}")
    resp = session.get(rmemakdk_url, headers=headers, timeout=15)
    return resp.json()


def visit_article_link(link,session):
    """
    访问文章link，模拟阅读
    """
    article_headers = {
        "User-Agent": UA_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }
    print(f"📖 开始模拟阅读文章...")
    resp = session.get(link, headers=article_headers, timeout=15)
    return resp


def submit_read_result(host, sk, sleep_time,session):
    """
    提交阅读完成
    """
    psign = random.randint(200, 400)
    jiajinbimao_url = f"http://{host}/jiajinbimao?time={sleep_time}&psign={psign}&sk={sk}"
    headers = {
        "Host": host,
        "Connection": "keep-alive",
        "User-Agent": UA_USER_AGENT,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    # print(f"📖 提交阅读完成")
    resp2 = session.get(jiajinbimao_url, headers=headers, timeout=15)
    return resp2.json()


def read_article(domain_url, sk):
    """
    1. GET /rmemakdk 获取文章link
    2. 请求link，等待20-30秒
    3. GET /jiajinbimao 获取阅读结果
    检测文章biz特殊处理：如biz在检测列表，等待120-130秒，提示手动阅读
    """
    check_biz_list = [
        "MzkzMTYyMDU0OQ==", "Mzk0NDcxMTk2MQ==",
        "MzkzNTYxOTgyMA==", "MzkzNDYxODY5OA==",
        "MzkwNzYwNDYyMQ==", "MzkyNjY0MTExOA==",
        "MzkwMTYwNzcwMw==", "Mzg4NTcwODE1NA==",
        "MzkyMjYxNzQ2NA==", "Mzk4ODQzNjU1OQ==",
        "MzkyMTc0MDU5Nw==", "Mzk4ODQzNzU3NA==",
        "Mzk5MDc1MDQzOQ==", "Mzg5ODIyOTI4MQ=="
    ]
    parsed = urlparse(domain_url)
    host = parsed.hostname
    # 1. 获取文章link
    try:
        data = get_article_link(host, sk,session)
        link = data.get('data', {}).get('link')
        if not link:
            if data.get('errcode') == 407:
                print('⚠️ 60分钟后可继续阅读！')
            elif data.get('errcode') == 405:
                print(f"❌ {data.get('msg')}")
            else:
                print(f"❌ 未获取到文章link: {data}")
            return False
        # print(f"✅ 获取到文章: {link}")
        # 提取biz
        biz_match = parse_qs(urlparse(link).query).get('__biz', [None])[0]
        print(f"文章标题: {biz_match}")
        print(f"📖 开始阅读: {link}", flush=True)
        # 检测文章特殊处理
        auto_checked = False
        if biz_match in check_biz_list or biz_match is None:
            wait_time = random.randint(120, 130)
            title = "⚠️ 猫猫检测文章！请在120s内完成阅读！"
            content = f"""
            ⚠️ 请在120s内完成阅读！
            ⚠️ 每次阅读不得少于8秒！
            文章链接：{link}
            当前时间 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}
            """
            # 自动过检逻辑
            auto_checked = False
            if API_URL:
                print(f"送入自动过检...")
                payload = {"url": link,"ck":bbus,"ua":UA_USER_AGENT,'version':'3.0'}
                try:
                    resp = requests.post(API_URL, json=payload, timeout=60).json()
                    if resp['status'] == 'success':
                        time.sleep(25)
                        print(f"✅ 自动过检成功，跳过推送")
                        auto_checked = True
                    else:
                        print(f"❌ 自动过检失败", resp['message'])
                except Exception as e:
                    print(f"自动过检请求异常: {e}")

            if not auto_checked:
                if PUSH_TOKEN:
                    print("开始推送文章...")
                    send_pushplus_notification(PUSH_TOKEN, title, content)
                else:
                    print("未配置推送token，尝试使用青龙配置文件推送")
                    print(QLAPI.notify(title, content))
                print(f"⏳ 检测文章等待 {wait_time} 秒...")
                time.sleep(wait_time)
            # 检测文章不请求link，但需要调用jiajinbimao接口
            sleep_time = random.randint(9, 18)
        else:
            # 2. 请求 link，等待20-30秒
            try:
                print(link)
                visit_article_link(link,session)
                sleep_time = random.randint(9, 18)
                print(f"⏳ 等待 {sleep_time} 秒模拟阅读...")
                time.sleep(sleep_time)
            except Exception as e:
                print(f"❌ 阅读文章请求失败: {e}")
                return False
        # 3. GET /jiajinbimao 获取阅读结果
        max_retries = 3
        for retry_count in range(max_retries):
            try:
                data2 = submit_read_result(host, sk, sleep_time,session)
                if data2.get('errcode') == 0:
                    d = data2.get('data', {})
                    print(
                        f"✅ 阅读完成！本次金币: {d.get('gold')}，今日已读: {d.get('day_read')}，今日金币: {d.get('day_gold')}，当前金币: {d.get('last_gold')}，剩余可读: {d.get('remain_read')}")
                    return True
                elif data2.get('errcode') == 405 and '未能获取到用户信息' in str(data2.get('msg')):
                    print(f"⚠️ 第 {retry_count + 1}/{max_retries} 次获取用户信息失败: {data2.get('msg')}，正在重试...")
                    if retry_count == max_retries - 1:
                        print(f"❌ 连续 {max_retries} 次用户信息获取失败，退出运行")
                        return False
                    time.sleep(2)
                    continue
                else:
                    print(f"❌ 阅读完成接口返回失败: {data2}")
                    return False
            except requests.exceptions.ReadTimeout:
                print(f"⏰ 第 {retry_count + 1}/{max_retries} 次请求超时，正在重试...")
                if retry_count == max_retries - 1:
                    print(f"❌ 连续 {max_retries} 次请求超时，退出运行")
                    return False
                time.sleep(2)
            except Exception as e:
                print(f"❌ 阅读完成接口请求失败: {e}")
                return False
    except Exception as e:
        print(f"❌ 解析文章任务响应失败: {e}")
        return False


def confirm_withdraw(domain_url, bbus, signid,session):
    """
    确认提现
    """
    from urllib.parse import urlparse
    host = urlparse(domain_url).hostname
    url = f"http://{host}/haobaobao/getwithdraw"
    headers = {
        "Host": host,
        "Connection": "keep-alive",
        "User-Agent": UA_USER_AGENT,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": f"http://{host}",
        "Referer": f"http://{host}/haobaobao/withdraw",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": f"bbus={bbus}",
        "X-Requested-With": "XMLHttpRequest"
    }
    data = f"signid={signid}&ua=2&ptype=0&paccount=&pname="
    # print(f"\n🔄 正在确认提现")
    resp = session.post(url, headers=headers, data=data, timeout=15)
    try:
        res_json = resp.json()
        if res_json.get('errcode') == 0:
            print("✅ 确认提现成功")
        else:
            if res_json.get('errcode') == 405:
                print(res_json.get('msg').replace("<br>", "\n"))
            else:
                print(f"❌ 确认提现失败: {res_json}")
    except Exception as e:
        print(f"❌ 确认提现响应解析失败: {e}")


def get_user_info_and_withdraw(domain_url, bbus,session):
    """
    获取用户信息并自动提现
    """
    from urllib.parse import urlparse
    host = urlparse(domain_url).hostname
    withdraw_url = f"http://{host}/haobaobao/withdraw"
    headers = {
        "Host": host,
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": UA_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/tpg,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "X-Requested-With": "com.tencent.mm",
        "Referer": f"http://{host}/haobaobao/home?v=1751942506",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": f"bbus={bbus}"
    }
    try:
        resp = session.get(withdraw_url, headers=headers, timeout=30)
    except requests.exceptions.ReadTimeout as e:
        print(f"[超时] 获取用户信息/提现页面超时: {e}")
        return None
    except Exception as e:
        print(f"[异常] 获取用户信息/提现页面失败: {e}")
        return None
    html = resp.text

    # 提取参数
    def extract_var(varname):
        m = re.search(rf'var {varname} ?= ?["\']?([^;"\']+)["\']?;', html)
        return m.group(1) if m else None

    request_id = extract_var('request_id')
    nickname = extract_var('nickname')
    qrcode_num = extract_var('qrcode_num')
    isallowtj = extract_var('isallowtj')
    # 提取金币
    m_gold = re.search(r'<p class="f_left" id="exchange_gold">(\d+)</p>', html)
    exchange_gold = int(m_gold.group(1)) if m_gold else 0
    print(f"用户ID: {nickname}")
    print(f"邀请人ID: {qrcode_num}")
    # print(f"是否可提现(isallowtj): {isallowtj}")
    print(f"当前金币: {exchange_gold}")
    # print(f"request_id: {request_id}")
    # 自动提现
    gold = (exchange_gold // 1000) * 1000
    if gold == 0 or not request_id:
        print("❌ 无法提现，金币不足或request_id缺失")
        return request_id
    if gold < MIN_WITHDRAW_GOLD:
        print(f"❌ 当前金币 {gold} 未达到提现门槛 {MIN_WITHDRAW_GOLD}，跳过提现")
        return request_id
    post_url = f"http://{host}/haobaobao/getgold"
    post_headers = headers.copy()
    post_headers.update({
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": f"http://{host}",
        "Referer": f"http://{host}/haobaobao/withdraw",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    })
    data = f"request_id={request_id}&gold={gold}"
    print(f"\n💸 正在发起提现，金币: {gold}")
    resp2 = session.post(post_url, headers=post_headers, data=data, timeout=15)
    try:
        res_json = resp2.json()
        if res_json.get('errcode') == 0:
            money = res_json.get('data', {}).get('money')
            print(f"✅ 提现成功，金额: {money}")
        else:
            if res_json.get('errcode') == 405:
                print(res_json.get('msg').replace("<br>", "\n"))
            else:
                print(f"❌ 提现失败: {res_json}")
    except Exception as e:
        print(f"❌ 提现响应解析失败: {e}")
    return request_id


def get_promotion_link(domain_url, bbus,session):
    """
    获取推广链接，输出qrcodes1和作者推广链接
    """
    from urllib.parse import urlparse

    host = urlparse(domain_url).hostname
    url = f"http://{host}/tiyvaewmk?v=1"
    headers = {
        "Host": host,
        "Connection": "keep-alive",
        "User-Agent": UA_USER_AGENT,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"http://{host}/haobaobao/showcode",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": f"bbus={bbus}"
    }
    try:
        resp = session.get(url, headers=headers, timeout=15)
        data = resp.json()
        if data.get('errcode') == 0:
            qrcodes1 = data.get('data', {}).get('qrcodes', {}).get('qrcodes1')
            if qrcodes1:
                # print(f"[🌟 推广链接] {qrcodes1}")
                # 输出作者推广链接
                # 替换kstief/后面的内容
                author_link = re.sub(r'(kstief/)[^/?]+(\?tsd=\d+)?', lambda m: m.group(1) + author_code, qrcodes1)
                print(f"[👨‍💻 作者推广链接] {author_link}")
            else:
                print("[❌ 推广链接] 未找到qrcodes1")
        else:
            print(f"[❌ 推广链接] 获取失败: {data}")
    except Exception as e:
        print(f"[❌ 推广链接] 请求异常: {e}")


def refresh_cookie(domain_url, bbus, session):
    """
    刷新cookie，GET /haobaobao/v1{author_code}?v=...，响应302为成功
    """
    from urllib.parse import urlparse
    import time
    host = urlparse(domain_url).hostname
    v = int(time.time())
    author_code = "1b69893ab98f0fd50e13e7d3e19d3c65"  # 与全局变量保持一致
    url = f"http://{host}/haobaobao/v1{author_code}?v={v}"
    headers = {
        "Host": host,
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": UA_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "X-Requested-With": "com.tencent.mm",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": f"bbus={bbus}"
    }
    try:
        resp = session.get(url, headers=headers, allow_redirects=False, timeout=10)
        if resp.status_code == 302:
            print(f"[Cookie刷新] 刷新成功")
            return True
        else:
            print(f"[Cookie刷新] {host} 刷新失败，状态码: {resp.status_code}")
            return False
    except Exception as e:
        print(f"[Cookie刷新] {host} 请求异常: {e}")
        return False


def enter_home(domain_url, bbus,session):
    """
    进入主页，返回True表示成功，False表示失败
    """
    try:
        import time
        from urllib.parse import urlparse
        host = urlparse(domain_url).hostname
        v = int(time.time())
        home_url = f"http://{host}/haobaobao/home?v={v}"
        headers = {
            "Host": host,
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": UA_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "X-Requested-With": "com.tencent.mm",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cookie": f"bbus={bbus}"
        }
        resp = session.get(home_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            # print(f"[主页] 进入主页成功")
            return True
        else:
            print(f"[Cookie刷新] Cookie刷新失败，状态码: {resp.status_code}")
            return False
    except Exception as e:
        print(f"[Cookie刷新] Cookie刷新请求异常: {e}")
        return False


def notice():
    try:
        response = requests.get("https://gitee.com/jdqlscript/zy/raw/master/label.txt", timeout=50)
        response.raise_for_status()
        print(response.text)
    except requests.RequestException as e:
        print(f"❗网络异常，获取通知时出错: {e}")



if __name__ == "__main__":
    notice()
    session = requests.Session()
    # ===== 全局变量配置区 =====
    MAX_RUNS = 30
    author_code = "668a330d2719521a88b79bf72adf6b05?tsd=246"
    MIN_WITHDRAW_GOLD = 5000  # 新增：提现所需最小金币数
    # API认证相关
    API_URL = os.getenv("mmyd_url")  # 检测文章提交接口URL
    PUSH_TOKEN = os.getenv("mmyd_token")  # PushPlus推送token
    UA_USER_AGENT = os.getenv("mmyd_ua")  # UA
    PROXY_URL = os.getenv("mmyd_proxy")  # 代理
    BBUS_LIST_OS = os.getenv(f"mmyd_ck")


    MULTI_ACCOUNT_SPLIT = ["\n", "@", "&"]  # 分隔符列表

    if not BBUS_LIST_OS:
        print("❌ 未配置cookie，程序无法继续执行，即将退出", flush=True)
        exit(1)
    BBUS_LIST = []
    if BBUS_LIST_OS:
        # 多分隔符分割
        split_pattern = '|'.join(map(re.escape, MULTI_ACCOUNT_SPLIT))
        bbus_items = [x for x in re.split(split_pattern, BBUS_LIST_OS) if x.strip()]
        print(f"🔍 从环境变量获取cookie: {len(bbus_items)} 个")
        BBUS_LIST.extend(bbus_items)

    print(f"从环境变量中获取到了，共{len(BBUS_LIST)}个账号")
    print(BBUS_LIST)
    # 检查自动过检配置
    if API_URL:
        print(f"✅ 已配置自动过检接口: {API_URL}")
    else:
        print("ℹ️ 未配置自动过检接口，检测文章将直接推送通知")

    # 检查推送token配置
    if PUSH_TOKEN:
        print(f"✅ 已配置推送token: {PUSH_TOKEN}")
    else:
        print("ℹ️ 未配置推送token，检测文章将不会推送通知")

    # 检查代理配置
    if PROXY_URL:
        print(f"✅ 已配置代理: {PROXY_URL}")
    else:
        print("ℹ️ 未配置代理，采用本地请求")

    # 最大运行次数，默认30次
    # MAX_RUNS = 30 # This line is removed as MAX_RUNS is now a global variable
    print(f"检测到共{len(BBUS_LIST)}个账号")
    for idx, bbus in enumerate(BBUS_LIST):
        proxies = {}
        if PROXY_URL:
            try:
                get_ip = requests.get(PROXY_URL).text
                proxies = {
                    "http": f"http://{get_ip}",
                    "https": f"http://{get_ip}",
                }
                session.proxies = proxies
            except Exception as e:
                print('获取代理失败，使用本地网络执行')


        print(f"\n{'=' * 10}🔰开始执行账号{idx + 1}🔰{'=' * 10}\n", flush=True)
        try:
            luodi_url = fetch_luodi_url(session)
        except requests.exceptions.ConnectionError as e:
            print(f"[连接错误] 获取活动地址失败: {e}")
            continue
        if not luodi_url:
            continue
        try:
            new_host, cid = get_first_redirect(luodi_url,session)
        except requests.exceptions.ConnectionError as e:
            print(f"[连接错误] 获取跳转地址失败: {e}")
            continue
        if not new_host or not cid:
            continue
        # 获取nLocation域名
        try:
            location_url, location_domain = get_location_domain(cid, bbus, new_host,session)
        except requests.exceptions.ConnectionError as e:
            print(f"[连接错误] 获取nLocation域名失败: {e}")
            continue
        if not location_domain:
            continue
        # 用nLocation域名拼成domain_url
        nlocation_domain_url = f"http://{location_domain}"
        # 刷新cookie
        try:
            refresh_cookie(nlocation_domain_url, bbus,session)
        except requests.exceptions.ConnectionError as e:
            print(f"[连接错误] 刷新cookie失败: {e}")
            continue
        # 刷新后进入主页
        try:
            enter_home(nlocation_domain_url, bbus, session)
        except requests.exceptions.ConnectionError as e:
            print(f"[连接错误] 进入主页失败: {e}")
            continue
        # 后续流程依然用原有domain_url, sk
        try:
            domain_url, sk = post_mwtmpdomain(location_domain, bbus,session)
        except requests.exceptions.ConnectionError as e:
            print(f"[连接错误] 获取domain_url/sk失败: {e}")
            continue
        # print(f"最终用户url: {domain_url}\nsk: {sk}")
        for run_count in range(1, MAX_RUNS + 1):
            print(f"\n🔄 第 {run_count}/{MAX_RUNS} 次运行")
            print("-" * 50)
            try:
                success = read_article(domain_url, sk)
            except requests.exceptions.ConnectionError as e:
                print(f"[连接错误] 阅读文章失败: {e}")
                break
            if not success:
                print(f"❌ 第 {run_count} 次运行失败")
                break
            # print(f"✅ 第 {run_count} 次运行完成")
            if run_count < MAX_RUNS:
                wait_time = random.randint(2, 5)
                print(f"⏳ 等待 {wait_time} 秒后继续下一次运行...")
                time.sleep(wait_time)
        print(f"\n🎉 账号运行完成！共运行 {run_count} 次")
        try:
            request_id = get_user_info_and_withdraw(nlocation_domain_url, bbus,session)
        except requests.exceptions.ConnectionError as e:
            print(f"[连接错误] 获取用户信息/提现失败: {e}")
            continue
        # 新增：获取推广链接
        try:
            get_promotion_link(nlocation_domain_url, bbus,session)
        except requests.exceptions.ConnectionError as e:
            print(f"[连接错误] 获取推广链接失败: {e}")
            continue
        time.sleep(random.randint(2, 3))
        try:
            confirm_withdraw(nlocation_domain_url, bbus, request_id,session)
        except requests.exceptions.ConnectionError as e:
            print(f"[连接错误] 确认提现失败: {e}")
            continue