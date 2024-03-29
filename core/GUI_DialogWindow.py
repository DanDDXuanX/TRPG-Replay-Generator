#!/usr/bin/env python
# coding: utf-8

# tk内置的会话框

import os
from ttkbootstrap.dialogs import colorchooser, Messagebox
from ttkbootstrap.localization import MessageCatalog
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename, askopenfilenames
from tkinter import StringVar
from .Utils import rgba_str_2_hex
from .FilePaths import Filepath
from .GUI_Link import Link
from .ProjConfig import preference
from .Utils import convert_audio
from .GUI_Language import tr

class ColorChooserDialogZH(colorchooser.ColorChooserDialog):
    # 重载：在中文系统里，OK被翻译为确定了，这回导致选色的值不输出到result
    def on_button_press(self, button):
        if button.cget('text') == MessageCatalog.translate('OK'):
            values = self.colorchooser.get_variables()
            self._result = colorchooser.ColorChoice(
                rgb=(values.r, values.g, values.b), 
                hsl=(values.h, values.s, values.l), 
                hex=values.hex
            )
            self._toplevel.destroy()            
        self._toplevel.destroy()

# 打开选色器，并把结果输出给 StringVar
def color_chooser(master,text_obj:StringVar,quote:bool=False)->tuple:
    initcolor = rgba_str_2_hex(text_obj.get())
    if initcolor:
        dialog_window = ColorChooserDialogZH(parent=master, initialcolor=initcolor)
    else:
        dialog_window = ColorChooserDialogZH(parent=master)
    # dialog_window = colorchooser.ColorChooserDialog(parent=master,title='选择颜色')
    dialog_window.show()
    color = dialog_window.result
    if color:
        # 选中的颜色
        R, G, B = color.rgb
        A = 255
        # 设置 StringVar
        if quote:
            text_obj.set("'({0},{1},{2},{3})'".format(int(R), int(G), int(B),int(A)))
        else:
            text_obj.set('({0},{1},{2},{3})'.format(int(R), int(G), int(B),int(A)))
        return (R,G,B,A)
    else:
        # text_obj.set("")
        return None

filetype_dic = {
    'zh':{
        'logfile':      [('剧本文件',('*.rgl','*.txt')),('全部文件','*.*')],
        'chartab':      [('角色配置表',('*.tsv','*.csv','*.xlsx','*.txt')),('全部文件','*.*')],
        'mediadef':     [('媒体定义文件',('*.txt','*.py')),('全部文件','*.*')],
        'rgscripts':    [('全部文件','*.*'),('剧本文件',('*.rgl','*.txt')),('角色配置表',('*.tsv','*.csv','*.xlsx','*.txt')),('媒体定义文件',('*.txt','*.py'))],
        'picture':      [('图片文件',('*.png','*.jpg','*.jpeg','*.bmp')),('全部文件','*.*')],
        'animate':      [('图片文件',('*.png','*.jpg','*.jpeg','*.bmp')),('动画文件',('*.apng','*.gif')),('全部文件','*.*')],
        'soundeff':     [('音效文件',('*.wav','*.mp3')),('全部文件','*.*')],
        'BGM':          [('背景音乐文件',('*.ogg','*.mp3','*.wav')),('全部文件','*.*')],
        'fontfile':     [('字体文件',('*.ttf','*.otf','*.ttc')),('全部文件','*.*')],
        'rplgenproj':   [('回声工程',('*.rgpj','*.json')),('全部文件','*.*')],
        'prefix':       [('全部文件','*.*')],
        'text':         [('文本文件','*.txt'),('全部文件','*.*')]
    },
    'en':{
        'logfile':      [('Log Scripts',('*.rgl','*.txt')),('All Files','*.*')],
        'chartab':      [('Character Tables',('*.tsv','*.csv','*.xlsx','*.txt')),('All Files','*.*')],
        'mediadef':     [('Media Defines',('*.txt','*.py')),('All Files','*.*')],
        'rgscripts':    [('All Files','*.*'),('Log Scripts',('*.rgl','*.txt')),('Character Table',('*.tsv','*.csv','*.xlsx','*.txt')),('Media Define',('*.txt','*.py'))],
        'picture':      [('Image Files',('*.png','*.jpg','*.jpeg','*.bmp')),('All Files','*.*')],
        'animate':      [('Image Files',('*.png','*.jpg','*.jpeg','*.bmp')),('Anime Files',('*.apng','*.gif')),('All Files','*.*')],
        'soundeff':     [('Audio Files',('*.wav','*.mp3')),('All Files','*.*')],
        'BGM':          [('Music Files',('*.ogg','*.mp3','*.wav')),('All Files','*.*')],
        'fontfile':     [('Font Files',('*.ttf','*.otf','*.ttc')),('All Files','*.*')],
        'rplgenproj':   [('RplGen Project',('*.rgpj','*.json')),('All Files','*.*')],
        'prefix':       [('All Files','*.*')],
        'text':         [('Text Files','*.txt'),('All Files','*.*')]
    },
}[preference.lang]
default_name = {
    'zh':{
        'logfile':   ['新建剧本文件','.rgl'],
        'chartab':   ['新建角色表'  ,'.tsv'],
        'mediadef':  ['新建媒体库'  ,'.txt'],
        'rplgenproj':['新建工程'    ,'.rgpj'],
        'prefix':    ['导出文件'    ,'']
    },
    'en':{
        'logfile':   ['New_Logfile','.rgl'],
        'chartab':   ['New_Chartab'  ,'.tsv'],
        'mediadef':  ['New_Mediadef'  ,'.txt'],
        'rplgenproj':['New_RplGen_Project','.rgpj'],
        'prefix':    ['Exported','']
    }
}[preference.lang]
# 浏览多个文件，并把路径返回（不输出给stringvar）：
def browse_multi_file(master, filetype=None ,related:bool=True,convert:bool=False)->list:
    if filetype is None:
        get_names:tuple = askopenfilenames(parent=master,)
    else:
        get_names:tuple = askopenfilenames(parent=master,filetypes=filetype_dic[filetype])
    # 检查结果
    getname = list(get_names)
    if getname == ['']:
        return None # 注意，如果没选择，返回None！
    else:
        # 是否需要转换格式
        if convert and filetype in ['soundeff','BGM']:
            convertname = getname
            for idx,file in enumerate(getname):
                newname = convert_audio_file(master=master,filetype=filetype,getname=file)
                if newname:
                    convertname[idx] = newname
            getname = convertname
        else:
            pass
        # 是否相对路径
        if related:
            out_path = []
            for path in getname:
                out_path.append(Filepath(path,check_exist=False).relative())
        else:
            out_path = getname
        # 返回
        return out_path
# 浏览文件，并把路径输出给 StringVar
def browse_file(master, text_obj:StringVar, method='file', filetype=None, quote:bool=True, related:bool=True, convert:bool=False):
    if method == 'file':
        if filetype is None:
            getname = askopenfilename(parent=master,)
        else:
            getname = askopenfilename(parent=master,filetypes=filetype_dic[filetype])
    else:
        getname = askdirectory(parent=master)
    # 输出
    if getname == '':
        return getname
    else:
        # 是否需要转换格式
        if convert and filetype in ['soundeff','BGM']:
            newname = convert_audio_file(master=master,filetype=filetype,getname=getname)
            if newname:
                getname = newname
        else:
            pass
        # 是否是媒体路径下的文件夹
        if related:
            try:
                getname = Filepath(getname,check_exist=False).relative()
            except Exception:
                pass
        # 是否加引号
        if quote:
            text_obj.set("'{}'".format(getname))
        else:
            text_obj.set(getname)
        # 返回
        return getname
# 转换音频格式
def convert_audio_file(master,filetype,getname):
    target_type = {'soundeff':'wav','BGM':'ogg'}[filetype]
    suffix = getname.split('.')[-1]
    prefix = getname.split('/')[-1][:-(len(suffix)+1)]
    if suffix != target_type:
        # 确定是否转格式
        if preference.auto_convert == 'ask':
            name = getname.split('/')[-1]
            choice = Messagebox().show_question(
                message=tr('选择了一个不支持的音频文件：{}，是否转换格式？').format(name)+'\n'+tr('如果不希望每次询问，请修改：首选项-编辑设置-','音频转格式'),
                title=tr('不支持的音频'),
                buttons=[tr('否')+":secondary",tr('是')+":primary"],
                parent=master
                )
        elif preference.auto_convert == 'yes':
            choice = tr('是')
        else:
            choice = tr('否')
        # 判断选择
        if choice == tr('是'):
            # 输出路径
            output_path = Link['media_dir'] + f'convert/'
            # 检查输出路径是否存在
            if not os.path.isdir(output_path):
                os.makedirs(output_path)
            output_file = output_path + f'{prefix}.{target_type}'
            state, info = convert_audio(target_type=target_type,ifile=getname,ofile=output_file)
            if state:
                return info
            else:
                Messagebox().show_error(message=info,title=tr('音频格式转换错误'),parent=master)
                return
        else:
            return
    else:
        return
def save_file(master, method='file', filetype=None, quote:bool=True)->str:
    if method == 'file':
        defaults = default_name[filetype]
        if filetype is None:
            getname = asksaveasfilename(parent=master,defaultextension=defaults[1],initialfile=defaults[0])
        else:
            getname = asksaveasfilename(parent=master,filetypes=filetype_dic[filetype],defaultextension=defaults[1],initialfile=defaults[0])
        return getname
    else:
        return ''