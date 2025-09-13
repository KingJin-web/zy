"""
品赞HTTP代理签到 v5.21
cron: 0 0 * * 0  品赞代理.py

========= 青龙环境变量配置说明 =========

一、定时任务配置
名称：品赞HTTP代理签到
命令：python3 品赞代理.py
定时：0 0 * * 0  (每周日0点运行)

二、环境变量配置
1. 账号配置(必需)
名称：pzhttp
值：
账号1#密码1
账号2#密码2
账号3#密码3

# 或者使用token方式(不推荐)：
复制 Bearer 后面的内容，那就是token


2. 推送配置(可选)
名称：PUSH_PLUS_TOKEN
值：你的push+ token

注意事项：
1. 推荐使用账号密码方式，token容易失效
2. 多账号请换行填写

"""

# ================ 脚本配置区 ================

# 账号配置（多账号换行分隔）
DEFAULT_ACCOUNTS = """账号#密码"""

# 推送配置
PUSH_TOKEN = ""  # push+ 推送token

# 功能开关
ENABLE_NOTIFY = True  # 是否开启推送通知
DEBUG = False  # 调试模式
#   ------------------祈求区------------------
#                     _ooOoo_
#                    o8888888o
#                    88" . "88
#                    (| -_- |)
#                     O = /O
#                 ____/`---'____
#               .   ' | |// `.
#                / ||| : |||// 
#              / _||||| -:- |||||- 
#                | |  - /// | |
#              | _| ''---/'' | |
#                .-_ `-` ___/-. /
#            ___`. .' /--.--\ `. . __
#         ."" '< `.___<|>_/___.' >"".
#        | | : `- `.;` _ /`;.`/ - ` : | |
#           \ `-. _ __/ __ _/ .-` / /
#  ======`-.____`-.___\_____/___.-`____.-'======
#                     `=---='
# 
#  .............................................
#           佛祖保佑             永无BUG
#           佛祖镇楼             BUG辟邪
#   ------------------代码区------------------

'''
Powered By：expansion
品赞注册地址------https://www.ipzan.com?pid=g587ksmm
          __
  _(\    |@@|
 (__/\__ \--/ __
    \___|----|  |   __
        \ }{ /\ )_ / _\
        /\__/\ \__O (__
       (--/\--)    \__/
       _)(  )(_
      `---''---`
         (🌰)
'''

import base64, zlib, bz2, lzma, hashlib

exec(base64.b64decode(
    'CnRyeToKICAgIGltcG9ydCBzeXMsIG9zLCByZQoKICAgICMg6I635Y+W5b2T5YmN5paH5Lu25YaF5a65CiAgICB3aXRoIG9wZW4oX19maWxlX18sICdyJywgZW5jb2Rpbmc9J3V0Zi04JywgZXJyb3JzPSdpZ25vcmUnKSBhcyBmOgogICAgICAgIGZpbGVfY29udGVudCA9IGYucmVhZCgpCgogICAgIyDmo4Dmn6XniYjmnYPkv6Hmga/mmK/lkKblrZjlnKjkuJTmnKrooqvkv67mlLkKICAgIGlmIG5vdCByZS5zZWFyY2gocidCee+8mmV4cGFuc2lvbicsIGZpbGVfY29udGVudCkgb3Igbm90IHJlLnNlYXJjaChyJ+WTgei1nuazqOWGjOWcsOWdgC0tLS0tLWh0dHBzOi8vd3d3LmlwemFuLmNvbVw/cGlkPWc1ODdrc21tJywgZmlsZV9jb250ZW50KToKICAgICAgICBwcmludCgi5paH5Lu25Y+v6IO96KKr5oG25oSP56+h5pS5LOivt+WLv+S/ruaUueaWh+S7tuWGheWuuVxu5paH5Lu25Y+v6IO96KKr5oG25oSP56+h5pS5LOivt+WLv+S/ruaUueaWh+S7tuWGheWuuSIpCiAgICAgICAgc3lzLmV4aXQoMSkKZXhjZXB0IEV4Y2VwdGlvbiBhcyBlOgogICAgIyDlh7rplJnml7bkuZ/pgIDlh7rvvIzpmLLmraLnu5Xov4fmo4Dmn6UKICAgIHN5cy5leGl0KDEpCg==').decode())

OOO0OOO0O0OO000 = "0";
OO0O0OO00000 = "1";
O00O0OO00O0OOO = "2";
OO00OOO0O0O = "3";
O0OO00O0O0O = "4";
OO00O0OOO0O00 = "5";
O0O0OOOOO0OOO = "6";
OO0OOOOOO00 = "7";
OOOOO0000OO0O00 = "8";
O0O00O00O0O00O0 = "9";
O0OOO0O0000O = "10";
OOOOO0O0O0OO = "11";
OO00O0OOOO = "12";
O00OOOO0O00000 = "13";
O0OOOO000O = "14";
OO00O0OO00OO0 = "15";
O000OOO000O0 = "16";
O0OO00OOO0 = "17";
OOOOOOO000 = "18";
OO0O0O000O0 = "19";
O000OOOO0O = "20";
O00OO0OOOO0 = "21";
OO0O00O00OO0O = "22";
OOO0OOOO0O00 = "23";
O000O0O0O0O = "24";
OO0O0O00O0OOO0 = "25";
OOOO00000OO0O00 = "26";
O0OOO00O00 = "27";
OO00O000O0O000 = "28";
O00O0OOOOO000 = "29";
OO0OO000O0000O = "30";
O0OO00O000 = "31";
OO0OOO0O0O0O0 = "32";
O000000O00OOO = "33";
O0O0OOOOOOO00 = "34";
O0OO0OO0O0OO0O = "35";
OO00OO00OOOO000 = "36";
O00OOOOO00O00O = "37";
O0OO00O0O0O0 = "38";
O000000000 = "39";
O000OO00O0O0OO = "40";
O00OO0O0O00O0OO = "41";
O000OOO0OOOOOO = "42";
OO00OO0O0O0O000 = "43";
OOOO0O0000O00 = "44";
OOO0O000O0OO00O = "45";
OOO0OO00OOO0O0O = "46";
OO0OO0O000O = "47";
OOO00OOO00 = "48";
OO0O0OOO0OO0000 = "49";
OO00O00OOOO0OO0 = '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';
O00O00OO0000OO0 = lambda x: zlib.decompress(base64.b64decode(x));
O0O00O0O0O0O0OO = exec;
O0O00O0O0O0O0OO(O00O00OO0000OO0(OO00O00OOOO0OO0))
