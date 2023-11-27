#!/usr/bin/env python
# coding: utf-8

# 代码编辑器视图

import re
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from chlorophyll import CodeView
from .ProjConfig import preference
from .RplGenLogLexer import RplGenLogLexer
from .ScriptParser import RplGenLog, CharTable, MediaDef
from .StoryImporter import StoryImporter
from .Medias import Audio
from .GUI_Link import Link
from .GUI_Snippets import RGLSnippets, RGLRightClick
from .GUI_PreviewCanvas import RGLPreviewCanvas
from .GUI_DialogWindow import browse_multi_file, browse_file
from .GUI_Util import clear_speech
from .GUI_Language import tr, Localize
from .Extension import auto_duet

# 查找且替换
class SearchReplaceBar(ttk.Frame, Localize):
    language = {
        'en':{
            '查找：': 'Find:',
            '替换：': 'Replace:',
            '正则' : 'Regex',
            '查找' : 'Find',
            '替换' : 'Replace',
            '全部替换' : 'Repl all'
        }
    }
    localize = preference.lang
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
        self.to_find.trace_add('write',callback=self.modify_tofind)
        # 元件
        self.line1 = {
            'label': ttk.Label(master=self,anchor='e',text=self.tr('查找：'),bootstyle='light-inverse',width=8),
            'entry': ttk.Entry(master=self,font=(Link['terminal_font_family'],10),bootstyle='secondary',textvariable=self.to_find),
            'button1': ttk.Checkbutton(master=self,text=self.tr('正则'),bootstyle='secondary-toolbutton',width=7,variable=self.is_regex,takefocus=False,cursor='hand2'),
            'button2': ttk.Button(master=self,text=self.tr('查找'),bootstyle='secondary-outline',width=7,command=self.search,takefocus=False,cursor='hand2'),
        }
        self.bind_key(self.line1['entry'])
        self.line2 = {
            'label': ttk.Label(master=self,anchor='e',text=self.tr('替换：'),bootstyle='light-inverse',width=8),
            'entry': ttk.Entry(master=self,font=(Link['terminal_font_family'],10),bootstyle='secondary',textvariable=self.to_replace),
            'button1': ttk.Button(master=self,text=self.tr('替换'),bootstyle='secondary-outline',width=7,command=self.replace,takefocus=False,cursor='hand2'),
            'button2': ttk.Button(master=self,text=self.tr('全部替换'),bootstyle='secondary-outline',width=7,command=self.replace_all,takefocus=False,cursor='hand2'),
        }
        self.bind_key(self.line2['entry'])
        self.update_item()
    def modify_tofind(self,*args):
        if self.is_searched:
            self.master.clear_search(None)
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
    def check_regex(self,regex_pattern):
        try:
            re.compile(regex_pattern)
            return True
        except re.error:
            return False
    def search(self):
        # 获取参数
        search_text = self.to_find.get()
        is_regex = self.is_regex.get()
        # 清除已有查找
        self.master.clear_search(None)
        start_index = '1.0'
        is_match = False
        # 检查是否可以做（搜索空白会崩溃！非法正则会崩溃！）
        if search_text == '':
            self.line1['entry'].configure(bootstyle='danger')
            return
        if is_regex:
            if self.check_regex(search_text) == False:
                self.line1['entry'].configure(bootstyle='danger')
                return
        while True:
            # 找到下一个匹配的文本
            index = self.codeview.search(search_text, start_index, stopindex='end',regexp=is_regex)
            # 如果找不到，停止搜索
            if index == '':
                break
            else:
                # 有搜索到
                is_match = True
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
                    this_line = int(index.split('.')[0]) - 1
                    line_number = len(self.codeview.get('1.0','end').splitlines())
                    self.codeview.yview_moveto(this_line/line_number)
                # 更新搜索位置
                start_index = end_index
        # 改颜色
        if is_match:
            self.line1['entry'].configure(bootstyle='secondary')
        else:
            self.line1['entry'].configure(bootstyle='danger')
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
        Messagebox().show_info(message=tr('已替换{}处文本。').format(replace_count),title=tr('全部替换'),parent=self.master)
    def bind_key(self,widget:ttk.Entry):
        widget.bind("<Return>", lambda _:self.search())
        widget.bind("<Shift-Return>", lambda _:self.replace_all())
        widget.bind("<KP_Enter>", lambda _:self.search())
        widget.bind("<Shift-KP_Enter>", lambda _:self.replace_all())
        widget.bind("<Escape>", self.master.close_search)
    def update_search(self,text):
        self.to_find.set(text)
    def move_focus(self):
        self.line1['entry'].focus_set()
# 右键预览
class PreviewWindow(ttk.Toplevel):
    def __init__(self,screenzoom,master,rplgenlog:RplGenLog,chartab:CharTable,mediadef:MediaDef,event):
        self.sz = screenzoom
        self.master = master
        SZ_60 = int(self.sz * 60)
        SZ_20 = int(self.sz * 20)
        SZ_2 = int(self.sz*2)
        # 尺寸
        config = Link['project_config']
        win_W = int(self.sz * config.Width / 2)
        win_H = int(self.sz * config.Height / 2)
        size = (win_W + 2*SZ_2, win_H + 2*SZ_2)
        # 位置
        mouse_y = event.y_root + SZ_20
        scr_H = self.master.winfo_screenheight()
        position_x = self.master.winfo_rootx() + SZ_60
        if mouse_y + win_H > scr_H:
            position_y = scr_H - win_H - SZ_60
        else:
            position_y = mouse_y
        # 初始化
        super().__init__(
            resizable           = (False,False),
            size                = size,
            position            = (position_x, position_y),
            overrideredirect    = True,
        )
        self.content = rplgenlog
        self.ref_media = mediadef
        self.ref_chartab = chartab
        self.edit = None # 假装有edit
        # 预览
        self.preview = RGLPreviewCanvas(
            master=self,
            screenzoom=self.sz,
            rplgenlog=self.content,
            mediadef=self.ref_media,
            chartab=self.ref_chartab
            )
        # 执行
        self.update_items()
    def update_items(self):
        self.preview.pack(fill='both',expand=True)
    def preview_line(self,line:int):
        try:
            self.preview.preview(line_index=str(line-1))
        except Exception as E:
            print(E)
            self.preview.show_error()
    def close(self):
        self.destroy() 
# 脚本模式
class RGLCodeViewFrame(ttk.Frame):
    def __init__(self,master,screenzoom,rplgenlog:RplGenLog,chartab:CharTable,mediadef:MediaDef):
        # 继承
        self.sz = screenzoom
        super().__init__(master)
        # 引用的角色和媒体资源
        self.chartab = chartab
        self.mediadef = mediadef
        # 是否存在异常
        self.is_error = False
        # 代码
        self.content:RplGenLog = rplgenlog
        self.codeview = CodeView(
            master      = self,
            lexer       = RplGenLogLexer,
            color_scheme= preference.editer_colorschemes,
            font        = (Link['terminal_font_family'], preference.editer_fontsize),
            undo        = True
        )
        self.codeview.insert("end",self.content.export(allowed_exception=True)) # 插入脚本文本，允许插入异常行
        # 高亮所有异常
        self.hightlight_error()
        # 清除撤回队列
        self.codeview.edit_reset() 
        # 绑定案件
        self.codeview.bind('<Control-Key-f>',self.show_search)
        self.codeview.bind('<Control-Key-s>',self.save_command)
        self.codeview.bind('<Control-Key-r>',self.update_codeview)
        self.codeview.bind('<FocusIn>',self.clear_search)
        self.codeview.bind('<Tab>',self.show_snippets)
        self.codeview.bind('<Alt-Up>',self.swap_lines)
        self.codeview.bind('<Alt-Down>',self.swap_lines)
        self.codeview.bind('<Alt-Return>',self.split_dialog)
        self.codeview.bind('<Button-3>',self.click_right_menu)
        # self.codeview.bind('<Key>',self.on_modified,'+')
        self.is_modified = False
        # self.codeview.bind_class("Text", "<Button-3>", self.click_right_menu,'+')
        # 代码视图
        if preference.theme == 'rplgendark':
            self.codeview._line_numbers.colors=('#dddddd','#2e2e2c')
        else:
            self.codeview._line_numbers.colors=('#2e2e2c','#dddddd')
        self.codeview._line_numbers.set_colors()
        self.codeview._line_numbers.bind('<ButtonRelease-3>',self.click_2_preview,'+')
        self.codeview._line_numbers.bind('<Leave>',self.close_preview,'+')
        self.codeview._line_numbers.configure(borderwidth=0)
        self.codeview._vs.configure(bootstyle='success-round')
        self.codeview._hs.configure(bootstyle='success-round')
        # 搜索高亮
        self.codeview.tag_config('search', background='#904f1e')
        self.codeview.tag_config('preview', background='#0072d6')
        self.codeview.tag_config('error', background='#aa0000')
        # 查找替换
        self.search_replace = SearchReplaceBar(master=self,codeview=self.codeview,screenzoom=self.sz)
        # 预览窗
        self.preview_window = None
        # 显示
        self.matches = []
        self.is_show_search = False
        self.update_item()
    def update_item(self):
        self.codeview.pack(side='top',fill='both',expand=True)
    # 展示、隐藏搜索栏
    def show_search(self,event):
        self.search_replace.pack(side='top',fill='x',expand=False)
        sel_text = self.codeview.get("sel.first", "sel.last")
        if len(sel_text) != 0:
            self.search_replace.update_search(sel_text)
        self.search_replace.move_focus()
        self.is_show_search = True
    def close_search(self,event):
        self.search_replace.pack_forget()
        self.clear_search(None)
        self.codeview.focus_set()
        self.is_show_search = False
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
        # 选中
        self.codeview.tag_add("sel",f"{line_to_swap}.0",f"{line_to_swap}.end")
        # 更新高亮
        self.codeview.highlight_all()
        # 移动光标
        self.codeview.mark_set("insert", f"{line_to_swap}.0")
        self.codeview.see("insert")
        return "break"
    # 预览
    def click_2_preview(self,event):
        self.codeview.tag_remove('preview','1.0','end')
        # 获取当前选中的行号
        preview_line = int(self.codeview.index(f'@{event.x},{event.y}').split('.')[0])
        # 更新结构
        try:
            self.update_rplgenlog()
        except Exception as E:
            Messagebox().show_error(message=re.sub('\x1B\[\d+m','',str(E)),title=tr('错误'),parent=self)
            return
        if self.preview_window is None:
            # 唤起
            self.preview_window = PreviewWindow(
                master=self,
                screenzoom=self.sz,
                rplgenlog=self.content,
                chartab=self.chartab,
                mediadef=self.mediadef,
                event=event
            )
        # 高亮
        self.codeview.tag_add('preview',f'{preview_line}.0',f'{preview_line}.end')
        # 显示
        self.preview_window.preview_line(preview_line)
    def close_preview(self,event):
        self.codeview.tag_remove('preview','1.0','end')
        if self.preview_window:
            self.preview_window.close()
            self.preview_window = None
    # 保存
    def save_command(self,event):
        # 保存
        mainwindow = self.winfo_toplevel()
        # 找到保存项目的命令
        mainwindow.view['project'].file_manager.save_file()
    # 右键
    def click_right_menu(self,event):
        RGLRightClick(master=self.codeview,frame=self,mediadef=self.mediadef,chartab=self.chartab,event=event)
        return "break"
    # 刷新：从log对象重新加载所有文字
    def update_codeview(self,event):
        # 撤回
        self.codeview.edit_separator()
        self.codeview.configure(autoseparators=False)
        # 移除全部文本
        self.codeview.delete("0.0",'end')
        # 插入脚本文本
        self.codeview.insert("end",self.content.export())
        # 清除变更标记
        # self.clear_modified()
        self.codeview.configure(autoseparators=True)
        # 刷新高亮
        self.codeview.highlight_all()
    # 将当前文本更新到RplGenLog
    def update_rplgenlog(self):
        # 将log中，从开头到当前行的内容转为RplGenLog.struct
        code_text = self.codeview.get('0.0','end')
        # 脚本更新到content
        self.content.struct = self.content.parser(code_text,allowed_exception=True)
        # 高亮全部异常
        self.hightlight_error()
        # 如果成功，清除error
        if not self.is_error:
            self.codeview.tag_remove('error','1.0','end')
    # 将对话行分割
    def split_dialog(self,event):
        index_ = self.codeview.index('insert')
        row,col = index_.split('.')
        # 当前行的全部内容
        text_this = self.codeview.get(f'{row}.0', f'{row}.end')
        text_upstream = text_this[:int(col)]
        text_downstream = text_this[int(col):]
        # 检查对话环
        M = re.fullmatch('^(\[[\w\ \.\,\(\)]+\](<\w+(=\d+)>)?:)([^\\"]+)',text_upstream)
        if M:
            # 添加撤回点
            self.codeview.configure(autoseparators=False)
            self.codeview.edit_separator()
            # 用于插入的文本
            insert_snippet = '\n'+M.group(1)
            self.codeview.insert(index_, insert_snippet)
            self.codeview.mark_set("insert",f'{index_}+{len(insert_snippet)}c')
            # 检查是否需要智能逗号
            if preference.auto_periods:
                periods = {'zh':'。','en':'.'}[preference.lang]
                if re.fullmatch('[\w]',text_upstream[-1]):
                    self.codeview.insert(f'{row}.end',periods)
                if re.fullmatch('[,，;；]',text_upstream[-1]):
                    self.codeview.delete(f'{row}.end-1c',f'{row}.end')
                    self.codeview.insert(f'{row}.end',periods)
            self.codeview.highlight_all()
            self.codeview.configure(autoseparators=True)
            return 'break'
        else:
            return '\n'
    # 高亮出错的行
    def hightlight_error(self,E:Exception=None,line:int=None):
        # 初始化错误
        self.is_error = False
        if line:
            errorline = line
            self.is_error = True
            self.codeview.tag_add('error', f"{errorline}.0", f"{errorline}.end")
        # 这一块好像根本没用到
        elif E:
            self.is_error = True
            try:
                if preference.lang == 'zh':
                    errorline = re.findall('.*异常.*第(\d+)行.*',str(E))[0]
                else:
                    errorline = re.findall('.*exception.*in line (\d+).*', str(E))[0]
                self.codeview.tag_add('error', f"{errorline}.0", f"{errorline}.end")
            except:
                pass
            finally:
                print(E)
        # 高亮所有异常
        else:
            for key in self.content.struct:
                if self.content.struct[key]['type'] == 'exception':
                    self.hightlight_error(line=int(key)+1)
        return self.is_error
    # 变更是否同步？TODO：暂时没用
    def on_modified(self,event):
        if self.is_modified:
            pass
        else:
            self.is_modified = True
            name = self.master.page_name
            tab = self.master.master.page_notebook.active_tabs[name]
            tab.set_change('●')
    def clear_modified(self):
        self.is_modified = False
        name = self.master.page_name
        tab = self.master.master.page_notebook.active_tabs[name]
        tab.set_change('x')
    # 添加全部语音合成标记
    def add_asterisk_marks(self):
        # 解析文字
        try:
            self.update_rplgenlog()
        except Exception as E:
            Messagebox().show_error(message=re.sub('\x1B\[\d+m','',str(E)),title=tr('错误'),parent=self)
            return
        # 添加星标
        add_count = 0
        missing_line = []
        for idx in self.content.struct:
            this_section = self.content.struct[idx]
            # 是否是对话行
            if this_section['type'] == 'dialog':
                # 是否已经包含星标
                if '{*}' not in this_section['sound_set'] and '*' not in this_section['sound_set']:
                    # 角色是否有语音
                    main_charactor = this_section['charactor_set']['0']
                    main_name = main_charactor['name']+'.'+main_charactor['subtype']
                    if main_name not in self.chartab.struct:
                        missing_line.append(int(idx)+1)
                    elif self.chartab.struct[main_name]['Voice'] != 'NA':
                        this_section['sound_set']['{*}'] = {"sound": None,"time": None}
                        add_count += 1
        # 更新变更
        self.update_codeview(None)
        # 高亮异常
        for line in missing_line:
            self.hightlight_error(line=line)
        # 消息框
        if add_count == 0:
            Messagebox().show_info(message=tr('没有添加语音合成标记！\n不会给没有指定音源的角色添加语音合成标记。'),title=tr('添加星标'),parent=self)
        else:
            if len(missing_line)==0:
                Messagebox().show_info(message=tr('添加语音合成标记{}个').format(add_count),title='添加星标',parent=self)
            else:
                Messagebox().show_warning(
                    message=tr('添加语音合成标记{add}个\n检查到共{miss}行出现未定义角色！').format(
                        add=add_count,
                        miss=len(missing_line)
                        ),
                    title=tr('添加星标'),
                    parent=self
                    )
    # 移除所有星标
    def remove_asterisk_marks(self,name=None,subtype=None):
        # 解析文字
        try:
            self.update_rplgenlog()
        except Exception as E:
            Messagebox().show_error(message=re.sub('\x1B\[\d+m','',str(E)),title=tr('错误'),parent=self)
            return
        # 目标角色
        target_charactors = self.chartab.get_target(name=name,subtype=subtype)
        # 如果目标是空，就可以结束了
        if len(target_charactors) == 0:
            Messagebox().show_warning(message=tr('指定的角色尚未定义！'),title=tr('移除星标'),parent=self)
            return
        # 移除星标
        remove_asterisk = 0
        remove_voice = 0
        for idx in self.content.struct:
            this_section = self.content.struct[idx]
            # 是否是对话行
            if this_section['type'] == 'dialog':
                main_charactor = this_section['charactor_set']['0']
                main_name = main_charactor['name']+'.'+main_charactor['subtype']
                # 是否是目标角色
                if main_name in target_charactors:
                    if "{*}" in this_section['sound_set']:
                        this_section['sound_set'].pop('{*}')
                        remove_asterisk += 1
                    if '*' in this_section['sound_set']:
                        this_section['sound_set'].pop('*')
                        remove_voice += 1
        # 更新变更
        self.update_codeview(None)
        # 消息框
        if (remove_asterisk+remove_voice) == 0:
            Messagebox().show_warning(message=tr('没有找到需要移除的星标音频或待合成标记！'),title=tr('移除星标'),parent=self)
        else:
            Messagebox().show_info(
                message=tr('移除星标语音{voice}个，\n待合成标记{asterisk}个。').format(
                    voice=remove_voice,
                    asterisk=remove_asterisk
                    ),
                title=tr('移除星标'),
                parent=self
            )
    # 批量导入音频文件
    def fill_asterisk_from_files(self,name=None,subtype=None):
        # 解析文字
        try:
            self.update_rplgenlog()
        except Exception as E:
            Messagebox().show_error(message=re.sub('\x1B\[\d+m','',str(E)),title=tr('错误'),parent=self)
            return
        # 目标角色
        target_charactors = self.chartab.get_target(name=name,subtype=subtype)
        # 如果目标是空，就可以结束了
        if len(target_charactors) == 0:
            Messagebox().show_warning(message=tr('指定的角色尚未定义！'),title=tr('移除星标'),parent=self)
            return
        # 浏览文件
        list_of_files = browse_multi_file(master=self,filetype='soundeff',related=True,convert=True)
        list_of_files.sort() # 升序
        num_of_files = len(list_of_files)
        # 移除星标
        filter_asterisk = 0
        fill_asterisk = 0
        file_used = 0
        for idx in self.content.struct:
            this_section = self.content.struct[idx]
            # 是否是对话行
            if this_section['type'] == 'dialog':
                main_charactor = this_section['charactor_set']['0']
                main_name = main_charactor['name']+'.'+main_charactor['subtype']
                # 是否是目标角色
                if main_name in target_charactors:
                    if "{*}" in this_section['sound_set']:
                        filter_asterisk += 1
                        try:
                            # 取出文件
                            this_file = list_of_files.pop(0)
                            audio_length = round(Audio(this_file).media.get_length(),2)
                            file_used += 1
                        except IndexError:
                            continue
                        this_section['sound_set'].pop('{*}')
                        this_section['sound_set']['*'] = {
                            "sound" : f"'{this_file}'",
                            "time"  : audio_length
                        }
                        fill_asterisk += 1
        # 更新变更
        self.update_codeview(None)
        # 消息框
        if filter_asterisk == 0:
            Messagebox().show_warning(message=tr('没有找到符合过滤条件的待合成标记！'),title=tr('批量导入语音'),parent=self)
        else:
            if name:
                if subtype:
                    target = name+'.'+subtype
                else:
                    target = name
            else:
                target = tr("（全部角色）")
            message = tr('——批量导入语音报告——\n')
            message += tr('目标角色：{target}\n选中的文件数量：{num}\n').format(target=target,num=num_of_files)
            message += tr('目标星标数量：{filter}\n填充的音标数量：{fill}').format(filter=filter_asterisk,fill=fill_asterisk)
            Messagebox().show_info(message=message,title=tr('批量导入语音'),parent=self)
    # 智能导入
    def rgl_intel_import(self):
        # 0. 将尚未保存的编辑内容保存
        try:
            self.update_rplgenlog()
        except Exception as E:
            Messagebox().show_error(message=re.sub('\x1B\[\d+m','',str(E)),title=tr('错误'),parent=self)
            return
        # 1. 载入导入的文本
        target_file = browse_file(master=self, text_obj=tk.StringVar(),method='file',filetype='text',related=False)
        if target_file == '':
            return False
        try:
            load_text = open(target_file,'r',encoding='utf-8').read()
        except UnicodeDecodeError:
            try:
                load_text = open(target_file,'r',encoding='gbk').read()
            except Exception as E:
                Messagebox().show_error(tr('无法解读导入文件的编码！\n请确定导入的是文本文件？'),title=tr('格式错误'),parent=self)
                return False
        except FileNotFoundError:
            Messagebox().show_error(tr('找不到导入的剧本文件，请检查文件名！'),title=tr('找不到文件'),parent=self)
            return False
        # 2. 开始解析
        story = StoryImporter()
        story.load(text=load_text,max_=300) # 限制，在单个log文件中最多导入300句
        # 3. 检查是否解析成功
        if story.log_mode is None:
            Messagebox().show_error(tr('当前着色器无法解析导入文本的结构！'),title=tr('格式错误'),parent=self)
            return False
        # 4. 获取角色
        charinfo = story.get_charinfo()
        # 5. 去除非法的角色
        charinfo = charinfo[-(charinfo['name'].duplicated() + (charinfo['name'] == '') + (charinfo['name'] == '_dup') + (charinfo.index==''))].copy()
        # 6. 注入log
        log_results = story.results
        log_results = log_results[log_results['ID'].map(lambda x:x in charinfo.index)].copy()
        line_index = len(self.content.struct)
        for key,value in log_results.iterrows():
            self.content.struct[str(line_index)] = {
                "type": "dialog",
                "charactor_set": {
                    "0": {
                        "name": charinfo['name'][value['ID']],
                        "subtype": "default",
                        "alpha": None
                    }
                },
                "ab_method": {
                    "method": "default",
                    "method_dur": "default"
                },
                "content": clear_speech(value['speech']),
                "tx_method": {
                    "method": "default",
                    "method_dur": "default"
                },
                "sound_set": {}
            }
            line_index += 1
        self.update_codeview(None)
        # 7. 添加角色 # TODO
    # 拓展功能
    def auto_duet(self):
        # 0. 将尚未保存的编辑内容保存
        try:
            self.update_rplgenlog()
        except Exception as E:
            Messagebox().show_error(message=re.sub('\x1B\[\d+m','',str(E)),title=tr('错误'),parent=self)
            return
        # 1. 执行
        auto_duet(rgl=self.content,mdf=self.mediadef,ctb=self.chartab)
        # 2. 刷新
        self.update_codeview(None)