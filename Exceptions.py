#!/usr/bin/env python
# coding: utf-8
# 异常定义

# 解析器错误

# 回声工坊核心的异常基类
class RplGenError(Exception):
    # lang: 0:en,1:zh
    lang = 0
    error_scripts = {
        'None'     :['',''],
        'ImportErr':['{}. Execution terminated!']
        }
    error_type = ["\x1B[31m[RplGenError]:\x1B[0m "]
    # init
    def __init__(self,key='None',*arguments):
        error_scripts_this = self.error_scripts[key][self.lang].format(*arguments)
        self.description = self.error_type[self.lang] + error_scripts_this
    def __str__(self):
        return self.description
# 参数错误，外部输出参数错误
class ArgumentError(RplGenError):
    error_scripts = {
        'MissInput'   :["Missing principal input argument!"],
        'FileNotFound':["Cannot find file {}"],
        'NeedOutput'  :["Some flags requires output path, but no output path is specified!"],
        'DirNotFound' :["Cannot find directory {}"],
        'FrameRate'   :["Invalid frame rate:{}"],
        'Resolution'  :["Invalid resolution:{}"],
        'BadInit'     :["Invalid initial status: {}"],
        'MustOutput'  :["No output path is specified!"],
        'MkdirErr'    :["Cannot make directory {}."],
    }
    error_type = ["\x1B[31m[ArgumentError]:\x1B[0m "]
# 解析错误，解析log错误
class ParserError(RplGenError):
    error_scripts = {
        'UnableDial' :["Unable to parse as dialogue line, due to invalid syntax!"],
        'UnablePlace':["Unable to parse as {} line, due to invalid syntax!"],
        'UnableSet'  :["Unable to parse as setting line, due to invalid syntax!"],
        'SwitchDial' :["Unrecognized switch method: \"{}\" appeared in dialogue line {}."],
        '2muchAster' :["Too much asterisk time labels are set in dialogue line {}."],
        '2muchChara' :["Too much charactor is specified in dialogue line {}."],
        'UndefName'  :["Undefined Name {} in dialogue line {}. due to: {}"],
        'DupSubtype' :["Duplicate subtype {} is set in charactor table!"],
        'UndefAnime' :["Name {} is not defined, which is specified to {} as Animation!"],
        'CharaNoBb'  :["No bubble is specified to major charactor {} of dialogue line {}."],
        'InvalidKey' :["Key '{}' specified to ChatWindow object '{}' is not exist!"],
        'CWUndepend' :["ChatWindow object '{}' can not be used independently without a specified key!"],
        'InvSymbpd'  :["Invalid symbol (pound mark or vertical bar) appeared in header text of charactor '{}'."],
        'UndefBubble':["Name {} is not defined, which is specified to {} as Bubble!"],
        'NotBubble'  :["Media object '{}', which is specified to {} as Bubble, is not a Bubble!"],
        'TgNotExist' :["Target columns {} specified to Bubble object '{}' is not exist!"],
        'MissMainTx' :["Main_Text of '{}' is None!"],
        'InvSymbqu'  :["Invalid symbol (double quote or backslash) appeared in speech text in dialogue line {}."],
        'UnrecTxMet' :["Unrecognized text display method: '{}' appeared in dialogue line {}."],
        'UnpreAster' :["Unprocessed asterisk time label appeared in dialogue line {}. Add --SynthesisAnyway may help."],
        'SEnotExist' :["The sound effect '{}' specified in dialogue line {} is not exist!"],
        'ParErrDial' :["Parse exception occurred in dialogue line {}."],
        'UndefBackGd':["The background '{}' specified in background line {} is not defined!"],
        'SwitchBkGd' :["Unrecognized switch method: '{}' appeared in background line {}."],
        'ParErrBkGd' :["Parse exception occurred in background line {}."],
        'UndefPAnime':["The Animation '{}' specified in animation line {} is not defined!"],
        'ParErrAnime':["Parse exception occurred in animation line {}."],
        'InvaPBbExp' :["The Bubble expression '{}' specified in bubble line {} is invalid syntax!"],
        'UnrecPBbTxM':["Unrecognized text display method: '{}' appeared in bubble line {}."],
        'UndefPBb'   :["The Bubble '{}' specified in bubble line {} is not defined!"],
        'ParErrBb'   :["Parse exception occurred in bubble line {}."],
        'UndefBGM'   :["The BGM '{}' specified in setting line {} is not exist!"],
        'UnspFormula':["Unsupported formula '{}' is specified in setting line {}."],
        'ModUndefCol':["Try to modify a undefined column '{}' in charactor table!'"],
        'ModProtcCol':["Try to modify a protected column '{}' in charactor table!'"],
        'ModCTError' :["Error occurred while modifying charactor table: {}, due to: {}"],
        'UndefTgName':["Target name '{}' in setting line {} is not undefined!"],
        'UndefTgSubt':["Target subtype '{}' in setting line {} is not undefined!"],
        'UnsuppSet'  :["Unsupported setting '{}' is specified in setting line {}."],
        'IvSyFrPos'  :["Invalid Syntax '{}' appeared while repositioning FreePos object '{}', due to: {}"],
        'ParErrSet'  :["Parse exception occurred in setting line {}."],
        'ParErrHit'  :["Parse exception occurred in hitpoint line {}."],
        'NoDice'     :["Invalid syntax, no dice args is specified!"],
        'ParErrDice' :["Parse exception occurred in dice line {}."],
        'UnrecLine'  :["Unrecognized line: {}."],
        'ParErrCompl':["Exception occurred while completing the placed medias."],
        'BadAsterSE' :["Asterisk SE file '{}' is not exist."],
        'InvAster'   :["Invalid asterisk lable appeared in dialogue line."],
    }
    error_type = ["\x1B[31m[ParserError]:\x1B[0m "]
# 渲染错误，渲染画面出现错误
class RenderError(RplGenError):
    error_scripts = {
        'UndefMedia' :["Undefined media object : '{}'."],
        'FailRender' :["Failed to render '{}' as {}."],
        'FailPlay'   :["Failed to play audio '{}'."],
        'BreakFrame' :['Render exception at frame: {}']
    }
    error_type = ["\x1B[31m[RenderError]:\x1B[0m "]
# 合成错误，语音合成未正常执行
class SynthesisError(RplGenError):
    error_scripts = {
        'CantBegin'  :['Speech synthesis cannot begin.'],
        'SynBreak'   :['Speech synthesis breaked, due to unresolvable error.'],
        'Unknown'    :['Unknown Exception.'],
        'FatalError' :['An unresolvable error occurred during speech synthesis!'],
        'AliEmpty'   :["AliyunError: Synthesis failed, an empty wav file is created!"],
        'AliOther'   :["AliyunError: Other exception occurred!"],
        'AliClose'   :["AliyunError: Close file failed since: {}"],
        'AliWrite'   :["AliyunError: Write data failed: {}"],
        'AzuInvArg'  :["AzureError: Invalid Voice argument: {}"],
        'AzuErrRetu' :["AzureError: {}"],
    }
    error_type = ["\x1B[31m[SynthesisError]:\x1B[0m "]
# 编码错误，输入文件的编码不支持
class DecodeError(RplGenError):
    error_scripts = {
        'DecodeErr':["{}"]
    }
    error_type = ["\x1B[31m[DecodeError]:\x1B[0m "]
# 语法错误，输入文件的语法错误
class SyntaxsError(RplGenError):
    error_scripts = {
        'OccName'  :['Obj name occupied!'],
        'InvaName' :['Invalid Obj name!'],
        'MediaDef' :["{} appeared in media define file line {} is invalid syntax!"],
        'CharTab'  :["Unable to load charactor table: {}"],
        'MissCol'  :["missing necessary columns."],
    }
    error_type = ["\x1B[31m[SyntaxError]:\x1B[0m "]
# 媒体错误，媒体定义的参数错误
class MediaError(RplGenError):
    error_scripts = {
        'ErrCovert' :["Exception during converting {} : {}"],
        'ILineDist' :["Invalid line distance: {}."],
        'BadAlign'  :["Unsupported align: {}."],
        'BnHead'    :["length of header params does not match!"],
        'InvSep'    :["Invalid bubble separate params: {}!"],
        'InvFill'   :["Invalid fill mode params: {}."],
        'CWKeyLen'  :["length of sub-key and sub-bubble does not match!"],
        'Bn2CW'     :["Ballon object '{}' is not supported to be set as a sub-bubble of ChatWindow!"],
        'DA2CW'     :["Dynamic Animations is not supported as sub-animations for ChatWindow!"],
        'FileNFound':["Cannot find file match {}"],
        'GAPrame'   :["length of subanimation params does not match!"],
        'Undef2GA'  :["The Animation '{}' is not defined, which was tried to group into GroupedAnimation!"],
        'DA2GA'     :["Trying to group a dynamic Animation '{}' into GroupedAnimation!"],
        'InvHPArg'  :["Invalid argument ({}) for BIAnime hitpoint!"],
        'InvDCSytx' :["Invalid syntax:{}, {}"],
        'InvDCArg'  :["Invalid argument ({}) for BIAnime dice!"],
        'BadAudio'  :["Unsupported audio files {}"],
    }
    error_type = ["\x1B[31m[MediaError]:\x1B[0m "]
# 忽略输入文件
class IgnoreInput(RplGenError):
    error_scripts = {'None':['[speech synthesizer]: Preview Only!','']}
    error_type = ['']
    pass

class Print:
    # lang: 0:en,1:zh
    lang = 0
    # 模块
    info_scripts = {}
    info_type = ['']
    def __init__(self,key,*arguments):
        info_scripts_this = self.info_scripts[key][self.lang].format(*arguments)
        self.description = self.info_type[self.lang] + info_scripts_this
    def __str__(self):
        return self.description

class MainPrint(Print):
    info_scripts = {
        'Welcome'   :["Welcome to use TRPG-replay-generator {}"],
        'SythAnyway':["Flag --SynthesisAnyway detected, running command:"],
        'LoadMedef' :["Loading media definition file."],
        'LoadChrtab':["Loading charactor table."],
        'LoadRGL'   :["Parsing Log file."],
        'OutTime'   :["The timeline and breakpoint file will be save at '{}'."],
        'ExportXML' :["Flag --ExportXML detected, running command:"],
        'ExportMp4' :["Flag --ExportVideo detected, running command:"],
        # exit
        'Error'     :["A major error occurred. Execution terminated!"],
        'User'      :["Display terminated, due to user commands."],
        'Video'     :["Video exported. Execution terminated!"],
        'End'       :["Display finished!"],
    }
    info_type = ["[replay generator]: "]
class SynthPrint(Print):
    info_scripts = {
        'Welcome' :["Welcome to use speech_synthesizer for TRPG-replay-generator {}"],
        'SaveAt'  :["The processed Logfile and audio file will be saved at '{}'"],
        'SthBegin':["Begin to speech synthesis!"],
        'OriBack' :["Original LogFile backup path: '{}'"],
        'Refresh' :["Logfile refresh Done!"],
        'Breaked' :["Synthesis Breaked, due to FatalError!"],
        'Done'    :["Synthesis Done!"],
    }
    info_type = ["[speech synthesizer]: "]
class PrxmlPrint(Print):
    info_scripts = {
        'Welcome' :["Welcome to use exportXML for TRPG-replay-generator {}"],
        'SaveAt'  :["The output xml file and refered png files will be saved at '{}'"],
        'ExpBegin':["Begin to export."],
        'Done'    :["Done! XML path : '{}'"],
    }
    info_type = ["[export XML]: "]
class VideoPrint(Print):
    info_scripts = {
        'Welcome'   :["Welcome to use exportVideo for TRPG-replay-generator {}"],
        'SaveAt'    :["The output mp4 file will be saved at '{}'."],
        'VideoBegin':["Start mixing audio tracks."],
        'TrackDone' :["Track {} finished."],
        'AudioDone' :["Audio mixing done!"],
        'EncoStart' :["Start encoding video, using ffmpeg."],
        'Progress'  :["[{0}] {1},\t{2}/{3}"],
        'CostTime'  :["Export time elapsed : {}"],
        'RendSpeed' :["Mean frames rendered per second : {} FPS"],
        'Done'      :["Encoding finished! Video path : {}"],
    }
    info_type = ["[export Video]: "]
class CMDPrint(Print):
    info_scripts = {
        'Command'  :["\x1B[32m{}\x1B[0m"],
        'BreakLine':["\x1B[32m------------------------------------------------------------\x1B[0m"],
    }
    info_type = ['']
class WarningPrint(Print):
    # 警告文本
    info_scripts = {
        'HighFPS'    :["FPS is set to {}, which may cause lag in the display!"],
        'HighRes'    :["Resolution is set to more than 3M, which may cause lag in the display!"],
        'FailAster'  :["Failed to load asterisk time in dialogue line {}."],
        'UndeclMB'   :["Undeclared manual break dialogue line {}."],
        'More4line'  :["More than 4 lines will be displayed in dialogue line {}."],
        'MBExceed'   :["Manual break line length exceed the Bubble line_limit in dialogue line {}."],
        'PAmMetDrop' :["The switch method of placed animation is dropped, due to short duration!"],
        'PBbMetDrop' :["The switch method of placed bubble is dropped, due to short duration!"],
        'Set2Invalid':["Setting {} to invalid value {}, the argument will not changed."],
        'UseLambda'  :["Using lambda formula range {} in line {}, which may cause unstableness during displaying!"],
        'ClearUndef' :["Trying to clear an undefined object '{}'."],
        'ClearNotCW' :["Trying to clear object '{}', which is not a ChatWindow."],
        'NoValidSyth':["No valid asterisk label synthesised!"],
        'UFT8BOM'    :["UTF8 BOM recognized in MediaDef, it will be drop from the begin of file!"],
        'XMLFail'    :["Failed to export XML, due to: {}"],
        'Mp4Fail'    :["Failed to export Video, due to: {}"],
        'FixScrZoom' :["OS exception, --FixScreenZoom is only avaliable on windows system!"],
        'AlphaText'  :["The transparency of text and edge may not be displayed normally, due to the limit of pygame!"],
        'LineDist'   :["Line distance is set to less than 1!"],
        'BadBGMFmt'  :["A not recommend music format '{}' is specified, which may cause unstableness during displaying!"],
        'DefAsterSE' :["A defined object '{}' is specified, which will not be processed."],
        'UndefChar'  :["Undefine charactor!"],
        'CharNoVoice':["No voice is specified for '{}'."],
        'SynthFail'  :["Synthesis failed in line {}({}), due to: {}"],
        'BadSpeaker' :["Unsupported speaker name '{}'."],
        'PrevFail'   :["Synthesis failed in preview, due to: {}"],
        'AuPlayFail' :["Failed to play the audio, due to: {}"],
        'SaveFail'   :["Failed to save the file, due to: {}"],
        'MissVoice'  :["Missing 'Voice' columns."],
        'No2Synth'   :["No valid asterisk label synthesised, execution terminated!"],
        'SynthNBegin':["Speech synthesis cannot begin, execution terminated!"],
        'BadAuLen'   :["Unable to get audio length of '{}', due to: {}"],
        'BadClip'    :["Unable to clip the silence part from '{}', due to: {}"],
        'BGMIgnore'  :["BGM '{}' is automatically ignored, you should add BGM manually in Premiere Pro later."],
        'BadAuFile'  :["Audio file '{}' is not exist."]
    }
    # 类型：警告
    info_type = ["\x1B[33m[warning]:\x1B[0m "]