#!/usr/bin/env python
# coding: utf-8

# 将mp3格式的音频批量转化为wav格式
# 使用方法 :
# python mp3_2_wav.py ./*.mp3 #用通配符选定mp3文件！

import pydub
import glob
import sys

pydub.AudioSegment.ffmpeg = "../ffmpeg.exe"
# 读取参数
try:
    target = sys.argv[1]
except IndexError:
    print('Target files path is required!')
    sys.exit()
# 寻找文件
file_path = glob.glob(target)
print(file_path)
# 导出wav
for f in file_path:
    f = f.replace('\\','/')
    ifile = pydub.AudioSegment.from_mp3(f)
    ofile = f.replace('mp3','wav')
    ifile.export(ofile,format='wav')
    print(f,'done!')