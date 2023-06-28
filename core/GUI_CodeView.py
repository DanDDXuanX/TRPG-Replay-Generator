#!/usr/bin/env python
# coding: utf-8

# 代码编辑器视图

import re
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from chlorophyll import CodeView

from .RplGenLogLexer import RplGenLogLexer
from .ScriptParser import RplGenLog, CharTable, MediaDef
from .GUI_Snippets import RGLSnippets

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
        # 添加撤回点
        self.codeview.configure(autoseparators=False)
        self.codeview.edit_separator()
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
        self.codeview.configure(autoseparators=True)
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
        # 添加撤回点
        self.codeview.configure(autoseparators=False)
        self.codeview.edit_separator()
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
        self.codeview.configure(autoseparators=True)
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
        self.codeview.bind('<Alt-Up>',self.swap_lines)
        self.codeview.bind('<Alt-Down>',self.swap_lines)
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
    # 整体移动行
    def swap_lines(self,event):
        # 获取当前行号
        current_line = self.codeview.index("insert").split(".")[0]
        # 判断是上还是下
        if event.keysym == 'Up':
            if current_line == '1':
                return
            else:
                line_to_swap = str(int(current_line)-1)
        elif event.keysym == 'Down':
            last_line = self.codeview.index('end').split(".")[0]
            if current_line == last_line:
                return
            else:
                line_to_swap = str(int(current_line)+1)
        else:
            return
        # 获取文本
        current_line_text = self.codeview.get(f"{current_line}.0", f"{current_line}.end")
        swap_line_text = self.codeview.get(f"{line_to_swap}.0", f"{line_to_swap}.end")
        # 创建撤销点
        self.codeview.edit_separator()
        self.codeview.configure(autoseparators=False)
        # 互换两行的文本
        self.codeview.delete(f"{current_line}.0", f"{current_line}.end")
        self.codeview.insert(f"{current_line}.0", swap_line_text)
        self.codeview.delete(f"{line_to_swap}.0", f"{line_to_swap}.end")
        self.codeview.insert(f"{line_to_swap}.0", current_line_text)
        # 恢复自动撤销点
        self.codeview.configure(autoseparators=True)
        # 更新高亮
        self.codeview.highlight_all()
        # 移动光标
        self.codeview.mark_set("insert", f"{line_to_swap}.0")
        self.codeview.see("insert")
        return "break"