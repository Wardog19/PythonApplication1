
import sys
import math
from PyQt5.QtCore import QTimer, QPointF, Qt, QEvent
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QCursor
from PyQt5.QtWidgets import QApplication, QWidget
from pynput import keyboard
import win32gui
import win32con
import win32api

class Ball:
    def __init__(self, x, y, radius, color, control_key=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.control_key = control_key
        self.follow_mouse = False
        self.velocity = (0, 0)
        self.collision_point = None
        self.new_velocity = None
        self.secondary_collision_point = None
        self.secondary_collision_other = None
        self.secondary_velocity = None

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def calculate_collision_point(self, other):
        direction_x, direction_y = self.velocity
        distance = math.sqrt(direction_x**2 + direction_y**2)
        if distance == 0:
            print("Distance is zero; no movement direction.")
            return None
        step_x = direction_x / distance
        step_y = direction_y / distance

        # Starten der Simulation vom Rand der Hauptkugel
        sim_x = self.x + step_x * self.radius
        sim_y = self.y + step_y * self.radius
        previous_distance = float('inf')

        while True:
            sim_x += step_x
            sim_y += step_y
            current_distance = math.sqrt((sim_x - other.x)**2 + (sim_y - other.y)**2)
            if current_distance <= self.radius + other.radius:
                normal = (other.x - sim_x, other.y - sim_y)
                normal_length = math.sqrt(normal[0]**2 + normal[1]**2)
                if normal_length == 0:
                    print("Normal length is zero; collision undefined.")
                    return None
                normal = (normal[0] / normal_length, normal[1] / normal_length)

                # Berechne den Kollisionspunkt am Rand der getroffenen Kugel
                contact_x = other.x - normal[0] * other.radius
                contact_y = other.y - normal[1] * other.radius
                self.collision_point = (contact_x, contact_y)
                self.collision_other = other  # Speichern der Referenz auf die andere Kugel

                # Berechne die neue Geschwindigkeit der getroffenen Kugel
                self.new_velocity = (
                    normal[0] * distance,
                    normal[1] * distance
                )
                print(f"Collision point: {self.collision_point}, New velocity: {self.new_velocity}")
                return
            if previous_distance <= current_distance:
                print("Moving away from collision point.")
                return
            previous_distance = current_distance
    pass

    def calculate_secondary_collision_point(self, other_balls):
        if self.new_velocity is None or self.collision_point is None:
            print("No new velocity or collision point found for secondary collision.")
            return None

        # Klone die getroffene Kugel (self.collision_other) und bewege sie entlang der new_velocity
        virtual_ball = Ball(self.collision_point[0], self.collision_point[1], 
                            self.collision_other.radius, self.collision_other.color)
        virtual_ball.velocity = self.new_velocity

        direction_x, direction_y = virtual_ball.velocity
        distance = math.sqrt(direction_x**2 + direction_y**2)
        if distance == 0:
            print("Distance is zero; cannot move virtual ball.")
            return None

        step_x = direction_x / distance
        step_y = direction_y / distance

        # Starten der Simulation vom Kollisionspunkt
        sim_x = virtual_ball.x + step_x * virtual_ball.radius
        sim_y = virtual_ball.y + step_y * virtual_ball.radius
        previous_distance = float('inf')

        while True:
            sim_x += step_x
            sim_y += step_y

            for other in other_balls:
                if other == self.collision_other or other == self:
                    continue
                current_distance = math.sqrt((sim_x - other.x)**2 + (sim_y - other.y)**2)
                if current_distance <= virtual_ball.radius + other.radius:
                    print(f"Secondary collision detected with {other}")
                    normal = (other.x - sim_x, other.y - sim_y)
                    normal_length = math.sqrt(normal[0]**2 + normal[1]**2)
                    if normal_length == 0:
                        print("Normal length is zero; cannot determine collision normal.")
                        return None
                    normal = (normal[0] / normal_length, normal[1] / normal_length)

                    # Berechne den Kollisionspunkt am Rand der getroffenen Kugel
                    contact_x = other.x - normal[0] * other.radius
                    contact_y = other.y - normal[1] * other.radius
                    self.secondary_collision_point = (contact_x, contact_y)
                    self.secondary_collision_other = other  # Speichern der Referenz auf die andere Kugel
                
                    # Berechne die sekundäre Geschwindigkeit der getroffenen Kugel
                    impact_speed = math.sqrt(self.new_velocity[0]**2 + self.new_velocity[1]**2)
                    secondary_velocity_x = normal[0] * impact_speed
                    secondary_velocity_y = normal[1] * impact_speed
                    self.secondary_velocity = (secondary_velocity_x, secondary_velocity_y)
                    print(f"Secondary collision point: {self.secondary_collision_point}, Secondary velocity: {self.secondary_velocity}")
                    return
                if current_distance > previous_distance:
                    print("Moving away from secondary collision point.")
                    return
                previous_distance = current_distance
            pass
    pass

class BilliardWidget(QWidget):
    def __init__(self, balls, app_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.balls = balls
        self.app_instance = app_instance  # Speichern der app_instance
        self.mouse_pos = QPointF(0, 0)
        self.setMouseTracking(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.initUI()
        self.freeze_mouse = False
        self.l_alt_pressed = False
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        
    def event(self, event):
        if event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
        return super().event(event)

    def initUI(self):
        self.setWindowTitle('Transparent Billiard Overlay')
        self.setGeometry(100, 100, 1600, 900)
        self.show()

    def on_press(self, key):
        if key == keyboard.Key.alt_l:
            self.l_alt_pressed = True
            self.bring_to_foreground()
            print("L-ALT gedrückt und Fenster in den Vordergrund gebracht.")
        
    def on_release(self, key):
        if key == keyboard.Key.alt_l:
            self.l_alt_pressed = False
            print("L-ALT losgelassen.")
        
    def bring_to_foreground(self):
        hwnd = self.winId().__int__()
        win32gui.SetForegroundWindow(hwnd)
        self.setFocus()  # Setzt den Fokus auf das Fenster
        # L-ALT-Taste loslassen, um potenzielle Blockaden zu vermeiden
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        try:
            self.drawBalls(qp)
            self.drawGuidelines(qp)
            self.drawCollisionPoints(qp)
        except Exception as e:
            print(f"Error in paintEvent: {e}")

    def drawBalls(self, qp):
        for ball in self.balls:
            color = QColor(*ball.color)
            color.setAlphaF(0.8)
            qp.setBrush(QBrush(color))
            qp.setPen(Qt.NoPen)
            qp.drawEllipse(QPointF(ball.x, ball.y), ball.radius, ball.radius)

    def drawGuidelines(self, qp):
        for ball in self.balls:
            self.drawBallGuidelines(qp, ball)

    def drawBallGuidelines(self, qp, ball):
        if ball == self.balls[0]:
            direction = QPointF(self.mouse_pos.x() - ball.x, self.mouse_pos.y() - ball.y)
            length = math.sqrt(direction.x()**2 + direction.y()**2)
            if length == 0:
                return
            direction.setX(direction.x() / length)
            direction.setY(direction.y() / length)

            ball.velocity = (direction.x(), direction.y())
        else:
            if ball.new_velocity:
                direction = QPointF(ball.new_velocity[0], ball.new_velocity[1])
            else:
                direction = QPointF(ball.velocity[0], ball.velocity[1])

        length = 1600

        qp.setPen(QPen(Qt.white, 1, Qt.SolidLine))
        qp.drawLine(QPointF(ball.x, ball.y), QPointF(ball.x + direction.x() * length, ball.y + direction.y() * length))

        normal = QPointF(-direction.y(), direction.x())
        qp.setPen(QPen(Qt.yellow, 1, Qt.DotLine))
        qp.drawLine(QPointF(ball.x + normal.x() * ball.radius, ball.y + normal.y() * ball.radius),
                    QPointF(ball.x + normal.x() * ball.radius + direction.x() * length,
                            ball.y + normal.y() * ball.radius + direction.y() * length))
        qp.drawLine(QPointF(ball.x - normal.x() * ball.radius, ball.y - normal.y() * ball.radius),
                    QPointF(ball.x - normal.x() * ball.radius + direction.x() * length,
                            ball.y - normal.y() * ball.radius + direction.y() * length))

        # Zeichnen der Kollisionslinie durch den Kollisionspunkt und Mittelpunkt
        if ball.collision_point:
            coll_x, coll_y = ball.collision_point
            center_x, center_y = ball.collision_other.x, ball.collision_other.y
            ref_dir_x = center_x - coll_x
            ref_dir_y = center_y - coll_y
            ref_length = math.sqrt(ref_dir_x**2 + ref_dir_y**2)
            if ref_length != 0:
                ref_dir_x /= ref_length
                ref_dir_y /= ref_length

                # Zeichne die Linie durch den Kollisionspunkt und den Mittelpunkt der Kugel
                qp.setPen(QPen(Qt.cyan, 1, Qt.SolidLine))
                qp.drawLine(QPointF(coll_x, coll_y), QPointF(center_x, center_y))
                # Verlängere die Linie durch den Mittelpunkt hinaus
                qp.drawLine(QPointF(center_x, center_y), 
                            QPointF(center_x + ref_dir_x * 1600, center_y + ref_dir_y * 1600))

                # Zeichnen der parallelen Linien
                self.drawParallelLines(qp, coll_x, coll_y, center_x, center_y, ball.radius)

                # Kollisionserkennung für die getroffene Kugel
                if ball.collision_other:
                    ball.collision_other.calculate_secondary_collision_point(self.balls)
                    self.drawSecondaryGuidelines(qp, ball.collision_other)

    def drawParallelLines(self, qp, coll_x, coll_y, center_x, center_y, radius):
        # Berechnung der Richtung der Linie
        direction = QPointF(center_x - coll_x, center_y - coll_y)
        length = math.sqrt(direction.x()**2 + direction.y()**2)
        if length == 0:
            return
        direction.setX(direction.x() / length)
        direction.setY(direction.y() / length)

        # Berechnung der Normalen zur Linie
        normal = QPointF(-direction.y(), direction.x())

        # Berechnung der Punkte für die parallelen Linien
        offset_up = QPointF(coll_x + normal.x() * radius, coll_y + normal.y() * radius)
        offset_down = QPointF(coll_x - normal.x() * radius, coll_y - normal.y() * radius)
        end_up = QPointF(center_x + normal.x() * radius, center_y + normal.y() * radius)
        end_down = QPointF(center_x - normal.x() * radius, center_y - normal.y() * radius)

        # Zeichnen der oberen parallelen Linie
        qp.setPen(QPen(Qt.green, 1, Qt.SolidLine))
        qp.drawLine(QPointF(offset_up.x(), offset_up.y()), QPointF(end_up.x(), end_up.y()))
        qp.drawLine(QPointF(end_up.x(), end_up.y()), QPointF(end_up.x() + direction.x() * 1600, end_up.y() + direction.y() * 1600))

        # Zeichnen der unteren parallelen Linie
        qp.drawLine(QPointF(offset_down.x(), offset_down.y()), QPointF(end_down.x(), end_down.y()))
        qp.drawLine(QPointF(end_down.x(), end_down.y()), QPointF(end_down.x() + direction.x() * 1600, end_down.y() + direction.y() * 1600))

    def drawSecondaryGuidelines(self, qp, ball):
        if ball.secondary_collision_point:
            coll_x, coll_y = ball.secondary_collision_point
            center_x, center_y = ball.secondary_collision_other.x, ball.secondary_collision_other.y
            ref_dir_x = center_x - coll_x
            ref_dir_y = center_y - coll_y
            ref_length = math.sqrt(ref_dir_x**2 + ref_dir_y**2)
            if ref_length != 0:
                ref_dir_x /= ref_length
                ref_dir_y /= ref_length

                # Zeichne die sekundäre Kollisionslinie
                qp.setPen(QPen(Qt.magenta, 1, Qt.SolidLine))
                qp.drawLine(QPointF(coll_x, coll_y), QPointF(center_x, center_y))
                qp.drawLine(QPointF(center_x, center_y), 
                            QPointF(center_x + ref_dir_x * 1600, center_y + ref_dir_y * 1600))

    def drawCollisionPoints(self, qp):
        for ball in self.balls:
            if ball.collision_point:
                x, y = ball.collision_point
                qp.setPen(QPen(Qt.white, 2))
                qp.drawPoint(QPointF(x, y))
            if ball.secondary_collision_point:
                x, y = ball.secondary_collision_point
                qp.setPen(QPen(Qt.red, 2))
                qp.drawPoint(QPointF(x, y))

    def mouseMoveEvent(self, event):
        if self.l_alt_pressed:
            self.mouse_pos = event.pos()
            print(f"Mouse moved to: {self.mouse_pos}")  # Debugging-Ausgabe
            for ball in self.balls:
                if ball.follow_mouse:
                    new_x = self.mouse_pos.x()
                    new_y = self.mouse_pos.y()
                    can_move = True
                    for other in self.balls:
                        if other != ball and self.would_collide(ball, new_x, new_y, other):
                            can_move = False
                            break
                    if can_move:
                        ball.set_position(new_x, new_y)
            self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.freeze_mouse = not self.freeze_mouse
            if self.freeze_mouse:
                QCursor.setPos(self.mapToGlobal(self.rect().center()))
        else:
            for ball in self.balls:
                if event.key() == ball.control_key:
                    ball.follow_mouse = True

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.freeze_mouse = False
        else:
            for ball in self.balls:
                if event.key() == ball.control_key:
                    ball.follow_mouse = False

    def would_collide(self, ball, new_x, new_y, other):
        dx = new_x - other.x
        dy = new_y - other.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance < ball.radius + other.radius

class BilliardApp:
    def __init__(self):
        self.balls = [
            Ball(100, 100, 18, (255, 0, 0), control_key=Qt.Key_1),
            Ball(200, 150, 18, (0, 255, 0), control_key=Qt.Key_2),
            Ball(300, 200, 18, (0, 0, 255), control_key=Qt.Key_3)
        ]
        self.app = QApplication(sys.argv)
        self.widget = BilliardWidget(self.balls, self)  # Übergabe der app_instance
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS
        self.paused = False  # Initialisieren des Pausenstatus
        self.previous_positions = [(ball.x, ball.y) for ball in self.balls]

    def update(self):
        if not self.paused:
            try:
                main_ball = self.balls[0]
                main_ball.collision_point = None
                main_ball.new_velocity = None
                main_ball.secondary_collision_point = None
                main_ball.secondary_collision_other = None
                for other_ball in self.balls[1:]:
                    main_ball.calculate_collision_point(other_ball)
                self.widget.update()
            except Exception as e:
                print(f"Error in update: {e}")

    def run(self):
        sys.exit(self.app.exec_())

    def set_paused(self, paused):
        self.paused = paused

if __name__ == '__main__':
    app = BilliardApp()
    app.run()

