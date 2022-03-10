#!/usr/bin/env python
# coding: utf-8
edtion = 'alpha 1.7.1'

import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image,ImageTk
import webbrowser
import os
import sys

Main_windows = tk.Tk()

Main_windows.resizable(0,0)
Main_windows.geometry("640x550")
Main_windows.iconbitmap('./doc/icon.ico')
Main_windows.config(background ='#e0e0e0')
Main_windows.title('TRPG Replay Generator ' + edtion)

try:
    big_text = font.Font(font="微软雅黑",size=25)
except:
    big_text = font.Font(size=25)

tab = tk.IntVar(Main_windows)

stdin_logfile = tk.StringVar(Main_windows)
characor_table = tk.StringVar(Main_windows)
media_define = tk.StringVar(Main_windows)
output_path = tk.StringVar(Main_windows)
timeline_file = tk.StringVar(Main_windows)
text_obj = {1:media_define,2:characor_table,3:stdin_logfile,4:output_path,5:timeline_file}

# 可选参数们
project_W = tk.StringVar(Main_windows)
project_H = tk.StringVar(Main_windows)
project_F = tk.StringVar(Main_windows)
project_Z = tk.StringVar(Main_windows)

AccessKey = tk.StringVar(Main_windows)
AccessKey.set('Your_AccessKey')
AccessKeySecret = tk.StringVar(Main_windows)
AccessKeySecret.set('Your_AccessKey_Secret')
Appkey = tk.StringVar(Main_windows)
Appkey.set('Your_Appkey')

# flag们

synthanyway = tk.IntVar(Main_windows)
exportprxml = tk.IntVar(Main_windows)
exportmp4 = tk.IntVar(Main_windows)
fixscrzoom = tk.IntVar(Main_windows)

project_W.set(1920)
project_H.set(1080)
project_F.set(30)
project_Z.set('BG3,BG2,BG1,Am3,Am2,Am1,Bb')

python3 = sys.executable.replace('\\','/') # 获取python解释器的路径

def printFrame():
    global frame_display
    frame_display.place_forget()
    select = tab_frame[tab.get()]
    select.place(x=10,y=50)
    #frame_item(select)
    frame_display = select

def browse_file(i,method='file'):
    if method == 'file':
        getname = filedialog.askopenfilename()
    else:
        getname = filedialog.askdirectory()
    text_obj[i].set(getname)

def run_command():
    optional = {1:'--OutputPath {of} ',2:'--ExportXML ',3:'--ExportVideo ',4:'--SynthesisAnyway ',5:'--FixScreenZoom '}
    command = python3 + ' ./replay_generator.py --LogFile {lg} --MediaObjDefine {md} --CharacterTable {ct} '
    command = command + '--FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd} '
    if output_path.get()!='':
        command = command + optional[1].format(of=output_path.get().replace('\\','/'))
    if synthanyway.get()==1:
        command = command + optional[4]
    if exportprxml.get()==1:
        command = command + optional[2]
    if exportmp4.get()==1:
        command = command + optional[3]
    if fixscrzoom.get()==1:
        command = command + optional[5]
    if '' in [stdin_logfile.get(),characor_table.get(),media_define.get(),project_W.get(),project_H.get(),project_F.get(),project_Z.get()]:
        messagebox.showerror(title='错误',message='缺少必要的参数！')
    else:
        command = command.format(lg = stdin_logfile.get().replace('\\','/'),md = media_define.get().replace('\\','/'),
                                 ct=characor_table.get().replace('\\','/'),fps=project_F.get().replace('\\','/'),
                                 wd=project_W.get().replace('\\','/'),he=project_H.get().replace('\\','/'),
                                 zd=project_Z.get().replace('\\','/'))
        try:
            print('[32m'+command+'[0m')
            os.system(command)
        except:
            messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了！')

def run_command_synth():
    command = python3 +' ./speech_synthesizer.py --LogFile {lg} --MediaObjDefine {md} --CharacterTable {ct} --OutputPath {of} --AccessKey {AK} --AccessKeySecret {AS} --Appkey {Ap}'
    if '' in [stdin_logfile.get(),characor_table.get(),media_define.get(),output_path.get(),AccessKey.get(),AccessKeySecret.get(),Appkey.get()]:
        messagebox.showerror(title='错误',message='缺少必要的参数！')
    else:
        command = command.format(lg = stdin_logfile.get().replace('\\','/'),md = media_define.get().replace('\\','/'),
                                 of = output_path.get().replace('\\','/'), ct = characor_table.get().replace('\\','/'),
                                 AK = AccessKey.get(), AS= AccessKeySecret.get(),AP=Appkey.get())
        try:
            print('[32m'+command+'[0m')
            os.system(command)
        except:
            messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了！')

def run_command_xml():
    command = python3 + ' ./export_xml.py --TimeLine {tm} --MediaObjDefine {md} --OutputPath {of} --FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd}'
    if '' in [timeline_file.get(),media_define.get(),output_path.get(),
              project_W.get(),project_H.get(),project_F.get(),project_Z.get()]:
        messagebox.showerror(title='错误',message='缺少必要的参数！')
    else:
        command = command.format(tm = timeline_file.get().replace('\\','/'),
                                 md = media_define.get().replace('\\','/'), of = output_path.get().replace('\\','/'), 
                                 fps = project_F.get().replace('\\','/'), wd = project_W.get().replace('\\','/'),
                                 he = project_H.get().replace('\\','/'), zd = project_Z.get().replace('\\','/'))
        try:
            print('[32m'+command+'[0m')
            os.system(command)
        except:
            messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了！')

def run_command_mp4():
    command = python3 + ' ./export_video.py --TimeLine {tm} --MediaObjDefine {md} --OutputPath {of} --FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd}'
    if '' in [timeline_file.get(),media_define.get(),output_path.get(),
              project_W.get(),project_H.get(),project_F.get(),project_Z.get()]:
        messagebox.showerror(title='错误',message='缺少必要的参数！')
    else:
        command = command.format(tm = timeline_file.get().replace('\\','/'),
                                 md = media_define.get().replace('\\','/'), of = output_path.get().replace('\\','/'), 
                                 fps = project_F.get().replace('\\','/'), wd = project_W.get().replace('\\','/'),
                                 he = project_H.get().replace('\\','/'), zd = project_Z.get().replace('\\','/'))
        try:
            print('[32m'+command+'[0m')
            os.system(command)
        except:
            messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了！')

# 标签页选项

tab1 = tk.Radiobutton(Main_windows,text="主程序", font=big_text,command=printFrame,variable=tab,value=1,indicatoron=False)
tab2 = tk.Radiobutton(Main_windows,text="语音合成", font=big_text,command=printFrame,variable=tab,value=2,indicatoron=False)
tab3 = tk.Radiobutton(Main_windows,text="导出XML", font=big_text,command=printFrame,variable=tab,value=3,indicatoron=False)
tab4 = tk.Radiobutton(Main_windows,text="导出MP4", font=big_text,command=printFrame,variable=tab,value=4,indicatoron=False)
tab1.place(x=10,y=10,width=155,height=40)
tab2.place(x=165,y=10,width=155,height=40)
tab3.place(x=320,y=10,width=155,height=40)
tab4.place(x=475,y=10,width=155,height=40)

# 四个界面

main_frame = tk.Frame(Main_windows,height=490 ,width=620)
synth_frame = tk.Frame(Main_windows,height=490 ,width=620)
xml_frame = tk.Frame(Main_windows,height=490 ,width=620)
mp4_frame = tk.Frame(Main_windows,height=490 ,width=620)
tab_frame = {1:main_frame,2:synth_frame,3:xml_frame,4:mp4_frame}

# 界面的初始值

tab.set(1)
main_frame.place(x=10,y=50)
frame_display = main_frame #frame初始值

# main_frame

# 路径

filepath = tk.LabelFrame(main_frame,text='文件路径')
filepath.place(x=10,y=10,width=600,height=200)

tk.Label(filepath, text="媒体定义：",anchor=tk.W).place(x=10,y=5,width=70,height=30)
tk.Label(filepath, text="角色配置：",anchor=tk.W).place(x=10,y=50,width=70,height=30)
tk.Label(filepath, text="log文件：",anchor=tk.W).place(x=10,y=95,width=70,height=30)
tk.Label(filepath, text="输出路径：",anchor=tk.W).place(x=10,y=140,width=70,height=30)
tk.Entry(filepath, textvariable=media_define).place(x=80,y=5+3,width=430,height=25)
tk.Entry(filepath, textvariable=characor_table).place(x=80,y=50+3,width=430,height=25)
tk.Entry(filepath, textvariable=stdin_logfile).place(x=80,y=95+3,width=430,height=25)
tk.Entry(filepath, textvariable=output_path).place(x=80,y=140+3,width=430,height=25)
tk.Button(filepath, command=lambda:browse_file(1),text="浏览").place(x=520,y=5,width=70,height=30)
tk.Button(filepath, command=lambda:browse_file(2),text="浏览").place(x=520,y=50,width=70,height=30)
tk.Button(filepath, command=lambda:browse_file(3),text="浏览").place(x=520,y=95,width=70,height=30)
tk.Button(filepath, command=lambda:browse_file(4,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

# 选项

optional = tk.LabelFrame(main_frame,text='选项')
optional.place(x=10,y=210,width=600,height=110)

tk.Label(optional,text="分辨率-宽:",anchor=tk.W).place(x=10,y=5,width=70,height=30)
tk.Label(optional,text="分辨率-高:",anchor=tk.W).place(x=160,y=5,width=70,height=30)
tk.Label(optional,text="帧率:",anchor=tk.W).place(x=310,y=5,width=70,height=30)
tk.Label(optional,text="图层顺序:",anchor=tk.W).place(x=10,y=50,width=70,height=30)

tk.Entry(optional,textvariable=project_W).place(x=80,y=5,width=70,height=25)
tk.Entry(optional,textvariable=project_H).place(x=230,y=5,width=70,height=25)
tk.Entry(optional,textvariable=project_F).place(x=380,y=5,width=70,height=25)
tk.Entry(optional,textvariable=project_Z).place(x=80,y=50,width=370,height=25)

# 标志

flag = tk.LabelFrame(main_frame,text='标志')
flag.place(x=10,y=320,width=600,height=110)


tk.Checkbutton(flag,text="先执行语音合成",variable=synthanyway,anchor=tk.W).place(x=10,y=5,width=150,height=30)
tk.Checkbutton(flag,text="导出为PR项目",variable=exportprxml,anchor=tk.W).place(x=10,y=50,width=150,height=30)
tk.Checkbutton(flag,text="导出为.mp4视频",variable=exportmp4,anchor=tk.W).place(x=200,y=50,width=150,height=30)
tk.Checkbutton(flag,text="取消系统缩放",variable=fixscrzoom,anchor=tk.W).place(x=200,y=5,width=150,height=30)

my_logo = ImageTk.PhotoImage(Image.open('./doc/icon.png').resize((75,75)))
tk.Button(flag,image = my_logo,command=lambda: webbrowser.open('https://github.com/DanDDXuanX/TRPG-Replay-Generator'),relief='flat').place(x=500,y=0)

# 开始

tk.Button(main_frame, command=run_command,text="开始",font=big_text).place(x=260,y=435,width=100,height=50)

# synth_frame

filepath_s = tk.LabelFrame(synth_frame,text='文件路径')
filepath_s.place(x=10,y=10,width=600,height=200)

tk.Label(filepath_s, text="媒体定义：",anchor=tk.W).place(x=10,y=5,width=70,height=30)
tk.Label(filepath_s, text="角色配置：",anchor=tk.W).place(x=10,y=50,width=70,height=30)
tk.Label(filepath_s, text="log文件：",anchor=tk.W).place(x=10,y=95,width=70,height=30)
tk.Label(filepath_s, text="输出路径：",anchor=tk.W).place(x=10,y=140,width=70,height=30)
tk.Entry(filepath_s, textvariable=media_define).place(x=80,y=5+3,width=430,height=25)
tk.Entry(filepath_s, textvariable=characor_table).place(x=80,y=50+3,width=430,height=25)
tk.Entry(filepath_s, textvariable=stdin_logfile).place(x=80,y=95+3,width=430,height=25)
tk.Entry(filepath_s, textvariable=output_path).place(x=80,y=140+3,width=430,height=25)
tk.Button(filepath_s, command=lambda:browse_file(1),text="浏览").place(x=520,y=5,width=70,height=30)
tk.Button(filepath_s, command=lambda:browse_file(2),text="浏览").place(x=520,y=50,width=70,height=30)
tk.Button(filepath_s, command=lambda:browse_file(3),text="浏览").place(x=520,y=95,width=70,height=30)
tk.Button(filepath_s, command=lambda:browse_file(4,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

optional_s = tk.LabelFrame(synth_frame,text='选项')
optional_s.place(x=10,y=210,width=600,height=110)

tk.Label(optional_s, text="AccessKey：",anchor=tk.W).place(x=10,y=0,width=110,height=25)
tk.Label(optional_s, text="AccessKeySecret：",anchor=tk.W).place(x=10,y=30,width=110,height=25)
tk.Label(optional_s, text="Appkey：",anchor=tk.W).place(x=10,y=60,width=110,height=25)

tk.Entry(optional_s, textvariable=AccessKey).place(x=120,y=0,width=390,height=25)
tk.Entry(optional_s, textvariable=AccessKeySecret).place(x=120,y=30,width=390,height=25)
tk.Entry(optional_s, textvariable=Appkey).place(x=120,y=60,width=390,height=25)

flag_s = tk.LabelFrame(synth_frame,text='标志')
flag_s.place(x=10,y=320,width=600,height=110)

aliyun_logo = ImageTk.PhotoImage(Image.open('./doc/aliyun.png'))
tk.Label(flag_s,image = aliyun_logo).place(x=20,y=13)
tk.Label(flag_s,text='本项功能由阿里云语音合成支持，了解更多：').place(x=300,y=20)
tk.Button(flag_s,text='https://ai.aliyun.com/nls/',command=lambda: webbrowser.open('https://ai.aliyun.com/nls/'),fg='blue',relief='flat').place(x=300,y=40)

tk.Button(synth_frame, command=run_command_synth,text="开始",font=big_text).place(x=260,y=435,width=100,height=50)

# xml_frame

filepath_x = tk.LabelFrame(xml_frame,text='文件路径')
filepath_x.place(x=10,y=10,width=600,height=200)

tk.Label(filepath_x, text="媒体定义：",anchor=tk.W).place(x=10,y=5,width=70,height=30)
tk.Label(filepath_x, text="角色配置：",anchor=tk.W,fg='#909090').place(x=10,y=50,width=70,height=30)
tk.Label(filepath_x, text="时间轴：",anchor=tk.W).place(x=10,y=95,width=70,height=30)
tk.Label(filepath_x, text="输出路径：",anchor=tk.W).place(x=10,y=140,width=70,height=30)
tk.Entry(filepath_x, textvariable=media_define).place(x=80,y=5+3,width=430,height=25)
tk.Entry(filepath_x, textvariable=characor_table,state=tk.DISABLED).place(x=80,y=50+3,width=430,height=25)
tk.Entry(filepath_x, textvariable=timeline_file).place(x=80,y=95+3,width=430,height=25)
tk.Entry(filepath_x, textvariable=output_path).place(x=80,y=140+3,width=430,height=25)
tk.Button(filepath_x, command=lambda:browse_file(1),text="浏览").place(x=520,y=5,width=70,height=30)
tk.Button(filepath_x, command=lambda:browse_file(2),text="浏览",state=tk.DISABLED).place(x=520,y=50,width=70,height=30)
tk.Button(filepath_x, command=lambda:browse_file(5),text="浏览").place(x=520,y=95,width=70,height=30)
tk.Button(filepath_x, command=lambda:browse_file(4,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

optional_x = tk.LabelFrame(xml_frame,text='选项')
optional_x.place(x=10,y=210,width=600,height=110)

tk.Label(optional_x,text="分辨率-宽:",anchor=tk.W).place(x=10,y=5,width=70,height=30)
tk.Label(optional_x,text="分辨率-高:",anchor=tk.W).place(x=160,y=5,width=70,height=30)
tk.Label(optional_x,text="帧率:",anchor=tk.W).place(x=310,y=5,width=70,height=30)
tk.Label(optional_x,text="图层顺序:",anchor=tk.W).place(x=10,y=50,width=70,height=30)

tk.Entry(optional_x,textvariable=project_W).place(x=80,y=5,width=70,height=25)
tk.Entry(optional_x,textvariable=project_H).place(x=230,y=5,width=70,height=25)
tk.Entry(optional_x,textvariable=project_F).place(x=380,y=5,width=70,height=25)
tk.Entry(optional_x,textvariable=project_Z).place(x=80,y=50,width=370,height=25)

flag_x = tk.LabelFrame(xml_frame,text='标志')
flag_x.place(x=10,y=320,width=600,height=110)

PR_logo = ImageTk.PhotoImage(Image.open('./doc/PR.png'))
Eta_logo = ImageTk.PhotoImage(Image.open('./doc/eta.png'))
tk.Label(flag_x,image = PR_logo).place(x=20,y=10)
tk.Label(flag_x,text='通向Premiere Pro世界的通道，感谢伊塔的Idea，了解更多：').place(x=110,y=30)
#tk.Button(,image = Eta_logo).place(x=500,y=10)
tk.Button(flag_x,image = Eta_logo,command=lambda: webbrowser.open('https://space.bilibili.com/10414609'),relief='flat').place(x=500,y=7)

tk.Button(xml_frame, command=run_command_xml,text="开始",font=big_text).place(x=260,y=435,width=100,height=50)

# mp4_frame

filepath_v = tk.LabelFrame(mp4_frame,text='文件路径')
filepath_v.place(x=10,y=10,width=600,height=200)

tk.Label(filepath_v, text="媒体定义：",anchor=tk.W).place(x=10,y=5,width=70,height=30)
tk.Label(filepath_v, text="角色配置：",anchor=tk.W,fg='#909090').place(x=10,y=50,width=70,height=30)
tk.Label(filepath_v, text="时间轴：",anchor=tk.W).place(x=10,y=95,width=70,height=30)
tk.Label(filepath_v, text="输出路径：",anchor=tk.W).place(x=10,y=140,width=70,height=30)
tk.Entry(filepath_v, textvariable=media_define).place(x=80,y=5+3,width=430,height=25)
tk.Entry(filepath_v, textvariable=characor_table,state=tk.DISABLED).place(x=80,y=50+3,width=430,height=25)
tk.Entry(filepath_v, textvariable=timeline_file).place(x=80,y=95+3,width=430,height=25)
tk.Entry(filepath_v, textvariable=output_path).place(x=80,y=140+3,width=430,height=25)
tk.Button(filepath_v, command=lambda:browse_file(1),text="浏览").place(x=520,y=5,width=70,height=30)
tk.Button(filepath_v, command=lambda:browse_file(2),text="浏览",state=tk.DISABLED).place(x=520,y=50,width=70,height=30)
tk.Button(filepath_v, command=lambda:browse_file(5),text="浏览").place(x=520,y=95,width=70,height=30)
tk.Button(filepath_v, command=lambda:browse_file(4,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

optional_v = tk.LabelFrame(mp4_frame,text='选项')
optional_v.place(x=10,y=210,width=600,height=110)

tk.Label(optional_v,text="分辨率-宽:",anchor=tk.W).place(x=10,y=5,width=70,height=30)
tk.Label(optional_v,text="分辨率-高:",anchor=tk.W).place(x=160,y=5,width=70,height=30)
tk.Label(optional_v,text="帧率:",anchor=tk.W).place(x=310,y=5,width=70,height=30)
tk.Label(optional_v,text="图层顺序:",anchor=tk.W).place(x=10,y=50,width=70,height=30)

tk.Entry(optional_v,textvariable=project_W).place(x=80,y=5,width=70,height=25)
tk.Entry(optional_v,textvariable=project_H).place(x=230,y=5,width=70,height=25)
tk.Entry(optional_v,textvariable=project_F).place(x=380,y=5,width=70,height=25)
tk.Entry(optional_v,textvariable=project_Z).place(x=80,y=50,width=370,height=25)

flag_v = tk.LabelFrame(mp4_frame,text='标志')
flag_v.place(x=10,y=320,width=600,height=110)

ffmpeg_logo = ImageTk.PhotoImage(Image.open('./doc/ffmpeg.png'))
tk.Label(flag_v,image = ffmpeg_logo).place(x=20,y=10)
tk.Label(flag_v,text='本项功能调用ffmpeg实现，了解更多：').place(x=300,y=20)
tk.Button(flag_v,text='https://ffmpeg.org/',command=lambda: webbrowser.open('https://ffmpeg.org/'),fg='blue',relief='flat').place(x=300,y=40)

tk.Button(mp4_frame, command=run_command_mp4,text="开始",font=big_text).place(x=260,y=435,width=100,height=50)

Main_windows.mainloop()
