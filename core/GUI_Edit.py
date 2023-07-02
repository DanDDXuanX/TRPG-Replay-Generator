#!/usr/bin/env python
# coding: utf-8

import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from .GUI_Util import KeyValueDescribe, TextSeparator
from .GUI_EditTableStruct import TableStruct, label_colors, projection, alignments, charactor_columns, fill_mode, fit_axis, True_False
from .ScriptParser import MediaDef, RplGenLog, CharTable
from .GUI_CustomDialog import voice_chooser
from ttkbootstrap.dialogs import Messagebox, Querybox
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
        # KVD的容器
        self.elements = {}
        # SEP的容器
        self.seperator = {}
        # 小节的字典结构
        self.section:dict = None
        # 小节的表结构
        self.table_struct:dict = None
        # 小节的表结构->字典结构的对应关系
        self.keyword_arguments:dict = None
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
        self.section_index = index
        # 确定页类型
        self.table_struct:dict = self.TableStruct[line_type]
        self.keyword_arguments:dict = self.TableStruct[line_type+'.args']
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
                        this_value = self.section_index
                    elif this_kvd['valuekey'] in self.section.keys():
                        this_value = self.struct_2_value(self.section[this_kvd['valuekey']])
                    else:
                        this_value = this_kvd['default']
                    # 添加一个KVD元件
                    self.elements[key] = self.seperator[sep].add_element(
                        key=key,
                        value=this_value,
                        kvd=this_kvd,
                        callback=self.update_section_from
                        )
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
                            # TODO: this_value = self.struct_2_value(kvalue)
                        except (KeyError,IndexError):
                            this_value = this_kvd['default']
                        # 添加一个KVD元件
                        self.elements[key%(idx+1)] = self.seperator[sep%(1+idx)].add_element(
                            key=key%(idx+1),
                            value=this_value,
                            kvd=this_kvd,
                            callback=self.update_section_from
                            )
            elif this_sep['Command']['type'] == 'add_kvd':
                # 包含可变数量KVD的Sep # 例如角色表的自定义列 # 先建个空的Sep
                self.seperator[sep] = TextSeparator(
                    master=self,
                    screenzoom=self.sz,
                    describe=this_sep['Text']
                )
                # 待重载
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
                    self.elements[key] = self.seperator[sep].add_element(
                        key=key, 
                        value=this_value, 
                        kvd=this_kvd,
                        callback=self.update_section_from
                        )
    # 从窗体内容更新小节：回调函数在哪个时间点调用最合适？
    # 每次内容发生变更就回调明显是不合适的，Entry输入到一半的时候，结果很多时候都是不合法的。
    # 在Entry失去焦点的时候
    # 在Combox和Spine确实发生了变化的时候
    # 在Button刷新了值的时候
    def update_section_from(self)->dict:
        section_geted:dict = {}
        for keyword in self.keyword_arguments:
            element_key = self.keyword_arguments[keyword]
            if '%d' not in element_key:
                # 一对一的参数
                section_geted[keyword] = self.value_2_struct(self.elements[element_key].get())
            else:
                # 一对多的列表参数（Balloon，ChatWindow）
                list_of_args = []
                # 遍历多次出现的参数
                for idx in range(0,999):
                    element_key_this = element_key%(1+idx)
                    if element_key_this in self.elements:
                        list_of_args.append(
                            self.value_2_struct(
                                self.elements[element_key_this].get()
                            )
                        )
                    else:
                        break
                # 将多次出现的参数以列表的形式返回
                section_geted[keyword] = list_of_args
        return section_geted
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
    table_col = CharTable.table_col
    def __init__(self, master, screenzoom):
        super().__init__(master, screenzoom)
        self.TableStruct = TableStruct['CharTable']
        # 初始化时的角色名
        self.name:str = ''
    # 从角色表更新表结构，初始化时
    def update_from_section(self,index:str,section:dict,line_type='charactor'):
        # 继承
        super().update_from_section(index,section,line_type=line_type)
        CharactorEdit.custom_col = self.page.content.get_customize()
        # 补充自定义列的内容
        self.seperator['CustomSep'].add_button(text='添加+',command=self.add_customs)
        self.seperator['CustomSep'].add_button(text='删除-',command=self.remove_customs)
        for custom in CharactorEdit.custom_col:
            self.add_a_custom_kvd(custom=custom)
        # 是否是default？是则禁用相应entry
        if self.elements['Subtype'].get() == 'default':
            self.elements['Subtype'].input.configure(state='disable')
        # 媒体
        self.elements['Animation'].input.configure(values=['NA']+self.get_avaliable_anime(),state='readonly')
        self.elements['Bubble'].input.configure(values=['NA']+self.get_avaliable_bubble(),state='readonly')
        self.elements['Animation'].input.bind("<<ComboboxSelected>>",self.update_preview,'+')
        self.elements['Bubble'].input.bind("<<ComboboxSelected>>",self.update_preview,'+')
        # 音源
        for ele in ['Voice','SpeechRate','PitchRate']:
            self.elements[ele].describe.configure(command=lambda :self.open_voice_selection(
                master=self,
                voice=self.elements['Voice'].value,
                speech_rate=self.elements['SpeechRate'].value,
                pitch_rate=self.elements['PitchRate'].value,
            ))
        # 更新
        self.update_item()
    # 从表结构更新角色表内容
    def update_section_from(self) -> dict:
        # 获取新小节
        new_section = super().update_section_from()
        # 补充自定义列
        for custom in CharactorEdit.custom_col:
            new_section[custom] = self.value_2_struct(self.elements[custom].get())
        # 是否发生变化？
        if new_section == self.section:
            return self.section
        # 新小节的keyword
        new_keyword = new_section['Name']+'.'+new_section['Subtype']
        # 检查是否是更名？
        if new_keyword != self.section_index:
            # 检查新名字是否可用
            if new_keyword in self.page.content.struct:
                Messagebox().show_warning(message='这个差分名已经被使用了！',title='重名',parent=self)
                self.elements['Subtype'].value.set(self.section['Subtype'])
                return self.section
            else:
                # 更新角色表的内容
                self.section.update(new_section)
                # 角色表执行重命名
                self.section:dict = self.page.content.resubtype(to_resubtype=self.section_index,new_subtype=new_keyword)
                # 视图刷新显示
                self.page.container.refresh_element(keyword=self.section_index,new_keyword=new_keyword)
                self.section_index = new_keyword
        else:
            # 更新角色表的内容
            self.section.update(new_section)
            self.page.container.refresh_element(keyword=self.section_index)
        return self.section
    # 立绘和角色发生变动的时候，刷新预览
    def update_preview(self,event):
        self.page.preview.preview(char_name=self.section_index)
    # 打开音源选择窗
    def open_voice_selection(self, master, voice, speech_rate, pitch_rate):
        voice_chooser(master=master,voice_obj=voice,speech_obj=speech_rate,pitch_obj=pitch_rate)
        # def 这个时候应有回调
        self.update_section_from()
    # 添加一个自定义列
    def add_customs(self):
        get_string = Querybox().get_string(prompt="请输入自定义列名",title='新建自定义列',parent=self)
        if get_string in self.custom_col or get_string in self.table_col:
            Messagebox().show_warning(message='这个列名已经使用过了',title='重名！',parent=self)
            return
        elif get_string is None:
            return
        else:
            # 在角色表中新建
            self.page.content.add_customize(get_string)
            CharactorEdit.custom_col.append(get_string)
            # 新建KVD
            self.add_a_custom_kvd(custom=get_string)
    # 移除一个自定义列
    def remove_customs(self):
        pass
    # 在自定义区新建一个KVD
    def add_a_custom_kvd(self,custom):
        kvd_tplt:dict = self.table_struct['CustomSep']['Content']
        tplt = kvd_tplt['{template}']
        this_kvd:dict = tplt.copy()
        # this_key
        this_key = custom
        # this_kvd
        for keyword in this_kvd:
            if type(this_kvd[keyword]) is str:
                this_kvd[keyword] = this_kvd[keyword].format(template=custom)
            else:
                pass
        # this_value
        if this_kvd['valuekey'].format(custom) in self.section.keys():
            this_value = self.struct_2_value(self.section[this_kvd['valuekey']])
        else:
            this_value = this_kvd['default']
        # 添加一个KVD元件
        self.elements[this_key] = self.seperator['CustomSep'].add_element(
            key=this_key,
            value=this_value,
            kvd=this_kvd,
            callback=self.update_section_from
            )
class MediaEdit(EditWindow):
    medef_tool = MediaDef()
    def __init__(self, master, screenzoom):
        super().__init__(master, screenzoom)
        self.TableStruct = TableStruct['MediaDef']
    def update_from_section(self,index:str,section: dict, line_type):
        super().update_from_section(index, section, line_type)
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