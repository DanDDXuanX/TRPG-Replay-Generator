#!/usr/bin/env python
# coding: utf-8

# 在 模板（xlsx） 里面编辑好之后，导出同名的log文件
# 使用方法:
# python excel_2_log.py StdinLog_tplt.xlsx

import pandas as pd
import sys
# 模板
template_basic = "[{name_subtype}]:{speech_text}"
# 输入文件路径
try:
    ifile = sys.argv[1]
except IndexError:
    print('Input file files path is required!')
    sys.exit()
# 输出文件路径
ofile = ifile.split('.')
ofile[-1] = 'txt'
ofile = '.'.join(ofile)
# 输出文件对象
out_file = open(ofile,'w',encoding='utf-8')
# 载入excel表
MainDF = pd.read_excel(ifile,sheet_name='极简模式',dtype=str)
MainDF = MainDF.set_index('序号')
# 开始处理
for key,values in MainDF.iterrows():
    try:
        name = values['发言人']
        subtype = values['差分']
        voice = values['音频']
        asterisk = values['星标']
        text = values['发言文本']
        # 如果没有差分立绘，就只保留一个名称
        if (subtype=='NA') or (subtype!=subtype) or (subtype=='default'):
            pass
        else:
            name = name+'.'+subtype
        # 如果文本中有换行符，则处理为'#'
        if '\n' in text:
            text = '^'+text
            text = text.replace('\n','#').replace('\r','')
        # 如果文本中有制表符，则处理为2个全角空格
        if '\t' in text:
            text = text.replace('\t','　　')
        # 格式化文本
        line_this = template_basic.format(name_subtype=name,speech_text=text)
        # 如果有星标，则加上星标
        if (asterisk=='*') or (asterisk=='True') or (asterisk==True):
            if (voice=='NA') or (voice!=voice):
                voice = '*'
            else:
                voice=voice+';'+'*'
        # 如果这时voice还是空的，就不加上{}部分了
        if (voice=='NA') or (voice!=voice):
            pass
        else:
            line_this=line_this+'{'+voice+'}'
        # 输出文件
        out_file.write(line_this+'\n')
    except Exception as E:
        print('Converting Error in line',key,',due to:',E)
# 处理完毕，导出文件
out_file.close()