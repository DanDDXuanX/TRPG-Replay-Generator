import ttkbootstrap as ttk

import pygments.lexers
from chlorophyll import CodeView

root = ttk.Window()

codeview = CodeView(root, lexer=pygments.lexers.PythonLexer, color_scheme="monokai", font='-family consolas -size 14')
codeview.pack(fill="both", expand=True)

root.mainloop()
