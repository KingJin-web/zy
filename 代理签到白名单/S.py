import socket
import struct
import sys
import argparse
from urllib.parse import urlparse
import ssl

# SOCKS5协议常量
SOCKS5_VERSION = 0x05
AUTH_NO_AUTH = 0x00
AUTH_USER_PASS = 0x02
AUTH_SUCCESS = 0x00
CMD_CONNECT = 0x01
ATYP_IPV4 = 0x01
ATYP_DOMAIN = 0x03
ATYP_IPV6 = 0x04


class Socks5ProxyTester:
    def __init__(self, proxy_host, proxy_port, username=None, password=None, timeout=10):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.socket = None

    def _connect_proxy(self):
        """建立与SOCKS5代理服务器的连接"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.proxy_host, self.proxy_port))
            return True
        except Exception as e:
            print(f"连接代理服务器失败: {str(e)}")
            return False

    def _handshake_auth(self):
        """SOCKS5握手与认证"""
        # 第一步：发送认证方法请求
        auth_methods = [AUTH_NO_AUTH]
        if self.username and self.password:
            auth_methods.append(AUTH_USER_PASS)

        # 构造握手请求：版本(1字节) + 方法数量(1字节) + 方法列表(n字节)
        handshake = struct.pack('!BB', SOCKS5_VERSION, len(auth_methods)) + bytes(auth_methods)
        self.socket.sendall(handshake)

        # 接收服务器响应：版本(1字节) + 选中的方法(1字节)
        response = self.socket.recv(2)
        if len(response) != 2 or response[0] != SOCKS5_VERSION:
            raise Exception("SOCKS5协议版本不匹配")

        selected_method = response[1]
        if selected_method == 0xFF:  # 无可用认证方法
            raise Exception("代理服务器不支持提供的认证方法")

        # 第二步：如果需要用户名密码认证
        if selected_method == AUTH_USER_PASS:
            # 构造认证请求：版本(1字节) + 用户名长度(1字节) + 用户名 + 密码长度(1字节) + 密码
            user_len = len(self.username.encode('utf-8'))
            pass_len = len(self.password.encode('utf-8'))
            auth_req = struct.pack('!BB', 0x01, user_len) + self.username.encode('utf-8')
            auth_req += struct.pack('!B', pass_len) + self.password.encode('utf-8')
            self.socket.sendall(auth_req)

            # 接收认证结果：版本(1字节) + 状态(1字节，0x00为成功)
            auth_resp = self.socket.recv(2)
            if len(auth_resp) != 2 or auth_resp[0] != 0x01 or auth_resp[1] != AUTH_SUCCESS:
                raise Exception("用户名或密码认证失败")

        return True

    def _send_connect_request(self, target_host, target_port):
        """向代理服务器发送CONNECT命令，请求连接目标地址"""
        # 构造目标地址部分（支持域名或IP）
        try:
            # 尝试解析为IPV4地址
            target_ip = socket.inet_aton(target_host)
            atyp = ATYP_IPV4
            addr_data = target_ip
        except socket.error:
            # 否则按域名处理
            atyp = ATYP_DOMAIN
            addr_len = len(target_host.encode('utf-8'))
            addr_data = struct.pack('!B', addr_len) + target_host.encode('utf-8')

        # 构造CONNECT请求：版本(1字节) + 命令(1字节) + 保留位(1字节) + 地址类型(1字节) + 地址 + 端口(2字节)
        request = struct.pack('!BBB', SOCKS5_VERSION, CMD_CONNECT, 0x00)
        request += struct.pack('!B', atyp) + addr_data
        request += struct.pack('!H', target_port)  # 端口（网络字节序）
        self.socket.sendall(request)

        # 接收响应：版本(1字节) + 状态(1字节) + 保留位(1字节) + 地址类型(1字节) + ...
        response = self.socket.recv(4)
        if len(response) != 4 or response[0] != SOCKS5_VERSION:
            raise Exception("CONNECT响应格式错误")

        status = response[1]
        if status != 0x00:  # 0x00表示成功，其他为错误（如0x05=拒绝）
            error_msg = {
                0x01: "一般SOCKS服务器故障",
                0x02: "规则集拒绝连接",
                0x03: "网络不可达",
                0x04: "主机不可达",
                0x05: "连接被拒绝",
                0x06: "TTL过期",
                0x07: "命令不支持",
                0x08: "地址类型不支持"
            }.get(status, f"未知错误（状态码：{status}）")
            raise Exception(f"代理服务器拒绝连接目标：{error_msg}")

        return True

    def test_connection(self, target_url="https://www.baidu.com"):
        """测试代理能否访问目标URL"""
        parsed_url = urlparse(target_url)
        target_host = parsed_url.hostname
        target_port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)

        try:
            # 1. 连接代理服务器
            if not self._connect_proxy():
                return False

            # 2. 完成认证握手
            self._handshake_auth()

            # 3. 请求连接目标地址
            self._send_connect_request(target_host, target_port)

            # 4. 通过代理发送HTTP请求验证连通性
            if parsed_url.scheme == 'https':
                # HTTPS需要SSL握手
                context = ssl.create_default_context()
                ssl_socket = context.wrap_socket(self.socket, server_hostname=target_host)
                sock = ssl_socket
            else:
                sock = self.socket

            # 发送简单HTTP请求
            request = f"GET {parsed_url.path or '/'} HTTP/1.1\r\nHost: {target_host}\r\nConnection: close\r\n\r\n"
            sock.sendall(request.encode('utf-8'))

            # 接收响应（只需要确认有响应即可）
            response = sock.recv(1024)
            if response:
                print(f"\n代理测试成功！\n目标响应片段：{response[:200].decode('utf-8', errors='ignore')}")
                return True
            else:
                raise Exception("未收到目标服务器响应")

        except Exception as e:
            print(f"\n代理测试失败: {str(e)}")
            return False
        finally:
            if self.socket:
                self.socket.close()


def main():
    print("===== SOCKS5代理测试工具 =====")

    # 解析输入的代理信息（格式：host|port|user|pass）
    proxy_input = input("请输入代理信息（格式：host|port|username|password）：")
    parts = proxy_input.strip().split('|')
    if len(parts) < 2:
        print("格式错误！请使用：host|port|username|password（用户名和密码可选）")
        sys.exit(1)

    proxy_host = parts[0]
    try:
        proxy_port = int(parts[1])
    except ValueError:
        print("端口必须是数字！")
        sys.exit(1)
    username = parts[2] if len(parts) > 2 and parts[2] else None
    password = parts[3] if len(parts) > 3 and parts[3] else None

    # 可选：自定义测试目标
    target_url = input("请输入测试目标URL（默认：https://www.baidu.com）：") or "https://www.baidu.com"

    # 执行测试
    tester = Socks5ProxyTester(proxy_host, proxy_port, username, password)
    tester.test_connection(target_url)


if __name__ == "__main__":
    main()