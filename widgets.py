"""
Author: rdbende
License: GNU GPLv3
Copyright: 2021 rdbende
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
import interpreter
import sys


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
        return self.text.get(f"{line}.0", "end")
    
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
        
    def delete(self, *args, **kwargs):
        self.text.config(state="normal")
        self.text.delete(*args, **kwargs)
        self.text.config(state="disabled")
        
        
    def write(self, content):
        self.text.config(state="normal")
        self.text.insert("end", content)
        self.text.config(state="disabled")


class Editor(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side='right', fill='y')
        
        self.text = tk.Text(self, relief="flat", highlightthickness=0, insertwidth=1, yscrollcommand=self.scrollbar.set)
        self.text.pack(expand=True, fill='both')
        
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
        
    def highlight(self, *args):
        line = 0
        total_lines = int(self.text.index('end').split('.')[0])
        for content in range(total_lines):
            char = 0
            for pattern in self.text.get("{}.0".format(content), "{}.end".format(content)):
                if pattern == "<" or pattern == ">":
                    tag = "pos"
                elif pattern == "." or pattern == ",":
                    tag = "io"
                elif pattern == "+" or pattern == "-":
                    tag = "value"
                elif pattern == "[" or pattern == "]":
                    tag = "brace"
                else:
                    tag = "normal"
                self.text.tag_add(tag, "{}.{}".format(line, char), "{}.{}".format(line, char + 1))
                char += 1
            line += 1
            
            
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
