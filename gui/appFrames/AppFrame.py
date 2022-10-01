"""
页面的公共父类，用来添加公共方法
"""
import tkinter as tk
from tkinter import messagebox
from utils import browse_file
import os

class AppFrame(tk.Frame):
    def __init__(self,master,app,*args, **kwargs):
        super().__init__(master,*args, **kwargs)
        
        self.v = app.v
        self.app = app
        
    def call_browse_file(self,text_obj,method='file'):
        """
        浏览文件，并根据媒体文件路径确定媒体定义文件路径框旁边的按钮显示“编辑”还是“新建”
        """
        getname = browse_file(text_obj,method)
        if text_obj == self.media_define:
            if os.path.isfile(getname):
                self.new_or_edit.config(text='编辑')
            else:
                self.new_or_edit.config(text='新建')
    def highlight(self,target):
        """
        根据目前标志的状态来高亮对应的目标
        """
        app = self.app
        if target == self.v["exportmp4"]:
            
            if target.get() == 1:
                app.tab4.config(fg='red',text='导出MP4 ⚑')
                app.mp4_frame.label_ql.config(fg='red')
            else:
                app.tab4.config(fg='black',text='导出MP4')
                app.mp4_frame.label_ql.config(fg='black')
        elif target == self.v["synthanyway"]:
            if target.get() == 1:
                warning_text = "注意！当使用“先执行语音合成”标志时，\n"
                warning_text += "若语音合成出现了异常，运行日志将会更难解读！\n"
                if messagebox.askokcancel(title='请谨慎使用“先执行语音合成”标志！',message=warning_text) == True:
                    app.tab2.config(fg='red',text='语音合成 ⚑')
                    app.synth_frame.label_AP.config(fg='red')
                    app.synth_frame.label_AK.config(fg='red')
                    app.synth_frame.label_AS.config(fg='red')
                    app.synth_frame.label_AZ.config(fg='red')
                    app.synth_frame.label_SR.config(fg='red')
                else:
                    # 否则，将先执行语音合成重置为"否"
                    target.set(0)
            else:
                app.tab2.config(fg='black',text='语音合成')
                app.synth_frame.label_AP.config(fg='black')
                app.synth_frame.label_AK.config(fg='black')
                app.synth_frame.label_AS.config(fg='black')
                app.synth_frame.label_AZ.config(fg='black')
                app.synth_frame.label_SR.config(fg='black')
        elif target == self.v["exportprxml"]:
            if target.get() == 1:
                app.tab3.config(text='导出XML ⚑')
            else:
                app.tab3.config(text='导出XML')
        elif target == self.v["fixscrzoom"]: 
            if target.get() == 1:
                try:
                    import ctypes
                    ctypes.windll.user32.SetProcessDPIAware() #修复错误的缩放，尤其是在移动设备。
                    app.root.update()
                except Exception:
                    messagebox.showwarning(title='警告',message='该选项在当前系统下不可用！')
                    target.set(0)
        else:
            pass