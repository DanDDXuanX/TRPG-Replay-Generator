#!/usr/bin/env python
# coding: utf-8

# 容器，文件页面的元素之一。
# 包含：可滚动的容器和对应的小节元素

import numpy as np
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs import Messagebox

from .GUI_SectionElement import MDFSectionElement, CTBSectionElement, RGLSectionElement
from .ScriptParser import MediaDef, CharTable, RplGenLog

# 容纳内容的滚动Frame
class Container(ScrolledFrame):
    element_clipboard = {}
    element_clipboard_source = None
    def __init__(self,master,content,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master, padding=3, bootstyle='light', autohide=True)
        self.page = master
        self.preview_canvas = self.page.preview
        self.edit_window = self.page.edit
        self.vscroll.config(bootstyle='primary-round')
        self.container.config(bootstyle='light',takefocus=True)
        # 按键绑定
        self.container.bind('<Control-Key-a>',lambda event:self.select_range(event,index=False),"+")
        self.container.bind('<Control-Key-c>',lambda event:self.copy_element(event),"+")
        self.container.bind('<Control-Key-v>',lambda event:self.paste_element(event,key=self.selected[0]),"+")
        self.container.bind('<Up>',lambda event:self.select_up(event),"+")
        self.container.bind('<Down>',lambda event:self.select_down(event),"+")
        self.container.bind('<Delete>',lambda event:self.del_select(event),"+")
        # 容器高度
        self.container_height = 0
        # 内容物
        self.content = content
        # 容器内的元件，顺序
        self.element = {}
        self.element_keys = []
        # 当前条件过滤的对象
        self.display_filter:list = []
        # 当前显示内容的列表记录
        self.display_recode:list = []
        # 当前选中的对象
        self.selected:list = []
    # 容器的高度
    def get_container_height(self)->int:
        return 0
    def reset_container_height(self):
        # 重设容器高度：# BUG：会导致闪烁！
        this_height = self.get_container_height()
        if self.container_height != this_height:
            self.config(height=this_height)
            self.container_height = this_height
            self.enable_scrolling()
    # 刷新容器内位置
    def place_item(self,key,idx):
        # 待重载
        pass
    def update_item(self,to_update=None):
        if to_update is None:
            for ele in self.element_keys:
                self.element[ele].place_forget()
            for idx,key in enumerate(self.display_filter):
                self.place_item(key, idx)
        else:
            for ele in to_update:
                self.element[ele].place_forget()
                self.place_item(ele, self.display_filter.index(ele))
    # 选择项目
    def select_item(self,event,index,add=False):
        self.container.focus_set()
        # 根据点击的y，定位本次选中的
        selected_idx = index
        if selected_idx in self.element_keys:
        # if selected_idx in self.element.keys():
            if add is not True:
                # 先清空选中的列表
                for idx in self.selected:
                    self.element[idx].drop_select()
                self.selected.clear()
            # 添加本次选中的
            if index not in self.selected:
                self.element[selected_idx].get_select()
                self.selected.append(selected_idx)
            # 尝试预览
            self.preview_select()
    def select_up(self,event):
        # top 顶部，初始值是所有元素的总长度
        top = len(self.element_keys)
        # 找到当前选中的所有元素的顶部
        for sele in self.selected:
            idx_this = self.element_keys.index(sele)
            if idx_this < top:
                top = idx_this
        if top == len(self.element_keys):
            pass
        elif top == 0:
            self.select_item(None,self.element_keys[0])
        else:
            self.select_item(None,self.element_keys[top-1])
    def select_down(self,event):
        # top 顶部，初始值是-1
        bottom = -1
        # 找到当前选中的所有元素的顶部
        for sele in self.selected:
            idx_this = self.element_keys.index(sele)
            if idx_this > bottom:
                bottom = idx_this
        if bottom == -1:
            pass
        elif bottom == len(self.element_keys)-1:
            self.select_item(None,self.element_keys[-1])
        else:
            self.select_item(None,self.element_keys[bottom+1])
    def select_range(self,event,index:str):
        self.container.focus_set()
        if index == False:
            # effect_range = self.element.keys()
            effect_range = self.display_filter
        else:
            # 上一个选中的，数字序号
            # last_selected_idx:int = int(self.selected[-1]) # 最后一个
            last_selected_idx:int = self.display_filter.index(self.selected[-1])
            # 本次选中的，数字序号
            this_selected_idx:int = self.display_filter.index(index)
            # this_selected_idx:int = int(index)
            # 正序或是倒序
            if this_selected_idx > last_selected_idx:
                effect_range = [self.display_filter[idx] for idx in range(last_selected_idx+1, this_selected_idx+1)]
            else:
                effect_range = [self.display_filter[idx] for idx in range(this_selected_idx, last_selected_idx)]
            # range(this_selected_idx,last_selected_idx,{True:1,False:-1}[last_selected_idx>=this_selected_idx])
        # 先清除所有已选择，再重新选择：不应该在这里操作
        # self.selected.clear()
        for idx in effect_range:
            if idx not in self.selected:
                self.select_item(event=event,index=str(idx),add=True)
    # 预览
    def preview_select(self):
        if len(self.selected) == 1:
            to_preview = self.selected[0]
            try:
                self.edit_select(to_preview)
                self.preview_canvas.preview(to_preview)
            except Exception as E:
                Messagebox().show_error(message=str(E),title='预览错误')
    def edit_select(self,to_preview):
        self.edit_window.update_from_section(index=to_preview, section=self.content.struct[to_preview])
    # 删除项目
    def reindex(self):
        # 重新设置序号，正常是不需要的
        # 待RGL类重载
        pass
    def del_select(self,event):
        # TODO：将发生了变更的页面，x变成o，需要把这个事件传递给 GUI.TabPage.TabNote.set_change()
        self.page.is_modified = True
        for sele in self.selected:
            # 删除section_element
            self.element_keys.remove(sele)
            self.display_filter.remove(sele)
            self.element.pop(sele).destroy()
            self.content.delete(sele)
        self.selected.clear()
        self.reindex()
        self.update_item()
        self.reset_container_height()
    # 搜索筛选
    def search(self,to_search,regex=False):
        if to_search == '':
            is_match = self.element_keys.copy()
        else:
            is_match = []
            for ele in self.element_keys:
                if self.element[ele].rearch_is_match(to_search, regex):
                    is_match.append(ele)
        self.display_filter = is_match
        self.update_item()
        self.reset_container_height()
    def reset_search(self):
        self.page.searchbar.click_clear()
    # 复制项目
    def copy_element(self,event):
        self.__class__.element_clipboard.clear()
        self.__class__.element_clipboard_source = self
        for sele in self.selected:
            self.__class__.element_clipboard[sele] = self.content.struct[sele].copy()
    # 黏贴项目
    def paste_element(self,event,key:str,ahead=True):
        # 是否是筛选状态？重置筛选！
        if self.display_filter != self.element_keys:
            self.reset_search()
        # 待重载
class RGLContainer(Container):
    def __init__(self,master,content:RplGenLog,screenzoom):
        # 初始化基类
        super().__init__(master=master,content=content,screenzoom=screenzoom)
        # 按键绑定
        self.container.bind('<Control-Up>',lambda event:self.move(event,up=True),"+")
        self.container.bind('<Control-Down>',lambda event:self.move(event,up=False),"+")
        # 遍历内容物，新建元件
        for key in self.content.struct:
            this_section = self.content.struct[key]
            self.element_keys.append(key)
            self.element[key] = self.new_element(key=key,section=this_section)
        # 将内容物元件显示出来
        self.display_filter = self.element_keys.copy()
        self.update_item()
        self.reset_container_height()
    def new_element(self,key:str,section:dict)->RGLSectionElement:
        return RGLSectionElement(
                master=self,
                bootstyle='primary',
                text=key,
                section=section,
                screenzoom=self.sz)
    def get_container_height(self) -> int:
        return int(60*self.sz)*len(self.display_filter)
    def reindex(self):
        new_element_keys = [str(x) for x in range(0,len(self.element_keys))]
        new_element:dict = {}
        new_display_filter = []
        for idx,ele in enumerate(self.element_keys):
            this_new = new_element_keys[idx]
            new_element[this_new] = self.element[ele]
            new_element[this_new].update_index(this_new)
            # 是否在当前显示过滤器中
            if ele in self.display_filter:
                new_display_filter.append(this_new)
        # 更新
        self.element = new_element
        self.element_keys = new_element_keys
        self.display_filter = new_display_filter
        self.content.reindex()
        return 1
    # 移动小节
    def exchange(self,key1:str,key2:str):
        # 变更element
        self.element[key1], self.element[key2] = self.element[key2], self.element[key1]
        self.element[key1].update_index(key1)
        self.element[key2].update_index(key2)
        # 变更content
        self.content.exchange(key1,key2)
        self.update_item(to_update=[key1,key2])
    def move(self,event,up=True)->bool:
        # 只能选中1个
        if len(self.selected)!=1:
            return False
        else:
            key = self.selected[0]
        # 不能有筛选过滤器
        if self.display_filter != self.element_keys:
            return False
        else:
            idx = self.element_keys.index(key)
        # 开头不能上移，结尾不能下移
        if up == True:
            if key == self.element_keys[0]:
                return False
            else:
                self.exchange(key1=self.element_keys[idx],key2=self.element_keys[idx-1])
                self.select_item(None,self.element_keys[idx-1])
                return True
        else:
            if key == self.element_keys[-1]:
                return False
            else:
                self.exchange(key1=self.element_keys[idx],key2=self.element_keys[idx+1])
                self.select_item(None,self.element_keys[idx+1])
                return True
    def place_item(self,key,idx):
        SZ_60 = int(self.sz * 60)
        SZ_55 = int(self.sz * 55)
        sz_10 = int(self.sz * 10)
        this_section_frame:RGLSectionElement = self.element[key]
        this_section_frame.place(x=0,y=idx*SZ_60,width=-sz_10,height=SZ_55,relwidth=1)
    def copy_element(self, event):
        super().copy_element(event)
        # 写入剪贴板
        self.clipboard_clear()
        self.clipboard_append(RplGenLog(dict_input=RGLContainer.element_clipboard).export())
    def paste_element(self, event, key: str, ahead=True):
        super().paste_element(event, key, ahead)
        insert_index = self.element_keys.index(key)
        insert_length = len(RGLContainer.element_clipboard.keys())
        # 要在插入之前预留好空间
        if ahead:
            # |0|1|2|3|
            move_index = range(len(self.element_keys)-1,insert_index-1,-1)
        else:
            # 不位移insert_index
            move_index = range(len(self.element_keys)-1,insert_index,-1)
        for idx in move_index:
            # element
            self.element[str(idx+insert_length)] = self.element[str(idx)]
            self.element[str(idx+insert_length)].update_index(str(idx+insert_length))
            # content
            self.content.add(key=str(idx+insert_length), section=self.content.struct[str(idx)])
        # 插入
        for idx,ele in enumerate(RGLContainer.element_clipboard.keys()):
            # insert_pos
            if ahead:
                ele_key = str(insert_index + idx)
            else:
                ele_key = str(insert_index + 1 + idx)
            # section
            section = RGLContainer.element_clipboard[ele].copy()
            # element
            self.element[ele_key] = self.new_element(key=ele_key,section=section)
            # contene
            self.content.add(ele_key, section)
        # elementkey
        self.element_keys = [str(x) for x in range(0,len(self.element))]
        # display
        self.display_filter = self.element_keys.copy()
        # 更新选中的index
        self.selected.clear()
        if ahead:
            self.select_item(None,str(insert_index+insert_length))
        else:
            self.select_item(None,key)
        # 更新显示
        self.update_item()
        self.reset_container_height()
class MDFContainer(Container):
    def __init__(self,master,content:MediaDef,typelist:list,screenzoom):
        # 初始化基类
        super().__init__(master=master,content=content,screenzoom=screenzoom)
        # 遍历内容物，新建元件
        for key in self.content.struct:
            this_section = self.content.struct[key]
            if this_section['type'] not in typelist:
                continue
            self.element_keys.append(key)
            self.element[key] = self.new_element(key=key,section=this_section)
        # 根据内容物，调整容器总高度
        # self.config(height=int(200*self.sz*np.ceil(len(self.element_keys)/3)))
        # 将内容物元件显示出来
        self.display_filter = self.element_keys.copy()
        self.update_item()
        self.reset_container_height()
    def new_element(self,key:str,section:dict)->MDFSectionElement:
        return MDFSectionElement(
            master=self,
            bootstyle='secondary',
            text=key,
            section=section,
            screenzoom=self.sz)
    def get_container_height(self) -> int:
        return int(200*self.sz*np.ceil(len(self.display_filter)/3))
    def place_item(self,key,idx):
        SZ_100 = int(self.sz * 200)
        SZ_95 = int(self.sz * 190)
        sz_10 = int(self.sz * 10)
        this_section_frame:MDFSectionElement = self.element[key]
        this_section_frame.place(relx=idx%3 * 0.33,y=idx//3*SZ_100,width=-sz_10,height=SZ_95,relwidth=0.33)
    def edit_select(self,to_preview):
        section_2_preview:dict = self.content.struct[to_preview]
        self.edit_window.update_from_section(index=to_preview, section=section_2_preview, line_type=section_2_preview['type'])
    def copy_element(self, event):
        super().copy_element(event)
        # 写入剪贴板
        self.clipboard_clear()
        self.clipboard_append(MediaDef(dict_input=MDFContainer.element_clipboard).export())
    def paste_element(self, event, key: str, ahead=True):
        super().paste_element(event, key, ahead)
        idx = self.element_keys.index(key)
        if MDFContainer.element_clipboard_source != self:
            Messagebox().show_warning(message='复制的内容无法黏贴到这个页面！',title='类型不正确')
        else:
            for ele in MDFContainer.element_clipboard.keys():
                # 不可以使用重名
                ele_key = ele
                while ele_key in self.element_keys:
                    ele_key = ele_key+'_cp'
                # section
                section = MDFContainer.element_clipboard[ele].copy()
                # element
                self.element[ele_key] = self.new_element(key=ele_key,section=section)
                # contene
                self.content.add(ele_key, section)
                # elementkey
                if ahead:
                    self.element_keys.insert(idx, ele_key)
                else:
                    self.element_keys.insert(idx+1, ele_key)
                # display
                self.display_filter = self.element_keys.copy()
        # 更新显示
        self.update_item()
        self.reset_container_height()
class CTBContainer(Container):
    def __init__(self,master,content:CharTable,name:str,screenzoom):
        # 初始化基类
        super().__init__(master=master,content=content,screenzoom=screenzoom)
        self.name:str = name
        # 可引用对象
        self.ref_medef = self.master.master.ref_medef
        # 遍历内容物，新建元件
        for key in self.content.struct:
            this_section = self.content.struct[key]
            if this_section['Name'] != self.name:
                continue
            self.element_keys.append(key)
            self.element[key] = self.new_element(key=key,section=this_section)
        # 根据内容物，调整容器总高度
        # self.config(height=int(100*self.sz*len(self.element_keys)))
        # 将内容物元件显示出来
        self.display_filter = self.element_keys.copy()
        self.update_item()
        self.reset_container_height()
    def new_element(self,key:str,section:dict)->CTBSectionElement:
        return CTBSectionElement(
                master=self,
                bootstyle='primary',
                text=key,
                section=section,
                screenzoom=self.sz
                )
    def get_container_height(self) -> int:
        return int(100*self.sz*len(self.display_filter))
    def place_item(self,key,idx):
        SZ_100 = int(self.sz * 100)
        SZ_95 = int(self.sz * 95)
        sz_10 = int(self.sz * 10)
        this_section_frame:CTBSectionElement = self.element[key]
        this_section_frame.place(x=0,y=idx*SZ_100,width=-sz_10,height=SZ_95,relwidth=1)
    def copy_element(self, event):
        super().copy_element(event)
        # 写入剪贴板
        self.clipboard_clear()
        self.clipboard_append(CharTable(dict_input=CTBContainer.element_clipboard).export().to_csv(sep='\t',index=False,encoding='utf-8').replace('\r',''))
    def paste_element(self, event, key: str, ahead=True):
        super().paste_element(event, key, ahead)
        idx = self.element_keys.index(key)
        for ele in CTBContainer.element_clipboard.keys():
            # 不可以使用重名
            name,subtype = ele.split('.')
            if name!=self.name:
                ele_key = self.name+'.'+subtype
            else:
                ele_key = ele
            while ele_key in self.element_keys:
                ele_key = ele_key+'_cp'
            # section
            section = CTBContainer.element_clipboard[ele].copy()
            section['Name'] = self.name
            # element
            self.element[ele_key] = self.new_element(key=ele_key,section=section)
            # contene
            self.content.add(ele_key, section)
            # elementkey
            if ahead:
                self.element_keys.insert(idx, ele_key)
            else:
                self.element_keys.insert(idx+1, ele_key)
            # display
            self.display_filter = self.element_keys.copy()
        # 更新显示
        self.update_item()
        self.reset_container_height()