#!/usr/bin/env python
# coding: utf-8

# 重构后的语音合成模块
import pandas as pd
import os
import re

from .ScriptParser import RplGenLog,CharTable,MediaDef
from .ProjConfig import Config
from .TTSengines import Aliyun_TTS_engine,Azure_TTS_engine,Beats_engine
from .Exceptions import WarningPrint,RplGenError,SynthesisError,SynthPrint,ParserError
from .Medias import Audio

from .Utils import mod62_timestamp,EDITION

class SpeechSynthesizer:
    # 初始化
    def __init__(self,rplgenlog:RplGenLog,chartab:CharTable,mediadef:MediaDef,output_path:str,config:Config=Config()) -> None:
        # 项目配置
        self.config = config
        # 输出路径
        self.output_path = output_path
        # 角色表
        self.charactor_table = chartab.execute()
        # 建立 TTS 对象
        self.charactor_table['TTS'] = self.bulid_tts_engine()
        # 媒体定义
        self.medias:dict = mediadef.Medias
        # log文件
        self.rgl:RplGenLog = rplgenlog
    # 建立语音合成对象
    def bulid_tts_engine(self) -> pd.Series:
        # TTS engines 对象的容器
        TTS = pd.Series(index=self.charactor_table.index,dtype='str')
        # 逐个遍历角色
        for key,value in self.charactor_table.iterrows():
            try:
                # 如果音源是NA，那么TTS 是 "None"
                if (value.Voice != value.Voice)|(value.Voice=="NA"): 
                    TTS[key] = None
                # 阿里云模式：如果音源名在音源表内
                elif value.Voice in Aliyun_TTS_engine.voice_list:
                    TTS[key] = Aliyun_TTS_engine(
                        name=key,
                        voice=value.Voice,
                        speech_rate=int(value.SpeechRate),
                        pitch_rate=int(value.PitchRate)
                        )
                # Azure 模式：如果音源名以 'Azure::' 作为开头
                elif value.Voice[0:7] == 'Azure::':
                    TTS[key] = Azure_TTS_engine(
                        name=key,
                        voice=value.Voice[7:], 
                        speech_rate=int(value.SpeechRate),
                        pitch_rate=int(value.PitchRate)
                        )
                # Beats 模式：如果音源名以 'Beats::' 作为开头
                elif value.Voice[0:7] == 'Beats::':
                    TTS[key] = Beats_engine(
                        name=key,
                        voice=value.Voice[7:],
                        frame_rate=self.config.frame_rate
                        )
                # 否则，是非法的音源名
                else:
                    print(WarningPrint('BadSpeaker',value.Voice))
                    TTS[key] = None
            except ModuleNotFoundError as E:
                # 缺乏依赖包，异常退出
                raise RplGenError('ImportErr',E)
            except ValueError as E:
                # 包含非法音源名，异常退出
                print(E)
        # 返回 TTS engine
        return TTS
    # 对log文件施加语音合成: 成功走完流程：True，FatalBreak : False
    def execute(self)->bool:
        # 为了 Beats，处理遍历log的时候，遍历set行
        tx_method_default = {'method':'all','method_dur':0}
        tx_dur_default = 5,
        # 开始遍历log文件
        for section in self.rgl.struct.keys():
            i = int(section) + 1
            # 当前小节
            this_section:dict = self.rgl.struct[section]
            # 如果是改变：tx_method 的设置行
            if this_section['type'] == 'set':
                if this_section['target'] == 'tx_method_default':
                    tx_method_default = this_section['value']
                elif this_section['target'] == 'tx_dur_default':
                    tx_dur_default = int(this_section['value'])
                continue
            # 如果也不是对话行
            elif this_section['type'] != 'dialog':
                continue
            # 检查是否需要执行语音合成
            if '{*}' not in this_section['sound_set'].keys():
                continue
            # 星标
            this_asterisk:dict = this_section['sound_set']['{*}']
            # 新的语音
            this_asterisk_synth:dict = {}
            # 检查是否有媒体
            if this_asterisk['sound'] is None:
                if 'specified_speech' in this_asterisk.keys():
                    # 指定内容的语音合成
                    this_content = this_asterisk['specified_speech']
                else:
                    # 普通的语音合成
                    this_content = this_section['content']
                # 取出首位角色名
                this_name:dict = this_section['charactor_set']['0']
                this_name_key:str = this_name['name'] + '.' + this_name['subtype']
                if this_name_key not in self.charactor_table.index:
                    # 使用了角色表中不存在的角色
                    print(WarningPrint('UndefChar',this_name_key))
                    continue
                # 语音合成对象
                this_TTS_engine = self.charactor_table.loc[this_name_key,'TTS']
                # 非法的语音合成对象
                if this_TTS_engine is None:
                    print(WarningPrint('CharNoVoice',this_name_key))
                    continue
                # 如果是节奏音
                elif type(this_TTS_engine) is Beats_engine:
                    # 检查，tx_method 的合法性
                    tx_method = this_section['tx_method'].copy()
                    if tx_method['method'] == 'default':
                        tx_method = tx_method_default.copy()
                    if tx_method['method_dur'] == 'default':
                        tx_method['method_dur'] = tx_dur_default
                    # 如果是非法的
                    if tx_method['method'] not in ['all','w2w','s2s','l2l','run']:
                        raise ParserError('UnrecPBbTxM',tx_method['method'],str(i+1))
                    # 更新单位小节时长
                    this_TTS_engine.tx_method_specify(tx_method)
                # 输出对象
                result = self.synthesizer(this_TTS_engine, content=this_content, i=i)
                if result == 'Fatal':
                    # 完全无法正常合成
                    print(SynthesisError('FatalError'))
                    return False
                elif result == 'Empty':
                    # 小节无有效的文字，改为停留1秒
                    this_asterisk_synth['sound'] = 'NA'
                    this_asterisk_synth['time'] = 1.0
                else:
                    this_asterisk_synth['sound'] = "'" + result + "'"
                    this_audio_obj = Audio(result)
                    this_asterisk_synth['time'] = round(this_audio_obj.media.get_length(),2)
            else:
                if this_asterisk['sound'] in self.medias.keys():
                    # 已定义的媒体
                    this_audio_obj:Audio = self.medias[this_asterisk['sound']]
                elif os.path.isfile(this_asterisk['sound'][1:-1]):
                    # 指定的一个文件
                    this_audio_obj:Audio = Audio(this_asterisk['sound'][1:-1])
                this_asterisk_synth['sound'] = this_asterisk['sound']
                this_asterisk_synth['time'] = round(this_audio_obj.media.get_length(),2)
            # 将变更应用到rgl
            this_section['sound_set']['*'] = this_asterisk_synth
            this_section['sound_set'].pop('{*}')
        # 如果能正常的合成
        return True
    # 执行一次语音合成
    def synthesizer(self,TTS_engine:Aliyun_TTS_engine,content:str,i:int)->str:
        # 输出文件
        ofile = self.output_path +'/'+'auto_AU_%d'%i+'_'+mod62_timestamp()+'.wav'
        # 检查，是不是空文件
        if re.findall('\w+',content) == []:
            print(WarningPrint('EmptyText', str(i)))
            return 'Empty'
        for time_retry in range(1,6):
            # 最多重试5次
            try:
                # 执行合成
                TTS_engine.start(text=content,ofile=ofile)
                return ofile
            except Exception as E:
                # 如果出现了异常
                print(WarningPrint('SynthFail', str(i), str(time_retry), E))
        return 'Fatal'
    # 主流程
    def main(self)->RplGenLog:
        # 欢迎
        print(SynthPrint('Welcome',EDITION))
        print(SynthPrint('SaveAt',self.output_path))
        print(SynthPrint('SthBegin'))
        result = self.execute()
        print(SynthPrint('Refresh'))
        if result == True:
            print(SynthPrint('Done'))
        else:
            print(SynthPrint('Breaked'))
        return self.rgl