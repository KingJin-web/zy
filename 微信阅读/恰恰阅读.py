# 配置说明：
# 1. 环境变量 QQ_TOKEN: 配置token账号信息支持多账号分隔符：#
# 2. 环境变量 qqyd_ua: 配置UA信息
# 3. 可配置过检测接口
# 4. 环境变量 qqyd_proxy: 配置代理连接，注意代理时长选择！注意代理时长选择！注意代理时长选择！同一账号运行时不要换ip（4.0更新内容）
# 活动入口 https://img.hnking.cn/blog/202509041844746.png


import time, json, random, requests, os
from urllib.parse import urlparse, parse_qs, unquote


PROXY_URL = os.getenv("qqyd_proxy")
UA_USER_AGENT = os.getenv("qqyd_ua")
# 配置
API_URL = ''  # 检测文章提交接口URL


def get_random_r():
    return str(random.uniform(0, 1))


def gettime():
    return str(int(time.time() * 1000))


def extract_biz(url):
    """从微信公众号文章链接中提取__biz参数值"""
    # 解析URL
    parsed_url = urlparse(url)

    # 解析查询参数
    query_params = parse_qs(parsed_url.query)

    # 提取__biz参数
    if '__biz' in query_params:
        return query_params['__biz'][0]
    else:
        return None


def getHomeInfo():
    """获取首页信息"""
    url = 'https://read.tslu.cn/abaaba/getHomeInfo/'
    params = {'token': TOKEN}
    headers = {
        'Host': 'read.tslu.cn',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': UA_USER_AGENT,
        'Origin': 'http://we.e9l.cn',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'http://we.e9l.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    try:
        response = requests.get(url, headers=headers, params=params, proxies=proxies).json()
        if response.get('code') == 0:
            home_data = response.get('data', {})
            print(
                f"首页信息 - 用户ID: {home_data.get('id', '未知')} | 累计阅读: {home_data.get('dayreads', 0)}天 | 金币: {home_data.get('gold', 0)}")
            return home_data
        else:
            print(f"首页信息获取失败: {response.get('msg', '未知错误')}")
    except Exception as e:
        print(f"首页信息请求异常: {str(e)}")
    return None


def extract_parameters(url):
    """从URL中提取t、ch、u参数"""
    # 解析URL
    parsed_url = urlparse(url)

    # 提取查询参数
    query_params = parse_qs(parsed_url.query)

    # 存储提取的参数
    params = {}

    # 检查是否有path参数需要解析
    if 'path=page/search/christmas_jump' in parsed_url.query and 'query=' in parsed_url.query:
        # 提取嵌套的URL
        for key, value in query_params.items():
            if key == 'query':
                nested_url = unquote(value[0])
                nested_parsed = urlparse(nested_url)
                nested_params = parse_qs(nested_parsed.query)

                # 提取嵌套URL中的参数
                for param in ['t', 'ch', 'u']:
                    if param in nested_params:
                        params[param] = nested_params[param][0]
                break
    else:
        # 直接从查询参数中提取
        for param in ['t', 'ch', 'u']:
            if param in query_params:
                params[param] = query_params[param][0]
    t = params.get('t', '')
    u = params.get('u', '')
    ch = params.get('ch', '')
    if t == '' or u == '' or ch == '':
        print(f"参数获取异常: {parsed_url}")
        exit(0)
    return t, u, ch


def getReadUrl():
    url = 'https://read.tslu.cn/abaaba/getReadUrl/'
    headers = {
        'Host': 'read.tslu.cn',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': UA_USER_AGENT,
        'Origin': 'http://we.e9l.cn',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'http://we.e9l.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    params = {'type': 2, 'b': str(int(time.time() * 1000)), 'token': TOKEN}

    try:
        response = requests.get(url, headers=headers, params=params, proxies=proxies).json()
        # print(f"url==={response['data']['url']}")
        return extract_parameters(response['data']['url'])
        # parsed_url = urlparse(response['data']['url'])
        # outer_params = parse_qs(parsed_url.query)
        # inner_url_encoded = outer_params.get('query', [''])[0]
        # inner_url = unquote(inner_url_encoded)
        # parsed_inner = urlparse(inner_url)
        # inner_params = parse_qs(parsed_inner.query)
        # print(inner_params)
        # t = inner_params.get('t', ['未获取t'])[0]
        # u = inner_params.get('u', ['未获取u'])[0]
        # ch = inner_params.get('ch', ['未获取ch'])[0]
        # return t, u, ch
    except Exception as e:
        print(f"参数获取异常: {str(e)}")
        return '未获取t', '未获取u', '未获取ch'





def check_article(aid, article_url):
    """文章检测逻辑"""
    print(f"检测文章 [ID:{aid}]")
    if not API_URL:
        print(f"未配置自动过检进入通知推送手动，请在面板配置文件设置对应推送..")
        title = "⚠️ QQ检测文章！请在120s内完成阅读！⚠️ 每次阅读不得少于8秒！"
        content = f"文章链接：{article_url}  当前时间 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 当前时间 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
        QLAPI.notify(title, content)
        time.sleep(60)
        return True
    else:
        try:
            resp = requests.post(API_URL,
                                 json={"url": article_url, 'token': TOKEN, 'ua': UA_USER_AGENT, 'proxies': proxies},
                                 timeout=60).json()
            if resp['status'] == 'success':
                time.sleep(8)
                print("✅ 自动过检成功")
                return True
            else:
                print(f"❌ 自动过检失败: {resp['message']}")
                return False
        except Exception as e:
            print(f"过检请求异常: {e}")
            return False


def sign_in():
    """执行签到"""
    print("\n--- 执行签到 ---")
    sign_url = "https://read.tslu.cn/abaaba/getxshd/"
    headers = {
        'Host': 'read.tslu.cn',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': UA_USER_AGENT,
        'Origin': 'http://we.e9l.cn',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'http://we.e9l.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    params = {'token': TOKEN}

    try:
        response = requests.get(sign_url, params=params, headers=headers, proxies=proxies).json()
        if response.get("code") == 0:
            print(f"签到成功! 获得金币: {response.get('golds', 0)}")
            getHomeInfo()  # 刷新金币显示
        else:
            print(f"签到失败: {response.get('msg', '未知错误')}")
    except Exception as e:
        print(f"签到请求异常: {str(e)}")
    print("--- 签到结束 ---\n")


def make_request(loop_count, initial_params, headers):
    """主循环请求逻辑"""
    url = "https://rdapi.hzjianyue.cn/api/articleTask0428"
    current_jkey = None
    current_params = initial_params.copy()
    current_c = 1
    user_id = initial_params.get("u", "")
    channel_id = initial_params.get("ch", "")

    for i in range(loop_count):
        print(f"\n[第{i + 1}次循环] c值: {current_c}")

        # 准备请求参数
        params = current_params.copy()
        params["c"] = current_c
        params["r"] = get_random_r()
        if i > 0 and current_jkey:
            params["jkey"] = current_jkey

        try:
            response = requests.get(url, params=params, headers=headers, proxies=proxies)
            response.raise_for_status()
            result = response.json()

            # 检测第5轮完成
            if result.get("code") == 1 and not result.get("data") and "第5轮已经完成" in result.get("msg", ""):
                print(f"检测到第5轮完成，任务结束!")
                sign_in()
                return

            # 检测其他轮次完成
            if result.get("code") == 1 and not result.get("data") and "轮已经完成" in result.get("msg", ""):
                print(f"轮次完成: {result.get('msg')}，终止循环")
                getHomeInfo()
                return

            # 检测其他轮次完成
            if result.get("code") == 1 and not result.get("data") and "暂时没有文章可供阅读" in result.get("msg", ""):
                print(f"轮次完成: {result.get('msg')}，终止循环")
                getHomeInfo()
                return

            # 检测其他轮次完成
            if result.get("code") == 1 and not result.get("data") and "您阅读数量已达今日上限" in result.get("msg", ""):
                print(f"轮次完成: {result.get('msg')}，终止循环")
                getHomeInfo()
                return

            # 检测其他轮次完成
            if result.get("code") == 1 and not result.get("data") and "前被微信判断为无效用户" in result.get("msg", ""):
                print(f"轮次完成: {result.get('msg')}，终止循环")
                getHomeInfo()
                return

            # 检测链接失效
            if result.get("code") == 1 and result.get("msg") == "当前链接已失效, 请获取最新链接哦" and not result.get(
                    "data"):
                print("链接失效，重新获取参数...")
                new_t, new_u, new_ch = getReadUrl()
                current_params.update({"t": new_t, "u": new_u, "ch": new_ch})
                user_id, channel_id = new_u, new_ch
                current_jkey = None
                current_c = 1
                continue

            # 处理正常响应
            if result.get("code") == 0:
                data = result.get("data", {})
                current_jkey = data.get("jkey")
                aid = data.get("aid", 0)
                article_url = data.get("url", "")

                _biz = extract_biz(article_url)
                print(f"📖 开始阅读: {article_url}", flush=True)
                print(f"文章信息 - : {_biz} | 已读/总数: {data.get('readNum', 0)}/{data.get('totalNum', 0)}")
                if _biz in ['MzkyNzYxMDA0Mw==', 'MzkzNzk3Mjk2MQ==', 'MzkyMjYxMDAwMA==', 'Mzk3NTc4MzI1NQ==',
                            'MzI5MjYyNDIxOA==', 'Mzk0OTYxMDEwNQ==', 'MzkzNjk3MjIxNg==', 'MzkzMTk0ODYxOQ==',
                            'MzkzODk3Mjk2NQ==', 'MzIwOTc0MzYxMg==', 'MzkyOTk0NzcyNw==', 'MzkxOTg4MjUzOA==',
                            'Mzk4ODQ2OTYyMg==',
                            'MzkzMjk3MDgxNQ==', 'MzkzOTYxMDQ2Mw==', 'MzkzODk0NzkwMg==', 'MzkwODYwOTUxOQ=='] or len(
                    current_jkey) > 35:
                    if not check_article(_biz, article_url):
                        return

                current_c += 1
            else:
                print(f"请求异常: {result.get('msg', '未知错误')}")
                current_c += 1

        except requests.exceptions.RequestException as e:
            print(f"网络请求错误: {e}")
            current_c += 1
        except json.JSONDecodeError:
            print("响应格式错误")
            current_c += 1

        # 延迟处理
        if i < loop_count - 1:
            delay = random.randint(8, 20)
            print(f"等待{delay}秒...")
            time.sleep(delay)

    print(f"\n所有{loop_count}次循环完成")
    getHomeInfo()


if __name__ == "__main__":
    QQ_TOKEN = os.getenv('QQ_TOKEN')
    if not QQ_TOKEN:
        print("请先配置账号信息(QQ_TOKEN)")
        exit()

    if UA_USER_AGENT:
        print(f"✅ 已配置ua: {UA_USER_AGENT}")
    else:
        print("ℹ️ 未配置ua，停止运行")
        exit()

    if PROXY_URL:
        print(f"✅ 已配置代理: {PROXY_URL}")
    else:
        print("ℹ️ 未配置代理，采用本地请求")

    TOKENS = QQ_TOKEN.split('#')
    print(f"共{len(TOKENS)}个账号")
    for TOKEN in TOKENS:
        proxies = {}
        if PROXY_URL:
            try:
                get_ip = requests.get(PROXY_URL).text.strip()
                print('获取代理：{0}'.format(get_ip))
                proxies = {
                    "http": f"http://{get_ip}",
                    "https": f"http://{get_ip}",
                }
            except Exception as e:
                print('获取代理失败，使用本地网络执行')
        getHomeInfo()  # 初始首页信息
        t, u, ch = getReadUrl()

        initial_params = {
            "t": t,
            "u": u,
            "ch": ch,
            "pageshow": "",
        }

        headers = {
            "Host": "rdapi.hzjianyue.cn",
            "Connection": "keep-alive",
            "User-Agent": UA_USER_AGENT,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "*/*",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        loop_times = 39
        print(f"\n开始执行{loop_times}次循环...")
        print(initial_params)
        make_request(loop_times, initial_params, headers)
