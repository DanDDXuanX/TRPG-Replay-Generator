#!/usr/bin/env python
# coding: utf-8

from ttkbootstrap.localization import MessageCatalog
# 多语言支持

# regex: (".*[\u4e00-\u9fff]+.*?")|('.*[\u4e00-\u9fff]+.*?')

# TODO: 未来有时间了再弄吧

class Translate:
    locale_dictionary = {
        'zh_cn':[
            ('Current','当前'),
            ('New','新的'),
            ('Hue','色相'),
            ('Sat','饱和'),
            ('Lum','明度'),
            ('Hex','16位'),
            ('Red','红'),
            ('Green','绿'),
            ('Blue','蓝'),
            ('Advanced','高级'),
            ('Themed','主题'),
            ('Standard','标准'),
            ('Color Chooser','选择颜色'),
        ]
    }
    dictionary = {
        'en':{
            '否' : 'No',
            '是' : 'Yes',
            '警告': 'Warning',
            '错误': 'Error',
            '确定': 'OK',
            '取消': 'Cancel',
            '复制': 'Copy',
            '保存': 'Save',
            '试听': 'Play',
            '：':':',
            '首选项': "Preference",
            '项目'  : "Projects",
            '脚本'  : "Scripts",
            '控制台': "Terminal",
            '传送门': "Portal",
            '回声工坊'  : 'RplGen Studio',
            '点亮创意火花': 'Kindle the flame of imaginative brilliance',
            '打开项目'  : 'Open Project',
            '新建空白项目'  : 'New Empty Project',
            '新建智能项目'  : 'New Intel Project',
            '保存项目'      :  'Save Project',
            '项目设置'      : 'Project Setting',
            '导入工程文件'   : 'Import Scripts',
            '导出工程文件'   : 'Export Scripts',
            '关闭项目'      : 'Close Project',
            '最近项目：'    : 'Recent:',
            '清除'      : 'clear',
            '无记录'        : 'No recode',
            '运行脚本'      : 'Run Scripts',
            '重置'  : 'Reset',
            '终止'  : 'Interrupt',
            '正则'      : 'regex',
            '搜索'      : 'search',
            '替换'      : 'replace',
            '全部替换'  : 'replace all',
            '(无)'      : '(None)',
            '媒体库'    : 'Media library',
            '角色配置'  : 'Character Config',
            '剧本文件'  : 'RplGenLog Files',
            '新增+'      : 'add+',
            '选择'  : 'select',
            '粘贴'  : 'paste',
            '属性'  : 'attributes',
            '全选'  : 'select all',
            '从[{}]粘贴' : 'Paste from [{}]',
            '文件已存在' : 'File Exist',
            '放弃导入': 'Give up',
            '继续导入': 'Continue',
            '格式错误': 'Format Error',
            '找不到文件': 'File Not Found',
            '修改': 'Modify',
            '导入文件': 'Import File',
            '导出成功': 'Export Done',
            '导出失败': 'Export Failed',
            '保存成功': 'Saved',
            '重命名' : 'Rename',
            '删除'  : 'Delete',
            '音源名：': 'Voice:',
            '语速：': 'SR:',
            '语调：': 'PR:',
            '风格：': 'style:',
            '强度：': 'degree:',
            '扮演：': 'role:',
            '选择音源' : 'Select Voice',
            '测试文本' : 'Text for text',
            '角色' : 'CTB',
            '媒体' : 'MDF',
            '剧本' : 'RGL',
            '播放预览' : 'Play Preview',
            '语音合成' : 'Speech Synthesis',
            '导出PR项目': 'Export PR Project',
            '导出视频' : 'Export Video',
            '新建差分' : 'New_Subtype',
            '立绘：' : 'Animation: ',
            '气泡：' : 'Bubble: ',
            '语音：' : 'Voice: ',
            '透明度' : 'alpha',
            '运动' : 'motion',
            '方向' : 'dirction',
            '尺度' : 'scale',
            '进出' : 'in&out',
            '重新定位媒体' : 'Relink Medias',
            "{}（自定义）": '{} (Custom)',
            '添加+': 'Add+',
            '删除-': 'Del-',
            '重名' : 'Duplicate Name',
            '非法名' : 'Invalid Name',
            '新建自定义列' : 'New Custom',
            '从文件夹中打开一个现有的项目。':'Open a project from local files.',
            '创建一个空白的项目，导入回声工坊1.0版本的工程文件，或者从头开始创建你的项目。':'Create an empty project and start from scratch, or load existing scripts.',
            '选择样式模板，智能解析导入聊天记录或者染色器log文件，直接创建一个半成品项目。':'Select a template, import raw chat logs, and create a semi-finished project.',
            '必须要选择一个文件夹用于保存项目文件！': 'Must choose a directory to save the project files.',
            '分辨率或帧率是非法的数值！': 'Resolution or frame rate is invalid!',
            '项目名中不能包含符号 {} ！': 'The project name cannot contain {} !',
            '目录下已经存在重名的项目文件，要覆盖吗？': 'There exist a project with the same name in the directory, overwrite?',
            '无法保存文件到：\n{}' : 'Cannot save files to:\n{}',
            '该预设模板可能已经损坏！': 'This template may have been corrupted!',
            '必须要选择样式模板！': 'Must choose a template for project!',
            '你正在尝试向智能项目中导入一个RGL文件！\n但是，智能项目并非设计用于导入RGL，可能出现异常。\n如果你已经拥有RGL文件，请新建空白项目，再导入文件！': 'You are trying to import an RGL file!\nHowever, intel projects are not designed to import RGL.\nIf you already have an RGL file, create a blank project instead.',
            '无法解读导入文件的编码！\n请确定导入的是文本文件？': 'Cannot decode the imported file. Please make sure to import a text file!',
            '找不到导入的剧本文件，请检查文件名！': 'File not found! Please check the file name.',
            '当前着色器无法解析导入文本的结构！': 'Current parser cannot parse the text struct.',
            '在导入文本时发生了异常！': 'Error occurred while loading log file.',
            '设置首选项时发生了如下错误！\n': 'Error occurred while modifying preference:\n',
            '已经成功设置首选项！\n主题变更需要重启程序后才会生效':'Preferences have been modified.\nTheme changes need restart to take effect.',
            '首选项已经重置为默认值！': 'Preference has been reset to default.',
            '导入失败，无法读取该文件！': 'Import failed, cannot read the file.',
            '导入如下文件：\n': 'Import the following files:\n',
            "向剧本文件中添加新剧本【{fn}】，包含{ct}个小节。": 'Add new RGL file [{fn}] to RGL library, containing {ct} sections.',
            "向角色配置中导入新角色{nc}个；新增角色差分{ct}个。": "Add {nc} new characters to Character Config, add {ct} new subtype.",
            "向角色配置中导入新角色{nc}个；新增角色差分{ct}个，更新角色差分{cr}个。":"Add {nc} new characters to Character Config, add {ct} new subtype, update {cr} subtype.",
            "向媒体库中导入媒体对象{ct}个。": "Add {ct} new media objects to Media Library.",
            "向媒体库中导入媒体对象{ct}个；更新媒体对象{cr}个。": "Add {ct} new media objects and update {cr} media objects to Media Library.",
            '成功将工程导出为脚本文件！\n导出路径：{}':'Successfully export as script file!\nExport path: {}',
            '无法将工程导出！\n由于：{}': 'Cannot export as script file!\nDue to: {}',
            "保存【{p}】时出现异常：{w}": 'Error occurred while saving RGL [{p}]: {w}',
            '\n在异常得到解决前，上述剧本文件的变更将无法得到保存！': '\nChanges to RGL above cannot be saved until these issues are resolved!',
            '成功保存项目到文件：\n':'Successfully save the project to a file:\n',
            '在关闭项目前，是否要保存项目？':'Save project before closing?',
            '语音Key未初始化！请检查版本，或者填写自定义key。': 'TTS Key is uninitiated! Please check the version, or offer custom keys.',
            '语音合成失败！检视控制台获取详细信息。': 'Synthesis Failed, check the terminal to get detail info',
            '必须选择一个音源！': 'Must choose a voice name.',
            '音源名是无效的！': 'The selected voice is invalid.',
            '在这里输入你想要合成的文本！' : 'Please enter the text for test here.',
            '失败的新建':'Failed to Create',
            '非法的{type}名：{name}\n{type}名只能包含中文、英文、数字、下划线和空格！': 'Invalid {type} name: {name}\n{type} name can only contain Chinese characters, English letters, numbers, underscores, and spaces.',
            '重复的{type}名：{name}！': 'Duplicate {type} name: {name} !',
            '确定要删除这个条目？\n这项删除将无法复原！': 'Sure to delete this item? This deletion cannot be recovered!',
            '尝试重命名一个已经启动的{}页面！\n重命名后，这个页面会被关闭！': 'Trying to rename a enabled {} page.\nAfter renaming, this page will be closed!',
            '失败的重命名':'Failed to Rename',
            '#! {executable}\n# {new_keyword}: 空白的剧本文件。点按键盘Tab键，获取命令智能补全。预览和导出按钮在右侧 ->\n':'#! {executable}\n# {new_keyword}: Empty RplGenLog. Press Tab to access Text Autocomplete Engine. Preview and export buttons are on the right->\n',
            '【{core}】执行完毕\n退出状态是：【{status}】': '[{core}] Execute done!\nExit status: [{status}]',
            "正在执行中": 'Core running!',
            "无效的执行": 'Invalid execution!',
            '核心退出': 'Core Exit',
            '添加语音合成标记': 'Add TTS mark',
            '批量导入外部语音文件': 'Import external voice files in batches',
            '移除星标语音': 'Remove asterisk voices',
            '智能导入剧本': 'Intel script-text importing',
            '（全部）': '(All)',
            '目标角色（Name）是？': 'Target character Name is ___?',
            '目标差分（Subtype）是？': 'Target character Subtype is ___?',
            '批量导入语音':'Import voice in batches',
            '没有匹配到任何小节！': 'No matched section!',
            '无匹配' : 'Not Match',
            '复制了多个对象，' : 'Copied multiple objects, ',
            '没有复制对象，' : 'Did not copy any object, ',
            '无法粘贴属性。': 'cannot paste attributes.',
            '类型不正确': 'Invalid Object Type',
            '复制的内容无法黏贴到这个页面！': 'Cannot paste the copied objects to this page!',
            '无法删除default差分！': 'Cannot delete the .default Subtype!',
            '这个差分名是非法的！': 'This Subtype name is invalid!',
            '这个差分名已经被使用了！': 'This Subtype name is occupied!',
            '请输入自定义列名': 'Please enter the name of custom attribute',
            '这个列名已经使用过了！': 'This custom attribute name is occupied!',
            '请选择想要删除的自定义项': 'Select the custom attribute to delete',
            '按回车确定': 'Press Enter to Comfirm',
            '如果确认修改差分名，请按回车键！': 'If sure to change the Subtype name, press Enter!',
            '如果确认修改媒体名，请按回车键！': 'If sure to change the Media name, press Enter!',
            '这个媒体名已经被使用了！': 'This Media name is occupied!',
            '这个媒体名是非法的！': 'This Media name is invalid!',
            '无效的值：{}': 'Invalid value: {}',
            '自定义切换效果': 'Custom Am/Bb Method',
            '删除自定义': 'Del Custom',
            '确认要关闭软件？\n尚未保存的项目变更将会丢失！': 'Sure to close? The unsaved changes in project will be lost!',
            '核心程序正在运行中！在核心程序终止前，图形界面已被暂时的禁用。': 'The core program is running! The GUI is disabled before the core program terminates',
            '禁用图形界面': 'GUI disabled'
        }
    }
    lang = 'zh'
    @staticmethod
    def set_language(lang='zh'):
        Translate.lang = lang
        if lang == 'zh':
            MessageCatalog.locale('zh_cn')
            Translate.init_lang('zh_cn')
        elif lang == 'en':
            MessageCatalog.locale('en')
        else:
            MessageCatalog.locale('en')
    @staticmethod
    def translate(src:str):
        if Translate.lang in Translate.dictionary:
            try:
                return Translate.dictionary[Translate.lang][src]
            except KeyError:
                return src
        else:
            return src
    @staticmethod
    def init_lang(locale:str):
        for pair in Translate.locale_dictionary[locale]:
            MessageCatalog.set_many(locale, *pair)
# 支持部分对象单独本地化
class Localize:
    language = {}
    localize = 'zh'
    def tr(self,key:str):
        if self.localize == 'zh':
            return key
        else:
            return self.language[self.localize][key]
def tr(src, *srcs):
    trans = Translate.translate(src)
    if srcs:
        if Translate.lang == 'en':
            sep = ' '
        else:
            sep = ''
        for s in srcs:
            trans += sep+Translate.translate(s)
    return trans