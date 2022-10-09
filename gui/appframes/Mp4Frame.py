import os
import tkinter as tk
import webbrowser
from tkinter import messagebox

from PIL import Image, ImageTk

from .AppFrame import AppFrame


class Mp4Frame(AppFrame):
    """
    导出mp4的页面
    """
    def __init__(self,master,app,*args, **kwargs):
        super().__init__(master,app,*args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        """创建组件"""
        # mp4_frame
        filepath_v = tk.LabelFrame(self,text='文件路径')
        filepath_v.place(x=10,y=10,width=600,height=200)

        tk.Label(filepath_v, text="媒体定义：",anchor=tk.W).place(x=10,y=5,width=70,height=30)
        tk.Label(filepath_v, text="角色配置：",anchor=tk.W,fg='#909090').place(x=10,y=50,width=70,height=30)
        tk.Label(filepath_v, text="时间轴：",anchor=tk.W).place(x=10,y=95,width=70,height=30)
        tk.Label(filepath_v, text="输出路径：",anchor=tk.W).place(x=10,y=140,width=70,height=30)
        tk.Entry(filepath_v, textvariable=self.app.media_define).place(x=80,y=5+3,width=430,height=25)
        tk.Entry(filepath_v, textvariable=self.app.characor_table,state=tk.DISABLED).place(x=80,y=50+3,width=430,height=25)
        tk.Entry(filepath_v, textvariable=self.app.timeline_file).place(x=80,y=95+3,width=430,height=25)
        tk.Entry(filepath_v, textvariable=self.app.output_path).place(x=80,y=140+3,width=430,height=25)
        tk.Button(filepath_v, command=lambda:self.call_browse_file(self.app.media_define,'file','mediadef'),text="浏览").place(x=520,y=5,width=70,height=30)
        tk.Button(filepath_v, command=lambda:self.call_browse_file(self.app.characor_table,'file','chartab'),text="浏览",state=tk.DISABLED).place(x=520,y=50,width=70,height=30)
        tk.Button(filepath_v, command=lambda:self.call_browse_file(self.app.timeline_file,'file','timeline'),text="浏览").place(x=520,y=95,width=70,height=30)
        tk.Button(filepath_v, command=lambda:self.call_browse_file(self.app.output_path,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

        optional_v = tk.LabelFrame(self,text='选项')
        optional_v.place(x=10,y=210,width=600,height=110)

        tk.Label(optional_v,text="分辨率-宽:",anchor=tk.W).place(x=10,y=5,width=70,height=30)
        tk.Label(optional_v,text="分辨率-高:",anchor=tk.W).place(x=160,y=5,width=70,height=30)
        tk.Label(optional_v,text="帧率:",anchor=tk.W).place(x=310,y=5,width=70,height=30)
        tk.Label(optional_v,text="图层顺序:",anchor=tk.W).place(x=10,y=50,width=70,height=30)
        self.label_ql = tk.Label(optional_v,text="质量:",anchor=tk.W)
        self.label_ql.place(x=310,y=50,width=70,height=30)

        tk.Entry(optional_v,textvariable=self.app.project_W).place(x=80,y=5,width=70,height=25)
        tk.Entry(optional_v,textvariable=self.app.project_H).place(x=230,y=5,width=70,height=25)
        tk.Entry(optional_v,textvariable=self.app.project_F).place(x=380,y=5,width=70,height=25)
        tk.Entry(optional_v,textvariable=self.app.project_Z).place(x=80,y=50,width=220,height=25)
        tk.Entry(optional_v,textvariable=self.app.project_Q).place(x=380,y=50,width=70,height=25)

        flag_v = tk.LabelFrame(self,text='标志')
        flag_v.place(x=10,y=320,width=600,height=110)

        self.ffmpeg_logo = ImageTk.PhotoImage(Image.open('./media/ffmpeg.png'))
        tk.Label(flag_v,image = self.ffmpeg_logo).place(x=20,y=10)
        tk.Label(flag_v,text='本项功能调用ffmpeg实现，了解更多：').place(x=300,y=15)
        tk.Button(flag_v,text='https://ffmpeg.org/',command=lambda: webbrowser.open('https://ffmpeg.org/'),fg='blue',relief='flat').place(x=300,y=40)

        tk.Button(self, command=self.run_command_mp4,text="开始",font=self.app.big_text).place(x=260,y=435,width=100,height=50)

    def run_command_mp4(self):
        """
        执行导出mp4的命令
        """
        command = self.app.python3 + ' ./export_video.py --TimeLine {tm} --MediaObjDefine {md} --OutputPath {of} --FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd} --Quality {ql}'
        if '' in [self.app.timeline_file.get(),self.app.media_define.get(),self.app.output_path.get(),
                  self.app.project_W.get(),self.app.project_H.get(),self.app.project_F.get(),self.app.project_Z.get(),self.app.project_Q.get()]:
            messagebox.showerror(title='错误',message='缺少必要的参数！')
        else:
            command = command.format(tm = self.app.timeline_file.get().replace('\\','/'),
                                     md = self.app.media_define.get().replace('\\','/'), of = self.app.output_path.get().replace('\\','/'), 
                                     fps = self.app.project_F.get(), wd = self.app.project_W.get(),
                                     he = self.app.project_H.get(), zd = self.app.project_Z.get(), ql = self.app.project_Q.get())
            try:
                print('\x1B[32m'+command+'\x1B[0m')
                exit_status = os.system(command)
                if exit_status != 0:
                    raise OSError('Major error occurred in export_video!')
                else:
                    messagebox.showinfo(title='完毕',message='导出视频程序执行完毕！')
            except Exception:
                messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了，检视控制台输出获取详细信息！')
