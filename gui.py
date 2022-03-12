#!/usr/bin/env python
# coding: utf-8
edtion = 'alpha 1.7.2'

import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox
from tkinter import colorchooser
from PIL import Image,ImageTk,ImageFont,ImageDraw
import webbrowser
import os
#import sys
import re

# preview 的类 定义
label_pos_show_text = ImageFont.truetype('./media/fzxbsjt.TTF', 30)

class Text:
    def __init__(self,fontfile='./media/simhei.ttf',fontsize=40,color=(0,0,0,255),line_limit=20):
        self.text_render = ImageFont.truetype(fontfile, fontsize)
        self.color=color
        self.size=fontsize
        self.line_limit = line_limit
    def draw(self,lenth=-1):
        if lenth ==-1:
            lenth = self.line_limit
        test_canvas = Image.new(mode='RGBA',size=(self.size*self.line_limit,self.size*2),color=(0,0,0,0))
        test_draw = ImageDraw.Draw(test_canvas)
        test_draw.text((0,0), ('测试文本'*50)[0:lenth], font = self.text_render,fill = self.color)
        return test_canvas.crop(test_canvas.getbbox())
    def preview(self):
        can_W,can_H = image_canvas.size
        draw_text = self.draw()
        txt_w,txt_h = draw_text.size
        image_canvas.paste(draw_text,((can_W-txt_w)//2,(can_H-txt_h)//2),mask=draw_text.split()[-1])
class Bubble:
    def __init__(self,filepath,Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),ht_pos=(0,0),align='left',line_distance=1.5):
        self.media = Image.open(filepath)
        self.pos = pos
        self.MainText = Main_Text
        self.mt_pos = mt_pos
        self.Header = Header_Text
        self.ht_pos = ht_pos
        self.line_distance = line_distance
        if align in ('left','center'):
            self.align = align
        else:
            raise ValueError('align非法参数：',align)
    def preview(self):
        def pos_add(pos1,pos2):
            return pos1[0]+pos2[0],pos1[1]+pos2[1]
        if self.media.mode == 'RGBA':
            image_canvas.paste(self.media,self.pos,mask=self.media.split()[-1])
        else:
            image_canvas.paste(self.media,self.pos)
        if self.Header != None:
            draw_text = self.Header.draw()
            image_canvas.paste(draw_text,pos_add(self.ht_pos,self.pos),draw_text.split()[-1])
        if self.MainText != None:
            tx_w = self.MainText.size*self.MainText.line_limit
            tx_h = self.line_distance*self.MainText.size
            mx,my = self.mt_pos
            for i,l in enumerate(range(self.MainText.line_limit,0,-self.MainText.line_limit//4)):
                draw_text = self.MainText.draw(l)
                image_canvas.paste(draw_text,pos_add(self.pos,(int(mx+(tx_w-draw_text.size[0])//2*(self.align=='center')),int(my+i*tx_h))),draw_text.split()[-1])
        draw = ImageDraw.Draw(image_canvas)
        p_x,p_y = self.pos
        h_x,h_y = pos_add(self.ht_pos,self.pos)
        m_x,m_y = pos_add(self.mt_pos,self.pos)
        draw.line([p_x-100,p_y,p_x+100,p_y],fill='green',width=2)
        draw.line([p_x,p_y-100,p_x,p_y+100],fill='green',width=2)
        draw.text((p_x,p_y),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='green')
        draw.line([h_x-100,h_y,h_x+100,h_y],fill='blue',width=2)
        draw.line([h_x,h_y-50,h_x,h_y+50],fill='blue',width=2)
        draw.text((h_x,h_y-35),'({0},{1})'.format(h_x-p_x,h_y-p_y),font=label_pos_show_text,fill='blue')
        draw.line([m_x-100,m_y,m_x+100,m_y],fill='blue',width=2)
        draw.line([m_x,m_y-50,m_x,m_y+50],fill='blue',width=2)
        draw.text((m_x,m_y-35),'({0},{1})'.format(m_x-p_x,m_y-p_y),font=label_pos_show_text,fill='blue')
class Background:
    cmap = {'black':(0,0,0,255),'white':(255,255,255,255),'greenscreen':(0,177,64,255)}
    def __init__(self,filepath,pos = (0,0)):
        if filepath in Background.cmap.keys(): #添加了，对纯色定义的背景的支持
            self.media = Image.new(screen_size,mode='RGBA')
            self.media.fill(Background.cmap[filepath])
        else:
            self.media = Image.open(filepath)
        self.pos = pos
    def preview(self):
        if self.media.mode == 'RGBA':
            image_canvas.paste(self.media,self.pos,mask=self.media.split()[-1])
        else:
            image_canvas.paste(self.media,self.pos)
        draw = ImageDraw.Draw(image_canvas)
        p_x,p_y = self.pos
        draw.line([p_x-100,p_y,p_x+100,p_y],fill='green',width=2)
        draw.line([p_x,p_y-100,p_x,p_y+100],fill='green',width=2)
        draw.text((p_x,p_y),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='green')
class Animation:
    def __init__(self,filepath,pos = (0,0),tick=1,loop=True):
        if '*' in filepath:
            raise ValueError('动画对象不支持预览！')
        else:
            self.media = Image.open(filepath)
        self.pos = pos
        self.loop = loop
        self.this = 0
        self.tick = tick
    def preview(self):
        if self.media.mode == 'RGBA':
            image_canvas.paste(self.media,self.pos,mask=self.media.split()[-1])
        else:
            image_canvas.paste(self.media,self.pos)
        draw = ImageDraw.Draw(image_canvas)
        p_x,p_y = self.pos
        draw.line([p_x-100,p_y,p_x+100,p_y],fill='green',width=2)
        draw.line([p_x,p_y-100,p_x,p_y+100],fill='green',width=2)
        draw.text((p_x,p_y),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='green')

# 编辑区，媒体定义窗
def Media_def_window():
    global obj_return_value,type_display,Mediatype,o_name,o_type
    obj_return_value = False
    def show_selected_options(event):
        global type_display
        type_display.place_forget()
        try:
            select = Mediatype[o_type.get()]
        except KeyError:
            select = Empty_frame
        select.place(x=10,y=40,width=300,height=270)
        type_display = select
    def comfirm_obj():
        global obj_return_value
        if '' in [o_name.get(),o_type.get()]:
            messagebox.showerror(title='错误',message='缺少必要的参数！')
        else:
            get_args = {
                'fontfile':fontfile.get(),'fontsize':fontsize.get(),'color':color.get(),'line_limit':line_limit.get(),
                'filepath':filepath.get(),'Main_Text':Main_Text.get(),'Header_Text':Header_Text.get(),
                'pos':pos.get(),'mt_pos':mt_pos.get(),'ht_pos':ht_pos.get(),'align':align.get(),
                'line_distance':line_distance.get(),'tick':tick.get(),'loop':loop.get(),
                'volume':volume.get()
            }
            this_tplt = arg_tplt[o_type.get()]
            
            obj_return_value = (o_name.get(),o_type.get(),this_tplt.format(**get_args))
            Objdef_windows.destroy()
            Objdef_windows.quit()
    def close_window():
        obj_return_value = False
        Objdef_windows.destroy()
        Objdef_windows.quit()

    Objdef_windows = tk.Toplevel()
    Objdef_windows.resizable(0,0)
    Objdef_windows.geometry("340x380")
    Objdef_windows.iconbitmap('./doc/icon.ico')
    Objdef_windows.config(background ='#e0e0e0')
    #Objdef_windows.attributes('-topmost', True)
    Objdef_windows.title('Media Define.')
    Objdef_windows.protocol('WM_DELETE_WINDOW',close_window)

    # 主框
    objdef = tk.Frame(Objdef_windows)
    objdef.place(x=10,y=10,height=360,width=320)

    o_name = tk.StringVar(Objdef_windows)
    o_type = tk.StringVar(Objdef_windows)

    o_name.set('')
    o_type.set('')

    arg_tplt = {
        'Text':"(fontfile='{fontfile}',fontsize={fontsize},color={color},line_limit={line_limit})",
        'Bubble':"(filepath='{filepath}',Main_Text={Main_Text},Header_Text={Header_Text},pos={pos},mt_pos={mt_pos},ht_pos={ht_pos},align='{align}',line_distance={line_distance})",
        'Background':"(filepath='{filepath}',pos={pos})",
        'Animation':"(filepath='{filepath}',pos={pos},tick={tick},loop={loop})",
        'Audio':"(filepath='{filepath}')",
        'BGM':"(filepath='{filepath}',volume={volume},loop={loop})"
    }

    # 名称
    tk.Label(objdef,text='名称：').place(x=10,y=10,width=40,height=25)
    tk.Entry(objdef,textvariable=o_name).place(x=50,y=10,width=100,height=25)

    # 类型
    tk.Label(objdef,text='类型：').place(x=160,y=10,width=40,height=25)
    choose_type = ttk.Combobox(objdef,textvariable=o_type,value=['Text','Bubble','Background','Animation','BGM','Audio'])
    choose_type.place(x=200,y=10,width=100,height=25)
    choose_type.bind("<<ComboboxSelected>>",show_selected_options)

    # 各个媒体的label_Frame
    Empty_frame = tk.LabelFrame(objdef,text='参数')
    Text_frame = tk.LabelFrame(objdef,text='Text参数')
    Bubble_frame = tk.LabelFrame(objdef,text='Bubble参数')
    Background_frame = tk.LabelFrame(objdef,text='Background参数')
    Animation_frame = tk.LabelFrame(objdef,text='Animation参数')
    BGM_frame = tk.LabelFrame(objdef,text='BGM参数')
    Audio_frame = tk.LabelFrame(objdef,text='Audio参数')
    Mediatype = {'Text':Text_frame,'Bubble':Bubble_frame,'Background':Background_frame,'Animation':Animation_frame,'BGM':BGM_frame,'Audio':Audio_frame}

    #初始状态
    Empty_frame.place(x=10,y=40,width=300,height=270)
    type_display = Empty_frame

    fontfile = tk.StringVar(Objdef_windows)
    fontsize = tk.IntVar(Objdef_windows)
    color = tk.StringVar(Objdef_windows)
    line_limit = tk.IntVar(Objdef_windows)
    filepath = tk.StringVar(Objdef_windows)
    Main_Text = tk.StringVar(Objdef_windows)
    Header_Text = tk.StringVar(Objdef_windows)
    pos = tk.StringVar(Objdef_windows)
    mt_pos = tk.StringVar(Objdef_windows)
    ht_pos = tk.StringVar(Objdef_windows)
    align = tk.StringVar(Objdef_windows)
    line_distance = tk.DoubleVar(Objdef_windows)
    tick = tk.IntVar(Objdef_windows)
    loop = tk.BooleanVar(Objdef_windows)
    volume = tk.IntVar()

    fontfile.set('./media/simhei.ttf')
    fontsize.set(40)
    color.set('(0,0,0,255)')
    line_limit.set(20)
    filepath.set('')
    Main_Text.set('Text()')
    Header_Text.set('None')
    pos.set('(0,0)')
    mt_pos.set('(0,0)')
    ht_pos.set('(0,0)')
    align.set('left')
    line_distance.set(1.5)
    tick.set(1)
    loop.set(True)
    volume.set(100)

    # Text_frame:
    tk.Label(Text_frame,text='字体文件').place(x=10,y=10,width=70,height=25)
    tk.Label(Text_frame,text='字体大小').place(x=10,y=40,width=70,height=25)
    tk.Label(Text_frame,text='字体颜色').place(x=10,y=70,width=70,height=25)
    tk.Label(Text_frame,text='单行字数').place(x=10,y=100,width=70,height=25)
    tk.Entry(Text_frame,textvariable=fontfile).place(x=80,y=10,width=150,height=25)
    tk.Entry(Text_frame,textvariable=fontsize).place(x=80,y=40,width=150,height=25)
    tk.Entry(Text_frame,textvariable=color).place(x=80,y=70,width=150,height=25)
    tk.Entry(Text_frame,textvariable=line_limit).place(x=80,y=100,width=150,height=25)
    tk.Button(Text_frame,text='浏览',command=lambda:browse_file(fontfile)).place(x=230,y=10,width=60,height=25)
    tk.Label(Text_frame,text='(整数)').place(x=230,y=40,width=60,height=25)
    tk.Button(Text_frame,text='选择',command=lambda:choose_color(color)).place(x=230,y=70,width=60,height=25)
    tk.Label(Text_frame,text='(整数)').place(x=230,y=100,width=60,height=25)

    # Bubble_frame
    tk.Label(Bubble_frame,text='底图文件').place(x=10,y=10,width=70,height=25)
    tk.Label(Bubble_frame,text='主文本字体').place(x=10,y=40,width=70,height=25)
    tk.Label(Bubble_frame,text='头文本字体').place(x=10,y=70,width=70,height=25)
    tk.Label(Bubble_frame,text='底图位置').place(x=10,y=100,width=70,height=25)
    tk.Label(Bubble_frame,text='主文本位置').place(x=10,y=130,width=70,height=25)
    tk.Label(Bubble_frame,text='头文本位置').place(x=10,y=160,width=70,height=25)
    tk.Label(Bubble_frame,text='对齐模式').place(x=10,y=190,width=70,height=25)
    tk.Label(Bubble_frame,text='主文本行距').place(x=10,y=220,width=70,height=25)
    tk.Entry(Bubble_frame,textvariable=filepath).place(x=80,y=10,width=150,height=25)
    tk.Entry(Bubble_frame,textvariable=Main_Text).place(x=80,y=40,width=150,height=25)
    tk.Entry(Bubble_frame,textvariable=Header_Text).place(x=80,y=70,width=150,height=25)
    tk.Entry(Bubble_frame,textvariable=pos).place(x=80,y=100,width=150,height=25)
    tk.Entry(Bubble_frame,textvariable=mt_pos).place(x=80,y=130,width=150,height=25)
    tk.Entry(Bubble_frame,textvariable=ht_pos).place(x=80,y=160,width=150,height=25)
    tk.Entry(Bubble_frame,textvariable=align).place(x=80,y=190,width=150,height=25)
    tk.Entry(Bubble_frame,textvariable=line_distance).place(x=80,y=220,width=150,height=25)
    tk.Button(Bubble_frame,text='浏览',command=lambda:browse_file(filepath)).place(x=230,y=10,width=60,height=25)
    tk.Label(Bubble_frame,text='(选择)').place(x=230,y=40,width=60,height=25)
    tk.Label(Bubble_frame,text='(选择)').place(x=230,y=70,width=60,height=25)
    tk.Label(Bubble_frame,text='(X,Y)').place(x=230,y=100,width=60,height=25)
    tk.Label(Bubble_frame,text='(X,Y)').place(x=230,y=130,width=60,height=25)
    tk.Label(Bubble_frame,text='(X,Y)').place(x=230,y=160,width=60,height=25)
    tk.Label(Bubble_frame,text='(选择)').place(x=230,y=190,width=60,height=25)
    tk.Label(Bubble_frame,text='(小数)').place(x=230,y=220,width=60,height=25)

    # Background
    tk.Label(Background_frame,text='背景文件').place(x=10,y=10,width=70,height=25)
    tk.Label(Background_frame,text='背景位置').place(x=10,y=40,width=70,height=25)
    tk.Entry(Background_frame,textvariable=filepath).place(x=80,y=10,width=150,height=25)
    tk.Entry(Background_frame,textvariable=pos).place(x=80,y=40,width=150,height=25)
    tk.Button(Background_frame,text='浏览',command=lambda:browse_file(filepath)).place(x=230,y=10,width=60,height=25)
    tk.Label(Background_frame,text='(X,Y)').place(x=230,y=40,width=60,height=25)

    # Animation
    tk.Label(Animation_frame,text='立绘文件').place(x=10,y=10,width=70,height=25)
    tk.Label(Animation_frame,text='立绘位置').place(x=10,y=40,width=70,height=25)
    tk.Label(Animation_frame,text='动画时刻').place(x=10,y=70,width=70,height=25)
    tk.Label(Animation_frame,text='动画循环').place(x=10,y=100,width=70,height=25)
    tk.Entry(Animation_frame,textvariable=filepath).place(x=80,y=10,width=150,height=25)
    tk.Entry(Animation_frame,textvariable=pos).place(x=80,y=40,width=150,height=25)
    tk.Entry(Animation_frame,textvariable=tick).place(x=80,y=70,width=150,height=25)
    tk.Entry(Animation_frame,textvariable=loop).place(x=80,y=100,width=150,height=25)
    tk.Button(Animation_frame,text='浏览',command=lambda:browse_file(filepath)).place(x=230,y=10,width=60,height=25)
    tk.Label(Animation_frame,text='(X,Y)').place(x=230,y=40,width=60,height=25)
    tk.Label(Animation_frame,text='(整数)').place(x=230,y=70,width=60,height=25)
    tk.Label(Animation_frame,text='(0/1)').place(x=230,y=100,width=60,height=25)

    # BGM
    tk.Label(BGM_frame,text='音乐文件').place(x=10,y=10,width=70,height=25)
    tk.Label(BGM_frame,text='音乐音量').place(x=10,y=40,width=70,height=25)
    tk.Label(BGM_frame,text='音乐循环').place(x=10,y=70,width=70,height=25)
    tk.Entry(BGM_frame,textvariable=filepath).place(x=80,y=10,width=150,height=25)
    tk.Entry(BGM_frame,textvariable=volume).place(x=80,y=40,width=150,height=25)
    tk.Entry(BGM_frame,textvariable=loop).place(x=80,y=70,width=150,height=25)
    tk.Button(BGM_frame,text='浏览',command=lambda:browse_file(filepath)).place(x=230,y=10,width=60,height=25)
    tk.Label(BGM_frame,text='(0-100)').place(x=230,y=40,width=60,height=25)
    tk.Label(BGM_frame,text='(0/1)').place(x=230,y=70,width=60,height=25)

    # Audio_frame
    tk.Label(Audio_frame,text='音效文件').place(x=10,y=10,width=70,height=25)
    tk.Entry(Audio_frame,textvariable=filepath).place(x=80,y=10,width=150,height=25)
    tk.Button(Audio_frame,text='浏览',command=lambda:browse_file(filepath)).place(x=230,y=10,width=60,height=25)

    # 完成
    tk.Button(objdef,text='确认',command=comfirm_obj).place(x=130,y=320,height=30,width=60)

    Objdef_windows.mainloop()
    return obj_return_value
def Edit_windows(Edit_filepath='',fig_W=960,fig_H=540):

    global selected,selected_name,selected_type,selected_args # 选中值
    global image_canvas,show_canvas # 预览的画布
    global edit_return_value # 编辑器的最终返回值
    selected_name,selected_type,selected_args = 'None','None','None'
    selected = 0
    edit_return_value = False

    def new_obj(): # 新建
        Edit_windows.attributes('-disabled',True)
        new_obj = Media_def_window()
        Edit_windows.attributes('-disabled',False)
        if new_obj:
            mediainfo.insert('','end',values =new_obj)
    def preview_obj(): # 预览
        global image_canvas,show_canvas # 必须是全局变量，否则在函数后就被回收了，不再显示
        if selected_type in ['Text','Bubble','Background','Animation']: # 执行
            try:
                image_canvas.paste(blank_canvas,(0,0),mask=blank_canvas)
                exec('global {name};{name}={type}{args}'.format(name=selected_name,type=selected_type,args=selected_args))
                exec('global {name};{name}.preview()'.format(name=selected_name))
                #image_canvas.show()
                show_canvas = ImageTk.PhotoImage(image_canvas.resize((fig_W//2,fig_H//2)))
                preview_canvas.config(image =show_canvas)
            except ValueError as E:
                messagebox.showerror(title='错误',message=E)
            except NameError as E:
                messagebox.showwarning(title='警告',message=E)
        elif selected_type in ['BGM','Audio']:
            messagebox.showwarning(title='警告',message='音频类对象不支持预览！')
        elif selected_type == 'BuiltInAnimation':
            messagebox.showwarning(title='警告',message='内建动画对象不支持GUI编辑！')
        else:
            messagebox.showerror(title='错误',message='不支持的媒体定义类型 '+selected_type)
    def edit_obj(selected): # 编辑
        if selected == 0:
            pass
        else:
            Edit_windows.attributes('-disabled',True)
            new_obj = Media_def_window()
            Edit_windows.attributes('-disabled',False)
            if new_obj:
                mediainfo.item(selected,values=new_obj)
    def del_obj(selected): # 删除
        if selected == 0:
            pass
        else:
            mediainfo.delete(selected)
    def finish(saveas=False): # 完成
        global edit_return_value
        if (Edit_filepath != '')&(saveas==False):
            ofile = open(Edit_filepath,'w',encoding='utf8')
            edit_return_value = Edit_filepath
        else:
            outputformat = [('All Files', '*.*'), ('Text Document', '*.txt')] 
            Save_filepath = filedialog.asksaveasfilename(filetypes = outputformat, defaultextension = outputformat)
            if Save_filepath == '':
                return False
            ofile = open(Save_filepath,'w',encoding='utf8')
            edit_return_value = Save_filepath
        for lid in mediainfo.get_children(): # 输出表格内容
            #print(mediainfo.item(lid, "values"))
            ofile.write('{0} = {1}{2}\n'.format(*mediainfo.item(lid, "values")))
        ofile.close()
        Edit_windows.destroy()
        Edit_windows.quit()
    def close_window():
        edit_return_value = False
        Edit_windows.destroy()
        Edit_windows.quit()
    def treeviewClick(event):  # 选中列单击
        global selected,selected_name,selected_type,selected_args
        try:
            selected = mediainfo.selection()
            selected_name,selected_type,selected_args = mediainfo.item(selected, "values")
            #print(selected_name,selected_type,selected_args)
        except:
            pass

    window_W , window_H = fig_W//2+40,fig_H//2+440

    Edit_windows = tk.Toplevel()
    Edit_windows.resizable(0,0)
    Edit_windows.geometry("{W}x{H}".format(W=window_W,H=window_H))
    Edit_windows.iconbitmap('./doc/icon.ico')
    Edit_windows.config(background ='#e0e0e0')
    Edit_windows.title('TRPG Replay Generator MediaDef Editer.')
    Edit_windows.protocol('WM_DELETE_WINDOW',close_window)
    #Edit_windows.attributes('-topmost', True)

    frame_edit = tk.Frame(Edit_windows)
    frame_edit.place(x=10,y=10,height=window_H-20,width=window_W-20)

    # 信息框

    mediainfo_frame = tk.LabelFrame(frame_edit,text='媒体对象')
    mediainfo_frame.place(x=10,y=10,height=390,width=fig_W//2)

    ybar = tk.Scrollbar(mediainfo_frame,orient='vertical')
    xbar = tk.Scrollbar(mediainfo_frame,orient='horizontal')
    mediainfo = ttk.Treeview(mediainfo_frame,columns=['name','type','args'],show = "headings",selectmode = tk.BROWSE,yscrollcommand=ybar.set,xscrollcommand=xbar.set)
    ybar.config(command=mediainfo.yview)
    xbar.config(command=mediainfo.xview)
    ybar.place(x=fig_W//2-25,y=10,height=300,width=15)
    xbar.place(x=10,y=295,height=15,width=fig_W//2-35)
    mediainfo.column("name",anchor = "center",width=100)
    mediainfo.column("type",anchor = "center",width=100)
    mediainfo.column("args",anchor = "w",width=900)

    mediainfo.heading("name", text = "对象名称")
    mediainfo.heading("type", text = "类型")
    mediainfo.heading("args", text = "参数")

    mediainfo.place(x=10,y=10,height=285,width=fig_W//2-35)
    mediainfo.bind('<ButtonRelease-1>', treeviewClick)

    # 按键

    button_w = (fig_W//2-20)//8
    button_x = lambda x:10+(fig_W//2-20-button_w)//5*x

    tk.Button(mediainfo_frame,text='预览',command=preview_obj).place(x=button_x(0),y=320,width=button_w,height=40)
    tk.Button(mediainfo_frame,text='新建',command=new_obj).place(x=button_x(1),y=320,width=button_w,height=40)
    tk.Button(mediainfo_frame,text='重设',command=lambda:edit_obj(selected)).place(x=button_x(2),y=320,width=button_w,height=40)
    tk.Button(mediainfo_frame,text='删除',command=lambda:del_obj(selected)).place(x=button_x(3),y=320,width=button_w,height=40)
    tk.Button(mediainfo_frame,text='保存',command=lambda:finish(False)).place(x=button_x(4),y=320,width=button_w,height=40)
    tk.Button(mediainfo_frame,text='另存',command=lambda:finish(True)).place(x=button_x(5),y=320,width=button_w,height=40)

    # 预览图
    image_canvas = Image.open('./doc/canvas.png').crop((0,0,fig_W,fig_H))
    blank_canvas = image_canvas.copy()
    blank_canvas.putalpha(220)
    show_canvas = ImageTk.PhotoImage(image_canvas.resize((fig_W//2,fig_H//2)))
    preview_canvas = tk.Label(frame_edit,bg='black')
    preview_canvas.config(image=show_canvas)
    preview_canvas.place(x=10,y=410,height=fig_H//2,width=fig_W//2)

    # 载入文件
    if Edit_filepath!='': # 如果有指定输入文件
        mediadef_text = open(Edit_filepath,'r',encoding='utf8').read().split('\n')
        warning_line = []
        for i,line in enumerate(mediadef_text):
            parseline = re.findall('(\w+)[=\ ]+(Text|Bubble|Animation|Background|BGM|Audio)(\(.+\))',line)
            if len(parseline) == 1:
                mediainfo.insert('','end',values =parseline[0])
            else:
                warning_line.append(i+1)
        if warning_line == []:
            messagebox.showinfo(title='完毕',message='载入完毕，共载入{i}条记录！'.format(i=i+1))
        else:
            messagebox.showwarning(title='完毕',message='载入完毕，共载入{i}条记录，\n第{warning}行因为无法解析而被舍弃！'.format(i=i+1-len(warning_line),warning=','.join(map(str,warning_line))))

    Edit_windows.mainloop()
    return edit_return_value

# 通用函数
def browse_file(text_obj,method='file',changebotton=False):
    if method == 'file':
        getname = filedialog.askopenfilename()
    else:
        getname = filedialog.askdirectory()
    text_obj.set(getname)
    if changebotton != False:
        if os.path.isfile(getname):
            changebotton.config(text='编辑')
        else:
            changebotton.config(text='新建')
def choose_color(text_obj):
    get_color = colorchooser.askcolor()
    R,G,B = get_color[0]
    A = 255
    text_obj.set('({0},{1},{2},{3})'.format(int(R),int(G),int(B),int(A)))

# 主界面的函数

# main:
def Main_windows():
    global frame_display
    def printFrame():
        global frame_display
        frame_display.place_forget()
        select = tab_frame[tab.get()]
        select.place(x=10,y=50)
        #frame_item(select)
        frame_display = select
    def call_Edit_windows():
        Edit_filepath=media_define.get()
        fig_W = project_W.get()
        fig_H = project_H.get()
        Main_windows.attributes('-disabled',True)
        return_from_Edit = Edit_windows(Edit_filepath,fig_W,fig_H)
        Main_windows.attributes('-disabled',False)
        if os.path.isfile(return_from_Edit):
            media_define.set(return_from_Edit)
    def run_command():
        optional = {1:'--OutputPath {of} ',2:'--ExportXML ',3:'--ExportVideo ',4:'--SynthesisAnyway --AccessKey {AK} --AccessKeySecret {AS} --Appkey {AP} ',5:'--FixScreenZoom '}
        command = python3 + ' ./replay_generator.py --LogFile {lg} --MediaObjDefine {md} --CharacterTable {ct} '
        command = command + '--FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd} '
        if output_path.get()!='':
            command = command + optional[1].format(of=output_path.get().replace('\\','/'))
        if synthanyway.get()==1:
            command = command + optional[4].format(AK=AccessKey.get(),AS=AccessKeySecret.get(),AP=Appkey.get())
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
                                     ct=characor_table.get().replace('\\','/'),fps=project_F.get(),
                                     wd=project_W.get(),he=project_H.get(),zd=project_Z.get())
            try:
                print('[32m'+command+'[0m')
                os.system(command)
            except:
                messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了！')
    def run_command_synth():
        command = python3 +' ./speech_synthesizer.py --LogFile {lg} --MediaObjDefine {md} --CharacterTable {ct} --OutputPath {of} --AccessKey {AK} --AccessKeySecret {AS} --Appkey {AP}'
        if '' in [stdin_logfile.get(),characor_table.get(),media_define.get(),output_path.get(),AccessKey.get(),AccessKeySecret.get(),Appkey.get()]:
            messagebox.showerror(title='错误',message='缺少必要的参数！')
        else:
            command = command.format(lg = stdin_logfile.get().replace('\\','/'),md = media_define.get().replace('\\','/'),
                                     of = output_path.get().replace('\\','/'), ct = characor_table.get().replace('\\','/'),
                                     AK = AccessKey.get(), AS= AccessKeySecret.get(),AP=Appkey.get())
            try:
                print('[32m'+command+'[0m')
                os.system(command)
                messagebox.showinfo(title='完毕',message='语音合成程序执行完毕，检视控制台输出获取详细信息！')
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
                                     fps = project_F.get(), wd = project_W.get(),
                                     he = project_H.get(), zd = project_Z.get())
            try:
                print('[32m'+command+'[0m')
                os.system(command)
                messagebox.showinfo(title='完毕',message='导出XML程序执行完毕，检视控制台输出获取详细信息！')
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
                                     fps = project_F.get(), wd = project_W.get(),
                                     he = project_H.get(), zd = project_Z.get())
            try:
                print('[32m'+command+'[0m')
                os.system(command)
                messagebox.showinfo(title='完毕',message='导出视频程序执行完毕，检视控制台输出获取详细信息！')
            except:
                messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了！')

    # 初始化
    Main_windows = tk.Tk()
    Main_windows.resizable(0,0)
    Main_windows.geometry("640x550")
    Main_windows.iconbitmap('./doc/icon.ico')
    Main_windows.config(background ='#e0e0e0')
    Main_windows.title('TRPG Replay Generator ' + edtion)

    # 大号字体
    try:
        big_text = font.Font(font="微软雅黑",size=25)
    except:
        big_text = font.Font(size=25)

    # 选中的sheet
    tab = tk.IntVar(Main_windows)
    # 几个文件的路径
    stdin_logfile = tk.StringVar(Main_windows)
    characor_table = tk.StringVar(Main_windows)
    media_define = tk.StringVar(Main_windows)
    output_path = tk.StringVar(Main_windows)
    timeline_file = tk.StringVar(Main_windows)
    #text_obj = {1:media_define,2:characor_table,3:stdin_logfile,4:output_path,5:timeline_file}
    # 可选参数们
    project_W = tk.IntVar(Main_windows)
    project_H = tk.IntVar(Main_windows)
    project_F = tk.IntVar(Main_windows)
    project_Z = tk.StringVar(Main_windows)
    project_W.set(1920)
    project_H.set(1080)
    project_F.set(30)
    project_Z.set('BG3,BG2,BG1,Am3,Am2,Am1,Bb')
    # 语音合成的key
    AccessKey = tk.StringVar(Main_windows)
    Appkey = tk.StringVar(Main_windows)
    AccessKeySecret = tk.StringVar(Main_windows)
    AccessKey.set('Your_AccessKey')
    AccessKeySecret.set('Your_AccessKey_Secret')
    Appkey.set('Your_Appkey')
    # flag们
    synthanyway = tk.IntVar(Main_windows)
    exportprxml = tk.IntVar(Main_windows)
    exportmp4 = tk.IntVar(Main_windows)
    fixscrzoom = tk.IntVar(Main_windows)
    # 获取python解释器的路径
    #python3 = sys.executable.replace('\\','/')
    python3 = 'python' # exe发布版

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
    new_or_edit = tk.Button(filepath, command=call_Edit_windows,text="新建")
    new_or_edit.place(x=555,y=5,width=35,height=30)
    tk.Button(filepath, command=lambda:browse_file(media_define,changebotton=new_or_edit),text="浏览").place(x=520,y=5,width=35,height=30)
    tk.Button(filepath, command=lambda:browse_file(characor_table),text="浏览").place(x=520,y=50,width=70,height=30)
    tk.Button(filepath, command=lambda:browse_file(stdin_logfile),text="浏览").place(x=520,y=95,width=70,height=30)
    tk.Button(filepath, command=lambda:browse_file(output_path,'path'),text="浏览").place(x=520,y=140,width=70,height=30)


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
    tk.Button(filepath_s, command=lambda:browse_file(media_define),text="浏览").place(x=520,y=5,width=70,height=30)
    tk.Button(filepath_s, command=lambda:browse_file(characor_table),text="浏览").place(x=520,y=50,width=70,height=30)
    tk.Button(filepath_s, command=lambda:browse_file(stdin_logfile),text="浏览").place(x=520,y=95,width=70,height=30)
    tk.Button(filepath_s, command=lambda:browse_file(output_path,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

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
    tk.Button(filepath_x, command=lambda:browse_file(media_define),text="浏览").place(x=520,y=5,width=70,height=30)
    tk.Button(filepath_x, command=lambda:browse_file(characor_table),text="浏览",state=tk.DISABLED).place(x=520,y=50,width=70,height=30)
    tk.Button(filepath_x, command=lambda:browse_file(timeline_file),text="浏览").place(x=520,y=95,width=70,height=30)
    tk.Button(filepath_x, command=lambda:browse_file(output_path,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

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
    #Eta_logo = ImageTk.PhotoImage(Image.open('./doc/eta.png'))
    tk.Label(flag_x,image = PR_logo).place(x=20,y=10)
    #tk.Label(flag_x,text='通向Premiere Pro世界的通道，感谢伊塔的Idea，了解更多：').place(x=110,y=30)
    tk.Label(flag_x,text='通向Premiere Pro世界的通道').place(x=110,y=30)
    #tk.Button(flag_x,image = Eta_logo,command=lambda: webbrowser.open('https://space.bilibili.com/10414609'),relief='flat').place(x=500,y=7)

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
    tk.Button(filepath_v, command=lambda:browse_file(media_define),text="浏览").place(x=520,y=5,width=70,height=30)
    tk.Button(filepath_v, command=lambda:browse_file(characor_table),text="浏览",state=tk.DISABLED).place(x=520,y=50,width=70,height=30)
    tk.Button(filepath_v, command=lambda:browse_file(timeline_file),text="浏览").place(x=520,y=95,width=70,height=30)
    tk.Button(filepath_v, command=lambda:browse_file(output_path,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

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

if __name__=='__main__':
    Main_windows()