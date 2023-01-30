#!/usr/bin/env python
# coding: utf-8
# 异常定义

# 解析器错误

# 回声工坊核心的异常基类
class RplGenError(Exception):
    # lang: 0:en,1:zh
    lang = 0
    error_scripts = {
        'None'      :['',
                      ''],
        'ImportErr' :['{}. Execution terminated!',
                      '{}，程序运行终止！']
        }
    error_type = ["\x1B[31m[RplGenError]:\x1B[0m ",
                  "\x1B[31m[回声工坊错误]:\x1B[0m "]
    # init
    def __init__(self,key='None',*arguments):
        error_scripts_this = self.error_scripts[key][self.lang].format(*arguments)
        self.description = self.error_type[self.lang] + error_scripts_this
    def __str__(self):
        return self.description
# 参数错误，外部输出参数错误
class ArgumentError(RplGenError):
    error_scripts = {
        'MissInput'   :["Missing principal input argument!",
                        "缺失必要的输入参数！"],
        'FileNotFound':["Cannot find file： '{}'",
                        "找不到文件：'{}'"],
        'NeedOutput'  :["Some flags requires output path, but no output path is specified!",
                        "勾选的某个标志选项要求输出路径，但是并没有指定输出路径！"],
        'DirNotFound' :["Cannot find directory '{}'",
                        "找不到文件夹：'{}'"],
        'FrameRate'   :["Invalid frame rate:{}",
                        "指定了无效的帧率：{}"],
        'Resolution'  :["Invalid resolution:{}",
                        "指定了无效的分辨率：{}"],
        'BadInit'     :["Invalid initial status: {}",
                        "无效的初始化状态：{}"],
        'MustOutput'  :["No output path is specified!",
                        "没有指定输出路径！"],
        'MkdirErr'    :["Cannot make directory '{}'.",
                        "无法创建文件夹：'{}'"],
    }
    error_type = ["\x1B[31m[ArgumentError]:\x1B[0m ",
                  "\x1B[31m[参数错误]:\x1B[0m "]
# 解析错误，解析log错误
class ParserError(RplGenError):
    error_scripts = {
        'UnableDial'  :["Unable to parse as dialogue line, due to invalid syntax!",
                        "无法解析为对话行，由于错误的语法！"],
        'UnablePlace' :["Unable to parse this line, due to invalid syntax!",
                        "无法解析本行，由于错误的语法！"],
        'UnableSet'   :["Unable to parse as setting line, due to invalid syntax!",
                        "无法解析为设置行，由于错误的语法！"],
        'SwitchDial'  :["Unrecognized switch method: '{}' appeared in dialogue line {}.",
                        "无法识别动态切换效果“{}”，出现在了第{}行（对话行）中。"],
        '2muchAster'  :["Too much asterisk time labels are set in dialogue line {}.",
                        "在第{}行（对话行）中指定了多余一个星标语音框！"],
        '2muchChara'  :["Too much charactor is specified in dialogue line {}.",
                        "在第{}行（对话行）中指定了超过3个角色！"],
        'UndefName'   :["Undefined Name '{}' in dialogue line {}. due to: {}",
                        "未定义的角色名“{}”出现在第{}行（对话行）中，由于：{}"],
        'DupSubtype'  :["Duplicate subtype '{}' is set in charactor table!",
                        "差分名“{}”在角色表中重复出现！"],
        'UndefAnime'  :["Name '{}' is not defined, which is specified to '{}' as Animation!",
                        "媒体名“{}”尚未在媒体定义文件中定义，但其被指定给角色 '{}' 作为立绘！"],
        'CharaNoBb'   :["No bubble is specified to major charactor '{0}' of dialogue line {1}.",
                        "第{1}行的主要发言人“{0}”，缺失发言气泡！"],
        'InvalidKey'  :["Key '{0}' specified to ChatWindow object '{1}' is not exist!",
                        "指定给聊天窗对象“{1}”的关键字“{0}”并不存在！"],
        'CWUndepend'  :["ChatWindow object '{}' can not be used independently without a specified key!",
                        "聊天窗对象“{}”未指定关键字，无法单独赋予给角色作为气泡使用！"],
        'InvSymbpd'   :["Invalid symbol (pound mark or vertical bar) appeared in header text of charactor '{}'.",
                        "非法的符号（井号“#”和竖线“|”）出现在角色“{}”的头文本中！"],
        'UndefBubble' :["Name {} is not defined, which is specified to {} as Bubble!",
                        "媒体名“{}”尚未在媒体定义文件中定义，但其被指定给角色 '{}' 作为气泡！"],
        'NotBubble'   :["Media object '{}', which is specified to {} as Bubble, is not a Bubble!",
                        "媒体对象“{}”并非一个气泡类，但其被指定给角色“{}”作为气泡！"],
        'TgNotExist'  :["Target columns {0} specified to Bubble object '{1}' is not exist!",
                        "气泡对象“{1}”中指定的头文本目标列“{0}”，在角色表中并不存在！"],
        'MissMainTx'  :["Main_Text of '{}' is None!",
                        "气泡对象“{}”缺失主文本！"],
        'InvSymbqu'   :["Invalid symbol (double quote or backslash) appeared in speech text in dialogue line {}.",
                        "非法的符号（英文双引号“\"”和反斜杠“\\”）出现在第{}行（对话行）的发言文本中！"],
        'UnrecTxMet'  :["Unrecognized text display method: '{}' appeared in dialogue line {}.",
                        "无法识别的文字演示效果“{}”，出现在第{}行（对话行）中！"],
        'UnpreAster'  :["Unprocessed asterisk time label appeared in dialogue line {}. Add --SynthesisAnyway may help.",
                        "尚未处理的待合成星标 {{*}} 出现在第{}行（对话行）中！勾选标志选项“先执行语音合成”或许能起到帮助。"],
        'SEnotExist'  :["The sound effect '{0}' specified in dialogue line {1} is not exist!",
                        "在第{1}行（对话行）中指定的音效“{0}”并不存在！"],
        'ParErrDial'  :["Parse exception occurred in dialogue line {}.",
                        "解析异常发生在第{}行（对话行）。"],
        'UndefBackGd' :["The background '{0}' specified in background line {1} is not defined!",
                        "在第{1}行（背景行）中指定的背景“{0}”尚未在媒体定义文件中定义！"],
        'SwitchBkGd'  :["Unrecognized switch method: '{}' appeared in background line {}.",
                        "无法识别的动态切换效果“{}”出现在第{}行（背景行）中。"],
        'ParErrBkGd'  :["Parse exception occurred in background line {}.",
                        "解析异常发生在第{}行（背景行）。"],
        'UndefPAnime' :["The Animation '{0}' specified in animation line {1} is not defined!",
                        "在第{1}行（立绘行）指定的立绘对象“{0}”尚未在媒体定义文件中定义！"],
        'ParErrAnime' :["Parse exception occurred in animation line {}.",
                        "解析异常发生在第{}行（立绘行）。"],
        'InvaPBbExp'  :["The Bubble expression '{0}' specified in bubble line {1} is invalid syntax!",
                        "在第{1}行（气泡行）使用的气泡表达式“{0}”存在语法错误！"],
        'UnrecPBbTxM' :["Unrecognized text display method: '{}' appeared in bubble line {}.",
                        "无法识别的文字演示效果“{}”，出现在第{}行（气泡行）中！"],
        'UndefPBb'    :["The Bubble '{0}' specified in bubble line {1} is not defined!",
                        "在第{1}行（气泡行）指定的气泡对象“{0}”尚未在媒体定义文件中定义！"],
        'ParErrBb'    :["Parse exception occurred in bubble line {}.",
                        "解析异常发生在第{}行（气泡行）。"],
        'UndefBGM'    :["The BGM '{0}' specified in setting line {1} is not exist!",
                        "在第{1}行（设置行）指定的背景音乐“{0}”并不存在！"],
        'UnspFormula' :["Unsupported formula '{0}' is specified in setting line {1}.",
                        "在第{1}行（设置行）指定的曲线函数“{0}”是不被支持的！"],
        'ModUndefCol' :["Try to modify a undefined column '{}' in charactor table!'",
                        "试图在角色表中修改一个并不存在的列“{}”！"],
        'ModProtcCol' :["Try to modify a protected column '{}' in charactor table!'",
                        "试图在角色表中修改一个受保护的列“{}”！"],
        'ModCTError'  :["Error occurred while modifying charactor table: {}, due to: {}",
                        "尝试修改角色表中“{}”列时发生错误，由于：{}"],
        'UndefTgName' :["Target name '{0}' in setting line {1} is not undefined!",
                        "在第{1}行（设置行）尝试修改角色表中角色“{0}”的某一列，然而这个角色并未出现在角色表中！"],
        'UndefTgSubt' :["Target subtype '{0}' in setting line {1} is not undefined!",
                        "在第{1}行（设置行）尝试修改角色表中角色差分“{0}”的某一列，然而这个角色差分并未出现在角色表中！"],
        'UnsuppSet'   :["Unsupported setting '{0}' is specified in setting line {1}.",
                        "在第{1}行设置中尝试设置一个不被支持的项目“{0}”"],
        'IvSyFrPos'   :["Invalid Syntax '{0}' appeared while repositioning FreePos object '{1}', due to: {2}",
                        "在重新定位自由位置对象“{1}”是，出现了无效语法“{0}”，由于：{2}"],
        'ParErrSet'   :["Parse exception occurred in setting line {}.",
                        "解析异常发生在第{}行（设置行）。"],
        'ParErrHit'   :["Parse exception occurred in hitpoint line {}.",
                        "解析异常发生在第{}行（血条行）。"],
        'NoDice'      :["Invalid syntax, no dice args is specified!",
                        "语法错误，没有指定骰子参数！"],
        'ParErrDice'  :["Parse exception occurred in dice line {}.",
                        "解析异常发生在第{}行（骰子行）。"],
        'UnrecLine'   :["Unrecognized line: {}.",
                        "无法识别第{}行！"],
        'ParErrCompl' :["Exception occurred while completing the placed medias.",
                        "在终止放置媒体图层时，遭遇了异常。"],
        'BadAsterSE'  :["Asterisk SE file '{}' is not exist.",
                        "星标语音文件 '{}' 并不存在！"],
        'InvAster'    :["Invalid asterisk label appeared in dialogue line.",
                        "无效的星标语音框出现在对话行中！"],
        'ParErrWait'  :["Parse exception occurred in wait line {}.",
                        "解析异常发生在第{}行（暂停行）。"],
        'InvWaitArg'  :["Invalid argument for command <wait>: {}.",
                        "在 <wait> 命令中指定了非法的参数：{}"],
    }
    error_type = ["\x1B[31m[ParserError]:\x1B[0m ",
                  "\x1B[31m[解析错误]:\x1B[0m "]
# 渲染错误，渲染画面出现错误
class RenderError(RplGenError):
    error_scripts = {
        'UndefMedia'  :["Undefined media object : '{}'.",
                        "媒体对象“{}”未定义！"],
        'FailRender'  :["Failed to render '{}' as {}.",
                        "无法将对象“{}”渲染为{}。"],
        'FailPlay'    :["Failed to play audio '{}'.",
                        "无法播放音频 '{}'。"],
        'BreakFrame'  :['Render exception at frame: {}',
                        "渲染异常发生在第{}帧。"]
    }
    error_type = ["\x1B[31m[RenderError]:\x1B[0m ",
                  "\x1B[31m[渲染错误]:\x1B[0m "]
# 合成错误，语音合成未正常执行
class SynthesisError(RplGenError):
    error_scripts = {
        'CantBegin'   :["Speech synthesis cannot begin.",
                        "语音合成无法开始。"],
        'SynBreak'    :["Speech synthesis breaked, due to unresolvable error.",
                        "由于无法解决的错误，语音合成终止！"],
        'Unknown'     :["Unknown Exception.",
                        "未知错误。"],
        'FatalError'  :["An unresolvable error occurred during speech synthesis!",
                        "在语音合成过程中发生了一个无法解决的错误。"],
        'AliEmpty'    :["AliyunError: Synthesis failed, an empty wav file is created!",
                        "阿里云错误：语音合成失败，生成了一个空文件！"],
        'AliOther'    :["AliyunError: Other exception occurred!",
                        "阿里云错误：语音合成失败，发生了一个其他错误。"],
        'AliClose'    :["AliyunError: Close file failed since: {}",
                        "阿里云错误：关闭文件时失败，由于：{}"],
        'AliWrite'    :["AliyunError: Write data failed: {}",
                        "阿里云错误：写入文件时失败，由于：{}"],
        'AzuInvArg'   :["AzureError: Invalid Voice argument: '{}'",
                        "Azure错误：非法的音源名：“{}”"],
        'AzuErrRetu'  :["AzureError: {}",
                        "Azure错误：{}"],
    }
    error_type = ["\x1B[31m[SynthesisError]:\x1B[0m ",
                  "\x1B[31m[合成错误]:\x1B[0m "]
# 编码错误，输入文件的编码不支持
class DecodeError(RplGenError):
    error_scripts = {
        'DecodeErr':["{}","{}"]
    }
    error_type = ["\x1B[31m[DecodeError]:\x1B[0m ",
                  "\x1B[31m[编码错误]:\x1B[0m "]
# 语法错误，输入文件的语法错误
class SyntaxsError(RplGenError):
    error_scripts = {
        'OccName'     :["Obj name occupied!",
                        "媒体变量名已被占用！"],
        'InvaName'    :["Invalid Obj name!",
                        "非法的媒体变量名！"],
        'MediaDef'    :["{0} appeared in media define file line {1} is invalid syntax!",
                        "媒体定义文件第{1}行的“{0}”是错误的语法。"],
        'CharTab'     :["Unable to load charactor table: {}",
                        "无法载入角色配置表，由于：{}"],
        'MissCol'     :["missing necessary columns.",
                        "角色配置表缺失必要的列"],
    }
    error_type = ["\x1B[31m[SyntaxError]:\x1B[0m ",
                  "\x1B[31m[语法错误]:\x1B[0m "]
# 媒体错误，媒体定义的参数错误
class MediaError(RplGenError):
    error_scripts = {
        'ErrCovert'   :["Exception during converting '{}' : {}",
                        "在初始化媒体对象“{}”时出现异常：{}"],
        'ILineDist'   :["Invalid line distance: {}.",
                        "无效的文本行距：{}。"],
        'BadAlign'    :["Unsupported align: {}.",
                        "不支持的对齐模式：{}。"],
        'BnHead'      :["length of header params does not match!",
                        "头文本的各参数的长度不匹配！"],
        'InvSep'      :["Invalid bubble separate params: {}!",
                        "非法的气泡分割参数：{}"],
        'InvFill'     :["Invalid fill mode params: {}.",
                        "无效的填充模式：{}"],
        'CWKeyLen'    :["length of sub-key and sub-bubble does not match!",
                        "关键字和子气泡参数的长度不匹配！"],
        'Bn2CW'       :["Ballon object of key '{}' is not supported to be set as a sub-bubble of ChatWindow!",
                        "关键字“{}”对应的子气泡是气球对象，无法在聊天窗中作为子气泡！"],
        'DA2CW'       :["Dynamic Animations is not supported as sub-animations for ChatWindow!",
                        "动态立绘对象无法在聊天窗中作为子头像！"],
        'FileNFound'  :["Cannot find file match '{}'",
                        "'{}' 无法匹配到任何文件！"],
        'GAPrame'     :["length of subanimation params does not match!",
                        "子立绘对象和归零位置长度不匹配。"],
        'Undef2GA'    :["The Animation '{}' is not defined, which was tried to group into GroupedAnimation!",
                        "尝试编入组合立绘的立绘名“{}”尚未在媒体定义文件中定义！"],
        'DA2GA'       :["Trying to group a dynamic Animation '{}' into GroupedAnimation!",
                        "动态立绘对象“{}”无法编入组合立绘！"],
        'InvHPArg'    :["Invalid argument ({}) for BIAnime hitpoint!",
                        "({})对于内建动画-生命值，是非法参数。"],
        'InvDCSytx'   :["Invalid syntax:{}, {}",
                        "语法错误：{}，由于：{}"],
        'InvDCArg'    :["Invalid argument ({}) for BIAnime dice!",
                        "({})对于内建动画-骰子，是非法参数。"],
        'BadAudio'    :["Unsupported audio files '{}'",
                        "不支持的音频文件 '{}'"],
        'InvEgWd'     :["Invalid edge width {} for StrokeText!",
                        "为描边文本指定的描边宽度 {} 是非法的值！"],
        'InvFit'      :["Invalid fit axis '{}' for DynamicBubble!",
                        "无效的自适应气泡的适应方向：{}"],
    }
    error_type = ["\x1B[31m[MediaError]:\x1B[0m ",
                  "\x1B[31m[媒体错误]:\x1B[0m "]
# 忽略输入文件
class IgnoreInput(RplGenError):
    error_scripts = {'None':['[speech synthesizer]: Preview Only!',
                             '[语音合成]:仅试听！']}
    error_type = ['','']
    pass

class Print:
    # lang: 0:en,1:zh
    lang = 0
    # 模块
    info_scripts = {}
    info_type = ['','']
    def __init__(self,key,*arguments):
        info_scripts_this = self.info_scripts[key][self.lang].format(*arguments)
        self.description = self.info_type[self.lang] + info_scripts_this
    def __str__(self):
        return self.description

class MainPrint(Print):
    info_scripts = {
        'Welcome'     :["Welcome to use TRPG-replay-generator {}",
                        "欢迎使用回声工坊 {}"],
        'SythAnyway'  :["Flag --SynthesisAnyway detected, running command:",
                        "检测到标志选项：“先执行语音合成”，执行指令："],
        'LoadMedef'   :["Loading media definition file.",
                        "正在载入媒体定义文件。"],
        'LoadChrtab'  :["Loading charactor table.",
                        "正在载入角色配置表。"],
        'LoadRGL'     :["Parsing Log file.",
                        "正在解析Log文件。"],
        'OutTime'     :["The timeline file will be save at '{}'.",
                        "时间轴文件将保存至路径：'{}'"],
        'ExportXML'   :["Flag --ExportXML detected, running command:",
                        "检测到标志选项：“导出为PR项目”，执行指令："],
        'ExportMp4'   :["Flag --ExportVideo detected, running command:",
                        "检测到标志选项：“导出为.mp4视频”，执行指令："],
        # exit
        'Error'       :["A major error occurred. Execution terminated!",
                        "出现了一个重大错误，程序执行终止！"],
        'User'        :["Display terminated, due to user commands.",
                        "由于用户操作，演示终止。"],
        'Video'       :["Video exported. Execution terminated!",
                        "导出视频，而非直接演示，程序终止。"],
        'End'         :["Display finished!",
                        "演示完毕！"],
    }
    info_type = ["[replay generator]: ",
                 "[回声工坊]: "]
class SynthPrint(Print):
    info_scripts = {
        'Welcome'     :["Welcome to use speech_synthesizer for TRPG-replay-generator {}",
                        "欢迎使用回声工坊，语音合成模块 {}"],
        'SaveAt'      :["The backup Logfile and audio file will be saved at '{}'",
                        "备份的原始Log文件与合成的音频文件将会保存至文件夹：'{}'"],
        'SthBegin'    :["Begin to speech synthesis!",
                        "开始执行语音合成！"],
        'OriBack'     :["Original LogFile backup path: '{}'",
                        "原始Log文件备份路径：'{}'"],
        'Refresh'     :["Logfile refresh Done!",
                        "Log文件更新完毕！"],
        'Breaked'     :["Synthesis Breaked, due to FatalError!",
                        "语音合成中断，由于无法解决的错误。"],
        'Done'        :["Synthesis Done!",
                        "语音合成完毕！"],
    }
    info_type = ["[speech synthesizer]: ",
                 "[语音合成]: "]
class PrxmlPrint(Print):
    info_scripts = {
        'Welcome'     :["Welcome to use exportXML for TRPG-replay-generator {}",
                        "欢迎使用回声工坊，导出PR工程模块 {}"],
        'SaveAt'      :["The output xml file and refered png files will be saved at '{}'",
                        "输出的xml工程文件及其引用的图片将会保存至文件夹：'{}'"],
        'ExpBegin'    :["Begin to export.",
                        "开始导出！"],
        'Done'        :["Done! XML path : '{}'",
                        "导出完毕！XML工程文件的路径：'{}'"],
    }
    info_type = ["[export XML]: ",
                 "[导出PR工程]: "]
class VideoPrint(Print):
    info_scripts = {
        'Welcome'     :["Welcome to use exportVideo for TRPG-replay-generator {}",
                        "欢迎使用回声工坊，导出视频模块 {}"],
        'SaveAt'      :["The output mp4 file will be saved at '{}'.",
                        "输出的MP4视频将会保存至文件夹：'{}'"],
        'VideoBegin'  :["Start mixing audio tracks.",
                        "开始混合音频轨道，这可能需要一些时间。"],
        'TrackDone'   :["Track {} finished.",
                        "轨道 {} 混合完毕！"],
        'AudioDone'   :["Audio mixing done!",
                        "音频混合完毕！"],
        'EncoStart'   :["Start encoding video, using ffmpeg.",
                        "开始编码视频流，使用ffmpeg。"],
        'Progress'    :["{0} {1} {2}/{3} {4}",
                        "{0} {1} {2}/{3} {4}"],
        'CostTime'    :["Export time elapsed : {}",
                        "导出耗时：{}"],
        'RendSpeed'   :["Mean frames rendered per second : {} FPS",
                        "平均渲染速度：{} 帧/秒"],
        'Done'        :["Encoding finished! Video path : {}",
                        "编码完毕！视频文件路径：'{}'"],
    }
    info_type = ["[export Video]: ",
                 "[导出视频]: "]
class CMDPrint(Print):
    info_scripts = {
        'Command'     :["\x1B[32m{}\x1B[0m",
                        "\x1B[32m{}\x1B[0m"],
        'BreakLine'   :["\x1B[32m------------------------------------------------------------\x1B[0m",
                        "\x1B[32m------------------------------------------------------------\x1B[0m"],
    }
    info_type = ['','']
class WarningPrint(Print):
    # 警告文本
    info_scripts = {
        'HighFPS'     :["FPS is set to {}, which may cause lag in the display!",
                        "帧率被设置为{}，这可能会导致在演示时出现卡顿！"],
        'HighRes'     :["Resolution is set to more than 3M, which may cause lag in the display!",
                        "分辨率被设置超过300万像素，这可能导致在演示时出现卡顿！"],
        'FailAster'   :["Failed to load asterisk time in dialogue line {}.",
                        "无法载入第{}行（对话行）中的星标音频的时间。"],
        'UndeclMB'    :["Undeclared manual break dialogue line {}.",
                        "第{}行（对话行）中存在未声明的手动换行符；请留意是否是符号误用。"],
        'More4line'   :["More than 4 lines will be displayed in dialogue line {}.",
                        "第{}行（对话行）的文本内容将会超过4行；请注意气泡是否能容纳该行数的文本。"],
        'MBExceed'    :["Manual break line length exceed the Bubble line_limit in dialogue line {}.",
                        "第{}行（对话行）由于手动换行，单行字数超出了气泡主文本的设置的单行字数限制；请注意超出气泡范围的文字将不会显示！"],
        'PAmMetDrop'  :["The switch method of placed animation is dropped, due to short duration!",
                        "指定给放置立绘的切换效果失效，因为小节过短的持续时间。"],
        'PBbMetDrop'  :["The switch method of placed bubble is dropped, due to short duration!",
                        "指定给放置气泡的切换效果失效，因为小节过短的持续时间。"],
        'Set2Invalid' :["Setting {} to invalid value {}, the argument will not changed.",
                        "尝试将动态变量 {} 设置为非法值 {} ，该变量将不会发生改变。"],
        'UseLambda'   :["Using lambda formula range {0} in line {1}, which may cause unstableness during displaying!",
                        "在第{1}行（设置行）中，曲线函数被设置为一个取值范围是 {0} 的 lambda 函数，这可能导致演示中的不稳定表现！"],
        'ClearUndef'  :["Trying to clear an undefined object '{}'.",
                        "尝试清空一个未定义的对象名“{}”。"],
        'ClearNotCW'  :["Trying to clear object '{}', which is not a ChatWindow.",
                        "尝试清空一个媒体对象“{}”，但是这个对象并非聊天窗对象！"],
        'NoValidSyth' :["No valid asterisk label synthesised!",
                        "没有找到任何有效的待合成星标，无法语音合成。"],
        'UFT8BOM'     :["UTF8 BOM recognized, it will be drop from the begin of file!",
                        "在文件的开头识别到 UTF8 BOM ，其将自动无视。"],
        'XMLFail'     :["Failed to export XML, due to: {}",
                        "无法导出为PR xml 工程，由于：{}"],
        'Mp4Fail'     :["Failed to export Video, due to: {}",
                        "无法导出为视频，由于：{}"],
        'FixScrZoom'  :["OS exception, --FixScreenZoom is only avaliable on windows system!",
                        "系统异常！标志选项“取消系统缩放”仅在windows系统可用！"],
        'AlphaText'   :["The transparency of text and edge may not be displayed normally, due to the limit of pygame!",
                        "由于图形引擎pygame的固有限制，描边文本的透明度表现可能出现些许异常。"],
        'LineDist'    :["Line distance is set to less than 1!",
                        "主文本行距被设置为小于1！"],
        'BadBGMFmt'   :["A not recommend music format '{}' is specified, which may cause unstableness during displaying!",
                        "指定了一个不被建议使用的音频格式 “{}”，这可能导致演示过程中的不稳定表现！"],
        'DefAsterSE'  :["A defined object '{}' is specified, which will not be processed.",
                        "在音效框中指定了一个音频媒体对象，语音合成模块将会无条件无视这种音效框。"],
        'UndefChar'   :["Undefine charactor: {}!",
                        "未定义的角色：{}"],
        'CharNoVoice' :["No voice is specified for '{}'.",
                        "未给角色“{}”指定一个有效的发音人名。"],
        'SynthFail'   :["Synthesis failed in line {}({}), due to: {}",
                        "第{}行（尝试次数：{}）语音合成失败，由于：{}"],
        'BadSpeaker'  :["Unsupported speaker name '{}'.",
                        "不支持的发音人名：“{}”"],
        'PrevFail'    :["Synthesis failed in preview, due to: {}",
                        "试听时语音合成失败，由于：{}"],
        'AuPlayFail'  :["Failed to play the audio, due to: {}",
                        "无法播放音频，由于：{}"],
        'SaveFail'    :["Failed to save the file, due to: {}",
                        "无法保存文件，由于：{}"],
        'MissVoice'   :["Missing 'Voice' columns.",
                        "角色表中缺失“Voice”列！"],
        'No2Synth'    :["No valid asterisk label synthesised, execution terminated!",
                        "没有找到任何有效的待合成星标，无法语音合成，程序执行终止！"],
        'SynthNBegin' :["Speech synthesis cannot begin, execution terminated!",
                        "语音合成无法开始，程序执行终止！"],
        'BadAuLen'    :["Unable to get audio length of '{}', due to: {}",
                        "无法获取音频文件 '{}' 的持续时长，由于：{}"],
        'BadClip'     :["Unable to clip the silence part from '{}', due to: {}",
                        "无法从音频文件 '{}' 中剪切静音片段，由于：{}"],
        'BGMIgnore'   :["BGM '{}' is automatically ignored, you should add BGM manually in Premiere Pro later.",
                        "背景音乐 “{}” 被自动地忽略了！你应该稍后在Premiere Pro软件中手动添加背景音乐。"],
        'BadAuFile'   :["Audio file '{}' is not exist.",
                        "音频文件 '{}' 并不存在！"],
        'WideEdge'    :["The edge width is set to more than 3, which may cause unintended results.",
                        "描边宽度被设置超过3，这可能导致意料之外的显示效果。"]
    }
    # 类型：警告
    info_type = ["\x1B[33m[warning]:\x1B[0m ",
                 "\x1B[33m[警告]:\x1B[0m "]