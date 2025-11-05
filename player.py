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

    def get_bounds(self):
        # AABB碰撞检测：返回玩家的边界框
        x, y = self.position()
        return (x - 10, y - 10, x + 10, y + 10)

