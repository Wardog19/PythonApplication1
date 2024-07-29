import tkinter as tk
from tkinter.colorchooser import askcolor

class SettingsWindow:
    def __init__(self, parent, game_logic):
        self.parent = parent
        self.game_logic = game_logic

        self.window = parent
        self.window.title("Settings")

        # Ball Radius
        self.ball_radius_label = tk.Label(self.window, text="Ball Radius:")
        self.ball_radius_label.grid(row=0, column=0)
        self.ball_radius_var = tk.DoubleVar(value=self.game_logic.ball_radius)
        self.ball_radius_entry = tk.Entry(self.window, textvariable=self.ball_radius_var)
        self.ball_radius_entry.grid(row=0, column=1)

        # Field Dimensions
        self.field_width_label = tk.Label(self.window, text="Field Width:")
        self.field_width_label.grid(row=1, column=0)
        self.field_width_var = tk.DoubleVar(value=self.game_logic.field_x2 - self.game_logic.field_x1)
        self.field_width_entry = tk.Entry(self.window, textvariable=self.field_width_var)
        self.field_width_entry.grid(row=1, column=1)

        self.field_height_label = tk.Label(self.window, text="Field Height:")
        self.field_height_label.grid(row=2, column=0)
        self.field_height_var = tk.DoubleVar(value=self.game_logic.field_y2 - self.game_logic.field_y1)
        self.field_height_entry = tk.Entry(self.window, textvariable=self.field_height_var)
        self.field_height_entry.grid(row=2, column=1)

        # Ball Color
        self.ball_color_label = tk.Label(self.window, text="Ball Color:")
        self.ball_color_label.grid(row=3, column=0)
        self.ball_color_button = tk.Button(self.window, text="Choose Color", command=self.choose_ball_color)
        self.ball_color_button.grid(row=3, column=1)

        # Frame Thickness
        self.frame_thickness_label = tk.Label(self.window, text="Frame Thickness:")
        self.frame_thickness_label.grid(row=4, column=0)
        self.frame_thickness_var = tk.DoubleVar(value=self.game_logic.frame_thickness)
        self.frame_thickness_entry = tk.Entry(self.window, textvariable=self.frame_thickness_var)
        self.frame_thickness_entry.grid(row=4, column=1)

        # Extra Balls
        self.extra_ball_vars = []
        self.extra_ball_checks = []
        for i, ball in enumerate(self.game_logic.extra_balls):
            var = tk.BooleanVar(value=True)
            self.extra_ball_vars.append(var)
            check = tk.Checkbutton(self.window, text=f"Extra Ball {i+1}", variable=var)
            check.grid(row=5+i, column=0, columnspan=2)
            self.extra_ball_checks.append(check)

        self.update_button = tk.Button(self.window, text="Update", command=self.update_settings)
        self.update_button.grid(row=5+len(self.extra_ball_vars), column=0, columnspan=2)

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Real-time update bindings
        self.ball_radius_var.trace_add('write', self.real_time_update)
        self.field_width_var.trace_add('write', self.real_time_update)
        self.field_height_var.trace_add('write', self.real_time_update)
        self.frame_thickness_var.trace_add('write', self.real_time_update)

    def real_time_update(self, *args):
        try:
            self.update_settings()
        except tk.TclError:
            pass

    def choose_ball_color(self):
        color_code = askcolor(title="Choose ball color")
        if color_code[1] is not None:
            self.game_logic.update_ball_color(color_code[1])

    def update_settings(self):
        # Update ball radius
        new_radius = self.ball_radius_var.get()
        self.game_logic.update_ball_diameter(new_radius * 2)

        # Update field dimensions
        new_width = self.field_width_var.get()
        new_height = self.field_height_var.get()
        self.game_logic.update_field_dimensions(new_width, new_height)

        # Update frame thickness
        new_thickness = self.frame_thickness_var.get()
        self.game_logic.update_frame_thickness(new_thickness)

        # Update extra balls
        for i, var in enumerate(self.extra_ball_vars):
            if var.get():
                self.game_logic.canvas.itemconfigure(self.game_logic.extra_balls[i], state='normal')
            else:
                self.game_logic.canvas.itemconfigure(self.game_logic.extra_balls[i], state='hidden')

    def on_close(self):
        self.window.destroy()

def open_settings_window(parent, game_logic):
    SettingsWindow(parent, game_logic)