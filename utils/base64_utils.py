"""
Base64编码工具
提供兼容深澜认证系统的Base64编码实现
"""

_PADCHAR = "="
_ALPHA = "LVoJPiCN2R8G90yg+hmFHuacZ1OWMnrsSTXkYpUq/3dlbfKwv6xztjI7DeBE45QA"

def _getbyte(s, i):
    """
    获取字符串指定位置的字符ASCII码
    
    参数:
        s (str): 输入字符串
        i (int): 索引位置
        
    返回:
        int: 字符的ASCII码
    """
    if len(s) > i:
        return ord(s[i])
    return 0

def get_base64(s):
    """
    自定义Base64编码实现
    
    参数:
        s (str): 要编码的字符串
        
    返回:
        str: Base64编码后的字符串
    """
    if not s:
        return ""
    
    x = []
    imax = len(s) - len(s) % 3
    
    if len(s) == 0:
        return s
    
    for i in range(0, imax, 3):
        b10 = (_getbyte(s, i) << 16) | (_getbyte(s, i + 1) << 8) | _getbyte(s, i + 2)
        x.append(_ALPHA[(b10 >> 18)])
        x.append(_ALPHA[((b10 >> 12) & 63)])
        x.append(_ALPHA[((b10 >> 6) & 63)])
        x.append(_ALPHA[(b10 & 63)])
    
    i = imax
    
    if len(s) - imax == 1:
        b10 = _getbyte(s, i) << 16
        x.append(_ALPHA[(b10 >> 18)])
        x.append(_ALPHA[((b10 >> 12) & 63)])
        x.append(_PADCHAR)
        x.append(_PADCHAR)
    elif len(s) - imax == 2:
        b10 = (_getbyte(s, i) << 16) | (_getbyte(s, i + 1) << 8)
        x.append(_ALPHA[(b10 >> 18)])
        x.append(_ALPHA[((b10 >> 12) & 63)])
        x.append(_ALPHA[((b10 >> 6) & 63)])
        x.append(_PADCHAR)
    
    return "".join(x)
