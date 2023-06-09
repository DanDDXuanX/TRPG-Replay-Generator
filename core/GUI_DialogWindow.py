#!/usr/bin/env python
# coding: utf-8

# 会话框

from ttkbootstrap.dialogs import colorchooser
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename
from tkinter import StringVar

# 打开选色器，并把结果输出给 StringVar
def color_chooser(master,text_obj:StringVar)->str:
    dialog_window = colorchooser.ColorChooserDialog(parent=master,title='选择颜色')
    dialog_window.show()
    if dialog_window.result.rgb:
        # 选中的颜色
        R, G, B = dialog_window.result.rgb
        A = 255
        # 设置 StringVar
        text_obj.set('({0},{1},{2},{3})'.format(int(R), int(G), int(B),int(A)))
        return (R,G,B,A)
    else:
        # text_obj.set("")
        return None

# 浏览文件，并把路径输出给 StringVar
def browse_file(master, text_obj:StringVar, method='file', filetype=None):
    filetype_dic = {
        'logfile':  [('log文件',('*.rgl','*.txt')),('全部文件','*.*')],
        'chartab':  [('角色配置表',('*.tsv','*.csv','*.xlsx','*.txt')),('全部文件','*.*')],
        'mediadef': [('媒体定义文件',('*.txt','*.py')),('全部文件','*.*')],
        'picture':  [('图片文件',('*.png','*.jpg','*.jpeg','*.bmp')),('全部文件','*.*')],
        'soundeff': [('音效文件','*.wav'),('全部文件','*.*')],
        'BGM':      [('背景音乐文件','*.ogg'),('全部文件','*.*')],
        'fontfile': [('字体文件',('*.ttf','*.otf','*.ttc')),('全部文件','*.*')],
        # 'timeline': [('回声时间轴','.timeline'),('全部文件','*.*')]
    }
    if method == 'file':
        if filetype is None:
            getname = askopenfilename()
        else:
            getname = askopenfilename(filetypes=filetype_dic[filetype])
    else:
        getname = askdirectory()
    # 可用性检查
    # if (' ' in getname) | ('$' in getname) | ('(' in getname) | (')' in getname):
    #    messagebox.showwarning(title='警告', message='请勿使用包含空格、括号或特殊符号的路径！')
    #    text_obj.set('')
    #    return None
    if getname == '':
        return getname
    else:
        text_obj.set("'{}'".format(getname))
        return getname
