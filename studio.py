from distutils import text_file
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox
from tkinter import colorchooser
from PIL import Image,ImageTk,ImageFont,ImageDraw
import webbrowser
import os
import sys
import re
import pickle

from pygame import init

def open_Tuning_windows(father,init_type='阿里云'):
    def show_selected_options(event):
        pass
    # 窗口
    Tuning_windows = tk.Toplevel(father)
    Tuning_windows.resizable(0,0)
    Tuning_windows.geometry("400x400")
    Tuning_windows.config(background ='#e0e0e0')
    Tuning_windows.title('回声工坊 语音合成试听窗口')
    Tuning_windows.transient(father)
    # 主框
    tunaudio = tk.Frame(Tuning_windows)
    tunaudio.place(x=10,y=10,height=380,width=380)
    # 音源变量
    tts_service = tk.StringVar(Tuning_windows)
    tts_service.set(init_type)
    # 选择音源变量
    tk.Label(tunaudio,text='服务：').place(x=10,y=10,width=40,height=25)
    choose_type = ttk.Combobox(tunaudio,textvariable=tts_service,value=['Aliyun','Azure'])
    choose_type.place(x=50,y=10,width=100,height=25)
    choose_type.bind("<<ComboboxSelected>>",show_selected_options)
    # 音源窗口
    Aliyun_frame = tk.LabelFrame(tunaudio,text='阿里云智能语音交互-参数')
    Azure_frame = tk.LabelFrame(tunaudio,text='Azure认知语音服务-参数')
    Servicetype = {'阿里云':Aliyun_frame,'微软Azure':Azure_frame}
    Servicetype[tts_service.get()].place(x=10,y=40,width=360,height=315)
    # 阿里云参数
    aliyun_voice = tk.StringVar(Aliyun_frame)
    aliyun_speech_rate = tk.IntVar(Aliyun_frame)
    aliyun_pitch_rate = tk.IntVar(Aliyun_frame)
    aliyun_speech_rate.set(0)
    aliyun_pitch_rate.set(0)
    ttk.Label(Aliyun_frame,text='音源名:').place(x=10,y=10,width=65,height=25)
    ttk.Label(Aliyun_frame,text='语速:').place(x=10,y=40,width=65,height=25)
    ttk.Label(Aliyun_frame,text='语调:').place(x=10,y=70,width=65,height=25)
    ttk.Entry(Aliyun_frame,textvariable=aliyun_voice).place(x=75,y=10,width=260,height=25)
    ttk.Entry(Aliyun_frame,textvariable=aliyun_speech_rate).place(x=75,y=40,width=50,height=25)
    ttk.Entry(Aliyun_frame,textvariable=aliyun_pitch_rate).place(x=75,y=70,width=50,height=25)
    ttk.Scale(Aliyun_frame,from_=-500,to=500,variable=aliyun_speech_rate).place(x=135,y=40,width=200,height=25)
    ttk.Scale(Aliyun_frame,from_=-500,to=500,variable=aliyun_pitch_rate).place(x=135,y=70,width=200,height=25)
    # Azure参数
    # 主循环
    Tuning_windows.mainloop()
def Main():
    Main_windows = tk.Tk()
    Main_windows.geometry("100x100")
    open_Tuning_windows(Main_windows)
    Main_windows.mainloop()

Main()