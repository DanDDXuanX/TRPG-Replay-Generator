#!/usr/bin/env python
# coding: utf-8

import multiprocessing
from core.GUI_Welcome import RplGenStudioWelcome
from core.ProjConfig import preference
from ttkbootstrap.dialogs import Querybox

def show_welcome(conn):
    welcome = RplGenStudioWelcome(conn)
    pass

if __name__ == '__main__':
    # 多进程的支持
    multiprocessing.freeze_support()
    # 多进程启动welcome
    parent_conn, child_conn = multiprocessing.Pipe()
    show_welcome_process = multiprocessing.Process(target=show_welcome,args=(child_conn,))
    show_welcome_process.start()

    # 再初始化 MainWindow
    from core.GUI_MainWindow import RplGenStudioMainWindow

    # 检查是否需要输入CDkey
    if preference.bulitin_keys_status == 8:
        cdkey_get = Querybox.get_string(prompt='请输入软件序列号（CDKey）',title='序列号',parent=self.content)
        if cdkey_get:
            print(cdkey_get)

    # 等待
    # show_welcome_process.join()
    parent_conn.send('terminate')
    show_welcome_process.join()

    # gui的入口
    root = RplGenStudioMainWindow()
    root.mainloop()