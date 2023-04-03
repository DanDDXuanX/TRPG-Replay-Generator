#!/usr/bin/env python
# coding: utf-8
# 项目配置参数

from .Exceptions import ArgumentError,WarningPrint,Print,RplGenError
from .Motion import MotionMethod
from .Medias import MediaObj
from .TTSengines import Aliyun_TTS_engine,Azure_TTS_engine

# 项目设置
class Config:
    def __init__(self,dict_input=None,argparse_input=None) -> None:
        if dict_input is not None:
            try:
                # 分辨率参数
                self.Width:int = dict_input['Width']
                self.Height:int = dict_input['Height']
                # 帧率
                self.frame_rate:int = dict_input['frame_rate']
                # 图层顺序
                self.zorder:list = dict_input['Zorder']
                # 语言
                # self.lang:str = dict_input['Language']
                # 合成语音时：key
                # self.accesskey:str = dict_input['AccessKey']
                # self.accesskey_secret:str = dict_input['AccessKeySecret']
                # self.appkey:str = dict_input['Appkey']
                # self.azurekey:str = dict_input['Azurekey']
                # self.service_region:str = dict_input['ServRegion']
                # 导出视频时：视频质量
                # self.crf:int = dict_input['ServRegion']
            except:
                raise ArgumentError('InvDict')
        elif argparse_input is not None:
            # 分辨率参数
            self.Width = argparse_input.Width
            self.Height = argparse_input.Height
            # 帧率
            self.frame_rate = argparse_input.FramePerSecond # 帧率 单位fps
            # 图层顺序
            self.zorder = argparse_input.Zorder.split(',') # 渲染图层顺序
            # 语言
            # self.lang:str = argparse_input.Language
            # 合成语音时：key
            # self.accesskey:str = argparse_input.AccessKey
            # self.accesskey_secret:str = argparse_input.AccessKeySecret
            # self.appkey:str = argparse_input.Appkey
            # self.azurekey:str = argparse_input.Azurekey
            # self.service_region:str = argparse_input.ServRegion
            # 导出视频时：视频质量
            # self.crf:int = argparse_input.Quality
        else:
            # 分辨率参数
            self.Width = 1920
            self.Height = 1080
            # 帧率
            self.frame_rate = 30 # 帧率 单位fps
            # 图层顺序
            self.zorder = ['BG2','BG1','Am3','Am2','Am1','AmS','Bb','BbS'] # 渲染图层顺序
            # # 语言
            # self.lang:str = 'en'
            # 合成语音时：key
            # self.accesskey:str = 'Your_AccessKey'
            # self.accesskey_secret:str = 'Your_AccessKey_Secret'
            # self.appkey:str = 'Your_Appkey'
            # self.azurekey:str = 'Your_Azurekey'
            # self.service_region:str = 'eastasia'
            # 导出视频时：视频质量
            # self.crf:int = 24
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
    def get_struct(self)->dict:
        return {
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

# 程序设置
class Preference:
    def __init__(self,dict_input:dict=None) -> None:
        # 合成语音时：key
        self.accesskey:str = 'Your_AccessKey'
        self.accesskey_secret:str = 'Your_AccessKey_Secret'
        self.appkey:str = 'Your_Appkey'
        self.azurekey:str = 'Your_Azurekey'
        self.service_region:str = 'eastasia'
        # 导出视频时：视频质量
        self.crf:int = 24
        # 语言
        self.lang:str = 'en'
        
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
        self.theme:str = 'light'
        # 进度条样式 # color ,black ,disable
        self.progress_bar_style:str = 'color'
        # 帧率显示器开启
        self.framerate_counter:bool = True
        # 导出PR
        # 是否强制在断点处拆分序列
        self.force_split_clip:bool = False
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