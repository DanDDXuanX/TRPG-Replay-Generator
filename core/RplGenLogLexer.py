#!/usr/bin/env python
# coding: utf-8

# 适用于 pygments 的 rplgenlog 语法高亮规则

from pygments.lexer import RegexLexer
from pygments.token import Text, Comment, Operator, Keyword, Name, String
from pygments.token import Number, Punctuation, Whitespace

class RplGenLogLexer(RegexLexer):
    name = "RplGenLog"
    aliases = ['rplgenlog','rgl','RGL']
    filenames = ['*.rgl']
    tokens = {
        # 基础
        "root":[
            # 注释
            (r'^#.*$', Comment),
            # 错误
            (r'^[\t\ ]+$',Whitespace),
            # 命令
            (r'<(background|animation|bubble|clear|dice|hitpoint|wait)>',Name.Tag,'media'),
            # 设置
            (r'^<((set|table|move):[^>]+|table|bgm|BGM)>',Name.Function,'target'),
            # 会话
            (r'^\[([\ \w\.\;\(\)\,]+)\]',Name.Decorator,'content'),
            # 自然文本
            (r'.+?',Text),
        ],
        # 放置型媒体
        "media":[
            # 方法
            (r'<\w+(\=\d+)?>',Name.Builtin.Pseudo),
            # 冒号
            (r'\B:',Operator),
            # 括号
            (r'\(',Name.Decorator,'brackets'),
            # 特殊的关键字
            (r'\b(NA|black|white)\b',Name.Exception,'#pop'),
            # 逗号
            (r',', Punctuation),
            # 自然文本
            (r'.+?',Text),
            # 句子结尾
            (r'$',Punctuation,'#pop')
        ],
        # 括号内的东西
        "brackets":[
            # 字符串？
            (r'["\'].+?["\']', String),
            # 整数
            (r'\b(-)?\d+\b', Number.Integer),
            # NA
            (r'NA', Number.Integer),
            # 方法
            (r'<\w+(\=\d+)?>',Name.Builtin.Pseudo),
            # 逗号
            (r',', Text),
            # 括号返回
            (r'\)',Name.Decorator,'#pop'),
            # 自然文本
            (r'.+?',Text),
        ],
        # 设置的目标
        "target":[
            # 冒号
            (r'\B:',Operator),
            # 整数
            (r'\b(-)?\d+$\b',Number.Integer,'#pop'),
            # 曲线函数
            (r'\b(linear|quadraticR|quadratic|sigmoid|right|left|sincurve)\b',Name.Exception,'#pop'),
            # 特殊的关键字
            (r'\b(animation|bubble|both|none|stop|black|white)\b',Name.Exception,'#pop'),
            # 方法
            (r'<\w+(\=\d+)?>',Name.Builtin.Pseudo,'#pop'),
            # 字符串？
            (r'["\'].+?["\']', String),
            # 逗号
            (r',', Text),
            # 自然文本
            (r'.+?',Text),
            # 句子结尾
            (r'$',Punctuation,'#pop')
        ],
        # 发言的内容
        "content":[
            # 方法
            (r'<\w+(\=\d+)?>',Name.Builtin.Pseudo),
            # 冒号
            (r'\B:',Operator),
            # 富文本标记
            (r'\[(\w{1,}|[\^#]|\/\w{1,2}|fs\:\d+|(bg|fg)\:#([\da-fA-F]{2}){3,4})\]',Name.Tag),
            # 换行符
            (r'(\^|#)',Name.Tag),
            # 待合成星标
            (r'({\*})',Punctuation),
            # 语音
            (r'({.+?})',Keyword.Constant),
            # 自然文本
            (r'.+?',Text),
            # 句子结尾
            (r'$',Punctuation,'#pop'),
        ]
    }
