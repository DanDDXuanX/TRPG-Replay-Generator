#!/usr/bin/env python
# coding: utf-8
# 异常定义

# 解析器错误
class ParserError(Exception):
    def __init__(self,*description):
        self.description = ' '.join(map(str,description))
    def __str__(self):
        return self.description

# 媒体定义错误
class MediaError(ParserError):
    pass

# 忽略输入文件
class IgnoreInput(Exception):
    pass