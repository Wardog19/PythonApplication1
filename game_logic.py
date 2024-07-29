import pyautogui
from collision import detect_collision, detect_wall_collision
import math

class GameLogic:
    def __init__(self, canvas):
        self.canvas = canvas
        self.frame_thickness = 10
        self.frame_color = "blue"
        self.field_x1 = 50
        self.field_y1 = 50
        self.field_x2 = 300
        self.field_y2 = 300
        self.field_frame = self.canvas.create_rectangle(
            self.field_x1, self.field_y1, self.field_x2, self.field_y2,
            outline=self.frame_color, width=self.frame_thickness
        )

        self.ball_radius = 25
        self.main_ball_color = "green"
        self.main_ball = self.canvas.create_oval(
            150 - self.ball_radius, 150 - self.ball_radius,
            150 + self.ball_radius, 150 + self.ball_radius,
            fill=self.main_ball_color, outline="black"
        )

        self.extra_balls = []
        self.ball_colors = ["red", "blue", "yellow"]

        self.mouse_x = 0
        self.mouse_y = 0
        self.one_pressed = False
        self.two_pressed = False
        self.three_pressed = False
        self.four_pressed = False
        self.alt_pressed = False
        self.resizing = False
        self.dragging = False
        self.rollbahn_line = None
        self.balls = [self.main_ball]
        self.trajectory_lines = []

    def add_extra_ball(self, color):
        x, y = 150, 150
        ball = self.canvas.create_oval(
            x - self.ball_radius, y - self.ball_radius,
            x + self.ball_radius, y + self.ball_radius,
            fill=color, outline="black"
        )
        self.extra_balls.append(ball)
        self.balls.append(ball)

    def update_mouse_position(self, x, y):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, event):
        if (self.field_x2 - 10 <= event.x <= self.field_x2 and
            self.field_y2 - 10 <= event.y <= self.field_y2):
            self.resizing = True
        elif (self.field_x1 <= event.x <= self.field_x2 and
              self.field_y1 <= event.y <= self.field_y2):
            self.dragging = True
            self.drag_start_x = event.x
            self.drag_start_y = event.y

    def on_mouse_release(self, event):
        self.resizing = False
        self.dragging = False

    def update_ball_position(self):
        self.mouse_x, self.mouse_y = pyautogui.position()
        canvas_x = self.mouse_x - self.canvas.winfo_rootx()
        canvas_y = self.mouse_y - self.canvas.winfo_rooty()
        
        inner_x1 = self.field_x1 + self.frame_thickness
        inner_y1 = self.field_y1 + self.frame_thickness
        inner_x2 = self.field_x2 - self.frame_thickness
        inner_y2 = self.field_y2 - self.frame_thickness

        x = min(max(canvas_x, inner_x1 + self.ball_radius), inner_x2 - self.ball_radius)
        y = min(max(canvas_y, inner_y1 + self.ball_radius), inner_y2 - self.ball_radius)

        if self.one_pressed:
            ball = self.main_ball
        elif self.two_pressed and len(self.extra_balls) > 0:
            ball = self.extra_balls[0]
        elif self.three_pressed and len(self.extra_balls) > 1:
            ball = self.extra_balls[1]
        elif self.four_pressed and len(self.extra_balls) > 2:
            ball = self.extra_balls[2]
        else:
            return

        self.canvas.coords(
            ball,
            x - self.ball_radius, y - self.ball_radius,
            x + self.ball_radius, y + self.ball_radius
        )

        self.check_collisions()

    def check_collisions(self):
        for ball in self.balls:
            if ball != self.main_ball:
                if detect_collision(self.canvas.coords(self.main_ball), self.canvas.coords(ball)):
                    print("Collision detected")
            if detect_wall_collision(self.canvas.coords(ball), self.field_x1, self.field_y1, self.field_x2, self.field_y2, self.ball_radius):
                print("Wall collision detected")
    def update_rollbahn(self):
        if self.rollbahn_line:
            self.canvas.delete(self.rollbahn_line)
        
        ball_center_x = (self.canvas.coords(self.main_ball)[0] + self.canvas.coords(self.main_ball)[2]) / 2
        ball_center_y = (self.canvas.coords(self.main_ball)[1] + self.canvas.coords(self.main_ball)[3]) / 2

        inner_x1 = self.field_x1 + self.frame_thickness
        inner_y1 = self.field_y1 + self.frame_thickness
        inner_x2 = self.field_x2 - self.frame_thickness
        inner_y2 = self.field_y2 - self.frame_thickness
        
        self.rollbahn_line = self.canvas.create_line(
            ball_center_x, ball_center_y,
            min(max(self.mouse_x, inner_x1), inner_x2),
            min(max(self.mouse_y, inner_y1), inner_y2),
            fill="red", dash=(4, 2), width=2
        )
        self.update_trajectory_lines(ball_center_x, ball_center_y, self.mouse_x, self.mouse_y)

    def update_trajectory_lines(self, x0, y0, x1, y1):
        for line in self.trajectory_lines:
            self.canvas.delete(line)
        self.trajectory_lines = []

        vx = x1 - x0
        vy = y1 - y0

        # Normalize velocity vector
        mag = math.sqrt(vx**2 + vy**2)
        if mag == 0:
            return
        vx /= mag
        vy /= mag

        for ball in self.balls:
            if ball == self.main_ball:
                continue
            bx, by = (self.canvas.coords(ball)[0] + self.canvas.coords(ball)[2]) / 2, (self.canvas.coords(ball)[1] + self.canvas.coords(ball)[3]) / 2
            cx, cy = bx + vx * 100, by + vy * 100
            line = self.canvas.create_line(bx, by, cx, cy, fill="blue", dash=(2, 2))
            self.trajectory_lines.append(line)

    def clear_rollbahn(self):
        if self.rollbahn_line:
            self.canvas.delete(self.rollbahn_line)
            self.rollbahn_line = None
        for line in self.trajectory_lines:
            self.canvas.delete(line)
        self.trajectory_lines = []
    def resize_field(self, x, y):
        min_width, min_height = 50, 50  # Minimum dimensions for the field
        self.field_x2 = max(x, self.field_x1 + min_width)
        self.field_y2 = max(y, self.field_y1 + min_height)
        self.canvas.coords(
            self.field_frame,
            self.field_x1, self.field_y1,
            self.field_x2, self.field_y2
        )
        self.adjust_ball_position()

    def drag_field(self, x, y):
        dx = x - self.drag_start_x
        dy = y - self.drag_start_y
        self.field_x1 += dx
        self.field_y1 += dy
        self.field_x2 += dx
        self.field_y2 += dy
        self.canvas.coords(
            self.field_frame,
            self.field_x1, self.field_y1,
            self.field_x2, self.field_y2
        )
        self.drag_start_x = x
        self.drag_start_y = y
        self.adjust_ball_position(dx, dy)

    def adjust_ball_position(self, dx=0, dy=0):
        ball_coords = self.canvas.coords(self.main_ball)
        new_x = ball_coords[0] + dx
        new_y = ball_coords[1] + dy
        self.update_ball_position()

    def update_ball_diameter(self, diameter):
        self.ball_radius = diameter / 2
        for ball in self.balls:
            ball_coords = self.canvas.coords(ball)
            ball_center_x = (ball_coords[0] + ball_coords[2]) / 2
            ball_center_y = (ball_coords[1] + ball_coords[3]) / 2
            new_coords = [
                ball_center_x - self.ball_radius, 
                ball_center_y - self.ball_radius,
                ball_center_x + self.ball_radius, 
                ball_center_y + self.ball_radius
            ]
            self.canvas.coords(ball, *new_coords)

    def update_field_dimensions(self, width, height):
        self.field_x2 = self.field_x1 + width
        self.field_y2 = self.field_y1 + height
        self.canvas.coords(
            self.field_frame,
            self.field_x1, self.field_y1,
            self.field_x2, self.field_y2
        )
        self.update_ball_position()

    def update_ball_color(self, color):
        self.main_ball_color = color
        self.canvas.itemconfig(self.main_ball, fill=color)

    def update_frame_thickness(self, thickness):
        self.frame_thickness = thickness
        self.canvas.itemconfig(self.field_frame, width=thickness)
        self.update_ball_position()
