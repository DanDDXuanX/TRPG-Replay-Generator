#!/usr/bin/env python
# coding: utf-8

from ttkbootstrap.localization import MessageCatalog

# 多语言支持

# regex: ["'].*[\u4e00-\u9fa5].*["']

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
            ('Warning','警告'),
            ('Error','错误'),
        ]
    }
    dictionary = {
        'en':{
            '确定': 'OK',
            '取消': 'Cancel',
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
            '最近项目：'    : 'Recent:',
            '清除'      : 'clear',
            '无记录'        : 'No recode',
            '运行脚本'      : 'Run Scripts',
            '重置'  : 'Reset',
            '终止'  : 'Interrupt',
            '固定点'    : 'Pos',
            '自由点'    : 'FreePos',
            '点网格'    : 'PosGrid',
            '字体'      : 'Text',
            '描边字体'  : 'StrokeText',
            '富文本'    : 'RichText',
            '血条标签'  : 'HPLabel',
            '气泡'      : 'Bubble',
            '气球'      : 'Balloon',
            '动态气泡'  : 'DynamicBubble',
            '聊天窗'    : 'ChatWindow',
            '立绘'      : 'Animation',
            '背景'      : 'Background',
            '音效'      : 'Audio',
            '背景音乐'  : 'BGM',
            '角色差分'  : 'Subtype',
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
            '从[{}]粘贴' : 'Paste from [{}]'
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
                return MessageCatalog.translate(src)
        else:
            return src
    @staticmethod
    def init_lang(locale:str):
        for pair in Translate.locale_dictionary[locale]:
            MessageCatalog.set_many(locale, *pair)

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