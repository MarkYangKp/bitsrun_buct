"""
BitSRun - 深澜校园网自动认证工具核心模块

该模块实现了深澜校园网认证的核心功能，包括IP获取、令牌验证和登录流程。
"""

import requests
import time
import hashlib
import hmac
import json
import re
import logging
import sys
from utils.xencoding import get_xencode
from utils.base64_utils import get_base64

def setup_logging(level=logging.INFO):
    """设置日志系统"""
    logger = logging.getLogger('bitsrun')
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 控制台处理器
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(level)
        
        # 格式化器
        if level == logging.DEBUG:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        else:
            formatter = logging.Formatter('%(message)s')
            
        console.setFormatter(formatter)
        logger.addHandler(console)
    
    return logger

class BitSRun:
    """深澜校园网认证客户端"""
    
    def __init__(self, config):
        """
        初始化客户端
        
        参数:
            config (ConfigParser): 配置对象
        """
        self.logger = logging.getLogger('bitsrun')
        
        # 从配置文件加载设置
        self._load_config(config)
        
        # 初始化会话
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 初始化状态变量
        self.ip = ""
        self.login_username = ""
        
    def _load_config(self, config):
        """
        从配置文件加载设置
        
        参数:
            config (ConfigParser): 配置对象
        """
        # 登录凭据
        self.username = config.get('Credentials', 'username', fallback='')
        self.password = config.get('Credentials', 'password', fallback='')
        self.user_type = config.get('Credentials', 'user_type', fallback='')
        
        # 服务器设置
        self.server_url = config.get('Server', 'url', 
                                     fallback='http://202.4.130.95')
        
        # 登录参数
        self.ac_id = config.get('Parameters', 'ac_id', fallback='1')
        self.enc_ver = config.get('Parameters', 'enc_ver', fallback='srun_bx1')
        self.n = config.get('Parameters', 'n', fallback='200')
        self.type = config.get('Parameters', 'type', fallback='1')
        self.os = config.get('Parameters', 'os', fallback='Windows 10')
        self.name = config.get('Parameters', 'name', fallback='Windows')
        self.double_stack = config.get('Parameters', 'double_stack', fallback='0')
        self.info_prefix = config.get('Parameters', 'info_prefix', fallback='SRBX1')
        
        # 守卫模式配置
        self.guard_enable = config.getboolean('Guard', 'enable', fallback=False)
        self.guard_interval = config.getint('Guard', 'interval', fallback=300)
        
        # 请求头
        self.headers = {
            'User-Agent': config.get(
                'Headers', 'user_agent', 
                fallback='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36'
            )
        }
        
    def get_ip(self):
        """
        获取本机IP地址
        
        返回:
            bool: 是否成功获取IP
        """
        self.logger.info("正在获取IP地址...")
        
        try:
            # 访问登录页面获取IP信息
            init_res = self.session.get(
                f"{self.server_url}/srun_portal_pc?ac_id={self.ac_id}&theme=basic"
            )
            
            # 使用正则表达式提取IP地址
            ip_match = re.search(r'ip\s*:\s*"(.*?)"', init_res.text)
            
            if ip_match:
                self.ip = ip_match.group(1)
                self.logger.info(f"IP获取成功: {self.ip}")
                return True
            else:
                self.logger.error("无法从页面提取IP地址")
                return False
                
        except Exception as e:
            self.logger.error(f"获取IP异常: {str(e)}")
            return False
    
    def _get_md5(self, password, token):
        """
        使用HMAC-MD5算法对密码进行加密
        
        参数:
            password (str): 密码
            token (str): 认证令牌
            
        返回:
            str: 加密后的密码
        """
        return hmac.new(token.encode(), password.encode(), hashlib.md5).hexdigest()
    
    def _get_sha1(self, value):
        """
        对值进行SHA1哈希计算
        
        参数:
            value (str): 要计算的值
            
        返回:
            str: 哈希结果
        """
        hash_obj = hashlib.sha1(value.encode())
        hex_digest = hash_obj.hexdigest()
        # 添加换行符以与原版保持一致
        return hex_digest + "\n"
    
    def _get_info(self):
        """
        生成认证信息JSON
        
        返回:
            str: JSON格式的认证信息
        """
        info_data = {
            "username": self.login_username,
            "password": self.password,
            "ip": self.ip,
            "acid": self.ac_id,
            "enc_ver": self.enc_ver
        }
        return json.dumps(info_data, separators=(',', ':'))
    
    def _get_chksum(self, token, login_username, hmd5, ip, info_str):
        """
        生成校验和
        
        参数:
            token (str): 认证令牌
            login_username (str): 登录用户名
            hmd5 (str): 加密后的密码
            ip (str): IP地址
            info_str (str): 加密后的信息
            
        返回:
            str: 校验和
        """
        chkstr = token + login_username
        chkstr += token + hmd5
        chkstr += token + self.ac_id
        chkstr += token + ip
        chkstr += token + self.n
        chkstr += token + self.type
        chkstr += token + info_str
        return self._get_sha1(chkstr)
    
    def _request(self, path, params=None):
        """
        发送API请求
        
        参数:
            path (str): 请求路径
            params (dict): 请求参数
            
        返回:
            dict: 解析后的响应数据
        """
        if params is None:
            params = {}
        
        timestamp = int(time.time() * 1000)  # 毫秒级时间戳
        callback = f"jQuery_{timestamp}"
        
        params["callback"] = callback
        params["_"] = timestamp
        
        url = f"{self.server_url}/{path}"
        self.logger.debug(f"HTTP GET {url}")
        self.logger.debug(f"参数: {params}")
        
        try:
            response = self.session.get(url, params=params)
            self.logger.debug(f"HTTP状态码: {response.status_code}")
            
            content = response.text
            self.logger.debug(f"原始响应: {content}")
            
            # 去除jQuery回调包装
            if callback in content:
                content = content[content.find("(")+1:content.rfind(")")]
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON解析错误: {e}")
                    return None
            else:
                self.logger.error("响应中没有找到callback")
                return None
        except Exception as e:
            self.logger.error(f"请求出错: {e}")
            return None
    
    def check_online(self):
        """
        检查当前在线状态
        
        返回:
            bool: 是否在线
        """
        self.logger.info("检查在线状态...")
        res = self._request("cgi-bin/rad_user_info")
        
        if res and "error" in res:
            if res["error"] == "ok":
                self.logger.info("当前已在线")
                if "online_ip" in res:
                    self.logger.info(f"在线IP: {res['online_ip']}")
                elif "client_ip" in res:
                    self.logger.info(f"客户端IP: {res['client_ip']}")
                return True
            else:
                self.logger.info("当前未在线")
                return False
        
        self.logger.error("检查在线状态失败")
        return False
    
    def login(self):
        """
        执行登录流程
        
        返回:
            bool: 是否登录成功
        """
        # 处理用户名（添加运营商类型）
        self.login_username = self.username
        if self.user_type:
            self.login_username += f"@{self.user_type}"
        
        self.logger.info(f"准备使用账号 {self.login_username} 登录...")
        
        # 获取认证令牌
        challenge_params = {
            "username": self.login_username,
            "ip": self.ip
        }
        
        res = self._request("cgi-bin/get_challenge", challenge_params)
        if not res or "challenge" not in res:
            self.logger.error("获取token失败")
            return False
            
        token = res["challenge"]
        self.logger.debug(f"获取token成功: {token}")
        
        # 生成info加密数据
        info_str = self._get_info()
        self.logger.debug(f"原始info: {info_str}")
        
        # 使用xencode加密
        xencode_str = get_xencode(info_str, token)
        
        # Base64编码, 添加前缀
        prefix = ""
        if self.info_prefix:
            prefix = "{" + self.info_prefix + "}"
        info_encoded = prefix + get_base64(xencode_str)
        
        self.logger.debug(f"加密后info: {info_encoded}")
        
        # 计算密码的MD5值
        md5_pwd = self._get_md5(self.password, token)
        hmd5 = "{MD5}" + md5_pwd
        self.logger.debug(f"加密后密码: {hmd5}")
        
        # 计算校验和
        chksum = self._get_chksum(token, self.login_username, md5_pwd, self.ip, info_encoded)
        self.logger.debug(f"校验和: {chksum}")
        
        # 构造登录请求
        login_params = {
            "action": "login",
            "username": self.login_username,
            "password": hmd5,
            "ac_id": self.ac_id,
            "ip": self.ip,
            "info": info_encoded,
            "chksum": chksum,
            "n": self.n,
            "type": self.type,
            "os": self.os,
            "name": self.name,
            "double_stack": self.double_stack
        }
        
        # 发送登录请求
        login_res = self._request("cgi-bin/srun_portal", login_params)
        
        # 检查是否登录成功
        if login_res and "error" in login_res:
            if login_res["error"] == "ok":
                self.logger.info("登录成功!")
                return True
            else:
                error_msg = login_res.get("error_msg", "未知错误")
                self.logger.error(f"登录失败: {login_res['error']} - {error_msg}")
                return False
        else:
            self.logger.error("登录请求未返回有效响应")
            return False
    
    def run(self):
        """执行完整的认证流程"""
        # 获取IP地址
        if not self.get_ip():
            self.logger.error("未能获取IP地址，退出程序")
            return False
        
        # 检查是否已经在线
        if self.check_online():
            self.logger.info("已经在线，无需重新登录")
            return True
            
        # 执行登录
        login_result = self.login()
        if login_result:
            self.logger.info("登录流程执行完成")
            # 再次检查在线状态
            return self.check_online()
        else:
            self.logger.error("登录失败，请检查配置和网络")
            return False
    
    def guard(self, interval_seconds=300):
        """
        认证守卫模式，定期检查登录状态，在需要时进行自动登录
        
        参数:
            interval_seconds (int): 检查间隔，单位为秒
        """
        self.logger.info(f"认证守卫已启动，每 {interval_seconds} 秒检查一次登录状态")
        
        try:
            while True:
                # 记录当前时间
                check_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                self.logger.info(f"[{check_time}] 开始检查登录状态")
                
                # 获取IP地址(每次都刷新获取，避免IP变化问题)
                if not self.get_ip():
                    self.logger.error("获取IP地址失败，将在下次继续尝试")
                    time.sleep(interval_seconds)
                    continue
                
                # 检查在线状态
                if self.check_online():
                    self.logger.info("当前已在线，保持连接")
                else:
                    self.logger.warning("当前未登录或连接已断开，尝试重新登录")
                    if self.login():
                        self.logger.info("自动重新登录成功")
                    else:
                        self.logger.error("自动重新登录失败，将在下次继续尝试")
                
                # 等待到下一次检查
                self.logger.info(f"下次检查将在 {interval_seconds} 秒后进行")
                time.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            self.logger.info("认证守卫被用户手动停止")
        except Exception as e:
            self.logger.error(f"认证守卫发生异常: {str(e)}")
            raise
