"""
Author: rdbende
License: GNU GPLv3
Copyright: 2021 rdbende
"""

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import webbrowser
import interpreter
import sys
try:
    from pygments import lex
    from pygments.lexers import BrainfuckLexer
    pygments = True
except ImportError:
    pygments = False


class Input(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side='right', fill='y')
        
        self.text = tk.Text(self, relief="flat", highlightthickness=0, insertwidth=1, yscrollcommand=self.scrollbar.set)
        self.text.pack(expand=True, fill='both')
        
        self.scrollbar.config(command=self.text.yview)
        
        sys.stdin = self
        self.enter_pressed = False
        
        def enter(*args):
            self.enter_pressed = True
            
        self.text.bind("<Return>", enter)
        
    def write(self, content):
        self.text.insert("end", content)
        
    def readline(self):
        self.enter_pressed = False
        self.text.focus()
        while not self.enter_pressed:
            if interpreter.stop:
                interpreter.running = False
                interpreter.exit()
        line = int(self.text.index("insert")[0]) - 1
        return self.text.get("{}.0".format(line), "{}.end".format(line))
    
    def clear(self):
        self.text.delete("0.0", "end")


class Output(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side='right', fill='y')
        
        self.text = tk.Text(self, state="disabled", relief="flat", highlightthickness=0, insertwidth=1, yscrollcommand=self.scrollbar.set)
        self.text.pack(expand=True, fill='both')
        
        self.scrollbar.config(command=self.text.yview)
        
        sys.stdout = self
    
    def disabler(func):
        def wrapper(self, *args, **kwargs):
            self.text.config(state="normal")
            func(self, *args, **kwargs)
            self.text.config(state="disabled")
            return func
        return wrapper
    
    @disabler
    def delete(self, *args, **kwargs):
        self.text.delete(*args, **kwargs)
        
    @disabler
    def write(self, content):
        self.text.insert("end", content)


class Editor(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side='right', fill='y')
        
        self.text = tk.Text(self, relief="flat", highlightthickness=0, insertwidth=1, yscrollcommand=self.scrollbar.set)
        self.text.pack(expand=True, fill='both')
        
        self.font = tkfont.Font(family='monospace', size=10)
        tab = self.font.measure("    ")
        self.text.config(font=self.font, tabs=tab)
        
        self.scrollbar.config(command=self.text.yview)
        
        self.text.bind("<KeyRelease>", self.modified)
        
        self.get = self.text.get
        self.delete = self.text.delete
        self.dirty = False
        
    def insert(self, *args, **kwargs):
        self.text.insert(*args, **kwargs)
        self.highlight()
        
    def modified(self, *args):
        self.event_generate("<<Compare>>")
        self.highlight()
        
    def highlight_line(self, event=None, line=None):
        index = self.text.index("insert").split(".")
        line_no = int(index[0])
        
        if line == None:
            line_text = self.text.get("{}.{}".format(line_no, 0),  "{}.end".format(line_no))
            self.text.mark_set("range_start", str(line_no) + '.0')
        
        elif line is not None:
            line_text = self.text.get("{}.{}".format(line, 0), "{}.end".format(line))
            self.text.mark_set("range_start", str(line) + '.0')

        for token, content in lex(line_text, BrainfuckLexer()):
            self.text.mark_set("range_end", "range_start + %dc" % len(content))
            self.text.tag_add(str(token), "range_start", "range_end")
            self.text.mark_set("range_start", "range_end")


    def highlight(self, *args):
        if pygments:
            code = self.text.get("1.0", "end-1c")
            i = 1
            for line in code.splitlines():
                self.text.index("%d.0" %i)
                self.highlight_line(line=i)
                self.text.update()
                i += 1
            
            
class LinkLabel(ttk.Label):
    
    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop("url", "https://")
        self.normalcolor = kwargs.pop("normalcolor", "#007fff")
        self.hovercolor = kwargs.pop("hovercolor", "#005ddd")
        
        ttk.Label.__init__(self, *args, foreground=self.normalcolor, **kwargs)
        
        if self.tk.eval("tk windowingsystem") == "aqua":
            cursor = kwargs.pop("cursor", "pointinghand")
        else:
            cursor = kwargs.pop("cursor", "hand2")
        self.configure(cursor=cursor)
        
        self.bind("<Button-1>", self._open)
        self.bind("<Enter>", self.enter)
        self.bind("<Leave>", self.leave)

    def enter(self, *args):
        self.configure(foreground=self.hovercolor)

    def leave(self, *args):
        self.configure(foreground=self.normalcolor)

    def _open(self, *args):
        self.leave()
        webbrowser.open(self.url)
        
        
class PopupMenu(tk.Menu):
    def __init__(self, master):
        tk.Menu.__init__(self, master, tearoff=False, bd=0, relief="flat")

        self.master.bind("<Button-3>", self.popup)

    def popup(self, event):
        try:
            self.tk_popup(int(event.x_root + 2), int(event.y_root + 2))
        finally:
            self.grab_release()

