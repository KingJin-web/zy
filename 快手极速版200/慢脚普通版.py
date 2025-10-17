#   ===========================================
#   ==================广告======================
#   ============================================
#   抓包工具 https://pan.quark.cn/s/44f90724e243
#   * 代理推荐：通过注册链接注册后，一对一成为您的专属代理，注册后提供账号，为您设置最优价格
#   http://www.tianxingip.com/proxy/index/index/code/hnking/p/2847.html 天行sk5代理 5一条
#   https://www.xiequ.cn/index.html?d630539f 注册送10元免费使用长效独享代理一天
#  http://www.gzsk5.com/#/register?invitation=hnking&shareid=425 光子sk5代理100M 4.5一条

#   入口: 快手极速版App 一机一号一个实名 只限安卓机器 （无需root） 最好一号一ip
#   抓包工具 https://pan.quark.cn/s/44f90724e243
#   需抓取数据:
#   * 登录时搜索 api_client_salt 找到5kb左右的链接 在响应里最下面找到你的salt 不会可以用一键抓取
#   * 开抓包点福利后 搜索 earn/overview/tasks 找到此请求的cookie 同时找到此请求下的请求头的user-agent的值
import os
import urllib.request
import sys
import time
import platform


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

####################使用教程区####################

#广告类型：1为普通广告， 2为200广(已单独剔出)，3为宝箱广告，其他值为以上全部执行,默认全部执行
# 抓包 ck和salt
# 格式1：备注#Cookie#salt#广告类型(备注#Cookie#salt#1,3)
# 格式2：备注#Cookie#salt#广告类型#sock5
#广告类型为列表模式，使用英文逗号隔开，填什么就指定跑什么
# socks5存在则使用代理，反之
# socks代理选择参数，可填可不填 格式：ip|port|username|password
# ck变量：ksck, 填写上面两种格式ck均可，多号新建变量即可
# 并发变量：KSP_BF, 设置为False为关闭并发，默认开启
# 卡密变量：KSP_Card 填写购买的卡密即可
# 金币自动兑换变量：KSP_JBDH 默认关闭，True开启
# 运行延迟变量：KSP_YC 默认30,45，格式为【最低,最高】，中间英文逗号隔开
# 运行次数变量：KSP_YXCS 默认200
# 金币控制变量：KSP_JBMAX 默认500000
# 广告模式变量：KSP_ADMS 默认为1(正常广告)，设置2为追加(理论默认即可)
# 自动更换did变量：KSP_DID 默认关闭，True开启(实测不好用)
# 自动更换did金币数量变量：KSP_JBSU 低于多少尝试更换did，默认1000，自动更换开启生效


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
            f'https://raw.bgithub.xyz/BIGOSTK/pyso/refs/heads/main/ksadp_{current_arch}_{PythonV}.so',
            f'https://gh-proxy.com/https://raw.githubusercontent.com/BIGOSTK/pyso/main/ksadp_{current_arch}_{PythonV}.so',
            f'https://raw.githubusercontent.com/BIGOSTK/pyso/main/ksadp_{current_arch}_{PythonV}.so',
            f'https://raw.bgithub.xyz/BIGOSTK/pyso/main/ksadp_{current_arch}_{PythonV}.so'
        ]

        last_error = None
        for url in mirrors:
            try:
                print(f'尝试从 {url} 下载...')
                with urllib.request.urlopen(url, timeout=15) as response:
                    if response.status == 200:
                        with open('./ksadp.so', 'wb') as out_file:
                            out_file.write(response.read())
                        print('下载成功')
                        return True, None
            except Exception as e:
                last_error = e
                print(f'下载失败: {e}')
                time.sleep(1)

        return False, f'所有镜像尝试失败: {last_error}'

    except Exception as e:
        return False, e


def main():
    if not os.path.exists('./ksadp.so'):
        success, error = GET_SO()
        if not success:
            print(f'无法获取ksadp.so: {error}')
            return

    try:
        import ksadp
        ksadp.main()
    except ImportError as e:
        print(f'导入ksadp模块失败: {e}')
    except Exception as e:
        print(f'执行ksadp.main()时出错: {e}')


if __name__ == '__main__':
    main()
