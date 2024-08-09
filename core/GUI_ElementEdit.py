#!/usr/bin/env python
# coding: utf-8

import re
import numpy as np
import ttkbootstrap as ttk
from .GUI_Util import KeyValueDescribe, TextSeparator, FluentFrame, ask_rename_boardcast
from .GUI_TableStruct import EditTableStruct, label_colors, projection, alignments, vertical_alignments, chatalign, charactor_columns, fill_mode, fit_axis, True_False, left_right, media_help_url,formulas
from .GUI_CustomDialog import voice_chooser, selection_query
from .GUI_Language import tr
from .GUI_Link import Link
from .ScriptParser import MediaDef, RplGenLog, CharTable
from .Exceptions import SyntaxsError
from ttkbootstrap.dialogs import Messagebox, Querybox
from ttkbootstrap.toast import ToastNotification
# 编辑区

# 编辑窗
class EditWindow(FluentFrame):
    TableStruct = EditTableStruct
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
        self.section_index:str = ''
        # 小节的表结构
        self.table_struct:dict = None
        # 小节的表结构->字典结构的对应关系
        self.keyword_arguments:dict = None
        # 更新
        self.update_item()
    def update_item(self):
        SZ_5 = int(5*self.sz)
        SZ_10 = 2 * SZ_5
        SZ_20 = 4 * SZ_5
        for key in self.seperator:
            item:TextSeparator = self.seperator[key]
            item.pack(side='top',anchor='n',fill='x',pady=(0,SZ_5),padx=(SZ_10,SZ_20))
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
        self.line_type = line_type
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
    # 从窗体内容更新小节
    def update_section_from(self)->dict:
        section_got:dict = {}
        for keyword in self.keyword_arguments:
            element_key = self.keyword_arguments[keyword]
            if '%d' not in element_key:
                # 一对一的参数
                section_got[keyword] = self.value_2_struct(self.elements[element_key].get())
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
                section_got[keyword] = list_of_args
        return section_got
    # 从section的值转为显示的value
    def struct_2_value(self,section):
        return section
    def value_2_struct(self,value):
        return value
    # 获取可用立绘、气泡名
    def get_avaliable_anime(self)->list:
        return self.page.ref_medef.get_type('anime')
    def get_avaliable_bubble(self,cw=True,bb=True)->list:
        if bb:
            return self.page.ref_medef.get_type('bubble',cw)
        else:
            return self.page.ref_medef.get_type('subbubble')
    def get_avaliable_text(self)->list:
        return self.page.ref_medef.get_type('text')
    def get_avaliable_pos(self,bezier=True)->list:
        if bezier:
            return self.page.ref_medef.get_type('bezier')
        else:
            return self.page.ref_medef.get_type('pos')
    def get_avaliable_charcol(self)->dict:
        charactor_columns_this = charactor_columns.copy()
        charactor_columns_this.update(self.get_avaliable_custom())
        return charactor_columns_this
    def get_avaliable_custom(self)->dict:
        charactor_columns_this = {}
        for key in Link['project_chartab'].customize_col:
            charactor_columns_this[tr("{}（自定义）").format(key)] = "'{}'".format(key)
        return charactor_columns_this
    # 刷新预览
    def update_preview(self,keywords:list):
        # 待重载
        pass
class CharactorEdit(EditWindow):
    custom_col = []
    table_col = CharTable.table_col
    def __init__(self, master, screenzoom):
        super().__init__(master, screenzoom)
        self.TableStruct = EditTableStruct['CharTable']
    # 从角色表更新表结构，初始化时
    def update_from_section(self,index:str,section:dict,line_type='charactor'):
        # 继承
        super().update_from_section(index,section,line_type=line_type)
        CharactorEdit.custom_col = self.page.content.customize_col # 直接引用，read only！
        # 补充自定义列的内容
        self.seperator['CustomSep'].add_button(text=tr('添加+'),command=self.add_customs)
        self.seperator['CustomSep'].add_button(text=tr('删除-'),command=self.remove_customs)
        for custom in CharactorEdit.custom_col:
            self.add_a_custom_kvd(custom=custom)
        # 是否是default？是则禁用相应entry
        if self.elements['Subtype'].get() == 'default':
            self.elements['Subtype'].input.configure(state='disable')
        self.elements['Subtype'].enable_trace()
        self.elements['Subtype'].input.bind("<FocusIn>",self.notice_enter)
        # 媒体
        self.elements['Animation'].input.configure(values=['NA']+self.get_avaliable_anime(),state='readonly')
        self.elements['Bubble'].input.configure(values=['NA']+self.get_avaliable_bubble(cw=True),state='readonly')
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
        else:
            # 发生变化的关键字
            changed_key = []
            for key in new_section:
                if key not in self.section:
                    changed_key.append(key)
                if new_section[key] != self.section[key]:
                    changed_key.append(key)
        # 新小节的keyword
        new_keyword = new_section['Name']+'.'+new_section['Subtype']
        # 检查是否是更名？
        if new_keyword != self.section_index:
            # 检查新名字是否可用
            if new_keyword in self.page.content.struct:
                # BUG：如何避免使用 focus out？ 这样会导致重复弹出两次！
                Messagebox().show_warning(message=tr('这个差分名已经被使用了！'),title=tr('重名'),parent=self)
                self.reset_name()
                return self.section
            elif re.fullmatch("^\w+$",new_section['Subtype']) is None:
                Messagebox().show_warning(message=tr('这个差分名是非法的！'),title=tr('非法名'),parent=self)
                self.reset_name()
                return self.section
            else:
                # 更新角色表的内容
                self.section.update(new_section)
                # 角色表执行重命名
                self.section:dict = self.page.content.resubtype(to_resubtype=self.section_index,new_subtype=new_keyword)
                # 广播
                ask_rename_boardcast(
                    master  = self,
                    old_name= self.section_index,
                    new_name= new_keyword,
                    otype   = 'subtype'
                    )
                # 视图刷新显示
                self.page.container.refresh_element(keyword=self.section_index,new_keyword=new_keyword)
                self.section_index = new_keyword
        else:
            # 更新角色表的内容
            self.section.update(new_section)
            self.page.container.refresh_element(keyword=self.section_index)
        # 刷新预览
        self.update_preview(keywords=changed_key)
        return self.section
    # 立绘和角色发生变动的时候，刷新预览
    def update_preview(self,keywords:list=[]):
        if 'Animation' in keywords or 'Bubble' in keywords:
            self.page.preview.preview(char_name=self.section_index)
    # 打开音源选择窗
    def open_voice_selection(self, master, voice, speech_rate, pitch_rate):
        voice_chooser(master=master,voice_obj=voice,speech_obj=speech_rate,pitch_obj=pitch_rate)
        # def 这个时候应有回调
        self.update_section_from()
    # 添加一个自定义列
    def add_customs(self):
        get_string = Querybox().get_string(prompt=tr("请输入自定义列名"),title=tr('新建自定义列'),parent=self)
        if get_string in self.custom_col or get_string in self.table_col:
            Messagebox().show_warning(message=tr('这个列名已经使用过了！'),title=tr('重名'),parent=self)
            return
        elif get_string is None:
            return
        else:
            # 在角色表中新建
            self.page.content.add_customize(get_string)
            # 新建KVD
            self.add_a_custom_kvd(custom=get_string)
    # 移除一个自定义列
    def remove_customs(self):
        get_string = selection_query(master=self,screenzoom=self.sz,title=tr('删除自定义'),prompt=tr('请选择想要删除的自定义项'),choice=self.get_avaliable_custom())
        if get_string:
            del_colname = get_string[1:-1]
            if del_colname in self.custom_col:
                # 在角色表中删除
                self.page.content.del_customize(del_colname)
                # 移除KVD
                self.del_a_custom_kvd(custom=del_colname)
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
        # 移动滚动条
        self.update()
        self.enable_scrolling()
        self.yview_moveto(1.0)
    def del_a_custom_kvd(self,custom):
        this_key = custom
        # 直接pop接destroy
        self.elements.pop(this_key).destroy()
        # 移动滚动条
        self.update()
        self.enable_scrolling()
        self.yview_moveto(1.0)
    # 重设名字
    def reset_name(self):
        self.elements['Subtype'].value.set(self.section['Subtype'])
    # 提醒回车键
    def notice_enter(self,event):
        # 弹出消息提示，Toast
        ToastNotification(
            title=tr('按回车确定'),
            message=tr('如果确认修改差分名，请按回车键！'),
            duration=1000
        ).show_toast()
class MediaEdit(EditWindow):
    medef_tool = MediaDef()
    def __init__(self, master, screenzoom):
        super().__init__(master, screenzoom)
        self.TableStruct = EditTableStruct['MediaDef']
    def update_from_section(self,index:str,section: dict, line_type):
        super().update_from_section(index, section, line_type)
        # 更新
        self.bind_media_class_help()
        self.update_media_element_prop()
        self.update_item()
    def update_section_from(self) -> dict:
        # 获取新小节
        new_section = super().update_section_from()
        # 新小节的keyword
        new_keyword:str = self.elements['Name'].get()
        # print(new_keyword, new_section)
        # 是否发生变化？
        if new_section == self.section and new_keyword==self.section_index:
            return self.section
        else:
            # 发生变化的关键字
            changed_key = []
            for key in new_section:
                # KEY
                if key not in self.section:
                    changed_key.append(key)
                elif new_section[key] != self.section[key]:
                    changed_key.append(key)
        # 检查是否更名
        if new_keyword != self.section_index:
            # 检查新名字是否可用
            if new_keyword in self.page.content.struct or new_keyword in ['black','white']:
                Messagebox().show_warning(message=tr('这个媒体名已经被使用了！'),title=tr('重名'),parent=self)
                self.reset_name()
                return self.section
            elif re.fullmatch("^\w+$",new_keyword) is None or new_keyword[0].isdigit():
                Messagebox().show_warning(message=tr('这个媒体名是非法的！'),title=tr('非法名'),parent=self)
                self.reset_name()
                return self.section
            else:
                # 更新媒体库的内容
                self.section.update(new_section)
                # 媒体库执行重命名
                self.section:dict = self.page.content.rename(to_rename=self.section_index,new_name=new_keyword)
                # 广播
                ask_rename_boardcast(
                    master  = self,
                    old_name= self.section_index,
                    new_name= new_keyword,
                    otype   = self.section['type']
                    )
                # 视图刷新显示
                self.page.container.refresh_element(keyword=self.section_index,new_keyword=new_keyword)
                self.section_index = new_keyword
        else:
            # 更新媒体库内容
            self.section.update(new_section)
            self.page.container.refresh_element(keyword=self.section_index)
        # 刷新预览的显示
        self.update_preview(keywords=changed_key)
        return self.section
    def bind_media_class_help(self):
        url = media_help_url[self.line_type]
        self.elements['type'].bind_button(dtype='url:'+url)
    def update_media_element_prop(self):
        # 媒体名：禁用focus out
        self.elements['Name'].enable_trace()
        self.elements['Name'].input.bind("<FocusIn>",self.notice_enter)
        # 标签色
        if self.line_type not in ['Pos','FreePos','PosGrid','BezierCurve']:
            self.elements['label_color'].input.update_dict(label_colors)
        if self.line_type in ['Pos','FreePos','PosGrid']:
            self.elements['pos'].describe.configure(command=lambda :self.select_dot('o0','p1'))
        # PosGrid
        if self.line_type == 'PosGrid':
            self.elements['x_step'].input.configure(from_=1,to=100,increment=1)
            self.elements['y_step'].input.configure(from_=1,to=100,increment=1)
            self.elements['end'].describe.configure(command=lambda :self.select_dot('o1','p1'))
        # BezierCurve
        if self.line_type == 'BezierCurve':
            self.elements['pos'].describe.configure(command=lambda :self.select_dot('a0','p1'))
            self.elements['pos'].input.configure(values=self.get_avaliable_pos(bezier=False))
            for idx in range(1,999):
                if "anchor_%d"%idx in self.elements:
                    self.elements["control_left_%d"%idx].describe.configure(command=self.select_dot_idx(idx,dottype='cl'))
                    self.elements['control_right_%d'%idx].describe.configure(command=self.select_dot_idx(idx,dottype='cr'))
                    self.elements['anchor_%d'%idx].describe.configure(command=self.select_dot_idx(idx,dottype='a'))
                    self.elements['anchor_%d'%idx].input.configure(values=self.get_avaliable_pos(bezier=False))
                    self.elements["frame_point_%d"%idx].input.configure(from_=0,to=3000,increment=5)
                    self.elements["speed_formula_%d"%idx].input.update_dict(formulas)
                else:
                    break
            self.update_sep_button()
        # 字体
        if self.line_type in ['Text','StrokeText','RichText','HPLabel']:
            self.elements['fontsize'].input.configure(from_=0,to=300,increment=5)
            self.elements['fontfile'].bind_button(dtype='fontfile-file')
            self.elements['color'].bind_button(dtype='color')
            if self.line_type != 'HPLabel':
                self.elements['line_limit'].input.configure(from_=0,to=100,increment=1)
            else:
                self.elements['fg_path'].bind_button(dtype='picture-file')
                self.elements['bg_path'].bind_button(dtype='picture-file')
                self.elements['align'].input.update_dict(left_right)
                self.elements['width'].input.configure(from_=0,to=1000,increment=50)
                self.elements['repeat'].input.configure(from_=0,to=100,increment=1)
            if self.line_type == 'StrokeText':
                self.elements['edge_color'].bind_button(dtype='color')
                self.elements['edge_width'].input.configure(from_=0,to=30,increment=1)
                self.elements['projection'].input.update_dict(projection)
            if self.line_type == 'RichText':
                self.elements['scale'].input.configure(from_=0.1,to=3.0,increment=0.2)
                for idx in range(1,999):
                    if "sub_key_%d"%idx in self.elements:
                        self.elements['sub_icon_%d'%idx].bind_button(dtype='picture-file')
                    else:
                        break
                self.update_sep_button()
        # Pos
        if self.line_type in ['Bubble','Balloon','DynamicBubble','ChatWindow','Animation','Sprite','Background']:
            if self.line_type == 'Animation':
                self.elements['filepath'].bind_button(dtype='animate-file')
            elif self.line_type == 'Sprite':
                self.elements['filepath'].bind_button(dtype='animate-file')
                self.elements['eyepath'].bind_button(dtype='animate-file')
                self.elements['mouthpath'].bind_button(dtype='animate-file')
            else:
                self.elements['filepath'].bind_button(dtype='picture-file')
            self.elements['pos'].input.configure(values=self.get_avaliable_pos())
            self.elements['pos'].describe.configure(command=lambda :self.select_dot('g0','p1'))
            self.elements['scale'].input.configure(from_=0.1,to=3,increment=0.01)
        # MainText HeadText
        if self.line_type in ['Bubble','Balloon','DynamicBubble']:
            self.elements['Main_Text'].input.configure(values=['Text()']+self.get_avaliable_text(),state='readonly')
            self.elements['line_distance'].input.configure(from_=0.8,to=3,increment=0.1)
        if self.line_type in ['Bubble','Balloon']:
            self.elements['mt_pos'].describe.configure(command=lambda :self.select_dot('b0','p1'))
            self.elements["mt_rotate"].input.configure(from_=-180,to=180,increment=1)
            self.elements['align'].input.update_dict(alignments)
            self.elements['vertical_align'].input.update_dict(vertical_alignments)
            self.elements['line_num_est'].input.configure(from_=1,to=10,increment=1)
        if self.line_type in ['Bubble','DynamicBubble']:
            self.elements['Header_Text'].input.configure(values=['None','Text()']+self.get_avaliable_text(),state='readonly')
            self.elements['ht_pos'].describe.configure(command=lambda :self.select_dot('b1','p1'))
            self.elements['ht_target'].input.update_dict(self.get_avaliable_charcol())
        if self.line_type == 'Bubble':
            self.elements["head_align"].input.update_dict(alignments)
            self.elements["ht_rotate"].input.configure(from_=-180,to=180,increment=1)
        if self.line_type == 'DynamicBubble':
            self.elements['mt_pos'].describe.configure(command=lambda :self.select_dot('m0','p1'))
            self.elements['mt_end'].describe.configure(command=lambda :self.select_dot('m0','p2'))
            self.elements['fill_mode'].input.update_dict(fill_mode)
            self.elements['fit_axis'].input.update_dict(fit_axis)
        if self.line_type == 'Balloon':
            for idx in range(1,999):
                if "Header_Text_%d"%idx in self.elements:
                    self.elements["Header_Text_%d"%idx].input.configure(values=['None','Text()']+self.get_avaliable_text(),state='readonly')
                    self.elements['ht_pos_%d'%idx].describe.configure(command=self.select_dot_idx(idx))
                    self.elements['ht_target_%d'%idx].input.update_dict(self.get_avaliable_charcol())
                    self.elements["head_align_%d"%idx].input.update_dict(alignments)
                    self.elements["ht_rotate_%d"%idx].input.configure(from_=-180,to=180,increment=1)
                else:
                    break
            self.update_sep_button()
        if self.line_type == 'ChatWindow':
            self.elements["sub_distance"].input.configure(from_=0,to=1000,increment=10)
            self.elements["sub_pos"].describe.configure(command=lambda :self.select_dot('p0','p1'))
            self.elements["sub_end"].describe.configure(command=lambda :self.select_dot('p0','p2'))
            self.elements["am_left"].describe.configure(command=lambda :self.select_dot('r0','p1'))
            self.elements["am_right"].describe.configure(command=lambda :self.select_dot('r1','p1'))
            for idx in range(1,999):
                if "sub_key_%d"%idx in self.elements:
                    self.elements["sub_Bubble_%d"%idx].input.configure(values=['Bubble()']+self.get_avaliable_bubble(cw=False,bb=False),state='readonly')
                    self.elements["sub_Anime_%d"%idx].input.configure(values=['None']+self.get_avaliable_anime(),state='readonly')
                    self.elements["sub_align_%d"%idx].input.update_dict(chatalign)
                else:
                    break
            self.update_sep_button()
        if self.line_type == 'Animation':
            self.elements['tick'].input.configure(from_=1,to=30,increment=1)
            self.elements['loop'].input.update_dict(True_False)
        if self.line_type == 'Sprite':
            self.elements['tick'].input.configure(from_=1,to=30,increment=1)
            self.elements['blink_mean'].input.configure(from_=0.5,to=10,increment=0.1)
            self.elements['blink_std'].input.configure(from_=0.0,to=3,increment=0.1)
        if self.line_type == 'Audio':
            self.elements['filepath'].bind_button(dtype='soundeff-file',convert=True)
            self.elements['volume'].input.configure(from_=0,to=100,increment=10)
        if self.line_type == 'BGM':
            self.elements['filepath'].bind_button(dtype='BGM-file',convert=True)
            self.elements['volume'].input.configure(from_=0,to=100,increment=10)
            self.elements['loop'].input.update_dict(True_False)
    def struct_2_value(self,section):
        return self.medef_tool.value_export(section)
    def value_2_struct(self, value):
        try:
            return self.medef_tool.value_parser(str(value))
        except SyntaxsError:
            Messagebox().show_error(message=tr('无效的值：{}').format(value),title=tr('错误'),parent=self)
            return value
    def update_preview(self, keywords: list):
        # 更新对象
        ref_medef:MediaDef = self.page.content
        # 检查目前是否有现有对象
        if self.page.preview.object_this:
            try:
                # 尝试重设媒体参数
                for key in keywords:
                    # 使用了MediaDef的value_execute，将字典类型解析为对象
                    exec_value = ref_medef.value_execute(self.section[key])
                    self.page.preview.object_this.configure(key=key,value=exec_value)
            except Exception:
                # 如果在重设媒体参数的时候，发生了异常，移除现有预览媒体，显示错误画面
                # 建议：重新梳理和预览相关的操作的触发流程，并在所有敏感节点添加异常处理！
                self.page.preview.set_error()
            finally:
                # 更新显示
                self.page.preview.update_dotview()
                self.page.preview.update_preview()
        else:
            # 如果之前是无预览媒体，那么重新执行一次预览
            self.page.preview.preview(media_name=self.section_index)
    # 新建一个多项sep
    def update_sep_button(self):
        if self.line_type == 'Balloon':
            MultiSep = 'HeadSep-%d'
        elif self.line_type == 'ChatWindow':
            MultiSep = "SubSep-%d"
        elif self.line_type == 'BezierCurve':
            MultiSep = 'AnchorSep-%d'
        elif self.line_type == 'RichText':
            MultiSep = 'IconifySep-%d'
        else:
            return
        # 定位到最后一个
        for idx in range(1,999):
            if MultiSep%idx in self.seperator:
                # 先清除前面的
                self.seperator[MultiSep%idx].remove_button()
            else:
                # 在最后一个小节建立
                end = idx-1
                self.seperator[MultiSep%end].add_button(text=tr('添加+'),command=self.add_a_sep)
                if end > 1:
                    self.seperator[MultiSep%end].add_button(text=tr('删除-'),command=self.del_a_sep)
                # 结束循环
                self.sep_end = end
                self.multisep = MultiSep
                break
    def add_a_sep(self):
        this_sep:dict = self.TableStruct[self.line_type][self.multisep]
        # 先添加小节分割线 
        sep_new = self.sep_end + 1
        self.seperator[self.multisep%sep_new] = TextSeparator(
            master=self,
            screenzoom=self.sz,
            describe=this_sep['Text']%sep_new
        )
        # 再添加KVD
        for key in this_sep['Content']:
            this_kvd = this_sep['Content'][key]
            if r'%d' in this_kvd['default']:
                value_this = this_kvd['default']%sep_new
            else:
                value_this = this_kvd['default']
            self.elements[key%sep_new] = self.seperator[self.multisep%sep_new].add_element(
                key=key%sep_new,
                value=value_this,
                kvd=this_kvd,
                callback=self.update_section_from
            )
        # 添加内容
        if self.line_type == 'Balloon':
            self.elements["Header_Text_%d"%sep_new].input.configure(values=['None','Text()']+self.get_avaliable_text())
            self.elements['ht_pos_%d'%sep_new].describe.configure(command=self.select_dot_idx(sep_new))
            self.elements['ht_target_%d'%sep_new].input.update_dict(self.get_avaliable_charcol())
            self.elements["head_align_%d"%sep_new].input.update_dict(alignments)
            self.elements["ht_rotate_%d"%sep_new].input.configure(from_=-180,to=180,increment=1)
        elif self.line_type == 'ChatWindow':
            self.elements["sub_Bubble_%d"%sep_new].input.configure(values=['Bubble()']+self.get_avaliable_bubble(cw=False,bb=False),state='readonly')
            self.elements["sub_Anime_%d"%sep_new].input.configure(values=['None']+self.get_avaliable_anime(),state='readonly')
            self.elements["sub_align_%d"%sep_new].input.update_dict(chatalign)
        elif self.line_type == 'BezierCurve':
            # 贝塞尔曲线是特殊的，贝塞尔曲线需要前一个点的方向来延伸下一段线
            end_right_control = self.section['control_right'][-1]
            # TODO: end anchor，有可能是一个引用的pos对象，但是这个地方引用不到，只能强行设置了
            end_anchor = self.section['anchor'][-1]
            if type(end_anchor) is str:
                end_anchor = [300,300]
            end_frame_point = self.section['frame_point'][-1]
            dirction_vec = -np.array(end_right_control)/np.linalg.norm(end_right_control)
            self.elements["control_left_%d"%sep_new].set('({},{})'.format(*(dirction_vec*100).astype(int)))
            self.elements["control_right_%d"%sep_new].set('({},{})'.format(*(-dirction_vec*100).astype(int)))
            self.elements["anchor_%d"%sep_new].set('({},{})'.format(*(end_anchor + dirction_vec*300).astype(int)))
            self.elements["frame_point_%d"%sep_new].set(end_frame_point+30)
            # 正常的属性添加
            self.elements["control_left_%d"%sep_new].describe.configure(command=self.select_dot_idx(sep_new-1,dottype='cl'))
            self.elements['control_right_%d'%sep_new].describe.configure(command=self.select_dot_idx(sep_new-1,dottype='cr'))
            self.elements['anchor_%d'%sep_new].describe.configure(command=self.select_dot_idx(sep_new,dottype='a'))
            self.elements['anchor_%d'%sep_new].input.configure(values=self.get_avaliable_pos(bezier=False))
            self.elements["frame_point_%d"%sep_new].input.configure(from_=0,to=3000,increment=5)
            self.elements["speed_formula_%d"%sep_new].input.update_dict(formulas)
        elif self.line_type == 'RichText':
            self.elements['sub_icon_%d'%sep_new].bind_button(dtype='picture-file')
        # 更新显示
        SZ_10 = int(self.sz * 10)
        SZ_20 = 2*SZ_10
        self.seperator[self.multisep%sep_new].pack(side='top',anchor='n',fill='x',pady=(0,SZ_10),padx=(SZ_10,SZ_20))
        # 更新按钮
        self.update_sep_button()
        # 最后更新小节内容
        self.update_section_from()
        # 移动滚动条
        self.update()
        self.enable_scrolling()
        self.yview_moveto(1.0)
    def del_a_sep(self):
        # 先删除小节内容
        sep_struct:dict = self.TableStruct[self.line_type][self.multisep]['Content']
        for keyword in sep_struct:
            self.elements.pop(keyword%self.sep_end).destroy()
        # 再删除小节分割线
        self.seperator.pop(self.multisep%self.sep_end).destroy()
        # 更新按钮
        self.update_sep_button()
        # 最后更新小节内容
        self.update_section_from()
        # 移动滚动条
        self.update()
        self.enable_scrolling()
        self.yview_moveto(1.0)
    # 选中点
    def select_dot(self, dotID, pID):
        self.page.preview.force_dot(dotID, pID)
    def select_dot_idx(self,idx,dottype='b'):
        def command():
            self.select_dot(dottype+'%d'%idx,'p1')
        return command
    # 重设名字
    def reset_name(self,toast=False):
        self.elements['Name'].value.set(self.section_index)
    # 提醒回车键
    def notice_enter(self,event):
        # 弹出消息提示，Toast
        ToastNotification(
            title=tr('按回车确定'),
            message=tr('如果确认修改媒体名，请按回车键！'),
            duration=1000
        ).show_toast()
class LogEdit(EditWindow):
    def __init__(self, master, screenzoom):
        super().__init__(master, screenzoom)
        self.TableStruct = EditTableStruct['RplGenLog']
    def update_from_section(self,index:str,section: dict, line_type):
        super().update_from_section(index, section, line_type)
        # TODO:各个类型的config
        # 更新
        self.update_item()