# v29
# 部分逻辑回退v23
# 新增变量 lindong_onegoldmax 可以设置出现多少1金币后才停止运行
# 低金币尝试开启养号功能  1金币自行分辨是否代理（ip）或黑号（宝箱都是1）或上限（跑着跑着1金币要过一会才有金币） 排除这三个原因基本可以养到1000-2500

# 快手v11/v12/v17:
# 1.更新养号逻辑(仅限于低金币 1/10金币还是ip或者号的问题)
# 2.修复部分情况下不能跑的bug
# 3.修复获取不到广告的bug
# 4.适配一键获取的ck 可以直接填 备注#ck#salt（有代理后面接上#代理就行了）就能跑了
# 5.新建提现
# 统一格式为 备注#ck#salt 或者 备注@ck@salt 备注不能不填否则报错
# 如果需要ua就  备注#ck#salt#ua 或者 备注@ck@salt@ua
# 如果需要代理就 备注#ck#salt#ua#代理 或者 备注@ck@salt@ua@代理
#

#   ===========================================
#   ==================广告======================
#   ============================================
#   入口: 快手极速版App 一机一号一个实名 只限安卓机器 （无需root） 最好一号一ip
#   需抓取数据:
#   * 登录时搜索 api_client_salt 找到5kb左右的链接 在响应里最下面找到你的salt 不会可以用一键抓取
#   * 开抓包点福利后 搜索 earn/overview/tasks 找到此请求的cookie 同时找到此请求下的请求头的user-agent的值
#   抓包工具 https://pan.quark.cn/s/44f90724e243
#   * 代理推荐：通过注册链接注册后，一对一成为您的专属代理，注册后提供账号，为您设置最优价格
#  https://www.jichiy.com/views/login.html#?promotionCode=319256E847DF4C26986A63AC04155561 极驰云
#   http://www.tianxingip.com/proxy/index/index/code/hnking/p/2847.html 天行sk5代理 5一条
#   https://www.xiequ.cn/index.html?d630539f 注册送10元免费使用长效独享代理一天
#  http://www.gzsk5.com/#/register?invitation=hnking2&shareid=516 光子sk5代理100M 4.5一条

print('''https://www.jichiy.com/views/login.html#?promotionCode=319256E847DF4C26986A63AC04155561 极驰云
http://www.tianxingip.com/proxy/index/index/code/hnking/p/2847.html 天行sk5代理 5一条
https://www.xiequ.cn/index.html?d630539f 注册送10元免费使用长效独享代理一天
http://www.gzsk5.com/#/register?invitation=hnking2&shareid=516 光子sk5代理100M 4.5一条''')

#   * 如果一个青龙跑两号及以上 则就需要填写socket5代理防止黑号,注意一号一代理,不允许多号共用 第一个号不使用代理则不填
#   * 代理为万安格式 即代理ip|端口|代理用户名|代理密码
#   * 变量: Lindong_ksjsb 填写上面获取的数据 格式为 备注@cookie@salt@ua(选填)[@代理ip|端口|代理用户名|代理密码](可选 代理格式不包括括号)
#   * 也可以是 备注#cookie#salt@ua(选填)[@代理ip|端口|代理用户名|代理密码](可选 代理格式不包括括号)
#   * 不可以不填备注 可以不填ua 不填备注报错
#   * 多号换行或新建同名变量
#   * 变量: Lindong_ksCard 卡密变量
#   * 可选变量(可不填): lindong_ks_thread     最大线程数       默认 1 设置 2 以上为多线程 不懂设置为100即可
#   * 可选变量(可不填): lindong_ks_maxgold    最大金币数       默认 50w (跑多了第二天可能1金币 有此需求请勿兑换金币)
#   * 可选变量(可不填): lindong_ks_run_task   额外执行任务     默认 无 多个额外执行的任务用,分割 填0,1,2,3 执行所有任务
#   * 可选的是 0:签到 | 1.宝箱 | 2.宝箱广告(需要运行宝箱广告必须开宝箱) | 3.饭补广告
#   * 可选变量(可不填): lindong_ksyhtimes     执行多少个广告后进行休眠操作     默认 40
#   * 可选变量(可不填): lindong_autotixi      是否自动提现        默认否 填1自动提现(只会提现50 不够50手动提)
#   * 可选变量(可不填): lindong_tixipay       提现渠道           默认微信 填1微信 填2支付宝
#   * 可选变量(可不填): lindong_dijinbyh      低金币是否进行养号  默认否 填1是 (由于服务放在云端运行 人多时可能会出现失败)
#   * 可选变量(可不填): lindong_dijinbyhyz    养号金币阈值       默认500 范围10-1000 (上一个不开这个不生效)
#   * 可选变量(可不填): lindong_onegoldmax    出现多少1金币后停止脚本    默认5
#   * 可选变量(可不填): lindong_zuijiaad      是否开启追加广告    默认关 填1开启
#   * 可选变量(可不填): lindong_fuckcd        是否无视cd硬跑     默认关 填1开启
#   * 需要安装依赖: py的 requests[socks]
#   * 多号方式 [ 换行 | 新建同名变量 | & 分割 ]
#   * tg群组:https://t.me/+1BVEpYhydgplYWY9
#   ========================================================================================
import os
import sys
import platform
import subprocess
import importlib
import json
import logging
import glob

try:
    import requests
except ImportError:
    print("请安装requests依赖")
    sys.exit(1)

# === 全局开关：空字符串=最新版本 | 数字字符串=指定版本 ===
VERSION = ''  # 例如：'32' 表示固定运行 v32 | '' 表示最新

MODULE_NAME = 'ksjsb'
API_BASE_URL = 'http://pyenc.lindong.xyz'

MAX_RETRY = 3
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] ===> %(message)s')
log = logging.getLogger(__name__)


class SoManager:
    def __init__(self, module_name, api_base_url):
        self.module_name = module_name
        self.api_base_url = api_base_url.rstrip('/')
        self.api_url = f"{self.api_base_url}/api.php"
        self.version_file = f"{module_name}.version"
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.arch = self._get_arch()
        self.platform_key = f"{self.arch}_py{self.python_version.replace('.', '')}"
        self.wanted_version = str(VERSION).strip() if VERSION is not None else ''

    def _get_arch(self):
        machine = platform.machine().lower()
        if machine in ['x86_64', 'amd64', 'x64']:
            return 'x64'
        elif machine in ['aarch64', 'arm64']:
            return 'aarch64'
        else:
            log.warning(f"未知架构 {machine}，默认使用 aarch64")
            return 'aarch64'

    def _check_system_compatibility(self):
        if sys.version_info.major != 3 or sys.version_info.minor not in [10, 11]:
            log.error(f"不支持的Python版本 {sys.version}，请使用Python 3.10或3.11")
            return False
        if platform.system() != 'Linux':
            log.error(f"不支持的操作系统 {platform.system()}，请使用Linux系统")
            return False
        log.info(f"系统检测通过 [Python {sys.version}] [{platform.system()} {platform.machine()}]")
        return True

    def _get_local_version(self):
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            log.warning(f"读取本地版本失败: {e}")
        return None

    def _save_local_version(self, version):
        try:
            with open(self.version_file, 'w') as f:
                f.write(str(version))
        except Exception as e:
            log.error(f"保存版本号失败: {e}")

    def _post_json(self, payload):
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code != 200:
                log.error(f"API请求失败: HTTP {response.status_code}")
                return None
            data = response.json()
            if not data.get('success'):
                log.error(f"API返回错误: {data.get('message', '未知错误')}")
                return None
            return data
        except requests.exceptions.RequestException as e:
            log.error(f"网络请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            log.error(f"JSON解析失败: {e}")
            return None
        except Exception as e:
            log.error(f"接口调用异常: {e}")
            return None

    def _get_remote_info(self):
        if self.wanted_version:
            if not self.wanted_version.isdigit() or int(self.wanted_version) <= 0:
                log.error(f"指定的 VERSION 无效：{self.wanted_version}（应为正整数或空字符串）")
                return None
            data = self._post_json({
                "action": "get_version",
                "module_name": self.module_name,
                "version": int(self.wanted_version)
            })
            if not data:
                return None
            return {
                "version": str(data.get('version')),
                "files": data.get('files', {}),
                "created_at": data.get('created_at')
            }
        # 最新版本
        data = self._post_json({
            "action": "get_latest",
            "module_name": self.module_name
        })
        if not data:
            return None
        return {
            "version": str(data.get('latest_version')),
            "files": data.get('files', {}),
            "created_at": data.get('created_at')
        }

    def _download_file(self, download_url):
        """下载.so文件"""
        temp_file = f"{self.so_filename}.tmp"

        for attempt in range(MAX_RETRY):
            try:
                log.info(f"开始下载 (尝试 {attempt + 1}/{MAX_RETRY}): {download_url}")

                response = requests.get(download_url, timeout=180, stream=True)
                if response.status_code != 200:
                    log.error(f"下载失败: HTTP {response.status_code}")
                    continue
                with open(temp_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                if os.path.getsize(temp_file) == 0:
                    log.error("下载的文件为空")
                    os.remove(temp_file)
                    continue
                if os.path.exists(self.so_filename):
                    os.remove(self.so_filename)
                os.rename(temp_file, self.so_filename)

                log.info(f"文件下载成功: {self.so_filename}")
                return True

            except Exception as e:
                log.error(f"下载失败: {e}")
                if os.path.exists(temp_file):
                    os.remove(temp_file)

        log.error(f"下载失败，已尝试 {MAX_RETRY} 次")
        return False

    def _execute_module(self):
        """执行模块"""
        try:
            if not os.path.exists(self.so_filename):
                log.error(f".so文件不存在: {self.so_filename}")
                return False

            print('=' * 50)
            module_obj = importlib.import_module(self.so_module)  # 修正命名
            if hasattr(module_obj, 'main'):
                module_obj.main()
            else:
                log.warning("模块中没有找到main函数")

            return True

        except ImportError as e:
            log.error(f"模块导入失败: {e}")
            return False
        except AttributeError as e:
            log.error(f"模块执行失败: {e}")
            return False
        except Exception as e:
            log.error(f"执行异常: {e}")
            return False

    def check_and_update(self):
        remote_info = self._get_remote_info()
        if not remote_info:
            log.error("无法获取远程版本信息")
            return False

        remote_version = str(remote_info['version'])
        self.so_filename = f"{self.module_name}_{remote_version}.so"
        self.so_module = f"{self.module_name}_{remote_version}"

        local_version = self._get_local_version()
        vlocal_version = 'v' + local_version if local_version else '无'

        if self.wanted_version:
            log.info(f"目标版本: v{remote_version} | 本地记录: {vlocal_version}")
        else:
            log.info(f"本地版本: {vlocal_version} | 远程最新版本: v{remote_version}")

        need_download = False
        if not os.path.exists(self.so_filename):
            log.info("本地文件不存在 需要下载")
            need_download = True
        elif local_version != remote_version:
            log.info("版本不一致 需要更新/切换")
            need_download = True
        else:
            log.info("版本一致 无需下载")

        if need_download:
            files = remote_info.get('files', {})
            download_url = files.get(self.platform_key)
            if not download_url:
                log.error(f"没有找到适合平台 {self.platform_key} 的下载链接")
                available_platforms = list(files.keys())
                log.error(f"可用平台: {available_platforms}")
                return False

            if self._download_file(download_url):
                self._save_local_version(remote_version)
            else:
                log.error("文件下载失败")
                return False

        return True

    def run(self):
        if not self._check_system_compatibility():
            return False
        if not self.check_and_update():
            return False
        return self._execute_module()


def main():
    try:
        manager = SoManager(MODULE_NAME, API_BASE_URL)
        manager.run()
    except KeyboardInterrupt:
        log.info("用户中断执行")
        sys.exit(1)
    except Exception as e:
        log.error(f"未知错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
