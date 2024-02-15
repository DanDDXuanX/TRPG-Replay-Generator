#!/usr/bin/env python
# coding: utf-8

import json
import ttkbootstrap as ttk
from ttkbootstrap.toast import ToastNotification
from PIL import Image, ImageTk
from .ProjConfig import preference, Preference
from .GUI_PageElement import OutPutCommand
from .GUI_Util import TextSeparator, FluentFrame, StickyLabelSeperator
from .GUI_Link import Link
from .GUI_Language import tr
from .GUI_TableStruct import PreferenceTableStruct, ExecuteTableStruct, PortalStruct
from .GUI_TableStruct import language, True_False, theme, progressbar, import_mode, dice_mode, askyesno, colorschemes, is_enable

class OutPutCommandAtScriptExecuter(OutPutCommand):
    # 重载
    def load_input(self):
        raise Exception('WIP')

# 脚本执行
class TableEdit(ttk.Frame):
    TableStruct = {}
    def __init__(self,master,screenzoom,title:str,pady:int=5)->None:
        # 初始化
        self.sz = screenzoom
        SZ_10 = int(self.sz*10)
        super().__init__(master,borderwidth=0,padding=SZ_10)
        self.title = ttk.Label(master=self,text=title,font=(Link['system_font_family'], 20, "bold"),anchor='center')
        self.options = FluentFrame(master=self,autohide=True)
        self.options.vscroll.config(bootstyle='primary-round')
        self.outputs = ttk.Frame(master=self)
        # 结构
        self.struct = {}
        # 分隔符和项目
        self.seperator = {}
        self.elements = {}
        # 布局
        self.pady = pady
        # 初始化
        # self.update_from_tablestruct()
        # self.update_item()
    def update_item(self):
        SZ_5 = int(self.sz * self.pady)
        SZ_10 = 2 * SZ_5
        SZ_20 = 4 * SZ_5
        self.title.pack(fill='x',side='top')
        self.options.pack(fill='both',expand=True,side='top')
        self.outputs.pack(fill='x',side='top')
        # 滚动窗项目下
        for key in self.seperator:
            item:TextSeparator = self.seperator[key]
            item.pack(side='top',anchor='n',fill='x',pady=(0,SZ_5),padx=(SZ_10,SZ_20))
    def update_from_tablestruct(self, detail=False):
        # 从EditWindow.update_from_section方法中简化而来的
        self.table_struct:dict = self.TableStruct
        for sep in self.table_struct:
            this_sep:dict = self.table_struct[sep]
            if this_sep['Command'] is None:
                self.seperator[sep] = TextSeparator(
                    master=self.options,
                    screenzoom=self.sz,
                    describe=this_sep['Text'],
                    pady=self.pady
                )
                for key in this_sep['Content']:
                    this_kvd:dict = this_sep['Content'][key]
                    # 获取struct，或者default
                    try:
                        this_value = self.struct[this_kvd['valuekey']]
                    except KeyError:
                        this_value = this_kvd['default']
                    # 新建kvd
                    self.elements[key] = self.seperator[sep].add_element(key=key, value=this_value, kvd=this_kvd, detail=detail)
        # 绑定功能
        self.update_element_prop()
    def update_element_prop(self):
        pass

class ScriptExecuter(TableEdit):
    TableStruct = ExecuteTableStruct
    def __init__(self,master,screenzoom)->None:
        # 继承
        super().__init__(master=master,screenzoom=screenzoom,title=tr('运行脚本'))
        # 重写：改为不可滚动的
        self.options = ttk.Frame(master=self)
        # 输出选项
        self.outputs = OutPutCommandAtScriptExecuter(master=self,screenzoom=self.sz)
        # 初始化
        self.update_from_tablestruct(detail=False)
        self.update_item()
        # TODO: 临时的告示
        ttk.Label(
            master=self.options,
            text='暂时禁用，未来可能移除！',
            font=(Link['system_font_family'], 30, "bold"),
            foreground='#bbbbbb',
            anchor='center'
        ).pack(
            side='top',
            fill='both',
            expand=True
        )
    def update_element_prop(self):
        self.elements['mediadef'].bind_button(dtype='mediadef-file',related=False)
        self.elements['chartab'].bind_button(dtype='chartab-file',related=False)
        self.elements['logfile'].bind_button(dtype='logfile-file',related=False)

# 首选项
class ResetConfirm(ttk.Frame):
    def __init__(self,master,screenzoom,preferencetable):
        self.sz = screenzoom
        SZ_5 = int(self.sz*5)
        SZ_30 = int(self.sz * 30)
        icon_size = [SZ_30,SZ_30]
        super().__init__(master=master,borderwidth=SZ_5)
        self.preferencetable = preferencetable
        self.image = {
            'reset'     : ImageTk.PhotoImage(image=Image.open('./assets/icon/reset.png').resize(icon_size)),
            'confirm'   : ImageTk.PhotoImage(image=Image.open('./assets/icon/confirm.png').resize(icon_size)),
        }
        # 输出选项
        self.buttons = {
            'reset'     : ttk.Button(master=self, text=tr('重置'),compound='left',image=self.image['reset'],command=self.preferencetable.reset, style='output.TButton',padding=0,cursor='hand2'),
            'confirm'   : ttk.Button(master=self, text=tr('确定'),compound='left',image=self.image['confirm'],command=self.preferencetable.confirm, style='output.TButton',padding=0,cursor='hand2')
        }
        for key in self.buttons:
            item:ttk.Button = self.buttons[key]
            item.pack(fill='both',side='top',expand=True,pady=SZ_5,padx=SZ_5)
class PreferenceTable(TableEdit):
    TableStruct = PreferenceTableStruct
    def __init__(self,master,screenzoom)->None:
        # 继承
        super().__init__(master=master,screenzoom=screenzoom,title=tr('首选项'),pady=10)
        # 首选项
        self.struct = preference.get_struct()
        # self.outputs = OutPutCommand(master=self,screenzoom=self.sz)
        # 初始化
        self.update_from_tablestruct(detail=True)
        self.update_item()
    def update_element_prop(self):
        # combox
        self.elements['System.lang'].input.update_dict(language)
        self.elements['System.theme'].input.update_dict(theme)
        self.elements['System.editer_colorschemes'].input.update_dict(colorschemes)
        self.elements['System.performance_mode'].input.update_dict(is_enable)
        self.elements['Preview.progress_bar_style'].input.update_dict(progressbar)
        self.elements['Preview.framerate_counter'].input.update_dict(True_False)
        self.elements['Export.force_split_clip'].input.update_dict(True_False)
        self.elements['Export.export_srt'].input.update_dict(True_False)
        self.elements['Export.hwaccels'].input.update_dict(True_False)
        self.elements['Export.alpha_export'].input.update_dict(True_False)
        self.elements['Edit.auto_periods'].input.update_dict(True_False)
        self.elements['Edit.import_mode'].input.update_dict(import_mode)
        self.elements['Edit.auto_convert'].input.update_dict(askyesno)
        self.elements['Edit.asterisk_import'].input.update_dict(True_False)
        self.elements['Edit.rename_boardcast'].input.update_dict(askyesno)
        self.elements['BIA.dice_mode'].input.update_dict(dice_mode)
        self.elements['TTSKey.UseBulitInKeys'].input.update_dict(is_enable)
        # spine
        self.elements['System.editer_fontsize'].input.configure(from_=5,to=30,increment=1)
        self.elements['System.terminal_fontsize'].input.configure(from_=5,to=30,increment=1)
        self.elements['Export.crf'].input.configure(from_=0,to=51,increment=1)
        # button
        self.elements['BIA.font'].bind_button(dtype='fontfile-file',quote=False,related=False)
        self.elements['BIA.heart_pic'].bind_button(dtype='picture-file',quote=False,related=False)
        self.elements['BIA.heart_shape'].bind_button(dtype='picture-file',quote=False,related=False)
    def reset(self):
        reset_struct:dict = Preference().get_struct()
        # 重设前端显示
        for keyword in self.elements:
            self.elements[keyword].set(reset_struct[keyword])
        # 重设prefernce对象
        preference.set_struct(reset_struct)
        # 消息
        self.show_toast(message=tr('首选项已经重置为默认值！'),title=tr('重置','首选项'))
    def confirm(self):
        new_struct = {}
        for keyword in self.elements:
            element_value = self.elements[keyword].get()
            # 去除key中潜在的换行符
            if keyword.split('.')[0] in ['Aliyun','Azure','Tencent']:
                element_value = element_value.replace('\n','')
            # 结束
            new_struct[keyword] = element_value
        try:
            # 修改首选项前，将之前的用量报文上传
            preference.post_usage()
            # 重设prefernce对象
            preference.set_struct(new_struct)
            preference.execute() # 执行变更
            preference.dump_json() # 保存配置文件
            # 更新状态栏
            try:
                Link['update_statusbar']()
            except Exception: # 在当前显示的不是首页时，可能会出现异常
                pass
            # 消息
            self.show_toast(message=tr('已经成功设置首选项！\n主题变更需要重启程序后才会生效'),title=tr('修改','首选项'))
        except Exception as E:
            error_message = f"[{E.__class__.__name__}]: {E.__str__()}"
            # 错误
            self.show_toast(
                message=tr('设置首选项时发生了如下错误！\n')+error_message,
                title=tr('错误')
                )
    def show_toast(self,message,title='test'):
        toast = ToastNotification(title=title,message=message,duration=3000)
        toast.show_toast()
        toast.toplevel.lift()

# 传送门
class PortalTable(TableEdit):
    TableStruct = PortalStruct
    # TableStruct = json.load(open('./assets/GUI_portal.json'))
    def __init__(self,master,screenzoom)->None:
        # 继承
        super().__init__(master=master,screenzoom=screenzoom,title=tr('传送门'),pady=10)
        # 初始化
        self.update_from_tablestruct()
        self.update_item()
    def update_item(self):
        SZ_5 = int(self.sz * self.pady)
        SZ_10 = 2 * SZ_5
        self.title.pack(fill='x',side='top')
        self.options.pack(fill='both',expand=True,side='top')
        self.outputs.pack(fill='x',side='top')
        # 滚动窗项目下
        for key in self.seperator:
            item:TextSeparator = self.seperator[key]
            item.pack(side='top',anchor='n',fill='x',pady=(0,SZ_5),padx=(0,SZ_5))
    def update_from_tablestruct(self):
        # 从EditWindow.update_from_section方法中简化而来的
        self.table_struct:dict = self.TableStruct
        for sep in self.table_struct:
            this_sep:dict = self.table_struct[sep]
            if this_sep['Command'] is None:
                self.seperator[sep] = StickyLabelSeperator(
                    master=self.options,
                    screenzoom=self.sz,
                    describe=this_sep['Text'],
                    pady=self.pady
                )
                for key in this_sep['Content']:
                    this_slabel:dict = this_sep['Content'][key]
                    # 新建kvd
                    self.elements[key] = self.seperator[sep].add_element(
                        key=key,
                        icon=this_slabel['icon'],
                        title=this_slabel['title'],
                        describe=this_slabel['describe'],
                        url=this_slabel['url']
                        )
                # 更新显示
                self.seperator[sep].update_elements()
        # 绑定功能
        self.update_element_prop()