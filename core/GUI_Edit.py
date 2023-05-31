#!/usr/bin/env python
# coding: utf-8

import ttkbootstrap as ttk
from .GUI_Util import KeyValueDescribe, TextSeparator
from .ScriptParser import MediaDef
# 编辑区

# 编辑窗
class EditWindow(ttk.LabelFrame):
    def __init__(self,master,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master,bootstyle='primary',text='编辑区')
        self.page = master
        # 初始化状态
        self.line_type = 'no_selection'
        self.elements = {}
        self.section:dict = None
        # 更新
        self.update_item()
    def update_item(self):
        SZ_5 = int(5*self.sz)
        SZ_15 = int(15*self.sz)
        for key in self.elements:
            item:KeyValueDescribe = self.elements[key]
            item.pack(side='top',anchor='n',fill='x',pady=(0,SZ_5),padx=(SZ_5,SZ_15))
    def clear_item(self):
        for key in self.elements:
            item:KeyValueDescribe = self.elements[key]
            item.destroy()
        self.elements.clear()
    # 从小节中更新窗体内容
    def update_from_section(self,section:dict):
        self.clear_item()
    # 将窗体内容覆盖到小节
    def write_section(self):
        self.section.clear()
    # 获取可用立绘、气泡名
    def get_avaliable_anime(self)->list:
        return self.page.ref_medef.get_type('anime')
    def get_avaliable_bubble(self)->list:
        return self.page.ref_medef.get_type('bubble')
    def get_avaliable_text(self)->list:
        return self.page.ref_medef.get_type('text')
    def get_avaliable_pos(self)->list:
        return self.page.ref_medef.get_type('pos')
class CharactorEdit(EditWindow):
    custom_col = []
    table_col = {
        'Sep1'      :['角色'],
        'Name'      :['名字：',   'str','label',  'text','',    ''],
        'Subtype'   :['差分：',   'str','entry',  'text','（输入）',    'default'],
        'Sep2'      :['媒体'],
        'Animation' :['立绘：',   'str','combox', 'text','（选择）',    'NA'],
        'Bubble'    :['气泡：',   'str','combox', 'text','（选择）',    'NA'],
        'Sep3'      :['语音'],
        'Voice'     :['音源：',   'str','entry',  'button','选择',      'NA'],
        'SpeechRate':['语速：',   'int','entry',  'button','选择',      0],
        'PitchRate' :['语调：',   'int','entry',  'button','选择',      0],
        'Sep4'      :['自定义']
        }
    def update_from_section(self,section:dict):
        super().update_from_section(section)
        self.section = section
        # 编辑区
        for col in CharactorEdit.table_col:
            if col[:3] == 'Sep':
                name, = CharactorEdit.table_col[col]
                self.elements[col] = TextSeparator(
                    master=self,
                    screenzoom=self.sz,
                    describe=name
                    )
            else:
                key,entry_T,entry_S,descr_T,descr_V,default = CharactorEdit.table_col[col]
                self.elements[col] = KeyValueDescribe(
                    master=self,
                    screenzoom=self.sz,
                    key=key,
                    value={
                        'type':entry_T,
                        'style':entry_S,
                        'value':self.section[col]},
                    describe={
                        'type':descr_T,
                        'text':descr_V
                    }
                )
        # 媒体
        self.elements['Animation'].input.configure(values=['NA']+self.get_avaliable_anime(),state='readonly')
        self.elements['Bubble'].input.configure(values=['NA']+self.get_avaliable_bubble(),state='readonly')
        # 音源
        for ele in ['Voice','SpeechRate','PitchRate']:
            self.elements[ele].describe.configure(command=lambda :self.open_voice_selection(
                master=self,
                voice=self.elements['Voice'].get(),
                speech_rate=self.elements['SpeechRate'].get(),
                pitch_rate=self.elements['PitchRate'].get(),
            ))
        # 更新
        self.update_item()
    # 打开音源选择窗
    def open_voice_selection(self, master, voice, speech_rate, pitch_rate):
        print(voice,speech_rate,pitch_rate)
class MediaEdit(EditWindow):
    def __init__(self, master, screenzoom, type):
        super().__init__(master, screenzoom)

class AnimeEdit(EditWindow):
    table_col = {
        'Sep1'          :['媒体信息'],
        'type'          :['类型：',   'str','label',  'text','', 'Animation'],
        # 'Name'          :['媒体名：', 'str','entry',  'text','（数据）'],
        'Sep2'          :['图片参数'],
        'filepath'      :['文件路径：','str','entry',  'button','浏览', ''],
        'pos'           :['位置：',    'str','combox', 'button','选择', '(0,0)'],
        'scale'         :['缩放：',    'float','spine', 'button','选择','1.0'],
        'Sep3'          :['动画参数'],
        'tick'          :['拍率：',    'int','spine',   'text','（选择）', '1'],
        'loop'          :['循环播放：','bool','combox',  'text','（选择）', True],
        'Sep4'          :['标签色'],
        'label_color'   :['标签色：',   'int','combox',  'text','（选择）', 'Lavender'],
        }
    medef_tool = MediaDef()
    def update_from_section(self,section:dict):
        super().update_from_section(section)
        self.section = section
        # 编辑区
        for col in AnimeEdit.table_col:
            if col[:3] == 'Sep':
                name, = AnimeEdit.table_col[col]
                self.elements[col] = TextSeparator(
                    master=self,
                    screenzoom=self.sz,
                    describe=name
                    )
            else:
                key,entry_T,entry_S,descr_T,descr_V,default = AnimeEdit.table_col[col]
                try:
                    this_value = self.medef_tool.value_export(self.section[col])
                except KeyError:
                    this_value = default
                try:
                    self.elements[col] = KeyValueDescribe(
                        master=self,
                        screenzoom=self.sz,
                        key=key,
                        value={
                            'type':entry_T,
                            'style':entry_S,
                            'value':this_value},
                        describe={
                            'type':descr_T,
                            'text':descr_V
                        }
                    )
                except:
                    pass
        # 更新
        self.update_item()