#!/usr/bin/env python
# coding: utf-8

import ttkbootstrap as ttk
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.toast import ToastNotification
import tkinter as tk
from PIL import Image, ImageTk
from .GUI_DialogWindow import color_chooser, browse_file
from .Boardcast import BoardcastHandler
from .ProjConfig import preference
from .GUI_Link import Link

# 公用小元件
# 滚动得更加流畅的scollframe
class FluentFrame(ScrolledFrame):
    # 重载 yview_scroll
    def yview_scroll(self, number: int, what: str):
        """Update the vertical position of the content frame within the
        container.

        Parameters:

            number (int):
                The amount by which the content frame will be moved
                within the container frame by 'what' units.

            what (str):
                The type of units by which the number is to be interpeted.
                This parameter is currently not used and is assumed to be
                'units'.
        """
        base, thumb = self._measures()
        first, _ = self.vscroll.get()
        fraction = (number / (base*10)) + first
        self.yview_moveto(fraction)

# 可以自由指定显示位置的tooltip
class FreeToolTip(ToolTip):
    def __init__(self, widget, text="widget info", bootstyle=None, wraplength=None, delay=250, side='right', screenzoom=1.0, **kwargs):
        super().__init__(widget, text, bootstyle, wraplength, delay, **kwargs)
        # 位置
        self.side = side
        self.sz = screenzoom
    def show_tip(self, *_):
        """Create a show the tooltip window"""
        if self.toplevel:
            return
        SZ_25 = int(self.sz * 25)
        SZ_50 = 2 * SZ_25
        SZ_100 = 2 * SZ_50
        SZ_10 = int(self.sz * 10)
        if self.side == 'right':
            self.tx = SZ_25
            self.ty = SZ_10
        elif self.side == 'up':
            self.tx =  SZ_10
            self.ty = -SZ_50
        elif self.side == 'left':
            self.tx = -SZ_100
            self.ty = -SZ_10
        self.toplevel = ttk.Toplevel(
            position=(
                self.widget.winfo_pointerx() + self.tx,
                self.widget.winfo_pointery() + self.ty
            ),
            **self.toplevel_kwargs
        )
        lbl = ttk.Label(
            master=self.toplevel,
            text=self.text,
            justify='left',
            wraplength=self.wraplength,
            padding=10,
        )
        lbl.pack(fill='both', expand=True)
        if self.bootstyle:
            lbl.configure(bootstyle=self.bootstyle)
        else:
            lbl.configure(style="tooltip.TLabel")
    def move_tip(self, *_):
        """Move the tooltip window to the current mouse position within the
        widget.
        """
        if self.toplevel:
            x = self.widget.winfo_pointerx() + self.tx
            y = self.widget.winfo_pointery() + self.ty
            self.toplevel.geometry(f"+{x}+{y}")
# 加上值的映射关系的Combobox\
class DictCombobox(ttk.Combobox):
    def __init__(self, master,textvariable,**kw):
        self.dictionary = {}
        # 实际的值
        self.var = textvariable
        self.var_update_text = True
        self.var.trace_variable("w", self.update_text) # 检查是否发生了变更，如果变更了则刷新text
        # 显示的
        self.text = tk.StringVar(master=master,value=self.var.get())
        # 初始化
        super().__init__(master, textvariable=self.text, **kw)
        self.combox_state = 'normal'
        self.bind('<<ComboboxSelected>>', self.update_var)
        self.bind('<KeyRelease>',self.update_var)
    def update_dict(self, dict:dict):
        # 显示的内容：实际的内容
        self.dictionary = dict
        self.configure(values=list(self.dictionary.keys()), state='readonly')
        self.combox_state = 'readonly'
        # 修改目前text
        self.set_dictionary_text()
    def update_var(self, event):
        # 禁用 update_text
        self.var_update_text = False
        # 获取当前 text
        text = self.text.get()
        if text in self.dictionary:
            self.var.set(self.dictionary[text])
        else:
            self.var.set(text)
        # 重新启用 update_text
        self.var_update_text = True
    # 从被修改的self.var里更新显示的文本
    def update_text(self, *args):
        if self.var_update_text:
            var = self.var.get()
            self.text.set(var)
            self.set_dictionary_text()
    # 从var更新dictionary.text
    def set_dictionary_text(self):
        keys = [key for key,value in self.dictionary.items() if tk.StringVar(value=value).get() == self.text.get()]
        if len(keys) > 0:
            self.text.set(keys[0])
# 一个键、值、描述的最小单位。
class KeyValueDescribe(ttk.Frame):
    def __init__(self,master,screenzoom:float,key:str,value:dict,describe:dict,tooltip:str=None,callback=None):
        self.sz = screenzoom
        super().__init__(master=master)
        SZ_5 = int(self.sz * 5)
        padding = (0,SZ_5,0,SZ_5)
        # 当前
        # 数值类型
        if value['type'] == 'int':
            self.value = tk.IntVar(master=self,value=value['value'])
        elif value['type'] == 'float':
            self.value = tk.DoubleVar(master=self,value=value['value'])
        elif value['type'] == 'bool':
            self.value = tk.BooleanVar(master=self,value=value['value'])
        elif value['type'] == 'str':
            self.value = tk.StringVar(master=self,value=value['value'])
        else:
            self.value = tk.StringVar(master=self,value=value['value'])
        # 数值受到更改
        # self.value.trace_variable("w", self.config_content) # 检查是否发生了变更，如果变更了则刷新text
        self.callback = callback
        # 关键字
        self.key = ttk.Label(master=self,text=key,width=8,anchor='e',padding=padding)
        if tooltip is not None:
            self.tooltip = ToolTip(widget=self.key,text=tooltip,bootstyle='light-inverse')
        # 容器
        if value['style'] == 'entry':
            self.input = ttk.Entry(master=self,textvariable=self.value,width=30)
            self.input.bind("<FocusOut>",self.config_content,'+')
        elif value['style'] == 'spine':
            self.input = ttk.Spinbox(master=self,textvariable=self.value,width=30,command=self.config_content)
        elif value['style'] == 'combox':
            self.input = DictCombobox(master=self,textvariable=self.value,width=30)
            self.input.bind("<<ComboboxSelected>>",self.config_content,'+')
        elif value['style'] == 'label':
            self.input = ttk.Label(master=self,textvariable=self.value,width=30)
        else:
            self.input = ttk.Label(master=self,textvariable=self.value,width=30)
        # 通用的，按回车键刷新
        self.input.bind("<Return>",self.config_content)
        # 描述
        if describe['type'] == 'label':
            self.describe = ttk.Label(master=self,text=describe['text'],width=8,anchor='center',padding=padding)
        elif describe['type'] == 'button':
            self.describe = ttk.Button(master=self,text=describe['text'],width=8,padding=padding)
        else:
            self.describe = ttk.Label(master=self,text=describe['text'],width=8,anchor='center',padding=padding)
        # 显示
        self.update_item()
    def update_item(self):
        SZ_5 = int(self.sz * 5)
        # 放置
        self.key.pack(fill='none',side='left',padx=SZ_5)
        self.input.pack(fill='x',side='left',padx=SZ_5,expand=True)
        self.describe.pack(fill='none',side='left',padx=SZ_5)
    def config_content(self, *args):
        print(args)
        # 回调函数
        if self.callback:
            self.callback()
        # 清除焦点
        if args:
            try:
                if args[0].keysym == 'Return':
                    self.describe.focus_set()
            except:
                pass
    def get(self):
        return self.value.get()
    def set(self,value):
        return self.value.set(value)
    def bind_button(self,dtype='picture-file',quote=True,related=True,convert=False):
        if type(self.describe) != ttk.Button:
            return
        def command():
            if dtype == 'dir':
                browse_file(master=self.winfo_toplevel(), text_obj=self.value, method='dir', filetype=None, quote=quote, related=related)
            elif 'file' in dtype:
                filetype = dtype.split('-')[0]
                browse_file(master=self.winfo_toplevel(), text_obj=self.value, method='file', filetype=filetype, quote=quote, related=related, convert=convert)
            elif 'color' in dtype:
                color_chooser(master=self.winfo_toplevel(), text_obj=self.value)
            # 更新
            self.config_content()
        self.describe.configure(command=command)
    def disable(self):
        self.input.configure(state='disable')
        self.describe.configure(state='disable')
    def enable(self):
        if type(self.input) is DictCombobox:
            self.input.configure(state=self.input.combox_state)
        else:
            self.input.configure(state='normal')
        self.describe.configure(state='normal')
    def enable_trace(self):
        if type(self.input) is ttk.Entry:
            self.input.unbind("<FocusOut>")
            self.input.bind("<Return>",self.clear_trace,'+')
            self.value.trace(mode='w',callback=self.show_trace)
        else:
            pass
    def show_trace(self,*args):
        self.input.configure(bootstyle='danger')
    def clear_trace(self,event):
        self.input.configure(bootstyle='primary')
# 一个比上面的KVD更详细的最小单位，常用于设置
class DetailedKeyValueDescribe(KeyValueDescribe):
    def __init__(self,master,screenzoom:float,key:str,value:dict,describe:dict,tooltip:str=None,callback=None):
        super().__init__(master=master,screenzoom=screenzoom,key=key,value=value,describe=describe,tooltip=None,callback=callback)
        SZ_5 = int(self.sz * 5)
        padding = (0,SZ_5,0,SZ_5)
        if preference.theme == 'rplgenlight':
            self.key.configure(
                font=(Link['system_font_family'], 11, "bold"),
                foreground='#000000',
                anchor='w',
                width=30
            )
            self.tooltip = ttk.Label(master=self,text=tooltip,anchor='w',padding=padding,foreground='#888888')
        else:
            self.key.configure(
                font=(Link['system_font_family'], 11, "bold"),
                foreground='#eeeeee',
                anchor='w',
                width=30
            )
            self.tooltip = ttk.Label(master=self,text=tooltip,anchor='w',padding=padding,foreground='#aaaaaa')
        self.sideshow = ttk.Frame(master=self, bootstyle='secondary')
        self.update_item_delay()
    def update_item(self):
        # 把super的update_item无效化
        pass
    def update_item_delay(self):
        # 重做的update_item
        SZ_5 = int(self.sz * 5)
        SZ_2 = int(self.sz * 1)
        SZ_10 = int(self.sz * 10)
        # 放置
        self.key.pack(fill='x',side='top',padx=(SZ_10, SZ_5))
        self.tooltip.pack(fill='x',side='top',padx=(SZ_10, SZ_5),pady=0)
        self.input.pack(fill='x',side='left',padx=(SZ_10, SZ_5),expand=True)
        self.describe.pack(fill='none',side='left',padx=SZ_5)
        # 边缘线
        self.sideshow.place(x=0,y=0,width=SZ_2,relheight=1)

# 文本分割线，包含若干个KVD，可以折叠
class TextSeparator(ttk.Frame):
    def __init__(self,master,screenzoom:float,describe:dict,pady:int=5):
        self.sz = screenzoom
        super().__init__(master=master)
        self.pady = int(self.sz * pady)
        # 标题栏
        self.title = ttk.Frame(master=self)
        ## 文字：
        self.label = ttk.Label(master=self.title,text=describe,style='dialog.TLabel')
        self.label.bind("<Button-1>",self.update_toggle)
        ## 分割线
        self.sep = ttk.Separator(
                    master=self.title,
                    orient='horizontal',
                    bootstyle='primary'
                    )
        # 容器
        self.content = {}
        self.content_index = []
        self.content_frame = ttk.Frame(master=self)
        self.buttons = []
        # 显示
        self.update_item()
    # 刷新显示
    def update_item(self):
        # 是否扩展
        self.update_title()
        self.expand = True
        self.title.pack(fill='x',side='top')
        self.content_frame.pack(fill='x',side='top')
    # 放置标题
    def update_title(self):
        self.label.pack(fill='x',side='top',expand=True)
        self.sep.pack(fill='x',side='top',expand=True)
    # 切换收缩
    def update_toggle(self,event):
        if self.expand:
            self.content_frame.pack_forget()
            self.expand:bool = False
        else:
            self.content_frame.pack(fill='x',side='top')
            self.expand:bool = True
        self.master.update()
    # 添加KVD
    def add_element(self,key:str,value:str,kvd:dict,detail:bool=False,callback=None)->KeyValueDescribe:
        if detail:
            this_kvd = DetailedKeyValueDescribe(
                master = self.content_frame,
                screenzoom = self.sz,
                key=kvd['ktext'],
                value={
                    'type':kvd['vtype'],
                    'style':kvd['vitem'],
                    'value':value},
                describe={
                    'type':kvd['ditem'],
                    'text':kvd['dtext']
                },
                tooltip=kvd['tooltip'],
                callback=callback
            )
        else:
            this_kvd = KeyValueDescribe(
                master = self.content_frame,
                screenzoom = self.sz,
                key=kvd['ktext'],
                value={
                    'type':kvd['vtype'],
                    'style':kvd['vitem'],
                    'value':value},
                describe={
                    'type':kvd['ditem'],
                    'text':kvd['dtext']
                },
                tooltip=kvd['tooltip'],
                callback=callback
            )
        self.content_index.append(key)
        self.content[key] = this_kvd
        # 摆放
        this_kvd.pack(side='top',anchor='n',fill='x',pady=(self.pady + detail*self.pady ,0))
        return this_kvd
    # 添加按钮
    def add_button(self,text,command):
        self.buttons.append(ttk.Button(master=self.label,text=text,command=command,bootstyle='primary-link'))
        self.buttons[-1].pack(side='right',expand=False)
    # 移除按钮
    def remove_button(self):
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()
# 纹理背景
class Texture(tk.Frame):
    def __init__(self,master,screenzoom,file='./media/icon/texture4.png'):
        super().__init__(master=master,borderwidth=0)
        # Label对象
        self.canvas = ttk.Label(master=self,padding=0)
        # 纹理图片
        self.texture = Image.open(file)
        # 如果是黑暗模式，则反向
        if preference.theme == 'rplgendark':
            self.texture = Image.eval(self.texture, lambda x: 255 + 16 - x)
        self.bind('<Configure>', self.update_image)
        self.update_image(None)
        self.update_item()
    def update_item(self):
        self.canvas.pack(fill='both', expand=True)
    def update_image(self, event):
        self.image = ImageTk.PhotoImage(self.fill_texture(self.winfo_width(),self.winfo_height()))
        self.canvas.config(image=self.image)
    def fill_texture(self,width,height):
        new_image = Image.new('RGB',(width,height))
        for x in range(0, width, self.texture.width):
            for y in range(0, height, self.texture.height):
                new_image.paste(self.texture, (x, y))
        return new_image
# 将一个图片处理为指定的icon大小（方形）
def thumbnail(image:Image.Image,icon_size:int)->Image.Image:
    origin_w,origin_h = image.size
    if origin_w > origin_h:
        icon_width = icon_size
        icon_height = int(origin_h/origin_w * icon_size)
    else:
        icon_height = icon_size
        icon_width = int(origin_w/origin_h * icon_size)
    return image.resize([icon_width,icon_height]).convert('RGBA')
# 询问更名广播
def ask_rename_boardcast(master, old_name, new_name, otype):
    boardcast:BoardcastHandler = Link['boardcast']
    # 判断是否要做
    if preference.rename_boardcast == 'ask':
        choice = Messagebox().show_question(
            message='是否要将更名同步到所有引用位置？\n如果不希望每次询问，请修改：首选项-编辑设置-更名广播',
            title='更名广播',
            buttons=["否:secondary","是:primary"],
            parent= master
            )
    elif preference.rename_boardcast == 'yes':
        choice = '是'
    else:
        choice = '否'
    # 广播
    if choice == '是':
        if otype == 'name':
            result = boardcast.rename_charactor(old_name=old_name,new_name=new_name)
        elif otype == 'subtype':
            result = boardcast.rename_subtype(old_name=old_name,new_name=new_name)
        else:
            result = boardcast.rename_media(mtype=otype,old_name=old_name,new_name=new_name)
        # 弹出消息提示，Toast
        message = f'{otype}: {old_name}->{new_name}\n'
        message += '在媒体库中更新了{mediadef}处引用\n在角色配置中更新了{chartab}处引用\n在剧本文件中更新了{logfile}处引用'.format(**result)
        ToastNotification(
            title='更名广播',
            message=message,
            duration=3000
        ).show_toast()
        return True
    else:
        return False
