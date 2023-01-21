"""
通用函数
"""
from tkinter import colorchooser, filedialog, messagebox

EDITION = '1.18.4'

def browse_file(text_obj, method='file',filetype=None):
    """
    浏览文件或者文件夹
    """
    filetype_dic = {
        'logfile':[('log文件',('*.rgl','*.txt')),('全部文件','*.*')],
        'chartab':[('角色配置表',('*.tsv','*.csv','*.xlsx','*.txt')),('全部文件','*.*')],
        'mediadef':[('媒体定义文件',('*.txt','*.py')),('全部文件','*.*')],
        'picture':[('图片文件',('*.png','*.jpg','*.jpeg','*.bmp')),('全部文件','*.*')],
        'soundeff':[('音效文件','*.wav'),('全部文件','*.*')],
        'BGM':[('背景音乐文件','*.ogg'),('全部文件','*.*')],
        'fontfile':[('字体文件',('*.ttf','*.otf','*.ttc')),('全部文件','*.*')],
        'timeline':[('回声时间轴','.timeline'),('全部文件','*.*')]
    }
    if method == 'file':
        if format is None:
            getname = filedialog.askopenfilename()
        else:
            getname = filedialog.askopenfilename(filetypes=filetype_dic[filetype])
    else:
        getname = filedialog.askdirectory()
    if (' ' in getname) | ('$' in getname) | ('(' in getname) | (')' in getname):
        messagebox.showwarning(title='警告', message='请勿使用包含空格、括号或特殊符号的路径！')
        text_obj.set('')
        return None
    text_obj.set(getname)
    return getname


def choose_color(text_obj):
    """
    选择颜色，并将颜色设置给类型为StringVar的参数
    """
    get_color = colorchooser.askcolor()
    try:
        R, G, B = get_color[0]
        A = 255
        text_obj.set('({0},{1},{2},{3})'.format(int(R), int(G), int(B),
                                                int(A)))
    except Exception:
        text_obj.set('')
