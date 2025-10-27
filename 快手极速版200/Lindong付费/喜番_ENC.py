
#   入口: 喜番App 一机一号一个实名 只限安卓机器 （无需root）
#   需抓取数据: 
#   * 开抓包点福利后 搜索/inspire/home 找到此请求的cookie例如kssig==****;playlet.api_st=****; userId=****;...同时找到此请求下的请求体的message的值 获取请求头的SystemUa和BrowserUa的值
#   * 如果一个青龙跑两号及以上 则就需要填写socket5代理防止黑ip,注意一号一代理,不允许多号共用 第一个号不使用代理则不填 @代理ip|端口|代理用户名|代理密码
#   * 变量: lindong_xf 填写上面获取的数据 格式为 备注@cookie@message@SystemUa@BrowserUa [@代理ip|端口|代理用户名|代理密码](可选) 多号换行或新建同名变量
#   * 变量: lindong_XFKami 卡密变量
#   * 可选变量(可不填)： lindong_XF_limit    最大运行金币量 默认 1500000
#   * 可选变量(可不填)： lindong_XF_thread   最大线程数     默认 1
#   * 可选变量(可不填)： lindong_XF_sleepTimes 广告间休眠时间 是区间用英文逗号隔开 默认为 22,28 即在22-28之间随机取值 自己把握
#   * 需要安装依赖: py的 requests[socks]
#   * 多号方式 [ 换行 | 新建同名变量 | & 分割 ]
#   * 此版本更换玄学养号逻辑 自行判断哪个版本好用用哪个就行了
#   * tg群组:https://t.me/+WSJMTfFFBI1kM2Q1
#   ===========================================
#   ==================广告======================
#   ============================================
#
#   * 代理推荐：通过注册链接注册后，一对一成为您的专属代理，注册后提供账号，为您设置最优价格
#   http://www.tianxingip.com/proxy/index/index/code/hnking/p/2847.html 天行sk5代理 5一条
#   https://www.xiequ.cn/index.html?d630539f 注册送10元免费使用长效独享代理一天
#  http://www.gzsk5.com/#/register?invitation=hnking2&shareid=516 光子sk5代理100M 4.5一条
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
    print("请安装依赖: pip install requests")
    sys.exit(1)


MODULE_NAME = 'xf'
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
        

    
    def _get_arch(self):
        machine = platform.machine().lower()
        if machine in ['x86_64', 'amd64', 'x64']:
            return 'x64'
        elif machine in ['aarch64', 'arm64']:
            return 'aarch64'
        else:
            log.warning(f"未知架构 {machine}，默认使用 x64")
            return 'x64'
    
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
    
    def _get_remote_latest(self):
        try:
            payload = {
                "action": "get_latest",
                "module_name": self.module_name
            }
            
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
            log.error(f"获取远程版本失败: {e}")
            return None
    
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
            module_obj = importlib.import_module(self.so_moudel)
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
        remote_info = self._get_remote_latest()
        if not remote_info:
            log.error("无法获取远程版本信息")
            return False
        remote_version = str(remote_info['latest_version'])
        self.so_filename = f"{self.module_name}_{remote_version}.so"
        self.so_moudel = f"{self.module_name}_{remote_version}"
        local_version = self._get_local_version()
        vlocal_version = 'v' + local_version if local_version else '无'
        
        log.info(f"本地版本: {vlocal_version} | 远程最新版本: v{remote_version}")
        need_download = False
        if not os.path.exists(self.so_filename):
            log.info("本地文件不存在，需要下载")
            need_download = True
        elif local_version != remote_version:
            log.info("版本不一致，需要更新")
            need_download = True
        else:
            log.info("版本已是最新，无需下载")

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