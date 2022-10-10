#!/usr/bin/env python
# coding: utf-8
# 异常定义

# 解析器错误

# 回声工坊核心的异常基类
class RplGenError(Exception):
    def __init__(self, *description):
        self.errortype = ''
        self.description = self.errortype + ' '.join(map(str,description))
    def __str__(self):
        return self.description

class ArgumentError(RplGenError):
    def __init__(self, *description):
        super().__init__(*description)
        self.errortype = "\x1B[31m[ArgumentError]:\x1B[0m "
class ParserError(RplGenError):
    def __init__(self,*description):
        super().__init__(*description=)
    def __str__(self):
        return self.description

class ParserError(RplGenError):
    def __init__(self, *description):
        super().__init__(*description)
        self.errortype = "\x1B[31m[ParserError]:\x1B[0m "

# 媒体定义错误
class MediaError(ParserError):
    pass

# 忽略输入文件
class IgnoreInput(Exception):
    pass