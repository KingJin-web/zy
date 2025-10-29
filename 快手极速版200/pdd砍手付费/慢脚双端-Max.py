#####################################砍手双端-Max################################################

# 需要安装python依赖：PySocks , pycryptodome, packaging
#   ===========================================
#   ==================广告======================
#   ============================================
#   抓包工具 https://pan.quark.cn/s/44f90724e243
#   * 代理推荐：通过注册链接注册后，一对一成为您的专属代理，注册后提供账号，为您设置最优价格
#   http://www.tianxingip.com/proxy/index/index/code/hnking/p/2847.html 天行sk5代理 5一条
#   https://www.xiequ.cn/index.html?d630539f 注册送10元免费使用长效独享代理一天
#  http://www.gzsk5.com/#/register?invitation=hnking2&shareid=516 光子sk5代理100M 4.5一条
# 本脚本为快手普通版和快手极速版合并版，ck填写哪个版本的ck就自动运行指定快手版本，脚本自动检测快手版本类型
# 本脚本为快手普通版和快手极速版合并版，ck填写哪个版本的ck就自动运行指定快手版本，脚本自动检测快手版本类型
# 本脚本为快手普通版和快手极速版合并版，ck填写哪个版本的ck就自动运行指定快手版本，脚本自动检测快手版本类型

# 支持系统类型：arm，amd64，不支持windos，支持py版本：3.10，3.11
# 支持系统类型：arm，amd64，不支持windos，支持py版本：3.10，3.11
# 支持系统类型：arm，amd64，不支持windos，支持py版本：3.10，3.11

######################################使用教程区#################################################
print('''https://www.jichiy.com/views/login.html#?promotionCode=319256E847DF4C26986A63AC04155561 极驰云
http://www.tianxingip.com/proxy/index/index/code/hnking/p/2847.html 天行sk5代理 5一条
https://www.xiequ.cn/index.html?d630539f 注册送10元免费使用长效独享代理一天
http://www.gzsk5.com/#/register?invitation=hnking2&shareid=516 光子sk5代理100M 4.5一条''')
# 极速版广告类型：1为饭补， 2为看广告，3为宝箱广告，4为200广
# 极速版全局广告类型变量：KS_JSLX，列表模式，写什么就运行指定类型任务，格式：1,2,3，数字之间使用英文逗号隔开，不写则默认运行全部，
# 普通版广告类型：1为看广告，2为200广，3为宝箱广告
# 极速版全局广告类型变量：KS_PTLX，列表模式，写什么就运行指定类型任务，格式：1,2,3，数字之间使用英文逗号隔开，不写则默认运行全部，
# 抓包 ck和salt
# 格式1：Cookie#salt（一键抓包参数）
# 格式2：Cookie#salt#sock5代理（一键抓包参数#socks代理）
# 格式3：备注#Cookie#salt（一键抓包参数）
# 格式4：备注#Cookie#salt#sock5代理（一键抓包参数#socks代理）
# ck前面添加备注则使用备注，不写默认账号名
# 广告类型为列表模式，使用英文逗号隔开，填什么就指定跑什么
# socks5存在则使用代理，反之
# socks代理选择参数，可填可不填 格式：ip|port|username|password
# ck变量：ksmaxck, 填写上面两种格式ck均可，多号新建变量即可
# 并发变量：KS_BF, 设置为False为关闭并发，默认开启
# 并发模式变量：KS_BFMS, 写1或者2，默认2，某些情况运行脚本后无法手动停止时可切换并发模式尝试解决
# 卡密变量：KS_Card 填写购买的卡密即可
# 金币自动兑换变量：KS_JBDH 默认关闭，True开启 (仅支持极速版)
# 自动提现变量：KS_TX 默认关闭，True开启 (仅支持极速版)
# 提现金额变量：KS_TXAmout 默认50，只支持3，10，20，50 类型 (仅支持极速版)
# 运行延迟变量：KS_YC 默认30,45，格式为【最低,最高】，不要【】，中间英文逗号隔开
# 运行次数变量：KS_YXCS 默认50，每个类型广告运行指定次数后切换下一个广告类型
# 金币控制变量：KS_JBMAX 默认500000，金币达到当前数量则结束运行（已修改为当日获得金币，而不是账号金币总余额）
# 广告模式变量：KS_ADMS 默认为1(正常广告)，设置2为追加(理论默认即可)，正常广告只有几条跑完无广告后可修改为2后继续尝试
# 自动更换did变量：KS_DID 默认关闭，True开启(外面的养号)
# 自动更换did金币数量变量：KS_JBSU 低于多少尝试更换did，默认1000，自动更换开启生效

###############################################################################################
# 注意：上面变量理论默认值即可，自己需要改的设置变量修改即可，不需要改的变量切勿设置变量后值留空，不然会报错
# 注意：上面变量理论默认值即可，自己需要改的设置变量修改即可，不需要改的变量切勿设置变量后值留空，不然会报错
# 注意：上面变量理论默认值即可，自己需要改的设置变量修改即可，不需要改的变量切勿设置变量后值留空，不然会报错
###############################################################################################



import os
import urllib.request
import sys
import time
import requests
import platform
from packaging import version


class SystemChecker:
    @staticmethod
    def is_arm_architecture():
        """检测是否为ARM架构"""
        machine = platform.machine().lower()
        arm_patterns = [
            'arm', 'aarch', 'arm64', 'aarch64',
            'armv7', 'armv8', 'armhf'
        ]
        return any(pattern in machine for pattern in arm_patterns)

    @staticmethod
    def is_amd_architecture():
        """检测是否为AMD/x86架构"""
        machine = platform.machine().lower()
        amd_patterns = [
            'x86_64', 'amd64', 'x86', 'i386', 'i686',
            'amd', 'intel', 'x64'
        ]
        return any(pattern in machine for pattern in amd_patterns)

    @staticmethod
    def is_supported_architecture():
        """检测是否支持ARM或AMD架构"""
        return SystemChecker.is_arm_architecture() or SystemChecker.is_amd_architecture()

    @staticmethod
    def is_linux_supported():
        """检测是否为Linux且支持ARM或AMD架构"""
        return SystemChecker.is_supported_architecture()

    @staticmethod
    def get_architecture_type():
        """获取具体的架构类型"""
        if SystemChecker.is_arm_architecture():
            return 'arm'
        elif SystemChecker.is_amd_architecture():
            return 'amd'
        else:
            return 'unknown'

    @staticmethod
    def get_detailed_info():
        return {
            'os': platform.system(),
            'architecture': platform.machine(),
            'arch_type': SystemChecker.get_architecture_type()
        }


checker = SystemChecker()

if checker.is_linux_supported():
    pass
else:
    info = checker.get_detailed_info()
    print(f'当前系统不支持,当前系统类型: {info["os"]},系统架构: {info["architecture"]}')
    exit(1)

def get_architecture():
    """获取系统架构"""
    arch = platform.machine().lower()
    if 'arm' in arch or 'aarch' in arch:
        return 'arm'
    elif 'x86' in arch or 'amd' in arch or 'i386' in arch or 'i686' in arch:
        return 'amd'
    else:
        return arch

current_arch = get_architecture()


def GET_SO():
    PythonV = sys.version_info
    if PythonV.major == 3 and PythonV.minor == 10:
        PythonV = '10'
        print('当前Python版本为3.10 开始安装...')
    elif PythonV.major == 3 and PythonV.minor == 11:
        PythonV = '11'
        print('当前Python版本为3.11 开始安装...')
    else:
        return False, f'不支持的Python版本：{sys.version}'

    try:
        mirrors = [
            f'https://raw.bgithub.xyz/BIGOSTK/pyso/refs/heads/main/ksmax_{current_arch}_{PythonV}.so',
            f'https://gh-proxy.com/https://raw.githubusercontent.com/BIGOSTK/pyso/main/ksmax_{current_arch}_{PythonV}.so',
            f'https://raw.githubusercontent.com/BIGOSTK/pyso/main/ksmax_{current_arch}_{PythonV}.so',
            f'https://raw.bgithub.xyz/BIGOSTK/pyso/main/ksmax_{current_arch}_{PythonV}.so'
        ]

        last_error = None
        for url in mirrors:
            try:
                print(f'尝试从 {url} 下载...')
                with urllib.request.urlopen(url, timeout=15) as response:
                    if response.status == 200:
                        with open('./ksmax.so', 'wb') as out_file:
                            out_file.write(response.read())
                        print('下载更新成功')
                        return True, None
            except Exception as e:
                last_error = e
                print(f'下载更新失败: {e}')
                time.sleep(1)

        return False, f'所有镜像尝试失败: {last_error}'

    except Exception as e:
        return False, e

def get_version():
    url = 'https://gh-proxy.com/https://raw.githubusercontent.com/BIGOSTK/pyso/main/ksmax_ver.json'
    try:
        r = requests.get(url)
        r.raise_for_status()
        remote_version = r.json()['ksmax']['version']
        return remote_version
    except Exception as e:
        return None

def restart_script():
    print("检测到更新，正在重启脚本...")
    python_executable = sys.executable
    script_path = os.path.abspath(__file__)
    os.execv(python_executable, [python_executable, script_path])

def main():
    need_restart = False

    if not os.path.exists('./ksmax.so'):
        print("未找到ksmax.so文件，开始下载...")
        success, error = GET_SO()
        if not success:
            print(f'无法获取ksmax.so: {error}')
            return
        need_restart = True
    else:
        try:
            import ksmax
            LocalVersion = ksmax.get_ver()
            YunVersion = get_version()
            if YunVersion is not None and version.parse(LocalVersion) != version.parse(YunVersion):
                print(f"检测到新版本: {YunVersion} (当前: {LocalVersion})，开始更新...")
                success, error = GET_SO()
                if success:
                    need_restart = True
                else:
                    print(f'更新失败: {error}')
        except ImportError:
            print("ksmax.so文件损坏或版本不兼容，重新下载...")
            success, error = GET_SO()
            if success:
                need_restart = True
            else:
                print(f'重新下载失败: {error}')
                return

    if need_restart:
        restart_script()

    try:
        import ksmax
        ksmax.main()
    except ImportError as e:
        print(f'导入ksmax模块失败: {e}')
        print("尝试重新下载模块...")
        success, error = GET_SO()
        if success:
            restart_script()
        else:
            print(f'重新下载失败: {e}')
    except Exception as e:
        print(f'执行ksmax.main()时出错: {e}')


if __name__ == '__main__':
    main()