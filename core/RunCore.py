#!/usr/bin/env python
# coding: utf-8

# 尝试多进程的实现

from .ScriptParser import MediaDef,CharTable,RplGenLog
from .ProjConfig import Config, Preference
from .OutputType import PreviewDisplay,ExportVideo,ExportXML

from multiprocessing import Queue,Process,TimeoutError
from queue import Empty
import threading
import sys
import time

# 核心进程
class CoreProcess(Process):
    def bind_queue(self,std_queue:Queue,msg_queue:Queue):
        self.msg_queue = msg_queue # 子进程接收消息的队列
        self.std_queue = std_queue # 子进程发送消息（标准输出）的队列
    def terminate(self) -> None:
        # 线程安全的终止
        self.msg_queue.put('[Terminated]')
        # 最多等待2秒，否则就强制终止
        self.join(timeout=2)
        if self.is_alive():
            self.std_queue.put('[MultiProcessEnd]:4') # KILLED
            super().terminate()
    # def terminate(self) -> None:
    #     self.std_queue.put('[MultiProcessEnd]:4') # KILLED
    #     super().terminate()

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
        Type:str,std_queue:Queue,msg_queue:Queue,mediadef:MediaDef,chartab:CharTable,rplgenlog:RplGenLog,config:Config, # 常规参数
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
        elif Type == 'ExportVideo':
            core = ExportVideo(mediadef,chartab,rplgenlog,config,prefer,media_path,output_path,key)
        elif Type == 'ExportXML':
            core = ExportXML(mediadef,chartab,rplgenlog,config,prefer,media_path,output_path,key)
        else:
            raise Exception('Invalid Core')
        # 创建消息监听线程
        on_listening = True
        def listen_message():
            while on_listening:
                try:
                    msg = msg_queue.get_nowait()
                    if msg == '[Terminated]':
                        core.terminate()
                        break
                except Empty:
                    time.sleep(0.3)
                    continue
        listen = threading.Thread(target=listen_message)
        listen.start()
        # 开始核心程序
        status = core.main()
        # 终止监听线程
        on_listening = False
        listen.join()
    except Exception as E:
        status = 1 # 异常
        print(E)
    # 队列输出，结束的标志
    std_queue.put(f'[MultiProcessEnd]:{status}')