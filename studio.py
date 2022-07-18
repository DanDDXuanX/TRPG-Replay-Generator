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
import pandas as pd
import pickle

voice_lib = pd.read_csv('./media/voice_volume.tsv',sep='\t').set_index('Voice')

def open_Tuning_windows(father,init_type='阿里云'):
    def show_selected_options(event):
        pass
    def get_scale_to_intvar(variable):
        variable.set(int(variable.get()))
    # 窗口
    Tuning_windows = tk.Toplevel(father)
    Tuning_windows.resizable(0,0)
    Tuning_windows.geometry("400x400")
    Tuning_windows.config(background ='#e0e0e0')
    Tuning_windows.title('回声工坊 语音合成试听窗口')
    Tuning_windows.transient(father)
    # 主框
    tune_main_frame = tk.Frame(Tuning_windows)
    tune_main_frame.place(x=10,y=10,height=380,width=380)
    # 音源变量
    tts_service = tk.StringVar(tune_main_frame)
    tts_service.set(init_type)
    # 语速语调文本变量
    pitch_rate = tk.IntVar(tune_main_frame)
    speech_rate = tk.IntVar(tune_main_frame)
    text_to_synth = tk.StringVar(tune_main_frame)
    text_to_synth.set('在这里输入你想要合成的文本，然后点击试听即可播放。')
    # 选择音源变量
    tk.Label(tune_main_frame,text='服务：').place(x=10,y=10,width=40,height=25)
    choose_type = ttk.Combobox(tune_main_frame,textvariable=tts_service,value=['Aliyun','Azure'])
    choose_type.place(x=50,y=10,width=100,height=25)
    choose_type.bind("<<ComboboxSelected>>",show_selected_options)
    # 音源窗口
    Aliyun_frame = tk.LabelFrame(tune_main_frame,text='阿里云智能语音交互-参数')
    Azure_frame = tk.LabelFrame(tune_main_frame,text='Azure认知语音服务-参数')
    text_frame = tk.LabelFrame(tune_main_frame,text='文本')
    Servicetype = {'阿里云':Aliyun_frame,'微软Azure':Azure_frame}
    # 初始化显示的服务
    Servicetype[tts_service.get()].place(x=10,y=40,width=360,height=130)
    text_frame.place(x=10,y=180,width=360,height=150)
    # 阿里云参数
    aliyun_voice = tk.StringVar(Aliyun_frame)
    speech_rate.set(0)
    pitch_rate.set(0)
    ttk.Label(Aliyun_frame,text='音源名:').place(x=10,y=10,width=65,height=25)
    ttk.Label(Aliyun_frame,text='语速:').place(x=10,y=40,width=65,height=25)
    ttk.Label(Aliyun_frame,text='语调:').place(x=10,y=70,width=65,height=25)
    ttk.Combobox(Aliyun_frame,textvariable=aliyun_voice,values=list(voice_lib[voice_lib.service=='Aliyun'].index)).place(x=75,y=10,width=260,height=25)
    ttk.Spinbox(Aliyun_frame,from_=-500,to=500,textvariable=speech_rate,increment=10).place(x=75,y=40,width=50,height=25)
    ttk.Spinbox(Aliyun_frame,from_=-500,to=500,textvariable=pitch_rate,increment=10).place(x=75,y=70,width=50,height=25)
    ttk.Scale(Aliyun_frame,from_=-500,to=500,variable=speech_rate,command=lambda x:get_scale_to_intvar(speech_rate)).place(x=135,y=40,width=200,height=25)
    ttk.Scale(Aliyun_frame,from_=-500,to=500,variable=pitch_rate,command=lambda x:get_scale_to_intvar(pitch_rate)).place(x=135,y=70,width=200,height=25)
    # Azure参数
    # 文本
    # tk.Text(text_frame,textvariable=text_to_synth).place(x=10,y=5,width=335,height=120)
    # 主循环
    Tuning_windows.mainloop()
def Main():
    Main_windows = tk.Tk()
    Main_windows.geometry("100x100")
    open_Tuning_windows(Main_windows)
    Main_windows.mainloop()

Main()