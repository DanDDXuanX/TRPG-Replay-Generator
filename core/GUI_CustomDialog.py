#!/usr/bin/env python
# coding: utf-8

# 自定义的会话框

import pandas as pd
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Dialog,MessageCatalog
from tkinter import StringVar, IntVar
# 语音选择、重定位文件、新建项目
from .GUI_VoiceChooser import VoiceChooserDialog
from .GUI_Relocate import RelocateDialog
from .GUI_NewProject import CreateProjectDialog
from .GUI_Util import DictCombobox
# 语法解释器
from .ScriptParser import MediaDef

# 包含一个选项的选择聊天框
class SelectionQurey(Dialog):
    def __init__(self, parent=None, title="选择", prompt="",choice={}, alert=False):
        super().__init__(parent, title, alert)
        self._prompt:str = prompt
        self._choice:dict = choice
        self._padding = (20,20)
    def create_body(self, master):
        frame = ttk.Frame(master, padding=self._padding)
        if self._prompt:
            prompt_label = ttk.Label(frame, text=self._prompt)
            prompt_label.pack(pady=(0, 5), fill='x', anchor='n')
        self.varible = StringVar()
        entry = DictCombobox(master=frame, textvariable=self.varible, state='disable')
        entry.update_dict(self._choice)
        entry.pack(pady=(0, 5), fill='x')
        entry.bind("<Return>", self.on_submit)
        entry.bind("<KP_Enter>", self.on_submit)
        entry.bind("<Escape>", self.on_cancel)
        frame.pack(fill='x', expand=True)
        self._initial_focus = entry
    def create_buttonbox(self, master):
        frame = ttk.Frame(master, padding=(5, 10))
        # 确定
        submit = ttk.Button(
            master=frame,
            bootstyle="primary",
            text=MessageCatalog.translate("Submit"),
            command=self.on_submit,
        )
        submit.pack(padx=5, side='right')
        submit.lower()
        # 取消
        cancel = ttk.Button(
            master=frame,
            bootstyle="secondary",
            text=MessageCatalog.translate("Cancel"),
            command=self.on_cancel,
        )
        cancel.pack(padx=5, side='right')
        cancel.lower()
        ttk.Separator(self._toplevel).pack(fill='x')
        frame.pack(side='bottom', fill='x', anchor='s')
    def on_submit(self, *_):
        self._result = self.varible.get()
        self._toplevel.destroy()
    def on_cancel(self, *_):
        self._toplevel.destroy()
        return
def selection_query(master,prompt,choice:dict):
    dialog_window = SelectionQurey(parent=master,prompt=prompt,choice=choice)
    dialog_window.show()
    # 获取结果
    result_args = dialog_window.result
    return result_args
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
    
# 打开新建项目窗口，并新建一个项目
def new_project(master, ptype='Empty'):
    dialog_window = CreateProjectDialog(
        parent=master,
        screenzoom=master.sz,
        ptype=ptype
    )
    dialog_window.show()
    # 获取结果
    return dialog_window.result