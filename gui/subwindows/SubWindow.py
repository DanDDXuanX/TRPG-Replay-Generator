import tkinter as tk


class SubWindow(tk.Toplevel):
    """
    子窗口公共父类
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
    # 禁用子窗体方法
    def disable(self,status):
        if status == True:
            try:
                self.attributes('-disabled', True)
            except Exception:
                pass
        else:
            try:
                self.attributes('-disabled', False)
            except:
                pass
            self.lift()
            self.focus_force()
