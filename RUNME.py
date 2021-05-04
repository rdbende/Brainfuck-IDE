"""
Author: rdbende
License: GNU GPLv3
Copyright: 2021 rdbende
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os, sys, time, threading, configparser, webbrowser

import widgets, interpreter
from constants import *


class Application(ttk.Frame):
    def __init__(self, window=tk._default_root):
        self.window = window
        tk.Frame.__init__(self, window)
        
        icon = tk.PhotoImage(file="icon.png")
        # I didn't want to hack around by cross platforming,
        # in ico, icns, xbm formats, so I just use png
        self.window.iconphoto(False, icon)
    
        self.brainfuck_image = tk.PhotoImage(file="brainfuck.png")

        self.config = configparser.ConfigParser()
        try:
            self.config.read("settings.ini")
            self.dark_mode = tk.IntVar(value=int(self.config["settings"]["dark_mode"]))
            self.use_azure = tk.BooleanVar(value=bool(int(self.config["settings"]["use_azure"])))
            self.current_file = self.config["files"]["current"]
        except:
            raise RuntimeError("Problem with configuration file")

        if not os.path.exists("Azure-ttk-theme-main"):
            self.use_azure.set(False)


        self.menubar = tk.Menu(relief="flat")

        self.file_menu = tk.Menu(self.menubar, tearoff=False, bd=0)
        self.file_menu.add_command(label="New", command=self.new_file, accelerator=new_accel)
        self.file_menu.add_command(label="Open", command=self.open_file, accelerator=open_accel)
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator=save_accel)
        self.file_menu.add_command(label="Save as", command=self.save_as_file, accelerator=saveas_accel)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit, accelerator=quit_accel)

        self.help_menu = tk.Menu(self.menubar, tearoff=False, bd=0)
        self.help_menu.add_command(label="About", command=self.about)
        self.help_menu.add_command(label="What is Brainfuck?", command=self.open_wiki)

        self.menubar.add_cascade(menu=self.file_menu, label="File")
        self.menubar.add_command(label="Settings", command=self.settings)
        self.menubar.add_cascade(menu=self.help_menu, label="Help")
        self.menubar.add_command(label="    ", state="disabled")
        self.menubar.add_command(label="Run", command=self.run)
        self.menubar.add_command(label="Stop", command=self.stop)
        
        self.window.config(menu=self.menubar)


        self.main_paned = ttk.PanedWindow(self)

        self.editor_box = widgets.Editor(self.main_paned)
        self.main_paned.add(self.editor_box, weight=1)

        self.io_paned = ttk.PanedWindow(self, orient="horizontal")
        self.main_paned.add(self.io_paned, weight=2)

        self.input_box = widgets.Input(self.io_paned)
        self.io_paned.add(self.input_box, weight=1)

        self.output_box = widgets.Output(self.io_paned)
        self.io_paned.add(self.output_box, weight=1)

        self.main_paned.pack(expand=True, fill="both")


        self.change_appearance()
        self.show_file()
        self.save_file()


        # self.window.bind("<FocusIn>", self.ask_reload)
        self.window.bind("<<Compare>>", self.compare)
        self.window.bind_all("<F5>", self.run)
        self.window.bind_all(settings_keys, self.settings)
        self.window.bind_all(new_keys, self.new_file)
        self.window.bind_all(open_keys, self.open_file)
        self.window.bind_all(save_keys, self.save_file)
        self.window.bind_all(saveas_keys, self.save_as_file)
        self.window.protocol("WM_DELETE_WINDOW", self.exit)
        
    def check_internet(self):
        import socket
        HOST = "8.8.8.8"
        PORT = 53
        TIMEOUT = 2
        try:
            socket.setdefaulttimeout(TIMEOUT)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((HOST, PORT))
            return True
        except socket.error:
            return False
        
    def threaded(func):
        def wrapper(*args, **kwargs):
            thread = threading.Thread(target=func, args=args, kwargs=kwargs)
            thread.start()
            return thread
        return wrapper


    def new_file(self, *args):
        self.save_file()
        new_file = filedialog.asksaveasfilename(title='Create...', filetypes=[('Brainfuck files', '*.bf *.b'), ('All files', '*.*')])
        if new_file:
            self.current_file = new_file
            self.editor_box.delete("0.0", "end")
            self.save_file()
            self.show_file()


    def open_file(self, *args):
        self.save_file()
        new_file = filedialog.askopenfilename(title='Open...', filetypes=[('Brainfuck files', '*.bf *.b'), ('All files', '*.*')])
        if new_file:
            self.current_file = new_file
            self.show_file()
        

    def save_file(self, *args):
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.editor_box.get("0.0", "end"))
        else:
            self.save_as_file()
        self.editor_box.dirty = False
        self.window.title("Brainfuck IDE - {}".format(self.current_file))


    def save_as_file(self, *args):
        new_file = filedialog.asksaveasfilename(title='Save as...', filetypes=[('Brainfuck files', '*.bf *.b'), ('All files', '*.*')])
        if new_file:
            self.current_file = new_file
            self.save_file()
            self.show_file()


    def show_file(self):
        self.editor_box.delete("0.0", "end")
        try:
            with open(self.current_file, "r") as program:
                content = program.read()
                content = content.rstrip("\n") # Removes the unnecessary newline character
                if content:
                    self.editor_box.insert("1.0", content)
            self.output_box.delete("0.0", "end")
            self.window.title("Brainfuck IDE - {}".format(self.current_file))
        except FileNotFoundError:
            pass


    def change_appearance(self):
        Appearance.change_appearance(self.dark_mode.get())
        
        self.editor_box.text.config(bg=Appearance.bg, fg=Appearance.fg, insertbackground=Appearance.insert, selectbackground=Appearance.select)
        self.input_box.text.config(bg=Appearance.bg, fg=Appearance.fg, insertbackground=Appearance.insert, selectbackground=Appearance.select)
        self.output_box.text.config(bg=Appearance.bg, fg=Appearance.fg, selectbackground=Appearance.select)
        
        self.editor_box.text.tag_configure("pos", foreground=Appearance.pos)
        self.editor_box.text.tag_configure("io", foreground=Appearance.io)
        self.editor_box.text.tag_configure("brace", foreground=Appearance.brace)
        self.editor_box.text.tag_configure("value", foreground=Appearance.value)
        self.editor_box.text.tag_configure("normal", foreground=Appearance.fg)
        
        self.editor_box.highlight()
        
        if self.dark_mode.get() and self.use_azure.get():
            try:
                self.tk.eval("source Azure-ttk-theme-main/azure-dark.tcl")
            except:
                pass
            ttk.Style().theme_use("azure-dark")
        elif not self.dark_mode.get() and self.use_azure.get():
            try:
                self.tk.eval("source Azure-ttk-theme-main/azure.tcl")
            except:
                pass
            ttk.Style().theme_use("azure")
            

    def open_wiki(self):
        webbrowser.open("https://en.wikipedia.org/wiki/Brainfuck")
        

    def compare(self, *args):
        with open(self.current_file) as file:
            if file.read() != self.editor_box.get("0.0", "end"):
                self.editor_box.dirty = True
                self.window.title("Brainfuck IDE - {} *".format(self.current_file))


    # def ask_reload(self, args):
    #     with open(self.current_file) as file:
    #         content = file.read()
    #         print(content)
    #         print(self.editor_box.get("0.0", "end"))
    #         if content != self.editor_box.get("0.0", "end"):
    #             msg = messagebox.askyesno("External modification", "Looks like\n'{}' was modified outside the editor.\n\nDo you want to discard the current editor content and reload the file from disk?".format(self.current_file))
    #             if msg:
    #                 self.editor_box.delete("0.0", "end")
    #                 self.editor_box.insert("0.0", content)
    #             else:
    #                 self.editor_box.dirty = True
    #                 self.window.title("Brainfuck IDE - {} *".format(self.current_file))


    @threaded
    def exec(self):
        interpreter.execute(self.current_file)


    def run(self, *args):
        if not interpreter.running:
            self.save_file()
            sys.stdin.clear()
            self.exec()


    def stop(self):
        interpreter.stop = True
        
        
    def settings(self, *args):
        settings_window = tk.Toplevel(self.window)
        settings_window.transient(self.window)
        settings_window.resizable(False, False)
        settings_window.title("Settings")
        
        theme_frame = ttk.LabelFrame(settings_window, text="UI theme")
        theme_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")
        
        light_radio = ttk.Radiobutton(theme_frame, text="Light mode", variable=self.dark_mode, value=0, command=self.change_appearance)
        light_radio.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        dark_radio = ttk.Radiobutton(theme_frame, text="Dark mode", variable=self.dark_mode, value=1, command=self.change_appearance)
        dark_radio.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="w")
        
        theme_label = ttk.Label(theme_frame, text="Restart needed after changing these options!")
        theme_label.grid(row=3, column=0, padx=10, pady=(5, 10))
        
    #     font_button = ttk.Button(settings_window, text="Change font", command=change_font)
    #     font_button.grid(row=4, column=0, padx=10, pady=(10, 5))
    
        def download_azure():
            import requests
            import zipfile
            
            nonlocal azure_button
            
            azure_button.config(state="disabled")
            azure_progress = ttk.Progressbar(azure_frame)
            azure_progress.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="we")
            settings_window.update()
            
            azure = requests.get("https://github.com/rdbende/Azure-ttk-theme/archive/refs/heads/main.zip")
            with open("azure.zip", 'wb') as file:
                file.write(azure.content)
                
            azure_progress.config(value=20)
            azure_progress.update()
            
            with zipfile.ZipFile("azure.zip") as zip_file:
                zip_file.extractall(".")
                
            azure_progress.config(value=70)
            azure_progress.update()
            
            os.remove("azure.zip")
            
            azure_progress.config(value=90)
            azure_progress.update()
            
            self.use_azure.set(True)
            
            self.change_appearance()
            azure_progress.config(value=100)
            azure_progress.update()


        if not os.path.exists("Azure-ttk-theme-main") and self.check_internet():
            azure_frame = ttk.LabelFrame(settings_window, text="Azure theme")
            azure_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nswe")
            
            azure_label = ttk.Label(azure_frame, text="Download my beautiful Azure theme for Brainfuck IDE")
            azure_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
            
            azure_button = ttk.Button(azure_frame, text="Download", command=download_azure)
            azure_button.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="we")
            
            azure_link = widgets.LinkLabel(azure_frame, text="Visit it on GitHub", url="https://github.com/rdbende/Azure-ttk-theme")
            azure_link.grid(row=1, column=1, padx=10, pady=(5, 10))
            
        elif os.path.exists("Azure-ttk-theme-main"):
            azure_switch = ttk.Checkbutton(theme_frame, text="Azure theme", variable=self.use_azure, command=self.change_appearance)
            azure_switch.grid(row=2, column=0, padx=10, pady=(5, 5), sticky="w")
            try:
                azure_switch.config(style="Switch")
            except:
                pass


    def about(self, *args):
        about_window = tk.Toplevel(self.window)
        about_window.transient(self.window)
        about_window.resizable(False, False)
        about_window.title("About Brainfuck IDE")
        
        about_frame = tk.Frame(about_window)
        about_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        image_label = tk.Label(about_frame, image=self.brainfuck_image, compound="center")
        image_label.grid(row=0, column=0, pady=5)
        
        credit_label = ttk.Label(about_frame, text="Copyright (c) 2021 rdbende")
        credit_label.grid(row=1, column=0, pady=5)
        
        version_label = ttk.Label(about_frame, text="v1.0")
        version_label.grid(row=2, column=0, pady=5)
        
        version_label = widgets.LinkLabel(about_frame, text="Visit repo on GitHub", url="https://github.com/rdbende/Brainfuck-IDE")
        version_label.grid(row=3, column=0, pady=5)
        
        
    def exit(self):
        if interpreter.running:
            msg = messagebox.askyesno("Program is running!", "Your program is still running!\nDo you want to kill it?")
            if msg:
                self.stop()
                time.sleep(0.001) # The sleep is needed, because the thread does not stop immediately
                self.exit()
                
        if self.editor_box.dirty:
            msg = messagebox.askyesnocancel("File not saved", "Do you want to save your file?")
            if msg:
                self.editor_box.dirty = False
                self.save_file()
                self.exit()
            elif msg is False:
                self.editor_box.dirty = False
                self.exit()
                
        if not interpreter.running and not self.editor_box.dirty: 
            with open('settings.ini', 'w') as file:
                self.config["settings"]["dark_mode"] = str(self.dark_mode.get())
                self.config["settings"]["use_azure"] = str(int(self.use_azure.get()))
                self.config["files"]["current"] = self.current_file
                self.config.write(file)
            try: # I haven't figured out why, but sometimes it want to close itself twice:
                # application has been destroyed
                self.window.destroy()
            except:
                pass


    # def change_font():
    #     def font(font_settings):
    #         current_font = font_settings
    #     
    #     root.tk.call("tk", "fontchooser", "configure", "-command", root._register(font))
    #     root.tk.eval("tk fontchooser show")

if __name__ == "__main__":
    root = tk.Tk(className="Brainfuck") # On Ubuntu the className will be appear on the top bar, and on the dock tooltip
    root.geometry("800x500")
    root.title("Python Brainfuck IDE")
    
    Application(root).pack(fill="both", expand=True)
    
    root.mainloop()
