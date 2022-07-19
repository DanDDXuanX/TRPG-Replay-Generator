import tkinter as tk
from tkinter import ttk
import pandas as pd

voice_lib = pd.read_csv('./media/voice_volume.tsv',sep='\t').set_index('Voice')

def open_Tuning_windows(father,init_type='阿里云'):
    # 根据选中的语音服务，切换frame
    def show_selected_options(event):
        nonlocal servframe_display
        servframe_display.place_forget()
        try:
            select = Servicetype[tts_service.get()]
        except:
            messagebox.showerror(title='错误',message='服务名错误！')
            select = Servicetype['阿里云']
        select.place(x=10,y=40,width=360,height=190)
        servframe_display = select
    # 根据选中的Azure音源，更新可用的role和style
    def update_selected_voice(event):
        azure_voice_selected = azure_voice.get()
        azure_style_available = voice_lib.loc[azure_voice_selected,'style'].split(',')
        azure_role_available = voice_lib.loc[azure_voice_selected,'role'].split(',')
        azure_style_combobox.config(values=azure_style_available)
        azure_role_combobox.config(values=azure_role_available)
        azure_style.set('general')
        azure_role.set('Default')
        azure_degree.set(1.0)
    # 将选择条的数值强行转换为整型
    def get_scale_to_intvar(variable):
        variable.set(int(variable.get()))
    # 窗口
    Tuning_windows = tk.Toplevel(father)
    Tuning_windows.resizable(0,0)
    Tuning_windows.geometry("400x460")
    Tuning_windows.config(background ='#e0e0e0')
    Tuning_windows.title('语音合成试听')
    Tuning_windows.transient(father)
    # 主框
    tune_main_frame = tk.Frame(Tuning_windows)
    tune_main_frame.place(x=10,y=10,height=440,width=380)
    # 语音服务变量
    tts_service = tk.StringVar(tune_main_frame)
    tts_service.set(init_type)
    # 语速语调文本变量
    pitch_rate = tk.IntVar(tune_main_frame)
    pitch_rate.set(0)
    speech_rate = tk.IntVar(tune_main_frame)
    speech_rate.set(0)
    # 选中音源变量
    tk.Label(tune_main_frame,text='服务：').place(x=10,y=10,width=40,height=25)
    choose_type = ttk.Combobox(tune_main_frame,textvariable=tts_service,value=['阿里云','微软Azure'])
    choose_type.place(x=50,y=10,width=100,height=25)
    choose_type.bind("<<ComboboxSelected>>",show_selected_options)
    # 音源窗口
    Aliyun_frame = tk.LabelFrame(tune_main_frame,text='阿里-参数')
    Azure_frame = tk.LabelFrame(tune_main_frame,text='微软-参数')
    text_frame = tk.LabelFrame(tune_main_frame,text='文本')
    Servicetype = {'阿里云':Aliyun_frame,'微软Azure':Azure_frame}
    # 初始化显示的服务
    servframe_display = Servicetype[tts_service.get()]
    servframe_display.place(x=10,y=40,width=360,height=190)
    text_frame.place(x=10,y=240,width=360,height=150)
    # 阿里云参数
    aliyun_voice = tk.StringVar(Aliyun_frame)
    ttk.Label(Aliyun_frame,text='音源名:').place(x=10,y=10,width=65,height=25)
    ttk.Label(Aliyun_frame,text='语速:').place(x=10,y=40,width=65,height=25)
    ttk.Label(Aliyun_frame,text='语调:').place(x=10,y=70,width=65,height=25)
    ttk.Combobox(Aliyun_frame,textvariable=aliyun_voice,values=list(voice_lib[voice_lib.service=='Aliyun'].index)).place(x=75,y=10,width=260,height=25)
    ttk.Spinbox(Aliyun_frame,from_=-500,to=500,textvariable=speech_rate,increment=10).place(x=75,y=40,width=50,height=25)
    ttk.Spinbox(Aliyun_frame,from_=-500,to=500,textvariable=pitch_rate,increment=10).place(x=75,y=70,width=50,height=25)
    ttk.Scale(Aliyun_frame,from_=-500,to=500,variable=speech_rate,command=lambda x:get_scale_to_intvar(speech_rate)).place(x=135,y=40,width=200,height=25)
    ttk.Scale(Aliyun_frame,from_=-500,to=500,variable=pitch_rate,command=lambda x:get_scale_to_intvar(pitch_rate)).place(x=135,y=70,width=200,height=25)
    # Azure参数
    azure_voice = tk.StringVar(Azure_frame)
    azure_style = tk.StringVar(Azure_frame)
    azure_degree = tk.DoubleVar(Azure_frame)
    azure_role = tk.StringVar(Azure_frame)
    azure_style.set('general')
    azure_degree.set(1.0)
    azure_role.set('Default')
    ttk.Label(Azure_frame,text='音源名:').place(x=10,y=10,width=65,height=25)
    ttk.Label(Azure_frame,text='风格:').place(x=10,y=40,width=65,height=25)
    ttk.Label(Azure_frame,text='风格强度:').place(x=215,y=40,width=65,height=25)
    ttk.Label(Azure_frame,text='扮演:').place(x=10,y=70,width=65,height=25)
    ttk.Label(Azure_frame,text='语速:').place(x=10,y=100,width=65,height=25)
    ttk.Label(Azure_frame,text='语调:').place(x=10,y=130,width=65,height=25)
    ## 选择音源名
    azure_voice_combobox = ttk.Combobox(Azure_frame,textvariable=azure_voice,values=list(voice_lib[voice_lib.service=='Azure'].index))
    azure_voice_combobox.place(x=75,y=10,width=260,height=25)
    azure_voice_combobox.bind("<<ComboboxSelected>>",update_selected_voice)
    ## 选择style就role
    azure_style_combobox = ttk.Combobox(Azure_frame,textvariable=azure_style,values=['general'])
    azure_style_combobox.place(x=75,y=40,width=130,height=25)
    ttk.Spinbox(Azure_frame,textvariable=azure_degree,from_=0.01,to=2,increment=0.1).place(x=285,y=40,width=50,height=25)
    azure_role_combobox = ttk.Combobox(Azure_frame,textvariable=azure_role,values=['Default'])
    azure_role_combobox.place(x=75,y=70,width=260,height=25)
    ## 选择语速和语调
    ttk.Spinbox(Azure_frame,from_=-500,to=500,textvariable=speech_rate,increment=10).place(x=75,y=100,width=50,height=25)
    ttk.Spinbox(Azure_frame,from_=-500,to=500,textvariable=pitch_rate,increment=10).place(x=75,y=130,width=50,height=25)
    ttk.Scale(Azure_frame,from_=-500,to=500,variable=speech_rate,command=lambda x:get_scale_to_intvar(speech_rate)).place(x=135,y=100,width=200,height=25)
    ttk.Scale(Azure_frame,from_=-500,to=500,variable=pitch_rate,command=lambda x:get_scale_to_intvar(pitch_rate)).place(x=135,y=130,width=200,height=25)
    # 文本框体
    text_to_synth = tk.Text(text_frame,font=("黑体",10))
    text_to_synth.place(x=10,y=5,width=335,height=115)
    text_to_synth.insert(tk.END,'在这里输入你想要合成的文本！')
    # 确定合成按钮
    ttk.Button(tune_main_frame,text='合成').place(x=160,y=395,height=40,width=60)

    # 主循环
    Tuning_windows.mainloop()
def Main():
    Main_windows = tk.Tk()
    Main_windows.geometry("100x100")
    open_Tuning_windows(Main_windows)
    Main_windows.mainloop()

Main()