#!/usr/bin/env python
# coding: utf-8

# 新建空白项目，新建智能项目的窗口
import os
import json
import tkinter as tk
import ttkbootstrap as ttk
from pathlib import Path
from ttkbootstrap.dialogs import Dialog, Messagebox, MessageCatalog
from PIL import Image, ImageTk
from .GUI_Util import KeyValueDescribe, thumbnail
from .GUI_TableStruct import ProjectTableStruct

class CreateProject(ttk.Frame):
    table_struct = {}
    def __init__(self,master,screenzoom,close_func):
        # 缩放尺度
        self.sz = screenzoom
        SZ_5 = int(5*self.sz)
        super().__init__(master,borderwidth=SZ_5)
        # 退出函数
        self.close_func = close_func
        # 结构
        self.seperator = {}
        self.elements = {}
        self.comfirm_button = ttk.Button(master=self,text='确定',bootstyle='primary',command=self.confirm,width=10)
        self.build_struct()
        self.update_item()
    def build_struct(self):
        for sep in self.table_struct:
            this_sep = self.table_struct[sep]
            self.seperator[sep] = ttk.LabelFrame(master=self,text=this_sep['Text'])
            for keyword in this_sep['Content']:
                this_kwd = this_sep['Content'][keyword]
                self.elements[keyword] = KeyValueDescribe(
                    master=self.seperator[sep],
                    screenzoom=self.sz,
                    key=this_kwd['ktext'],
                    value={
                        'type':this_kwd['vtype'],
                        'style':this_kwd['vitem'],
                        'value':this_kwd['default']
                    },
                    describe={
                        "type":this_kwd['ditem'],
                        "text":this_kwd['dtext']
                    },
                    tooltip=this_kwd['tooltip']
                )
    def update_item(self):
        SZ_5 = int(5*self.sz)
        SZ_3 = int(3*self.sz)
        for key in self.seperator:
            item = self.seperator[key]
            item.pack(side='top',anchor='n',fill='x',pady=(0,SZ_5),padx=(SZ_5,SZ_5))
        for key in self.elements:
            item = self.elements[key]
            item.pack(side='top',anchor='n',fill='x',pady=(0,SZ_5))
        # 确认键
        self.comfirm_button.pack(side='top',anchor='center',expand=False,pady=SZ_5,ipady=SZ_3)
    def clear_item(self):
        for key in self.elements:
            item:KeyValueDescribe = self.elements[key]
            item.destroy()
        for key in self.seperator:
            item = self.seperator[key]
            item.destroy()
        self.elements.clear()
        self.seperator.clear()
    def confirm(self):
        pass

# 新建空白项目
class CreateEmptyProject(CreateProject):
    # 原件：
    # 1. 基本（项目名称、项目封面、位置）
    # 2. 视频（分辨率、帧率）
    # 3. 图层（图层顺序）
    table_struct = ProjectTableStruct['EmptyProject']
    video_preset = {
        '自定义':   None,
        '横屏-高清 (1920x1080, 30fps)'  : [1920, 1080, 30],
        '横屏-标清（1280x720, 30fps)'   : [1280, 720, 30],
        '竖屏-高清 (1080x1920, 30fps)'  : [1080, 1920, 30],
        '竖屏-标清（720x1280, 30fps）'   : [720, 1280, 30],
        '横屏-高清 (1920x1080, 25fps)'  : [1920, 1080, 25],
        '横屏-标清 (1280x720, 25fps)'   : [1280, 720, 25],
    }
    zorder_preset = {
        '自定义'    :None,
        '背景->立绘->气泡'  : "BG2,BG1,Am3,Am2,Am1,AmS,Bb,BbS",
        '背景->气泡->立绘'  : "BG2,BG1,Bb,BbS,Am3,Am2,Am1,AmS"
    }
    def build_struct(self):
        super().build_struct()
        # 绑定功能
        self.elements['proj_cover'].bind_button(dtype='picture-file',quote=False,related=False)
        self.elements['save_pos'].bind_button(dtype='dir',quote=False,related=False)
        self.elements['preset_video'].input.configure(values=list(self.video_preset.keys()), state='readonly')
        self.elements['preset_layer'].input.configure(values=list(self.zorder_preset.keys()), state='readonly')
        self.elements['preset_video'].input.bind('<<ComboboxSelected>>', self.update_preset,'+')
        self.elements['preset_layer'].input.bind('<<ComboboxSelected>>', self.update_preset,'+')
        self.update_preset(None)
    def update_preset(self,event):
        video_preset_args = self.video_preset[self.elements['preset_video'].get()]
        zorder_preset_args = self.zorder_preset[self.elements['preset_layer'].get()]
        if video_preset_args:
            W,H,F = video_preset_args
            # 修改值
            self.elements['video_width'].value.set(W)
            self.elements['video_height'].value.set(H)
            self.elements['frame_rate'].value.set(F)
            # 设置参数为仅只读
            self.elements['video_width'].input.configure(state='disabled')
            self.elements['video_height'].input.configure(state='disabled')
            self.elements['frame_rate'].input.configure(state='disabled')
        else:
            # 如果是自定义，则启用编辑
            self.elements['video_width'].input.configure(state='normal')
            self.elements['video_height'].input.configure(state='normal')
            self.elements['frame_rate'].input.configure(state='normal')
        if zorder_preset_args:
            self.elements['layer_zorder'].value.set(zorder_preset_args)
            self.elements['layer_zorder'].input.configure(state='disabled')
        else:
            self.elements['layer_zorder'].input.configure(state='normal')
    def confirm(self):
        W = int(self.elements['video_width'].get())
        H = int(self.elements['video_height'].get())
        F = int(self.elements['frame_rate'].get())
        Z = self.elements['layer_zorder'].get().split(',')
        cover_path = self.elements['proj_cover'].get()
        save_dir = self.elements['save_pos'].get()
        file_name = self.elements['proj_name'].get()
        save_path = save_dir + '/' + file_name + '.rgpj'
        if save_dir == '':
            Messagebox().show_error(title='错误',message='必须要选择一个文件夹用于保存项目文件！',parent=self)
            return False
        # 检查合法性
        if W<0 or H<0 or F<0:
            Messagebox().show_error(title='错误',message='分辨率或帧率是非法的数值！',parent=self)
            return False
        for symbol in ['/','\\',':','*','?','"','<','>','|']:
            if symbol in file_name:
                Messagebox().show_error(title='错误',message=f'文件名中不能包含符号 {symbol} ！',parent=self)
                return False
        # 如果文件已经存在
        if os.path.isfile(save_path):
            choice = Messagebox().okcancel(title='文件已存在',message='目录下已经存在重名的项目文件，要覆盖吗？',parent=self)
            if choice != MessageCatalog.translate('OK'):
                return False
        # 新建项目结构
        new_project_struct = {
            'config':{
                'Name'          : file_name,
                'Cover'         : cover_path,
                'Width'         : W,
                'Height'        : H,
                'frame_rate'    : F,
                'Zorder'        : Z,
            },
            'mediadef':{},
            'chartab':{},
            'logfile':{}
        }
        # 保存文件
        try:
            # 建立项目文件
            with open(save_path,'w',encoding='utf-8') as of:
                of.write(json.dumps(new_project_struct,indent=4))
            # 建立项目资源目录
            try:
                os.makedirs(save_dir + '/' + file_name)
            except FileExistsError:
                pass
            # 退出
            self.close_func(save_path)
        except:
            Messagebox().show_error(title='错误',message=f'无法保存文件到：\n{save_path}')
            return False
# 新建智能项目
class CreateIntelProject(CreateProject):
    table_struct = ProjectTableStruct['IntelProject']
    def __init__(self, master, screenzoom, close_func):
        self.frame_metainfo = None
        self.intel_dir = './intel/'
        super().__init__(master, screenzoom, close_func)
    def build_struct(self):
        super().build_struct()
        # 绑定功能
        self.elements['proj_cover'].bind_button(dtype='picture-file',quote=False,related=False)
        self.elements['save_pos'].bind_button(dtype='dir',quote=False,related=False)
        self.elements['textfile'].bind_button(dtype='logfile-file',quote=False,related=False)
        self.elements['section_break'].input.configure(values=[0,100,300,1000,3000,10000,30000],state='readonly')
        # TODO: 浏览资源文件夹，并指定给self.element['template']
        self.elements['template'].input.bind('<<ComboboxSelected>>', self.template_selected,'+')
        # 从预设文件夹获取
        intels = os.listdir(self.intel_dir)
        self.elements['template'].input.configure(values=intels,state='readonly')
        # 添加进度条
        self.progress = ttk.Progressbar(master=self.seperator['LogSep'],maximum=1.0,value=0.5,bootstyle='primary-striped')
        self.elements['progress'] = self.progress
    def load_template(self,tplt_name):
        SZ_5 = int(self.sz * 5)
        tplt_path = self.intel_dir + tplt_name + '/' + tplt_name + '.rgint'
        self.template:dict = json.load(open(tplt_path,'r',encoding='utf-8'))
        # meta
        self.frame_metainfo = ttk.Frame(master=self.seperator['TpltSep'],borderwidth=0)
        ttk.Separator(master=self.frame_metainfo,bootstyle='secondary',orient='horizontal').pack(fill='x',side='top',pady=SZ_5)
        # thumbnail
        sep_w = self.seperator['TpltSep'].winfo_width() - SZ_5 *2
        thumbnail_size = (sep_w,int(sep_w/16*9)) # 16:9
        self.tplt_cover = ImageTk.PhotoImage(
            image=Image.open(self.template['meta']['cover']).resize(thumbnail_size)
        )
        # info
        self.metainfo = {
            'cover'     : ttk.Label(master=self.frame_metainfo,image=self.tplt_cover),
            'describe'  : ttk.Label(master=self.frame_metainfo,text='简介：{}'.format(self.template['meta']['describe'])),
            'author'    : ttk.Label(master=self.frame_metainfo,text='作者：{}'.format(self.template['meta']['author'])),
            'licence'   : ttk.Label(master=self.frame_metainfo,text='授权：{}'.format(self.template['meta']['licence'])),
        }
        # 显示
        for item in self.metainfo:
            self.metainfo[item].pack(fill='x',side='top',padx=SZ_5)
        # 返回
        return self.frame_metainfo
    def template_selected(self,event):
        if self.frame_metainfo:
            self.frame_metainfo.destroy()
            # self.frame_metainfo.pack_forget()
        try:
            self.load_template(self.elements['template'].get())
            self.frame_metainfo.pack(fill='x',side='top',pady=(0,int(self.sz*5)))
        except Exception as E:
            self.elements['template'].set("")
            raise Exception()
    def confirm(self):
        # TODO：将预设项目的资源文件复制到输出目录
        pass
# 项目配置
class ConfigureProject(CreateEmptyProject):
    def __init__(self, master, screenzoom, close_func, proj_config, file_path):
        # 项目配置对象
        self.proj_config = proj_config
        self.file_path = file_path
        super().__init__(master, screenzoom, close_func)
    def build_struct(self):
        super().build_struct()
        # 额外变更：保存项目的按钮和输入框应该禁用
        self.elements['save_pos'].describe.configure(state='disable')
        self.elements['save_pos'].input.configure(state='disable')
        # 载入预设
        self.load_config()
    def load_config(self):
        # 设置值
        if self.file_path:
            Dir = Path(self.file_path).parent.absolute()
        else:
            Dir = '<尚未保存的项目！>'
        Name = self.proj_config['Name']
        Cover = self.proj_config['Cover']
        W = self.proj_config['Width']
        H = self.proj_config['Height']
        F = self.proj_config['frame_rate']
        Z = ','.join(self.proj_config['Zorder'])
        self.elements['proj_cover'].value.set(Cover)
        self.elements['save_pos'].value.set(Dir)
        self.elements['proj_name'].value.set(Name)
        self.elements['video_width'].value.set(W)
        self.elements['video_height'].value.set(H)
        self.elements['frame_rate'].value.set(F)
        self.elements['layer_zorder'].value.set(Z)
        # 检查是否是预设
        for keyword in self.video_preset:
            if [W,H,F] == self.video_preset[keyword]:
                self.elements['preset_video'].value.set(keyword)
                break
            else:
                self.elements['preset_video'].value.set('自定义')
        for keyword in self.zorder_preset:
            if Z == self.zorder_preset[keyword]:
                self.elements['preset_layer'].value.set(keyword)
                break
            else:
                self.elements['preset_layer'].value.set('自定义')
        # 更新预设
        self.update_preset(None)
    def confirm(self):
        W = int(self.elements['video_width'].get())
        H = int(self.elements['video_height'].get())
        F = int(self.elements['frame_rate'].get())
        Z = self.elements['layer_zorder'].get().split(',')
        file_name = self.elements['proj_name'].get()
        cover_path = self.elements['proj_cover'].get()
        # 检查合法性
        if W<0 or H<0 or F<0:
            Messagebox().show_warning(title='警告',message='分辨率或帧率是非法的数值！')
            return False
        for symbol in ['/','\\',':','*','?','"','<','>','|']:
            if symbol in file_name:
                Messagebox().show_warning(title='警告',message=f'项目名中不能包含符号 {symbol} ！')
                return False
        # 新建项目结构
        new_config_struct = {
            'Name'          : file_name,
            'Cover'         : cover_path,
            'Width'         : W,
            'Height'        : H,
            'frame_rate'    : F,
            'Zorder'        : Z,
        }
        # 退出值是项目的结构！
        self.close_func(new_config_struct)
# 对话框
class CreateProjectDialog(Dialog):
    def __init__(self, screenzoom, parent=None, ptype='Empty', **kw_args):
        if ptype == 'Intel':
            super().__init__(parent, '新建智能项目', alert=False)
        elif ptype == 'Config':
            super().__init__(parent, '项目设置', alert=False)
            self.proj_configure = kw_args['config']
            self.file_path = kw_args['file_path']
        else:
            super().__init__(parent, '新建空白项目', alert=False)
        self.sz = screenzoom
        self.ptype = ptype
    def close_dialog(self,result=None):
        self._result = result
        self._toplevel.destroy()
    def create_body(self, master):
        if self.ptype == 'Intel':
            self.create_project = CreateIntelProject(
                master = master,
                screenzoom = self.sz,
                close_func=self.close_dialog,
            )
        elif self.ptype == 'Config':
            self.create_project = ConfigureProject(
                master = master,
                screenzoom = self.sz,
                close_func=self.close_dialog,
                proj_config=self.proj_configure,
                file_path=self.file_path
            )
        else:
            self.create_project = CreateEmptyProject(
                master = master,
                screenzoom = self.sz,
                close_func=self.close_dialog
                )
        self.create_project.pack(fill='both',expand=True)
    def create_buttonbox(self, master):
        pass