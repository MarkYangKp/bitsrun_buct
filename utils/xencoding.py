"""
XEncoding 加密工具
提供兼容深澜认证系统的加密编码实现
"""

import math

def force(msg):
    """
    强制转换字符串为字节序列
    
    参数:
        msg (str): 输入字符串
        
    返回:
        bytes: 字节序列
    """
    ret = []
    for w in msg:
        ret.append(ord(w))
    return bytes(ret)

def ordat(msg, idx):
    """
    获取字符串指定位置的字符ASCII码
    
    参数:
        msg (str): 输入字符串
        idx (int): 索引位置
        
    返回:
        int: 字符的ASCII码
    """
    if len(msg) > idx:
        return ord(msg[idx])
    return 0

def sencode(msg, key):
    """
    编码消息
    
    参数:
        msg (str): 输入消息
        key (bool): 是否添加长度
        
    返回:
        list: 编码后的整数列表
    """
    l = len(msg)
    pwd = []
    for i in range(0, l, 4):
        pwd.append(
            ordat(msg, i) | ordat(msg, i + 1) << 8 | ordat(msg, i + 2) << 16
            | ordat(msg, i + 3) << 24)
    if key:
        pwd.append(l)
    return pwd

def lencode(msg, key):
    """
    解码消息
    
    参数:
        msg (list): 编码后的整数列表
        key (bool): 是否包含长度
        
    返回:
        str: 解码后的字符串
    """
    l = len(msg)
    ll = (l - 1) << 2
    if key:
        m = msg[l - 1]
        if m < ll - 3 or m > ll:
            return
        ll = m
    for i in range(0, l):
        msg[i] = chr(msg[i] & 0xff) + chr(msg[i] >> 8 & 0xff) + chr(
            msg[i] >> 16 & 0xff) + chr(msg[i] >> 24 & 0xff)
    if key:
        return "".join(msg)[0:ll]
    return "".join(msg)

def get_xencode(msg, key):
    """
    对消息进行加密编码
    
    参数:
        msg (str): 要加密的消息
        key (str): 加密密钥
        
    返回:
        str: 加密后的字符串
    """
    if msg == "":
        return ""
        
    pwd = sencode(msg, True)
    pwdk = sencode(key, False)
    
    if len(pwdk) < 4:
        pwdk = pwdk + [0] * (4 - len(pwdk))
        
    n = len(pwd) - 1
    z = pwd[n]
    y = pwd[0]
    c = 0x86014019 | 0x183639A0
    m = 0
    e = 0
    p = 0
    q = math.floor(6 + 52 / (n + 1))
    d = 0
    
    while 0 < q:
        d = d + c & (0x8CE0D9BF | 0x731F2640)
        e = d >> 2 & 3
        p = 0
        
        while p < n:
            y = pwd[p + 1]
            m = z >> 5 ^ y << 2
            m = m + ((y >> 3 ^ z << 4) ^ (d ^ y))
            m = m + (pwdk[(p & 3) ^ e] ^ z)
            pwd[p] = pwd[p] + m & (0xEFB8D130 | 0x10472ECF)
            z = pwd[p]
            p = p + 1
            
        y = pwd[0]
        m = z >> 5 ^ y << 2
        m = m + ((y >> 3 ^ z << 4) ^ (d ^ y))
        m = m + (pwdk[(p & 3) ^ e] ^ z)
        pwd[n] = pwd[n] + m & (0xBB390742 | 0x44C6F8BD)
        z = pwd[n]
        q = q - 1
        
    return lencode(pwd, False)
