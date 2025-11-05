from turtle import Turtle


class Art:

    def __init__(self):
        self.pave()

    def pave(self):
        berm = Turtle()
        berm.shape("square")
        berm.color("#6FF584")
        berm.penup()
        berm.shapesize(stretch_wid=25, stretch_len=30)
        berm.goto(0, 0)

        strip = Turtle()
        strip.shape("square")
        strip.color("#BC2BFF")
        strip.penup()
        strip.shapesize(stretch_wid=24, stretch_len=30)
        strip.goto(0, 0)

        road = Turtle()
        road.shape("square")
        road.color("black")
        road.penup()
        road.shapesize(stretch_wid=23.5, stretch_len=30)
        road.goto(0, 0)

        center_lines1 = Turtle()
        center_lines1.shape("square")
        center_lines1.color("#62EFFF")
        center_lines1.penup()
        center_lines1.shapesize(stretch_wid=.1, stretch_len=30)
        center_lines1.goto(0, -100)

        center_lines2 = Turtle()
        center_lines2.shape("square")
        center_lines2.color("#62EFFF")
        center_lines2.penup()
        center_lines2.shapesize(stretch_wid=.1, stretch_len=30)
        center_lines2.goto(0, 100)
