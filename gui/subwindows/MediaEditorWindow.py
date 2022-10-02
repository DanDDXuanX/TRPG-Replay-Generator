import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from .Media import Animation, Background, Bubble, StrokeText, Text
from .MediaDefWindow import MediaDefWindow, open_media_def_window
from .SubWindow import SubWindow


class MediaEditorWindow(SubWindow):
    """
    媒体定义文件编辑器
    """
    # 需要用到的正则表达式
    RE_mediadef_args = re.compile('(fontfile|fontsize|color|line_limit|filepath|Main_Text|Header_Text|pos|mt_pos|ht_pos|align|line_distance|tick|loop|volume|edge_color|label_color)?\ {0,4}=?\ {0,4}(Text\(\)|[^,()]+|\([-\d,\ ]+\))')
    RE_parse_mediadef = re.compile('(\w+)[=\ ]+(Text|StrokeText|Bubble|Animation|Background|BGM|Audio)(\(.+\))')
    RE_vaildname = re.compile('^\w+$')
    
    def __init__(self,master,Edit_filepath='',fig_W=960,fig_H=540,*args, **kwargs):
        super().__init__(master,*args, **kwargs)
        self.edit_filepath = Edit_filepath
        self.fig_W = fig_W
        self.fig_H = fig_H
        # 主框体
        self.window_W , self.window_H = fig_W//2+40,fig_H//2+440

        self.resizable(0,0)
        self.geometry("{W}x{H}".format(W=self.window_W,H=self.window_H))
        self.config(background ='#e0e0e0')
        self.title('回声工坊 媒体定义文件编辑器')
        self.protocol('WM_DELETE_WINDOW',self.close_window)
        self.transient(master)
        try:
            self.iconbitmap('./media/icon.ico')
        except tk.TclError:
            pass
        
        # 初始化变量
        self.selected_name,self.selected_type,self.selected_args = 'None','None','None'
        self.selected = 0
        self.edit_return_value = "" # 返回的文件路径
        self.available_text = ['None','Text()'] # 所有的可用文本名
        self.used_variable_name = [] # 已经被用户占用的命名
        self.media_lines = [] # 保存当前所有媒体行，用于筛选时避免丢失原有媒体。有used_variable_name的地方就有它
        self.occupied_variable_name = open('./media/occupied_variable_name.list','r',encoding='utf8').read().split('\n') # 已经被系统占用的变量名
        
        self.create_widgets()
        self.load_media_define_file()
        
    def create_widgets(self):
        # 总框架
        frame_edit = tk.Frame(self)
        frame_edit.place(x=10,y=10,height=self.window_H-20,width=self.window_W-20)

        # 媒体对象信息框
        mediainfo_frame = tk.LabelFrame(frame_edit,text='媒体对象')
        mediainfo_frame.place(x=10,y=10,height=390,width=self.fig_W//2)

        # 顶部控件
        button_w = (self.fig_W//2-20)//8 # 这数字8 应该等于按键的 数量+1
        button_x = lambda x:10+(self.fig_W//2-20-button_w)//6*x # 这个数字6 应该等于按键的 数量-1

        # 导入媒体的按钮，宽
        ttk.Button(mediainfo_frame,text='载入目录',command=self.import_media).place(x=button_x(0),y=0,width=max(button_w,60),height=25)
        
        # 筛选媒体下拉框
        self.media_type = tk.StringVar(self)
        ttk.Label(mediainfo_frame,text='筛选：').place(x=button_x(1),y=0,width=40,height=25)
        choose_type = ttk.Combobox(mediainfo_frame,textvariable=self.media_type,value=['All','Text','StrokeText','Bubble','Background','Animation','BGM','Audio'])
        choose_type.place(x=button_x(1)+40,y=0,width=button_w*2-40,height=25) # 我就随便找个位置先放着，等后来人调整布局（都是绝对坐标很难搞啊）
        choose_type.current(0)
        choose_type.bind("<<ComboboxSelected>>",self.filter_media)

        # 搜索框
        self.search_text = tk.StringVar(self)
        ttk.Label(mediainfo_frame,text='搜索:').place(x=button_x(3),y=0,width=40,height=25)
        search_entry =  ttk.Entry(mediainfo_frame, textvariable=self.search_text)
        search_entry.place(x=button_x(3)+40,y=0,width=button_w*2-40,height=25) # 同上，位置暂时随便摆的
        search_entry.bind('<Key-Return>',self.search_media) # 回车后搜索

        # 缩放比例
        self.preview_fade = tk.DoubleVar(self)
        self.preview_fade.set(75)
        ttk.Label(mediainfo_frame,text='淡去:').place(x=button_x(5),y=0,width=40,height=25)
        ttk.Entry(mediainfo_frame,textvariable=self.preview_fade).place(x=button_x(5)+40,y=0,width=30,height=25)
        choose_fade = ttk.Scale(mediainfo_frame,from_=0,to=100,variable=self.preview_fade)
        choose_fade.place(x=button_x(5)+70,y=0,width=max(60,button_w*2-70),height=25)
        
        # 解决偶数颜色不显示的bug
        def fixed_map(option):
            return [elm for elm in style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled","!selected")]
        
        style = ttk.Style()
        style.map("Treeview",foreground=fixed_map("foreground"),background=fixed_map("background"))
        # 媒体列表
        ybar = ttk.Scrollbar(mediainfo_frame,orient='vertical')
        xbar = ttk.Scrollbar(mediainfo_frame,orient='horizontal')
        self.mediainfo = ttk.Treeview(mediainfo_frame,columns=['name','type','args'],show = "headings",selectmode = tk.BROWSE,yscrollcommand=ybar.set,xscrollcommand=xbar.set)
        ybar.config(command=self.mediainfo.yview)
        xbar.config(command=self.mediainfo.xview)
        ybar.place(x=self.fig_W//2-25,y=30,height=285,width=15)
        xbar.place(x=10,y=300,height=15,width=self.fig_W//2-35)
        self.mediainfo.column("name",anchor = "center",width=100)
        self.mediainfo.column("type",anchor = "center",width=100)
        self.mediainfo.column("args",anchor = "w",width=900)

        self.mediainfo.heading("name", text = "对象名称")
        self.mediainfo.heading("type", text = "类型")
        self.mediainfo.heading("args", text = "参数")

        self.mediainfo.place(x=10,y=30,height=270,width=self.fig_W//2-35)
        self.mediainfo.tag_configure("evenColor",background="#e6e6e6") # 行标签，用于偶数行着色

        self.mediainfo.bind('<ButtonRelease-1>', self.treeview_click)
        self.mediainfo.bind('<Double-Button-1>',self.preview_obj) # 双击左键预览
        self.mediainfo.bind('<Button-3>',self.edit_obj) # 单击右键编辑
        self.mediainfo.bind('<Delete>',self.del_obj) # Delete键删除
        self.mediainfo.bind('<Key>',self.handle_key_event) # 按键处理
        
        # 底部按键

        ttk.Button(mediainfo_frame,text='预览',command=self.preview_obj).place(x=button_x(0),y=325,width=button_w,height=35)
        ttk.Button(mediainfo_frame,text='新建',command=self.new_obj).place(x=button_x(1),y=325,width=button_w,height=35)
        ttk.Button(mediainfo_frame,text='复制',command=self.copy_obj).place(x=button_x(2),y=325,width=button_w,height=35)    
        ttk.Button(mediainfo_frame,text='编辑',command=self.edit_obj).place(x=button_x(3),y=325,width=button_w,height=35)
        ttk.Button(mediainfo_frame,text='删除',command=self.del_obj).place(x=button_x(4),y=325,width=button_w,height=35)
        ttk.Button(mediainfo_frame,text='保存',command=lambda:self.finish(False)).place(x=button_x(5),y=325,width=button_w,height=35)
        ttk.Button(mediainfo_frame,text='另存',command=lambda:self.finish(True)).place(x=button_x(6),y=325,width=button_w,height=35)

        # 预览图
        self.image_canvas = Image.open('./media/canvas.png').crop((0,0,self.fig_W,self.fig_H))
        self.blank_canvas = self.image_canvas.copy() # 用于覆盖在上一张图片上
        self.last_fade = 191
        self.blank_canvas.putalpha(self.last_fade) # alpha 1.10.6 220 -> 192 上一个预览画面的残影更强了
        self.show_canvas = ImageTk.PhotoImage(self.image_canvas.resize((self.fig_W//2,self.fig_H//2)))
        self.preview_canvas = tk.Label(frame_edit,bg='black')
        self.preview_canvas.config(image=self.show_canvas)
        self.preview_canvas.place(x=10,y=410,height=self.fig_H//2,width=self.fig_W//2)
 
    def load_media_define_file(self):
        """
        载入媒体定义文件
        """
        if self.edit_filepath!='': # 如果有指定输入文件
            try:
                mediadef_text = open(self.edit_filepath,'r',encoding='utf8').read().split('\n')
                if mediadef_text[-1] == '':
                    mediadef_text.pop() # 如果最后一行是空行，则无视掉最后一行
                warning_line = []
                i = -1 # 即使是输入空文件，也能正确弹出提示框
                
                for i,line in enumerate(mediadef_text):
                    parseline = self.RE_parse_mediadef.findall(line)
                    if len(parseline) == 1:
                        # 插入行，并进行偶数行着色
                        if i % 2 ==1:
                            self.mediainfo.insert('','end',values = parseline[0])
                        else:
                            self.mediainfo.insert('','end',values = parseline[0],tags=("evenColor"))
                        
                        # 如果是字体媒体，提前载入
                        # if parseline[0][1] == "Text" or parseline[0][1] == "StrokeText":
                        #     exec('global {name};{name}={type}{args}'.format(name=parseline[0][0],type=parseline[0][1],args=parseline[0][2]))

                        self.used_variable_name.append(parseline[0][0])
                        self.media_lines.append(parseline[0])

                        if parseline[0][1] in ['Text','StrokeText']:
                            self.available_text.append(parseline[0][0])
                    else:
                        warning_line.append(i+1)
                
                # 载入完毕先排个序
                self.sort_media()
                if warning_line == []:
                    messagebox.showinfo(title='完毕',message='载入完毕，共载入{i}条记录！'.format(i=i+1))
                else:
                    messagebox.showwarning(title='完毕',message='载入完毕，共载入{i}条记录，\n第{warning}行因为无法解析而被舍弃！'.format(i=i+1-len(warning_line),warning=','.join(map(str,warning_line))))
            except UnicodeDecodeError:
                messagebox.showerror(title='错误',message='无法载入文件，请检查文本文件编码！')
        else:
            pass
    
    def open_window(self):
        """
        打开编辑器窗口，返回关闭窗口时媒体定义文件的保存地址
        """
        
        self.mainloop()
        return self.edit_return_value
    # 关闭窗口
    def close_window(self):
        """
        关闭窗口时的处理函数，二次确认
        """
        if messagebox.askyesno(title='确认退出？',message='未保存的改动将会丢失！') == True:
            self.edit_return_value = self.edit_filepath
            self.destroy()
            self.quit()
        else:
            pass
    # 选中列单击
    def treeview_click(self,event=None):
        try:
            self.selected = self.mediainfo.selection()
            self.selected_name,self.selected_type,self.selected_args = self.mediainfo.item(self.selected, "values")
        except Exception:
            pass
    def instantiate_media_fromname(self,media_name):
        """
        实例化媒体名，返回值：
        0: 成功，媒体名（包括子对象已经全部实例化）
        NameError: 失败
        """
        def get_medianame(_NameError):
            # 获取NameError的变量名
            name_error = str(_NameError)
            name_err = name_error[name_error.index("'")+1:]
            name = name_err[:name_err.index("'")]
            return name
        # 遍历所有整个媒体列表
        for line in self.media_lines:
            name_this,type_this,args_this = line
            # 如果名字相匹配！
            if name_this == media_name:
                # 循环重试次数不可能超过媒体变量的总长
                for i in range(0,len(self.media_lines)):
                    try:
                        exec('global {name};{name}={type}{args}'.format(name=name_this,type=type_this,args=args_this))
                        # 未发生异常，则退出重试循环，返回0
                        return 0
                    except NameError as E:
                        # 如果存在尚未实例化，获取尚未定义的变量名
                        err_name = get_medianame(E)
                        # 递归调用
                        instantiation_return = self.instantiate_media_fromname(err_name)
                        # 如果递归调用遭遇未定义变量名，返回NameError
                        if instantiation_return != 0:
                            return instantiation_return
            else:
                pass
        # 找不到指定的媒体名
        return NameError("Media object name '" + media_name + "' is not defined!")
    # 预览
    def preview_obj(self,event=None):
        """预览媒体"""
        image_canvas = self.image_canvas
        last_fade = self.last_fade
        blank_canvas = self.blank_canvas
        preview_canvas = self.preview_canvas
        # 预览前先将当前选中项写入变量
        self.treeview_click(event) 
        if self.selected_type in ['Text','StrokeText','Bubble','Background','Animation']: # 执行
            try:
                this_fade = round(self.preview_fade.get()*2.55)
                if last_fade != this_fade:
                    self.blank_canvas.putalpha(this_fade)
                    last_fade = this_fade
                image_canvas.paste(blank_canvas,(0,0),mask=blank_canvas)
                # 实例化选中的
                instantiation_return = self.instantiate_media_fromname(self.selected_name)
                if instantiation_return != 0:
                    raise instantiation_return # NameError
                else:
                    # eval(self.selected_name).preview(image_canvas) # 另一种方法
                    exec('global {name};{name}.preview(image_canvas)'.format(name=self.selected_name))
                    self.show_canvas = ImageTk.PhotoImage(image_canvas.resize((self.fig_W//2,self.fig_H//2)))
                    preview_canvas.config(image = self.show_canvas)
            except NameError as E: # 使用了尚未定义的对象！
                messagebox.showerror(title='媒体名尚未定义！',message=E)
            except Exception as E: # 其他错误，主要是参数错误
                messagebox.showerror(title='错误',message=E)
        elif self.selected_type in ['BGM','Audio']:
            messagebox.showwarning(title='警告',message='音频类对象不支持预览！')
        elif self.selected_type == 'BuiltInAnimation':
            messagebox.showwarning(title='警告',message='内建动画对象不支持GUI编辑！')
        elif self.selected_type == 'None':
            messagebox.showwarning(title='警告',message='未选中任何对象！')
        else:
            messagebox.showerror(title='错误',message='不支持的媒体定义类型：'+self.selected_type)
    # 新建
    def new_obj(self,event=None):
        try:# 非win系统，可能没有disable
            self.attributes('-disabled',True)
        except Exception:
            pass
        # new_obj = MediaDefWindow(self).open()
        new_obj = open_media_def_window(father = self,image_canvas = self.image_canvas,available_Text= self.available_text,used_variable_name=self.used_variable_name)
        try:
            self.attributes('-disabled',False)
        except Exception:
            pass
        self.lift()
        self.focus_force()
        if new_obj:
            self.used_variable_name.append(new_obj[0]) # 新建的媒体名
            self.media_lines.append(new_obj)
            self.mediainfo.insert('','end',values =new_obj) # 否则插入在最后

            if new_obj[1] in ['Text','StrokeText']: # 如果新建了文本
                self.available_text.append(new_obj[0])

        self.sort_media()
    # 复制
    def copy_obj(self,event=None):
        if self.selected == 0:
            pass
        else:
            i = 1
            while True:
                new_name = self.selected_name+'_cp'+str(i)
                if (new_name in self.used_variable_name)|(new_name in self.occupied_variable_name):
                    i = i + 1
                else:
                    break
            self.used_variable_name.append(new_name) # 新建的媒体名
            self.media_lines.append((new_name,self.selected_type,self.selected_args))
            self.mediainfo.insert('','end',values =(new_name,self.selected_type,self.selected_args)) # 否则插入到最后面

            if self.selected_type in ['Text','StrokeText']: # 如果新建了文本
                self.available_text.append(new_name)

        self.sort_media()
    # 编辑
    def edit_obj(self,event=None):
        selected = self.selected
        selected_name = self.selected_name
        selected_type = self.selected_type
        selected_args = self.selected_args
        if selected == 0:
            pass
        else:
            try:
                self.attributes('-disabled',True)
            except Exception:
                pass
            new_obj = open_media_def_window(self,i_name=selected_name,i_type=selected_type,i_args=selected_args,image_canvas = self.image_canvas,available_Text= self.available_text,used_variable_name=self.used_variable_name)
            try:
                self.attributes('-disabled',False)
            except Exception:
                pass
            self.lift()
            self.focus_force()
            if new_obj:
                self.used_variable_name.remove(selected_name) # 原来的媒体名
                self.used_variable_name.append(new_obj[0]) # 新建的媒体名
                self.media_lines.remove((selected_name,selected_type,selected_args))
                self.media_lines.append(new_obj)

                if selected_type in ['Text','StrokeText']: # 如果编辑的对象是文本
                    self.available_text.remove(selected_name)
                    self.available_text.append(new_obj[0])

                self.mediainfo.item(selected,values=new_obj)
                selected_name,selected_type,selected_args = new_obj
        self.sort_media()
    # 删除
    def del_obj(self,event=None):
        selected = self.selected
        selected_name = self.selected_name
        selected_type = self.selected_type
        selected_args = self.selected_args
        if selected == 0:
            pass
        else:
            self.mediainfo.delete(selected)
            self.used_variable_name.remove(selected_name)
            self.media_lines.remove((selected_name,selected_type,selected_args))

            if selected_type in ['Text','StrokeText']: # 如果删除了文本
                self.available_text.remove(selected_name)
            selected = 0
            selected_name,selected_type,selected_args = 'None','None','None'
    # 完成
    def finish(self,saveas=False):
        if (self.edit_filepath != '')&(saveas==False):
            ofile = open(self.edit_filepath,'w',encoding='utf8')
            self.edit_return_value = self.edit_filepath
        else:
            outputformat = [('All Files', '*.*'), ('Text Document', '*.txt')] 
            Save_filepath = filedialog.asksaveasfilename(filetypes = outputformat, defaultextension = outputformat)
            if Save_filepath == '':
                return False
            ofile = open(Save_filepath,'w',encoding='utf8')
            self.edit_return_value = Save_filepath
        
        # 保存前先将筛选器调回All
        self.media_type.set("All")
        self.filter_media(None)

        for lid in self.mediainfo.get_children(): # 输出表格内容
            #print(mediainfo.item(lid, "values"))
            ofile.write('{0} = {1}{2}\n'.format(*self.mediainfo.item(lid, "values")))
        ofile.close()
        self.destroy()
        self.quit()
    # 更新表格显示数据，注意并不会修改统计数据，只会更新表格显示的内容
    def update_treeview(self,new_list):
        i = 0
        self.mediainfo.delete(*self.mediainfo.get_children()) # 清空媒体
        for medium in new_list:
            if i % 2 == 1:
                self.mediainfo.insert('','end',values=medium)
            else:
                self.mediainfo.insert('','end',values=medium,tags=("evenColor"))
            i+=1
    # 过滤媒体
    def filter_media(self,event):
        t = self.media_type.get()
        
        if t == 'All':
            filtered_list = self.media_lines
        else:
            filtered_list = [x for x in self.media_lines if x[1] == t]
        
        # 由于没有改动media_lines，所以不必在“All”选项时将文本媒体特地插到头部，按顺序遍历即可
        self.update_treeview(filtered_list)
    # 给媒体分类排序
    def sort_media(self): 
        priority = {
            "Text":1,
            "StrokeText":2,
            "Animation":3, 
            "Bubble":4, 
            "Background":5,
            "Audio":6, 
            "BGM":7
        }

        self.media_lines.sort(key=lambda elem:priority[elem[1]])
        self.update_treeview(self.media_lines)
    # 搜索框的回车事件处理函数
    def search_media(self,event):
        text = self.search_text.get()
        result_list = [x for x in self.media_lines if x[0].find(text)!=-1 ]
        self.update_treeview(result_list)
    # 批量载入媒体
    def import_media(self):
        path = filedialog.askdirectory()
        media_parameter_dict = {
            "Bubble":"(filepath='{}',Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),ht_pos=(0,0),align='left',line_distance=1.5)",
            "Background":"(filepath='{}',pos=(0,0))",
            "Animation":"(filepath='{}',pos=(0,0),tick=1,loop=True)",
            "BGM":"(filepath='{}',volume=100,loop=True)",
            "Audio":"(filepath='{}')"
        }
        media = []
        warning_line = []
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                if dir in media_parameter_dict.keys():
                    # 如果是对应的媒体文件夹，则进入其中遍历文件
                    for sub_root, sub_dirs, sub_files in os.walk(os.path.join(root, dir),topdown=False):
                        for sub_file in sub_files:
                            # 将媒体文件夹中的每个媒体都添加到列表中
                            abs_path = os.path.join(sub_root, sub_file).replace('\\','/')

                            medium_name = sub_file.split('.')[0] # 去除扩展名
                            
                            if ((medium_name in self.occupied_variable_name)|(medium_name in self.used_variable_name)):
                                # 名字在已经占用（用户或系统）的名字里面
                                warning_line.append("“{}”是已经被占用的变量名！".format(medium_name))
                            elif (len(re.findall('^\w+$',medium_name))==0) | (medium_name[0].isdigit()): # 全字符是\w，且首字符不是数字
                                # 如果新名字是非法的变量名
                                warning_line.append("“{}”是非法的变量名！".format(medium_name))
                            else:
                                medium = (medium_name,dir,media_parameter_dict[dir].format(abs_path))
                                media.append(medium)
        if warning_line == []:
            messagebox.showinfo(title='完毕',message='载入完毕，共载入{}条记录！'.format(len(media)))
        else:
            messagebox.showwarning(title='完毕',message='载入完毕，共载入{i}条记录，\n无法解析而被舍弃的内容与原因如下：\n{warning}'.format(i=len(media),warning='\n'.join(map(str,warning_line))))
        self.media_lines.extend(media)
        self.media_type.set('All')
        self.update_treeview(self.media_lines)
    # 按键事件处理
    def handle_key_event(self,event):
        if event.char == 'e' or event.char == 'E':# 编辑（Edit）
            self.edit_obj(event)
        elif event.char == 'a' or event.char == 'A':# 新建（Add）
            self.new_obj(event)
        elif event.char == 'd' or event.char == 'D':# 复制（Duplicate）
            self.copy_obj(event)

