#!/usr/bin/env python
# coding: utf-8
# 项目配置参数

import os
import json
from pathlib import Path
from PIL import ImageFile
from .Exceptions import ArgumentError,WarningPrint,Print,RplGenError
from .Motion import MotionMethod
from .Medias import MediaObj, BuiltInAnimation, HitPoint
from .TTSengines import Aliyun_TTS_engine,Azure_TTS_engine

# 项目设置
class Config:
    def __init__(self,dict_input=None,argparse_input=None) -> None:
        # 载入值
        self.set_struct(dict_input=dict_input,argparse_input=argparse_input)
        # 检查：帧率
        if self.frame_rate <= 0:
            raise ArgumentError('FrameRate',str(self.frame_rate))
        elif self.frame_rate>30:
            print(WarningPrint('HighFPS',str(self.frame_rate)))
        # 检查：分辨率
        if (self.Width<=0) | (self.Height<=0):
            raise ArgumentError('Resolution',str((self.Width,self.Height)))
        if self.Width*self.Height > 3e6:
            print(WarningPrint('HighRes'))
    def set_struct(self,dict_input=None,argparse_input=None):
        if dict_input is not None:
            try:
                # 项目基本信息
                self.Name:str = dict_input['Name']
                self.Cover:str = dict_input['Cover']
                # 分辨率参数
                self.Width:int = dict_input['Width']
                self.Height:int = dict_input['Height']
                # 帧率
                self.frame_rate:int = dict_input['frame_rate']
                # 图层顺序
                self.zorder:list = dict_input['Zorder']
            except:
                raise ArgumentError('InvDict')
        elif argparse_input is not None:
            # 项目基本信息
            self.Name:str = 'Terminal'
            self.Cover:str = ''
            # 分辨率参数
            self.Width = argparse_input.Width
            self.Height = argparse_input.Height
            # 帧率
            self.frame_rate = argparse_input.FramePerSecond # 帧率 单位fps
            # 图层顺序
            self.zorder = argparse_input.Zorder.split(',') # 渲染图层顺序
        else:
            # 项目基本信息
            self.Name:str = "Dev"
            self.Cover:str = "./media/cover.jpg"
            # 分辨率参数
            self.Width = 1920
            self.Height = 1080
            # 帧率
            self.frame_rate = 30 # 帧率 单位fps
            # 图层顺序
            self.zorder = ['BG2','BG1','Am3','Am2','Am1','AmS','Bb','BbS'] # 渲染图层顺序
    def get_struct(self)->dict:
        return {
            'Name'          : self.Name,
            'Cover'         : self.Cover,
            'Width'         : self.Width,
            'Height'        : self.Height,
            'frame_rate'    : self.frame_rate,
            'Zorder'        : self.zorder,
        }
    def execute(self):
        # 动态效果
        MotionMethod.screen_size:tuple = (self.Width,self.Height)
        # 媒体
        MediaObj.screen_size:tuple     = (self.Width,self.Height)
        MediaObj.frame_rate:int        = self.frame_rate
        MediaObj.Is_NTSC:bool          = self.frame_rate % 30 == 0 
        MediaObj.Audio_type:str        = 'Audio_type'

# 程序设置
class Preference:
    def __init__(self,dict_input:dict=None,json_input:str=None) -> None:
        # 载入
        if json_input:
            self.file = json_input
            self.set_struct(dict_input=self.load_json(json_input))
        else:
            self.file = home_dir /'.rplgen' /'preference.json'
            self.set_struct(dict_input=dict_input)
        # 执行
        self.execute()
    def set_struct(self,dict_input:dict=None) -> None:
        if dict_input:
            # 合成
            self.accesskey:str = dict_input['Aliyun.accesskey']
            self.accesskey_secret:str = dict_input['Aliyun.accesskey_secret']
            self.appkey:str = dict_input['Aliyun.appkey']
            self.azurekey:str = dict_input['Azure.azurekey']
            self.service_region:str = dict_input['Azure.service_region']
            # 系统
            self.lang:str = dict_input['System.lang']
            self.theme:str = dict_input['System.theme']
            # 媒体
            self.BIA_font:str = dict_input['BIA.font']
            self.BIA_font_size:float =dict_input['BIA.font_size']
            self.heart_pic:str = dict_input['BIA.heart_pic']
            self.heart_shape:str = dict_input['BIA.heart_shape']
            self.heart_distance:float = dict_input['BIA.heart_distance']
            # 编辑
            self.auto_periods:bool = dict_input['Edit.auto_periods']
            self.import_mode:str = dict_input['Edit.import_mode']
            # 预览
            self.progress_bar_style:str = dict_input['Preview.progress_bar_style']
            self.framerate_counter:bool = dict_input['Preview.framerate_counter']
            # 导出
            self.force_split_clip:bool = dict_input['Export.force_split_clip']
            self.crf:int = dict_input['Export.crf']
        else:
            # 合成语音时：key
            self.accesskey:str = 'Your_AccessKey'
            self.accesskey_secret:str = 'Your_AccessKey_Secret'
            self.appkey:str = 'Your_Appkey'
            self.azurekey:str = 'Your_Azurekey'
            self.service_region:str = 'eastasia'
            # 导出视频时：视频质量
            self.crf:int = 24
            # 语言
            self.lang:str = 'zh'
            # 编辑
            self.auto_periods:bool = False
            # 媒体
            # 内建动画的字体文件
            self.BIA_font:str = './media/SourceHanSerifSC-Heavy.otf'
            # 内建动画的字体大小
            self.BIA_font_size:float = 0.0521 # W
            # 生命动画的前景图
            self.heart_pic:str = './media/heart.png'
            # 生命动画的背景图
            self.heart_shape:str = './media/heart_shape.png'
            # 心与心的距离
            self.heart_distance:float = 0.026 # W
            # 预览
            # theme # light, dark
            self.theme:str = 'rplgenlight'
            # 进度条样式 # color ,black ,disable
            self.progress_bar_style:str = 'color'
            # 帧率显示器开启
            self.framerate_counter:bool = True
            # 导出PR
            # 是否强制在断点处拆分序列
            self.force_split_clip:bool = False
            # 导入模式
            self.import_mode:str = 'add'
    def get_struct(self)->dict:
        return {
            # 语音合成
            'Aliyun.accesskey'          : self.accesskey,
            'Aliyun.accesskey_secret'   : self.accesskey_secret,
            'Aliyun.appkey'             : self.appkey,
            'Azure.azurekey'            : self.azurekey,
            'Azure.service_region'      : self.service_region,
            # 系统
            'System.lang'               : self.lang,
            'System.theme'              : self.theme,
            # 媒体
            'BIA.font'                  : self.BIA_font,
            'BIA.font_size'             : self.BIA_font_size,
            'BIA.heart_pic'             : self.heart_pic,
            'BIA.heart_shape'           : self.heart_shape,
            'BIA.heart_distance'        : self.heart_distance,
            # 编辑
            'Edit.auto_periods'         : self.auto_periods,
            'Edit.import_mode'          : self.import_mode,
            # 预览
            'Preview.progress_bar_style': self.progress_bar_style,
            'Preview.framerate_counter' : self.framerate_counter,
            # 导出
            'Export.crf'                : self.crf,
            'Export.force_split_clip'   : self.force_split_clip,
        }
    def execute(self):
        # 修改语言
        if self.lang == 'zh':
            # 中文
            Print.lang = 1 
            RplGenError.lang = 1
        else:
            # 英文
            Print.lang == 0
            RplGenError.lang = 0
        # 阿里云语音合成key
        Aliyun_TTS_engine.AKID = self.accesskey
        Aliyun_TTS_engine.AKKEY = self.accesskey_secret
        Aliyun_TTS_engine.APPKEY = self.appkey
        # Azure语音合成key
        Azure_TTS_engine.AZUKEY = self.azurekey
        Azure_TTS_engine.service_region = self.service_region
        # 内建动画
        BuiltInAnimation.BIA_font = self.BIA_font
        BuiltInAnimation.BIA_font_size = self.BIA_font_size
        HitPoint.heart_image = self.heart_pic
        HitPoint.heart_shape = self.heart_shape
        HitPoint.heart_distance = self.heart_distance
    def load_json(self,filepath)->dict:
        with open(filepath,'r') as json_file:
            data =json.load(json_file)
        return data
    def dump_json(self,filepath=None)->None:
        if filepath is None:
            filepath = self.file
        with open(filepath,'w') as out_file:
            json.dump(self.get_struct(), out_file, indent=4)

# 全局变量

home_dir = Path(os.path.expanduser("~"))
try:
    # 从home目录读取
    preference = Preference(json_input=home_dir /'.rplgen' /'preference.json')
except:
    # 在home目录新建目录
    try:
        os.makedirs(home_dir / '.rplgen')
    except FileExistsError:
        pass
    preference = Preference()
    preference.dump_json(home_dir / '.rplgen' / 'preference.json')

# 全局常量
ImageFile.LOAD_TRUNCATED_IMAGES = True