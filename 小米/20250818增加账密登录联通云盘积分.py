

#!/usr/bin/env python3

import subprocess
import os
import requests
import json
import platform

script_dir = os.path.dirname(os.path.abspath(__file__)) 

os.chdir(script_dir)

def detect_platform():
    system = platform.system().lower()
    arch = platform.machine().lower()

    print(f"检测到系统: {system}")
    print(f"检测到架构: {arch}")

    is_android = False
    try:
        if os.path.exists('/system/build.prop') or 'ANDROID_ROOT' in os.environ:
            is_android = True
            system = 'android'
    except:
        pass

    if is_android and arch in ['aarch64', 'arm64']:
        # Android ARM64
        return {
            'json_url': 'https://gitee.com/YCTZ/file/raw/master/LTYP3.json',
            'platform_name': 'Android ARM64',
            'file_pattern': 'android-arm64'
        }
    elif arch in ['aarch64', 'arm64', 'armv8', 'armv8l']:
        # ARM64
        return {
            'json_url': 'https://gitee.com/YCTZ/file/raw/master/LTYP2.json',
            'platform_name': 'ARM64',
            'file_pattern': 'arm64'
        }
    elif arch in ['armv7l', 'armv7', 'armv6l', 'armv6', 'arm']:
        # ARM32 (ARMv7)
        return {
            'json_url': 'https://gitee.com/YCTZ/file/raw/master/LTYP1.json',
            'platform_name': 'ARM32 (ARMv7)',
            'file_pattern': 'armv7'
        }
    else:
        # AMD64 (x86_64)
        return {
            'json_url': 'https://gitee.com/YCTZ/file/raw/master/LTYP.json',
            'platform_name': 'AMD64 (x86_64)',
            'file_pattern': 'amd64'
        }

def find_ltyp_files():
    """查找当前目录下所有LTYP文件"""
    ltyp_files = []
    for filename in os.listdir('.'):
        if filename.startswith('LTYP') and os.path.isfile(filename):
            ltyp_files.append(filename)
    return ltyp_files

def extract_version_from_filename(filename):
    try:
        name_part = filename.replace('LTYP-', '').replace('LTYP', '')
        if name_part.startswith('-'):
            name_part = name_part[1:]

        if '.' in name_part and name_part.endswith(('.exe', '.bin')):
            name_part = name_part.rsplit('.', 1)[0]

        version_parts = name_part.split('-')
        for part in version_parts:
            try:
                return float(part)
            except ValueError:
                continue
        return 0
    except:
        return 0

def delete_old_ltyp_files(keep_file=None):
    ltyp_files = find_ltyp_files()
    deleted_files = []

    for filename in ltyp_files:

        if filename.endswith('.py'):
            print(f"跳过 .py 文件: {filename}")
            continue
        if filename != keep_file:
            try:
                os.remove(filename)
                deleted_files.append(filename)
                print(f"已删除旧版本文件: {filename}")
            except Exception as e:
                print(f"删除文件 {filename} 失败: {e}")

    return deleted_files

def check_and_update_version():
    try:
        print("检查版本更新...")
        platform_config = detect_platform()
        json_url = platform_config['json_url']
        platform_name = platform_config['platform_name']

        print(f"使用 {platform_name} 平台配置")

        response = requests.get(json_url, timeout=10)
        response.raise_for_status()
        remote_info = response.json()

        remote_version = remote_info.get("version", 0)
        download_url = remote_info.get("Url", "")
        readme = remote_info.get("README", "")

        print(f"远程版本信息: {readme}")
        print(f"远程版本: {remote_version}")

        ltyp_files = find_ltyp_files()
        current_version = 0
        current_executable = None

        for filename in ltyp_files:
            file_version = extract_version_from_filename(filename)
            if file_version > current_version:
                current_version = file_version
                current_executable = filename

        if current_executable:
            print(f"当前文件: {current_executable}")
            print(f"当前版本: {current_version}")
        else:
            print("当前目录下没有LTYP文件")
            print("当前版本: 无")

        need_download = False
        if not current_executable:
            print("当前目录没有LTYP文件，开始下载...")
            need_download = True
        elif current_version < remote_version:
            print(f"发现新版本 {remote_version}，开始下载更新...")
            need_download = True
        else:
            print("当前版本已是最新版本")

        if need_download:
            print(f"⬇️正在下载: {download_url}")
            download_response = requests.get(download_url, timeout=30)
            download_response.raise_for_status()

            if '/' in download_url:
                new_filename = download_url.split('/')[-1]
            else:
                new_filename = f"LTYP-{remote_version}"

            if not new_filename.startswith('LTYP'):
                new_filename = f"LTYP-{remote_version}"

            with open(new_filename, 'wb') as f:
                f.write(download_response.content)

            if platform.system().lower() != 'windows':
                try:
                    subprocess.run(["chmod", "+x", new_filename], check=True)
                    print(f"为 {new_filename} 添加可执行权限...")
                except:
                    print("添加可执行权限失败，但文件已下载")

            deleted_files = delete_old_ltyp_files(keep_file=new_filename)
            if deleted_files:
                print(f"已清理 {len(deleted_files)} 个旧版本文件")

            print(f"更新完成！新版本已保存为: {new_filename}")
            return new_filename
        else:
            return current_executable

    except requests.RequestException as e:
        print(f"网络请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return None
    except Exception as e:
        print(f"版本检查失败: {e}")
        return None

target_executable = check_and_update_version()

if target_executable:
    executable = f"./{target_executable}"
    if platform.system().lower() != 'windows':
        try:
            subprocess.run(["chmod", "+x", executable], check=True)
        except:
            print("添加可执行权限失败，但继续运行")
else:
    print("未找到可执行文件，请检查目录下是否有LTYP文件")
    exit(1)

env = os.environ.copy()

print("🔍 检查环境变量...")

#多种环境变量
###tokenonline方式多账户用&回车等分割:
cookie_value = (
    os.environ.get("chinaUnicomCookie") or
    os.environ.get("CHINA_UNICOM_COOKIE") or
    os.environ.get("unicom_cookie") or
    os.environ.get("UNICOM_COOKIE") or
    ""
)

###账密登录多账户用&分割账密用#分割:例如15555555555#123456&15555555556#123456
chinaUnicomAccountCredentials = os.environ.get("chinaUnicomAccountCredentials", "")

if cookie_value:
    print(f"环境变量配置正常")
    env.update({
        "chinaUnicomCookie": cookie_value,
    })
else:
    print("未找到chinaUnicomCookie环境变量")
    print("请在青龙面板中设置 chinaUnicomCookie 环境变量")

###---要通知就自己选个---###
qywx_key = os.environ.get("QYWX_KEY", "")#企业微信配置
wxpusher_token = os.environ.get("WXPUSHER_TOKEN", "")


if qywx_key:
    env["QYWX_KEY"] = qywx_key
    print(f"已配置企业微信推送")

if wxpusher_token:
    env["WXPUSHER_TOKEN"] = wxpusher_token
    print(f"已配置WxPusher推送")

print(f"正在运行 {executable}...")
result = subprocess.run([executable], env=env)

if result.returncode == 0:
    print("Success!")
else:
    print(f"Failed code: {result.returncode}")