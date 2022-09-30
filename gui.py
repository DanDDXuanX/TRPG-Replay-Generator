#!/usr/bin/env python
# coding: utf-8
edtion = 'alpha 1.12.7'

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
from Medias import Audio
from Medias import BGM

# preview 的类定义
label_pos_show_text = ImageFont.truetype('./media/SourceHanSerifSC-Heavy.otf', 30)
RE_mediadef_args = re.compile('(fontfile|fontsize|color|line_limit|filepath|Main_Text|Header_Text|pos|mt_pos|ht_pos|align|line_distance|tick|loop|volume|edge_color|label_color)?\ {0,4}=?\ {0,4}(Text\(\)|[^,()]+|\([-\d,\ ]+\))')
RE_parse_mediadef = re.compile('(\w+)[=\ ]+(Text|StrokeText|Bubble|Animation|Background|BGM|Audio)(\(.+\))')
RE_vaildname = re.compile('^\w+$')
occupied_variable_name = open('./media/occupied_variable_name.list','r',encoding='utf8').read().split('\n') # 已经被系统占用的变量名

# global image_canvas
class Text:
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20,label_color='Lavender'):
        self.text_render = ImageFont.truetype(fontfile, fontsize)
        self.color=color
        self.size=fontsize
        self.line_limit = line_limit
    def draw(self,lenth=-1):
        if lenth ==-1:
            lenth = self.line_limit
        test_canvas = Image.new(mode='RGBA',size=(self.size*int(self.line_limit*1.5),self.size*2),color=(0,0,0,0))#高度贪婪2x,宽度贪婪1.5x
        test_draw = ImageDraw.Draw(test_canvas)
        test_draw.text((0,0), ('测试文本'*50)[0:lenth], font = self.text_render,fill = self.color)
        p1,p2,p3,p4 = test_canvas.getbbox()
        return test_canvas.crop((0,0,p3,p4))
    def preview(self,prevpos='None'):
        can_W,can_H = image_canvas.size
        draw_text = self.draw()
        txt_w,txt_h = draw_text.size
        if prevpos=='None':
            image_canvas.paste(draw_text,((can_W-txt_w)//2,(can_H-txt_h)//2),mask=draw_text.split()[-1])
        else:
            image_canvas.paste(draw_text,prevpos,mask=draw_text.split()[-1])
class StrokeText(Text):
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20,edge_color=(255,255,255,255),label_color='Lavender'):
        super().__init__(fontfile=fontfile,fontsize=fontsize,color=color,line_limit=line_limit,label_color=label_color)
        self.edge_color=edge_color
    def draw(self,lenth=-1):
        if lenth ==-1:
            lenth = self.line_limit
        test_canvas = Image.new(mode='RGBA',size=(self.size*int(self.line_limit*1.5),self.size*2),color=(0,0,0,0))#高度贪婪2x,宽度贪婪1.5x
        test_draw = ImageDraw.Draw(test_canvas)
        for pos in [(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)]:
            test_draw.text(pos, ('测试文本'*50)[0:lenth], font = self.text_render,fill = self.edge_color)
        test_draw.text((1,1), ('测试文本'*50)[0:lenth], font = self.text_render,fill = self.color)
        p1,p2,p3,p4 = test_canvas.getbbox()
        return test_canvas.crop((0,0,p3,p4))
class Bubble:
    def __init__(self,filepath=None,Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),ht_pos=(0,0),align='left',line_distance=1.5,label_color='Lavender'):
        if filepath is None: # 支持气泡图缺省
            self.media  = Image.new(mode='RGBA',size=(1920,1080),color=(0,0,0,0))
        else:
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
        draw = ImageDraw.Draw(image_canvas)
        p_x,p_y = self.pos
        h_x,h_y = pos_add(self.ht_pos,self.pos)
        m_x,m_y = pos_add(self.mt_pos,self.pos)
        if self.media.mode == 'RGBA':
            image_canvas.paste(self.media,self.pos,mask=self.media.split()[-1])
        else:
            image_canvas.paste(self.media,self.pos)
        draw.line([p_x-100,p_y,p_x+100,p_y],fill='green',width=2)
        draw.line([p_x,p_y-100,p_x,p_y+100],fill='green',width=2)
        draw.text((p_x,p_y),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='green')
        if self.Header != None:
            draw_text = self.Header.draw()
            image_canvas.paste(draw_text,pos_add(self.ht_pos,self.pos),draw_text.split()[-1])
            draw.line([h_x-100,h_y,h_x+100,h_y],fill='blue',width=2)
            draw.line([h_x,h_y-50,h_x,h_y+50],fill='blue',width=2)
            draw.text((h_x,h_y-35),'({0},{1})'.format(h_x-p_x,h_y-p_y),font=label_pos_show_text,fill='blue')
        if self.MainText != None:
            tx_w = self.MainText.size*self.MainText.line_limit
            tx_h = self.line_distance*self.MainText.size
            mx,my = self.mt_pos
            for i,l in enumerate(range(self.MainText.line_limit,0,-self.MainText.line_limit//4)):
                draw_text = self.MainText.draw(l)
                image_canvas.paste(draw_text,pos_add(self.pos,(int(mx+(tx_w-draw_text.size[0])//2*(self.align=='center')),int(my+i*tx_h))),draw_text.split()[-1])
            draw.line([m_x-100,m_y,m_x+100,m_y],fill='blue',width=2)
            draw.line([m_x,m_y-50,m_x,m_y+50],fill='blue',width=2)
            draw.text((m_x,m_y-35),'({0},{1})'.format(m_x-p_x,m_y-p_y),font=label_pos_show_text,fill='blue')
class Background:
    cmap = {'black':(0,0,0,255),'white':(255,255,255,255),'greenscreen':(0,177,64,255)}
    def __init__(self,filepath,pos = (0,0),label_color='Lavender'):
        if filepath in Background.cmap.keys(): #添加了，对纯色定义的背景的支持
            self.media = Image.new(mode='RGBA',size=(1920,1080),color=Background.cmap[filepath]) # GUI里面没有全局的screen_size，用1080p的参数替代
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
    def __init__(self,filepath,pos = (0,0),tick=1,loop=True,label_color='Lavender'):
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




# 选择位置窗
def open_PosSelect(father,bgfigure='',postype='green',current_pos=''):
    def close_window(): # 取消 关闭窗口
        nonlocal posselect_return
        posselect_return = current_pos
        PosSelect_window.destroy()
        PosSelect_window.quit()
    def comfirm_pos(): # 确认
        nonlocal posselect_return
        posselect_return = '({0},{1})'.format(p_x,p_y)
        PosSelect_window.destroy()
        PosSelect_window.quit()
    def get_click(event=None): # 鼠标点击、方向键
        nonlocal select_canvas,select_canvas_show,cursor_figure,p_x,p_y
        direction_key = {'Up':(0,-1),'Down':(0,1),'Left':(-1,0),'Right':(1,0)}
        # 处理事件
        if event is None:
            pass
        elif event.type=='2': # tk.EventType.KeyPress
            try: # 获取键盘方向键
                p_x = p_x+direction_key[event.keysym][0]
                p_y = p_y+direction_key[event.keysym][1]
            except KeyError as E:
                pass # 则不变
        elif event.type=='4': # tk.EventType.ButtonPress
            try: # 获取鼠标点击位置
                p_x,p_y = 2*event.x,2*event.y
            except Exception:
                pass # 则不变
        else:
            pass
        # 初始化图像
        select_draw = ImageDraw.Draw(select_canvas)
        select_canvas.paste(select_blank,(0,0))
        # 画十字选择点
        if postype=='green':
            select_canvas.paste(cursor_figure,(p_x,p_y),mask=cursor_figure) # cursor_figure
            select_draw.line([p_x-100,p_y,p_x+100,p_y],fill='green',width=2)
            select_draw.line([p_x,p_y-100,p_x,p_y+100],fill='green',width=2)
            select_draw.text((p_x,p_y),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='green')
        elif postype=='blue':
            select_draw.line([p_x-100,p_y,p_x+100,p_y],fill='blue',width=2)
            select_draw.line([p_x,p_y-50,p_x,p_y+50],fill='blue',width=2)
            select_draw.text((p_x,p_y-35),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='blue')
        # 更新到图片上
        select_canvas_show = ImageTk.PhotoImage(select_canvas.resize((can_W,can_H)))
        sele_preview.config(image=select_canvas_show)
    # 载入底图
    if postype=='green': # pos
        fig_W,fig_H = image_canvas.size
        select_canvas = Image.open('./media/canvas.png').crop((0,0,fig_W,fig_H))
        try: # 附图
            cursor_figure = Image.open(bgfigure)
            if cursor_figure.mode != 'RGBA': # 如果没有alpha通道
                cursor_figure.putalpha(255)
        except Exception:
            cursor_figure = Image.new(mode='RGBA',size=(1,1),color=(0,0,0,0))
    elif postype=='blue': # mtpos htpos
        try:
            select_canvas = Image.open(bgfigure)
        except Exception as E:
            messagebox.showwarning(title='无法载入气泡底图！',message=E)
            fig_W,fig_H = image_canvas.size
            select_canvas = Image.open('./media/canvas.png').crop((0,0,fig_W,fig_H))
        cursor_figure = Image.new(mode='RGBA',size=(1,1),color=(0,0,0,0))
    else:
        return False

    posselect_return = '' # 返回值
    can_W,can_H = select_canvas.size[0]//2,select_canvas.size[1]//2
    select_canvas_show = ImageTk.PhotoImage(select_canvas.resize((can_W,can_H)))
    select_blank = select_canvas.copy()

    PosSelect_window = tk.Toplevel(father)
    PosSelect_window.resizable(0,0)
    PosSelect_window.config(background ='#e0e0e0')
    #Objdef_windows.attributes('-topmost', True)
    PosSelect_window.title('选择位置')
    PosSelect_window.protocol('WM_DELETE_WINDOW',close_window)
    PosSelect_window.transient(father)
    PosSelect_window.geometry("{0}x{1}".format(can_W+40,can_H+90))
    PosSelect_window.bind("<Key>",get_click) # 获取键盘事件
    try:
        PosSelect_window.iconbitmap('./media/icon.ico')
    except tk.TclError:
        pass

    sele_frame = tk.Frame(PosSelect_window)
    sele_frame.place(x=10,y=10,height=can_H+20,width=can_W+20)
    sele_preview = tk.Label(sele_frame,bg='#f0f0f0')
    sele_preview.config(image=select_canvas_show)
    sele_preview.place(x=10,y=10,height=can_H,width=can_W)
    sele_preview.bind("<Button-1>",get_click) # 获取鼠标点击事件
    
    ttk.Button(PosSelect_window,text='确定',command=comfirm_pos).place(x=can_W//2-20,y=can_H+40,width=80,height=40)
    # 初始位置
    try:
        p_x,p_y = re.findall('\(([\ \d]+),([\ \d]+)\)',current_pos)[0]
        p_x,p_y= int(p_x),int(p_y)
    except Exception:
        p_x,p_y= 0,0
    get_click()
    sele_preview.mainloop()
    return posselect_return
# 媒体定义窗
def open_Media_def_window(father,i_name='',i_type='',i_args=''):
    obj_return_value = False
    def show_selected_options(event):
        nonlocal type_display
        type_display.place_forget()
        try:
            select = Mediatype[o_type.get()]
        except KeyError:
            select = Empty_frame
        select.place(x=10,y=40,width=300,height=275)
        type_display = select
    def comfirm_obj():
        nonlocal obj_return_value
        if '' in [o_name.get(),o_type.get()]:
            # 如果名字和类型有缺省
            messagebox.showerror(title='错误',message='缺少必要的参数！')
        elif (o_name.get()!=i_name)&((o_name.get() in occupied_variable_name)|(o_name.get() in used_variable_name)):
            # 如果名字发生了改变，且新名字在已经占用（用户或系统）的名字里面
            messagebox.showerror(title='错误',message='已被占用的变量名！') #############改这里！
        elif (len(re.findall('^\w+$',o_name.get()))==0) | (o_name.get()[0].isdigit()): # 全字符是\w，且首字符不是数字
            # 如果新名字是非法的变量名
            messagebox.showerror(title='错误',message='非法的变量名！') 
        else:
            get_args = {
                'fontfile':fontfile.get(),'fontsize':fontsize.get(),'color':color.get(),'line_limit':line_limit.get(),
                'filepath':filepath.get(),'Main_Text':Main_Text.get(),'Header_Text':Header_Text.get(),
                'pos':pos.get(),'mt_pos':mt_pos.get(),'ht_pos':ht_pos.get(),'align':align.get(),
                'line_distance':line_distance.get(),'tick':tick.get(),'loop':loop.get(),
                'volume':volume.get(),'edge_color':edge_color.get(),'label_color':label_color.get()
            }
            this_tplt = arg_tplt[o_type.get()]
            
            obj_return_value = (o_name.get(),o_type.get(),this_tplt.format(**get_args))
            Objdef_windows.destroy()
            Objdef_windows.quit()
    def close_window():
        nonlocal obj_return_value
        obj_return_value = False
        Objdef_windows.destroy()
        Objdef_windows.quit()
    def call_possele(target): # target是一个stringVar，pos的
        if target in [mt_pos,ht_pos]:
            get = open_PosSelect(father=Objdef_windows,bgfigure=filepath.get(),postype='blue',current_pos=target.get())
        elif target is pos:
            get = open_PosSelect(father=Objdef_windows,bgfigure=filepath.get(),postype='green',current_pos=target.get())
        target.set(get) # 设置为的得到的返回值

    Objdef_windows = tk.Toplevel(father)
    Objdef_windows.resizable(0,0)
    Objdef_windows.geometry("340x415")
    Objdef_windows.config(background ='#e0e0e0')
    Objdef_windows.title('媒体参数')
    Objdef_windows.protocol('WM_DELETE_WINDOW',close_window)
    Objdef_windows.transient(father)
    try:
        Objdef_windows.iconbitmap('./media/icon.ico')
    except tk.TclError:
        pass

    # 主框
    objdef = tk.Frame(Objdef_windows)
    objdef.place(x=10,y=10,height=395,width=320)

    o_name = tk.StringVar(Objdef_windows)
    o_type = tk.StringVar(Objdef_windows)

    o_name.set(i_name) # 默认是''
    o_type.set(i_type) # 默认是''

    arg_tplt = {
        'Text':"(fontfile='{fontfile}',fontsize={fontsize},color={color},line_limit={line_limit},label_color='{label_color}')",
        'StrokeText':"(fontfile='{fontfile}',fontsize={fontsize},color={color},line_limit={line_limit},edge_color={edge_color},label_color='{label_color}')",
        'Bubble':"(filepath='{filepath}',Main_Text={Main_Text},Header_Text={Header_Text},pos={pos},mt_pos={mt_pos},ht_pos={ht_pos},align='{align}',line_distance={line_distance},label_color='{label_color}')",
        'Background':"(filepath='{filepath}',pos={pos},label_color='{label_color}')",
        'Animation':"(filepath='{filepath}',pos={pos},tick={tick},loop={loop},label_color='{label_color}')",
        'Audio':"(filepath='{filepath}',label_color='{label_color}')",
        'BGM':"(filepath='{filepath}',volume={volume},loop={loop},label_color='{label_color}')"
    }

    # 名称
    tk.Label(objdef,text='名称：').place(x=10,y=10,width=40,height=25)
    ttk.Entry(objdef,textvariable=o_name).place(x=50,y=10,width=100,height=25)

    # 类型
    tk.Label(objdef,text='类型：').place(x=160,y=10,width=40,height=25)
    choose_type = ttk.Combobox(objdef,textvariable=o_type,value=['Text','StrokeText','Bubble','Background','Animation','BGM','Audio'])
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
    StrokeText_frame = tk.LabelFrame(objdef,text='StrokeText参数')
    Mediatype = {'Text':Text_frame,'StrokeText':StrokeText_frame,'Bubble':Bubble_frame,'Background':Background_frame,'Animation':Animation_frame,'BGM':BGM_frame,'Audio':Audio_frame}

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
    edge_color = tk.StringVar(Objdef_windows)
    label_color = tk.StringVar(Objdef_windows)
    # 默认参数
    fontfile.set('./media/SourceHanSansCN-Regular.otf')
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
    edge_color.set('(255,255,255,255)')
    label_color.set('Lavender')
    # 可用标签颜色
    available_label_color = {'Violet':'#a690e0','Iris':'#729acc','Caribbean':'#29d698','Lavender':'#e384e3',
                             'Cerulean':'#2fbfde','Forest':'#51b858','Rose':'#f76fa4','Mango':'#eda63b',
                             'Purple':'#970097','Blue':'#3c3cff','Teal':'#008080','Magenta':'#e732e7',
                             'Tan':'#cec195','Green':'#1d7021','Brown':'#8b4513','Yellow':'#e2e264'}
    # 外部输入参数
    type_keyword_position = {'Text':['fontfile','fontsize','color','line_limit','label_color'],
                             'StrokeText':['fontfile','fontsize','color','line_limit','edge_color','label_color'],
                             'Bubble':['filepath','Main_Text','Header_Text','pos','mt_pos','ht_pos','align','line_distance','label_color'],
                             'Background':['filepath','pos','label_color'],
                             'Animation':['filepath','pos','tick','loop','label_color'],
                             'Audio':['filepath','label_color'],
                             'BGM':['filepath','volume','loop','label_color']}

    #初始状态 空白或者选中
    if i_type == '':
        Empty_frame.place(x=10,y=40,width=300,height=275)
        type_display = Empty_frame
    else:
        Mediatype[i_type].place(x=10,y=40,width=300,height=275)
        type_display = Mediatype[i_type]
        for i,arg in enumerate(RE_mediadef_args.findall(i_args)):
            keyword,value = arg
            if keyword == '':
                keyword = type_keyword_position[i_type][i]
            if (('"' == value[0]) & ('"' == value[-1]))|(("'" == value[0]) & ("'" == value[-1])): # 如果是双引号括起来的路径
                exec('{0}.set({1})'.format(keyword,value))
            else:
                exec('{0}.set("{1}")'.format(keyword,value))

    # Text_frame:
    ttk.Label(Text_frame,text='字体文件').place(x=10,y=10,width=65,height=25)
    ttk.Label(Text_frame,text='字体大小').place(x=10,y=40,width=65,height=25)
    ttk.Label(Text_frame,text='字体颜色').place(x=10,y=70,width=65,height=25)
    ttk.Label(Text_frame,text='单行字数').place(x=10,y=100,width=65,height=25)
    ttk.Entry(Text_frame,textvariable=fontfile).place(x=75,y=10,width=160,height=25)
    ttk.Entry(Text_frame,textvariable=fontsize).place(x=75,y=40,width=160,height=25)
    ttk.Entry(Text_frame,textvariable=color).place(x=75,y=70,width=160,height=25)
    ttk.Entry(Text_frame,textvariable=line_limit).place(x=75,y=100,width=160,height=25)
    ttk.Button(Text_frame,text='浏览',command=lambda:browse_file(fontfile)).place(x=240,y=10,width=50,height=25)
    ttk.Label(Text_frame,text='(整数)',anchor='center').place(x=240,y=40,width=50,height=25)
    ttk.Button(Text_frame,text='选择',command=lambda:choose_color(color)).place(x=240,y=70,width=50,height=25)
    ttk.Label(Text_frame,text='(整数)',anchor='center').place(x=240,y=100,width=50,height=25)

    # StrokeText_frame
    ttk.Label(StrokeText_frame,text='字体文件').place(x=10,y=10,width=65,height=25)
    ttk.Label(StrokeText_frame,text='字体大小').place(x=10,y=40,width=65,height=25)
    ttk.Label(StrokeText_frame,text='字体颜色').place(x=10,y=70,width=65,height=25)
    ttk.Label(StrokeText_frame,text='单行字数').place(x=10,y=100,width=65,height=25)
    ttk.Label(StrokeText_frame,text='描边颜色').place(x=10,y=130,width=65,height=25)
    ttk.Entry(StrokeText_frame,textvariable=fontfile).place(x=75,y=10,width=160,height=25)
    ttk.Entry(StrokeText_frame,textvariable=fontsize).place(x=75,y=40,width=160,height=25)
    ttk.Entry(StrokeText_frame,textvariable=color).place(x=75,y=70,width=160,height=25)
    ttk.Entry(StrokeText_frame,textvariable=line_limit).place(x=75,y=100,width=160,height=25)
    ttk.Entry(StrokeText_frame,textvariable=edge_color).place(x=75,y=130,width=160,height=25)
    ttk.Button(StrokeText_frame,text='浏览',command=lambda:browse_file(fontfile)).place(x=240,y=10,width=50,height=25)
    ttk.Label(StrokeText_frame,text='(整数)',anchor='center').place(x=240,y=40,width=50,height=25)
    ttk.Button(StrokeText_frame,text='选择',command=lambda:choose_color(color)).place(x=240,y=70,width=50,height=25)
    ttk.Label(StrokeText_frame,text='(整数)',anchor='center').place(x=240,y=100,width=50,height=25)
    ttk.Button(StrokeText_frame,text='选择',command=lambda:choose_color(edge_color)).place(x=240,y=130,width=50,height=25)

    # Bubble_frame
    ttk.Label(Bubble_frame,text='底图文件').place(x=10,y=10,width=65,height=25)
    ttk.Label(Bubble_frame,text='主文本字体').place(x=10,y=40,width=65,height=25)
    ttk.Label(Bubble_frame,text='头文本字体').place(x=10,y=70,width=65,height=25)
    ttk.Label(Bubble_frame,text='底图位置').place(x=10,y=100,width=65,height=25)
    ttk.Label(Bubble_frame,text='主文本位置').place(x=10,y=130,width=65,height=25)
    ttk.Label(Bubble_frame,text='头文本位置').place(x=10,y=160,width=65,height=25)
    ttk.Label(Bubble_frame,text='对齐模式').place(x=10,y=190,width=65,height=25)
    ttk.Label(Bubble_frame,text='主文本行距').place(x=10,y=220,width=65,height=25)
    ttk.Entry(Bubble_frame,textvariable=filepath).place(x=75,y=10,width=160,height=25)
    ttk.Combobox(Bubble_frame,textvariable=Main_Text,value=available_Text).place(x=75,y=40,width=160,height=25)
    ttk.Combobox(Bubble_frame,textvariable=Header_Text,value=available_Text).place(x=75,y=70,width=160,height=25)
    ttk.Entry(Bubble_frame,textvariable=pos).place(x=75,y=100,width=160,height=25)
    ttk.Entry(Bubble_frame,textvariable=mt_pos).place(x=75,y=130,width=160,height=25)
    ttk.Entry(Bubble_frame,textvariable=ht_pos).place(x=75,y=160,width=160,height=25)
    ttk.Combobox(Bubble_frame,textvariable=align,value=['left','center']).place(x=75,y=190,width=160,height=25)
    ttk.Entry(Bubble_frame,textvariable=line_distance).place(x=75,y=220,width=160,height=25)
    ttk.Button(Bubble_frame,text='浏览',command=lambda:browse_file(filepath)).place(x=240,y=10,width=50,height=25)
    ttk.Label(Bubble_frame,text='(选择)',anchor='center').place(x=240,y=40,width=50,height=25)
    ttk.Label(Bubble_frame,text='(选择)',anchor='center').place(x=240,y=70,width=50,height=25)
    ttk.Button(Bubble_frame,text='选择',command=lambda:call_possele(pos)).place(x=240,y=100,width=50,height=25)
    ttk.Button(Bubble_frame,text='选择',command=lambda:call_possele(mt_pos)).place(x=240,y=130,width=50,height=25)
    ttk.Button(Bubble_frame,text='选择',command=lambda:call_possele(ht_pos)).place(x=240,y=160,width=50,height=25)
    ttk.Label(Bubble_frame,text='(选择)',anchor='center').place(x=240,y=190,width=50,height=25)
    ttk.Label(Bubble_frame,text='(小数)',anchor='center').place(x=240,y=220,width=50,height=25)

    # Background
    ttk.Label(Background_frame,text='背景文件').place(x=10,y=10,width=65,height=25)
    ttk.Label(Background_frame,text='背景位置').place(x=10,y=40,width=65,height=25)
    ttk.Entry(Background_frame,textvariable=filepath).place(x=75,y=10,width=160,height=25)
    ttk.Entry(Background_frame,textvariable=pos).place(x=75,y=40,width=160,height=25)
    ttk.Button(Background_frame,text='浏览',command=lambda:browse_file(filepath)).place(x=240,y=10,width=50,height=25)
    ttk.Button(Background_frame,text='选择',command=lambda:call_possele(pos)).place(x=240,y=40,width=50,height=25)

    # Animation
    ttk.Label(Animation_frame,text='立绘文件').place(x=10,y=10,width=65,height=25)
    ttk.Label(Animation_frame,text='立绘位置').place(x=10,y=40,width=65,height=25)
    ttk.Label(Animation_frame,text='动画时刻').place(x=10,y=70,width=65,height=25)
    ttk.Label(Animation_frame,text='动画循环').place(x=10,y=100,width=65,height=25)
    ttk.Entry(Animation_frame,textvariable=filepath).place(x=75,y=10,width=160,height=25)
    ttk.Entry(Animation_frame,textvariable=pos).place(x=75,y=40,width=160,height=25)
    ttk.Entry(Animation_frame,textvariable=tick).place(x=75,y=70,width=160,height=25)
    ttk.Entry(Animation_frame,textvariable=loop).place(x=75,y=100,width=160,height=25)
    ttk.Button(Animation_frame,text='浏览',command=lambda:browse_file(filepath)).place(x=240,y=10,width=50,height=25)
    ttk.Button(Animation_frame,text='选择',command=lambda:call_possele(pos)).place(x=240,y=40,width=50,height=25)
    ttk.Label(Animation_frame,text='(整数)',anchor='center').place(x=240,y=70,width=50,height=25)
    ttk.Label(Animation_frame,text='(0/1)',anchor='center').place(x=240,y=100,width=50,height=25)

    # BGM
    ttk.Label(BGM_frame,text='音乐文件').place(x=10,y=10,width=65,height=25)
    ttk.Label(BGM_frame,text='音乐音量').place(x=10,y=40,width=65,height=25)
    ttk.Label(BGM_frame,text='音乐循环').place(x=10,y=70,width=65,height=25)
    ttk.Entry(BGM_frame,textvariable=filepath).place(x=75,y=10,width=160,height=25)
    ttk.Entry(BGM_frame,textvariable=volume).place(x=75,y=40,width=160,height=25)
    ttk.Entry(BGM_frame,textvariable=loop).place(x=75,y=70,width=160,height=25)
    ttk.Button(BGM_frame,text='浏览',command=lambda:browse_file(filepath)).place(x=240,y=10,width=50,height=25)
    ttk.Label(BGM_frame,text='(0-100)',anchor='center').place(x=240,y=40,width=50,height=25)
    ttk.Label(BGM_frame,text='(0/1)',anchor='center').place(x=240,y=70,width=50,height=25)

    # Audio_frame
    ttk.Label(Audio_frame,text='音效文件').place(x=10,y=10,width=65,height=25)
    ttk.Entry(Audio_frame,textvariable=filepath).place(x=75,y=10,width=160,height=25)
    ttk.Button(Audio_frame,text='浏览',command=lambda:browse_file(filepath)).place(x=240,y=10,width=50,height=25)

    # 标签颜色 colabel
    label_label_color = tk.Label(objdef,text='▉标签颜色',fg=available_label_color[label_color.get()],bg='#262626')
    label_label_color.place(x=22,y=320,width=62,height=25)
    choose_labelcolor = ttk.Combobox(objdef,textvariable=label_color,value=list(available_label_color.keys()))
    choose_labelcolor.place(x=87,y=320,width=160,height=25)
    choose_labelcolor.bind("<<ComboboxSelected>>",lambda event: label_label_color.config(fg=available_label_color[label_color.get()]))
    ttk.Label(objdef,text='(选择)',anchor='center').place(x=252,y=320,width=50,height=25)
    

    # 完成
    ttk.Button(objdef,text='确认',command=comfirm_obj).place(x=130,y=355,height=30,width=50)

    Objdef_windows.mainloop()
    return obj_return_value
# 编辑区
def open_Edit_windows(father,Edit_filepath='',fig_W=960,fig_H=540):
    global image_canvas # 预览的画布
    global available_Text # 所有的可用文本名
    global used_variable_name # 已经被用户占用的命名
    selected_name,selected_type,selected_args = 'None','None','None'
    selected = 0
    edit_return_value = False
    available_Text = ['None','Text()']
    used_variable_name = []
    media_lines = [] # 保存当前所有媒体行，用于筛选时避免丢失原有媒体。有used_variable_name的地方就有它
    

    def new_obj(event=None): # 新建
        treeviewClick(event)
        try:# 非win系统，可能没有disable
            Edit_windows.attributes('-disabled',True)
        except Exception:
            pass
        new_obj = open_Media_def_window(father=Edit_windows)
        try:
            Edit_windows.attributes('-disabled',False)
        except Exception:
            pass
        Edit_windows.lift()
        Edit_windows.focus_force()
        if new_obj:
            used_variable_name.append(new_obj[0]) # 新建的媒体名
            media_lines.append(new_obj)

            if new_obj[1] in ['Text','StrokeText']: # 如果新建了文本
                mediainfo.insert('',0,values =new_obj) # 则插入在最上层
                available_Text.append(new_obj[0])
            else:
                mediainfo.insert('','end',values =new_obj) # 否则插入在最后
        sortMedia()
    def copy_obj(event=None): # 复制
        treeviewClick(event)
        if selected == 0:
            pass
        else:
            i = 1
            while True:
                new_name = selected_name+'_cp'+str(i)
                if (new_name in used_variable_name)|(new_name in occupied_variable_name):
                    i = i + 1
                else:
                    break
            used_variable_name.append(new_name) # 新建的媒体名
            media_lines.append((new_name,selected_type,selected_args))

            if selected_type in ['Text','StrokeText']: # 如果新建了文本
                available_Text.append(new_name)
                mediainfo.insert('',0,values =(new_name,selected_type,selected_args)) # 插入到最前面
            else:
                mediainfo.insert('','end',values =(new_name,selected_type,selected_args)) # 否则插入到最后面

        sortMedia()
    def preview_obj(event=None): # 预览
        treeviewClick(event) # 预览前先将当前选中项写入变量
        global image_canvas
        nonlocal show_canvas # 必须是全局变量，否则在函数后就被回收了，不再显示
        if selected_type in ['Text','StrokeText','Bubble','Background','Animation']: # 执行
            try:
                image_canvas.paste(blank_canvas,(0,0),mask=blank_canvas)
                exec('global {name};{name}={type}{args}'.format(name=selected_name,type=selected_type,args=selected_args))
                exec('global {name};{name}.preview()'.format(name=selected_name))
                show_canvas = ImageTk.PhotoImage(image_canvas.resize((fig_W//2,fig_H//2)))
                preview_canvas.config(image =show_canvas)
            except NameError as E: # 使用了尚未定义的对象！
                messagebox.showwarning(title='请先预览字体',message=E)
            except Exception as E: # 其他错误，主要是参数错误
                messagebox.showerror(title='错误',message=E)
        elif selected_type in ['BGM','Audio']:
            exec('global {name};{name}={type}{args}'.format(name=selected_name,type=selected_type,args=selected_args))
            exec('global {name};{name}.display()'.format(name=selected_name))

        elif selected_type == 'BuiltInAnimation':
            messagebox.showwarning(title='警告',message='内建动画对象不支持GUI编辑！')
        elif selected_type == 'None':
            messagebox.showwarning(title='警告',message='未选中任何对象！')
        else:
            messagebox.showerror(title='错误',message='不支持的媒体定义类型：'+selected_type)
    def edit_obj(event=None): # 编辑
        treeviewClick(event)
        nonlocal selected,selected_name,selected_type,selected_args
        if selected == 0:
            pass
        else:
            try:
                Edit_windows.attributes('-disabled',True)
            except Exception:
                pass
            new_obj = open_Media_def_window(Edit_windows,selected_name,selected_type,selected_args)
            try:
                Edit_windows.attributes('-disabled',False)
            except Exception:
                pass
            Edit_windows.lift()
            Edit_windows.focus_force()
            if new_obj:
                used_variable_name.remove(selected_name) # 原来的媒体名
                used_variable_name.append(new_obj[0]) # 新建的媒体名
                media_lines.remove((selected_name,selected_type,selected_args))
                media_lines.append(new_obj)

                if selected_type in ['Text','StrokeText']: # 如果编辑的对象是文本
                    available_Text.remove(selected_name)
                    available_Text.append(new_obj[0])
                mediainfo.item(selected,values=new_obj)
                selected_name,selected_type,selected_args = new_obj
        sortMedia()
    def del_obj(event=None): # 删除
        treeviewClick(event)
        nonlocal selected,selected_name,selected_type,selected_args
        if selected == 0:
            pass
        else:
            mediainfo.delete(selected)
            used_variable_name.remove(selected_name)
            media_lines.remove((selected_name,selected_type,selected_args))

            if selected_type in ['Text','StrokeText']: # 如果删除了文本
                available_Text.remove(selected_name)
            selected = 0
            selected_name,selected_type,selected_args = 'None','None','None'
    def finish(saveas=False): # 完成
        nonlocal edit_return_value
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
        
        # 保存前先将筛选器调回All
        media_type.set("All")
        filterMedia(None)

        for lid in mediainfo.get_children(): # 输出表格内容
            #print(mediainfo.item(lid, "values"))
            ofile.write('{0} = {1}{2}\n'.format(*mediainfo.item(lid, "values")))
        ofile.close()
        Edit_windows.destroy()
        Edit_windows.quit()
    def close_window():
        nonlocal edit_return_value
        if messagebox.askyesno(title='确认退出？',message='未保存的改动将会丢失！') == True:
            edit_return_value = Edit_filepath
            Edit_windows.destroy()
            Edit_windows.quit()
        else:
            pass
    def treeviewClick(event):  # 选中列单击
        nonlocal selected,selected_name,selected_type,selected_args
        try:
            selected = mediainfo.selection()
            selected_name,selected_type,selected_args = mediainfo.item(selected, "values")
            #print(selected_name,selected_type,selected_args)
        except Exception:
            pass
    def keyHandler(event): # 按键事件处理
        if event.char == 'e' or event.char == 'E':# 编辑（Edit）
            edit_obj(event)
        elif event.char == 'a' or event.char == 'A':# 新建（Add）
            new_obj(event)
        elif event.char == 'd' or event.char == 'D':# 复制（Duplicate）
            copy_obj(event)
    def filterMedia(event):
        nonlocal media_lines,media_type
        t = media_type.get()
        
        if t == 'All':
            filtered_list = media_lines
        else:
            filtered_list = [x for x in media_lines if x[1] == t]
        
        # 由于没有改动media_lines，所以不必在“All”选项时将文本媒体特地插到头部，按顺序遍历即可
        updateTreeView(filtered_list)

    def updateTreeView(new_list):# 更新表格显示数据，注意并不会修改统计数据，只会更新表格显示的内容
        i = 0
        mediainfo.delete(*mediainfo.get_children()) # 清空媒体
        for medium in new_list:
            if i % 2 == 1:
                mediainfo.insert('','end',values=medium)
            else:
                mediainfo.insert('','end',values=medium,tags=("evenColor"))
            i+=1


    def sortMedia(): # 给媒体分类排序
        priority = {
            "Text":1,
            "StrokeText":2,
            "Animation":3, 
            "Bubble":4, 
            "Background":5,
            "Audio":6, 
            "BGM":7
        }

        media_lines.sort(key=lambda elem:priority[elem[1]])
        updateTreeView(media_lines)

    def searchMedia(event): # 搜索框的回车事件处理函数
        text = search_text.get()
        result_list = [x for x in media_lines if x[0].find(text)!=-1 ]
        updateTreeView(result_list)

    def importMedia(): # 批量导入媒体
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
                            
                            if ((medium_name in occupied_variable_name)|(medium_name in used_variable_name)):
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
        media_lines.extend(media)
        media_type.set('All')
        updateTreeView(media_lines)

        


        



    window_W , window_H = fig_W//2+40,fig_H//2+440

    Edit_windows = tk.Toplevel(father)
    Edit_windows.resizable(0,0)
    Edit_windows.geometry("{W}x{H}".format(W=window_W,H=window_H))
    Edit_windows.config(background ='#e0e0e0')
    Edit_windows.title('回声工坊 媒体定义文件编辑器')
    Edit_windows.protocol('WM_DELETE_WINDOW',close_window)
    Edit_windows.transient(father)
    try:
        Edit_windows.iconbitmap('./media/icon.ico')
    except tk.TclError:
        pass
    
    frame_edit = tk.Frame(Edit_windows)
    frame_edit.place(x=10,y=10,height=window_H-20,width=window_W-20)

    # 信息框

    mediainfo_frame = tk.LabelFrame(frame_edit,text='媒体对象')
    mediainfo_frame.place(x=10,y=10,height=390,width=fig_W//2)

    ybar = ttk.Scrollbar(mediainfo_frame,orient='vertical')
    xbar = ttk.Scrollbar(mediainfo_frame,orient='horizontal')
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
    mediainfo.tag_configure("evenColor",background="#E6E6E6") # 行标签，用于偶数行着色

    mediainfo.bind('<ButtonRelease-1>', treeviewClick)
    mediainfo.bind('<Double-Button-1>',preview_obj) # 双击左键预览
    mediainfo.bind('<Button-3>',edit_obj) # 单击右键编辑
    mediainfo.bind('<Delete>',del_obj) # Delete键删除
    mediainfo.bind('<Key>',keyHandler) # 按键处理
    
    



    # 按键

    button_w = (fig_W//2-20)//8 # 这数字8 应该等于按键的 数量+1
    button_x = lambda x:10+(fig_W//2-20-button_w)//6*x # 这个数字6 应该等于按键的 数量-1

    ttk.Button(mediainfo_frame,text='导入',command=importMedia).place(x=button_x(0),y=320,width=button_w,height=40)
    ttk.Button(mediainfo_frame,text='新建',command=new_obj).place(x=button_x(1),y=320,width=button_w,height=40)
    ttk.Button(mediainfo_frame,text='复制',command=copy_obj).place(x=button_x(2),y=320,width=button_w,height=40)    
    ttk.Button(mediainfo_frame,text='编辑',command=edit_obj).place(x=button_x(3),y=320,width=button_w,height=40)
    ttk.Button(mediainfo_frame,text='删除',command=del_obj).place(x=button_x(4),y=320,width=button_w,height=40)
    ttk.Button(mediainfo_frame,text='保存',command=lambda:finish(False)).place(x=button_x(5),y=320,width=button_w,height=40)
    ttk.Button(mediainfo_frame,text='另存',command=lambda:finish(True)).place(x=button_x(6),y=320,width=button_w,height=40)

    # 预览图
    image_canvas = Image.open('./media/canvas.png').crop((0,0,fig_W,fig_H))
    blank_canvas = image_canvas.copy()
    blank_canvas.putalpha(192) # alpha 1.10.6 220 -> 192 上一个预览画面的残影更强了
    show_canvas = ImageTk.PhotoImage(image_canvas.resize((fig_W//2,fig_H//2)))
    preview_canvas = tk.Label(frame_edit,bg='black')
    preview_canvas.config(image=show_canvas)
    preview_canvas.place(x=10,y=410,height=fig_H//2,width=fig_W//2)

    # 筛选媒体下拉框
    media_type = tk.StringVar(Edit_windows)
    choose_type = ttk.Combobox(Edit_windows,textvariable=media_type,value=['All','Text','StrokeText','Bubble','Background','Animation','BGM','Audio'])
    choose_type.place(x=Edit_windows.winfo_width()-100,y=10,width=100,height=25) # 我就随便找个位置先放着，等后来人调整布局（都是绝对坐标很难搞啊）
    choose_type.current(0)
    choose_type.bind("<<ComboboxSelected>>",filterMedia)

    # 搜索框
    search_text = tk.StringVar(Edit_windows)
    search_entry =  tk.Entry(Edit_windows, textvariable=search_text)
    search_entry.place(x=200,y=10,width=300,height=25) # 同上，位置暂时随便摆的
    search_entry.bind('<Key-Return>',searchMedia) # 回车后搜索

    # 载入文件
    if Edit_filepath!='': # 如果有指定输入文件
        try:
            mediadef_text = open(Edit_filepath,'r',encoding='utf8').read().split('\n')
            if mediadef_text[-1] == '':
                mediadef_text.pop() # 如果最后一行是空行，则无视掉最后一行
            warning_line = []
            i = -1 # 即使是输入空文件，也能正确弹出提示框

            
            for i,line in enumerate(mediadef_text):
                parseline = RE_parse_mediadef.findall(line)
                if len(parseline) == 1:
                    # 插入行，并进行偶数行着色
                    if i % 2 ==1:
                        mediainfo.insert('','end',values = parseline[0])
                    else:
                        mediainfo.insert('','end',values = parseline[0],tags=("evenColor"))
                    
                    # 如果是字体媒体，提前载入
                    if parseline[0][1] == "Text" or parseline[0][1] == "StrokeText":
                        exec('global {name};{name}={type}{args}'.format(name=parseline[0][0],type=parseline[0][1],args=parseline[0][2]))


                    used_variable_name.append(parseline[0][0])
                    media_lines.append(parseline[0])

                    if parseline[0][1] in ['Text','StrokeText']:
                        available_Text.append(parseline[0][0])
                else:
                    warning_line.append(i+1)
            
            # 载入完毕先排个序
            sortMedia()
            if warning_line == []:
                messagebox.showinfo(title='完毕',message='载入完毕，共载入{i}条记录！'.format(i=i+1))
            else:
                messagebox.showwarning(title='完毕',message='载入完毕，共载入{i}条记录，\n第{warning}行因为无法解析而被舍弃！'.format(i=i+1-len(warning_line),warning=','.join(map(str,warning_line))))
        except UnicodeDecodeError:
            messagebox.showerror(title='错误',message='无法载入文件，请检查文本文件编码！')
    else:
        pass

    Edit_windows.mainloop()
    return edit_return_value

# 通用函数
def browse_file(text_obj,method='file'):
    if method == 'file':
        getname = filedialog.askopenfilename()
    else:
        getname = filedialog.askdirectory()
    if (' ' in getname) | ('$' in getname) | ('(' in getname) | (')' in getname):
        messagebox.showwarning(title='警告',message='请勿使用包含空格、括号或特殊符号的路径！')
        text_obj.set('')
        return None
    text_obj.set(getname)
    return getname

def choose_color(text_obj):
    get_color = colorchooser.askcolor()
    try:
        R,G,B = get_color[0]
        A = 255
        text_obj.set('({0},{1},{2},{3})'.format(int(R),int(G),int(B),int(A)))
    except Exception:
        text_obj.set('')
    
# 主界面的函数
def open_Main_windows():
    def printFrame():
        nonlocal frame_display
        frame_display.place_forget()
        select = tab_frame[tab.get()]
        select.place(x=10,y=50)
        frame_display = select
    def call_Edit_windows():
        Edit_filepath=media_define.get()
        fig_W = project_W.get()
        fig_H = project_H.get()
        try:
            Main_windows.attributes('-disabled',True)
        except Exception:
            pass
        # 如果Edit_filepath是合法路径
        if os.path.isfile(Edit_filepath): # alpha 1.8.5 非法路径
            return_from_Edit = open_Edit_windows(Main_windows,Edit_filepath,fig_W,fig_H)
        else:
            new_or_edit.config(text='新建')
            media_define.set('')
            return_from_Edit = open_Edit_windows(Main_windows,'',fig_W,fig_H)
        try:
            Main_windows.attributes('-disabled',False)
        except Exception:
            pass
        Main_windows.lift()
        Main_windows.focus_force()
        # 如果编辑窗的返回值是合法路径
        if os.path.isfile(return_from_Edit):
            media_define.set(return_from_Edit)
            new_or_edit.config(text='编辑')
        else:
            new_or_edit.config(text='新建')
    def call_browse_file(text_obj,method='file'):
        getname = browse_file(text_obj,method)
        if text_obj == media_define:
            if os.path.isfile(getname):
                new_or_edit.config(text='编辑')
            else:
                new_or_edit.config(text='新建')
    def load_au_file(): # 载入多个音频文件
        getnames = filedialog.askopenfilenames(filetypes=[('mp3文件','.mp3')])
        for index,filepath in enumerate(getnames):
            original_info.insert('','end',values =(index,filepath))
    def clear_au_file(): # 清空所有音频文件
        for item in original_info.get_children():
            original_info.delete(item)
        for item in convert_info.get_children():
            convert_info.delete(item)
    def run_convert(target):
        # 检查输出路径
        if output_path.get() == '':
            messagebox.showerror(title='错误',message='缺少输出路径，去主程序界面填写！')
            return -1
        else:
            opath = output_path.get()+'/'
        # 检查ffmpeg
        if os.path.isfile('./ffmpeg.exe'):
            ffmpeg_exec = 'ffmpeg.exe'
        else:
            ffmpeg_exec = 'ffmpeg'
        # 确定格式
        if target == 'wav':
            command = ffmpeg_exec+" -i {ifile} -f wav {ofile} -loglevel quiet"
        elif target == 'ogg':
            command = ffmpeg_exec+" -i {ifile} -acodec libvorbis -ab 128k {ofile} -loglevel quiet"
        else:
            return -1
        # 开始载入文件
        for item in original_info.get_children():
            index,filepath = original_info.item(item,"values")
            # 获取文件名
            try:
                filename = filepath.split('/')[-1][0:-3]
            except IndexError:
                messagebox.showerror(title='错误',message='出现了文件名称异常！'+filename)
                return -1
            # 检查文件路径
            if ' ' in filepath:
                filepath = '"'+filepath+'"'
            # 组装命令
            command_this = command.format(ifile = filepath, ofile = '"'+opath+filename+target+'"')
            # 执行命令
            try:
                print('[32m'+command_this+'[0m')
                exit_status = os.system(command_this)
                if exit_status != 0:
                    raise OSError('Major error occurred in ffmpeg!')
                else:
                    print('[convert_format]: '+opath + filename + target+' :Done!')
                    convert_info.insert('','end',values =(index,opath+filename+target))
            except Exception:
                messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了，检视控制台输出获取详细信息！')
                return -1
        messagebox.showinfo(title='完毕',message='格式格式转换完毕，输出文件在:'+opath)
    def run_command_main():
        optional = {1:'--OutputPath {of} ',2:'--ExportXML ',3:'--ExportVideo --Quality {ql} ',4:'--SynthesisAnyway --AccessKey {AK} --AccessKeySecret {AS} --Appkey {AP} --Azurekey {AZ} --ServRegion {SR} ',5:'--FixScreenZoom '}
        command = python3 + ' ./replay_generator.py --LogFile {lg} --MediaObjDefine {md} --CharacterTable {ct} '
        command = command + '--FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd} '
        if output_path.get()!='':
            command = command + optional[1].format(of=output_path.get().replace('\\','/'))
        if synthanyway.get()==1:
            command = command + optional[4].format(AK=AccessKey.get(),AS=AccessKeySecret.get(),AP=Appkey.get(),AZ=AzureKey.get(),SR=ServiceRegion.get()).replace('\n','').replace('\r','') # a 1.10.7 处理由于key复制导致的异常换行
        if exportprxml.get()==1:
            command = command + optional[2]
        if exportmp4.get()==1:
            command = command + optional[3].format(ql=project_Q.get())
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
                exit_status = os.system(command)
                if exit_status != 0:
                    raise OSError('Major error occurred in replay_generator!')
                else:
                    # 如果指定了要先语音合成，而且星标文件存在，且退出状态是正常，把log文件设置为星标文件：
                    if (synthanyway.get() == 1):
                        messagebox.showinfo(title='完毕',message='语音合成程序执行完毕！\nLog文件已更新')
            except Exception:
                messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了，检视控制台输出获取详细信息！')
    def run_command_synth():
        command = python3 +' ./speech_synthesizer.py --LogFile {lg} --MediaObjDefine {md} --CharacterTable {ct} --OutputPath {of} --AccessKey {AK} --AccessKeySecret {AS} --Appkey {AP} --Azurekey {AZ} --ServRegion {SR}'
        if '' in [stdin_logfile.get(),characor_table.get(),media_define.get(),output_path.get(),AccessKey.get(),AccessKeySecret.get(),Appkey.get(),AzureKey.get(),ServiceRegion.get()]:
            messagebox.showerror(title='错误',message='缺少必要的参数！')
        else:
            command = command.format(lg = stdin_logfile.get().replace('\\','/'),md = media_define.get().replace('\\','/'),
                                     of = output_path.get().replace('\\','/'), ct = characor_table.get().replace('\\','/'),
                                     AK=AccessKey.get(), AS=AccessKeySecret.get(),AP=Appkey.get(),AZ=AzureKey.get(),SR=ServiceRegion.get()).replace('\n','').replace('\r','') # a 1.10.7 处理由于key复制导致的异常换行
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
                exit_status = os.system(command)
                if exit_status != 0:
                    raise OSError('Major error occurred in export_xml!')
                else:
                    messagebox.showinfo(title='完毕',message='导出XML程序执行完毕！')
            except Exception:
                messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了，检视控制台输出获取详细信息！')
    def run_command_mp4():
        command = python3 + ' ./export_video.py --TimeLine {tm} --MediaObjDefine {md} --OutputPath {of} --FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd} --Quality {ql}'
        if '' in [timeline_file.get(),media_define.get(),output_path.get(),
                  project_W.get(),project_H.get(),project_F.get(),project_Z.get(),project_Q.get()]:
            messagebox.showerror(title='错误',message='缺少必要的参数！')
        else:
            command = command.format(tm = timeline_file.get().replace('\\','/'),
                                     md = media_define.get().replace('\\','/'), of = output_path.get().replace('\\','/'), 
                                     fps = project_F.get(), wd = project_W.get(),
                                     he = project_H.get(), zd = project_Z.get(), ql = project_Q.get())
            try:
                print('[32m'+command+'[0m')
                exit_status = os.system(command)
                if exit_status != 0:
                    raise OSError('Major error occurred in export_video!')
                else:
                    messagebox.showinfo(title='完毕',message='导出视频程序执行完毕！')
            except Exception:
                messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了，检视控制台输出获取详细信息！')
    def run_command_synth_preview(init_type='Aliyun'):
        command = python3 +' ./speech_synthesizer.py --PreviewOnly --Init {IN} --AccessKey {AK} --AccessKeySecret {AS} --Appkey {AP} --Azurekey {AZ} --ServRegion {SR}'
        command = command.format(IN=init_type, AK=AccessKey.get(), AS=AccessKeySecret.get(),AP=Appkey.get(),AZ=AzureKey.get(),SR=ServiceRegion.get()).replace('\n','').replace('\r','')
        try:
            print('[32m'+command+'[0m')
            exit_status = os.system(command)
            if exit_status != 0:
                raise OSError('Major error occurred in speech_synthesizer!')
            else:
                pass
        except Exception:
            messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了，检视控制台输出获取详细信息！')
    def highlight(target):
        if target == exportmp4:
            if target.get() == 1:
                tab4.config(fg='red',text='导出MP4 ⚑')
                label_ql.config(fg='red')
            else:
                tab4.config(fg='black',text='导出MP4')
                label_ql.config(fg='black')
        elif target == synthanyway:
            if target.get() == 1:
                warning_text = "注意！当使用“先执行语音合成”标志时，\n"
                warning_text += "若语音合成出现了异常，运行日志将会更难解读！\n"
                if messagebox.askokcancel(title='请谨慎使用“先执行语音合成”标志！',message=warning_text) == True:
                    tab2.config(fg='red',text='语音合成 ⚑')
                    label_AP.config(fg='red')
                    label_AK.config(fg='red')
                    label_AS.config(fg='red')
                    label_AZ.config(fg='red')
                    label_SR.config(fg='red')
                else:
                    # 否则，将先执行语音合成重置为"否"
                    target.set(0)
            else:
                tab2.config(fg='black',text='语音合成')
                label_AP.config(fg='black')
                label_AK.config(fg='black')
                label_AS.config(fg='black')
                label_AZ.config(fg='black')
                label_SR.config(fg='black')
        elif target == exportprxml:
            if target.get() == 1:
                tab3.config(text='导出XML ⚑')
            else:
                tab3.config(text='导出XML')
        elif target == fixscrzoom: 
            if target.get() == 1:
                try:
                    import ctypes
                    ctypes.windll.user32.SetProcessDPIAware() #修复错误的缩放，尤其是在移动设备。
                    Main_windows.update()
                except Exception:
                    messagebox.showwarning(title='警告',message='该选项在当前系统下不可用！')
                    target.set(0)
        else:
            pass
    def close_window():
        # 保存当前参数
        try:
            o_config = open('./media/save_config','wb')
            if save_config.get() == 1: # 以一个字典的形式把设置保存下来
                pickle.dump({
                    'stdin_logfile':stdin_logfile.get(),'characor_table':characor_table.get(),
                    'media_define':media_define.get(),'output_path':output_path.get(),
                    'timeline_file':timeline_file.get(),'project_W':project_W.get(),
                    'project_H':project_H.get(),'project_F':project_F.get(),
                    'project_Z':project_Z.get(),'project_Q':project_Q.get(),
                    'AccessKey':AccessKey.get(),'Appkey':Appkey.get(),'AccessKeySecret':AccessKeySecret.get(),
                    'AzureKey':AzureKey.get(),'ServiceRegion':ServiceRegion.get(),
                    'synthanyway':synthanyway.get(),'exportprxml':exportprxml.get(),
                    'exportmp4':exportmp4.get(),'fixscrzoom':fixscrzoom.get(),'save_config':save_config.get(),
                    'version':edtion
                },o_config) # 把版本信息保存下来
            else: # 如果选择不保存，则抹除保存的参数
                pickle.dump({'save_config':save_config.get()},o_config)
            o_config.close()
        except Exception:
            messagebox.showwarning(title='警告',message='保存设置内容失败!')
        finally: # 关闭主窗口
            Main_windows.destroy()
            Main_windows.quit()

    # 初始化
    Main_windows = tk.Tk()
    Main_windows.resizable(0,0)
    Main_windows.geometry("640x550")
    Main_windows.config(background ='#e0e0e0')
    Main_windows.protocol('WM_DELETE_WINDOW',close_window)
    Main_windows.title('回声工坊 ' + edtion)
    # linux:可能无法使用小图标
    try:
        Main_windows.iconbitmap('./media/icon.ico')
    except tk.TclError:
        pass
    # 大号字体
    try:
        big_text = font.Font(font=("微软雅黑",12))
    except Exception:
        big_text = font.Font(font=("System",12))

    # 选中的sheet
    tab = tk.IntVar(Main_windows)
    # 几个文件的路径
    stdin_logfile = tk.StringVar(Main_windows)
    characor_table = tk.StringVar(Main_windows)
    media_define = tk.StringVar(Main_windows)
    output_path = tk.StringVar(Main_windows)
    timeline_file = tk.StringVar(Main_windows)
    # 可选参数们
    project_W = tk.IntVar(Main_windows)
    project_H = tk.IntVar(Main_windows)
    project_F = tk.IntVar(Main_windows)
    project_Z = tk.StringVar(Main_windows)
    project_Q = tk.IntVar(Main_windows)
    # 语音合成的key
    AccessKey = tk.StringVar(Main_windows)
    Appkey = tk.StringVar(Main_windows)
    AccessKeySecret = tk.StringVar(Main_windows)
    AzureKey = tk.StringVar(Main_windows)
    ServiceRegion = tk.StringVar(Main_windows)
    # flag们
    synthanyway = tk.IntVar(Main_windows)
    exportprxml = tk.IntVar(Main_windows)
    exportmp4 = tk.IntVar(Main_windows)
    fixscrzoom = tk.IntVar(Main_windows)
    save_config = tk.IntVar(Main_windows)
    # 载入保存的参数
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
        project_W.set(1920)
        project_H.set(1080)
        project_F.set(30)
        project_Z.set('BG3,BG2,BG1,Am3,Am2,Am1,Bb')
        project_Q.set(24)
        AccessKey.set('Your_AccessKey')
        AccessKeySecret.set('Your_AccessKey_Secret')
        Appkey.set('Your_Appkey')
        AzureKey.set('Your_Azurekey')
        ServiceRegion.set('eastasia')
        # 将取消系统缩放设为默认值
        if sys.platform == 'win32':
            fixscrzoom.set(1)
        else:
            fixscrzoom.set(0)

    # 获取python解释器的路径
    python3 = sys.executable.replace('\\','/')
    #python3 = 'python' # exe发布版

    # 标签页选项
    tab1 = tk.Radiobutton(Main_windows,text="主程序", font= big_text,command=printFrame,variable=tab,value=1,indicatoron=False)
    tab2 = tk.Radiobutton(Main_windows,text="语音合成", font=big_text,command=printFrame,variable=tab,value=2,indicatoron=False)
    tab3 = tk.Radiobutton(Main_windows,text="导出XML", font=big_text,command=printFrame,variable=tab,value=3,indicatoron=False)
    tab4 = tk.Radiobutton(Main_windows,text="导出MP4", font=big_text,command=printFrame,variable=tab,value=4,indicatoron=False)
    tab5 = tk.Radiobutton(Main_windows,text="音频\n格式转换",command=printFrame,variable=tab,value=5,indicatoron=False)
    tab1.place(x=10,y=10,width=138,height=40)
    tab2.place(x=148,y=10,width=138,height=40)
    tab3.place(x=286,y=10,width=138,height=40)
    tab4.place(x=424,y=10,width=138,height=40)
    tab5.place(x=562,y=10,width=68,height=40)

    # 四个界面
    main_frame = tk.Frame(Main_windows,height=490 ,width=620)
    synth_frame = tk.Frame(Main_windows,height=490 ,width=620)
    xml_frame = tk.Frame(Main_windows,height=490 ,width=620)
    mp4_frame = tk.Frame(Main_windows,height=490 ,width=620)
    format_frame = tk.Frame(Main_windows,height=490 ,width=620)
    tab_frame = {1:main_frame,2:synth_frame,3:xml_frame,4:mp4_frame,5:format_frame}

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
    tk.Button(filepath, command=lambda:call_browse_file(media_define),text="浏览").place(x=520,y=5,width=35,height=30)
    tk.Button(filepath, command=lambda:call_browse_file(characor_table),text="浏览").place(x=520,y=50,width=70,height=30)
    tk.Button(filepath, command=lambda:call_browse_file(stdin_logfile),text="浏览").place(x=520,y=95,width=70,height=30)
    tk.Button(filepath, command=lambda:call_browse_file(output_path,'path'),text="浏览").place(x=520,y=140,width=70,height=30)


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

    tk.Checkbutton(flag,text="先执行语音合成",variable=synthanyway,anchor=tk.W,command=lambda:highlight(synthanyway)).place(x=10,y=0,width=150,height=30)
    tk.Checkbutton(flag,text="导出为PR项目",variable=exportprxml,anchor=tk.W,command=lambda:highlight(exportprxml)).place(x=10,y=27,width=150,height=30)
    tk.Checkbutton(flag,text="导出为.mp4视频",variable=exportmp4,anchor=tk.W,command=lambda:highlight(exportmp4)).place(x=170,y=27,width=150,height=30)
    tk.Checkbutton(flag,text="取消系统缩放",variable=fixscrzoom,anchor=tk.W,command=lambda:highlight(fixscrzoom)).place(x=170,y=0,width=150,height=30)
    tk.Checkbutton(flag,text="保存设置内容",variable=save_config,anchor=tk.W).place(x=10,y=55,width=150,height=30)

    my_logo = ImageTk.PhotoImage(Image.open('./media/logo.png').resize((236,75)))
    tk.Button(flag,image = my_logo,command=lambda: webbrowser.open('https://www.wolai.com/PjcZ7xwNTKB2VJ5AJYggv'),relief='flat').place(x=339,y=0)

    # 开始
    tk.Button(main_frame, command=run_command_main,text="开始",font=big_text).place(x=260,y=435,width=100,height=50)

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
    tk.Button(filepath_s, command=lambda:call_browse_file(media_define),text="浏览").place(x=520,y=5,width=70,height=30)
    tk.Button(filepath_s, command=lambda:call_browse_file(characor_table),text="浏览").place(x=520,y=50,width=70,height=30)
    tk.Button(filepath_s, command=lambda:call_browse_file(stdin_logfile),text="浏览").place(x=520,y=95,width=70,height=30)
    tk.Button(filepath_s, command=lambda:call_browse_file(output_path,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

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

    optional_s = tk.LabelFrame(synth_frame,text='选项')
    optional_s.place(x=10,y=210,width=600,height=110)

    label_AP = tk.Label(optional_s, text="Appkey：",anchor=tk.W)
    label_AP.place(x=10,y=0,width=110,height=25)
    label_AK = tk.Label(optional_s, text="AccessKey：",anchor=tk.W)
    label_AK.place(x=10,y=30,width=110,height=25)
    label_AS = tk.Label(optional_s, text="AccessKeySecret：",anchor=tk.W)
    label_AS.place(x=10,y=60,width=110,height=25)

    tk.Entry(optional_s, textvariable=Appkey).place(x=120,y=0,width=390,height=25)
    tk.Entry(optional_s, textvariable=AccessKey).place(x=120,y=30,width=390,height=25)
    tk.Entry(optional_s, textvariable=AccessKeySecret).place(x=120,y=60,width=390,height=25)
    tk.Button(optional_s,text="⇵",command=lambda: change_service(optional_s)).place(x=565,y=0,width=25,height=25)

    optional_azs = tk.LabelFrame(synth_frame,text='选项')
    #optional_azs.place(x=10,y=210,width=600,height=110)

    label_AZ = tk.Label(optional_azs, text="AzureKey：",anchor=tk.W)
    label_AZ.place(x=10,y=10,width=110,height=25)
    label_SR = tk.Label(optional_azs, text="服务区域：",anchor=tk.W)
    label_SR.place(x=10,y=50,width=110,height=25)

    tk.Entry(optional_azs, textvariable=AzureKey).place(x=120,y=10,width=390,height=25)
    tk.Entry(optional_azs, textvariable=ServiceRegion).place(x=120,y=50,width=390,height=25)
    tk.Button(optional_azs,text="⇵",command=lambda: change_service(optional_azs)).place(x=565,y=0,width=25,height=25)

    flag_s = tk.LabelFrame(synth_frame,text='标志')
    flag_s.place(x=10,y=320,width=600,height=110)
    aliyun_logo = ImageTk.PhotoImage(Image.open('./media/aliyun.png'))
    tk.Label(flag_s,image = aliyun_logo).place(x=20,y=13)
    tk.Label(flag_s,text='本项功能由阿里云语音合成支持，了解更多：').place(x=300,y=15)
    tk.Button(flag_s,text='https://ai.aliyun.com/nls/',command=lambda: webbrowser.open('https://ai.aliyun.com/nls/'),fg='blue',relief='flat').place(x=300,y=40)
    tk.Button(flag_s,text='试听',command=lambda:run_command_synth_preview('Aliyun')).place(x=540,y=55,width=50,height=25)

    flag_azs = tk.LabelFrame(synth_frame,text='标志')
    #flag_azs.place(x=10,y=320,width=600,height=110)
    azure_logo = ImageTk.PhotoImage(Image.open('./media/Azure.png'))
    tk.Label(flag_azs,image = azure_logo).place(x=20,y=8)
    tk.Label(flag_azs,text='本项功能由Azure认知语音服务支持，了解更多：').place(x=300,y=15)
    tk.Button(flag_azs,text='https://docs.microsoft.com/azure/',command=lambda: webbrowser.open('https://docs.microsoft.com/zh-cn/azure/cognitive-services'),fg='blue',relief='flat').place(x=300,y=40)
    tk.Button(flag_azs,text='试听',command=lambda:run_command_synth_preview('Azure')).place(x=540,y=55,width=50,height=25)

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
    tk.Button(filepath_x, command=lambda:call_browse_file(media_define),text="浏览").place(x=520,y=5,width=70,height=30)
    tk.Button(filepath_x, command=lambda:call_browse_file(characor_table),text="浏览",state=tk.DISABLED).place(x=520,y=50,width=70,height=30)
    tk.Button(filepath_x, command=lambda:call_browse_file(timeline_file),text="浏览").place(x=520,y=95,width=70,height=30)
    tk.Button(filepath_x, command=lambda:call_browse_file(output_path,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

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

    PR_logo = ImageTk.PhotoImage(Image.open('./media/PR.png'))
    Eta_logo = ImageTk.PhotoImage(Image.open('./media/eta.png'))
    tk.Label(flag_x,image = PR_logo).place(x=20,y=10)
    tk.Label(flag_x,text='通向Premiere Pro世界的通道。').place(x=110,y=30)
    tk.Label(flag_x,text='感谢up主伊塔的Idea，了解更多：').place(x=300,y=30)
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
    tk.Button(filepath_v, command=lambda:call_browse_file(media_define),text="浏览").place(x=520,y=5,width=70,height=30)
    tk.Button(filepath_v, command=lambda:call_browse_file(characor_table),text="浏览",state=tk.DISABLED).place(x=520,y=50,width=70,height=30)
    tk.Button(filepath_v, command=lambda:call_browse_file(timeline_file),text="浏览").place(x=520,y=95,width=70,height=30)
    tk.Button(filepath_v, command=lambda:call_browse_file(output_path,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

    optional_v = tk.LabelFrame(mp4_frame,text='选项')
    optional_v.place(x=10,y=210,width=600,height=110)

    tk.Label(optional_v,text="分辨率-宽:",anchor=tk.W).place(x=10,y=5,width=70,height=30)
    tk.Label(optional_v,text="分辨率-高:",anchor=tk.W).place(x=160,y=5,width=70,height=30)
    tk.Label(optional_v,text="帧率:",anchor=tk.W).place(x=310,y=5,width=70,height=30)
    tk.Label(optional_v,text="图层顺序:",anchor=tk.W).place(x=10,y=50,width=70,height=30)
    label_ql = tk.Label(optional_v,text="质量:",anchor=tk.W)
    label_ql.place(x=310,y=50,width=70,height=30)

    tk.Entry(optional_v,textvariable=project_W).place(x=80,y=5,width=70,height=25)
    tk.Entry(optional_v,textvariable=project_H).place(x=230,y=5,width=70,height=25)
    tk.Entry(optional_v,textvariable=project_F).place(x=380,y=5,width=70,height=25)
    tk.Entry(optional_v,textvariable=project_Z).place(x=80,y=50,width=220,height=25)
    tk.Entry(optional_v,textvariable=project_Q).place(x=380,y=50,width=70,height=25)

    flag_v = tk.LabelFrame(mp4_frame,text='标志')
    flag_v.place(x=10,y=320,width=600,height=110)

    ffmpeg_logo = ImageTk.PhotoImage(Image.open('./media/ffmpeg.png'))
    tk.Label(flag_v,image = ffmpeg_logo).place(x=20,y=10)
    tk.Label(flag_v,text='本项功能调用ffmpeg实现，了解更多：').place(x=300,y=15)
    tk.Button(flag_v,text='https://ffmpeg.org/',command=lambda: webbrowser.open('https://ffmpeg.org/'),fg='blue',relief='flat').place(x=300,y=40)

    tk.Button(mp4_frame, command=run_command_mp4,text="开始",font=big_text).place(x=260,y=435,width=100,height=50)

    # format_frame

    original_file = tk.LabelFrame(format_frame,text='原始音频文件')
    convert_file = tk.LabelFrame(format_frame,text='转换后音频文件')
    original_file.place(x=10,y=10,width=600,height=210)
    convert_file.place(x=10,y=220,width=600,height=210)
    # 原始音频文件
    ybar_original = ttk.Scrollbar(original_file,orient='vertical')
    original_info = ttk.Treeview(original_file,columns=['index','filepath'],show = "headings",selectmode = tk.BROWSE,yscrollcommand=ybar_original.set)
    ybar_original.config(command=original_info.yview)
    ybar_original.place(x=575,y=0,height=180,width=15)

    original_info.column("index",anchor = "center",width=40)
    original_info.column("filepath",anchor = "w",width=520)

    original_info.heading("index", text = "序号")
    original_info.heading("filepath", text = "路径")

    original_info.place(x=10,y=0,height=180,width=565)
    # 转换后音频文件
    ybar_convert = ttk.Scrollbar(convert_file,orient='vertical')
    convert_info = ttk.Treeview(convert_file,columns=['index','filepath'],show = "headings",selectmode = tk.BROWSE,yscrollcommand=ybar_convert.set)
    ybar_convert.config(command=convert_info.yview)
    ybar_convert.place(x=575,y=0,height=180,width=15)

    convert_info.column("index",anchor = "center",width=40)
    convert_info.column("filepath",anchor = "w",width=520)

    convert_info.heading("index", text = "序号")
    convert_info.heading("filepath", text = "路径")

    convert_info.place(x=10,y=0,height=180,width=565)
    # 按键
    tk.Button(format_frame, command=load_au_file,text="载入",font=big_text).place(x=65,y=440,width=100,height=40)
    tk.Button(format_frame, command=clear_au_file,text="清空",font=big_text).place(x=195,y=440,width=100,height=40)
    tk.Button(format_frame, command=lambda:run_convert('wav'),text="转wav",font=big_text).place(x=325,y=440,width=100,height=40)
    tk.Button(format_frame, command=lambda:run_convert('ogg'),text="转ogg",font=big_text).place(x=455,y=440,width=100,height=40)

    # 初始化highlight和编辑/新建按钮的显示
    try:
        for flag in [synthanyway,exportmp4,exportprxml,fixscrzoom]:
            if flag.get() == 1:
                highlight(flag)
        if os.path.isfile(media_define.get()):
            new_or_edit.config(text='编辑')
        else:
            new_or_edit.config(text='新建')
    except Exception:
        pass
        
    # Mainloop
    Main_windows.mainloop()

if __name__=='__main__':
    open_Main_windows()