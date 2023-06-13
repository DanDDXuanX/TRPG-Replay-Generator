#!/usr/bin/env python
# coding: utf-8

# 会话框

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import colorchooser
from ttkbootstrap.localization import MessageCatalog
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename
from tkinter import StringVar
from .Utils import rgba_str_2_hex
from .TTSengines import Aliyun_TTS_engine, Azure_TTS_engine, Beats_engine, voice_lib

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

class VoiceArgs(ttk.Frame):
    voice_lib = voice_lib
    def __init__(self,master,screenzoom,service:str,voice:str='',speech_rate:int=0,pitch_rate:int=0):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0)
        SZ_10 = int(10 * self.sz)
        SZ_5 = int(5*self.sz)
        # variables
        self.voice = tk.StringVar(master=self,value=voice)
        self.speechrate = tk.IntVar(master=self,value=speech_rate)
        self.pitchrate = tk.IntVar(master=self,value=pitch_rate)
        self.voice_description = self.get_voice_description()
        # labels
        self.labels = {
            'voice'         : ttk.Label(master=self,text='音源名：',width=8),
            'speechrate'    : ttk.Label(master=self,text='语速：',width=8),
            'pitchrate'     : ttk.Label(master=self,text='语调：',width=8)
        }
        # input
        self.inputs = {
            'voice'         : ttk.Combobox(master=self,textvariable=self.voice,values=list(self.voice_lib[self.voice_lib.service==service].index)),
            'speechrate'    : ttk.Spinbox(master=self,textvariable=self.speechrate, width=8, from_=-500,to=500,increment=10),
            'pitchrate'     : ttk.Spinbox(master=self,textvariable=self.pitchrate, width=8, from_=-500,to=500,increment=10)
        }
        # addition
        self.addition = {
            'voice'         : ttk.Label(self.master,text=self.voice_description),
            'speechrate'    : ttk.Scale(self.master,from_=-500,to=500,variable=self.speechrate,command=lambda:self.get_scale_to_intvar(self.speechrate)),
            'pitchrate'     : ttk.Scale(self.master,from_=-500,to=500,variable=self.pitchrate,command=lambda:self.get_scale_to_intvar(self.pitchrate)),
        }
    def get_voice_description(self)->str:
        try:
            return self.voice_lib.loc[self.voice.get(),'description']
        except:
            return '无'
    def update_selected_voice(self,event):
        pass
    def get_scale_to_intvar(self,variable):
        variable.set(int(variable.get()))
class VoiceChooser(ttk.Frame):
    def __init__(self,master,screenzoom,voice:str,speech_rate:int,pitch_rate:int):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0)
        SZ_10 = int(10 * self.sz)
        SZ_5 = int(5*self.sz)
        # 解析输入
        if '::' in voice:
            service,speaker = voice.split('::')
        else:
            service = "Aliyun"
            speaker = voice
        # Azure解析
        if ':' in speaker:
            speaker,style,degree,roleplay = speaker.split(':')
            degree = float(degree)
        # 建立元件
        self.title = ttk.Label(master=self,text='选择音源',font='-family 微软雅黑 -size 15 -weight bold')
        self.argument_notebook = ttk.Notebook(master=self,bootstyle="primary")
        self.args_frame = {
            'Aliyun'    :ttk.Frame(master=self.argument_notebook),
            'Azure'     :ttk.Frame(master=self.argument_notebook),
            'Beats'     :ttk.Frame(master=self.argument_notebook),
        }
        self.init_Aliyun_frame()
        self.init_Azure_frame()
        self.init_Beats_frame()
        for keyword in self.args_frame:
            self.argument_notebook.add(self.args_frame[keyword],text='{}'.format(keyword))
        # 测试文本
        self.preview_frame = ttk.LabelFrame(master=self, text='测试文本',padding=(SZ_10,SZ_5,SZ_10,SZ_10))
        self.preview_text = ttk.Text(master=self.preview_frame,font='-family 微软雅黑 -size 12')
        self.preview_text.pack(fill='both',expand=True)
        # 按钮
        self.button_frame = ttk.Frame(master=self)
        self.buttons = {
            'confirm' : ttk.Button(master=self.button_frame,bootstyle='primary',text='确定'),
            'preview' : ttk.Button(master=self.button_frame,bootstyle='primary',text='试听'),
            'save'    : ttk.Button(master=self.button_frame,bootstyle='primary',text='保存'),
            'copy'    : ttk.Button(master=self.button_frame,bootstyle='primary',text='复制'),
        }
        for keyword in self.buttons:
            self.buttons[keyword].pack(side='left',fill='x',expand=True,padx=SZ_10,ipady=SZ_5)
        self.update_items()
    def update_items(self):
        SZ_10 = int(10 * self.sz)
        SZ_5 = int(5*self.sz)
        self.title.pack(side='top',fill='x',padx=SZ_10,pady=[SZ_10,SZ_5])
        self.argument_notebook.pack(side='top',fill='x',padx=SZ_10,pady=SZ_5)
        self.preview_frame.pack(side='top',fill='both',expand=True,padx=SZ_10,pady=SZ_5)
        self.button_frame.pack(side='top',fill='x',padx=SZ_10,pady=[SZ_5,SZ_10])
    def init_Aliyun_frame(self):
        this_frame = self.args_frame['Aliyun']
    def init_Azure_frame(self):
        this_frame = self.args_frame['Azure']
    def init_Beats_frame(self):
        this_frame = self.args_frame['Beats']

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