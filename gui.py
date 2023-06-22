#!/usr/bin/env python
# coding: utf-8

import multiprocessing
from core.GUI_Welcome import RplGenStudioWelcome

def show_welcome():
    welcome = RplGenStudioWelcome()

if __name__ == '__main__':

    # 多进程启动welcome
    show_welcome_process = multiprocessing.Process(target=show_welcome,args=())
    show_welcome_process.start()

    # 再初始化 MainWindow
    from core.GUI_MainWindow import RplGenStudioMainWindow

    # 等待
    show_welcome_process.join()

    # gui的入口
    root = RplGenStudioMainWindow()
    root.mainloop()