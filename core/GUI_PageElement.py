#!/usr/bin/env python
# coding: utf-8

# 页面的其他公用元件
# 包含：搜索栏、输出命令按钮

import os
import tkinter as tk
import ttkbootstrap as ttk
import threading
import pygame
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.toast import ToastNotification
from PIL import Image, ImageTk
from .GUI_Container import Container
from .GUI_TableStruct import NewElement
from .GUI_Language import tr
from .GUI_DialogWindow import browse_multi_file
from .GUI_CustomDialog import selection_query
from .OutputType import PreviewDisplay, ExportVideo, ExportXML
from .SpeechSynth import SpeechSynthesizer
from .Medias import MediaObj
from .Utils import extract_valid_variable_name
from .ScriptParser import Script
from .FilePaths import Filepath
from .GUI_Link import Link
from .GUI_Util import FreeToolTip
from .ProjConfig import preference
from .Utils import readable_timestamp

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
            'regex' : ttk.Checkbutton(master=self, text=tr('正则'), bootstyle='round-toggle', variable=self.is_regex,cursor='hand2'),
            'search' : ttk.Button(master=self,text=tr('搜索'),command=self.click_search,bootstyle='primary',cursor='hand2')
        }
        self.right = {
            'clear' : ttk.Button(master=self,text=tr('清除'),command=self.click_clear,cursor='hand2'),
            'info'  : ttk.Label(master=self,text=tr('(无)')),
        }
        self.update_item()
    def update_item(self):
        SZ_5 = int(self.sz * 5)
        for key in self.left:
            item:ttk.Button = self.left[key]
            item.pack(padx=[SZ_5,0], fill='y',side='left')
        for key in self.right:
            item:ttk.Button = self.right[key]
            item.pack(padx=[0,SZ_5], fill='y',side='right')
    def click_search(self):
        if self.is_regex.get():
            self.right['info'].config(text = tr('正则','搜索','：') +self.search_text.get())
        else:
            self.right['info'].config(text = tr('搜索','：')+self.search_text.get())
        # 搜索与显示过滤
        self.container.search(to_search=self.search_text.get(),regex=self.is_regex.get())
    def click_clear(self):
        self.right['info'].config(text = tr('(无)'))
        self.container.search(to_search='')
# 输出指令
class OutPutCommand(ttk.Frame):
    def __init__(self,master,screenzoom):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='light')
        # 引用
        self.page = self.master
        self.name = self.page.page_name.lstrip(tr('剧本')+'-')
        icon_size = [int(30*self.sz),int(30*self.sz)]
        self.image = {
            'display'   : ImageTk.PhotoImage(name='display',image=Image.open('./assets/icon/display.png').resize(icon_size)),
            'synth'     : ImageTk.PhotoImage(name='synth',image=Image.open('./assets/icon/synth.png').resize(icon_size)),
            'exportpr'  : ImageTk.PhotoImage(name='exportpr', image=Image.open('./assets/icon/premiere.png').resize(icon_size)),
            'recode'    : ImageTk.PhotoImage(name='recode',image=Image.open('./assets/icon/ffmpeg.png').resize(icon_size)),
        }
        self.buttons = {
            'display'   : ttk.Button(master=self,image='display',text=tr('播放预览'),compound='left',style='output.TButton',command=lambda:self.open_new_thread('display'),cursor='hand2'),
            'synth'     : ttk.Button(master=self,image='synth',text=tr('语音合成'),compound='left',style='output.TButton',command=lambda:self.open_new_thread('synth'),cursor='hand2'),
            'exportpr'    : ttk.Button(master=self,image='exportpr',text=tr('导出PR项目'),compound='left',style='output.TButton',command=lambda:self.open_new_thread('exportpr'),cursor='hand2'),
            'recode'    : ttk.Button(master=self,image='recode',text=tr('导出视频'),compound='left',style='output.TButton',command=lambda:self.open_new_thread('recode'),cursor='hand2'),
        }
        # 音效
        self.toastSE = pygame.mixer.Sound('./assets/SE_toast.wav')
        # 退出状态
        self.status = {
            'zh':{
                0 : '正常',
                1 : '异常',
                2 : '终止',
                3 : '初始化'
            },
            'en':{
                0 : 'Normal',
                1 : 'Error',
                2 : 'Terminated',
                3 : 'Initialize'
            }
        }[preference.lang]
        # 线程
        self.runing_thread = None
        self.update_item()
    def update_item(self):
        for key in self.buttons:
            item:ttk.Button = self.buttons[key]
            # TODO：临时禁用
            item.configure(state='disable')
            item.pack(fill='both',side='left',expand=True,pady=0)
    def load_input(self):
        # 项目配置
        self.pconfig = Link['project_config']
        # 脚本
        self.medef = self.page.ref_medef.copy()
        self.chartab = self.page.ref_chartab.copy()
        self.rplgenlog = self.page.content.copy()
        # 初始化配置项
        self.pconfig.execute()
        # 初始化媒体
        self.medef.execute()
        # 初始化角色表
        self.chartab.execute()
        # 初始化log文件
        self.rplgenlog.execute(media_define=self.medef,char_table=self.chartab,config=self.pconfig)
    def preview_display(self):
        exit_status = 3
        try:
            # 载入
            self.load_input()
            # 初始化
            Link['pipeline'] = PreviewDisplay(
                rplgenlog   = self.rplgenlog,
                config      = self.pconfig,
                title       = self.page.page_name
            )
            # 启用终止按钮
            Link['terminal_control'].configure(state='normal')
            # 执行
            exit_status = Link['pipeline'].main()
            # 返回
            self.after(500,self.return_project)
        except Exception as E:
            print(E)
        finally:
            # 重置
            pygame.init()
            pygame.font.init()
            pygame.mixer.init()
            Link['pipeline'] = None
            Link['terminal_control'].configure(state='disable')
            self.winfo_toplevel().navigate_bar.enable_navigate()
            self.show_toast(
                message=tr('【{core}】执行完毕\n退出状态是：【{status}】').format(
                    core=tr('播放预览'),
                    status=self.status[exit_status]
                ),
                notice=False
            )
    def synth_speech(self):
        exit_status = 3
        # 项目配置
        self.pconfig = Link['project_config']
        # 脚本
        self.medef = self.page.ref_medef.copy()
        self.chartab = self.page.ref_chartab.copy()
        # 注意，log不是copy，是实质上要修改内容的！
        self.rplgenlog = self.page.content
        # 输出路径
        output_path = Link['media_dir'] + 'voice/'
        # 检查输出路径是否存在
        if not os.path.isdir(output_path):
            os.makedirs(output_path)
        try:
            # 初始化
            Link['pipeline'] = SpeechSynthesizer(
                rplgenlog   = self.rplgenlog,
                chartab     = self.chartab,
                mediadef    = self.medef,
                config      = self.pconfig,
                output_path = output_path
            )
            # 启用终止按钮
            Link['terminal_control'].configure(state='normal')
            # 执行
            exit_status = Link['pipeline'].main()
            # 上传用量报文
            preference.post_usage()
            # 返回
            self.after(500,self.return_project)
        except Exception as E:
            print(E)
        finally:
            Link['pipeline'] = None
            Link['terminal_control'].configure(state='disable')
            self.winfo_toplevel().navigate_bar.enable_navigate()
            self.show_toast(
                message=tr('【{core}】执行完毕\n退出状态是：【{status}】').format(
                    core=tr('语音合成'),
                    status=self.status[exit_status]
                )
            )
    def export_video(self):
        exit_status = 3
        try:
            # 载入
            timestamp = readable_timestamp()
            self.load_input()
            # 初始化
            Link['pipeline'] = ExportVideo(
                rplgenlog   = self.rplgenlog,
                config      = self.pconfig,
                output_path = Link['media_dir'],
                key         = f"{self.name}_{timestamp}"
            )
            # 启用终止按钮
            Link['terminal_control'].configure(state='normal')
            # 执行
            exit_status = Link['pipeline'].main()
            # 返回
            self.after(500,self.return_project)
        except Exception as E:
            print(E)
        finally:
            # 重置
            pygame.init()
            pygame.font.init()
            pygame.mixer.init()
            Link['pipeline'] = None
            Link['terminal_control'].configure(state='disable')
            self.winfo_toplevel().navigate_bar.enable_navigate()
            self.show_toast(
                message=tr('【{core}】执行完毕\n退出状态是：【{status}】').format(
                    core=tr('导出视频'),
                    status=self.status[exit_status]
                )
            )
    def export_xml(self):
        exit_status = 3
        try:
            # 调整全局变量
            timestamp = readable_timestamp()
            MediaObj.export_xml = True
            MediaObj.output_path = Link['media_dir'] + f"{self.name}_{timestamp}/"
            # 检查输出路径是否存在（大多是时候都是不存在的）
            if not os.path.isdir(MediaObj.output_path):
                os.makedirs(MediaObj.output_path)
            # 载入
            self.load_input()
            # 初始化
            Link['pipeline'] = ExportXML(
                rplgenlog   = self.rplgenlog,
                config      = self.pconfig,
                output_path = Link['media_dir'],
                key         = f"{self.name}_{timestamp}"
            )
            # 启用终止按钮
            Link['terminal_control'].configure(state='normal')
            # 执行
            exit_status = Link['pipeline'].main()
            # 返回
            self.after(500,self.return_project)
        except Exception as E:
            print(E)
        finally:
            # 重置
            pygame.init()
            pygame.font.init()
            pygame.mixer.init()
            MediaObj.export_xml = False
            Link['pipeline'] = None
            Link['terminal_control'].configure(state='disable')
            self.winfo_toplevel().navigate_bar.enable_navigate()
            self.show_toast(
                message=tr('【{core}】执行完毕\n退出状态是：【{status}】').format(
                    core=tr('导出PR项目'),
                    status=self.status[exit_status]
                )
            )
    def open_new_thread(self,output_type:str):
        # 先切换到终端页
        self.winfo_toplevel().navigate_bar.press_button('console')
        self.winfo_toplevel().navigate_bar.disable_navigate()
        # 检查是否有正在执行的
        if self.runing_thread is None:
            pass
        elif self.runing_thread.is_alive():
            print(tr("正在执行中"))
            self.winfo_toplevel().navigate_bar.enable_navigate()
            return
        # 新建线程
        if output_type == 'display':
            self.runing_thread = threading.Thread(target=self.preview_display)
        elif output_type == 'synth':
            self.runing_thread = threading.Thread(target=self.synth_speech)
        elif output_type == 'exportpr':
            self.runing_thread = threading.Thread(target=self.export_xml)
        elif output_type == 'recode':
            self.runing_thread = threading.Thread(target=self.export_video)
        else:
            self.runing_thread = threading.Thread(target=lambda:print(tr("无效的执行")))
        # 开始执行
        self.runing_thread.start()
        Link['runing_thread'] = self.runing_thread
    def return_project(self):
        self.winfo_toplevel().navigate_bar.press_button('project',force=True)
    def show_toast(self,message,notice=True):
        # 弹出消息提示，Toast
        ToastNotification(
            title=tr('核心退出'),
            message=message,
            duration=5000
        ).show_toast()
        # 播放吐司机音效
        if notice:
            self.toastSE.play()

class VerticalOutputCommand(OutPutCommand):
    def __init__(self,master,screenzoom,codeview):
        # 继承
        super().__init__(master=master,screenzoom=screenzoom)
        SZ_5 = int(self.sz * 5)
        # 额外的按钮
        icon_size = [int(30*self.sz),int(30*self.sz)]
        # 图片
        self.image['asterisk_add'] = ImageTk.PhotoImage(image=Image.open('./assets/icon/asterisk_add.png').resize(icon_size))
        self.image['asterisk_import'] = ImageTk.PhotoImage(image=Image.open('./assets/icon/asterisk_import.png').resize(icon_size))
        self.image['asterisk_del'] = ImageTk.PhotoImage(image=Image.open('./assets/icon/asterisk_del.png').resize(icon_size))
        self.image['intel_import'] = ImageTk.PhotoImage(image=Image.open('./assets/icon/intel_import.png').resize(icon_size))
        self.side_button = {
            'asterisk_add'   : ttk.Button(master=self,image=self.image['asterisk_add'],bootstyle='secondary',command=self.add_asterisk_marks,padding=SZ_5,cursor='hand2'),
            'asterisk_import': ttk.Button(master=self,image=self.image['asterisk_import'],bootstyle='secondary',command=self.fill_asterisk_from_files,padding=SZ_5,cursor='hand2'),
            'asterisk_del'   : ttk.Button(master=self,image=self.image['asterisk_del'],bootstyle='danger',command=self.del_asterisk_marks,padding=SZ_5,cursor='hand2'),
            'sep1'           : ttk.Separator(master=self), # --------------------------
            'intel_import'   : ttk.Button(master=self,image=self.image['intel_import'],bootstyle='secondary',command=self.rgl_intel_import,padding=SZ_5,cursor='hand2'),
        }
        # 小贴士
        self.tooltip = {
            'display'        : FreeToolTip(widget=self.buttons['display'],bootstyle='primary-inverse',text=tr('播放预览'),screenzoom=self.sz,side='left'),
            'synth'          : FreeToolTip(widget=self.buttons['synth'],bootstyle='primary-inverse',text=tr('语音合成'),screenzoom=self.sz,side='left'),
            'exportpr'       : FreeToolTip(widget=self.buttons['exportpr'],bootstyle='primary-inverse',text=tr('导出PR项目'),screenzoom=self.sz,side='left'),
            'recode'         : FreeToolTip(widget=self.buttons['recode'],bootstyle='primary-inverse',text=tr('导出视频'),screenzoom=self.sz,side='left'),
            'asterisk_add'   : FreeToolTip(widget=self.side_button['asterisk_add'],bootstyle='secondary-inverse',text=tr('添加语音合成标记'),screenzoom=self.sz,side='left'),
            'asterisk_import': FreeToolTip(widget=self.side_button['asterisk_import'],bootstyle='secondary-inverse',text=tr('批量导入外部语音文件'),screenzoom=self.sz,side='left'),
            'asterisk_del'   : FreeToolTip(widget=self.side_button['asterisk_del'],bootstyle='danger-inverse',text=tr('移除星标语音'),screenzoom=self.sz,side='left'),
            'intel_import'   : FreeToolTip(widget=self.side_button['intel_import'],bootstyle='secondary-inverse',text=tr('智能导入剧本'),screenzoom=self.sz,side='left'),
        }
        self.update_side_button()
        self.configure(borderwidth=SZ_5,bootstyle='light')
        # 引用的codeview
        self.codeview = codeview
        # 要有边框
        for keyword in self.buttons:
            self.buttons[keyword].configure(text='',compound='center',padding=SZ_5)
    def update_item(self):
        SZ_5 = int(self.sz * 5)
        for key in self.buttons:
            item:ttk.Button = self.buttons[key]
            item.pack(fill='x',anchor='n',side='top',pady=(0,SZ_5))
    def update_side_button(self):
        SZ_5 = int(self.sz * 5)
        for key in self.side_button:
            item:ttk.Button = self.side_button[key]
            item.pack(fill='x',anchor='n',side='bottom',pady=(SZ_5,0))
    def validate_rgl_syntax(self):
        # 更新rgl
        self.codeview.update_rplgenlog()
        # 如果log中存在错误！
        if self.codeview.is_error:
            # 重新启用
            Link['terminal_control'].configure(state='disable')
            self.winfo_toplevel().navigate_bar.enable_navigate()
            return False
        else:
            return True
    # 因为垂直输出命令，涉及的是CodeView，因此在导出前应该添加：将CodeView的内容更新到RGL，并尝试自动保存
    def preview_display(self):
        if self.validate_rgl_syntax():
            # self.codeview.save_command(None) # 预览播放不自动保存
            return super().preview_display()
        else:
            return 
    def export_video(self):
        if self.validate_rgl_syntax():
            self.codeview.save_command(None)
            return super().export_video()
        else:
            return 
    def export_xml(self):
        if self.validate_rgl_syntax():
            self.codeview.save_command(None)
            return super().export_xml()
        else:
            return
    # 因为语音合成涉及到RGL的改变，因此执行成功之后，应该返回给RGL对象，并更新给CodeView！
    def synth_speech(self):
        if self.validate_rgl_syntax():
            super().synth_speech()
            # 更新codeview
            self.codeview.update_codeview(None)
            self.codeview.save_command(None)
            return 
        else:
            return
    # 对整个文件操作，添加语音合成标记
    def add_asterisk_marks(self):
        self.codeview.add_asterisk_marks()
    # 目标角色询问
    def target_charactor_query(self,title:str)->tuple:
        "弹出询问框，让用户选择目标角色。返回name,subtypes"
        # 获取名字
        all_names = self.master.ref_chartab.get_names()
        name_dict = {value:value for value in [tr('（全部）')]+all_names}
        name_choice = selection_query(
            master  = self.master,
            screenzoom  = self.sz,
            prompt  = tr('目标角色（Name）是？'),
            title   = title,
            choice  = name_dict,
            init    = tr('（全部）')
        )
        if name_choice == tr('（全部）'):
            return None,None
        elif name_choice == None:
            return 
        else:
            all_subtype = self.master.ref_chartab.get_subtype(name=name_choice)
            subtype_dict = {value:value for value in [tr('（全部）')]+all_subtype}
            subtype_choice = selection_query(
                master  = self.master,
                screenzoom  = self.sz,
                prompt  = tr('目标差分（Subtype）是？'),
                title   = title,
                choice  = subtype_dict,
                init    = tr('（全部）')
            )
            if subtype_choice == tr('（全部）'):
                return name_choice,None
            elif subtype_choice == None:
                return
            else:
                return name_choice,subtype_choice
    def del_asterisk_marks(self):
        # 获取名字
        try:
            name_choice,subtype_choice = self.target_charactor_query(title=tr('移除星标语音'))
            self.codeview.remove_asterisk_marks(name=name_choice,subtype=subtype_choice)
        except TypeError: # cannot unpack non-iterable NoneType object
            return
    def fill_asterisk_from_files(self):
        # 获取名字
        try:
            name_choice,subtype_choice = self.target_charactor_query(title=tr('批量导入语音'))
            self.codeview.fill_asterisk_from_files(name=name_choice,subtype=subtype_choice)
        except TypeError: # cannot unpack non-iterable NoneType object
            return
    # 智能导入
    def rgl_intel_import(self):
        self.codeview.rgl_intel_import()
# 新建指令
class NewElementCommand(ttk.Frame):
    struct = NewElement
    def __init__(self,master,screenzoom,pagetype):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='light')
        # 引用
        self.page = self.master
        self.container = self.page.container
        self.pagetype = pagetype
        self.section_struct = self.struct[self.pagetype]
        # 初始化的容器
        self.image = {}
        self.buttons = {}
        self.buttons_tooltip = {}
        # 载入表结构
        self.init_buttons()
        self.update_item()
    def init_buttons(self):
        icon_size = [int(30*self.sz),int(30*self.sz)]
        for keyword in self.section_struct:
            button_this = self.section_struct[keyword]
            # 新建按钮绑定的命令
            new_element = self.create_command(button_this=button_this,keyword=keyword)
            batch_new_element = self.create_media_inbatch_command(keyword=keyword)
            # 按钮
            if self.pagetype in ['charactor','Pos']:
                button_left = new_element
                button_right = batch_new_element
            else:
                button_left = batch_new_element
                button_right = new_element
            self.image[keyword] = ImageTk.PhotoImage(image=Image.open(button_this['icon']).resize(icon_size))
            self.buttons[keyword] = ttk.Button(
                master=self,
                # image='display',
                text=button_this['text'],
                image=self.image[keyword],
                compound='left',
                style='output.TButton',
                width=5,
                command=None,
                cursor='hand2'
            )
            self.buttons[keyword].bind('<ButtonRelease-1>', button_left)
            self.buttons[keyword].bind('<ButtonRelease-3>', button_right)
            self.buttons_tooltip[keyword] = FreeToolTip(
                widget=self.buttons[keyword],
                text=button_this['tooltip'],
                bootstyle='secondary-inverse',
                screenzoom=self.sz,
                side='up'
            )
    # 生成按钮命令的闭包
    def create_command(self,button_this,keyword):
        def command(event=None):
            if self.pagetype == 'charactor':
                name_this = self.container.name
                element_name = self.page.content.new_subtype(name=name_this,subtype=tr('新建差分'))
            elif self.pagetype in Script.Media_type:
                if preference.lang == 'zh':
                    new_name = '新建'+button_this['text']
                else:
                    new_name = 'New_' + button_this['text']
                element_name = self.page.content.new_element(name=new_name,element_type=keyword)
            else:
                return
            # 新建原件
            self.container.new_section(key=element_name)
        return command
    # 从文件批量新建媒体的闭包
    def create_media_inbatch_command(self,keyword):
        def command(event=None):
            if self.pagetype == 'charactor':
                return
            if self.pagetype == 'Pos':
                return
            elif self.pagetype == 'Text':
                filetype = 'fontfile'
            elif self.pagetype == 'Audio':
                if event.widget.cget('text') in ['背景音乐','BGM']:
                    filetype = 'BGM'
                else:
                    filetype = 'soundeff'
            elif self.pagetype == 'Animation':
                filetype = 'animate'
            else:
                filetype = 'picture'
            # 开始建立
            list_of_file = browse_multi_file(master=self.page,filetype=filetype,related=True,convert=True)
            for filepath in list_of_file:
                name = extract_valid_variable_name(Filepath(filepath,check_exist=False).prefix())
                # 后端：新建对象
                if filetype == 'fontfile':
                    element_name = self.page.content.new_element(name=name, element_type=keyword, fontfile=filepath)
                else:
                    element_name = self.page.content.new_element(name=name, element_type=keyword, filepath=filepath, convert=True)
                # 前端：新建原件
                self.container.new_section(key=element_name)
        return command
    def update_item(self):
        for key in self.buttons:
            item:ttk.Button = self.buttons[key]
            item.pack(fill='both',side='left',expand=True,pady=0)