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

    def make_car(self):
        random_car = random.randint(1, 6)
        if random_car == 1:
            rand_y = random.randint(-200, 200)
            car = Turtle(shape="square")
            car.shapesize(stretch_len=2, stretch_wid=1)
            car.color(random.choice(COLORS))
            car.penup()
            car.setheading(180)
            car.goto(350, rand_y)
            self.all_cars.append(car)

    def move_cars(self):
        for cars in self.all_cars:
            cars.forward(STARTING_DISTANCE)
