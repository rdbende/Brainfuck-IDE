"""
Author: rdbende
License: GNU GPLv3
Copyright: 2021 rdbende
"""

import platform

class Appearance():
    light_bg = "#eee"
    light_fg = "#0d1117"
    light_insert = "#24292e"
    light_select = "#ccc"
    light_io = "#6f42c1"
    light_var = "#d73a49"
    light_brace = "#6f42c1"
    light_value = "#005cc5"
    light_comment = "#0d1117"
    
    
    dark_bg = "#0d1117"
    dark_fg = "#eee"
    dark_insert = "#c9d1d9"
    dark_select = "#aaa"
    dark_io = "#d2a8ff"
    dark_var = "#ff7b72"
    dark_brace = "#d2a8ff"
    dark_value = "#79c0ff"
    dark_comment = "#767d87"
    
    @classmethod
    def change_appearance(cls, dark_mode):
        if dark_mode:
            cls.bg = cls.dark_bg
            cls.fg = cls.dark_fg
            cls.insert = cls.dark_insert
            cls.select = cls.dark_select
            cls.io = cls.dark_io
            cls.variable = cls.dark_var
            cls.brace = cls.dark_brace
            cls.value = cls.dark_value
            cls.comment = cls.dark_comment
        else:
            cls.bg = cls.light_bg
            cls.fg = cls.light_fg
            cls.insert = cls.light_insert
            cls.select = cls.light_select
            cls.io = cls.light_io
            cls.variable = cls.light_var
            cls.brace = cls.light_brace
            cls.value = cls.light_value
            cls.comment = cls.light_comment

if platform.system() == "darwin":
    new_accel = "Cmd+N"
    new_keys = "<Command-n>"
    open_accel = "Cmd+O"
    open_keys = "<Command-o>"
    save_accel = "Cmd+S"
    save_keys = "<Command-s>"
    saveas_accel = "Cmd+Shift+S"
    saveas_keys = "<Command-Shift-S>"
    settings_keys = "<Command-p>"
    quit_accel = "Cmd+W"
else:
    new_accel = "Ctrl+N"
    new_keys = "<Control-n>"
    open_accel = "Ctrl+O"
    open_keys = "<Control-o>"
    save_accel = "Ctrl+S"
    save_keys = "<Control-s>"
    saveas_accel = "Ctrl+Shift+S"
    saveas_keys = "<Control-Shift-S>"
    settings_keys = "<Control-p>"
    quit_accel = "Alt+F4"
