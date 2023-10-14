#!/usr/bin/env python
# coding: utf-8

# 根据不同语言，导入不同的表结构

from .ProjConfig import preference

if preference.lang == 'zh':
    from .GUI_TableStruct_ZH import *
elif preference.lang == 'en':
    from .GUI_TableStruct_EN import *
else:
    pass