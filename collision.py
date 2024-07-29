import math

def detect_collision(ball1_coords, ball2_coords):
    ball1_center_x = (ball1_coords[0] + ball1_coords[2]) / 2
    ball1_center_y = (ball1_coords[1] + ball1_coords[3]) / 2
    ball2_center_x = (ball2_coords[0] + ball2_coords[2]) / 2
    ball2_center_y = (ball2_coords[1] + ball2_coords[3]) / 2

    ball1_radius = (ball1_coords[2] - ball1_coords[0]) / 2
    ball2_radius = (ball2_coords[2] - ball2_coords[0]) / 2

    distance = math.sqrt((ball1_center_x - ball2_center_x)**2 + (ball1_center_y - ball2_center_y)**2)
    return distance <= (ball1_radius + ball2_radius)

def detect_wall_collision(ball_coords, field_x1, field_y1, field_x2, field_y2, ball_radius):
    ball_left, ball_top, ball_right, ball_bottom = ball_coords
    collided = False
    if ball_left <= field_x1 or ball_right >= field_x2:
        collided = True
    if ball_top <= field_y1 or ball_bottom >= field_y2:
        collided = True
    return collided
