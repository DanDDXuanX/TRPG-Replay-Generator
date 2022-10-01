#!/usr/bin/env python
# coding: utf-8
edtion = 'alpha 1.12.7'

"""
这个gui.py是对根目录下的gui.py的实验性重构
"""

import tkinter as tk
from tkinter import font
from tkinter import messagebox
import sys
import appFrames as af
import os
import sys
import re
import pickle



class Application():
    def __init__(self):
        # 初始化
        root = tk.Tk()
        root.resizable(0,0)
        root.geometry("640x550")
        root.config(background ='#e0e0e0')
        root.protocol('WM_DELETE_WINDOW',self.close_window)
        root.title('回声工坊 ' + edtion)
        # linux:可能无法使用小图标
        try:
            root.iconbitmap('./media/icon.ico')
        except tk.TclError:
            pass

        self.root = root

        # 大号字体
        try:
            self.big_text = font.Font(font=("微软雅黑",12))
        except Exception:
            self.big_text = font.Font(font=("System",12))
        
        
        # 选中的sheet
        self.tab = tk.IntVar(self.root)
        # 几个文件的路径
        self.stdin_logfile = tk.StringVar(self.root)
        self.characor_table = tk.StringVar(self.root)
        self.media_define = tk.StringVar(self.root)
        self.output_path = tk.StringVar(self.root)
        self.timeline_file = tk.StringVar(self.root)
        # 可选参数
        self.project_W = tk.IntVar(self.root)
        self.project_H = tk.IntVar(self.root)
        self.project_F = tk.IntVar(self.root)
        self.project_Z = tk.StringVar(self.root)
        self.project_Q = tk.IntVar(self.root)
        # 语音合成的key
        self.AccessKey = tk.StringVar(self.root)
        self.Appkey = tk.StringVar(self.root)
        self.AccessKeySecret = tk.StringVar(self.root)
        self.AzureKey = tk.StringVar(self.root)
        self.ServiceRegion = tk.StringVar(self.root)
        # flag
        self.synthanyway = tk.IntVar(self.root)
        self.exportprxml = tk.IntVar(self.root)
        self.exportmp4 = tk.IntVar(self.root)
        self.fixscrzoom = tk.IntVar(self.root)
        self.save_config = tk.IntVar(self.root)

        # 读取配置
        self.loadConfigure()

        # 获取python解释器的路径
        self.python3 = sys.executable.replace('\\','/')
        #python3 = 'python' # exe发布版

        # 创建组件
        self.createWidgets()

    def mainloop(self):
        self.root.mainloop()

    def loadConfigure(self):
        try:
            # 读取保存参数的文件
            i_config = open('./media/save_config','rb')
            configs = pickle.load(i_config)
            i_config.close()
            # 检查是否有保存参数
            if configs['save_config'] == 0: # 如果上一次保存时，是否保存是否
                raise ValueError('No save config!')
            if configs.pop('version') != edtion: # 如果版本不一致 # 在这里直接把version pop 出来！免得在应用时导致NameError！
                if messagebox.askyesno(title='版本变动',message='发现版本变动！\n是否仍然载入上一次的配置？') == False:
                    raise ValueError('Edition change!')
            # 应用变更
            for key,value in configs.items():
                eval(key).set(value)
        except Exception: # 使用原装默认参数
            self.project_W.set(1920)
            self.project_H.set(1080)
            self.project_F.set(30)
            self.project_Z.set('BG3,BG2,BG1,Am3,Am2,Am1,Bb')
            self.project_Q.set(24)
            self.AccessKey.set('Your_AccessKey')
            self.AccessKeySecret.set('Your_AccessKey_Secret')
            self.Appkey.set('Your_Appkey')
            self.AzureKey.set('Your_Azurekey')
            self.ServiceRegion.set('eastasia')
            # 将取消系统缩放设为默认值
            if sys.platform == 'win32':
                self.fixscrzoom.set(1)
            else:
                self.fixscrzoom.set(0)
        
    
    def createWidgets(self):
        # 标签页选项
        self.tab1 = tk.Radiobutton(self.root,text="主程序", font= self.big_text,command=self.printFrame,variable=self.tab,value=1,indicatoron=False)
        self.tab2 = tk.Radiobutton(self.root,text="语音合成", font=self.big_text,command=self.printFrame,variable=self.tab,value=2,indicatoron=False)
        self.tab3 = tk.Radiobutton(self.root,text="导出XML", font=self.big_text,command=self.printFrame,variable=self.tab,value=3,indicatoron=False)
        self.tab4 = tk.Radiobutton(self.root,text="导出MP4", font=self.big_text,command=self.printFrame,variable=self.tab,value=4,indicatoron=False)
        self.tab5 = tk.Radiobutton(self.root,text="音频\n格式转换",command=self.printFrame,variable=self.tab,value=5,indicatoron=False)
        self.tab1.place(x=10,y=10,width=138,height=40)
        self.tab2.place(x=148,y=10,width=138,height=40)
        self.tab3.place(x=286,y=10,width=138,height=40)
        self.tab4.place(x=424,y=10,width=138,height=40)
        self.tab5.place(x=562,y=10,width=68,height=40)
        
        # 界面
        self.main_frame = af.MainFrame(self.root,self,height=490 ,width=620)
        self.synth_frame = af.SynthFrame(self.root,self,height=490 ,width=620)
        self.xml_frame = af.XmlFrame(self.root,self,height=490 ,width=620)
        self.mp4_frame = af.Mp4Frame(self.root,self,height=490 ,width=620)
        self.format_frame = af.FormatFrame(self.root,self,height=490 ,width=620)
        
        self.tab_frame = {1:self.main_frame,2:self.synth_frame,3:self.xml_frame,4:self.mp4_frame,5:self.format_frame}
        
        # 初始界面
        self.tab.set(1)
        self.frame_display = self.main_frame #目前展示的frame
        
    def printFrame(self):
        """
        显示当前选中的页面
        """
        self.frame_display.place_forget()
        select = self.tab_frame[self.tab.get()]
        select.place(x=10,y=50)
        self.frame_display = select
     
    def close_window(self):
        try:
            o_config = open('./media/save_config','wb')
            if self.save_config.get() == 1: # 以一个字典的形式把设置保存下来
                pickle.dump({
                    'stdin_logfile':self.stdin_logfile.get(),'characor_table':self.characor_table.get(),
                    'media_define':self.media_define.get(),'output_path':self.output_path.get(),
                    'timeline_file':self.timeline_file.get(),'project_W':self.project_W.get(),
                    'project_H':self.project_H.get(),'project_F':self.project_F.get(),
                    'project_Z':self.project_Z.get(),'project_Q':self.project_Q.get(),
                    'AccessKey':self.AccessKey.get(),'Appkey':self.Appkey.get(),'AccessKeySecret':self.AccessKeySecret.get(),
                    'AzureKey':self.AzureKey.get(),'ServiceRegion':self.ServiceRegion.get(),
                    'synthanyway':self.synthanyway.get(),'exportprxml':self.exportprxml.get(),
                    'exportmp4':self.exportmp4.get(),'fixscrzoom':self.fixscrzoom.get(),'save_config':self.save_config.get(),
                    'version':edtion
                },o_config) # 把版本信息保存下来
            else: # 如果选择不保存，则抹除保存的参数
                pickle.dump({'save_config':self.save_config.get()},o_config)
            
            o_config.close()
        except Exception:
            messagebox.showwarning(title='警告',message='保存设置内容失败!')
        finally: # 关闭主窗口
            self.root.destroy()
            self.root.quit()
    
if __name__=='__main__':
    app=Application()
    app.mainloop()
