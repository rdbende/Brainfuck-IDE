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


root = tk.Tk(className="Brainfuck") # On Ubuntu the className will be appear on the top bar, and on the dock tooltip
root.geometry("800x500")

root.title("Python Brainfuck IDE")


icon = tk.PhotoImage(file="icon.png")
# I didn't want to hack around by cross platforming,
# in ico, icns, xbm formats, so I just use png
root.iconphoto(False, icon)
brainfuck_image = tk.PhotoImage(file="brainfuck.png")


config = configparser.ConfigParser()
config.read("settings.ini")

dark_mode = tk.IntVar(value=int(config["settings"]["dark_mode"]))
use_azure = tk.BooleanVar(value=bool(int(config["settings"]["use_azure"])))

if not os.path.exists("Azure-ttk-theme-main"):
    use_azure.set(False)

current_file = config["files"]["current"]



def check_internet():
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


def new_file(*args):
    global current_file
    save_file()
    new_file = filedialog.asksaveasfilename(title='Create...', filetypes=[('Brainfuck files', '*.bf *.b'), ('All files', '*.*')])
    if new_file:
        current_file = new_file
        editor_box.delete("0.0", "end")
        save_file()
        show_file()


def open_file(*args):
    global current_file
    save_file()
    new_file = filedialog.askopenfilename(title='Open...', filetypes=[('Brainfuck files', '*.bf *.b'), ('All files', '*.*')])
    if new_file:
        current_file = new_file
        show_file()
    

def save_file(*args):
    if current_file:
        with open(current_file, "w") as file:
            file.write(editor_box.get("0.0", "end"))
    else:
        save_as_file()
    editor_box.dirty = False
    root.title("Brainfuck IDE - {}".format(current_file))


def save_as_file(*args):
    global current_file
    new_file = filedialog.asksaveasfilename(title='Save as...', filetypes=[('Brainfuck files', '*.bf *.b'), ('All files', '*.*')])
    if new_file:
        current_file = new_file
        save_file()
        show_file()


def show_file():
    global editor_box
    editor_box.delete("0.0", "end")
    try:
        with open(current_file, "r") as program:
            content = program.read()
            content = content.rstrip("\n") # Removes the unnecessary newline character
            if content:
                editor_box.insert("1.0", content)
        output_box.delete("0.0", "end")
        root.title("Brainfuck IDE - {}".format(current_file))
    except FileNotFoundError:
        pass


def change_appearance():
    global use_azure
    
    Appearance.change_appearance(dark_mode.get())
    
    editor_box.text.config(bg=Appearance.bg, fg=Appearance.fg, insertbackground=Appearance.insert, selectbackground=Appearance.select)
    input_box.text.config(bg=Appearance.bg, fg=Appearance.fg, insertbackground=Appearance.insert, selectbackground=Appearance.select)
    output_box.text.config(bg=Appearance.bg, fg=Appearance.fg, selectbackground=Appearance.select)
    
    editor_box.text.tag_configure("pos", foreground=Appearance.pos)
    editor_box.text.tag_configure("io", foreground=Appearance.io)
    editor_box.text.tag_configure("brace", foreground=Appearance.brace)
    editor_box.text.tag_configure("value", foreground=Appearance.value)
    editor_box.text.tag_configure("normal", foreground=Appearance.fg)
    
    editor_box.highlight()
    
    if dark_mode.get() and use_azure.get():
        try:
            root.tk.eval("source Azure-ttk-theme-main/azure-dark.tcl")
        except:
            pass
        ttk.Style().theme_use("azure-dark")
    elif not dark_mode.get() and use_azure.get():
        try:
            root.tk.eval("source Azure-ttk-theme-main/azure.tcl")
        except:
            pass
        ttk.Style().theme_use("azure")
        

def open_wiki():
    webbrowser.open("https://en.wikipedia.org/wiki/Brainfuck")
    

def compare(*args):
    with open(current_file) as file:
        if not file.read() == editor_box.get("0.0", "end"):
            editor_box.dirty = True
            root.title("Brainfuck IDE - {} *".format(current_file))


# def ask_reload(*args):
#     with open(current_file) as file:
#         content = file.read()
#         print(content)
#         print(editor_box.get("0.0", "end"))
#         if not content == editor_box.get("0.0", "end"):
#             msg = messagebox.askyesno("External modification", "Looks like\n'{}' was modified outside the editor.\n\nDo you want to discard the current editor content and reload the file from disk?".format(current_file))
#             if msg:
#                 editor_box.delete("0.0", "end")
#                 editor_box.insert("0.0", content)
#             else:
#                 editor_box.dirty = True
#                 root.title("Brainfuck IDE - {} *".format(current_file))


@threaded
def exec():
    interpreter.execute(current_file)


def run(*args):
    if not interpreter.running:
        save_file()
        sys.stdin.clear()
        exec()


def stop():
    interpreter.stop = True
    
    
def settings(*args):
    settings_window = tk.Toplevel(root)
    settings_window.transient(root)
    settings_window.resizable(False, False)
    settings_window.title("Settings")
    
    theme_frame = ttk.LabelFrame(settings_window, text="UI theme")
    theme_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")
    
    light_radio = ttk.Radiobutton(theme_frame, text="Light mode", variable=dark_mode, value=0, command=change_appearance)
    light_radio.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
    
    dark_radio = ttk.Radiobutton(theme_frame, text="Dark mode", variable=dark_mode, value=1, command=change_appearance)
    dark_radio.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="w")
    
    theme_label = ttk.Label(theme_frame, text="Restart needed after changing these options!")
    theme_label.grid(row=3, column=0, padx=10, pady=(5, 10))
    
#     font_button = ttk.Button(settings_window, text="Change font", command=change_font)
#     font_button.grid(row=4, column=0, padx=10, pady=(10, 5))

    if not os.path.exists("Azure-ttk-theme-main") and check_internet():
        azure_frame = ttk.LabelFrame(settings_window, text="Azure theme")
        azure_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nswe")
        
        azure_label = ttk.Label(azure_frame, text="Download my beautiful Azure theme for Brainfuck IDE")
        azure_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        
        azure_button = ttk.Button(azure_frame, text="Download", command=download_azure)
        azure_button.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="we")
        
        azure_link = widgets.LinkLabel(azure_frame, text="Visit it on GitHub", url="https://github.com/rdbende/Azure-ttk-theme")
        azure_link.grid(row=1, column=1, padx=10, pady=(5, 10))
        
    elif os.path.exists("Azure-ttk-theme-main"):
        azure_switch = ttk.Checkbutton(theme_frame, text="Azure theme", variable=use_azure, command=change_appearance)
        azure_switch.grid(row=2, column=0, padx=10, pady=(5, 5), sticky="w")
        try:
            azure_switch.config(style="Switch")
        except:
            pass

    def download_azure():
        import requests
        import zipfile
        
        global use_azure
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
        
        use_azure.set(True)
        
        change_appearance()
        azure_progress.config(value=100)
        azure_progress.update()


def about(*args):
    about_window = tk.Toplevel(root)
    about_window.transient(root)
    about_window.resizable(False, False)
    about_window.title("About Brainfuck IDE")
    
    about_frame = tk.Frame(about_window)
    about_frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    image_label = tk.Label(about_frame, image=brainfuck_image, compound="center")
    image_label.grid(row=0, column=0, pady=5)
    
    credit_label = ttk.Label(about_frame, text="Copyright (c) 2021 rdbende")
    credit_label.grid(row=1, column=0, pady=5)
    
    version_label = ttk.Label(about_frame, text="v1.0")
    version_label.grid(row=2, column=0, pady=5)
    
    version_label = widgets.LinkLabel(about_frame, text="Visit repo on GitHub", url="https://github.com/rdbende/Brainfuck-IDE")
    version_label.grid(row=3, column=0, pady=5)
    
    
def exit():
    if interpreter.running:
        msg = messagebox.askyesno("Program is running!", "Your program is still running!\nDo you want to kill it?")
        if msg:
            stop()
            time.sleep(0.001) # The sleep is needed, because the thread does not stop immediately
            with open('settings.ini', 'w') as file:
                # I can't simply write exit(), because if the program contains an unopened brace, you can't stop it
                config["settings"]["dark_mode"] = str(dark_mode.get())
                config["settings"]["use_azure"] = str(int(use_azure.get()))
                config["files"]["current"] = current_file
                config.write(file)
            root.destroy()
            
    elif editor_box.dirty:
        msg = messagebox.askyesnocancel("File not saved", "Do you want to save your file?")
        if msg:
            editor_box.dirty = False
            save_file()
            exit()
        elif msg is False:
            editor_box.dirty = False
            exit()
    else: 
        with open('settings.ini', 'w') as file:
            config["settings"]["dark_mode"] = str(dark_mode.get())
            config["settings"]["use_azure"] = str(int(use_azure.get()))
            config["files"]["current"] = current_file
            config.write(file)
        root.destroy()


# def change_font():
#     def font(font_settings):
#         global current_font
#         current_font = font_settings
#     
#     root.tk.call("tk", "fontchooser", "configure", "-command", root._register(font))
#     root.tk.eval("tk fontchooser show")



menubar = tk.Menu(relief="flat")

file_menu = tk.Menu(menubar, tearoff=False, bd=0)
file_menu.add_command(label="New", command=new_file, accelerator=new_accel)
file_menu.add_command(label="Open", command=open_file, accelerator=open_accel)
file_menu.add_command(label="Save", command=save_file, accelerator=save_accel)
file_menu.add_command(label="Save as", command=save_as_file, accelerator=saveas_accel)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit, accelerator=quit_accel)

help_menu = tk.Menu(menubar, tearoff=False, bd=0)
help_menu.add_command(label="About", command=about)
help_menu.add_command(label="What is Brainfuck?", command=open_wiki)

menubar.add_cascade(menu=file_menu, label="File")
menubar.add_command(label="Settings", command=settings)
menubar.add_cascade(menu=help_menu, label="Help")
menubar.add_command(label="    ", state="disabled")
menubar.add_command(label="Run", command=run)
menubar.add_command(label="Stop", command=stop)



main_paned = ttk.PanedWindow(root)


editor_box = widgets.Editor(main_paned)
main_paned.add(editor_box, weight=1)


io_paned = ttk.PanedWindow(root, orient="horizontal")
main_paned.add(io_paned, weight=2)


input_box = widgets.Input(io_paned)
io_paned.add(input_box, weight=1)


output_box = widgets.Output(io_paned)
io_paned.add(output_box, weight=1)


main_paned.pack(expand=True, fill="both")


change_appearance()
show_file()
save_file()


# root.bind("<FocusIn>", ask_reload)
root.bind("<<Compare>>", compare)
root.bind_all("<F5>", run)
root.bind_all(settings_keys, settings)
root.bind_all(new_keys, new_file)
root.bind_all(open_keys, open_file)
root.bind_all(save_keys, save_file)
root.bind_all(saveas_keys, save_as_file)
root.protocol("WM_DELETE_WINDOW", exit)

root.config(menu=menubar)


root.mainloop()