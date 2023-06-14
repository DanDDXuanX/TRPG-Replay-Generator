#!/usr/bin/env python
# coding: utf-8

# 会话框

import pandas as pd
from ttkbootstrap.dialogs import colorchooser
from ttkbootstrap.localization import MessageCatalog
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename
from tkinter import StringVar, IntVar
from .Utils import rgba_str_2_hex
from .GUI_VoiceChooser import VoiceChooserDialog
from .GUI_Relocate import RelocateDialog
from .ScriptParser import MediaDef

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
def color_chooser(master,text_obj:StringVar)->str:
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
        text_obj.set('({0},{1},{2},{3})'.format(int(R), int(G), int(B),int(A)))
        return (R,G,B,A)
    else:
        # text_obj.set("")
        return None
    
# 打开语音选择器，并把结果输出给 StringVar
def voice_chooser(master,voice_obj:StringVar,speech_obj:IntVar,pitch_obj:IntVar):
    init_voice = voice_obj.get()
    init_speech = speech_obj.get()
    init_pitch = pitch_obj.get()
    dialog_window = VoiceChooserDialog(
        parent=master,
        screenzoom=master.sz,
        title='选择语音音源',
        voice=init_voice,
        speechrate=init_speech,
        pitchrate=init_pitch
        )
    dialog_window.show()
    # 获取结果
    result_args = dialog_window.result
    if result_args:
        voice_obj.set(result_args['voice'])
        speech_obj.set(result_args['speechrate'])
        pitch_obj.set(result_args['pitchrate'])
        return result_args
    else:
        return None

# 打开重定位文件，并获取一个包含了前后文件路径的表格
def relocate_file(master, file_not_found:dict, mediadef:MediaDef):
    dialog_window = RelocateDialog(
        parent=master,
        screenzoom=master.sz,
        title = '重新定位媒体',
        file_not_found=file_not_found,
    )
    dialog_window.show()
    # 获取结果
    result_args:pd.DataFrame = dialog_window.result
    if result_args is not None:
        for key,value in result_args.iterrows():
            # 检查是否需要替换：空白和脱机则不需要替换
            if value['relocate_path'] in ['None', '脱机']:
                continue
            else:
                # 变更媒体定义文件
                mediadef.update_media_file(
                    name     = value['media_name'],
                    old_path = value['invalid_path'],
                    new_path = value['relocate_path']
                    )
        return result_args
    else:
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
# 浏览文件，并把路径输出给 StringVar
def browse_file(master, text_obj:StringVar, method='file', filetype=None):
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
        text_obj.set("'{}'".format(getname))
        return getname
    
def save_file(master, method='file', filetype=None)->str:
    if method == 'file':
        defaults = default_name[filetype]
        if filetype is None:
            getname = asksaveasfilename(parent=master,defaultextension=defaults[1],initialfile=defaults[0])
        else:
            getname = asksaveasfilename(parent=master,filetypes=filetype_dic[filetype],defaultextension=defaults[1],initialfile=defaults[0])
        return getname
    else:
        return ''