#!/usr/bin/env python
# coding: utf-8

# tk内置的会话框

from ttkbootstrap.dialogs import colorchooser
from ttkbootstrap.localization import MessageCatalog
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename, askopenfilenames
from tkinter import StringVar
from .Utils import rgba_str_2_hex
from .GUI_Link import Link

class ColorChooserDialogZH(colorchooser.ColorChooserDialog):
    # 重载：在中文系统里，OK被翻译为确定了，这回导致选色的值不输出到result
    def on_button_press(self, button):
        if button.cget('text') == MessageCatalog.translate('OK'):
            values = self.colorchooser.get_variables()
            self._result = colorchooser.ColorChoice(
                rgb=(values.r, values.g, values.b), 
                hsl=(values.h, values.s, values.l), 
                hex=values.hex
            )
            self._toplevel.destroy()            
        self._toplevel.destroy()

# 打开选色器，并把结果输出给 StringVar
def color_chooser(master,text_obj:StringVar,quote:bool=False)->str:
    initcolor = rgba_str_2_hex(text_obj.get())
    if initcolor:
        dialog_window = ColorChooserDialogZH(parent=master,title='选择颜色',initialcolor=initcolor)
    else:
        dialog_window = ColorChooserDialogZH(parent=master,title='选择颜色')
    # dialog_window = colorchooser.ColorChooserDialog(parent=master,title='选择颜色')
    dialog_window.show()
    color = dialog_window.result
    if color:
        # 选中的颜色
        R, G, B = color.rgb
        A = 255
        # 设置 StringVar
        if quote:
            text_obj.set("'({0},{1},{2},{3})'".format(int(R), int(G), int(B),int(A)))
        else:
            text_obj.set('({0},{1},{2},{3})'.format(int(R), int(G), int(B),int(A)))
        return (R,G,B,A)
    else:
        # text_obj.set("")
        return None

filetype_dic = {
    'logfile':      [('剧本文件',('*.rgl','*.txt')),('全部文件','*.*')],
    'chartab':      [('角色配置表',('*.tsv','*.csv','*.xlsx','*.txt')),('全部文件','*.*')],
    'mediadef':     [('媒体定义文件',('*.txt','*.py')),('全部文件','*.*')],
    'rgscripts':    [('全部文件','*.*'),('剧本文件',('*.rgl','*.txt')),('角色配置表',('*.tsv','*.csv','*.xlsx','*.txt')),('媒体定义文件',('*.txt','*.py'))],
    'picture':      [('图片文件',('*.png','*.jpg','*.jpeg','*.bmp')),('全部文件','*.*')],
    'soundeff':     [('音效文件','*.wav'),('全部文件','*.*')],
    'BGM':          [('背景音乐文件','*.ogg'),('全部文件','*.*')],
    'fontfile':     [('字体文件',('*.ttf','*.otf','*.ttc')),('全部文件','*.*')],
    'rplgenproj':   [('回声工程',('*.rgpj','*.json')),('全部文件','*.*')],
    'prefix':       [('全部文件','*.*')]
}
default_name = {
    'logfile':   ['新建剧本文件','.rgl'],
    'chartab':   ['新建角色表'  ,'.tsv'],
    'mediadef':  ['新建媒体库'  ,'.txt'],
    'rplgenproj':['新建工程'    ,'.rgpj'],
    'prefix':    ['导出文件'    ,'']
}
# 浏览多个文件，并把路径返回（不输出给stringvar）：
def browse_multi_file(master, filetype=None ,related:bool=True)->list:
    if filetype is None:
        getname:tuple = askopenfilenames(parent=master,)
    else:
        getname:tuple = askopenfilenames(parent=master,filetypes=filetype_dic[filetype])
    # 检查结果
    if getname == ['']:
        return None # 注意，如果没选择，返回None！
    else:
        if related:
            media_dir = Link['media_dir']
            out_path = []
            for path in getname:
                if path.startswith(media_dir):
                    out_path.append('@/' + getname[len(media_dir):])
                else:
                    out_path.append(path)
        else:
            out_path = list(getname)
        # 返回
        return out_path
# 浏览文件，并把路径输出给 StringVar
def browse_file(master, text_obj:StringVar, method='file', filetype=None, quote:bool=True, related:bool=True):
    if method == 'file':
        if filetype is None:
            getname = askopenfilename(parent=master,)
        else:
            getname = askopenfilename(parent=master,filetypes=filetype_dic[filetype])
    else:
        getname = askdirectory(parent=master)
    # 可用性检查
    # if (' ' in getname) | ('$' in getname) | ('(' in getname) | (')' in getname):
    #    messagebox.showwarning(title='警告', message='请勿使用包含空格、括号或特殊符号的路径！')
    #    text_obj.set('')
    #    return None
    if getname == '':
        return getname
    else:
        # 是否是媒体路径下的文件夹
        if related:
            try:
                media_dir = Link['media_dir']
                if getname.startswith(media_dir):
                    getname = '@/' + getname[len(media_dir):]
            except KeyError:
                pass
        # 是否加引号
        if quote:
            text_obj.set("'{}'".format(getname))
        else:
            text_obj.set(getname)
        # 返回
        # print(getname)
        return getname
    
def save_file(master, method='file', filetype=None, quote:bool=True)->str:
    if method == 'file':
        defaults = default_name[filetype]
        if filetype is None:
            getname = asksaveasfilename(parent=master,defaultextension=defaults[1],initialfile=defaults[0])
        else:
            getname = asksaveasfilename(parent=master,filetypes=filetype_dic[filetype],defaultextension=defaults[1],initialfile=defaults[0])
        return getname
    else:
        return ''