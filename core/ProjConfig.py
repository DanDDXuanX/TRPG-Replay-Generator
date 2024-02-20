#!/usr/bin/env python
# coding: utf-8
# 项目配置参数

import os
import json
from pathlib import Path
from PIL import ImageFile
from .Exceptions import ArgumentError,WarningPrint,Print,RplGenError
from .Motion import MotionMethod
from .Medias import MediaObj, BuiltInAnimation, HitPoint, Dice
from .TTSengines import TTS_engine,Aliyun_TTS_engine,Azure_TTS_engine,Tencent_TTS_engine
from .Security import KeyRequest

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
            self.Cover:str = "./assets/cover.jpg"
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
    default = {
        # 合成语音时：key
        'use_bulitin_keys' : True,
        'accesskey' : 'Your_AccessKey',
        'accesskey_secret' : 'Your_AccessKey_Secret',
        'appkey' : 'Your_Appkey',
        'azurekey' : 'Your_Azurekey',
        'service_region' : 'eastasia',
        'appid' : '0',
        'secretid' : 'Your_SecretID',
        'secretkey' : 'Your_SecretKey',
        # 系统
        'lang' : 'zh',
        'theme' : 'rplgenlight',
        'editer_fontsize' : 12,
        'editer_colorschemes' : "monokai",
        'terminal_fontsize' : 14,
        'performance_mode'  : False,
        # 内置动画
        'BIA_font' : './assets/SourceHanSerifSC-Heavy.otf',
        'BIA_font_size' : 0.0521,
        'dice_mode' : 'COC',
        'dice_threshold' : 0.05,
        'heart_pic' : './assets/heart.png',
        'heart_shape' : './assets/heart_shape.png',
        'heart_distance' : 0.026,
        # 编辑
        'auto_periods' : False,
        'import_mode' : 'add',
        'auto_convert' : 'ask',
        'rename_boardcast' : 'ask',
        'asterisk_import' : True,
        'masked_symbol' : '',
        # 预览
        'progress_bar_style' : 'color',
        'framerate_counter' : True,
        # 导出视频时：视频质量
        'crf' : 24,
        'hwaccels' : False,
        'force_split_clip' : False,
        'alphaexp' : False,
        'export_srt' : False
    }
    keyword = {
        # 语音key
        'use_bulitin_keys' : "TTSKey.UseBulitInKeys",
        'accesskey' : 'Aliyun.accesskey',
        'accesskey_secret' : 'Aliyun.accesskey_secret',
        'appkey' : 'Aliyun.appkey',
        'azurekey' : 'Azure.azurekey',
        'service_region' : 'Azure.service_region',
        'appid' : 'Tencent.appid',
        'secretid' : 'Tencent.secretid',
        'secretkey' : 'Tencent.secretkey',
        # 系统
        'lang' : 'System.lang',
        'theme' : 'System.theme',
        'editer_fontsize' : 'System.editer_fontsize',
        'editer_colorschemes' : 'System.editer_colorschemes',
        'terminal_fontsize' : 'System.terminal_fontsize',
        'performance_mode'  : 'System.performance_mode',
        # 媒体
        'BIA_font' : 'BIA.font',
        'BIA_font_size' : 'BIA.font_size',
        'dice_mode' : 'BIA.dice_mode',
        'dice_threshold' : 'BIA.dice_threshold',
        'heart_pic' : 'BIA.heart_pic',
        'heart_shape' : 'BIA.heart_shape',
        'heart_distance' : 'BIA.heart_distance',
        # 编辑
        'auto_periods' : 'Edit.auto_periods',
        'import_mode' : 'Edit.import_mode',
        'auto_convert' : 'Edit.auto_convert',
        'asterisk_import' : 'Edit.asterisk_import',
        'rename_boardcast' : 'Edit.rename_boardcast',
        'masked_symbol' : 'Edit.masked_symbol',
        # 预览
        'progress_bar_style' : 'Preview.progress_bar_style',
        'framerate_counter' : 'Preview.framerate_counter',
        # 导出
        'force_split_clip' : 'Export.force_split_clip',
        'export_srt'  : 'Export.export_srt',
        'crf' : 'Export.crf',
        'alphaexp' : 'Export.alpha_export',
        'hwaccels' : 'Export.hwaccels',
    }
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
            # 如果缺省值，则采用默认值
            for key,value in self.keyword.items():
                try:
                    self.__setattr__(key,dict_input[value])
                except KeyError:
                    self.__setattr__(key,self.default[key])
        else:
            for key,value in self.keyword.items():
                self.__setattr__(key,self.default[key])
    def get_struct(self)->dict:
        struct = {}
        for key, value in self.keyword.items():
            struct[value] = self.__getattribute__(key)
        return struct
    def execute(self):
        # 修改语言
        if self.lang == 'zh':
            # 中文
            Print.lang = 1 
            RplGenError.lang = 1
            MediaObj.test_str = '测试文本'
        else:
            # 英文
            Print.lang == 0
            RplGenError.lang = 0
            MediaObj.test_str = 'Test'
        # 语音合成的屏蔽符号
        TTS_engine.masked_symbol = list(set(self.masked_symbol))
        # 如果不使用内置key
        if self.use_bulitin_keys == False:
            # 阿里云语音合成key
            Aliyun_TTS_engine.AKID = self.accesskey
            Aliyun_TTS_engine.AKKEY = self.accesskey_secret
            Aliyun_TTS_engine.APPKEY = self.appkey
            # Azure语音合成key
            Azure_TTS_engine.AZUKEY = self.azurekey
            Azure_TTS_engine.service_region = self.service_region
            # 腾讯的语音合成key
            Tencent_TTS_engine.APPID = int(self.appid)
            Tencent_TTS_engine.SecretId = self.secretid
            Tencent_TTS_engine.SecretKey = self.secretkey
            self.bulitin_keys_status = -1
        else:
            self.key_security = KeyRequest()
            self.bulitin_keys_status = self.key_security.status
        # 内建动画
        BuiltInAnimation.BIA_font = self.BIA_font
        BuiltInAnimation.BIA_font_size = self.BIA_font_size
        HitPoint.heart_image = self.heart_pic
        HitPoint.heart_shape = self.heart_shape
        HitPoint.heart_distance = self.heart_distance
        Dice.significant = self.dice_threshold
        Dice.mode = self.dice_mode
    def load_json(self,filepath)->dict:
        with open(filepath,'r') as json_file:
            data =json.load(json_file)
        return data
    def dump_json(self,filepath=None)->None:
        if filepath is None:
            filepath = self.file
        with open(filepath,'w') as out_file:
            json.dump(self.get_struct(), out_file, indent=4)
    # 反馈语音合成用量报文
    def post_usage(self):
        if self.bulitin_keys_status == 0:
            # 上传用量信息报文
            status = self.key_security.post_usage()
            return status
        else:
            return -1 # 代表没做
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