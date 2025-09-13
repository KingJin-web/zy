import time
import os
import requests
import json
import numpy as np
import urllib3
from datetime import datetime

################################################################################################
# 1.修复第一期因为时间太短而报错
# 2.优化部分代码

# 由 风华正太D猫 原脚本修改
#本脚本优点：多个账号在同一个群时，只需要修改XL_ID即可，原脚本每个号都需要修改活动id，你问我在不同群怎么办，那就用原脚本喽，另外原脚本环境变量设置有点问题
# 客服微信：yyttgi ，，，XL_ID每天都得改，不然运行不了
# 添加环境变量
# 抓包链接：https://fw1537.h5.sagx.net/detail.html?id=364f160eed5e4b404f2113a347c6a1af id=后面的不同，抓fw1537.h5.sagx.net的就行，抓不到cookie或者openid请刷新网页！！！
# ------------ 必填配置（三个注意大小写） ------------
# XL_HOST="api.h5.sagx.net" 应该是这个具体看你的群里发的链接，不要https，只要域名
# XL_ID="364f160eed5e4b404f2113a347c6a1af"  id=,只要=后面的
# xlwy="wx_openid1#主账号&wx_openid2#测试账号"  抓包链接抓cookie中的O=，只要=后面的
# 抓不到cookie或者openid请刷新网页！！！
# 示例抓包图 https://img.vki.im/file/1747740497098_image_1747740493580.jpg 
# 如果真的是看了图还不会，再说话吧
################################################################################################

COLOR = {
    "RED": "\033[38;5;124m",
    "GREEN": "\033[38;5;22m",
    "BLUE": "\033[38;5;19m",
    "YELLOW": "\033[38;5;130m",
    "CYAN": "\033[38;5;23m",
    "BOLD": "\033[1m",
    "END": "\033[0m"
}

def log_info(msg, emoji="ℹ️"):
    print(f"{COLOR['BLUE']}[{datetime.now().strftime('%H:%M:%S')}] {emoji} INFO  - {msg}{COLOR['END']}")

def log_success(msg, emoji="✅"):
    print(f"{COLOR['GREEN']}[{datetime.now().strftime('%H:%M:%S')}] {emoji} SUCCESS - {msg}{COLOR['END']}")

def log_warning(msg, emoji="⚠️"):
    print(f"{COLOR['YELLOW']}[{datetime.now().strftime('%H:%M:%S')}] {emoji} WARN  - {msg}{COLOR['END']}")

def log_error(msg, emoji="❌"):
    print(f"{COLOR['RED']}[{datetime.now().strftime('%H:%M:%S')}] {emoji} ERROR - {msg}{COLOR['END']}")

def log_debug(data, emoji="🐛"):
    print(f"{COLOR['CYAN']}[{datetime.now().strftime('%H:%M:%S')}] {emoji} DEBUG - 响应数据:\n{json.dumps(data, indent=2, ensure_ascii=False)}{COLOR['END']}")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AccountResult:
    def __init__(self):
        self.total_accounts = 0
        self.success_count = 0
        self.fail_count = 0
        self.rewards = {}
        self.details = {}

    def add_success(self, wx_openid, remark, reward):
        self.success_count += 1
        self.rewards[wx_openid] = reward
        self.details[wx_openid] = {'remark': remark, 'reward': reward, 'status': '成功'}

    def add_fail(self, wx_openid, remark):
        self.fail_count += 1
        self.rewards[wx_openid] = 0.0
        self.details[wx_openid] = {'remark': remark, 'reward': 0.0, 'status': '失败'}

    def total_reward(self):
        return sum(self.rewards.values())

class Config:
    def __init__(self):
        self.XL_HOST = os.getenv("XL_HOST")
        self.XL_ID = os.getenv("XL_ID")
        self.XL_USER_LIST = os.getenv("xlwy", "").split("&")
        self.XL_MIN_SEGMENT = int(os.getenv("XL_MIN_SEGMENT", "300"))
        self.XL_MAX_SEGMENT = int(os.getenv("XL_MAX_SEGMENT", "1800"))
        self.XL_TIMEOUT = int(os.getenv("XL_TIMEOUT", "15"))
        self.XL_RETRY = int(os.getenv("XL_RETRY", "3"))
        self.XL_DELAY_MIN = int(os.getenv("XL_DELAY_MIN", "5"))   # 新增最小延迟
        self.XL_DELAY_MAX = int(os.getenv("XL_DELAY_MAX", "15"))  # 新增最大延迟

def validate_config(cfg):
    errors = []
    if not cfg.XL_HOST: errors.append("XL_HOST 未配置")
    if not cfg.XL_ID: errors.append("XL_ID 未配置")
    if not cfg.XL_USER_LIST or any(len(u.split('#')) != 2 for u in cfg.XL_USER_LIST):
        errors.append("xlwy 格式错误，应为 wx_openid#备注")
    if cfg.XL_DELAY_MIN > cfg.XL_DELAY_MAX:
        errors.append("延迟范围配置错误（MIN > MAX）")
    return errors

def random_delay(min_sec=0.5, max_sec=2.0):
    """生成随机延迟"""
    delay = np.random.uniform(min_sec, max_sec)
    time.sleep(delay)
    return delay

def parse_video_time(time_str):
    try:
        hms, _ = time_str.split('.')
        hours, mins, secs = hms.split(':')
        return int(hours)*3600 + int(mins)*60 + int(secs)
    except:
        log_warning(f"视频时长解析失败，使用默认值1小时")
        return 3600

def simulate_watch_time(headers, user_activity_id, xlhost, cfg, video_time):
    log_info(f"🎬 视频实际时长: {video_time//60}分{video_time%60}秒")
    
    segments = []
    remaining = video_time
    
    # 分段逻辑保持不变
    while remaining > 0:
        max_seg = min(cfg.XL_MAX_SEGMENT, remaining)
        min_seg_candidate = max(cfg.XL_MIN_SEGMENT, remaining // 3)
        min_seg = min(min_seg_candidate, max_seg)
        
        if min_seg >= max_seg:
            segment = max_seg
        else:
            if max_seg - min_seg <= 0:
                segment = max_seg
            else:
                segment = np.random.randint(min_seg, max_seg + 1)
        
        segments.append(segment)
        remaining -= segment
        
        if len(segments) >=2 and remaining < cfg.XL_MIN_SEGMENT:
            segments[-1] += remaining
            remaining = 0
    
    if len(segments) > 1:
        first = segments.pop(0)
        np.random.shuffle(segments)
        segments.insert(0, first)
    
    for idx, sec in enumerate(segments, 1):
        for attempt in range(cfg.XL_RETRY):
            try:
                # 添加分段上报前的随机延迟
                if idx > 1:
                    d = random_delay(0.3, 1.2)
                    log_debug(f"分段上报前延迟: {d:.2f}秒")
                
                res = requests.post(
                    f"https://{xlhost}/api-user/v1/activityWatchVideo",
                    json={"userActivityId": user_activity_id, "second": sec},
                    headers=headers,
                    verify=False,
                    timeout=cfg.XL_TIMEOUT
                )
                if res.json().get("status") == "success":
                    log_info(f"  第{idx}次上报 | 时长: {sec//60}分{sec%60}秒 | 累计: {sum(segments[:idx])//60}分")
                    break
                else:
                    log_warning(f"上报失败: {res.json().get('message')} | 第{attempt+1}次重试")
            except Exception as e:
                log_warning(f"网络异常: {str(e)} | 第{attempt+1}次重试")
        time.sleep(np.random.uniform(0.5, 1.5))
    
    return video_time

def main():
    cfg = Config()
    if errors := validate_config(cfg):
        for err in errors: log_error(err)
        exit()

    result = AccountResult()
    result.total_accounts = len(cfg.XL_USER_LIST)

    log_info(f"{COLOR['BOLD']}🚀 脚本启动 | 域名: {cfg.XL_HOST} | 课程ID: {cfg.XL_ID}{COLOR['END']}")
    log_info(f"📊 待处理账号: {result.total_accounts} 个")
    log_info(f"⏱️ 账号间延迟: {cfg.XL_DELAY_MIN}-{cfg.XL_DELAY_MAX}秒")

    for idx, user in enumerate(cfg.XL_USER_LIST, 1):
        wx_openid, remark = user.split('#')
        current_reward = 0.0
        log_info(f"\n{COLOR['BOLD']}🔢 处理进度: {idx}/{result.total_accounts} [账号尾号: {wx_openid[-4:]}] [备注: {remark}]{COLOR['END']}")

        try:
            headers = {
                "Host": cfg.XL_HOST,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
                "Content-Type": "application/json",
                "Referer": f"https://{cfg.XL_HOST}/activity/index.html?id={cfg.XL_ID}&code=0&state=STATE"
            }

            # Token获取
            token = None
            for retry in range(cfg.XL_RETRY):
                try:
                    token_res = requests.post(
                        f"https://{cfg.XL_HOST}/api-user/v2/getToken",
                        headers=headers,
                        json={"wx_openid": wx_openid, "id": cfg.XL_ID},
                        verify=False,
                        timeout=cfg.XL_TIMEOUT
                    )
                    token_data = token_res.json()
                    if token_res.status_code == 200 and token_data.get("status") == "success":
                        token = token_data["data"]["token"]
                        headers["Authorization"] = f"Bearer {token}"
                        log_success(f"🔑 Token获取成功 ({token[:6]}***)")
                        # Token获取后延迟
                        d = random_delay(1.0, 3.0)
                        log_debug(f"Token获取后延迟: {d:.2f}秒")
                        break
                    else:
                        log_error(f"Token错误: {token_data.get('message', '未知错误')}")
                except Exception as e:
                    log_warning(f"Token请求异常: {str(e)}")
                if retry < cfg.XL_RETRY - 1:
                    time.sleep(2)
            if not token:
                result.add_fail(wx_openid, remark)
                continue

            # 获取活动详情前延迟
            random_delay(0.5, 1.5)
            detail_res = requests.get(
                f"https://{cfg.XL_HOST}/api-user/v2/activityDetatil",
                headers=headers,
                params={"id": cfg.XL_ID, "withMaterial": "1"},
                verify=False,
                timeout=cfg.XL_TIMEOUT
            )
            detail_data = detail_res.json()
            
            if detail_res.status_code != 200 or "data" not in detail_data:
                log_error(f"活动详情获取失败 HTTP {detail_res.status_code}")
                result.add_fail(wx_openid, remark)
                continue

            # 解析视频信息
            video_time_str = detail_data["data"]["media"]["media_v_time"]
            video_total_sec = parse_video_time(video_time_str)

            # 解析答案
            questions = detail_data["data"]["materialDetail"].get("questions", [])
            answer_keys = []
            for q_idx, question in enumerate(questions, 1):
                answers = question.get("answer", [])
                correct_index = next((i for i, a in enumerate(answers) if a.get("result") == "1"), None)
                if correct_index is None:
                    log_error(f"第{q_idx}题未找到正确答案")
                    answer_keys = []
                    break
                answer_keys.append(f"{q_idx-1}_{correct_index}")
                log_success(f"第{q_idx}题答案: 选项[{correct_index}] {answers[correct_index].get('item')}")

            if not answer_keys:
                result.add_fail(wx_openid, remark)
                continue

            # 上报观影时间
            user_activity_id = detail_data["meta"]["joinInfo"]["userActivityId"]
            total_time = simulate_watch_time(headers, user_activity_id, cfg.XL_HOST, cfg, video_total_sec)
            
            # 完成观影后延迟
            d = random_delay(0.5, 2.0)
            log_debug(f"观影完成延迟: {d:.2f}秒")
            over_res = requests.post(
                f"https://{cfg.XL_HOST}/api-user/v1/activityWatchVideoOver",
                json={"userActivityId": user_activity_id},
                headers=headers,
                verify=False
            )
            log_success(f"✅ 观影完成 | 总时长: {total_time//60}分{total_time%60}秒")

            # 领取奖励前延迟
            random_delay(1.0, 2.0)
            reward_res = requests.post(
                f"https://{cfg.XL_HOST}/api-user/v1/receiveAwardAndWatchOver",
                headers=headers,
                data=json.dumps({
                    "activity_id": detail_data["data"]["activity_id"],
                    "answers": answer_keys
                }, separators=(',', ':'))
            )
            reward_data = reward_res.json()
            
            if reward_data.get("status") in ["success", "领取成功"] or reward_data.get("status_code") == 200:
                current_reward = float(reward_data["data"].get("red_money", 0))
                result.add_success(wx_openid, remark, current_reward)
                log_success(f"💰 实际到账: ¥{current_reward:.2f}")
            else:
                result.add_fail(wx_openid, remark)
                log_error(f"领取失败: {reward_data.get('message', '未知错误')}")

        except Exception as e:
            result.add_fail(wx_openid, remark)
            log_error(f"处理异常: {str(e)}")
        
        # 账号间随机延迟
        delay = np.random.randint(cfg.XL_DELAY_MIN, cfg.XL_DELAY_MAX + 1)
        log_info(f"⏸️ 随机延迟 {delay} 秒（范围: {cfg.XL_DELAY_MIN}-{cfg.XL_DELAY_MAX}）...")
        time.sleep(delay)

    # 结果汇总
    log_info(f"\n{COLOR['BOLD']}📈 执行汇总 {COLOR['END']}")
    log_info(f"   账号总数: {result.total_accounts}")
    log_success(f"   成功数量: {result.success_count}")
    if result.fail_count > 0:
        log_error(f"   失败数量: {result.fail_count}")
    else:
        log_info(f"   失败数量: 0")
    log_success(f"   累计总收益: ¥{result.total_reward():.2f}")

    log_info(f"\n{COLOR['BOLD']}📋 账号明细 {COLOR['END']}")
    for wx_openid, info in result.details.items():
        status_color = COLOR['GREEN'] if info['status'] == '成功' else COLOR['RED']
        log_info(
            f"   OpenID尾号: {wx_openid[-4:]} | "
            f"备注: {info['remark']} | "
            f"状态: {status_color}{info['status']}{COLOR['END']} | "
            f"收益: ¥{info['reward']:.2f}"
        )

if __name__ == "__main__":
    main()