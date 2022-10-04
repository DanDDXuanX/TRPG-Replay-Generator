"""
TODO
新增媒体对象的窗口

（深感工作量恐怖，所以这个还是不抽取为类了，就把原来的函数直接拿来用吧，想优化的时候可以把这个类写完，然后调用它的open函数来代替原来的函数）
"""

import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageDraw, ImageFont, ImageTk
from utils import browse_file, choose_color

from .Media import Animation, Background, Bubble, StrokeText, Text
from .Media import Pos, FreePos, PosGrid
from .Media import Balloon, DynamicBubble

from .SubWindow import SubWindow

###################如果把类写完，可以删掉下面的函数，用类中带mainloop的函数替代之
###################上面那个类比较干扰增加新功能，暂时删了。之后需要的话，在前一个结点起branch去继续做吧

label_pos_show_text = ImageFont.truetype('./media/SourceHanSerifSC-Heavy.otf', 30)
# RE_mediadef_args = re.compile('(fontfile|fontsize|color|line_limit|filepath|Main_Text|Header_Text|pos|end|x_step|y_step|mt_pos|mt_end|ht_pos|ht_target|fill_mode|align|line_distance|tick|loop|volume|edge_color|label_color)?\ {0,4}=?\ {0,4}(Text\(\)|[^,()]+|\([-\d,\ ]+\))')
RE_mediadef_args = re.compile("(fontfile|fontsize|color|line_limit|filepath|Main_Text|Header_Text|pos|end|x_step|y_step|mt_pos|mt_end|ht_pos|ht_target|fill_mode|align|line_distance|tick|loop|volume|edge_color|label_color|sub_key|sub_Bubble|sub_Anime|sub_align)?\ {0,4}=?\ {0,4}(Text\(\)|\[[\w,'()]+\]|\w+\[[\d\,]+\]|[^,()]+|\([-\d,\ ]+\))")
# RE_parse_mediadef = re.compile('(\w+)[=\ ]+(Pos|FreePos|PosGrid|Text|StrokeText|Bubble|Animation|Background|BGM|Audio)(\(.+\))')
RE_vaildname = re.compile('^\w+$')
RE_pos_args = re.compile('(\d+),(\d+)|\*\((\d+),(\d+)\)')
occupied_variable_name = open('./media/occupied_variable_name.list','r',encoding='utf8').read().split('\n') # 已经被系统占用的变量名

# 选择位置窗
def open_pos_select_window(father,image_canvas,bgfigure='',postype='green',current_pos=''):
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
def open_media_def_window(father,image_canvas,available_Text,used_variable_name,i_name='',i_type='',i_args=''):
    # 函数正文
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
                'pos':pos.get(),'end':end.get(),'x_step':x_step.get(),'y_step':y_step.get(),
                'mt_pos':mt_pos.get(),'mt_end':mt_end.get(),
                'ht_pos':ht_pos.get(),'ht_target':ht_target.get(),
                'align':align.get(),'fill_mode':fill_mode.get(),
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
            get = open_pos_select_window(father=Objdef_windows,image_canvas=image_canvas,bgfigure=filepath.get(),postype='blue',current_pos=target.get())
        elif target in [pos,end]:
            get = open_pos_select_window(father=Objdef_windows,image_canvas=image_canvas,bgfigure=filepath.get(),postype='green',current_pos=target.get())
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
        'Pos':"{pos}",
        'FreePos':"{pos}",
        'PosGrid':"(pos={pos},end={end},x_step={x_step},y_step={y_step})",
        'Text':"(fontfile='{fontfile}',fontsize={fontsize},color={color},line_limit={line_limit},label_color='{label_color}')",
        'StrokeText':"(fontfile='{fontfile}',fontsize={fontsize},color={color},line_limit={line_limit},edge_color={edge_color},label_color='{label_color}')",
        'Bubble':"(filepath='{filepath}',Main_Text={Main_Text},Header_Text={Header_Text},pos={pos},mt_pos={mt_pos},ht_pos={ht_pos},ht_target={ht_target},align='{align}',line_distance={line_distance},label_color='{label_color}')",
        'Balloon':"(filepath='{filepath}',Main_Text={Main_Text},Header_Text=[{Header_Text}],pos={pos},mt_pos={mt_pos},ht_pos=[{ht_pos}],ht_target=[{ht_target}],align={align},line_distance={line_distance},label_color='{label_color}')",
        'DynamicBubble':"(filepath='{filepath}',Main_Text={Main_Text},Header_Text={Header_Text},pos={pos},mt_pos={mt_pos},mt_end={mt_end},ht_pos={ht_pos},ht_target={ht_target},fill_mode={fill_mode},line_distance={line_distance},label_color='{label_color}')",
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
    choose_type = ttk.Combobox(objdef,textvariable=o_type,value=list(arg_tplt.keys()))
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
    # 新增：Pos，FreePos，PosGrid
    Pos_frame = tk.LabelFrame(objdef,text='Pos参数')
    FreePos_frame = tk.LabelFrame(objdef,text='FreePos参数')
    PosGrid_frame = tk.LabelFrame(objdef,text='PosGrid参数')
    Balloon_frame = tk.LabelFrame(objdef,text='Balloon参数')
    DynamicBubble_frame = tk.LabelFrame(objdef,text='DynamicBubble参数')
    GroupedAnimation_frame = tk.LabelFrame(objdef,text='GroupedAnimation参数')
    # 新增：
    # typedi
    Mediatype = {'Pos':Pos_frame,'FreePos':FreePos_frame,'PosGrid':PosGrid_frame,
                 'Text':Text_frame,'StrokeText':StrokeText_frame,
                 'Bubble':Bubble_frame,'Balloon':Balloon_frame,'DynamicBubble':DynamicBubble_frame,
                 'Background':Background_frame,
                 'Animation':Animation_frame,'GroupedAnimation':GroupedAnimation_frame,
                 'BGM':BGM_frame,'Audio':Audio_frame}

    fontfile = tk.StringVar(Objdef_windows)
    fontsize = tk.IntVar(Objdef_windows)
    color = tk.StringVar(Objdef_windows)
    line_limit = tk.IntVar(Objdef_windows)
    filepath = tk.StringVar(Objdef_windows)
    Main_Text = tk.StringVar(Objdef_windows)
    Header_Text = tk.StringVar(Objdef_windows)
    pos = tk.StringVar(Objdef_windows)
    end = tk.StringVar(Objdef_windows)
    x_step = tk.StringVar(Objdef_windows)
    y_step = tk.StringVar(Objdef_windows)
    mt_pos = tk.StringVar(Objdef_windows)
    mt_end = tk.StringVar(Objdef_windows)
    ht_pos = tk.StringVar(Objdef_windows)
    ht_target = tk.StringVar(Objdef_windows)
    fill_mode = tk.StringVar(Objdef_windows)
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
    end.set('')
    x_step.set(1)
    y_step.set(1)
    mt_pos.set('(0,0)')
    ht_pos.set('(0,0)')
    align.set('left')
    line_distance.set(1.5)
    tick.set(1)
    loop.set(True)
    volume.set(100)
    edge_color.set('(255,255,255,255)')
    label_color.set('Lavender')
    mt_end.set('(0,0)')
    ht_target.set('Name')
    fill_mode.set('stretch')
    # 可用标签颜色
    available_label_color = {'Violet':'#a690e0','Iris':'#729acc','Caribbean':'#29d698','Lavender':'#e384e3',
                             'Cerulean':'#2fbfde','Forest':'#51b858','Rose':'#f76fa4','Mango':'#eda63b',
                             'Purple':'#970097','Blue':'#3c3cff','Teal':'#008080','Magenta':'#e732e7',
                             'Tan':'#cec195','Green':'#1d7021','Brown':'#8b4513','Yellow':'#e2e264'}
    # 外部输入参数
    type_keyword_position = {'Pos':['pos'],'FreePos':['pos'],'PosGrid':['pos','end','x_step','y_step'],
                            'Text':['fontfile','fontsize','color','line_limit','label_color'],
                            'StrokeText':['fontfile','fontsize','color','line_limit','edge_color','label_color'],
                            'Bubble':['filepath','Main_Text','Header_Text','pos','mt_pos','ht_pos','ht_target','align','line_distance','label_color'],
                            'Balloon':['filepath','Main_Text','Header_Text','pos','mt_pos','ht_pos','ht_target','align','line_distance','label_color'],
                            'DynamicBubble':['filepath','Main_Text','Header_Text','pos','mt_pos','mt_end','ht_pos','ht_target','fill_mode','line_distance','label_color'],
                            'Background':['filepath','pos','label_color'],
                            'Animation':['filepath','pos','tick','loop','label_color'],
                            'Audio':['filepath','label_color'],
                            'BGM':['filepath','volume','loop','label_color']}

    #初始状态 空白或者选中
    if i_type == '':
        Empty_frame.place(x=10,y=40,width=300,height=275)
        type_display = Empty_frame
    elif i_type in [Pos,FreePos]:
        Mediatype[i_type].place(x=10,y=40,width=300,height=275)
        type_display = Mediatype[i_type]
        pos_args = RE_pos_args.findall(i_args)[0]
        if pos_args[0] != '':
            pos_x = pos_args[0]
            pos_y = pos_args[1]
        elif pos_args[2] != '':
            pos_x = pos_args[2]
            pos_y = pos_args[3]
        else:
            pos_x = 0
            pos_y = 0
        pos.set('({0},{1})'.format(pos_x,pos_y))
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
    # Pos_frame
    ttk.Label(Pos_frame,text='位置').place(x=10,y=10,width=65,height=25)
    ttk.Entry(Pos_frame,textvariable=pos).place(x=75,y=10,width=160,height=25)
    ttk.Button(Pos_frame,text='选择',command=lambda:call_possele(pos)).place(x=240,y=10,width=50,height=25)
    # FreePos_frame
    ttk.Label(FreePos_frame,text='初始位置').place(x=10,y=10,width=65,height=25)
    ttk.Entry(FreePos_frame,textvariable=pos).place(x=75,y=10,width=160,height=25)
    ttk.Button(FreePos_frame,text='选择',command=lambda:call_possele(pos)).place(x=240,y=10,width=50,height=25)
    # PosGrid_frame
    ttk.Label(PosGrid_frame,text='网格起点').place(x=10,y=10,width=65,height=25)
    ttk.Label(PosGrid_frame,text='网格终点').place(x=10,y=40,width=65,height=25)
    ttk.Label(PosGrid_frame,text='X轴格数').place(x=10,y=70,width=65,height=25)
    ttk.Label(PosGrid_frame,text='Y轴格数').place(x=10,y=100,width=65,height=25)
    ttk.Entry(PosGrid_frame,textvariable=pos).place(x=75,y=10,width=160,height=25)
    ttk.Entry(PosGrid_frame,textvariable=end).place(x=75,y=40,width=160,height=25)
    ttk.Entry(PosGrid_frame,textvariable=x_step).place(x=75,y=70,width=160,height=25)
    ttk.Entry(PosGrid_frame,textvariable=y_step).place(x=75,y=100,width=160,height=25)
    ttk.Button(PosGrid_frame,text='选择',command=lambda:call_possele(pos)).place(x=240,y=10,width=50,height=25)
    ttk.Button(PosGrid_frame,text='选择',command=lambda:call_possele(end)).place(x=240,y=40,width=50,height=25)
    ttk.Label(PosGrid_frame,text='(整数)',anchor='center').place(x=240,y=70,width=50,height=25)
    ttk.Label(PosGrid_frame,text='(整数)',anchor='center').place(x=240,y=100,width=50,height=25)
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

    # Balloon_frame

    # DynamicBubble_frame

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

