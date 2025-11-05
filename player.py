from turtle import Turtle

START_POS = (0, -280)
MOVE_DISTANCE = 10
FINISH_LINE = 280
UP = 90


class TurtlePlayer(Turtle):

    def __init__(self):
        super().__init__()
        self.shape("turtle")
        self.color("#FF6600")
        self.penup()
        self.goto(START_POS)
        self.setheading(UP)

    def up(self):
        self.forward(MOVE_DISTANCE)

    def reset(self):
        self.goto(START_POS)

