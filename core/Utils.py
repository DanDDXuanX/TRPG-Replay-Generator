#!/usr/bin/env python
# coding: utf-8
# 小工具们
EDITION = 'alpha 1.24.0'

import numpy as np
import time
from .Regexs import RE_rich

# UF : 将2个向量组合成"(x,y)"的形式
concat_xy = np.frompyfunc(lambda x,y:'('+'%d'%x+','+'%d'%y+')',2,1)

# 截断字符串
def cut_str(str_,len_):
    return str_[0:int(len_)]
UF_cut_str = np.frompyfunc(cut_str,2,1)

# 清理ts文本中的标记符号
def clean_ts(text):
    # 用于语音合成的内容，不应该包括富标记
    return RE_rich.sub(text,'').replace('^','').replace('#','')

def isnumber(str):
    try:
        float(str)
        return True
    except Exception:
        return False
    
# hexcolor 转 rgb(a)
def hex_2_rgba(hex_string)->tuple:
    if len(hex_string) == 7:
        r = int(hex_string[1:3], 16)
        g = int(hex_string[3:5], 16)
        b = int(hex_string[5:7], 16)
        a = 255
    elif len(hex_string) == 9:
        r = int(hex_string[1:3], 16)
        g = int(hex_string[3:5], 16)
        b = int(hex_string[5:7], 16)
        a = int(hex_string[7:9], 16)
    else:
        r,g,b,a = 0,0,0,0
    return (r,g,b,a)

# 62进制时间戳*1000，ms单位
def mod62_timestamp():
    timestamp = int(time.time()*1000)
    outstring = ''
    while timestamp > 1:
        residual = timestamp%62
        mod = timestamp//62
        if residual<10:
            # 数值 48=0
            outstring = outstring + chr(48+residual)
        elif residual<36:
            # 大写 65=A
            outstring = outstring + chr(65+residual-10)
        else:
            # 小写 97=a
            outstring = outstring + chr(97+residual-36)
        timestamp = mod
    return outstring[::-1]