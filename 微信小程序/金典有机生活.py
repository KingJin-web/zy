import base64
'''#
复制微信小程序链接:#小程序://金典有机生活+/IOS93RRB7klnqOg
打开链接进入小程序抓包搜zyhd的链接
#'''
# 1. 在青龙面板 → 环境变量 中添加：
# 变量名：JD_HOLIDAY_ACCOUNTS
# 变量值：每行一个账号，格式为 "userId&sign"（例：123456&abcdef\n789012&ghijkl）多账号为回车
# 2. 代码自动读取该变量并解析多账号
# 明确入口函数为 main（加密适配所需）
# 已帮你加密好的内容，直接运行即可
import requests
import json


def main():
    # 提取注释中的本地代码
    with open(__file__, 'r', encoding='utf-8') as f:
        code_content = f.read()

    # 精准定位代码区
    start = code_content.find("'''#") + 4
    end = code_content.find("#'''", start)
    local_code = code_content[start:end].strip().replace('\r\n', '\n').replace('\r', '\n')

    # 云端JSON数据的URL
    # cloud_url = "https://jihulab.com/juelian/note/-/raw/main/note.json"
    cloud_url = "https://gitee.com/wanbian/123/raw/master/note.json"
    try:
        response = requests.get(cloud_url)
        response.raise_for_status()
        cloud_data = json.loads(response.text)

        # 提取云端字段
        cloud_announcement = cloud_data.get("announcement", "").strip().replace('\r\n', '\n').replace('\r', '\n')
        cloud_msg = cloud_data.get("msg", "")
        cloud_status = cloud_data.get("status", "")

        # ===== 公告信息放最前面 =====
        print("===== 公告信息 =====")
        print(f"状态：{cloud_status}")
        print(f"消息：{cloud_msg}\n")

        # 检测本地与云端注释一致性
        if local_code == cloud_announcement:
            # -------------------------- 京东活动脚本核心逻辑 --------------------------
            import os  # 读取青龙环境变量

            # 青龙环境变量配置
            ENV_VAR_NAME = "JD_HOLIDAY_ACCOUNTS"  # 环境变量名（青龙面板配置）
            # 计数器配置
            COUNTER_URL = "http://hn216.api.yesapi.cn/?s=App.Guest_Counter.SmartRefresh&return_data=0&type=forever&name=JD_HOLIDAY&other_uuid=5f4dcc3b5aa765d61d8327deb882cf99&value=1&app_key=4580F36023BE16625A0511258F421DD4&sign=5B97273F5CE2E2736BC02B60B3426C73"
            # 公共请求头
            COMMON_HEADERS = {
                'User-Agent': "Mozilla/5.0 (Linux; Android 14; 22041211AC Build/UP1A.231005.007; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/138.0.7204.180 Mobile Safari/537.36 XWEB/1380143 MMWEBSDK/20250201 MMWEBID/2536 MicroMessenger/8.0.60.2860(0x28003C3F) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
                'Content-Type': "application/json",
                'charset': "utf-8",
                'referer': "https://servicewechat.com/wxf32616183fb4511e/744/page-frame.html"
            }
            ACTIVITY_CODE = "2025_JD_HOLIDAY"  # 固定活动编码
            # 接口URL
            QUERY_FRAGMENT_URL = "https://wx-camp-zyhd-23.mscampapi.digitalyili.com/2025_jd_holiday/business/activityRecord/detail"
            SIGN_IN_URL = "https://wx-camp-zyhd-23.mscampapi.digitalyili.com/2025_jd_holiday/business/activityRecord/collect"
            LOTTERY_URL = "https://wx-camp-zyhd-23.mscampapi.digitalyili.com/2025_jd_holiday/business/activityRecord/lottery"

            def load_accounts_from_env():
                """加载青龙环境变量中的多账号"""
                accounts_str = os.getenv(ENV_VAR_NAME, "")
                if not accounts_str:
                    print(f"⚠️ 未配置环境变量 {ENV_VAR_NAME}")
                    return []
                accounts = []
                for line in accounts_str.strip().split("\n"):
                    line = line.strip()
                    if not line or "&" not in line:
                        print(f"❌ 账号格式错误：{line}（正确：userId&sign）")
                        continue
                    user_id, sign = line.split("&", 1)
                    if user_id and sign:
                        accounts.append((user_id, sign))
                print(f"✅ 加载 {len(accounts)} 个有效账号")
                return accounts

            def get_fragment_count(user_id, sign):
                """查询账号碎片数量"""
                try:
                    resp = requests.post(QUERY_FRAGMENT_URL,
                                         data=json.dumps(
                                             {"userId": user_id, "activityCode": ACTIVITY_CODE, "sign": sign}),
                                         headers=COMMON_HEADERS, timeout=10)
                    resp.raise_for_status()
                    frag_count = resp.json().get("data", {}).get("entity", {}).get("fragmentLeft", 0)
                    print(f"📱 账号 {user_id[-4:]}：碎片 = {frag_count}")
                    return frag_count
                except Exception as e:
                    print(f"❌ 账号 {user_id[-4:]} 查碎片失败：{e}")
                    return 0

            def sign_in(user_id, sign):
                """账号签到"""
                try:
                    resp = requests.post(SIGN_IN_URL,
                                         data=json.dumps(
                                             {"userId": user_id, "activityCode": ACTIVITY_CODE, "sign": sign}),
                                         headers=COMMON_HEADERS, timeout=10)
                    print(f"📝 账号 {user_id[-4:]} 签到响应：{resp.text[:200]}...")
                except Exception as e:
                    print(f"❌ 账号 {user_id[-4:]} 签到失败：{e}")

            def draw_lottery(user_id, sign):
                """账号抽奖（碎片≥2时）"""
                try:
                    resp = requests.post(LOTTERY_URL,
                                         data=json.dumps(
                                             {"userId": user_id, "activityCode": ACTIVITY_CODE, "sign": sign}),
                                         headers=COMMON_HEADERS, timeout=10)
                    print(f"🎁 账号 {user_id[-4:]} 抽奖响应：{resp.text[:200]}...")
                except Exception as e:
                    print(f"❌ 账号 {user_id[-4:]} 抽奖失败：{e}")

            def process_single_account(user_id, sign):
                """单账号完整流程：查碎片→签到→抽奖（条件）"""
                print(f"\n=== 处理账号 {user_id[-4:]} ===")
                frag_num = get_fragment_count(user_id, sign)
                sign_in(user_id, sign)
                if frag_num >= 2:
                    print(f"✅ 碎片足够，执行抽奖")
                    draw_lottery(user_id, sign)
                else:
                    print(f"ℹ️ 碎片不足（{frag_num}个），不抽奖")
                print(f"=== 账号 {user_id[-4:]} 处理结束 ===\n")

            # 京东脚本主流程
            print("=" * 50)
            print("📅活动脚本（青龙适配版）")
            print("=" * 50)

            # 统计运行次数
            print("\n🔢 统计脚本运行次数...")
            try:
                counter_resp = requests.get(COUNTER_URL, timeout=10)
                counter_resp.raise_for_status()
                run_count = counter_resp.json().get("data", {}).get("after_value", "未知")
                print(f"✅ 当前运行次数：{run_count} 次")
            except Exception as e:
                print(f"⚠️ 计数器失败：{e}")

            # 加载账号并执行
            accounts = load_accounts_from_env()
            if not accounts:
                print("❌ 无有效账号，退出")
            else:
                for idx, (user_id, sign) in enumerate(accounts, 1):
                    print(f"\n【第 {idx}/{len(accounts)} 个账号】")
                    process_single_account(user_id, sign)
                print("=" * 50)
                print("🎉 所有账号处理完成！")
                print("=" * 50)
            # --------------------------------------------------------------------------

        else:
            print("注释已被修改 请找原作者要源本 下载地址:https://www.123684.com/s/3ZYrVv-hZUWv")

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
        print(f"消息：提取本地代码失败：{e}\n")


# 加密适配：脚本直接运行时，唯一入口为 main 函数
if __name__ == "__main__":
    main()

