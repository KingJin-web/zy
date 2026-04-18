import os
import time
import json
import base64
import hashlib
import random
import string
import urllib.parse
import re
from collections import OrderedDict
from curl_cffi import requests  
from Crypto.Cipher import AES, DES3, PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
#傻子传谣
TEST_ACCOUNTS = os.environ.get('chinaTelecomAccount', '') 
CHANNEL_ID = "156000008364"
ACTIVITY_ID = "ai096"
TEMPLATE_ID = "ve_3949"
TEMPLATE_CONF_ID = "2JCg"
FAKE_VIDEO_ID = ""
LOTTERY_COST_SCORE = 20
# 邀请任务开关，默认关闭（False），设为 True 启用
INVITE_TASK_ENABLED = os.environ.get('INVITE_TASK', 'False').lower() == 'true'
# 固定邀请码（可选，设置后所有任务都使用此邀请码）
FIXED_INVITER_CODE = os.environ.get('FIXED_INVITER_CODE', '2799914b8a4760a45a155cdb44c595917729b5b7eb2c111f7856d33bb552acce')

def md5(t): return hashlib.md5(t.encode()).hexdigest()

def rsa_encrypt(t):
    pub = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----"""
    return base64.b64encode(PKCS1_v1_5.new(RSA.import_key(pub)).encrypt(t.encode())).decode()

def des3_op(t, decrypt=False):
    key = b"1234567`90koiuyhgtfrdews"
    c = DES3.new(key, DES3.MODE_CBC, b"\x00"*8)
    if decrypt: 
        try: return unpad(c.decrypt(bytes.fromhex(t)), 8).decode()
        except: return t
    return c.encrypt(pad(t.encode(), 8)).hex()

class ImCrypto:
    def __init__(self):
        self.ts = str(int(time.time() * 1000))
        self.rdm = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        m_ts = md5(self.ts)
        self.key_h = md5(base64.b64encode((m_ts + self.rdm).encode()).decode() + self.rdm)
        self.e_k = md5(base64.b64encode(self.rdm.encode()).decode() + m_ts + self.key_h)[:16]
        self.e_i = md5(base64.b64encode(self.ts.encode()).decode() + md5(self.rdm) + self.key_h)[:16]

    def encrypt(self, d):
        s = json.dumps(d, separators=(',', ':'), ensure_ascii=False)
        c = AES.new(self.e_k.encode(), AES.MODE_CBC, self.e_i.encode())
        return base64.b64encode(c.encrypt(pad(s.encode('utf-8'), 16))).decode()

    def decrypt(self, t):
        try:
            d_k = md5(base64.b64encode(self.ts.encode()).decode() + self.key_h + md5(self.rdm))[:16]
            d_i = md5(base64.b64encode(self.rdm.encode()).decode() + self.key_h + md5(self.ts))[:16]
            c = AES.new(d_k.encode(), AES.MODE_CBC, d_i.encode())
            return unpad(c.decrypt(base64.b64decode(t)), 16).decode('utf-8')
        except: return t

def check_and_update_token(res, current_token):
    new_auth = res.headers.get("authorization") or res.headers.get("Authorization")
    if new_auth:
        new_token = new_auth.replace("Bearer ", "").strip()
        if new_token and new_token != current_token:
            print("🔄 [拦截器] 捕获到下发的刷新 Token，已动态更新凭证！")
            return new_token
    return current_token

def get_headers(crypto_inst, token="", is_share=False):
    ref = f"https://ai.imusic.cn/h5v/fusion/ai-luck-win-share?videoId={FAKE_VIDEO_ID}&cc={CHANNEL_ID}" if is_share else f"https://ai.imusic.cn/h5v/fusion/ai-luck-win?cc={CHANNEL_ID}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://ai.imusic.cn",
        "Referer": ref,
        "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "imencrypt": "1",
        "imtimestamp": crypto_inst.ts,
        "imrandomnum": crypto_inst.rdm,
        "imencryptkey": crypto_inst.key_h,
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def parse_accounts(raw_text):
    accounts = []
    normalized = raw_text.replace("\r", "\n").replace("&", "\n")
    for part in normalized.split("\n"):
        item = part.strip()
        if not item:
            continue
        if "#" not in item:
            raise ValueError(f"账号格式错误，必须为 手机号#密码: {item}")
        phone, password = item.split("#", 1)
        phone = phone.strip()
        password = password.strip()
        if not phone or not password:
            raise ValueError(f"账号格式错误，手机号或密码为空: {item}")
        accounts.append((phone, password))
    if not accounts:
        raise ValueError("未解析到有效账号，请按 手机号#密码 输入，多个账号可用 & 或换行分隔")
    return accounts

def parse_invite_accounts(raw_text):
    """
    解析邀请任务账号对格式
    格式: 邀请人手机#密码,被邀请人手机#密码
    或多对: 邀请人1#密码1,被邀请人1#密码1 & 邀请人2#密码2,被邀请人2#密码2
    """
    invite_pairs = []
    normalized = raw_text.replace("\r", "\n").replace("&", "\n")
    for part in normalized.split("\n"):
        pair = part.strip()
        if not pair:
            continue
        if "," not in pair:
            raise ValueError(f"邀请任务格式错误，请使用: 邀请人手机#密码,被邀请人手机#密码")
        inviter_str, invitee_str = pair.split(",", 1)
        inviter_str = inviter_str.strip()
        invitee_str = invitee_str.strip()
        
        if "#" not in inviter_str or "#" not in invitee_str:
            raise ValueError(f"邀请任务格式错误，每个账号需要 手机号#密码 格式")
        
        inviter_phone, inviter_pwd = inviter_str.split("#", 1)
        invitee_phone, invitee_pwd = invitee_str.split("#", 1)
        
        inviter_phone, inviter_pwd = inviter_phone.strip(), inviter_pwd.strip()
        invitee_phone, invitee_pwd = invitee_phone.strip(), invitee_pwd.strip()
        
        if not all([inviter_phone, inviter_pwd, invitee_phone, invitee_pwd]):
            raise ValueError(f"邀请任务账号信息不完整")
        
        invite_pairs.append({
            "inviter": (inviter_phone, inviter_pwd),
            "invitee": (invitee_phone, invitee_pwd)
        })
    
    if not invite_pairs:
        raise ValueError("未解析到有效邀请任务账号对")
    return invite_pairs


def do_login(session, crypto_inst, phone, password):
    ts_l = time.strftime("%Y%m%d%H%M%S")
    en_p = "".join(chr(ord(c)+2) for c in phone)
    en_pwd = "".join(chr(ord(c)+2) for c in password)
    
    login_body = {
        "headerInfos": {"code": "userLoginNormal", "timestamp": ts_l, "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "userLoginName": en_p, "clientType": "#11.3.0#channel50#iPhone 14 Pro Max#"},
        "content": {"fieldData": {"loginType": "4", "loginAuthCipherAsymmertric": rsa_encrypt(f"iPhone 14 15.4.{crypto_inst.rdm[:12]}{phone}{ts_l}{password}0$$$0."), "deviceUid": crypto_inst.rdm, "phoneNum": en_p, "authentication": en_pwd}}
    }
    res_l = session.post("https://appgologin.189.cn:9031/login/client/userLoginNormal", json=login_body).json()
    
    if res_l.get("responseData", {}).get("resultCode") != "0000":
        print(f"❌ 登录失败: {res_l}")
        raise Exception("Telecom Login Fail")
    
    l_succ = res_l["responseData"]["data"]["loginSuccessResult"]
    tk_val, uid = l_succ['token'], l_succ['userId']

    xml = f"<Request><HeaderInfos><Code>getSingle</Code><Timestamp>{ts_l}</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>{tk_val}</Token><UserLoginName>{phone}</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>{des3_op(str(uid))}</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>"
    res_xml = session.post("https://appgologin.189.cn:9031/map/clientXML", data=xml, headers={"Content-Type": "application/xml"}).text
    
    tk_match = re.search(r'<Ticket>(.*?)</Ticket>', res_xml)
    if not tk_match:
        print("❌ Ticket 获取失败！")
        raise Exception("Ticket Regex Match Fail")
    
    ticket = des3_op(tk_match.group(1), decrypt=True)

    sso_data = {"portal":"45","channelId":CHANNEL_ID,"ticket":ticket,"user118100cn":"user118100cn"}
    res_sso = session.post("https://ai.imusic.cn/vapi/vue_login/sso_login_v2", json=sso_data).json()
    
    return res_sso.get("token"), res_sso.get("mobile"), res_sso.get("enDataCode"), ticket

def warmup_session(session, crypto_inst, token, mobile):
    active_token = token
    
    h_share = get_headers(crypto_inst, active_token, is_share=True)
    res1 = session.post(f"https://ai.imusic.cn/vapi/new_member/get_user_info?channelId={CHANNEL_ID}&portal=45&mobile={mobile}", headers=h_share, data="")
    active_token = check_and_update_token(res1, active_token)
    
    h_share = get_headers(crypto_inst, active_token, is_share=True)
    res2 = session.post(f"https://ai.imusic.cn/vapi/vrbt/check_user_state?mobile={mobile}&is4G=1&is5G=1&isDX=1&channelId={CHANNEL_ID}&portal=45", headers=h_share, data="")
    active_token = check_and_update_token(res2, active_token)
    
    en_init = crypto_inst.encrypt({"channelId": CHANNEL_ID, "portal": "45", "mobile": mobile, "method": "init"})
    h_share = get_headers(crypto_inst, active_token, is_share=True)
    res3 = session.post(f"https://ai.imusic.cn/hapi/en/api?formData={urllib.parse.quote(en_init)}", headers=h_share, data="")
    active_token = check_and_update_token(res3, active_token)
    
    ugc_p = crypto_inst.encrypt({"channelId": CHANNEL_ID, "portal": "45", "mobile": mobile})
    h_share = get_headers(crypto_inst, active_token, is_share=True)
    res4 = session.post(f"https://ai.imusic.cn/hapi/diy_ugc/imu/get_ugc_info?formData={urllib.parse.quote(ugc_p)}", headers=h_share, data="")
    active_token = check_and_update_token(res4, active_token)

    time.sleep(0.5)
    return active_token

def query_template_meta(session, token):
    h = get_headers(ImCrypto(), token, is_share=False)
    res = session.post(
        f"https://ai.imusic.cn/hapi/de/api?pageNo=1&pageSize=50&activityId={ACTIVITY_ID}&apiName=diy%2FDiyVideoApi%2FqueryActRecommendTemplateList&channelId={CHANNEL_ID}&portal=45",
        headers=h,
        data=""
    )
    data = res.json()
    for item in data.get("data", {}).get("list", []):
        if item.get("templateId") == TEMPLATE_ID:
            return {
                "templateConfId": item.get("templateConfId") or TEMPLATE_CONF_ID,
                "userWords": item.get("userWords") or "古风插画，姐姐坐在秋千上。",
                "videoName": item.get("videoName") or "创作",
                "background": item.get("background") or "",
                "isAI": 1 if str(item.get("isAI", 0)) == "1" else 0,
                "arrangeId": item.get("arrangeId") or "",
            }
    return {
        "templateConfId": TEMPLATE_CONF_ID,
        "userWords": "古风插画，姐姐坐在秋千上。",
        "videoName": "创作",
        "background": "",
        "isAI": 0,
        "arrangeId": "",
    }


def post_encrypted_api(session, crypto_inst, token, api_path, payload, is_share=False):
    enc_str = crypto_inst.encrypt(payload)
    api_url = f"https://ai.imusic.cn{api_path}?formData={urllib.parse.quote(enc_str)}"
    h = get_headers(crypto_inst, token, is_share=is_share)
    res = session.post(api_url, headers=h, data="")
    return res, check_and_update_token(res, token)


def send_stat_message(session, crypto_inst, token, mobile, actname, actparam):
    payload = OrderedDict([
        ("channelId", CHANNEL_ID),
        ("portal", "45"),
        ("mobile", mobile),
        ("actname", actname),
        ("actparam", actparam),
        ("sid", "")
    ])
    return post_encrypted_api(session, crypto_inst, token, "/vapi/vue_stat/sendMessage", payload, is_share=False)


def query_fun_play_score(session, crypto_inst, token, mobile):
    res, active_token = post_encrypted_api(
        session,
        crypto_inst,
        token,
        "/hapi/en/api",
        OrderedDict([
            ("activityId", ACTIVITY_ID),
            ("mobile", mobile),
            ("apiName", "act/LaborApi/getFunPlayTotalScoreOrRemainingScore"),
            ("channelId", CHANNEL_ID),
            ("portal", "45")
        ]),
        is_share=False
    )
    dec_text = crypto_inst.decrypt(res.text)
    score_data = {}
    try:
        score_data = json.loads(dec_text).get("data", {}) or {}
        print(f"📊 当前积分: totalScore={score_data.get('totalScore', '')}, remainingScore={score_data.get('remainingScore', '')}")
    except Exception:
        pass
    return active_token, score_data


def query_rewards(session, crypto_inst, token, mobile):
    """查询用户可领取的奖励"""
    try:
        # 使用正确的API查询中奖列表
        res, active_token = post_encrypted_api(
            session,
            crypto_inst,
            token,
            "/hapi/en/api",
            OrderedDict([
                ("activityId", ACTIVITY_ID),
                ("mobile", mobile),
                ("pageNo", 1),
                ("pageSize", 10),
                ("apiName", "act/LaborApi/funPlayFestivalPointsAwardList"),
                ("channelId", CHANNEL_ID),
                ("portal", "45")
            ]),
            is_share=False
        )
        dec_text = crypto_inst.decrypt(res.text)
        try:
            data = json.loads(dec_text)
            if data.get("code") != "0000":
                print(f"⚠️  奖励查询失败: {data.get('desc')}")
                return active_token, {}
            reward_list = data.get("data", {}).get("list", [])
            if reward_list:
                print(f"🎁 发现 {len(reward_list)} 个奖励")
                for reward in reward_list:
                    if isinstance(reward, dict):
                        print(f"   - {reward.get('awardName', '未知奖励')} (状态: {'可领取' if reward.get('status') == '-1' else '已领取'})")
            return active_token, data.get("data", {})
        except Exception as e:
            print(f"⚠️  解析奖励列表失败: {str(e)}")
            return active_token, {}
    except Exception as e:
        print(f"⚠️  调用奖励查询接口失败: {str(e)}")
        return token, {}

def claim_reward(session, crypto_inst, token, mobile, reward_id):
    """领取指定奖励"""
    try:
        # 使用正确的API和参数格式领取奖励
        res, active_token = post_encrypted_api(
            session,
            crypto_inst,
            token,
            "/hapi/en/api",
            OrderedDict([
                ("mobile", mobile),
                ("awardId", reward_id),
                ("activityId", ACTIVITY_ID),
                ("apiName", "act/LaborApi/funPlayEggCostRedeem"),
                ("channelId", CHANNEL_ID),
                ("portal", "45")
            ]),
            is_share=False
        )
        dec_text = crypto_inst.decrypt(res.text)
        try:
            data = json.loads(dec_text)
            if data.get("code") == "0000":
                print(f"✅ 领取成功")
            else:
                print(f"❌ 领取失败: {data.get('desc', '未知错误')}")
        except Exception:
            print(f"📥 领取结果: {dec_text}")
        return active_token
    except Exception as e:
        print(f"⚠️  调用奖励领取接口失败: {str(e)}")
        return token

def claim_all_rewards(session, crypto_inst, token, mobile):
    """专门用于领取所有可领取的奖励"""
    print("\n=== 开始领取奖励 ===")
    active_token, rewards = query_rewards(session, crypto_inst, token, mobile)
    claimed = False
    failed_awards = []
    if rewards and isinstance(rewards, dict) and rewards.get("list"):
        for reward in rewards.get("list", []):
            if isinstance(reward, dict):
                # 检查是否是1元电信话费奖励
                award_name = reward.get('awardName', '')
                award_id = reward.get("awardId")
                if '1元' in award_name and '话费' in award_name and award_id not in failed_awards:
                    print(f"📋 领取: {award_name}")
                    # 尝试领取
                    try:
                        active_token = claim_reward(session, crypto_inst, active_token, mobile, award_id)
                        claimed = True
                        # 领取后再次查询奖励状态
                        active_token, updated_rewards = query_rewards(session, crypto_inst, active_token, mobile)
                        # 检查奖励状态是否已更新（简化逻辑，只要能查询到奖励就认为状态已更新）
                        updated_list = updated_rewards.get("list", [])
                        reward_updated = False
                        for updated_reward in updated_list:
                            if isinstance(updated_reward, dict) and updated_reward.get("awardId") == award_id:
                                reward_updated = True
                                break
                        if not reward_updated:
                            # 如果状态未更新，添加到失败列表
                            failed_awards.append(award_id)
                            print(f"⚠️  奖励状态未更新，将避免重复尝试")
                    except Exception as e:
                        print(f"⚠️  领取过程出错: {str(e)}")
                        failed_awards.append(award_id)
                    time.sleep(0.5)
        if claimed:
            print("✅ 奖励领取完成")
        else:
            print("📭 没有可领取的奖励")
    else:
        print("📭 没有可领取的奖励")
    return active_token

def run_lottery(session, crypto_inst, token, mobile):
    active_token, score_data = query_fun_play_score(session, crypto_inst, token, mobile)
    try:
        remaining_score = int(score_data.get("remainingScore") or 0)
    except Exception:
        remaining_score = 0

    lottery_count = remaining_score // LOTTERY_COST_SCORE
    print(f"🎰 可用积分={remaining_score}，按每次{LOTTERY_COST_SCORE}积分计算，可抽奖 {lottery_count} 次")
    if lottery_count <= 0:
        # 即使没有积分抽奖，也检查是否有未领取的奖励
        active_token, rewards = query_rewards(session, crypto_inst, active_token, mobile)
        if rewards and isinstance(rewards, dict) and rewards.get("rewards"):
            for reward in rewards.get("rewards", []):
                if isinstance(reward, dict) and reward.get("status") == "1":  # 假设1表示可领取
                    reward_id = reward.get("rewardId")
                    if reward_id:
                        print(f"📋 发现可领取奖励: {reward.get('rewardName', '未知奖励')}")
                        active_token = claim_reward(session, crypto_inst, active_token, mobile, reward_id)
                        time.sleep(0.5)
        return active_token

    for index in range(1, lottery_count + 1):
        res, active_token = post_encrypted_api(
            session,
            crypto_inst,
            active_token,
            "/hapi/en/api",
            OrderedDict([
                ("activityId", ACTIVITY_ID),
                ("mobile", mobile),
                ("apiName", "act/LaborApi/funPlayFestivalLottery"),
                ("channelId", CHANNEL_ID),
                ("portal", "45")
            ]),
            is_share=False
        )
        dec_text = crypto_inst.decrypt(res.text)
        print(f"🎁 第{index}次抽奖结果: {dec_text}")
        time.sleep(0.2)

    # 抽奖完成后检查并领取奖励
    active_token, rewards = query_rewards(session, crypto_inst, active_token, mobile)
    if rewards and isinstance(rewards, dict) and rewards.get("rewards"):
        for reward in rewards.get("rewards", []):
            if isinstance(reward, dict) and reward.get("status") == "1":  # 假设1表示可领取
                reward_id = reward.get("rewardId")
                if reward_id:
                    print(f"📋 发现可领取奖励: {reward.get('rewardName', '未知奖励')}")
                    active_token = claim_reward(session, crypto_inst, active_token, mobile, reward_id)
                    time.sleep(0.5)

    return active_token


def premake_prepare(session, crypto_inst, token, mobile, template_meta):
    active_token = token

    res_pkg, active_token = post_encrypted_api(
        session,
        crypto_inst,
        active_token,
        "/hapi/en/api",
        OrderedDict([
            ("channelId", CHANNEL_ID),
            ("portal", "45"),
            ("mobile", mobile),
            ("templateId", TEMPLATE_ID),
            ("aid", ACTIVITY_ID),
            ("apiName", "ismp/IsmpApi/queryAiMakePkgInfo")
        ]),
        is_share=False
    )

    stat_events = [
        ("page_vring_index", f"玩转AI赢手机_activityID_{ACTIVITY_ID}_entrance_{CHANNEL_ID}"),
        ("activity_vring_make_1.9", f"_activityID_{ACTIVITY_ID}_templateID_{TEMPLATE_ID}_entrance_{CHANNEL_ID}_templateconfID_{template_meta['templateConfId']}"),
        ("activity_2603AI-meet_25.1", f"activityID_{ACTIVITY_ID}_undefined_templateID_{TEMPLATE_ID}_entrance_{CHANNEL_ID}_templateconfID_{template_meta['templateConfId']}"),
        ("page_2511AI-makeonekey_9", f"activityID_{ACTIVITY_ID}_templateID_{TEMPLATE_ID}_entrance_{CHANNEL_ID}_templateConfID_{template_meta['templateConfId']}"),
        ("page_2511AI-makeonekey_3", f"activityID_{ACTIVITY_ID}_templateID_{TEMPLATE_ID}_entrance_{CHANNEL_ID}_templateConfID_{template_meta['templateConfId']}"),
    ]
    for actname, actparam in stat_events:
        _, active_token = send_stat_message(session, crypto_inst, active_token, mobile, actname, actparam)
        time.sleep(0.08)

    return active_token


def make_request(session, crypto_inst, token, mobile, en_code, template_meta):
    rand_name = f"{template_meta['videoName']}{random.randint(100000, 999999)}"
    payload = OrderedDict([
        ("channelId", CHANNEL_ID), ("portal", "45"), ("mobile", mobile),
        ("openId", ""), ("makeId", ""), ("background", template_meta.get("background", "")), ("userPhotos", ""),
        ("userWords", template_meta["userWords"]),
        ("templateName", rand_name), ("videoName", rand_name),
        ("templateId", TEMPLATE_ID), ("templateConfId", template_meta["templateConfId"]), ("aid", ACTIVITY_ID),
        ("inviterMobile", en_code), ("isAI", template_meta.get("isAI", 0)), ("aiPack", 0), ("arrangeId", template_meta.get("arrangeId", "")),
        ("autoOrderUgc", 0), ("aiGatewayImagMakeId", ""), ("fromType", ""),
        ("sessionId", ""), ("voice", ""), ("invitationCode", en_code)
    ])
    print(f"🧩 当前模板参数: templateId={TEMPLATE_ID}, templateConfId={template_meta['templateConfId']}, isAI={template_meta.get('isAI', 0)}, arrangeId={template_meta.get('arrangeId', '')!s}, background={template_meta.get('background', '')!r}")
    enc_str = crypto_inst.encrypt(payload)
    api_url = f"https://ai.imusic.cn/hapi/diy_video/au/template_make_add_v2?formData={urllib.parse.quote(enc_str)}"

    h = get_headers(crypto_inst, token, is_share=False)
    return session.post(api_url, headers=h, data="")

def run_single_account(phone, password):
    print(f"\n{'=' * 20} 开始处理账号 {phone} {'=' * 20}")

    session = requests.Session(impersonate="chrome120")
    
    global_crypto = ImCrypto()

    session.cookies.set('cc', CHANNEL_ID, domain='ai.imusic.cn')
    session.cookies.set('imusic', f'118100{int(time.time()*1000)}', domain='ai.imusic.cn')
    session.cookies.set('loginState', 'true', domain='ai.imusic.cn')

    try:
        token, mobile, en_code, ticket = do_login(session, global_crypto, phone, password)
        if not en_code:
            en_code = "7c254a3c19d2b314d5d4415d9a0961e27729b5b7eb2c111f7856d33bb552acce"

        active_token = warmup_session(session, global_crypto, token, mobile)
        template_meta = query_template_meta(session, active_token)
        active_token = premake_prepare(session, global_crypto, active_token, mobile, template_meta)

        res = make_request(session, global_crypto, active_token, mobile, en_code, template_meta)
        active_token = check_and_update_token(res, active_token)
        
        resp_text = global_crypto.decrypt(res.text)

        if "10013" in resp_text:
            trace_id = json.loads(resp_text).get("imuTraceId")
            h_rem = get_headers(global_crypto, active_token, True)

            _, active_token = send_stat_message(
                session,
                global_crypto,
                active_token,
                mobile,
                "page_vring_index",
                f"玩转AI赢手机_activityID_{ACTIVITY_ID}_entrance_{CHANNEL_ID}"
            )
            time.sleep(0.05)
            _, active_token = send_stat_message(
                session,
                global_crypto,
                active_token,
                mobile,
                "activity_vring_make_1.9",
                f"_activityID_{ACTIVITY_ID}_entrance_{CHANNEL_ID}"
            )

            rem_en = global_crypto.encrypt({"method": "remedy", "traceId": trace_id, "mobile": mobile})
            res_rem = session.post(f"https://ai.imusic.cn/hapi/en/api?formData={urllib.parse.quote(rem_en)}", headers=h_rem, data="")
            active_token = check_and_update_token(res_rem, active_token)

            res_refresh = session.post("https://ai.imusic.cn/vapi/vue_login/sso_login_v2", json={"portal":"45","channelId":CHANNEL_ID,"ticket":ticket,"user118100cn":"user118100cn"}).json()
            active_token = res_refresh.get("token")
            active_token = premake_prepare(session, global_crypto, active_token, mobile, template_meta)

            time.sleep(1)

            res_final = make_request(session, global_crypto, active_token, mobile, en_code, template_meta)
            final_text = global_crypto.decrypt(res_final.text)
            print(f"🎉 最终响应结果: {final_text}")
            if '"code":"0000"' in final_text:
                active_token = check_and_update_token(res_final, active_token)
                active_token = run_lottery(session, global_crypto, active_token, mobile)
        else:
            print("✅ 任务提交成功！")
            active_token = run_lottery(session, global_crypto, active_token, mobile)

        print(f"✅ 账号 {phone} 处理完成")
    except Exception as e:
        print(f"💥 账号 {phone} 程序崩溃，原因: {str(e)}")


def run_invite_task(invite_pair):
    """执行单个邀请任务"""
    inviter_phone, inviter_pwd = invite_pair["inviter"]
    invitee_phone, invitee_pwd = invite_pair["invitee"]
    
    print(f"\n{'=' * 25} 邀请任务 {'=' * 25}")
    print(f"👤 邀请人: {inviter_phone}")
    print(f"👤 被邀请人: {invitee_phone}")
    
    session = requests.Session(impersonate="chrome120")
    global_crypto = ImCrypto()
    session.cookies.set('cc', CHANNEL_ID, domain='ai.imusic.cn')
    session.cookies.set('imusic', f'118100{int(time.time()*1000)}', domain='ai.imusic.cn')
    session.cookies.set('loginState', 'true', domain='ai.imusic.cn')
    
    # 1. 邀请人登录获取 en_code
    print(f"\n--- 步骤1: 邀请人 {inviter_phone} 登录 ---")
    try:
        token_inviter, mobile_inviter, en_code, ticket_inviter = do_login(session, global_crypto, inviter_phone, inviter_pwd)
        if not en_code:
            en_code = "7c254a3c19d2b314d5d4415d9a0961e27729b5b7eb2c111f7856d33bb552acce"
        print(f"✓ 邀请人登录成功，en_code: {en_code[:20]}...")
    except Exception as e:
        print(f"❌ 邀请人登录失败: {str(e)}")
        return
    
    # 2. 被邀请人登录
    print(f"\n--- 步骤2: 被邀请人 {invitee_phone} 登录 ---")
    try:
        token_invitee, mobile_invitee, _, ticket_invitee = do_login(session, global_crypto, invitee_phone, invitee_pwd)
        print(f"✓ 被邀请人登录成功")
    except Exception as e:
        print(f"❌ 被邀请人登录失败: {str(e)}")
        return
    
    # 3. 被邀请人环境预热
    print(f"\n--- 步骤3: 被邀请人环境预热 ---")
    active_token = warmup_session(session, global_crypto, token_invitee, mobile_invitee)
    template_meta = query_template_meta(session, active_token)
    active_token = premake_prepare(session, global_crypto, active_token, mobile_invitee, template_meta)
    
    # 4. 被邀请人做任务（使用邀请人的 en_code）
    print(f"\n--- 步骤4: 被邀请人完成任务（邀请码: {en_code[:20]}...）---")
    res = make_request(session, global_crypto, active_token, mobile_invitee, en_code, template_meta)
    active_token = check_and_update_token(res, active_token)
    resp_text = global_crypto.decrypt(res.text)
    
    if "10013" in resp_text:
        trace_id = json.loads(resp_text).get("imuTraceId")
        h_rem = get_headers(global_crypto, active_token, True)
        _, active_token = send_stat_message(session, global_crypto, active_token, mobile_invitee, "page_vring_index", f"玩转AI赢手机_activityID_{ACTIVITY_ID}_entrance_{CHANNEL_ID}")
        time.sleep(0.05)
        _, active_token = send_stat_message(session, global_crypto, active_token, mobile_invitee, "activity_vring_make_1.9", f"_activityID_{ACTIVITY_ID}_entrance_{CHANNEL_ID}")
        rem_en = global_crypto.encrypt({"method": "remedy", "traceId": trace_id, "mobile": mobile_invitee})
        res_rem = session.post(f"https://ai.imusic.cn/hapi/en/api?formData={urllib.parse.quote(rem_en)}", headers=h_rem, data="")
        active_token = check_and_update_token(res_rem, active_token)
        res_refresh = session.post("https://ai.imusic.cn/vapi/vue_login/sso_login_v2", json={"portal":"45","channelId":CHANNEL_ID,"ticket":ticket_invitee,"user118100cn":"user118100cn"}).json()
        active_token = res_refresh.get("token")
        active_token = premake_prepare(session, global_crypto, active_token, mobile_invitee, template_meta)
        time.sleep(1)
        res_final = make_request(session, global_crypto, active_token, mobile_invitee, en_code, template_meta)
        final_text = global_crypto.decrypt(res_final.text)
        print(f"🎉 最终响应结果: {final_text}")
        if '"code":"0000"' in final_text:
            active_token = check_and_update_token(res_final, active_token)
            run_lottery(session, global_crypto, active_token, mobile_invitee)
    else:
        print("✅ 任务提交成功！")
        run_lottery(session, global_crypto, active_token, mobile_invitee)
    
    print(f"\n✅ 邀请任务完成: {inviter_phone} 邀请 {invitee_phone}")


def run():
    # 检查是否有固定邀请码
    if FIXED_INVITER_CODE:
        print(f"\n📌 使用固定邀请码模式: {FIXED_INVITER_CODE[:20]}...")
        # 普通账号+固定邀请码模式
        accounts = parse_accounts(TEST_ACCOUNTS)
        print(f"共 {len(accounts)} 个账号将使用固定邀请码")
        for idx, (phone, password) in enumerate(accounts, start=1):
            print(f"\n#### [{idx}/{len(accounts)}] ####")
            # 使用固定邀请码
            run_single_account_with_inviter(phone, password, FIXED_INVITER_CODE)
    elif INVITE_TASK_ENABLED:
        # 邀请任务模式
        invite_pairs = parse_invite_accounts(TEST_ACCOUNTS)
        print(f"共 {len(invite_pairs)} 对邀请任务")
        for idx, pair in enumerate(invite_pairs, start=1):
            print(f"\n====== [{idx}/{len(invite_pairs)}] ======")
            run_invite_task(pair)
    else:
        # 普通模式
        accounts = parse_accounts(TEST_ACCOUNTS)
        print(f"共解析到 {len(accounts)} 个账号")
        for idx, (phone, password) in enumerate(accounts, start=1):
            print(f"\n#### [{idx}/{len(accounts)}] ####")
            run_single_account(phone, password)


def run_single_account_with_inviter(phone, password, inviter_code):
    """单账号使用指定邀请码"""
    print(f"\n{'=' * 20} 使用指定邀请码处理账号 {phone} {'=' * 20}")
    session = requests.Session(impersonate="chrome120")
    global_crypto = ImCrypto()
    session.cookies.set('cc', CHANNEL_ID, domain='ai.imusic.cn')
    session.cookies.set('imusic', f'118100{int(time.time()*1000)}', domain='ai.imusic.cn')
    session.cookies.set('loginState', 'true', domain='ai.imusic.cn')
    
    try:
        token, mobile, _, ticket = do_login(session, global_crypto, phone, password)
        active_token = warmup_session(session, global_crypto, token, mobile)
        template_meta = query_template_meta(session, active_token)
        active_token = premake_prepare(session, global_crypto, active_token, mobile, template_meta)
        
        res = make_request(session, global_crypto, active_token, mobile, inviter_code, template_meta)
        active_token = check_and_update_token(res, active_token)
        resp_text = global_crypto.decrypt(res.text)
        
        if "10013" in resp_text:
            trace_id = json.loads(resp_text).get("imuTraceId")
            h_rem = get_headers(global_crypto, active_token, True)
            _, active_token = send_stat_message(session, global_crypto, active_token, mobile, "page_vring_index", f"玩转AI赢手机_activityID_{ACTIVITY_ID}_entrance_{CHANNEL_ID}")
            time.sleep(0.05)
            _, active_token = send_stat_message(session, global_crypto, active_token, mobile, "activity_vring_make_1.9", f"_activityID_{ACTIVITY_ID}_entrance_{CHANNEL_ID}")
            rem_en = global_crypto.encrypt({"method": "remedy", "traceId": trace_id, "mobile": mobile})
            res_rem = session.post(f"https://ai.imusic.cn/hapi/en/api?formData={urllib.parse.quote(rem_en)}", headers=h_rem, data="")
            active_token = check_and_update_token(res_rem, active_token)
            res_refresh = session.post("https://ai.imusic.cn/vapi/vue_login/sso_login_v2", json={"portal":"45","channelId":CHANNEL_ID,"ticket":ticket,"user118100cn":"user118100cn"}).json()
            active_token = res_refresh.get("token")
            active_token = premake_prepare(session, global_crypto, active_token, mobile, template_meta)
            time.sleep(1)
            res_final = make_request(session, global_crypto, active_token, mobile, inviter_code, template_meta)
            final_text = global_crypto.decrypt(res_final.text)
            print(f"🎉 最终响应结果: {final_text}")
            if '"code":"0000"' in final_text:
                active_token = check_and_update_token(res_final, active_token)
                run_lottery(session, global_crypto, active_token, mobile)
        else:
            print("✅ 任务提交成功！")
            run_lottery(session, global_crypto, active_token, mobile)
        
        print(f"✅ 账号 {phone} 处理完成")
    except Exception as e:
        print(f"💥 账号 {phone} 程序崩溃，原因: {str(e)}")


def run_only_claim_rewards():
    """只领取奖励，不执行其他任务"""
    accounts = parse_accounts(TEST_ACCOUNTS)
    print(f"共解析到 {len(accounts)} 个账号，将执行奖励领取")
    for idx, (phone, password) in enumerate(accounts, start=1):
        print(f"\n#### [{idx}/{len(accounts)}] 开始领取奖励: {phone} ####")
        session = requests.Session(impersonate="chrome120")
        global_crypto = ImCrypto()
        session.cookies.set('cc', CHANNEL_ID, domain='ai.imusic.cn')
        session.cookies.set('imusic', f'118100{int(time.time()*1000)}', domain='ai.imusic.cn')
        session.cookies.set('loginState', 'true', domain='ai.imusic.cn')
        try:
            token, mobile, en_code, ticket = do_login(session, global_crypto, phone, password)
            if not en_code:
                en_code = "7c254a3c19d2b314d5d4415d9a0961e27729b5b7eb2c111f7856d33bb552acce"
            active_token = warmup_session(session, global_crypto, token, mobile)
            active_token = claim_all_rewards(session, global_crypto, active_token, mobile)
            print(f"✅ 账号 {phone} 奖励领取完成")
        except Exception as e:
            print(f"💥 账号 {phone} 程序崩溃，原因: {str(e)}")

if __name__ == "__main__":
    # 运行只领取奖励的功能
    run_only_claim_rewards()