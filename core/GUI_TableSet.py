#!/usr/bin/env python
# coding: utf-8

import ttkbootstrap as ttk
from ttkbootstrap.constants import DEFAULT
from ttkbootstrap.scrolled import ScrolledFrame
from .GUI_PageElement import OutPutCommand
from .GUI_Util import TextSeparator, KeyValueDescribe

class OutPutCommandAtScriptExecuter(OutPutCommand):
    # 重载
    def load_input(self):
        raise Exception('WIP')

# 脚本执行
class TableEdit(ttk.Frame):
    TableStruct = {}
    def __init__(self,master,screenzoom,title:str)->None:
        # 初始化
        self.sz = screenzoom
        SZ_10 = int(self.sz*10)
        super().__init__(master,borderwidth=0,padding=SZ_10)
        self.title = ttk.Label(master=self,text=title,font='-family 微软雅黑 -size 20 -weight bold',anchor='center')
        self.options = ScrolledFrame(master=self,autohide=True)
        self.options.vscroll.config(bootstyle='primary-round')
        self.outputs = ttk.Frame(master=self)
        # 分隔符和项目
        self.seperator = {}
        self.elements = {}
        # 初始化
        # self.update_from_tablestruct()
        # self.update_item()
    def update_item(self):
        SZ_5 = int(self.sz * 5)
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
                    describe=this_sep['Text']
                )
                for key in this_sep['Content']:
                    this_kvd:dict = this_sep['Content'][key]
                    this_value = this_kvd['default']
                    self.elements[key] = self.seperator[sep].add_element(key=key, value=this_value, kvd=this_kvd, detail=detail)
        # 绑定功能
        self.update_element_prop()
    def update_element_prop(self):
        pass

class ScriptExecuter(TableEdit):
    TableStruct = {
        "InputSep":{
            "Text": "输入文件",
            "Command":None,
            "Content":{
                "mediadef": {
                    "ktext": "媒体定义：",
                    "tooltip":"媒体库的定义文件，是一个txt文本文件",
                    "dtext": "浏览",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": ""
                },
                "chartab": {
                    "ktext": "角色配置：",
                    "tooltip":"角色配置表，是一个tsv表格或者xlsx表格",
                    "dtext": "浏览",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": ""
                },
                "logfile": {
                    "ktext": "剧本文件：",
                    "tooltip":"也称log文件，是一个rgl文本文件",
                    "dtext": "浏览",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": ""
                },
            }
        },
        "ArgsSep":{
            "Text": "设置",
            "Command":None,
            "Content":{
                "width":{
                    "ktext": "分辨率-宽：",
                    "tooltip":None,
                    "dtext": "（偶数）",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "int",
                    "default": 1920
                },
                "height":{
                    "ktext": "分辨率-高：",
                    "tooltip":None,
                    "dtext": "（偶数）",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "int",
                    "default": 1080
                },
                "framerate":{
                    "ktext": "帧率：",
                    "tooltip":None,
                    "dtext": "（数值）",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "int",
                    "default": 30
                },
                "zorder":{
                    "ktext": "图层顺序：",
                    "tooltip":None,
                    "dtext": "（输入）",
                    "ditem": "label",
                    "valuekey": "pos",
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "BG2,BG1,Am3,Am2,Am1,AmS,Bb,BbS"
                },
            }
        }
    }
    def __init__(self,master,screenzoom)->None:
        # 继承
        super().__init__(master=master,screenzoom=screenzoom,title='运行脚本')
        # 输出选项
        self.outputs = OutPutCommand(master=self,screenzoom=self.sz)
        # 初始化
        self.update_from_tablestruct(detail=False)
        self.update_item()
    def update_element_prop(self):
        self.elements['mediadef'].bind_button(dtype='mediadef-file')
        self.elements['chartab'].bind_button(dtype='chartab-file')
        self.elements['logfile'].bind_button(dtype='logfile-file')

# 首选项
class PreferenceTable(TableEdit):
    TableStruct = {
        "KeySep":{
            "Text": "语音合成Key",
            "Command":None,
            "Content":{
                "accesskey": {
                    "ktext": "阿里云-AccessKey",
                    "tooltip":"在AccessKey管理中获取，是一段长度为24的乱码。",
                    "dtext": "（输入）",
                    "ditem": "label",
                    "valuekey": "accesskey",
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "请输入你的AccessKey！"
                },
                "accesskey_secret": {
                    "ktext": "阿里云-AccessKeySecret",
                    "tooltip":"在AccessKey管理中获取，是一段长度为30的乱码。",
                    "dtext": "（输入）",
                    "ditem": "label",
                    "valuekey": "accesskey_secret",
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "请输入你的AccessKeySecret！"
                },
                "appkey": {
                    "ktext": "阿里云-AppKey",
                    "tooltip":"在智能语音服务的项目管理页面中，新建项目后获取，是一段长度为16的乱码。",
                    "dtext": "（输入）",
                    "ditem": "label",
                    "valuekey": "appkey",
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "请输入你的AppKey！"
                },
                "azurekey": {
                    "ktext": "微软Azure-密钥",
                    "tooltip":"在语音服务中，点击管理密钥后获取，是一段长度为32的乱码。",
                    "dtext": "（输入）",
                    "ditem": "label",
                    "valuekey": "appkey",
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "请输入你的密钥！"
                },
                "service_region": {
                    "ktext": "微软Azure-位置/区域",
                    "tooltip":"开通语音服务时选择的服务区域。",
                    "dtext": "（输入）",
                    "ditem": "label",
                    "valuekey": "appkey",
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "eastasia"
                },
            }
        },
        "AppearanceSep":{
            "Text": "界面外观",
            "Command":None,
            "Content":{
                "lang":{
                    "ktext": "语言：",
                    "tooltip":"在控制台终端显示的语言。",
                    "dtext": "（选择）",
                    "ditem": "label",
                    "valuekey": "lang",
                    "vitem": "combox",
                    "vtype": "str",
                    "default": 'en'
                },
                "theme":{
                    "ktext": "主题：",
                    "tooltip": "主界面的配色方案，有深色和浅色两个选择。",
                    "dtext": "（选择）",
                    "ditem": "label",
                    "valuekey": "theme",
                    "vitem": "combox",
                    "vtype": "str",
                    "default": 'light'
                },
            }
        },       
        "MediaSep":{
            "Text": "内建动画",
            "Command":None,
            "Content":{
                "BIA_font":{
                    "ktext": "内建动画字体：",
                    "tooltip":"骰子和血条动画中的文字部分的字体。",
                    "dtext": "浏览",
                    "ditem": "button",
                    "valuekey": "BIA_font",
                    "vitem": "entry",
                    "vtype": "str",
                    "default": './media/SourceHanSerifSC-Heavy.otf'
                },
                "BIA_font_size":{
                    "ktext": "内建动画字号：",
                    "tooltip":"骰子和血条动画中文字的大小的乘数，实际字号等于这个数值乘以项目的宽分辨率。",
                    "dtext": "（数值）",
                    "ditem": "label",
                    "valuekey": "BIA_font_size",
                    "vitem": "entry",
                    "vtype": "float",
                    "default": 0.0521
                },
                "heart_pic":{
                    "ktext": "HP动画前景：",
                    "tooltip":"在血条动画中，代表剩余生命值的符号的图片。",
                    "dtext": "浏览",
                    "ditem": "button",
                    "valuekey": "heart_pic",
                    "vitem": "entry",
                    "vtype": "str",
                    "default": './media/heart.png'
                },
                "heart_shape":{
                    "ktext": "HP动画背景：",
                    "tooltip":"在血条动画中，代表生命值总量的符号的图片。",
                    "dtext": "浏览",
                    "ditem": "button",
                    "valuekey": "heart_shape",
                    "vitem": "entry",
                    "vtype": "str",
                    "default": './media/heart_shape.png'
                },
                "heart_distance":{
                    "ktext": "HP动画心心距离：",
                    "tooltip":"在血条动画中，邻近的两个心心的间距的乘数，实际间距等于这个数值乘以项目的宽分辨率。",
                    "dtext": "（数值）",
                    "ditem": "label",
                    "valuekey": "heart_distance",
                    "vitem": "entry",
                    "vtype": "float",
                    "default": 0.026
                },
            }
        },
        "PreviewSep":{
            "Text": "预览设置",
            "Command":None,
            "Content":{
                "progress_bar_style":{
                    "ktext": "进度条风格：",
                    "tooltip":"选择进度条是彩色风格、黑白风格，还是不显示进度条。",
                    "dtext": "（选择）",
                    "ditem": "label",
                    "valuekey": "progress_bar_style",
                    "vitem": "combox",
                    "vtype": "str",
                    "default": 'color'
                },
                "framerate_counter":{
                    "ktext": "帧率显示器开启：",
                    "tooltip":"选择是否常驻开启帧率显示器。",
                    "dtext": "（选择）",
                    "ditem": "label",
                    "valuekey": "framerate_counter",
                    "vitem": "combox",
                    "vtype": "bool",
                    "default": True
                },
            }
        },
        "ExportSep":{
            "Text": "导出设置",
            "Command":None,
            "Content":{
                "force_split_clip":{
                    "ktext": "强制拆分剪辑：",
                    "tooltip":"如果选择是，在所有小节断点，都会强制拆分所有剪辑，即使这个断点前后是同一个媒体。",
                    "dtext": "（选择）",
                    "ditem": "label",
                    "valuekey": "force_split_clip",
                    "vitem": "combox",
                    "vtype": "bool",
                    "default": False
                },
                "crf":{
                    "ktext": "视频质量：",
                    "tooltip":"导出为mp4视频时的质量，即ffmpeg程序的crf值；取值范围为0-51，越小对应越高的视频质量，通常合理范围为18-28。",
                    "dtext": "（选择）",
                    "ditem": "label",
                    "valuekey": "crf",
                    "vitem": "spine",
                    "vtype": "int",
                    "default": 24
                },
            }
        },
    }
    def __init__(self,master,screenzoom)->None:
        # 继承
        super().__init__(master=master,screenzoom=screenzoom,title='首选项')
        # 输出选项
        # self.outputs = OutPutCommand(master=self,screenzoom=self.sz)
        # 初始化
        self.update_from_tablestruct(detail=True)
        self.update_item()
    def update_element_prop(self):
        pass