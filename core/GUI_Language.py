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
            ('Color Chooser','选择颜色')
        ]
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
