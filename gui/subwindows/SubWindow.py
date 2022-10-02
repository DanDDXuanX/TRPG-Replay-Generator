import tkinter as tk


class SubWindow(tk.Toplevel):
    """
    子窗口公共父类
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
