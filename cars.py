from turtle import Turtle
import random

COLORS = [
    "#FFFF00", "#FFFF33", "#F2EA02", "#E6FB04", "#FF0000", "#FD1C03", "#FF3300", "#00FF00", "#00FF33",
    "#00FF66", "#33FF00", "#00FFFF", "#099FFF", "#0062FF", "#0033FF", "#FF00FF", "#FF00CC", "#FF0099", "#CC00FF",
    "#9D00FF", "#CC00FF", "#6E0DD0", "#9900FF"]
STARTING_DISTANCE = 5


class CarManager:

    def __init__(self):
        self.all_cars = []

    def make_car(self, speed_multiplier=1.0):
        random_car = random.randint(1, 6)
        if random_car == 1:
            rand_y = random.randint(-200, 200)
            car = Turtle(shape="square")
            car.shapesize(stretch_len=2, stretch_wid=1)
            car.color(random.choice(COLORS))
            car.penup()
            car.setheading(180)
            car.goto(350, rand_y)
            # 为汽车添加速度属性
            car.speed = STARTING_DISTANCE * speed_multiplier
            # 为汽车添加get_bounds方法
            def get_bounds(self):
                x, y = self.position()
                return (x - 20, y - 10, x + 20, y + 10)
            car.get_bounds = get_bounds.__get__(car, Turtle)
            self.all_cars.append(car)

    def move_cars(self):
        for car in self.all_cars:
            car.forward(car.speed)
