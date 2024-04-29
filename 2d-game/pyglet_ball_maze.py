import pyglet
from pyglet import shapes, clock, text
import random
import time
import numpy as np
import sys
from time import sleep
from DIPPID import SensorUDP

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
PORT = 5700
sensor = SensorUDP(PORT)

BALL_SPEED = 3 #adjust to make game easier or harder

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
#https://stackoverflow.com/a/42481452
pyglet.gl.glClearColor(0.62,0.79,0.49,1)

#https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#
#https://www.zapsplat.com/music/object-drop-in-bath-water-splash/
sound_water = pyglet.media.load('sounds/water.mp3', streaming=False)
#https://www.zapsplat.com/music/game-tone-bright-and-positive-musical-tone-good-for-winning-award-or-point-or-success-version-1/
sound_win = pyglet.media.load('sounds/win.mp3', streaming=False)
player = pyglet.media.Player()

#https://pyglet.readthedocs.io/en/latest/modules/shapes.html
batch = pyglet.graphics.Batch()

labyrinth_line_coords = [
    #horizontal
    (0, 350, 75, 350),
    (100, 450, 300, 450),
    (475, 525, 525, 525),
    (350, 425, 400, 425),
    (450, 425, 475, 425),
    (250, 375, 350, 375),
    (425, 375, 450, 375),
    (525, 400, 600, 400),
    (100, 300, 150, 300),
    (375, 325, 425, 325),
    (475, 325, 525, 325),
    (300, 275, 375, 275),
    (450, 275, 475, 275),
    (100, 150, 200, 150),
    (75, 200, 100, 200),
    (200, 225, 275, 225),
    (200, 75, 400, 75),
    (375, 150, 500, 150),
    #vertical
    (75, 350, 75, 400),
    (100, 450, 100, 500),
    (100, 0, 100, 300),
    (150, 300, 150, 450),
    (200, 550, 200, 600),
    (300, 450, 300, 500),
    (250, 225, 250, 375),
    (275, 75, 275, 225),
    (350, 375, 350, 425),
    (375, 150, 375, 325),
    (275, 75, 275, 225),
    (400, 425, 400, 600),
    (425, 325, 425, 375),
    (450, 375, 450, 425),
    (475, 425, 475, 525),
    (525, 475, 525, 525),
    (450, 375, 450, 425),
    (525, 325, 525, 400),
    (475, 275, 475, 325),
    (500, 0, 500, 250),
]

hole_coords = [
    (25, 125),
    (25, 325),
    (25, 575),
    (50, 375),
    (125, 25),
    (125, 125),
    (125, 175),
    (125, 275),
    (125, 475),
    (175, 575),
    (175, 425),
    (225, 575),
    (225, 250),
    (250, 200),
    (275, 475),
    (275, 350),
    (300, 100),
    (325, 400),
    (350, 250),
    (375, 575),
    (375, 400),
    (400, 175),
    (425, 575),
    (475, 175),
    (475, 125),
    (475, 25),
    (500, 450),
    (525, 250),
    (525, 125),
    (575, 575),
    (575, 375),
    (575, 175)
]

labyrinth_lines = []
for x1, y1, x2, y2 in labyrinth_line_coords:
    line = shapes.Line(x1, y1, x2, y2, width = 2, color=(95, 120, 74), batch = batch)
    labyrinth_lines.append(line)

holes = []
for x, y in hole_coords:
    hole = shapes.Circle(x, y, radius = 20, color=(94, 172, 204, 200), batch = batch)
    holes.append(hole)

start_point = (50, 50)
finish_rect = shapes.Rectangle(500, 0, 100, 100, color=(101, 100, 100, 100), batch = batch)

text_finish = pyglet.text.HTMLLabel('YOU WIN',
                                    x=window.width//2, y=window.height//2,
                                    anchor_x='center', anchor_y='center')
text_finish.set_style('color', (0, 0, 0, 255))
text_finish.set_style('bold', True)
text_finish.set_style('font_name', 'Courier New')
text_finish.set_style('font_size', 80) 

draw_text = False

#from lecture: pyglet_click.py
def measure_distance(x1, y1, x2, y2):
    distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return distance
    
class Ball:
    def __init__(self):
        self.ball = shapes.Circle(50, 50, radius=10, color=(102, 51, 0))
        self.x_movement = 0
        self.y_movement = 0     

    def move(self):
        for line in labyrinth_lines:
            self.adjust_ball_movement(line)
        self.ball.y = self.ball.y + self.y_movement
        self.ball.x = self.ball.x + self.x_movement
        self.check_ball_in_hole()
        self.check_ball_outside_window()
        self.check_game_finish()

    def check_ball_outside_window(self):
        if(self.ball.y < self.ball.radius):
            self.ball.y = self.ball.radius
        if(self.ball.x < self.ball.radius):
            self.ball.x = self.ball.radius
        if(self.ball.y > window.height - self.ball.radius):
            self.ball.y = window.height - self.ball.radius
        if(self.ball.x > window.width - self.ball.radius):
            self.ball.x = window.width - self.ball.radius
    
    def adjust_ball_movement(self, line):
        if(line.x == line.x2): #vertical line
            #check if ball is in width of line
            if((min(line.y, line.y2) - self.ball.radius < self.ball.y < max(line.y, line.y2) + self.ball.radius)):
                if(self.x_movement > 0):
                    if(self.ball.x + self.ball.radius < line.x < self.ball.x + self.ball.radius + self.x_movement): 
                        #ball crosses line from left
                        self.ball.x = line.x - self.ball.radius - 1
                        self.x_movement = 0
                else:
                    if(self.ball.x - self.ball.radius > line.x > self.ball.x - self.ball.radius + self.x_movement):
                        #ball crosses line from right
                        self.ball.x = line.x + self.ball.radius + 1 
                        self.x_movement = 0
            if(self.ball.x - self.ball.radius < line.x < self.ball.x + self.ball.radius): #ball in width of line
                if((measure_distance(line.x, line.y, self.ball.x + self.x_movement, self.ball.y + self.y_movement) < self.ball.radius)
                   or (measure_distance(line.x2, line.y2, self.ball.x + self.x_movement, self.ball.y + self.y_movement) < self.ball.radius)):
                    #ball would cross line end
                    self.y_movement = 0 
        if(line.y == line.y2): #horizontal line
            #check if ball is in width of line
            if((min(line.x, line.x2) - self.ball.radius < self.ball.x < max(line.x, line.x2) + self.ball.radius)):
                if(self.y_movement > 0):
                    if(self.ball.y + self.ball.radius < line.y < self.ball.y + self.ball.radius + self.y_movement): 
                        #ball crosses line from underneath
                        self.ball.y = line.y - self.ball.radius - 1
                        self.y_movement = 0
                else:
                    if(self.ball.y - self.ball.radius > line.y > self.ball.y - self.ball.radius + self.y_movement):
                        #ball crosses line from above
                        self.ball.y = line.y + self.ball.radius + 1 
                        self.y_movement = 0
            if(self.ball.y - self.ball.radius < line.y < self.ball.y + self.ball.radius): #ball in height of line
                if((measure_distance(line.x, line.y, self.ball.x + self.x_movement, self.ball.y + self.y_movement) < self.ball.radius)
                   or (measure_distance(line.x2, line.y2, self.ball.x + self.x_movement, self.ball.y + self.y_movement) < self.ball.radius)):
                    #ball would cross line end
                    self.x_movement = 0 

    def draw(self):
        self.ball.draw()

    def check_ball_in_hole(self):
        for hole in holes:
            if(abs(self.ball.x - hole.x) < hole.radius and abs(self.ball.y - hole.y) < hole.radius):
                player.queue(sound_water)
                player.play()
                self.ball.position = start_point

    def check_game_finish(self):
        global draw_text
        if((finish_rect.x <= self.ball.x <= finish_rect.x + finish_rect.width)
           and (finish_rect.y <= self.ball.y <= finish_rect.y + finish_rect.height)):
            if(not draw_text): #only play on first entering
                player.queue(sound_win)
                player.play()
                draw_text = True
        else: draw_text = False

ball = Ball()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        window.close()

@window.event
def on_draw():
    window.clear()
    ball.draw()
    batch.draw()
    if(draw_text):
        text_finish.draw()

def handle_angle(data):
    ball.x_movement = data.get("pitch") * BALL_SPEED
    ball.y_movement = -data.get("roll") * BALL_SPEED
    ball.move()

sensor.register_callback('rotation', handle_angle)

pyglet.app.run()
