import tkinter as tk
import win32api
import win32gui
import win32con
from game_logic import GameLogic
from settings_window import open_settings_window

class OverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-transparentcolor", "white", "-fullscreen", True)
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.game_logic = GameLogic(self.canvas)

        self.root.bind("<ButtonPress-1>", self.on_mouse_press)
        self.root.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.root.bind("<B1-Motion>", self.on_mouse_move)
        self.root.bind("<KeyPress-1>", self.on_key_press_1)
        self.root.bind("<KeyRelease-1>", self.on_key_release_1)
        self.root.bind("<KeyPress-2>", self.on_key_press_2)
        self.root.bind("<KeyRelease-2>", self.on_key_release_2)
        self.root.bind("<KeyPress-3>", self.on_key_press_3)
        self.root.bind("<KeyRelease-3>", self.on_key_release_3)
        self.root.bind("<KeyPress-4>", self.on_key_press_4)
        self.root.bind("<KeyRelease-4>", self.on_key_release_4)
        self.root.bind("<KeyPress-Alt_L>", self.on_alt_press)
        self.root.bind("<KeyRelease-Alt_L>", self.on_alt_release)
        self.root.bind("<KeyPress-Control_L>", self.on_ctrl_press)
        self.root.bind("<KeyRelease-Control_L>", self.on_ctrl_release)

        self.create_settings_window()

        # Adding extra balls
        for color in self.game_logic.ball_colors:
            self.game_logic.add_extra_ball(color)

        self.update_overlay()

    def create_settings_window(self):
        self.settings_window = tk.Toplevel(self.root)
        open_settings_window(self.settings_window, self.game_logic)

    def on_mouse_press(self, event):
        self.game_logic.on_mouse_press(event)

    def on_mouse_release(self, event):
        self.game_logic.on_mouse_release(event)

    def on_mouse_move(self, event):
        if self.game_logic.resizing:
            self.game_logic.resize_field(event.x, event.y)
        elif self.game_logic.dragging:
            self.game_logic.drag_field(event.x, event.y)
        self.game_logic.update_mouse_position(event.x, event.y)

    def on_key_press_1(self, event):
        self.game_logic.one_pressed = True

    def on_key_release_1(self, event):
        self.game_logic.one_pressed = False

    def on_key_press_2(self, event):
        self.game_logic.two_pressed = True

    def on_key_release_2(self, event):
        self.game_logic.two_pressed = False

    def on_key_press_3(self, event):
        self.game_logic.three_pressed = True

    def on_key_release_3(self, event):
        self.game_logic.three_pressed = False

    def on_key_press_4(self, event):
        self.game_logic.four_pressed = True

    def on_key_release_4(self, event):
        self.game_logic.four_pressed = False

    def on_alt_press(self, event):
        self.game_logic.alt_pressed = True
        self.update_rollbahn()

    def on_alt_release(self, event):
        self.game_logic.alt_pressed = False
        self.game_logic.clear_rollbahn()

    def on_ctrl_press(self, event):
        self.root.attributes("-topmost", True)

    def on_ctrl_release(self, event):
        self.root.attributes("-topmost", False)

    def update_rollbahn(self):
        if self.game_logic.alt_pressed:
            self.game_logic.update_rollbahn()
        self.root.after(16, self.update_rollbahn)

    def update_overlay(self):
        self.game_logic.update_ball_position()
        self.root.after(16, self.update_overlay)
