#!/usr/bin/env python
# coding: utf-8

# 尝试多进程的实现

from .ScriptParser import MediaDef,CharTable,RplGenLog
from .ProjConfig import Config, Preference
from .OutputType import PreviewDisplay,ExportVideo,ExportXML

from multiprocessing import Queue
import sys

# 重定向，标准输出到Queue
class StdoutQueue:
    def __init__(self,queue:Queue) -> None:
        self.queue = queue
    def write(self, string):
        # 检查string到底有没有东西
        if string == '':
            return
        else:
            self.queue.put(string)
    def flush(self):
        pass

# 多进程：执行核心功能
def run_core(
        Type:str,std_queue:Queue,mediadef:MediaDef,chartab:CharTable,rplgenlog:RplGenLog,config:Config, # 常规参数
        prefer:Preference, # 首选项
        media_path:str, # 媒体路径
        output_path:str=None,key:str=None
        ):
    "在多进程中调用核心程序的接口"
    # 重定向
    sys.stdout = StdoutQueue(std_queue)
    # 执行主程序
    try:
        if Type == 'PreviewDisplay':
            core = PreviewDisplay(mediadef,chartab,rplgenlog,config,prefer,media_path,title=key)
            status = core.main()
        elif Type == 'ExportVideo':
            core = ExportVideo(mediadef,chartab,rplgenlog,config,prefer,media_path,output_path,key)
            status = core.main()
        elif Type == 'ExportXML':
            core = ExportXML(mediadef,chartab,rplgenlog,config,prefer,media_path,output_path,key)
            status = core.main()
        else:
            pass
    except Exception as E:
        status = 1 # 异常
        print(E)
    # 队列输出，结束的标志
    std_queue.put(f'[MultiProcessEnd]:{status}')