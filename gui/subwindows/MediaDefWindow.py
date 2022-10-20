"""
TODO
新增媒体对象的窗口

（深感工作量恐怖，所以这个还是不抽取为类了，就把原来的函数直接拿来用吧，想优化的时候可以把这个类写完，然后调用它的open函数来代替原来的函数）
"""

import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from turtle import update

from PIL import Image, ImageDraw, ImageFont, ImageTk
from utils import browse_file, choose_color

from .Media import Animation, Background, Bubble, StrokeText, Text
from .Media import Pos, FreePos, PosGrid
from .Media import Balloon, DynamicBubble,ChatWindow

from .SubWindow import SubWindow

###################如果把类写完，可以删掉下面的函数，用类中带mainloop的函数替代之
###################上面那个类比较干扰增加新功能，暂时删了。之后需要的话，在前一个结点起branch去继续做吧

label_pos_show_text = ImageFont.truetype('./media/SourceHanSerifSC-Heavy.otf', 30)
# RE_mediadef_args = re.compile('(fontfile|fontsize|color|line_limit|filepath|Main_Text|Header_Text|pos|end|x_step|y_step|mt_pos|mt_end|ht_pos|ht_target|fill_mode|align|line_distance|tick|loop|volume|edge_color|label_color)?\ {0,4}=?\ {0,4}(Text\(\)|[^,()]+|\([-\d,\ ]+\))')
RE_mediadef_args = re.compile("(fontfile|fontsize|color|line_limit|filepath|Main_Text|Header_Text|pos|end|x_step|y_step|mt_pos|mt_end|ht_pos|ht_target|fill_mode|align|line_distance|tick|loop|volume|edge_color|sub_key|sub_Bubble|sub_Anime|sub_align|sub_pos|sub_end|am_left|am_right|sub_distance|label_color)?\ {0,4}=?\ {0,4}(Text\(\)|Pos\(\)|\[[\w,'()]+\]|\w+\[[\d\,]+\]|[^,()]+|\([-\d,\ ]+\))")
# RE_parse_mediadef = re.compile('(\w+)[=\ ]+(Pos|FreePos|PosGrid|Text|StrokeText|Bubble|Animation|Background|BGM|Audio)(\(.+\))')
RE_vaildname = re.compile('^\w+$')
RE_pos_args = re.compile('(\d+),(\d+)|\*\((\d+),(\d+)\)')
occupied_variable_name = open('./media/occupied_variable_name.list','r',encoding='utf8').read().split('\n') # 已经被系统占用的变量名

# 多选参数窗
class Grouped_args_select_window(SubWindow):
    def __init__(self,master,input,available_Text,available_target,available_Bubble,available_Anime,filepath,image_canvas,*args, **kwargs):
        super().__init__(master,*args, **kwargs)
        self.resizable(0,0)
        self.geometry("{W}x{H}".format(W=340,H=340))
        self.config(background ='#e0e0e0')
        self.title('组合参数选择')
        self.protocol('WM_DELETE_WINDOW',self.close_window)
        self.transient(master)
        try:
            self.iconbitmap('./media/icon.ico')
        except tk.TclError:
            pass
        self.input = input
        self.available_Text = available_Text
        self.available_target = available_target
        self.available_Bubble = ['Bubble()'] + available_Bubble
        self.available_Anime = ['None'] + available_Anime
        self.filepath = filepath
        self.image_canvas = image_canvas
        # 初始化界面
        self.load_args()
        self.bulid_widget()
        # 主循环
        self.mainloop()
    # 关闭窗口
    def close_window(self):
        self.destroy()
        self.quit()
    # 获取点击内容
    def treeview_click(self,event=None):
        # 如果在修改了一行之后点击了另一行，则保存前一行
        def dequote(_str):
            if _str[0] == "'" or _str[0] == '"':
                return _str[1:-1]
        try:
            self.selected = self.args_table.selection()
            values = self.args_table.item(self.selected, "values")
            # 将本次点击获取的值保留再value_recode
            self.value_recode = values
            # 将值
            if len(self.args_name) == 3:
                self.HeaderText.set(values[0])
                self.ht_pos.set(values[1])
                self.ht_target.set(values[2])
            elif len(self.args_name) == 4:
                self.sub_key.set(dequote(values[0]))
                self.sub_Bubble.set(values[1])
                self.sub_Anime.set(values[2])
                self.sub_align.set(dequote(values[3]))
            self.frame_args.place(x=10,y=120,width=300,height=150)
            self.add_bubbon.place_forget()
            self.update_bubbon.place(x=40,y=275,width=60,height=35)
        except Exception:
            import traceback
            traceback.print_exc()
    # 更新表格
    def update_treeview(self,new_list):
        self.args_table.delete(*self.args_table.get_children()) # 清空媒体
        for medium in new_list:
            self.args_table.insert('','end',values=medium)
    # 从当前选择的参数更新参数
    def update_value(self):
        def quote(_str):
            return "'" + str(_str) + "'"
        old_values = self.value_recode
        if len(self.args_name) == 3:
            new_values = (self.HeaderText.get(),self.ht_pos.get(),self.ht_target.get())
        elif len(self.args_name) == 4:
            new_values = (quote(self.sub_key.get()),self.sub_Bubble.get(),self.sub_Anime.get(),quote(self.sub_align.get()))
        if new_values != old_values:
            index = self.args_list.index(old_values)
            # 直接按index索引并修改
            self.args_list[index] = new_values
            self.update_treeview(self.args_list)
        # 清除参数框，复原按钮
        self.update_bubbon.place_forget()
        self.frame_args.place_forget()
        self.add_bubbon.place(x=40,y=275,width=60,height=35)
    # 新建key
    def add_key(self):
        # 然后再走新建的流程
        if len(self.args_name) == 3:
            self.args_list.append(('Text()','(0,0)',"'Name'"))
        elif len(self.args_name) == 4:
            self.args_list.append(("'Key1'",'','',"'left'"))
        self.update_treeview(self.args_list)
        # 尝试设置为最后一行？
        self.args_table.selection_set(self.args_table.get_children()[-1])
        self.treeview_click()
    # 删除项目
    def del_key(self):
        values = self.args_table.item(self.selected, "values")
        self.args_list.remove(values)
        self.update_treeview(self.args_list)
        # 清除参数框，复原按钮
        self.update_bubbon.place_forget()
        self.frame_args.place_forget()
        self.add_bubbon.place(x=40,y=275,width=60,height=35)
    # 初始化的时候载入输入参数
    def load_args(self):
        # Header_Text,ht_pos,ht_target
        # sub_key,sub_bubble,sub_anime,sub_align
        RE_arglist = re.compile("Text\(\)|Bubble\(\)|'[^',]+'|\([\d\,\ ]+\)|\w+")
        if len(self.input) == 3:
            n_col = 3
            self.args_name = ['头文本字体','头文本位置','头文本目标']
            self.HeaderText = tk.StringVar(self)
            self.ht_pos = tk.StringVar(self)
            self.ht_target = tk.StringVar(self)
        elif len(self.input) == 4:
            n_col = 4
            self.args_name = ['关键字','聊天窗气泡','聊天窗头像','聊天窗对齐']
            self.sub_key = tk.StringVar(self)
            self.sub_Bubble = tk.StringVar(self)
            self.sub_Anime = tk.StringVar(self)
            self.sub_align = tk.StringVar(self)
        else:
            self.close_window()
        self.args_list = []
        line_index = 0
        this_line = []
        while this_line != [''] * n_col:
            this_line = [''] * n_col
            for i in range(n_col):
                try:
                    this_line[i] = RE_arglist.findall(self.input[i].get())[line_index]
                except IndexError:
                    pass
            self.args_list.append(tuple(this_line))
            line_index = line_index + 1
        # 删掉最后的一个空行
        self.args_list.remove(tuple([''] * n_col))
    # 确认选择-关闭窗口
    def comfirm(self):
        out_text = {}
        # 拼接参数
        for i in range(len(self.args_list)):
            for j in range(len(self.args_name)):
                if self.args_name[j] not in out_text.keys():
                    out_text[self.args_name[j]] = self.args_list[i][j]
                else:
                    out_text[self.args_name[j]] = out_text[self.args_name[j]] + ',' + self.args_list[i][j]
        # 赋值
        for j,name in enumerate(self.args_name):
            self.input[j].set(out_text[name])
        # 退出
        self.close_window()

    def call_possele(self,target,postype='green'): # target是一个stringVar，pos的
        if postype in ['green','blue','purple','red']:
            self.disable(True)
            get = open_pos_select_window(father=self,image_canvas=self.image_canvas,bgfigure=self.filepath.get(),postype=postype,current_pos=target.get())
            target.set(get) # 设置为的得到的返回值
            self.disable(False)
        else:
            pass
    def bulid_widget(self):
        # 主框体
        frame_group = tk.Frame(self)
        # y轴滚动条
        ybar = ttk.Scrollbar(frame_group,orient='vertical')
        # 表格
        self.args_table = ttk.Treeview(frame_group,columns=self.args_name,show = "headings",selectmode = tk.BROWSE,yscrollcommand=ybar.set)
        ybar.config(command=self.args_table.yview)
        ybar.place(x=295,y=10,height=110,width=15)
        for name in self.args_name:
            self.args_table.column(name,anchor='center',width=285//len(self.input))
            self.args_table.heading(name, text = name)
        self.args_table.bind('<ButtonRelease-1>', self.treeview_click)
        self.args_table.bind('<KeyRelease-Up>', self.treeview_click)
        self.args_table.bind('<KeyRelease-Down>', self.treeview_click)
        self.args_table.place(x=10,y=10,height=110,width=285)
        # 被选中的当前对象
        self.selected = None
        self.value_recode = None
        # 参数选择栏：
        self.frame_args = tk.LabelFrame(frame_group,text='参数')
        for i,name in enumerate(self.args_name):
            ttk.Label(self.frame_args,text=name).place(x=10,y=5+i*30,width=160,height=25)
        if len(self.args_name) == 3:
            # 中
            ttk.Combobox(self.frame_args,textvariable=self.HeaderText,value=self.available_Text).place(x=75,y=5,width=160,height=25)
            ttk.Entry(self.frame_args,textvariable=self.ht_pos).place(x=75,y=35,width=160,height=25)
            ttk.Combobox(self.frame_args,textvariable=self.ht_target,value=self.available_target).place(x=75,y=65,width=160,height=25)
            # 右
            ttk.Label(self.frame_args,text='(选择)',anchor='center').place(x=240,y=5,width=50,height=25)
            ttk.Button(self.frame_args,text='选择',command=lambda:self.call_possele(self.ht_pos,'blue')).place(x=240,y=35,width=50,height=25)
            ttk.Label(self.frame_args,text='(选择)',anchor='center').place(x=240,y=65,width=50,height=25)
        elif len(self.args_name) == 4: # ['关键字','聊天窗气泡','聊天窗头像','聊天窗对齐']
            # 中
            ttk.Entry(self.frame_args,textvariable=self.sub_key).place(x=75,y=5,width=160,height=25)
            ttk.Combobox(self.frame_args,textvariable=self.sub_Bubble,value=self.available_Bubble).place(x=75,y=35,width=160,height=25)
            ttk.Combobox(self.frame_args,textvariable=self.sub_Anime,value=self.available_Anime).place(x=75,y=65,width=160,height=25)
            ttk.Combobox(self.frame_args,textvariable=self.sub_align,values=['left','right']).place(x=75,y=95,width=160,height=25)
            # 右
            ttk.Label(self.frame_args,text='(输入)',anchor='center').place(x=240,y=5,width=50,height=25)
            ttk.Label(self.frame_args,text='(选择)',anchor='center').place(x=240,y=35,width=50,height=25)
            ttk.Label(self.frame_args,text='(选择)',anchor='center').place(x=240,y=65,width=50,height=25)
            ttk.Label(self.frame_args,text='(选择)',anchor='center').place(x=240,y=95,width=50,height=25)
        # self.frame_args.place(x=10,y=120,width=300,height=150)
        # 按钮
        self.add_bubbon = ttk.Button(frame_group,text='添加',command=self.add_key)
        self.update_bubbon = ttk.Button(frame_group,text='更新',command=self.update_value)
        self.add_bubbon.place(x=40,y=275,width=60,height=35)
        ttk.Button(frame_group,text='删除',command=self.del_key).place(x=130,y=275,width=60,height=35)
        ttk.Button(frame_group,text='确定',command=self.comfirm).place(x=220,y=275,width=60,height=35)
        # 放置总框
        frame_group.place(x=10,y=10,width=320,height=320)
        # 更新表格
        self.update_treeview(self.args_list)

# 选择位置窗
def open_pos_select_window(father,image_canvas,bgfigure='',postype='green',current_pos=''):
    def close_window(): # 取消 关闭窗口
        nonlocal posselect_return
        posselect_return = current_pos
        PosSelect_window.destroy()
        PosSelect_window.quit()
    def comfirm_pos(): # 确认
        nonlocal posselect_return
        if postype == 'red':
            posselect_return = str(p_x)
        else:
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
        select_size = select_canvas.size
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
            select_draw.text((p_x,p_y-40),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='blue')
        elif postype=='purple':
            select_draw.line([0,p_y,select_size[0],p_y],fill='purple',width=2)
            select_draw.line([p_x,0,p_x,select_size[1]],fill='purple',width=2)
            select_draw.text((p_x,p_y),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='purple')
        elif postype=='red':
            select_draw.line([p_x,0,p_x,select_size[1]],fill='red',width=2)
            select_draw.text((p_x,0),str(p_x),font=label_pos_show_text,fill='red')
        # 更新到图片上
        select_canvas_show = ImageTk.PhotoImage(select_canvas.resize((can_W,can_H)))
        sele_preview.config(image=select_canvas_show)
    # 载入底图
    if postype=='green': # pos
        fig_W,fig_H = image_canvas.size
        select_canvas = Image.open('./media/canvas.png').crop((0,0,fig_W,fig_H))
        # 叠上预览窗显示的内容（一半透明度）
        preview = image_canvas.copy()
        preview.putalpha(75)
        select_canvas.paste(preview,(0,0),mask=preview)
        try: # 附图
            cursor_figure = Image.open(bgfigure)
            if cursor_figure.mode != 'RGBA': # 如果没有alpha通道
                cursor_figure.putalpha(255)
        except Exception:
            cursor_figure = Image.new(mode='RGBA',size=(1,1),color=(0,0,0,0))
    elif postype in ['blue','purple','red']: # mtpos htpos
        try:
            select_canvas = Image.open(bgfigure)
        except Exception as E:
            # messagebox.showwarning(title='无法载入气泡底图！',message=E)
            fig_W,fig_H = image_canvas.size
            select_canvas = Image.open('./media/canvas.png').crop((0,0,fig_W,fig_H))
            # 叠上预览窗显示的内容（一半透明度）
            preview = image_canvas.copy()
            preview.putalpha(75)
            select_canvas.paste(preview,(0,0),mask=preview)
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
        p_x = int(current_pos)
        p_y = 0
    except ValueError:
        try:
            p_x,p_y = re.findall('\(([\ \d]+),([\ \d]+)\)',current_pos)[0]
            p_x,p_y= int(p_x),int(p_y)
        except Exception:
            p_x,p_y= 0,0
    get_click()
    sele_preview.mainloop()
    return posselect_return

# 媒体定义窗
def open_media_def_window(father,image_canvas,available_Text,available_Pos,available_Bubble,available_Anime,used_variable_name,i_name='',i_type='',i_args=''):
    # 函数正文
    obj_return_value = False
    def show_selected_options(event):
        nonlocal type_display
        type_display.place_forget()
        try:
            select = Mediatype[o_type.get()]
        except KeyError:
            select = Empty_frame
        select.place(x=10,y=40,width=300,height=365)
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
                'volume':volume.get(),'edge_color':edge_color.get(),
                'sub_key':sub_key.get(),'sub_Bubble':sub_Bubble.get(),'sub_Anime':sub_Anime.get(),
                'sub_align':sub_align.get(),'sub_pos':sub_pos.get(),'sub_end':sub_end.get(),
                'am_left':am_left.get(),'am_right':am_right.get(),'sub_distance':sub_distance.get(),
                'label_color':label_color.get()
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
    # 唤起子窗体时，禁用当前窗体
    def self_disable(status):
        if status == True:
            try:
                Objdef_windows.attributes('-disabled', True)
            except Exception:
                pass
        else:
            try:
                Objdef_windows.attributes('-disabled', False)
            except:
                pass
            Objdef_windows.lift()
            Objdef_windows.focus_force()
    def call_possele(target,postype='green'): # target是一个stringVar，pos的
        if postype in ['green','blue','purple','red']:
            self_disable(True)
            get = open_pos_select_window(father=Objdef_windows,image_canvas=image_canvas,bgfigure=filepath.get(),postype=postype,current_pos=target.get())
            target.set(get) # 设置为的得到的返回值
            self_disable(False)
        else:
            pass
    def call_browse_file(target,method='file',filetype=None):
        self_disable(True)
        browse_file(target,method,filetype)
        self_disable(False)
    def call_choose_color(target):
        self_disable(True)
        choose_color(target)
        self_disable(False)
    def call_grouped_args_select(type):
        self_disable(True)
        if type == 'Balloon':
            Grouped_args_select_window(master=Objdef_windows,
                                       input=[Header_Text,ht_pos,ht_target],
                                       available_Text=available_Text,
                                       available_Bubble=available_Bubble,
                                       available_target=available_target,
                                       available_Anime=available_Anime,
                                       filepath=filepath,
                                       image_canvas=image_canvas)
        else:
            Grouped_args_select_window(master=Objdef_windows,
                                       input=[sub_key,sub_Bubble,sub_Anime,sub_align],
                                       available_Text=available_Text,
                                       available_Bubble=available_Bubble,
                                       available_target=available_target,
                                       available_Anime=available_Anime,
                                       filepath=filepath,
                                       image_canvas=image_canvas)
        self_disable(False)

    Objdef_windows = tk.Toplevel(father)
    Objdef_windows.resizable(0,0)
    Objdef_windows.geometry("340x505")
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
    objdef.place(x=10,y=10,height=485,width=320)

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
        'Animation':"(filepath='{filepath}',pos={pos},tick={tick},loop={loop},label_color='{label_color}')",
        'Background':"(filepath='{filepath}',pos={pos},label_color='{label_color}')",
        'Bubble':"(filepath='{filepath}',Main_Text={Main_Text},Header_Text={Header_Text},pos={pos},mt_pos={mt_pos},ht_pos={ht_pos},ht_target={ht_target},align='{align}',line_distance={line_distance},label_color='{label_color}')",
        'Balloon':"(filepath='{filepath}',Main_Text={Main_Text},Header_Text=[{Header_Text}],pos={pos},mt_pos={mt_pos},ht_pos=[{ht_pos}],ht_target=[{ht_target}],align='{align}',line_distance={line_distance},label_color='{label_color}')",
        'DynamicBubble':"(filepath='{filepath}',Main_Text={Main_Text},Header_Text={Header_Text},pos={pos},mt_pos={mt_pos},mt_end={mt_end},ht_pos={ht_pos},ht_target={ht_target},fill_mode='{fill_mode}',line_distance={line_distance},label_color='{label_color}')",
        'ChatWindow':"(filepath='{filepath}',sub_key=[{sub_key}],sub_Bubble=[{sub_Bubble}],sub_Anime=[{sub_Anime}],sub_align=[{sub_align}],pos={pos},sub_pos={sub_pos},sub_end={sub_end},am_left={am_left},am_right={am_right},sub_distance={sub_distance},label_color='{label_color}')",
        'Audio':"(filepath='{filepath}',label_color='{label_color}')",
        'BGM':"(filepath='{filepath}',volume={volume},loop={loop},label_color='{label_color}')"
    }

    available_target = ["'Name'","'Subtype'","'Animation'","'Bubble'","'Voice'","'SpeechRate'","'PitchRate'"]

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
    ChatWindow_frame = tk.LabelFrame(objdef,text='ChatWindow参数')
    # 新增：
    # typedi
    Mediatype = {'Pos':Pos_frame,'FreePos':FreePos_frame,'PosGrid':PosGrid_frame,
                 'Text':Text_frame,'StrokeText':StrokeText_frame,
                 'Bubble':Bubble_frame,'Balloon':Balloon_frame,'DynamicBubble':DynamicBubble_frame,'ChatWindow':ChatWindow_frame,
                 'Background':Background_frame,
                 'Animation':Animation_frame,
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
    sub_key = tk.StringVar(Objdef_windows)
    sub_Bubble = tk.StringVar(Objdef_windows)
    sub_Anime = tk.StringVar(Objdef_windows)
    sub_align = tk.StringVar(Objdef_windows)
    sub_pos = tk.StringVar(Objdef_windows)
    sub_end = tk.StringVar(Objdef_windows)
    am_left = tk.IntVar(Objdef_windows)
    am_right = tk.IntVar(Objdef_windows)
    sub_distance = tk.IntVar(Objdef_windows)
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
    mt_end.set('(0,0)')
    ht_target.set("'Name'") ################BUG in Balloon
    fill_mode.set('stretch')
    sub_key.set("'Key'")
    sub_Bubble.set('Bubble()')
    sub_Anime.set('')
    sub_align.set("'left'")
    sub_pos.set('(0,0)')
    sub_end.set('(0,0)')
    am_left.set('0')
    am_right.set('0')
    sub_distance.set('50')
    label_color.set('Lavender')
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
                            'ChatWindow':['filepath','sub_key','sub_Bubble','sub_Anime','sub_align','pos','sub_pos','sub_end','am_left','am_right','sub_distance','label_color'],
                            'Background':['filepath','pos','label_color'],
                            'Animation':['filepath','pos','tick','loop','label_color'],
                            'Audio':['filepath','label_color'],
                            'BGM':['filepath','volume','loop','label_color']}

    #初始状态 空白或者选中
    if i_type == '':
        Empty_frame.place(x=10,y=40,width=300,height=365)
        type_display = Empty_frame
    elif i_type in [Pos,FreePos]:
        Mediatype[i_type].place(x=10,y=40,width=300,height=365)
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
        Mediatype[i_type].place(x=10,y=40,width=300,height=365)
        type_display = Mediatype[i_type]
        for i,arg in enumerate(RE_mediadef_args.findall(i_args)):
            keyword,value = arg
            if keyword == '':
                keyword = type_keyword_position[i_type][i]
            if (keyword!='ht_target')&((('"' == value[0]) & ('"' == value[-1]))|(("'" == value[0]) & ("'" == value[-1]))):
            # 如果是双引号括起来的路径，但是ht_target除外（很不优雅）
                exec('{0}.set({1})'.format(keyword,value))
            elif ('[' == value[0]) & (']' == value[-1]): # 如果是方括号括起来的列表
                exec('{0}.set("{1}")'.format(keyword,value[1:-1]))
            else:
                eval(keyword).set(value)
                # exec('{0}.set("{1}")'.format(keyword,value))
    # Pos_frame
    ttk.Label(Pos_frame,text='位置').place(x=10,y=10,width=65,height=25)
    ttk.Entry(Pos_frame,textvariable=pos).place(x=75,y=10,width=160,height=25)
    ttk.Button(Pos_frame,text='选择',command=lambda:call_possele(pos,'green')).place(x=240,y=10,width=50,height=25)
    # FreePos_frame
    ttk.Label(FreePos_frame,text='初始位置').place(x=10,y=10,width=65,height=25)
    ttk.Entry(FreePos_frame,textvariable=pos).place(x=75,y=10,width=160,height=25)
    ttk.Button(FreePos_frame,text='选择',command=lambda:call_possele(pos,'green')).place(x=240,y=10,width=50,height=25)
    # PosGrid_frame
    ttk.Label(PosGrid_frame,text='网格起点').place(x=10,y=10,width=65,height=25)
    ttk.Label(PosGrid_frame,text='网格终点').place(x=10,y=40,width=65,height=25)
    ttk.Label(PosGrid_frame,text='X轴格数').place(x=10,y=70,width=65,height=25)
    ttk.Label(PosGrid_frame,text='Y轴格数').place(x=10,y=100,width=65,height=25)
    ttk.Entry(PosGrid_frame,textvariable=pos).place(x=75,y=10,width=160,height=25)
    ttk.Entry(PosGrid_frame,textvariable=end).place(x=75,y=40,width=160,height=25)
    ttk.Entry(PosGrid_frame,textvariable=x_step).place(x=75,y=70,width=160,height=25)
    ttk.Entry(PosGrid_frame,textvariable=y_step).place(x=75,y=100,width=160,height=25)
    ttk.Button(PosGrid_frame,text='选择',command=lambda:call_possele(pos,'purple')).place(x=240,y=10,width=50,height=25)
    ttk.Button(PosGrid_frame,text='选择',command=lambda:call_possele(end,'purple')).place(x=240,y=40,width=50,height=25)
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
    ttk.Button(Text_frame,text='浏览',command=lambda:call_browse_file(fontfile,'file',filetype='fontfile')).place(x=240,y=10,width=50,height=25)
    ttk.Label(Text_frame,text='(整数)',anchor='center').place(x=240,y=40,width=50,height=25)
    ttk.Button(Text_frame,text='选择',command=lambda:call_choose_color(color)).place(x=240,y=70,width=50,height=25)
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
    ttk.Button(StrokeText_frame,text='浏览',command=lambda:call_browse_file(fontfile,'file',filetype='fontfile')).place(x=240,y=10,width=50,height=25)
    ttk.Label(StrokeText_frame,text='(整数)',anchor='center').place(x=240,y=40,width=50,height=25)
    ttk.Button(StrokeText_frame,text='选择',command=lambda:call_choose_color(color)).place(x=240,y=70,width=50,height=25)
    ttk.Label(StrokeText_frame,text='(整数)',anchor='center').place(x=240,y=100,width=50,height=25)
    ttk.Button(StrokeText_frame,text='选择',command=lambda:call_choose_color(edge_color)).place(x=240,y=130,width=50,height=25)

    # Bubble_frame
    # 左
    ttk.Label(Bubble_frame,text='底图文件').place(x=10,y=10,width=65,height=25)
    ttk.Label(Bubble_frame,text='底图位置').place(x=10,y=40,width=65,height=25)
    ttk.Label(Bubble_frame,text='头文本字体').place(x=10,y=70,width=65,height=25)
    ttk.Label(Bubble_frame,text='头文本位置').place(x=10,y=100,width=65,height=25)
    ttk.Label(Bubble_frame,text='头文本目标').place(x=10,y=130,width=65,height=25)
    ttk.Label(Bubble_frame,text='主文本字体').place(x=10,y=160,width=65,height=25)
    ttk.Label(Bubble_frame,text='主文本位置').place(x=10,y=190,width=65,height=25)
    ttk.Label(Bubble_frame,text='主文本行距').place(x=10,y=220,width=65,height=25)
    ttk.Label(Bubble_frame,text='对齐模式').place(x=10,y=250,width=65,height=25)
    # 中
    ttk.Entry(Bubble_frame,textvariable=filepath).place(x=75,y=10,width=160,height=25)
    ttk.Combobox(Bubble_frame,textvariable=pos,value=available_Pos).place(x=75,y=40,width=160,height=25)
    ttk.Combobox(Bubble_frame,textvariable=Header_Text,value=available_Text).place(x=75,y=70,width=160,height=25)
    ttk.Entry(Bubble_frame,textvariable=ht_pos).place(x=75,y=100,width=160,height=25)
    ttk.Combobox(Bubble_frame,textvariable=ht_target,values=available_target).place(x=75,y=130,width=160,height=25)
    ttk.Combobox(Bubble_frame,textvariable=Main_Text,value=available_Text).place(x=75,y=160,width=160,height=25)
    ttk.Entry(Bubble_frame,textvariable=mt_pos).place(x=75,y=190,width=160,height=25)
    ttk.Entry(Bubble_frame,textvariable=line_distance).place(x=75,y=220,width=160,height=25)
    ttk.Combobox(Bubble_frame,textvariable=align,value=['left','center']).place(x=75,y=250,width=160,height=25)
    # 右
    ttk.Button(Bubble_frame,text='浏览',command=lambda:call_browse_file(filepath,'file',filetype='picture')).place(x=240,y=10,width=50,height=25) # filepath
    ttk.Button(Bubble_frame,text='选择',command=lambda:call_possele(pos,'green')).place(x=240,y=40,width=50,height=25) # pos
    ttk.Label(Bubble_frame,text='(选择)',anchor='center').place(x=240,y=70,width=50,height=25) # HeaderText
    ttk.Button(Bubble_frame,text='选择',command=lambda:call_possele(ht_pos,'blue')).place(x=240,y=100,width=50,height=25) # ht_pos
    ttk.Label(Bubble_frame,text='(选择)',anchor='center').place(x=240,y=130,width=50,height=25) # ht_target
    ttk.Label(Bubble_frame,text='(选择)',anchor='center').place(x=240,y=160,width=50,height=25) # MainText
    ttk.Button(Bubble_frame,text='选择',command=lambda:call_possele(mt_pos,'blue')).place(x=240,y=190,width=50,height=25) # mt_pos
    ttk.Label(Bubble_frame,text='(小数)',anchor='center').place(x=240,y=220,width=50,height=25) # line_distance
    ttk.Label(Bubble_frame,text='(选择)',anchor='center').place(x=240,y=250,width=50,height=25) # align

    # Balloon_frame
    # 左
    ttk.Label(Balloon_frame,text='底图文件').place(x=10,y=10,width=65,height=25)
    ttk.Label(Balloon_frame,text='底图位置').place(x=10,y=40,width=65,height=25)
    ttk.Label(Balloon_frame,text='头文本字体').place(x=10,y=70,width=65,height=25)
    ttk.Label(Balloon_frame,text='头文本位置').place(x=10,y=100,width=65,height=25)
    ttk.Label(Balloon_frame,text='头文本目标').place(x=10,y=130,width=65,height=25)
    ttk.Label(Balloon_frame,text='主文本字体').place(x=10,y=160,width=65,height=25)
    ttk.Label(Balloon_frame,text='主文本位置').place(x=10,y=190,width=65,height=25)
    ttk.Label(Balloon_frame,text='主文本行距').place(x=10,y=220,width=65,height=25)
    ttk.Label(Balloon_frame,text='对齐模式').place(x=10,y=250,width=65,height=25)
    # 中
    ttk.Entry(Balloon_frame,textvariable=filepath).place(x=75,y=10,width=160,height=25)
    ttk.Combobox(Balloon_frame,textvariable=pos,value=available_Pos).place(x=75,y=40,width=160,height=25)
    ttk.Entry(Balloon_frame,textvariable=Header_Text).place(x=75,y=70,width=160,height=25)
    ttk.Entry(Balloon_frame,textvariable=ht_pos).place(x=75,y=100,width=160,height=25)
    ttk.Entry(Balloon_frame,textvariable=ht_target).place(x=75,y=130,width=160,height=25)
    ttk.Combobox(Balloon_frame,textvariable=Main_Text,value=available_Text).place(x=75,y=160,width=160,height=25)
    ttk.Entry(Balloon_frame,textvariable=mt_pos).place(x=75,y=190,width=160,height=25)
    ttk.Entry(Balloon_frame,textvariable=line_distance).place(x=75,y=220,width=160,height=25)
    ttk.Combobox(Balloon_frame,textvariable=align,value=['left','center']).place(x=75,y=250,width=160,height=25)
    # 右
    ttk.Button(Balloon_frame,text='浏览',command=lambda:call_browse_file(filepath,'file',filetype='picture')).place(x=240,y=10,width=50,height=25) # filepath
    ttk.Button(Balloon_frame,text='选择',command=lambda:call_possele(pos,'green')).place(x=240,y=40,width=50,height=25) # pos
    ttk.Button(Balloon_frame,text='选择',command=lambda:call_grouped_args_select('Balloon')).place(x=240,y=70,width=50,height=85) # HeaderText
    # ttk.Button(Balloon_frame,text='选择',command=lambda:call_possele(ht_pos)).place(x=240,y=100,width=50,height=25) # ht_pos
    # ttk.Label(Balloon_frame,text='(选择)',anchor='center').place(x=240,y=130,width=50,height=25) # ht_target
    ttk.Label(Balloon_frame,text='(选择)',anchor='center').place(x=240,y=160,width=50,height=25) # MainText
    ttk.Button(Balloon_frame,text='选择',command=lambda:call_possele(mt_pos,'blue')).place(x=240,y=190,width=50,height=25) # mt_pos
    ttk.Label(Balloon_frame,text='(小数)',anchor='center').place(x=240,y=220,width=50,height=25) # line_distance
    ttk.Label(Balloon_frame,text='(选择)',anchor='center').place(x=240,y=250,width=50,height=25) # align

    # DynamicBubble_frame
    # 左
    ttk.Label(DynamicBubble_frame,text='底图文件').place(x=10,y=10,width=65,height=25)
    ttk.Label(DynamicBubble_frame,text='底图位置').place(x=10,y=40,width=65,height=25)
    ttk.Label(DynamicBubble_frame,text='头文本字体').place(x=10,y=70,width=65,height=25)
    ttk.Label(DynamicBubble_frame,text='头文本位置').place(x=10,y=100,width=65,height=25)
    ttk.Label(DynamicBubble_frame,text='头文本目标').place(x=10,y=130,width=65,height=25)
    ttk.Label(DynamicBubble_frame,text='主文本字体').place(x=10,y=160,width=65,height=25)
    ttk.Label(DynamicBubble_frame,text='主文本起点').place(x=10,y=190,width=65,height=25)
    ttk.Label(DynamicBubble_frame,text='主文本终点').place(x=10,y=220,width=65,height=25)
    ttk.Label(DynamicBubble_frame,text='主文本行距').place(x=10,y=250,width=65,height=25)
    ttk.Label(DynamicBubble_frame,text='填充模式').place(x=10,y=280,width=65,height=25)
    # 中
    ttk.Entry(DynamicBubble_frame,textvariable=filepath).place(x=75,y=10,width=160,height=25)
    ttk.Combobox(DynamicBubble_frame,textvariable=pos,value=available_Pos).place(x=75,y=40,width=160,height=25)
    ttk.Combobox(DynamicBubble_frame,textvariable=Header_Text,value=available_Text).place(x=75,y=70,width=160,height=25)
    ttk.Entry(DynamicBubble_frame,textvariable=ht_pos).place(x=75,y=100,width=160,height=25)
    ttk.Combobox(DynamicBubble_frame,textvariable=ht_target,values=available_target).place(x=75,y=130,width=160,height=25)
    ttk.Combobox(DynamicBubble_frame,textvariable=Main_Text,value=available_Text).place(x=75,y=160,width=160,height=25)
    ttk.Entry(DynamicBubble_frame,textvariable=mt_pos).place(x=75,y=190,width=160,height=25)
    ttk.Entry(DynamicBubble_frame,textvariable=mt_end).place(x=75,y=220,width=160,height=25)
    ttk.Entry(DynamicBubble_frame,textvariable=line_distance).place(x=75,y=250,width=160,height=25)
    ttk.Combobox(DynamicBubble_frame,textvariable=fill_mode,value=['stretch','collage']).place(x=75,y=280,width=160,height=25)
    # 右
    ttk.Button(DynamicBubble_frame,text='浏览',command=lambda:call_browse_file(filepath,'file',filetype='picture')).place(x=240,y=10,width=50,height=25) # filepath
    ttk.Button(DynamicBubble_frame,text='选择',command=lambda:call_possele(pos,'green')).place(x=240,y=40,width=50,height=25) # pos
    ttk.Label(DynamicBubble_frame,text='(选择)',anchor='center').place(x=240,y=70,width=50,height=25) # HeaderText
    ttk.Button(DynamicBubble_frame,text='选择',command=lambda:call_possele(ht_pos,'blue')).place(x=240,y=100,width=50,height=25) # ht_pos
    ttk.Label(DynamicBubble_frame,text='(选择)',anchor='center').place(x=240,y=130,width=50,height=25) # ht_target
    ttk.Label(DynamicBubble_frame,text='(选择)',anchor='center').place(x=240,y=160,width=50,height=25) # MainText
    ttk.Button(DynamicBubble_frame,text='选择',command=lambda:call_possele(mt_pos,'purple')).place(x=240,y=190,width=50,height=25) # mt_pos
    ttk.Button(DynamicBubble_frame,text='选择',command=lambda:call_possele(mt_end,'purple')).place(x=240,y=220,width=50,height=25) # mt_end
    ttk.Label(DynamicBubble_frame,text='(小数)',anchor='center').place(x=240,y=250,width=50,height=25) # line_distance
    ttk.Label(DynamicBubble_frame,text='(选择)',anchor='center').place(x=240,y=280,width=50,height=25) # align

    # ChatWindow_frame
    # 左
    ttk.Label(ChatWindow_frame,text='底图文件').place(x=10,y=10,width=65,height=25)
    ttk.Label(ChatWindow_frame,text='底图位置').place(x=10,y=40,width=65,height=25)
    ttk.Label(ChatWindow_frame,text='关键字').place(x=10,y=70,width=65,height=25)
    ttk.Label(ChatWindow_frame,text='聊天窗气泡').place(x=10,y=100,width=65,height=25)
    ttk.Label(ChatWindow_frame,text='聊天窗头像').place(x=10,y=130,width=65,height=25)
    ttk.Label(ChatWindow_frame,text='聊天窗对齐').place(x=10,y=160,width=65,height=25)
    ttk.Label(ChatWindow_frame,text='子气泡起点').place(x=10,y=190,width=65,height=25)
    ttk.Label(ChatWindow_frame,text='子气泡终点').place(x=10,y=220,width=65,height=25)
    ttk.Label(ChatWindow_frame,text='头像左边界').place(x=10,y=250,width=65,height=25)
    ttk.Label(ChatWindow_frame,text='头像右边界').place(x=10,y=280,width=65,height=25)
    ttk.Label(ChatWindow_frame,text='子气泡间距').place(x=10,y=310,width=65,height=25)
    # 中
    ttk.Entry(ChatWindow_frame,textvariable=filepath).place(x=75,y=10,width=160,height=25)
    ttk.Combobox(ChatWindow_frame,textvariable=pos,value=available_Pos).place(x=75,y=40,width=160,height=25)
    ttk.Entry(ChatWindow_frame,textvariable=sub_key).place(x=75,y=70,width=160,height=25)
    ttk.Entry(ChatWindow_frame,textvariable=sub_Bubble).place(x=75,y=100,width=160,height=25)
    ttk.Entry(ChatWindow_frame,textvariable=sub_Anime).place(x=75,y=130,width=160,height=25)
    ttk.Entry(ChatWindow_frame,textvariable=sub_align).place(x=75,y=160,width=160,height=25)
    ttk.Entry(ChatWindow_frame,textvariable=sub_pos).place(x=75,y=190,width=160,height=25)
    ttk.Entry(ChatWindow_frame,textvariable=sub_end).place(x=75,y=220,width=160,height=25)
    ttk.Entry(ChatWindow_frame,textvariable=am_left).place(x=75,y=250,width=160,height=25)
    ttk.Entry(ChatWindow_frame,textvariable=am_right).place(x=75,y=280,width=160,height=25)
    ttk.Entry(ChatWindow_frame,textvariable=sub_distance).place(x=75,y=310,width=160,height=25)
    # 右
    ttk.Button(ChatWindow_frame,text='浏览',command=lambda:call_browse_file(filepath,'file',filetype='picture')).place(x=240,y=10,width=50,height=25) # filepath
    ttk.Button(ChatWindow_frame,text='选择',command=lambda:call_possele(pos,'green')).place(x=240,y=40,width=50,height=25) # pos
    ttk.Button(ChatWindow_frame,text='选择',command=lambda:call_grouped_args_select('ChatWindow')).place(x=240,y=70,width=50,height=115)# sub_key
    # ttk.Button(ChatWindow_frame,text='选择',command=lambda:call_possele(ht_pos)).place(x=240,y=100,width=50,height=25) # sub_Bubble
    # ttk.Label(ChatWindow_frame,text='(选择)',anchor='center').place(x=240,y=130,width=50,height=25) # sub_Anime
    # ttk.Label(ChatWindow_frame,text='(选择)',anchor='center').place(x=240,y=160,width=50,height=25) # sub_align
    ttk.Button(ChatWindow_frame,text='选择',command=lambda:call_possele(sub_pos,'purple')).place(x=240,y=190,width=50,height=25) # sub_pos
    ttk.Button(ChatWindow_frame,text='选择',command=lambda:call_possele(sub_end,'purple')).place(x=240,y=220,width=50,height=25) # sub_end
    ttk.Button(ChatWindow_frame,text='选择',command=lambda:call_possele(am_left,'red')).place(x=240,y=250,width=50,height=25) # am_left
    ttk.Button(ChatWindow_frame,text='选择',command=lambda:call_possele(am_right,'red')).place(x=240,y=280,width=50,height=25) # am_right
    ttk.Label(ChatWindow_frame,text='(整数)',anchor='center').place(x=240,y=310,width=50,height=25) # sub_distance

    # Background
    ttk.Label(Background_frame,text='背景文件').place(x=10,y=10,width=65,height=25)
    ttk.Label(Background_frame,text='背景位置').place(x=10,y=40,width=65,height=25)
    ttk.Entry(Background_frame,textvariable=filepath).place(x=75,y=10,width=160,height=25)
    ttk.Combobox(Background_frame,textvariable=pos,value=available_Pos).place(x=75,y=40,width=160,height=25)
    ttk.Button(Background_frame,text='浏览',command=lambda:call_browse_file(filepath,'file',filetype='picture')).place(x=240,y=10,width=50,height=25)
    ttk.Button(Background_frame,text='选择',command=lambda:call_possele(pos,'green')).place(x=240,y=40,width=50,height=25)

    # Animation
    ttk.Label(Animation_frame,text='立绘文件').place(x=10,y=10,width=65,height=25)
    ttk.Label(Animation_frame,text='立绘位置').place(x=10,y=40,width=65,height=25)
    ttk.Label(Animation_frame,text='动画时刻').place(x=10,y=70,width=65,height=25)
    ttk.Label(Animation_frame,text='动画循环').place(x=10,y=100,width=65,height=25)
    ttk.Entry(Animation_frame,textvariable=filepath).place(x=75,y=10,width=160,height=25)
    ttk.Combobox(Animation_frame,textvariable=pos,value=available_Pos).place(x=75,y=40,width=160,height=25)
    ttk.Entry(Animation_frame,textvariable=tick).place(x=75,y=70,width=160,height=25)
    ttk.Entry(Animation_frame,textvariable=loop).place(x=75,y=100,width=160,height=25)
    ttk.Button(Animation_frame,text='浏览',command=lambda:call_browse_file(filepath,'file',filetype='picture')).place(x=240,y=10,width=50,height=25)
    ttk.Button(Animation_frame,text='选择',command=lambda:call_possele(pos,'green')).place(x=240,y=40,width=50,height=25)
    ttk.Label(Animation_frame,text='(整数)',anchor='center').place(x=240,y=70,width=50,height=25)
    ttk.Label(Animation_frame,text='(0/1)',anchor='center').place(x=240,y=100,width=50,height=25)

    # BGM
    ttk.Label(BGM_frame,text='音乐文件').place(x=10,y=10,width=65,height=25)
    ttk.Label(BGM_frame,text='音乐音量').place(x=10,y=40,width=65,height=25)
    ttk.Label(BGM_frame,text='音乐循环').place(x=10,y=70,width=65,height=25)
    ttk.Entry(BGM_frame,textvariable=filepath).place(x=75,y=10,width=160,height=25)
    ttk.Entry(BGM_frame,textvariable=volume).place(x=75,y=40,width=160,height=25)
    ttk.Entry(BGM_frame,textvariable=loop).place(x=75,y=70,width=160,height=25)
    ttk.Button(BGM_frame,text='浏览',command=lambda:call_browse_file(filepath,'file',filetype='BGM')).place(x=240,y=10,width=50,height=25)
    ttk.Label(BGM_frame,text='(0-100)',anchor='center').place(x=240,y=40,width=50,height=25)
    ttk.Label(BGM_frame,text='(0/1)',anchor='center').place(x=240,y=70,width=50,height=25)

    # Audio_frame
    ttk.Label(Audio_frame,text='音效文件').place(x=10,y=10,width=65,height=25)
    ttk.Entry(Audio_frame,textvariable=filepath).place(x=75,y=10,width=160,height=25)
    ttk.Button(Audio_frame,text='浏览',command=lambda:call_browse_file(filepath,'file',filetype='soundeff')).place(x=240,y=10,width=50,height=25)

    # 标签颜色 colabel
    label_label_color = tk.Label(objdef,text='▉标签颜色',fg=available_label_color[label_color.get()],bg='#262626')
    label_label_color.place(x=22,y=410,width=62,height=25)
    choose_labelcolor = ttk.Combobox(objdef,textvariable=label_color,value=list(available_label_color.keys()))
    choose_labelcolor.place(x=87,y=410,width=160,height=25)
    choose_labelcolor.bind("<<ComboboxSelected>>",lambda event: label_label_color.config(fg=available_label_color[label_color.get()]))
    ttk.Label(objdef,text='(选择)',anchor='center').place(x=252,y=410,width=50,height=25)
    

    # 完成
    ttk.Button(objdef,text='确认',command=comfirm_obj).place(x=130,y=445,height=30,width=50)

    Objdef_windows.mainloop()
    return obj_return_value

