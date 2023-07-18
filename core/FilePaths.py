#!/usr/bin/env python
# coding: utf-8
# 对于文件路径的解析
import os
import sys
import glob
from core.Exceptions import MediaError

# 文件路径类
class Filepath:
    # 工作路径，转义字符 .
    RplGenpath:str = os.getcwd().replace('\\','/')
    # 媒体定义文件路径，转义字符：@
    Mediapath:str = RplGenpath
    # 初始化
    def __init__(self,filepath:str) -> None:
        # 相对路径 @
        if filepath[0] == '@':
            filepath = self.Mediapath + filepath[1:]
        # 相对路径 ./..
        self._absolute = os.path.abspath(filepath).replace('\\','/')
        # 首字符大写
        self._absolute = self.upper(self._absolute)
        # 通配符，多个文件
        if ('*' in self._absolute) or ('[' in self._absolute and ']' in self._absolute):
            # 文件列表
            self._list_absol = list(map(lambda x:x.replace('\\','/'),glob.glob(self._absolute)))
            # 如果匹配到的列表为空白
            if len(self._list_absol) == 0:
                raise MediaError('FileNFound',filepath)
        # 单文件
        else:
            # 校验文件可用性
            if os.path.isfile(self._absolute) == False:
                raise MediaError('FileNFound',filepath)
            self._list_absol = [self._absolute]
    # 首字母大写
    def upper(self,_str:str) -> str:
        if _str[0].islower():
            return _str[0].upper() + _str[1:]
        else:
            return _str
    # 字符串化
    def __str__(self) -> str:
        return self._absolute
    # 绝对路径(可能包含通配符)
    def absolute(self) -> str:
        return self._absolute
    # 相对路径(可能包含通配符)
    def relative(self) -> str:
        RplGenpath = self.upper(self.RplGenpath)
        Mediapath = self.upper(self.Mediapath)
        # 优先使用：程序根目录
        if RplGenpath in self._absolute:
            return self._absolute.replace(RplGenpath,'.')
        # 媒体目录
        elif Mediapath in self._absolute:
            return self._absolute.replace(Mediapath,'@')
        # 原始目录
        else:
            return self._absolute
    # 确切路径（绝对，且不包含通配符）
    def exact(self) -> str:
        return self._list_absol[0]
    # 列出文件
    def list(self) -> list:
        return self._list_absol
    # 文件后缀
    def type(self) -> str:
        return self.exact().split('.')[-1]
    # 文件名字
    def name(self) -> str:
        return self.exact().split('/')[-1]
    # PR路径（不包含通配符）
    def xml_reformated(self) -> str:
        to_format = self.exact()
        if ('&' in to_format)|('<' in to_format)|('>' in to_format):
            # xml 对于特殊字符的转义
            to_format = to_format.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') 
        if ('"' in to_format)|("'" in to_format):
            to_format = to_format.replace('"','&quot;').replace("'",'&apos;')
        if '//' in to_format:
            to_format = to_format.replace('//','/') # BUG 在 mac win 虚拟机
        # 判断文件系统
        if ('win32' in sys.platform) & (to_format[1] == ':'):
            # 替换冒号
            to_format = 'file://localhost/' + to_format[0] + '%3a' + to_format[2:]
        elif (sys.platform in ['darwin','linux']) & (to_format[0] == '/'):
            to_format = 'file://localhost' + to_format
        else:
            # 摆烂
            to_format = 'file://localhost' + to_format
        return to_format
    # 所在文件夹
    def directory(self) -> str:
        return '/'.join(self.exact().split('/')[0:-1]) + '/'