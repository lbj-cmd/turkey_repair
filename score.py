from turtle import Turtle
ALIGN = "center"
GO_FONT = ("System", 20, "bold")
LV_FONT = ("System", 13, "normal")
class Score(Turtle):

    def __init__(self):
        super().__init__()
        self.color("white")
        self.penup()
        self.hideturtle()
        self.level = 1
        self.update_level()
        self.drive_speed = 0.1

    def update_level(self):
        self.clear()
        self.goto(-240, 260)
        self.write(f"Level: {self.level}", align=ALIGN, font=LV_FONT)

    def new_level(self):
        self.level += 1
        self.update_level()

    def game_over(self):
        self.goto(0, 0)
        self.write("GAME OVER", align=ALIGN, font=GO_FONT)
