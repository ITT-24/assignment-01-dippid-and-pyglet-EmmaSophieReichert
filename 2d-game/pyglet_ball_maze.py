import pyglet
from pyglet import shapes, clock
import random
import time
import numpy as np
import sys
from time import sleep
from DIPPID import SensorUDP

WINDOW_WIDTH = 620
WINDOW_HEIGHT = 620
PORT = 5700
sensor = SensorUDP(PORT)

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
#https://stackoverflow.com/a/42481452
pyglet.gl.glClearColor(0.9,0.9,1,1)

#https://pyglet.readthedocs.io/en/latest/modules/shapes.html
batch = pyglet.graphics.Batch()

labyrinth_line_coords = [
    (100, 100, 300, 100),
    (100, 100, 100, 300),
    (100, 300, 300, 300),
    (300, 100, 300, 300)
]

labyrinth_lines = []
for x1, y1, x2, y2 in labyrinth_line_coords:
    line = shapes.Line(x1, y1, x2, y2, width = 2, color=(0, 0, 0), batch = batch)
    labyrinth_lines.append(line)

class Ball:
    def __init__(self):
        self.ball = shapes.Circle(x=200, y=200, radius=10, color=(0, 0, 255))
        self.x_movement = 0
        self.y_movement = 0     

    def move(self):
        for line in labyrinth_lines:
            self.adjust_ball_movement(line)
        self.ball.y = self.ball.y + self.y_movement
        self.ball.x = self.ball.x + self.x_movement
        if(self.ball.y < self.ball.radius):
            self.ball.y = self.ball.radius
        elif(self.ball.x < self.ball.radius):
            self.ball.x = self.ball.radius
        elif(self.ball.y > window.height - self.ball.radius):
            self.ball.y = window.height - self.ball.radius
        elif(self.ball.x > window.width - self.ball.radius):
            self.ball.x = window.width - self.ball.radius
    
    def adjust_ball_movement(self, line):
        if line.x == line.x2: #vertical line
            #check if ball is in width of line
            if(min(line.y, line.y2) < self.ball.y + self.y_movement < max(line.y, line.y2)):
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
        if line.y == line.y2: #horizontal line
            #check if ball is in width of line
            if(min(line.x, line.x2) < self.ball.x + self.x_movement < max(line.x, line.x2)):
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

    def draw(self):
        self.ball.draw()

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

def handle_angle(data):
    ball.x_movement = data.get("pitch")/2
    ball.y_movement = -data.get("roll")/2
    ball.move()

sensor.register_callback('rotation', handle_angle)

pyglet.app.run()
