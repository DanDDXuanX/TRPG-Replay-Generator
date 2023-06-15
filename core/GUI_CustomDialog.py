#!/usr/bin/env python
# coding: utf-8

# 自定义的会话框

import pandas as pd
from tkinter import StringVar, IntVar
# 语音选择、重定位文件、新建项目
from .GUI_VoiceChooser import VoiceChooserDialog
from .GUI_Relocate import RelocateDialog
from .GUI_NewProject import CreateProjectDialog
# 语法解释器
from .ScriptParser import MediaDef

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