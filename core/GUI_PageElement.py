#!/usr/bin/env python
# coding: utf-8

# 页面的其他公用元件
# 包含：搜索栏、输出命令按钮

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
import threading
import pygame
import re
from PIL import Image, ImageTk
from chlorophyll import CodeView
from .RplGenLogLexer import RplGenLogLexer
from .GUI_Snippets import RGLSnippets
from .GUI_Container import Container
from .OutputType import PreviewDisplay, ExportVideo, ExportXML
from .ScriptParser import RplGenLog, CharTable, MediaDef
from .Medias import MediaObj

# 搜索窗口
class SearchBar(ttk.Frame):
    def __init__(self,master,container:Container,screenzoom):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=int(5*self.sz))
        # 关联容器
        self.container = container
        # 元件
        self.search_text = tk.StringVar(master=self,value='')
        self.is_regex = tk.BooleanVar(master=self,value=False)
        self.left = {
            'entry' : ttk.Entry(master=self,width=30,textvariable=self.search_text),
            'regex' : ttk.Checkbutton(master=self, text='正则', variable=self.is_regex),
            'search' : ttk.Button(master=self,text='搜索',command=self.click_search,bootstyle='primary')
        }
        self.right = {
            'clear' : ttk.Button(master=self,text='清除',command=self.click_clear),
            'info'  : ttk.Label(master=self,text='(无)'),
        }
        self.update_item()
    def update_item(self):
        SZ_10 = int(self.sz * 10)
        for key in self.left:
            item:ttk.Button = self.left[key]
            item.pack(padx=SZ_10, fill='y',side='left')
        for key in self.right:
            item:ttk.Button = self.right[key]
            item.pack(padx=SZ_10, fill='y',side='right')
    def click_search(self):
        if self.is_regex.get():
            self.right['info'].config(text = '正则搜索：'+self.search_text.get())
        else:
            self.right['info'].config(text = '搜索：'+self.search_text.get())
        # 搜索与显示过滤
        self.container.search(to_search=self.search_text.get(),regex=self.is_regex.get())
    def click_clear(self):
        self.right['info'].config(text = '(无)')
        self.container.search(to_search='')
# 输出指令
class OutPutCommand(ttk.Frame):
    def __init__(self,master,screenzoom):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='light')
        # 引用
        self.page = self.master
        icon_size = [int(30*self.sz),int(30*self.sz)]
        self.image = {
            'display'   : ImageTk.PhotoImage(name='display',image=Image.open('./media/icon/display.png').resize(icon_size)),
            'exportpr'    : ImageTk.PhotoImage(name='exportpr', image=Image.open('./media/icon/premiere.png').resize(icon_size)),
            'recode'   : ImageTk.PhotoImage(name='recode',image=Image.open('./media/icon/ffmpeg.png').resize(icon_size)),
        }
        self.buttons = {
            'display' : ttk.Button(master=self,image='display',text='播放预览',compound='left',style='output.TButton',command=lambda:self.open_new_thread('display')),
            'export'  : ttk.Button(master=self,image='exportpr',text='导出PR工程',compound='left',style='output.TButton',command=lambda:self.open_new_thread('exportpr')),
            'recode'  : ttk.Button(master=self,image='recode',text='导出视频',compound='left',style='output.TButton',command=lambda:self.open_new_thread('recode')),
        }
        self.runing_thread = None
        self.update_item()
        
    def update_item(self):
        for key in self.buttons:
            item:ttk.Button = self.buttons[key]
            item.pack(fill='both',side='left',expand=True,pady=0)
    def load_input(self):
        # 项目配置
        self.pconfig = self.page.ref_config
        # 脚本
        self.medef = self.page.ref_medef.copy()
        self.chartab = self.page.ref_chartab.copy()
        self.rplgenlog = self.page.content.copy()
        try:
            # 初始化配置项
            self.pconfig.execute()
            # 初始化媒体
            self.medef.execute()
            # 初始化角色表
            self.chartab.execute()
            # 初始化log文件
            self.rplgenlog.execute(media_define=self.medef,char_table=self.chartab,config=self.pconfig)
        except Exception as E:
            print(E)
    def preview_display(self):
        self.load_input()
        try:
            PreviewDisplay(rplgenlog=self.rplgenlog,config=self.pconfig,output_path='./test_output')
        except Exception as E:
            print(E)
        finally:
            pygame.init()
            pygame.font.init()
            self.winfo_toplevel().navigate_bar.enable_navigate()
    def export_video(self):
        try:
            self.load_input()
            ExportVideo(rplgenlog=self.rplgenlog,config=self.pconfig,output_path='./test_output')
        except Exception as E:
            print(E)
        finally:
            pygame.init()
            pygame.font.init()
            self.winfo_toplevel().navigate_bar.enable_navigate()
    def export_xml(self):
        try:
            # 调整全局变量
            MediaObj.export_xml = True
            MediaObj.output_path = './test_output'
            self.load_input()
            ExportXML(rplgenlog=self.rplgenlog,config=self.pconfig,output_path='./test_output')
        except Exception as E:
            print(E)
        finally:
            # 复原全局变量
            pygame.init()
            pygame.font.init()
            MediaObj.export_xml = False
            self.winfo_toplevel().navigate_bar.enable_navigate()
    def open_new_thread(self,output_type:str):
        # 先切换到终端页
        self.winfo_toplevel().navigate_bar.press_button('console')
        self.winfo_toplevel().navigate_bar.disable_navigate()
        # 检查是否有正在执行的
        if self.runing_thread is None:
            pass
        elif self.runing_thread.is_alive():
            print("正在执行中")
            return
        # 新建线程：FIXME：重复两次开始预览播放，可能导致闪退，考虑改为多进程。
        if output_type == 'display':
            self.runing_thread = threading.Thread(target=self.preview_display)
        elif output_type == 'exportpr':
            self.runing_thread = threading.Thread(target=self.export_xml)
        elif output_type == 'recode':
            self.runing_thread = threading.Thread(target=self.export_video)
        else:
            self.runing_thread = threading.Thread(target=lambda:print("无效的执行"))
        # 开始执行
        self.runing_thread.start()
# 查找且替换
class SearchReplaceBar(ttk.Frame):
    def __init__(self,master,codeview,screenzoom):
        # 缩放尺度
        self.sz = screenzoom
        SZ_5 = int(self.sz * 3)
        super().__init__(master,borderwidth=int(5*self.sz),bootstyle='light',padding=(0,0,SZ_5,0))
        # 绑定的代码
        self.codeview:CodeView = codeview
        # 变量
        self.is_regex = tk.BooleanVar(master=self,value=False)
        self.to_find = tk.StringVar(master=self,value='')
        self.to_replace = tk.StringVar(master=self,value='')
        # 元件
        self.line1 = {
            'label': ttk.Label(master=self,anchor='e',text='查找：',bootstyle='light-inverse',width=8),
            'entry': ttk.Entry(master=self,font=('Sarasa Mono SC',10),bootstyle='secondary',textvariable=self.to_find),
            'button1': ttk.Checkbutton(master=self,text='正则',bootstyle='secondary-toolbutton',width=7,variable=self.is_regex),
            'button2': ttk.Button(master=self,text='查找',bootstyle='secondary-outline',width=7,command=self.search),
        }
        self.line2 = {
            'label': ttk.Label(master=self,anchor='e',text='替换：',bootstyle='light-inverse',width=8),
            'entry': ttk.Entry(master=self,font=('Sarasa Mono SC',10),bootstyle='secondary',textvariable=self.to_replace),
            'button1': ttk.Button(master=self,text='替换',bootstyle='secondary-outline',width=7,command=self.replace),
            'button2': ttk.Button(master=self,text='全部替换',bootstyle='secondary-outline',width=7,command=self.replace_all),
        }
        self.update_item()
    def update_item(self):
        SZ_5 = int(self.sz * 3)
        SZ_3 = int(self.sz * 2)
        # 第二列填充
        self.columnconfigure(1,weight=1)
        for row,line_dict in enumerate([self.line1,self.line2]):
            for col, keyword in enumerate(line_dict):
                widget:ttk.Entry = line_dict[keyword]
                widget.grid(row=row,column=col,padx=SZ_3,pady=SZ_5,sticky='ew')
    def regex_match_end(self,search_text,index)->tuple:
        # 正则最多匹配300字
        minimal_match = False
        for i in range(1,300):
            end_index = f'{index}+{i}c'
            text_this = self.codeview.get(index,end_index)
            M = re.fullmatch(search_text,text_this)
            # 最小匹配
            if M:
                minimal_match = True
            # 最大匹配
            elif minimal_match:
                break
        # 最后结局：i-1
        end_index = f'{index}+{i-1}c'
        text_this = self.codeview.get(index,end_index)
        M = re.fullmatch(search_text,text_this)
        return end_index, M
    def regex_replace_result(self,replace_text:str,match:re.Match)->str:
        match_group_re = re.compile('\$\d+')
        Matches = match
        # 美元组
        dollar_groups = match_group_re.findall(replace_text)
        new_text = replace_text
        # $1 -> match_group(1)
        for dollar in dollar_groups:
            # 每次只替换一次！
            new_text = new_text.replace(
                dollar,
                Matches.group(int(dollar[1:])),
                1
                )
        return new_text
    def search(self):
        # 获取参数
        search_text = self.to_find.get()
        is_regex = self.is_regex.get()
        # 清除已有查找
        self.master.clear_search(None)
        start_index = '1.0'
        while True:
            # 找到下一个匹配的文本
            index = self.codeview.search(search_text, start_index, stopindex='end',regexp=is_regex)
            # 如果找不到，停止搜索
            if index == '':
                break
            else:
                if is_regex:
                    end_index = self.regex_match_end(search_text=search_text,index=index)[0]
                else:
                    end_index = f'{index}+{len(search_text)}c'
                # 高亮找到的文本
                self.codeview.tag_add('search', index, end_index)
                # 在第一次搜索到的时候
                if self.is_searched == False:
                    self.is_searched = True
                    # 移动到第一个匹配的的位置
                    this_line = int(index.split('.')[0])
                    line_number = len(self.codeview.get('1.0','end').splitlines())
                    self.codeview.yview_moveto(this_line/line_number)
                # 更新搜索位置
                start_index = end_index
    def replace(self):
        # 如果还没搜索，先搜索，不替换
        if self.is_searched == False:
            self.search()
            return
        # 获取参数
        search_text = self.to_find.get()
        replace_text = self.to_replace.get()
        is_regex = self.is_regex.get()
        # 获取当前光标位置
        start_index = '1.0'
        # 执行一次
        index = self.codeview.search(search_text, start_index, stopindex='end',regexp=is_regex)
        # If the search text is not found, stop searching
        if index == '':
            pass
        else:
            if is_regex:
                end_index, Match = self.regex_match_end(search_text=search_text,index=index)
                # 替换文本
                self.codeview.delete(index, end_index)
                self.codeview.insert(index, self.regex_replace_result(replace_text, Match))
            else:
                end_index = f'{index}+{len(search_text)}c'
                # 替换文本
                self.codeview.delete(index, end_index)
                self.codeview.insert(index, replace_text)
        # 更新代码高亮
        self.codeview.highlight_all()
    def replace_all(self):
        # 如果还没搜索，先搜索，不替换
        if self.is_searched == False:
            self.search()
            return
        # 获取参数
        search_text = self.to_find.get()
        replace_text = self.to_replace.get()
        is_regex = self.is_regex.get()
        # 获取当前光标位置
        start_index = '1.0'
        # 计数
        replace_count = 0
        while True:
            # 全部执行
            index = self.codeview.search(search_text, start_index, stopindex='end',regexp=is_regex)
            # 如果找不到，退出循环
            if index == '':
                break
            else:
                if is_regex:
                    end_index, Match = self.regex_match_end(search_text=search_text,index=index)
                    # 替换文本
                    self.codeview.delete(index, end_index)
                    self.codeview.insert(index, self.regex_replace_result(replace_text, Match))
                else:
                    end_index = f'{index}+{len(search_text)}c'
                    # 替换文本
                    self.codeview.delete(index, end_index)
                    self.codeview.insert(index, replace_text)
                # 更新
                start_index = end_index
                replace_count += 1
        # 更新代码高亮
        self.codeview.highlight_all()
        # 弹出消息
        Messagebox().show_info(message=f'已替换{str(replace_count)}处文本。',title='全部替换',parent=self.master)
# 脚本模式
class RGLCodeViewFrame(ttk.Frame):
    def __init__(self,master,screenzoom,rplgenlog:RplGenLog,chartab:CharTable,mediadef:MediaDef):
        # 继承
        self.sz = screenzoom
        super().__init__(master)
        # 引用的角色和媒体资源
        self.chartab = chartab
        self.mediadef = mediadef
        # 代码
        self.content:RplGenLog = rplgenlog
        self.codeview = CodeView(master=self, lexer=RplGenLogLexer, color_scheme="monokai", font=('Sarasa Mono SC',12), undo=True)
        self.codeview.insert("end",self.content.export()) # 插入脚本文本
        self.codeview.bind('<Control-Key-f>',self.show_search)
        self.codeview.bind('<FocusIn>',self.clear_search)
        self.codeview.bind('<Tab>',self.show_snippets)
        # 搜索高亮
        self.codeview.tag_config('search', background='#904f1e')
        # 查找替换
        self.search_replace = SearchReplaceBar(master=self,codeview=self.codeview,screenzoom=self.sz)
        # 显示
        self.matches = []
        self.is_show_search = False
        self.update_item()
    def update_item(self):
        self.codeview.pack(side='top',fill='both',expand=True)
    # 展示、隐藏搜索栏
    def show_search(self,event):
        if self.is_show_search:
            self.search_replace.pack_forget()
            self.clear_search(None)
        else:
            self.search_replace.pack(side='top',fill='x',expand=False)
        self.is_show_search = not self.is_show_search
    # 清除所有搜索高亮
    def clear_search(self,event):
        self.matches = []
        self.codeview.tag_remove('search','1.0','end')
        self.search_replace.is_searched = False
    # 显示代码自动补全
    def show_snippets(self,event):
        RGLSnippets(master=self.codeview,mediadef=self.mediadef,chartab=self.chartab)
        return "break"
