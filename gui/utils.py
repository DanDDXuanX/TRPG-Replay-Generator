import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def browse_file(text_obj,method='file'):
    """
    浏览文件或者文件夹
    """
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