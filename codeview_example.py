
import tkinter as tk
import ttkbootstrap as ttk
from chlorophyll import CodeView
from core.RplGenLogLexer import RplGenLogLexer
from tkextrafont import Font

root = ttk.Window()

filefont = Font(file='./media/sarasa-mono-sc-regular.ttf')

codeview = CodeView(root, lexer=RplGenLogLexer, color_scheme="monokai", font=('Sarasa Mono SC',12),undo=True)
codeview.pack(fill="both", expand=True)
with open('./toy/LogFile.rgl','r',encoding='utf-8') as file:
    codeview.insert("end",file.read())

root.mainloop()
