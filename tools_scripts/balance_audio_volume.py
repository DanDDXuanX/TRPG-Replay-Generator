#!/usr/bin/env python
# coding: utf-8

# 用于平衡不同来源音源的音量
# 使用：python balance_audio_volume.py [输入路径] [输出路径]
# 要求要在存在ffmpeg的路径下运行

import pandas as pd
import numpy as np
import pydub
import glob
import re
import sys
from matplotlib import pyplot as plt

ipath = sys.argv[1].replace('\\','/')
opath = sys.argv[2].replace('\\','/')

# 获取均衡前平均音量信息
filelist = list(map(lambda x:x.replace('\\','/'),glob.glob(ipath+'/*.wav')))
stats = pd.DataFrame(index=filelist,columns=['dBFS','max_dBFS'])
for file in filelist:
    au_this = pydub.AudioSegment.from_file(file)
    stats.loc[file] = {
        'dBFS':au_this.dBFS,
        'max_dBFS':au_this.max_dBFS,
    }

stats['file_index'] = stats.index.map(lambda x:re.findall('.+auto_AU_(\d+)\.wav',x)[0])
stats['1'] = 1

# 绘图分析dBFS和dBFS_max的关系（均衡前）
plt.style.use('ggplot')
fig = plt.figure(figsize=(12,6))
ax1 = plt.subplot(121)
ax1.scatter(x=stats['dBFS'],
            y=stats['max_dBFS'],
            c=stats['file_index'].astype(int))
k,inter = np.linalg.lstsq(stats[['dBFS','1']].astype(np.float64).values,
                          stats['max_dBFS'].astype(np.float64).values,
                          rcond=None)[0]
x_range = np.array([stats['dBFS'].min(),stats['dBFS'].max()])
ax1.plot(x_range,x_range*k+inter,'--')
ax1.set_title('Before Balance')
ax1.set_xlabel('dBFS')
ax1.set_ylabel('max_dBFS')
xlim = ax1.get_xlim()
ylim = ax1.get_ylim()

# 导出
dbFS_mean = stats.dBFS.mean()
for file in filelist:
    au_this = pydub.AudioSegment.from_file(file)
    Gain = dbFS_mean - au_this.dBFS
    outau = au_this+Gain
    #print(opath+'/'+file.split('/')[-1])
    outau.export(opath+'/'+file.split('/')[-1])

# 获取均衡后平均音量信息
filelist = list(map(lambda x:x.replace('\\','/'),glob.glob(opath+'/*.wav')))
stats = pd.DataFrame(index=filelist,columns=['dBFS','max_dBFS'])
for file in filelist:
    au_this = pydub.AudioSegment.from_file(file)
    stats.loc[file] = {
        'dBFS':au_this.dBFS,
        'max_dBFS':au_this.max_dBFS,
    }

stats['file_index'] = stats.index.map(lambda x:re.findall('.+auto_AU_(\d+)\.wav',x)[0])
stats['1'] = 1

# 绘图分析dBFS和dBFS_max的关系（均衡后）
ax2 = plt.subplot(122)
ax2.scatter(x=stats['dBFS'],
            y=stats['max_dBFS'],
            c=stats['file_index'].astype(int))
k,inter = np.linalg.lstsq(stats[['dBFS','1']].astype(np.float64).values,
                          stats['max_dBFS'].astype(np.float64).values,
                          rcond=None)[0]
x_range = np.array([stats['dBFS'].min(),stats['dBFS'].max()])
ax2.set_xlim(xlim)
ax2.set_ylim(ylim)
ax2.plot(x_range,x_range*k+inter,'--')
ax2.set_title('After Balance')
ax2.set_xlabel('dBFS')
ax2.set_ylabel('max_dBFS')

fig.savefig(opath+'/stats.png',format='png',dpi=200)
print('done!')