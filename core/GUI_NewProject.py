#!/usr/bin/env python
# coding: utf-8

# 新建空白项目，新建智能项目的窗口
import os
import json
import shutil
import threading
import numpy as np
import pandas as pd
import tkinter as tk
import ttkbootstrap as ttk
from pathlib import Path
from ttkbootstrap.dialogs import Dialog, Messagebox, MessageCatalog
from PIL import Image, ImageTk
from .Exceptions import ParserError
from .StoryImporter import StoryImporter
from .ScriptParser import CharTable, RplGenLog
from .GUI_Util import KeyValueDescribe, clear_speech
from .GUI_TableStruct import ProjectTableStruct
from .GUI_Language import tr
from .ProjConfig import preference

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
        self.comfirm_button = ttk.Button(master=self,text=tr('确定'),bootstyle='primary',command=self.confirm,width=10)
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
        'zh':{
            '自定义':   None,
            '横屏-高清 (1920x1080, 30fps)'  : [1920, 1080, 30],
            '横屏-标清（1280x720, 30fps)'   : [1280, 720, 30],
            '竖屏-高清 (1080x1920, 30fps)'  : [1080, 1920, 30],
            '竖屏-标清（720x1280, 30fps）'   : [720, 1280, 30],
            '横屏-高清 (1920x1080, 25fps)'  : [1920, 1080, 25],
            '横屏-标清 (1280x720, 25fps)'   : [1280, 720, 25],
        },
        'en':{
            'Custom':   None,
            'FHD-H (1920x1080, 30fps)'  : [1920, 1080, 30],
            'HD-H（1280x720, 30fps)'   : [1280, 720, 30],
            'FHD-V (1080x1920, 30fps)'  : [1080, 1920, 30],
            'HD-V（720x1280, 30fps）'   : [720, 1280, 30],
            'FHD-H (1920x1080, 25fps)'  : [1920, 1080, 25],
            'HD-H (1280x720, 25fps)'   : [1280, 720, 25],
        }
    }[preference.lang]
    zorder_preset = {
        'zh':{
            '自定义'    :None,
            '背景->立绘->气泡'  : "BG2,BG1,Am3,Am2,Am1,AmS,Bb,BbS",
            '背景->气泡->立绘'  : "BG2,BG1,Bb,BbS,Am3,Am2,Am1,AmS"
        },
        'en':{
            'Custom'    :None,
            'Background->Animation->Bubble'  : "BG2,BG1,Am3,Am2,Am1,AmS,Bb,BbS",
            'Background->Bubble->Animation'  : "BG2,BG1,Bb,BbS,Am3,Am2,Am1,AmS"
        }
    }[preference.lang]
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
        save_path = f"{save_dir}/{file_name}/{file_name}.rgpj"
        if save_dir == '':
            Messagebox().show_error(title=tr('错误'),message=tr('必须要选择一个文件夹用于保存项目文件！'),parent=self)
            return False
        # 检查合法性
        if W<0 or H<0 or F<0:
            Messagebox().show_error(title=tr('错误'),message=tr('分辨率或帧率是非法的数值！'),parent=self)
            return False
        for symbol in ['/','\\',':','*','?','"','<','>','|']:
            if symbol in file_name:
                Messagebox().show_error(title=tr('错误'),message=tr('项目名中不能包含符号 {} ！').format(symbol),parent=self)
                return False
        # 如果文件已经存在
        if os.path.isfile(save_path):
            choice = Messagebox().okcancel(title=tr('文件已存在'),message=tr('目录下已经存在重名的项目文件，要覆盖吗？'),parent=self)
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
            # 建立项目资源目录
            try:
                os.makedirs(f"{save_dir}/{file_name}/")
            except FileExistsError:
                pass
            # 建立项目文件
            with open(save_path,'w',encoding='utf-8') as of:
                of.write(json.dumps(new_project_struct,indent=4))
            # 退出
            self.close_func(save_path)
        except:
            Messagebox().show_error(title=tr('错误'),message=tr('无法保存文件到：\n{}').format(save_path))
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
        self.elements['textfile'].bind_button(dtype='text-file',quote=False,related=False)
        self.elements['section_break'].input.configure(values=[0,100,300,1000,3000],state='readonly')
        self.elements['template'].input.bind('<<ComboboxSelected>>', self.template_selected,'+')
        # 从预设文件夹获取
        intels = os.listdir(self.intel_dir)
        self.elements['template'].input.configure(values=intels,state='readonly')
        # 添加进度条
        self.progress = ttk.Progressbar(master=self.seperator['LogSep'],maximum=1.0,value=0.0,bootstyle='primary-striped')
        self.elements['progress'] = self.progress
    def load_template(self,tplt_name):
        SZ_5 = int(self.sz * 5)
        # rgint 路径
        self.tplt_path = self.intel_dir + tplt_name + '/main.rgint'
        # @ 路径
        self.at_path = self.intel_dir+tplt_name
        try:
            self.template:dict = json.load(open(self.tplt_path,'r',encoding='utf-8'))
        except:
            Messagebox().show_error(tr('该预设模板可能已经损坏！'),title=tr('错误'),parent=self)
            self.elements['template'].set('')
            return
        # 显示
        self.frame_metainfo = ttk.Frame(master=self.seperator['TpltSep'],borderwidth=0)
        ttk.Separator(master=self.frame_metainfo,bootstyle='secondary',orient='horizontal').pack(fill='x',side='top',pady=SZ_5)
        ## thumbnail
        sep_w = self.seperator['TpltSep'].winfo_width() - SZ_5 *2
        thumbnail_size = (sep_w,int(sep_w/16*9)) # 16:9
        self.tplt_cover = ImageTk.PhotoImage(
            image=Image.open(self.template['meta']['cover'].replace('@',self.at_path)).resize(thumbnail_size)
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
            if self.load_template(self.elements['template'].get()):
                self.frame_metainfo.pack(fill='x',side='top',pady=(0,int(self.sz*5)))
        except Exception as E:
            self.elements['template'].set("")
            raise Exception()
    def reset_comfirm(self):
        # 恢复
        for key in self.elements:
            if key != 'progress':
                self.elements[key].enable()
        # 将进度条归零
        self.progress.configure(value=0.0)
        # 恢复按键
        self.comfirm_button.configure(text=tr('确定'),bootstyle='primary',command=self.confirm)
    def on_press_comfirm(self):
        # 禁用
        for key in self.elements:
            # 不操作progress！
            if key != 'progress':
                self.elements[key].disable()
        self.comfirm_button.configure(text=tr('取消'),bootstyle='danger',command=self.terminate_load)
    def confirm(self):
        # 检查合法性
        save_dir = self.elements['save_pos'].get()
        cover_path = self.elements['proj_cover'].get()
        file_name = self.elements['proj_name'].get()
        save_path = f"{save_dir}/{file_name}/{file_name}.rgpj"
        tplt_name = self.elements['template'].get()
        logfile_path = self.elements['textfile'].get()
        if save_dir == '':
            Messagebox().show_error(title=tr('错误'),message=tr('必须要选择一个文件夹用于保存项目文件！'),parent=self)
            return False
        if tplt_name == '':
            Messagebox().show_error(title=tr('错误'),message=tr('必须要选择样式模板！'),parent=self)
            return False
        for symbol in ['/','\\',':','*','?','"','<','>','|']:
            if symbol in file_name:
                Messagebox().show_error(title=tr('错误'),message=tr('项目名中不能包含符号 {} ！').format(symbol),parent=self)
                return False
        if os.path.isfile(save_path):
            choice = Messagebox().okcancel(title=tr('文件已存在'),message=tr('目录下已经存在重名的项目文件，要覆盖吗？'),parent=self)
            if choice != MessageCatalog.translate('OK'):
                return False
        if logfile_path.split('.')[-1] in ['rgl','RGL']:
            choice = Messagebox().show_question(
                title='RplGenLog',
                message=tr('你正在尝试向智能项目中导入一个RGL文件！\n但是，智能项目并非设计用于导入RGL，可能出现异常。\n如果你已经拥有RGL文件，请新建空白项目，再导入文件！'),
                parent=self,
                buttons=[tr('放弃导入')+':primary',tr('继续导入')+':danger']
                )
            if choice != tr('继续导入'):
                return False
        # 0. 禁用元件，更新按钮
        self.on_press_comfirm()
        # 1. 新建一个空白项目
        self.new_project_struct = {
            'config':{
                'Name'          : file_name,
                'Cover'         : cover_path,
            },
            'mediadef':{},
            'chartab':{},
            'logfile':{}
        }
        # 2. 输入模板的config
        self.new_project_struct['config'].update(self.template['config'])
        # 3. 导入模板的静态media
        self.new_project_struct['mediadef'].update(self.template['media']['static'])
        # 4. 载入导入的文本
        try:
            self.load_text = open(logfile_path,'r',encoding='utf-8').read()
        except UnicodeDecodeError:
            try:
                self.load_text = open(logfile_path,'r',encoding='gbk').read()
            except Exception as E:
                Messagebox().show_error(tr('无法解读导入文件的编码！\n请确定导入的是文本文件？'),title=tr('格式错误'),parent=self)
                self.reset_comfirm()
                return False
        except FileNotFoundError:
            Messagebox().show_error(tr('找不到导入的剧本文件，请检查文件名！'),title=tr('找不到文件'),parent=self)
            self.reset_comfirm()
            return False
        # 5. 开始解析
        self.story = StoryImporter()
        self.thread = threading.Thread(target=self.import_story)
        self.thread.start()
        # 6. 开始after
        self.after(500,self.update_progress)
        return self.thread
    # 导入成功之后
    def after_loading(self):
        tplt_chars = self.template['charactor']
        # 做在最前：检查是否解析成功
        if self.story.log_mode is None:
            Messagebox().show_error(tr('当前着色器无法解析导入文本的结构！'),title=tr('格式错误'),parent=self)
            self.reset_comfirm()
            return False
        # 7. 从解析结果中获取角色
        charinfo = self.story.get_charinfo()
        # 8. 去除非法的角色
        charinfo = charinfo[-(charinfo['name'].duplicated() + (charinfo['name'] == '') + (charinfo['name'] == '_dup') + (charinfo.index==''))].copy()
        charinfo['key'] = (np.arange(len(charinfo))%len(tplt_chars)).astype(str)
        # 9. 获取log
        bulid_rgl = np.frompyfunc(lambda char,speech:f"[{char}]:{speech}",2,1)
        log_results = self.story.results
        log_results = log_results[log_results['ID'].map(lambda x:x in charinfo.index)].copy()
        log_results.index = np.arange(len(log_results)) # 重设序号
        log_results['rgl'] = bulid_rgl(
            log_results['ID'].map(charinfo['name']),
            log_results['speech'].map(clear_speech)
            )
        # 10. 生成角色表
        chartable = pd.DataFrame(index=charinfo.index,columns=CharTable.table_col)
        chartable['Name'] = charinfo['name']
        chartable['Subtype'] = 'default'
        chartable['Animation'] = charinfo['key'].map(lambda x:tplt_chars[x]['Animation'])
        chartable['Bubble'] = charinfo['key'].map(lambda x:tplt_chars[x]['Bubble'])
        chartable['Voice'] = 'NA'
        chartable['SpeechRate'] = 0
        chartable['PitchRate'] = 0
        chartable['Header'] = charinfo['header']
        chartable.index = chartable['Name']+'.'+chartable['Subtype']
        self.new_project_struct['chartab'].update(CharTable(table_input=chartable).struct)
        # 11. 生成log文件
        preset_text = RplGenLog(dict_input=self.template['preset']).export()
        sep_length:int = self.elements['section_break'].get()
        if sep_length == 0:
            sep_length = len(log_results)
        section_idx = 0
        while section_idx < len(log_results):
            name_this = f"导入剧本_{section_idx}"
            rgl_text = preset_text + '\n' + '\n'.join(
                log_results.loc[
                    section_idx:(section_idx+sep_length),
                    'rgl'
                    ].values
                )
            try:
                self.new_project_struct['logfile'][name_this] = RplGenLog(string_input=rgl_text).struct
            except ParserError:
                error_text = '# 当你看见这段文字，意味着你触发了一个少见的异常。\n'
                error_text += '# 你的发言文本中的部分内容和RplGenLog的部分语法冲突，这会攻击RplGenLog解析器，并触发ParserError。\n'
                error_text += '# 这个问题并不难解决，请检查你的原始log中，是否某一行的末尾存在类似：<replace=> 的结构，并删除这个结构！\n'
                self.new_project_struct['logfile'][name_this] = RplGenLog(
                    string_input= error_text
                    ).struct
            section_idx += sep_length
        # 12. 新建项目和目录
        save_dir = self.elements['save_pos'].get()
        file_name = self.elements['proj_name'].get()
        save_path = f"{save_dir}/{file_name}/{file_name}.rgpj"
        # 13. 保存文件
        try:
            # 建立项目资源目录
            try:
                os.makedirs(save_dir + '/' + file_name)
            except FileExistsError:
                pass
            # 复制模板素材到项目文件夹
            try:
                shutil.copytree(
                    src=self.at_path+'/media/',
                    dst=f"{save_dir}/{file_name}/media/"
                )
            except FileExistsError:
                shutil.rmtree(f"{save_dir}/{file_name}/media/")
                shutil.copytree(
                    src=self.at_path+'/media/',
                    dst=f"{save_dir}/{file_name}/media/"
                )
            # 建立项目文件
            with open(save_path,'w',encoding='utf-8') as of:
                of.write(json.dumps(self.new_project_struct,indent=4))
            # 退出
            self.close_func(save_path)
        except:
            Messagebox().show_error(title=tr('错误'),message=tr('无法保存文件到：\n{}').format(save_path))
            return False
    def update_progress(self):
        # 如果子进程还活着
        if self.thread.is_alive():
            self.progress.configure(value=self.story.progress)
            self.after(500,self.update_progress)
        else:
            # 如果是手动终止
            if self.story.terminate == True:
                return
            # 如果是自动终止
            else:
                if self.story.progress == 1:
                    self.progress.configure(value=self.story.progress)
                    self.after_loading()
                else:
                    Messagebox().show_error(message=tr('在导入文本时发生了异常！'),title=tr('错误'),parent=self)
                    self.reset_comfirm()
                    return
    # 当正在导入时，终止导入
    def terminate_load(self):
        # 当点的足够快的时候，可能还没创建线程，就点下了终止。
        try:
            if self.thread.is_alive():
                self.story.terminate_load()
                self.thread.join()
                self.reset_comfirm()
            else:
                pass
        except AttributeError:
            pass
    def import_story(self):
        self.story.load(text=self.load_text)
        return
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
                self.elements['preset_video'].value.set(tr('自定义'))
        for keyword in self.zorder_preset:
            if Z == self.zorder_preset[keyword]:
                self.elements['preset_layer'].value.set(keyword)
                break
            else:
                self.elements['preset_layer'].value.set(tr('自定义'))
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
            Messagebox().show_warning(title=tr('警告'),message=tr('分辨率或帧率是非法的数值！'))
            return False
        for symbol in ['/','\\',':','*','?','"','<','>','|']:
            if symbol in file_name:
                Messagebox().show_warning(title=tr('警告'),message=tr('项目名中不能包含符号 {} ！').format(symbol),parent=self)
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
            super().__init__(parent, tr('新建智能项目'), alert=False)
        elif ptype == 'Config':
            super().__init__(parent, tr('项目设置'), alert=False)
            self.proj_configure = kw_args['config']
            self.file_path = kw_args['file_path']
        else:
            super().__init__(parent, tr('新建空白项目'), alert=False)
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