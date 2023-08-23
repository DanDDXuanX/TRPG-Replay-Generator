#!/usr/bin/env python
# coding: utf-8

# 语音合成音源的浏览框体

import pandas as pd
from shutil import copy
import tkinter as tk
import threading
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox, Dialog
from tkinter.filedialog import asksaveasfilename
from .TTSengines import Aliyun_TTS_engine, Azure_TTS_engine, Beats_engine
from .TTSengines import System_TTS_engine, Tencent_TTS_engine, voice_lib
from .Exceptions import WarningPrint
from .ProjConfig import home_dir
from .Medias import Audio
from .Utils import mod62_timestamp
from .GUI_Util import DictCombobox
from .GUI_Link import Link
# 语音参数
class VoiceArgs(ttk.Frame):
    def __init__(self,master,screenzoom,service:str,voice:str='',speech_rate:int=0,pitch_rate:int=0):
        # 缩放尺度
        self.sz = screenzoom
        SZ_5 = int(self.sz *5)
        super().__init__(master,borderwidth=SZ_5)
        # variables
        self.service = service
        self.voice_description = '无'
        self.voice_lib = voice_lib[voice_lib.service==self.service]
        self.TTS = Aliyun_TTS_engine
        # 载入输入参数
        self.variables = {}
        self.load_input_args(voice=voice,speech_rate=speech_rate,pitch_rate=pitch_rate)
        # labels
        self.frames = {
            'voice'         : ttk.Frame(master=self),
            'speechrate'    : ttk.Frame(master=self),
            'pitchrate'     : ttk.Frame(master=self),
        }
        self.labels = {
            'voice'         : ttk.Label(master=self.frames['voice'],text='音源名：',width=6),
            'speechrate'    : ttk.Label(master=self.frames['speechrate'],text='语速：',width=6),
            'pitchrate'     : ttk.Label(master=self.frames['pitchrate'],text='语调：',width=6)
        }
        # input
        self.inputs = {
            'voice'         : DictCombobox(master=self.frames['voice'],textvariable=self.variables['voice']),
            'speechrate'    : ttk.Scale(self.frames['speechrate'],from_=-500,to=500,variable=self.variables['speechrate'],command=lambda _:self.get_scale_to_intvar(self.variables['speechrate'])),
            'pitchrate'     : ttk.Scale(self.frames['pitchrate'],from_=-500,to=500,variable=self.variables['pitchrate'],command=lambda _:self.get_scale_to_intvar(self.variables['pitchrate'])),
        }
        self.inputs['voice'].update_dict(pd.Series(self.voice_lib.index, index=self.voice_lib['description']).to_dict())
        self.inputs['voice'].bind("<<ComboboxSelected>>",self.update_selected_voice,'+')
        # addition
        self.addition = {
            'voice'         : ttk.Label(self.frames['voice'],text=self.voice_description, width=18),
            'speechrate'    : ttk.Spinbox(master=self.frames['speechrate'],textvariable=self.variables['speechrate'], width=8, from_=-500,to=500,increment=10),
            'pitchrate'     : ttk.Spinbox(master=self.frames['pitchrate'],textvariable=self.variables['pitchrate'], width=8, from_=-500,to=500,increment=10)
        }
        self.display_order = ['voice','speechrate','pitchrate']
    def update_elements(self):
        SZ_5 = int(self.sz * 5)
        for keyword in self.display_order:
            self.labels[keyword].pack(fill='none',side='left',padx=SZ_5)
            self.inputs[keyword].pack(fill='x',side='left',padx=SZ_5,expand=True)
            # 不一定有的
            if self.addition[keyword] is not None:
                self.addition[keyword].pack(fill='none',side='left',padx=SZ_5)
    def update_items(self):
        SZ_5 = int(self.sz * 5)
        for keyword in self.display_order:
            if keyword in self.frames:
                self.frames[keyword].pack(fill='x',side='top',pady=SZ_5)
    def load_input_args(self,voice,speech_rate,pitch_rate):
        # 载入输入参数
        if voice in self.voice_lib.index:
            self.variables['voice'] = tk.StringVar(master=self, value=voice)
            self.variables['speechrate'] = tk.IntVar(master=self, value=speech_rate)
            self.variables['pitchrate'] = tk.IntVar(master=self, value=pitch_rate)
        else:
            self.variables['voice'] = tk.StringVar(master=self, value='')
            self.variables['speechrate'] = tk.IntVar(master=self, value=0)
            self.variables['pitchrate'] = tk.IntVar(master=self, value=0)
    def get_voice_info(self,colname='description')->str:
        if colname == 'voice':
            return self.variables['voice'].get()
        try:
            return self.voice_lib.loc[self.variables['voice'].get(),colname]
        except Exception:
            return {'description':'无','style':'general','role':'Default'}[colname]
    def update_selected_voice(self,event):
        # 更新介绍label
        self.addition['voice'].configure(text=self.get_voice_info('voice'))
    def get_scale_to_intvar(self,variable):
        variable.set(int(variable.get()))
    def get_args(self) -> dict:
        return {
            'voice' : self.variables['voice'].get(),
            'speechrate' :self.variables['speechrate'].get(),
            'pitchrate' :self.variables['pitchrate'].get(),
        }
    def exec_synthesis(self,text:str):
        # 载入音源名
        try:
            args = self.get_args()
        except ValueError as E:
            return False, str(E)
        if args['voice'] == '':
            return False, '缺少音源名！'
        elif '::' in args['voice']:
            TTS_voice = args['voice'].split('::')[1]
        else:
            TTS_voice = args['voice']
        # 新建语音合成对象
        this_TTS = self.TTS(
            name = 'preview',
            voice = TTS_voice,
            speech_rate = args['speechrate'],
            pitch_rate = args['pitchrate'],
            aformat = 'wav'
        )
        # 执行合成
        try:
            temp_path = str(home_dir / '.rplgen' / 'preview_tempfile.wav').replace('\\','/')
            this_TTS.start(text=text, ofile=temp_path)
            return True, temp_path
        except Exception as E:
            print(WarningPrint('PrevFail',E))
            return False, '语音合成失败！检视控制台获取详细信息。'
class AliyunVoiceArgs(VoiceArgs):
    def __init__(self, master, screenzoom, voice: str = '', speech_rate: int = 0, pitch_rate: int = 0):
        # 继承
        super().__init__(master, screenzoom, service='Aliyun', voice=voice, speech_rate=speech_rate, pitch_rate=pitch_rate)
        self.TTS = Aliyun_TTS_engine
        # 放置元件
        self.update_selected_voice(None)
        self.update_elements()
        self.update_items()
    def get_args(self) -> dict:
        if self.variables['voice'].get() in self.voice_lib.index:
            return super().get_args()
        elif self.variables['voice'].get() == '':
            raise ValueError('必须选择一个音源！')
        else:
            raise ValueError('音源名是无效的！')
class BeatsVoiceArgs(VoiceArgs):
    def __init__(self, master, screenzoom, voice: str = '', speech_rate: int = 0, pitch_rate: int = 0):
        # 继承
        super().__init__(master, screenzoom, service='Beats', voice=voice, speech_rate=0, pitch_rate=0)
        self.TTS = Beats_engine
        # 禁用语速语调
        for keyword in ['speechrate','pitchrate']:
            self.inputs[keyword].configure(state='disable')
            self.addition[keyword].configure(state='disable')
        # 放置元件
        self.update_selected_voice(None)
        self.update_elements()
        self.update_items()
    def load_input_args(self, voice, speech_rate, pitch_rate):
        super().load_input_args(voice, speech_rate, pitch_rate)
        # 强制归零语速和语调
        self.variables['speechrate'].set(0)
        self.variables['pitchrate'].set(0)
    def get_args(self) -> dict:
        if self.variables['voice'].get() in self.voice_lib.index:
            args = super().get_args()
            args['voice'] = 'Beats::' + args['voice']
            return args
        elif self.variables['voice'].get() == '':
            raise ValueError('必须选择一个音源！')
        else:
            raise ValueError('音源名是无效的！')
    def exec_synthesis(self,text:str):
        # 载入音源名
        try:
            args = self.get_args()
        except ValueError as E:
            return False, str(E)
        if args['voice'] == '':
            return False, '缺少音源名！'
        elif '::' in args['voice']:
            TTS_voice = args['voice'].split('::')[1]
        else:
            TTS_voice = args['voice']
        # 新建语音合成对象：默认帧率=30，<w2w=2>
        this_TTS = self.TTS(
            name = 'preview',
            voice = TTS_voice,
            frame_rate = 30,
            aformat = 'wav'
        )
        this_TTS.tx_method_specify(tx_method={"method":"w2w","method_dur":3})
        # 执行合成
        try:
            temp_path = str(home_dir / '.rplgen' / 'preview_tempfile.wav').replace('\\','/')
            this_TTS.start(text=text, ofile=temp_path)
            return True, temp_path
        except Exception as E:
            print(WarningPrint('PrevFail',E))
            return False, '语音合成失败！检视控制台获取详细信息。'
class AzureVoiceArgs(VoiceArgs):
    def __init__(self, master, screenzoom, voice: str = '', speech_rate: int = 0, pitch_rate: int = 0):
        # 继承
        super().__init__(master, screenzoom, service='Azure', voice=voice, speech_rate=speech_rate, pitch_rate=pitch_rate)
        self.TTS = Azure_TTS_engine
        # 添加额外
        # frames
        self.frames['style'] = ttk.Frame(master=self)
        self.frames['roleplay'] = ttk.Frame(master=self)
        # labels
        self.labels['style'] = ttk.Label(master=self.frames['style'], text='风格：',width=6)
        self.labels['degree'] = ttk.Label(master=self.frames['style'], text='强度：',width=6)
        self.labels['roleplay'] = ttk.Label(master=self.frames['roleplay'], text='扮演：',width=6)
        # input
        self.inputs['style'] = ttk.Combobox(master=self.frames['style'],textvariable=self.variables['style'])
        self.inputs['degree'] = ttk.Spinbox(master=self.frames['style'], textvariable=self.variables['degree'], width=8, from_=0.1,to=2.0,increment=0.1)
        self.inputs['roleplay'] = ttk.Combobox(master=self.frames['roleplay'],textvariable=self.variables['roleplay'])
        # add
        self.addition['style'] = None # 空占位
        self.addition['degree'] = None # 空占位
        self.addition['roleplay'] = ttk.Label(master=self.frames['roleplay'], text='',width=18)
        # order
        self.display_order = ['voice','style','degree','roleplay','speechrate','pitchrate']
        # 放置元件
        self.update_voice_style()
        self.update_elements()
        self.update_items()
    def update_elements(self):
        super().update_elements()
        # degree的spinebox不需要扩展，保持宽度8
        self.inputs['degree'].pack_configure(expand=False)
    def update_selected_voice(self, event):
        super().update_selected_voice(event)
        # 复原风格参数
        self.variables['style'].set('general')
        self.variables['degree'].set(1.0)
        self.variables['roleplay'].set('Default')
        # 刷新可选值
        self.update_voice_style()
    def update_voice_style(self):
        this_style:list = self.get_voice_info(colname='style').split(',')
        this_role:list = self.get_voice_info(colname='role').split(',')
        self.inputs['style'].configure(values=this_style)
        self.inputs['roleplay'].configure(values=this_role)
    def load_input_args(self, voice, speech_rate, pitch_rate):
        # Azure解析
        if ':' in voice:
            speaker,style,degree,roleplay = voice.split(':')
            degree = float(degree)
        else:
            speaker = voice
            style = 'general'
            degree = 1.0
            roleplay = 'Default'
        # variable
        self.variables['style'] = tk.StringVar(master=self,value=style)
        self.variables['degree'] = tk.DoubleVar(master=self,value=degree)
        self.variables['roleplay'] = tk.StringVar(master=self,value=roleplay)
        # 继承（voice,speech,pitch）
        super().load_input_args(speaker, speech_rate, pitch_rate)
    def get_args(self) -> dict:
        if self.variables['voice'].get() == '':
            raise ValueError('必须选择一个音源！')
        args = super().get_args()
        style = self.variables['style'].get()
        degree = str(self.variables['degree'].get())
        roleplay = self.variables['roleplay'].get()
        args['voice'] = 'Azure::' + ':'.join([args['voice'], style, degree, roleplay])
        return args
class SystemVoiceArgs(VoiceArgs):
    def __init__(self, master, screenzoom, voice: str = '', speech_rate: int = 0, pitch_rate: int = 0):
        # 继承
        self.update_voice_lib()
        super().__init__(master, screenzoom, service='System', voice=voice, speech_rate=0, pitch_rate=0)
        self.TTS = System_TTS_engine
        # 禁用语调
        self.inputs['pitchrate'].configure(state='disable')
        self.addition['pitchrate'].configure(state='disable')
        # 放置元件
        self.update_selected_voice(None)
        self.update_elements()
        self.update_items()
    # 重设列表
    def update_voice_lib(self):
        global voice_lib
        # 如果已经有了，就什么都不做
        if 'System' in voice_lib['service'].values:
            return
        list_of_voice = System_TTS_engine().get_available().keys()
        L = len(list_of_voice)
        df_of_voice = pd.DataFrame(columns=voice_lib.columns,index = range(L))
        # 设置值
        df_of_voice['service'] = 'System'
        df_of_voice['Voice'] = list_of_voice
        df_of_voice['description'] = list_of_voice
        df_of_voice['avaliable_volume'] = 100
        df_of_voice['style'] = 'general'
        df_of_voice['role'] = 'Default'
        df_of_voice = df_of_voice.set_index('Voice')
        # 延长表
        voice_lib = pd.concat([voice_lib, df_of_voice],axis=0)
    def load_input_args(self, voice, speech_rate, pitch_rate):
        super().load_input_args(voice, speech_rate, pitch_rate)
        # 强制归零语调
        self.variables['pitchrate'].set(0)
    def get_args(self) -> dict:
        if self.variables['voice'].get() in self.voice_lib.index:
            args = super().get_args()
            args['voice'] = 'System::' + args['voice']
            return args
        elif self.variables['voice'].get() == '':
            raise ValueError('必须选择一个音源！')
        else:
            raise ValueError('音源名是无效的！')
class TencentVoiceArgs(VoiceArgs):
    def __init__(self, master, screenzoom, voice: str = '', speech_rate: int = 0, pitch_rate: int = 0):
        # 继承
        super().__init__(master, screenzoom, service='Tencent', voice=voice, speech_rate=0, pitch_rate=0)
        self.TTS = Tencent_TTS_engine
        # 禁用语调
        self.inputs['pitchrate'].configure(state='disable')
        self.addition['pitchrate'].configure(state='disable')
        # 放置元件
        self.update_selected_voice(None)
        self.update_elements()
        self.update_items()
    def load_input_args(self, voice, speech_rate, pitch_rate):
        super().load_input_args(voice, speech_rate, pitch_rate)
        # 强制归零语调
        self.variables['pitchrate'].set(0)
    def get_args(self) -> dict:
        if self.variables['voice'].get() in self.voice_lib.index:
            args = super().get_args()
            args['voice'] = 'Tencent::' + args['voice']
            return args
        elif self.variables['voice'].get() == '':
            raise ValueError('必须选择一个音源！')
        else:
            raise ValueError('音源名是无效的！')
# 语音选择
class VoiceChooser(ttk.Frame):
    def __init__(self,master,screenzoom,voice:str,speech_rate:int,pitch_rate:int,close_func):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0)
        SZ_10 = int(10 * self.sz)
        SZ_5 = int(5*self.sz)
        # 关闭窗口命令
        self.close_func = close_func
        # 多线程
        self.running_thread = None
        # 解析输入
        if '::' in voice:
            service,speaker = voice.split('::')
            if service not in ['Aliyun','Azure','Beats','System','Tencent']:
                service = 'Aliyun'
        else:
            service = "Aliyun"
            speaker = voice
        # 建立元件
        self.title = ttk.Label(master=self,text='选择音源',font=(Link['system_font_family'], 15, "bold"))
        self.argument_notebook = ttk.Notebook(master=self,bootstyle="primary")
        self.args_frame = {
            'Aliyun'    : AliyunVoiceArgs(master=self.argument_notebook,screenzoom=self.sz,voice=speaker,speech_rate=speech_rate,pitch_rate=pitch_rate),
            'Azure'     : AzureVoiceArgs(master=self.argument_notebook,screenzoom=self.sz,voice=speaker,speech_rate=speech_rate,pitch_rate=pitch_rate),
            'Tencent'   : TencentVoiceArgs(master=self.argument_notebook,screenzoom=self.sz,voice=speaker,speech_rate=speech_rate,pitch_rate=pitch_rate),
            'Beats'     : BeatsVoiceArgs(master=self.argument_notebook,screenzoom=self.sz,voice=speaker,speech_rate=speech_rate,pitch_rate=pitch_rate),
            'System'    : SystemVoiceArgs(master=self.argument_notebook,screenzoom=self.sz,voice=speaker,speech_rate=speech_rate,pitch_rate=pitch_rate),
        }
        self.service_name = {
            'Aliyun'    : '阿里云',
            'Azure'     : '微软Azure',
            'Tencent'   : '腾讯云',
            'Beats'     : '节奏音',
            'System'    : '系统',
        }
        for keyword in self.args_frame:
            self.argument_notebook.add(self.args_frame[keyword],text='{}'.format(self.service_name[keyword]))
        # 切换初始化选择的标签
        self.argument_notebook.select(self.args_frame[service])
        # 测试文本
        self.preview_frame = ttk.LabelFrame(master=self, text='测试文本',padding=(SZ_10,SZ_5,SZ_10,SZ_10))
        self.preview_text = ttk.Text(master=self.preview_frame,font=(Link['system_font_family'], 12),height=5,width=20)
        self.preview_text.insert("end",'在这里输入你想要合成的文本！')
        self.preview_text.pack(fill='both',expand=True)
        # 按钮
        self.button_frame = ttk.Frame(master=self)
        self.buttons = {
            'confirm' : ttk.Button(master=self.button_frame,bootstyle='primary',text='确定',command=self.comfirm),
            'preview' : ttk.Button(master=self.button_frame,bootstyle='primary',text='试听',command=self.preview),
            'save'    : ttk.Button(master=self.button_frame,bootstyle='primary',text='保存',command=self.savefile),
            'copy'    : ttk.Button(master=self.button_frame,bootstyle='primary',text='复制',command=self.copy_args),
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
    def get_select_args(self)->VoiceArgs:
        # 当前选中的标签页的名字
        service_name:str = self.argument_notebook.tab(self.argument_notebook.select(), "text")
        service = {value:key for key,value in self.service_name.items()}[service_name]
        # 获取参数
        return self.args_frame[service]
    def copy_args(self):
        this_VoiceArgs = self.get_select_args()
        try:
            args = this_VoiceArgs.get_args()
        except ValueError as E:
            Messagebox().show_error(message=str(E),title='错误',parent=self)
            return
        # 添加到剪贴板
        self.clipboard_clear()
        self.clipboard_append('\t'.join([str(x) for x in args.values()]))
    def comfirm(self):
        this_VoiceArgs = self.get_select_args()
        try:
            args = this_VoiceArgs.get_args()
            # 关闭
            self.close_func(result=args)
        except ValueError as E:
            Messagebox().show_error(message=str(E),title='错误',parent=self)
            return
    def preview_command(self)->bool:
        this_VoiceArgs = self.get_select_args()
        ptext = self.preview_text.get("0.0","end")
        status, message = this_VoiceArgs.exec_synthesis(text=ptext)
        if status:
            try:
                Audio(filepath=message).preview(None)
                return True
            except Exception as E:
                print(WarningPrint('AuPlayFail',E))
                self.message = ['播放失败','无法播放音频文件！']
                return False
        else:
            self.message = ['合成失败',message]
            return False
    def savefile_command(self)->bool:
        this_VoiceArgs = self.get_select_args()
        ptext = self.preview_text.get("0.0","end")
        status, message = this_VoiceArgs.exec_synthesis(text=ptext)
        if status:
            try:
                voice_this = this_VoiceArgs.variables['voice'].get()
                default_filename = voice_this.split(':')[0] + '_' + mod62_timestamp()+ '.wav'
                save_path = asksaveasfilename(initialfile=default_filename,filetypes=[('音频文件','*.wav')])
                if save_path != '':
                    copy(message, save_path)
                    return True
                else:
                    return False
            except Exception as E:
                print(WarningPrint('SaveFail',E))
                self.message = ['保存失败','无法保存音频文件！']
                return False
        else:
            self.message = ['合成失败',message]
            return False
    def preview(self):
        self.message = None
        if self.running_thread:
            if self.running_thread.is_alive():
                pass
            else:
                self.running_thread = threading.Thread(target=self.preview_command)
                self.running_thread.start()
                self.after(500,self.wait_message)
        else:
            self.running_thread = threading.Thread(target=self.preview_command)
            self.running_thread.start()
            self.after(500,self.wait_message)
    def savefile(self):
        self.message = None
        if self.running_thread:
            if self.running_thread.is_alive():
                pass
            else:
                self.running_thread = threading.Thread(target=self.savefile_command)
                self.running_thread.start()
                self.after(500,self.wait_message)
        else:
            self.running_thread = threading.Thread(target=self.savefile_command)
            self.running_thread.start()
            self.after(500,self.wait_message)
    # 等待返回消息
    def wait_message(self):
        if self.running_thread.is_alive() == False:
            if self.message:
                title,message = self.message
                Messagebox().show_error(message=message,title=title,parent=self)
        else:
            self.after(500,self.wait_message)
class VoiceChooserDialog(Dialog):
    def __init__(self, screenzoom, parent=None, title="选择语音音源", voice='', speechrate=0, pitchrate=0):
        super().__init__(parent, title, alert=False)
        self.sz = screenzoom
        self.voice = voice
        self.speech_rate = speechrate
        self.pitch_rate = pitchrate
    def close_dialog(self,result=None):
        self._result = result
        self._toplevel.destroy()
    def create_body(self, master):
        self.voice_chooser = VoiceChooser(
            master,
            screenzoom=self.sz,
            voice=self.voice,
            speech_rate=self.speech_rate,
            pitch_rate=self.pitch_rate,
            close_func=self.close_dialog
        )
        self.voice_chooser.pack(fill='both', expand=True)
    def create_buttonbox(self, master):
        pass