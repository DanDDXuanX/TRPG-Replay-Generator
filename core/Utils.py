#!/usr/bin/env python
# coding: utf-8
# 小工具们
EDITION = 'alpha 2.0.0'

import numpy as np
import pygame
import time
import re
import os
import subprocess
from .Regexs import RE_rich

# 文字处理
# UF : 将2个向量组合成"(x,y)"的形式
concat_xy = np.frompyfunc(lambda x,y:'('+'%d'%x+','+'%d'%y+')',2,1)
# 截断字符串
def cut_str(str_,len_):
    return str_[0:int(len_)]
UF_cut_str = np.frompyfunc(cut_str,2,1)
# 清理ts文本中的标记符号
def clean_ts(text):
    # 用于语音合成的内容，不应该包括富标记
    return RE_rich.sub('',text).replace('^','').replace('#','')
# 是否是数值
def isnumber(str):
    try:
        float(str)
        return True
    except Exception:
        return False    

# 图像处理
# 获取点在矩形对角线垂直投影方向的投影点相对矩形垂直对角线的倍率（scale）
def get_vppr(new_pos,master_size):
    V_AP = np.array(new_pos)
    V_AB = np.array(master_size)
    Z = np.dot(V_AP,V_AB)/np.dot(V_AB,V_AB)
    return Z
# 给surface应用一个蒙版
def mask(surface:pygame.Surface,mask:np.ndarray=None)->pygame.Surface:
    """
    应用一个蒙版
    输入参数：
        surface，pygame.Surface
            输入的图像
        mask，np.ndarray
            和surface尺寸相符的矩阵，数值类型是 np.uint8
    输出
        surface，pygame.Surface
    """
    # 渐变蒙版
    if mask is None:
        w, h = surface.get_size()
        mask = np.tile(np.linspace(0,256,w,dtype=np.uint8),(h,1)).T
    # 应用
    outsurface = surface.copy()
    pygame.surfarray.pixels_alpha(outsurface)[:] = np.multiply(
        pygame.surfarray.pixels_alpha(outsurface)[:], mask,
        dtype=np.uint16,
    ) // 255
    return outsurface
# 基于surface的alpha通道，生成剪影
def cutout(surface:pygame.Surface,color:tuple=None)->pygame.Surface:
    if color is None:
        color = (72,72,72)
    w, h = surface.get_size()
    outsurface = pygame.Surface((w,h), pygame.SRCALPHA)
    outsurface.fill(color=color)
    mask = pygame.surfarray.array_alpha(surface)
    pygame.surfarray.pixels_alpha(outsurface)[:] = mask
    return outsurface
# 向量顺时针旋转
def rotate_vector(vector, angle):
    # 将角度转为弧度
    angle_rad = np.radians(angle)
    # 构建旋转矩阵
    rotation_matrix = np.array([[np.cos(angle_rad), -np.sin(angle_rad)],
                                [np.sin(angle_rad), np.cos(angle_rad)]])
    # 计算向量和旋转矩阵的乘法
    rotated_vector = np.dot(rotation_matrix, vector)
    return rotated_vector
# 图形绕左上角顺时针旋转
def rotate_surface(surface, angle):
    # O:旋转的中心点
    # S:Surface的右上角
    # A:我们指定的旋转锚点，是图形的右上角
    # 原始的计算v_OA
    original_width, original_height = surface.get_size()
    v_OA = -np.array([original_width,original_height])/2
    # 旋转图形：抗锯齿
    rotated_surface = pygame.transform.rotozoom(surface, -angle, 1.0)
    # rotated_surface = pygame.transform.rotate(surface, -angle)
    # 计算 r_SO
    new_width, new_height = rotated_surface.get_size()
    r_SO = np.array([new_width,new_height])/2
    # 通过旋转v_OA，得到r_OA
    r_OA = rotate_vector(v_OA, angle=angle)
    # 计算r_SA，在blit的时候，应该在锚点A上减去r_SA，才是新Surface的位置
    r_SA = r_SO + r_OA
    return rotated_surface, r_SA
# 基本的缩放操作
def zoom_surface(surface,zoom):
    if zoom == 1:
        return surface
    else:
        w,h = surface.get_size()
        W = int(w*zoom)
        H = int(h*zoom)
        return pygame.transform.smoothscale(surface,size=(W,H))

# 颜色
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
# rgb(a)，转hexcolor
def rgb_2_hex(R:int,G:int,B:int):
    return f"#{R:02x}{G:02x}{B:02x}"
def rgba_str_2_hex(rgba_str:str)->str:
    # alpha will be ignore
    m = re.match(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(,\s*\d+\s*)?\)$", rgba_str)
    if m:
        R = int(m.group(1))
        G = int(m.group(2))
        B = int(m.group(3))
        return rgb_2_hex(R,G,B)
    else:
        return None

# 时间
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
# 从字符串提取合法文件名
def extract_valid_variable_name(string):
    # 将非字母数字字符替换为下划线
    valid_string = re.sub(r'\W+', '_', string)
    # 如果字符串以数字开头，则在开头添加下划线
    if valid_string[0].isdigit():
        valid_string = '_' + valid_string
    # 如果字符串是不可以使用的变量名，则在末尾添加下划线
    keywords = ['black','white']
    if valid_string in keywords:
        valid_string += '_'
    # 返回提取的合法变量名
    return valid_string

# 文件格式
def convert_audio(target_type:str,ifile:str,ofile:str):
    # ffmpeg
    if os.path.isfile('./ffmpeg.exe'):
        ffmpeg_exec = 'ffmpeg.exe'
    else:
        ffmpeg_exec = 'ffmpeg'
    # 目标格式
    if target_type == 'wav':
        target_format = target_type
        ffmpeg_cmd = [
            ffmpeg_exec,
            '-i',ifile,
            '-f',target_format,
            '-vn',
            '-y',
            ofile,
            '-loglevel','quiet'
        ]
    elif target_type == 'ogg':
        target_format = target_type
        ffmpeg_cmd = [
            ffmpeg_exec,
            '-i',ifile,
            '-f',target_format,
            '-vn',
            '-acodec','libvorbis',
            '-ab','128k',
            '-y',
            ofile,
            '-loglevel','quiet'
        ]
    else:
        return False, f"不支持的格式：{target_type}"
    # 执行
    try:
        subprocess.run(ffmpeg_cmd, check=True, shell=True)
        return True, ofile
    except subprocess.CalledProcessError as E:
        return False, str(E)