#!/usr/bin/env python
# coding: utf-8

# 尝试多进程的实现

from .ScriptParser import MediaDef,CharTable,RplGenLog
from .ProjConfig import Config
from .OutputType import PreviewDisplay

from traceback import print_exc

def run_core(
        Type:str,mediadef:MediaDef,chartab:CharTable,rplgenlog:RplGenLog,config:Config, # 常规参数
        preference, # 首选项
        MediaPath, # 媒体路径
        output_path:str=None,key:str=None
        ):
    "在多进程中调用核心程序的接口"
    # 需要做的第一件事情：同步全局变量 
    # TODO：思考更加优雅的解决办法
    # 1. 减少全局变量的使用，让位于独立线程的核心程序能独立的活动
    # 2. 也就是，尽量把所有从主程序拿来的内容，都以本函数的参数的形式送入
    try:
        if Type == 'PreviewDisplay':
            core = PreviewDisplay(mediadef,chartab,rplgenlog,config)
            core.main()
        else:
            pass
    except Exception as E:
        print_exc()
        print(E)