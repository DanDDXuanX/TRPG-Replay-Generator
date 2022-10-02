import os
import tkinter as tk
import webbrowser
from tkinter import messagebox

from PIL import Image, ImageTk

from .AppFrame import AppFrame


class SynthFrame(AppFrame):
    """
    语音合成页面
    """
    def __init__(self,master,app,*args, **kwargs):
        super().__init__(master,app,*args, **kwargs)
        # self.place(x=10,y=50) # 不需要在这里place，Application.printFrame函数里面已经做了这件事
        self.create_widgets()
        
    def create_widgets(self):
        # synth_frame
        filepath_s = tk.LabelFrame(self,text='文件路径')
        filepath_s.place(x=10,y=10,width=600,height=200)
        # 路径
        tk.Label(filepath_s, text="媒体定义：",anchor=tk.W).place(x=10,y=5,width=70,height=30)
        tk.Label(filepath_s, text="角色配置：",anchor=tk.W).place(x=10,y=50,width=70,height=30)
        tk.Label(filepath_s, text="log文件：",anchor=tk.W).place(x=10,y=95,width=70,height=30)
        tk.Label(filepath_s, text="输出路径：",anchor=tk.W).place(x=10,y=140,width=70,height=30)
        tk.Entry(filepath_s, textvariable=self.app.media_define).place(x=80,y=5+3,width=430,height=25)
        tk.Entry(filepath_s, textvariable=self.app.characor_table).place(x=80,y=50+3,width=430,height=25)
        tk.Entry(filepath_s, textvariable=self.app.stdin_logfile).place(x=80,y=95+3,width=430,height=25)
        tk.Entry(filepath_s, textvariable=self.app.output_path).place(x=80,y=140+3,width=430,height=25)
        tk.Button(filepath_s, command=lambda:self.call_browse_file(self.app.media_define),text="浏览").place(x=520,y=5,width=70,height=30)
        tk.Button(filepath_s, command=lambda:self.call_browse_file(self.app.characor_table),text="浏览").place(x=520,y=50,width=70,height=30)
        tk.Button(filepath_s, command=lambda:self.call_browse_file(self.app.stdin_logfile),text="浏览").place(x=520,y=95,width=70,height=30)
        tk.Button(filepath_s, command=lambda:self.call_browse_file(self.app.output_path,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

        # 选项
        def change_service(now):
            if now == optional_s:
                optional_s.place_forget()
                flag_s.place_forget()
                optional_azs.place(x=10,y=210,width=600,height=110)
                flag_azs.place(x=10,y=320,width=600,height=110)
            elif now == optional_azs:
                optional_azs.place_forget()
                flag_azs.place_forget()
                optional_s.place(x=10,y=210,width=600,height=110)
                flag_s.place(x=10,y=320,width=600,height=110)
            else:
                pass
        
        optional_s = tk.LabelFrame(self,text='选项')
        optional_s.place(x=10,y=210,width=600,height=110)

        self.label_AP = tk.Label(optional_s, text="Appkey：",anchor=tk.W)
        self.label_AP.place(x=10,y=0,width=110,height=25)
        self.label_AK = tk.Label(optional_s, text="AccessKey：",anchor=tk.W)
        self.label_AK.place(x=10,y=30,width=110,height=25)
        self.label_AS = tk.Label(optional_s, text="AccessKeySecret：",anchor=tk.W)
        self.label_AS.place(x=10,y=60,width=110,height=25)

        tk.Entry(optional_s, textvariable=self.app.Appkey).place(x=120,y=0,width=390,height=25)
        tk.Entry(optional_s, textvariable=self.app.AccessKey).place(x=120,y=30,width=390,height=25)
        tk.Entry(optional_s, textvariable=self.app.AccessKeySecret).place(x=120,y=60,width=390,height=25)
        tk.Button(optional_s,text="⇵",command=lambda: change_service(optional_s)).place(x=565,y=0,width=25,height=25)

        optional_azs = tk.LabelFrame(self,text='选项')
        #optional_azs.place(x=10,y=210,width=600,height=110)

        self.label_AZ = tk.Label(optional_azs, text="AzureKey：",anchor=tk.W)
        self.label_AZ.place(x=10,y=10,width=110,height=25)
        self.label_SR = tk.Label(optional_azs, text="服务区域：",anchor=tk.W)
        self.label_SR.place(x=10,y=50,width=110,height=25)

        tk.Entry(optional_azs, textvariable=self.app.AzureKey).place(x=120,y=10,width=390,height=25)
        tk.Entry(optional_azs, textvariable=self.app.ServiceRegion).place(x=120,y=50,width=390,height=25)
        tk.Button(optional_azs,text="⇵",command=lambda: change_service(optional_azs)).place(x=565,y=0,width=25,height=25)

        flag_s = tk.LabelFrame(self,text='标志')
        flag_s.place(x=10,y=320,width=600,height=110)
        self.aliyun_logo = ImageTk.PhotoImage(Image.open('./media/aliyun.png'))
        tk.Label(flag_s,image = self.aliyun_logo).place(x=20,y=13)
        tk.Label(flag_s,text='本项功能由阿里云语音合成支持，了解更多：').place(x=300,y=15)
        tk.Button(flag_s,text='https://ai.aliyun.com/nls/',command=lambda: webbrowser.open('https://ai.aliyun.com/nls/'),fg='blue',relief='flat').place(x=300,y=40)
        tk.Button(flag_s,text='试听',command=lambda:self.run_command_synth_preview('Aliyun')).place(x=540,y=55,width=50,height=25)

        flag_azs = tk.LabelFrame(self,text='标志')
        #flag_azs.place(x=10,y=320,width=600,height=110)
        self.azure_logo = ImageTk.PhotoImage(Image.open('./media/Azure.png'))
        tk.Label(flag_azs,image = self.azure_logo).place(x=20,y=8)
        tk.Label(flag_azs,text='本项功能由Azure认知语音服务支持，了解更多：').place(x=300,y=15)
        tk.Button(flag_azs,text='https://docs.microsoft.com/azure/',command=lambda: webbrowser.open('https://docs.microsoft.com/zh-cn/azure/cognitive-services'),fg='blue',relief='flat').place(x=300,y=40)
        tk.Button(flag_azs,text='试听',command=lambda:self.run_command_synth_preview('Azure')).place(x=540,y=55,width=50,height=25)

        tk.Button(self, command=self.run_command_synth,text="开始",font=self.app.big_text).place(x=260,y=435,width=100,height=50)

    def run_command_synth_preview(self,init_type='Aliyun'):
        """
        执行试听命令
        """
        command = self.app.python3 +' ./speech_synthesizer.py --PreviewOnly --Init {IN} --AccessKey {AK} --AccessKeySecret {AS} --Appkey {AP} --Azurekey {AZ} --ServRegion {SR}'
        command = command.format(IN=init_type, AK=self.app.AccessKey.get(), AS=self.app.AccessKeySecret.get(),AP=self.app.Appkey.get(),AZ=self.app.AzureKey.get(),SR=self.app.ServiceRegion.get()).replace('\n','').replace('\r','')
        try:
            print('[32m'+command+'[0m')
            exit_status = os.system(command)
            if exit_status != 0:
                raise OSError('Major error occurred in speech_synthesizer!')
            else:
                pass
        except Exception:
            messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了，检视控制台输出获取详细信息！')
    
    def run_command_synth(self):
        """
        执行语音合成命令
        """
        command = self.app.python3 +' ./speech_synthesizer.py --LogFile {lg} --MediaObjDefine {md} --CharacterTable {ct} --OutputPath {of} --AccessKey {AK} --AccessKeySecret {AS} --Appkey {AP} --Azurekey {AZ} --ServRegion {SR}'
        if '' in [self.app.stdin_logfile.get(),self.app.characor_table.get(),self.app.media_define.get(),self.app.output_path.get(),self.app.AccessKey.get(),self.app.AccessKeySecret.get(),self.app.Appkey.get(),self.app.AzureKey.get(),self.app.ServiceRegion.get()]:
            messagebox.showerror(title='错误',message='缺少必要的参数！')
        else:
            command = command.format(lg = self.app.stdin_logfile.get().replace('\\','/'),md = self.app.media_define.get().replace('\\','/'),
                                     of = self.app.output_path.get().replace('\\','/'), ct = self.app.characor_table.get().replace('\\','/'),
                                     AK=self.app.AccessKey.get(), AS=self.app.AccessKeySecret.get(),AP=self.app.Appkey.get(),AZ=self.app.AzureKey.get(),SR=self.app.ServiceRegion.get()).replace('\n','').replace('\r','') # a 1.10.7 处理由于key复制导致的异常换行
            try:
                print('[32m'+command+'[0m')
                exit_status = os.system(command)
                # 0. 有Alog生成，合成正常，可以继续执行主程序
                if exit_status == 0:
                    messagebox.showinfo(title='完毕',message='语音合成程序执行完毕！\nLog文件已更新')
                # 1. 无Alog生成，无需合成，可以继续执行主程序
                elif exit_status == 1:
                    messagebox.showwarning(title='警告',message='未找到待合成星标！\n语音合成未执行')
                # 2. 无Alog生成，合成未完成，不能继续执行主程序
                elif exit_status == 2:
                    messagebox.showwarning(title='警告',message='无法执行语音合成！\n检视控制台输出获取详细信息！')
                # 3. 有Alog生成，合成未完成，不能继续执行主程序
                elif exit_status == 3:
                    messagebox.showwarning(title='警告',message='语音合成进度中断！\nLog文件已更新')
                else:
                    raise OSError('Unknown Exception.')
            except Exception:
                messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了，检视控制台输出获取详细信息！')
