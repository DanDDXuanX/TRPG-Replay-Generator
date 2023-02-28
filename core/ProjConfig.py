#!/usr/bin/env python
# coding: utf-8
# 项目配置参数

from .Exceptions import ArgumentError,WarningPrint,Print,RplGenError
from .Motion import MotionMethod
from .Medias import MediaObj

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
                self.lang:str = dict_input['Language']
                # 合成语音时：key
                self.accesskey:str = dict_input['AccessKey']
                self.accesskey_secret:str = dict_input['AccessKeySecret']
                self.appkey:str = dict_input['Appkey']
                self.azurekey:str = dict_input['Azurekey']
                self.service_region:str = dict_input['ServRegion']
                # 导出视频时：视频质量
                self.crf:int = dict_input['ServRegion']
                # 导出PR时：是否强制在断点处拆分序列
                self.force_split_clip:bool = dict_input['ForceSplitClip']
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
            self.lang:str = argparse_input.Language
            # 合成语音时：key
            self.accesskey:str = argparse_input.AccessKey
            self.accesskey_secret:str = argparse_input.AccessKeySecret
            self.appkey:str = argparse_input.Appkey
            self.azurekey:str = argparse_input.Azurekey
            self.service_region:str = argparse_input.ServRegion
            # 导出视频时：视频质量
            self.crf:int = argparse_input.Quality
            # 导出PR时：是否强制在断点处拆分序列
            self.force_split_clip:bool = argparse_input.ForceSplitClip
        else:
            # 分辨率参数
            self.Width = 1920
            self.Height = 1080
            # 帧率
            self.frame_rate = 30 # 帧率 单位fps
            # 图层顺序
            self.zorder = ['BG2','BG1','Am3','Am2','Am1','AmS','Bb','BbS'] # 渲染图层顺序
            # 语言
            self.lang:str = 'en'
            # 合成语音时：key
            self.accesskey:str = 'Your_AccessKey'
            self.accesskey_secret:str = 'Your_AccessKey_Secret'
            self.appkey:str = 'Your_Appkey'
            self.azurekey:str = 'Your_Azurekey'
            self.service_region:str = 'eastasia'
            # 导出视频时：视频质量
            self.crf:int = 24
            # 导出PR时：是否强制在断点处拆分序列
            self.force_split_clip:bool = False
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
        # 修改其他类的配置项
        MotionMethod.screen_size = (self.Width,self.Height)
        MediaObj.screen_size = (self.Width,self.Height)
        MediaObj.frame_rate = self.frame_rate
        # 修改语言
        if self.lang == 'zh':
            # 中文
            Print.lang = 1 
            RplGenError.lang = 1
        else:
            # 英文
            Print.lang == 0
            RplGenError.lang = 0