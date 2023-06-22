#!/usr/bin/env python
# coding: utf-8

# welcome的入口
# 
# from core.GUI_Welcome import RplGenStudioWelcome
# welcome = RplGenStudioWelcome()
# 
# gui的入口

from core.GUI_MainWindow import RplGenStudioMainWindow

root = RplGenStudioMainWindow()
root.mainloop()