#!/usr/bin/env python
# coding: utf-8

import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from .GUI_Util import KeyValueDescribe, TextSeparator
from .GUI_EditTableStruct import TableStruct, label_colors, projection, alignments, charactor_columns, fill_mode, fit_axis, True_False
from .ScriptParser import MediaDef, RplGenLog
# 编辑区

# 编辑窗
class EditWindow(ScrolledFrame):
    TableStruct = TableStruct
    def __init__(self,master,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master, autohide=True)
        self.vscroll.config(bootstyle='secondary-round')
        self.page = master
        # 初始化状态
        self.line_type = 'no_selection'
        self.elements = {}
        self.seperator = {}
        self.section:dict = None
        # 更新
        self.update_item()
    def update_item(self):
        SZ_5 = int(5*self.sz)
        SZ_15 = int(15*self.sz)
        for key in self.seperator:
            item:TextSeparator = self.seperator[key]
            item.pack(side='top',anchor='n',fill='x',pady=(0,SZ_5),padx=(SZ_5,SZ_15))
    def clear_item(self):
        for key in self.elements:
            item:KeyValueDescribe = self.elements[key]
            item.destroy()
        for key in self.seperator:
            item:TextSeparator = self.seperator[key]
            item.destroy()
        self.elements.clear()
        self.seperator.clear()
    # 从小节中更新窗体内容
    def update_from_section(self,index:str,section:dict,line_type):
        # 清除
        self.clear_item()
        self.section = section
        # 确定页类型
        self.table_struct:dict = self.TableStruct[line_type]
        # 编辑区
        for sep in self.table_struct:
            this_sep:dict = self.table_struct[sep]
            # 一般的
            if this_sep['Command'] is None:
                self.seperator[sep] = TextSeparator(
                    master=self,
                    screenzoom=self.sz,
                    describe=this_sep['Text']
                )
                for key in this_sep['Content']:
                    this_kvd:dict = this_sep['Content'][key]
                    # 如果valuekey判断valuekey
                    if this_kvd['valuekey'] == '$key':
                        this_value = index
                    elif this_kvd['valuekey'] in self.section.keys():
                        this_value = self.struct_2_value(self.section[this_kvd['valuekey']])
                    else:
                        this_value = this_kvd['default']
                    self.elements[key] = self.seperator[sep].add_element(key=key, value=this_value, kvd=this_kvd)
            # 重复出现的Sep
            elif this_sep['Command']['type'] == 'add_sep':
                key_target:str = this_sep['Command']['key']
                key_valuekey:str = this_sep['Content'][key_target]['valuekey']
                # 获取作为关键字的key_values
                if key_valuekey in self.section.keys():
                    key_values:list = self.section[key_valuekey]
                else:
                    key_values:list = [this_sep['Content'][key_target]['default']]
                # 多次建立
                for idx, kvalue in enumerate(key_values):
                    self.seperator[sep%(1+idx)] = TextSeparator(
                        master=self,
                        screenzoom=self.sz,
                        describe=this_sep['Text']%(1+idx)
                    )
                    for key in this_sep['Content']:
                        this_kvd:dict = this_sep['Content'][key]
                        # 取出对应顺序的
                        try:
                            this_value = self.struct_2_value(self.section[this_kvd['valuekey']][idx])
                        except (KeyError,IndexError):
                            this_value = this_kvd['default']
                        self.elements[key%(idx+1)] = self.seperator[sep%(1+idx)].add_element(key=key%(idx+1), value=this_value, kvd=this_kvd)
            elif this_sep['Command']['type'] == 'add_kvd':
                # 包含可变数量KVD的Sep # TODO
                pass
            elif this_sep['Command']['type'] == 'subscript':
                self.seperator[sep] = TextSeparator(
                    master=self,
                    screenzoom=self.sz,
                    describe=this_sep['Text']
                )
                split_str = this_sep['Command']['key']
                for key in this_sep['Content']:
                    this_kvd:dict = this_sep['Content'][key]
                    # subscript型key
                    key_subscript = this_kvd['valuekey'].split(split_str)
                    this_value = self.section
                    for ks in key_subscript:
                        try:
                            this_value = this_value[ks]
                        except KeyError as E:
                            print(E)
                            this_value = this_kvd['default']
                    self.elements[key] = self.seperator[sep].add_element(key=key, value=this_value, kvd=this_kvd)

    # 从section的值转为显示的value
    def struct_2_value(self,section):
        return section
    def value_2_struct(self,value):
        return value
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
    def get_avaliable_charcol(self)->dict:
        charactor_columns_this = charactor_columns.copy()
        for key in CharactorEdit.custom_col:
            charactor_columns_this["{}（自定义）".format(key)] = "'{}'".format(key)
        return charactor_columns_this
class CharactorEdit(EditWindow):
    custom_col = []
    def __init__(self, master, screenzoom):
        super().__init__(master, screenzoom)
        self.TableStruct = TableStruct['CharTable']
    def update_from_section(self,index:str,section:dict,line_type='charactor'):
        super().update_from_section(index,section,line_type=line_type)
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
    medef_tool = MediaDef()
    def __init__(self, master, screenzoom):
        super().__init__(master, screenzoom)
        self.TableStruct = TableStruct['MediaDef']
    def update_from_section(self,index:str,section: dict, line_type):
        super().update_from_section(index, section, line_type)
        # TODO:各个类型的config
        # 更新
        self.update_media_element_prop(line_type)
        self.update_item()
    def update_media_element_prop(self,line_type):
        # 标签色
        if line_type not in ['Pos','FreePos','PosGrid']:
            self.elements['label_color'].input.update_dict(label_colors)
        # PosGrid
        if line_type == 'PosGrid':
            self.elements['x_step'].input.configure(from_=0,to=100,increment=1)
            self.elements['y_step'].input.configure(from_=0,to=100,increment=1)
        # 字体
        if line_type in ['Text','StrokeText','RichText']:
            self.elements['line_limit'].input.configure(from_=0,to=100,increment=1)
            self.elements['fontsize'].input.configure(from_=0,to=300,increment=5)
            self.elements['fontfile'].bind_button(dtype='fontfile-file')
            self.elements['color'].bind_button(dtype='color')
            if line_type == 'StrokeText':
                self.elements['edge_color'].bind_button(dtype='color')
                self.elements['edge_width'].input.configure(from_=0,to=30,increment=1)
                self.elements['projection'].input.update_dict(projection)
        # Pos
        if line_type in ['Bubble','Balloon','DynamicBubble','ChatWindow','Animation','Background']:
            self.elements['filepath'].bind_button(dtype='picture-file')
            self.elements['pos'].input.configure(values=self.get_avaliable_pos())
            self.elements['scale'].input.configure(from_=0.1,to=3,increment=0.1)
        # MainText HeadText
        if line_type in ['Bubble','Balloon','DynamicBubble']:
            self.elements['Main_Text'].input.configure(values=['Text()']+self.get_avaliable_text())
            self.elements['line_distance'].input.configure(from_=0.8,to=3,increment=0.1)
        if line_type in ['Bubble','Balloon']:
            self.elements['align'].input.update_dict(alignments)
        if line_type in ['Bubble','DynamicBubble']:
            self.elements['Header_Text'].input.configure(values=['None','Text()']+self.get_avaliable_text())
            self.elements['ht_target'].input.update_dict(self.get_avaliable_charcol())
        if line_type == 'DynamicBubble':
            self.elements['fill_mode'].input.update_dict(fill_mode)
            self.elements['fit_axis'].input.update_dict(fit_axis)
        # TODO: Balloon 的每一个Header_Text、ht_target
        if line_type == 'Animation':
            self.elements['tick'].input.configure(from_=1,to=30,increment=1)
            self.elements['loop'].input.update_dict(True_False)
        if line_type == 'Audio':
            self.elements['filepath'].bind_button(dtype='soundeff-file')
        if line_type == 'BGM':
            self.elements['filepath'].bind_button(dtype='BGM-file')
            self.elements['volume'].input.configure(from_=0,to=100,increment=10)
            self.elements['loop'].input.update_dict(True_False)
    def struct_2_value(self,section):
        return self.medef_tool.value_export(section)
class LogEdit(EditWindow):
    def __init__(self, master, screenzoom):
        super().__init__(master, screenzoom)
        self.TableStruct = TableStruct['RplGenLog']
    def update_from_section(self,index:str,section: dict, line_type):
        super().update_from_section(index, section, line_type)
        # TODO:各个类型的config
        # 更新
        self.update_item()