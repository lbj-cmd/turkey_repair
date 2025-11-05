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
        self.lives = 3  # 默认3条生命
        self.score = 0  # 默认0分
        self.update_level()
        self.drive_speed = 0.1

    def update_level(self):
        self.clear()
        self.goto(-240, 260)
        self.write(f"Level: {self.level}", align=ALIGN, font=LV_FONT)
        # 显示生命值
        self.goto(240, 260)
        self.write(f"Lives: {self.lives}", align=ALIGN, font=LV_FONT)
        # 显示分数
        self.goto(0, 260)
        self.write(f"Score: {self.score}", align=ALIGN, font=LV_FONT)

    def new_level(self):
        self.level += 1
        self.update_level()

    def game_over(self):
        self.goto(0, 0)
        self.write("GAME OVER", align=ALIGN, font=GO_FONT)
        # 显示最终分数
        self.goto(0, -30)
        self.write(f"Final Score: {self.score}", align=ALIGN, font=LV_FONT)
        self.write("GAME OVER", align=ALIGN, font=GO_FONT)
