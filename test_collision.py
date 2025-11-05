import turtle
import time
import random

# Test collision detection
def test_collision():
    # Create a simple test
    screen = turtle.Screen()
    screen.setup(width=600, height=600)
    
    # Create player
    player = turtle.Turtle()
    player.shape("turtle")
    player.color("red")
    player.penup()
    player.goto(0, 0)
    
    # Create car
    car = turtle.Turtle()
    car.shape("square")
    car.color("blue")
    car.shapesize(stretch_len=2, stretch_wid=1)
    car.penup()
    car.goto(0, 0)
    
    # Define bounding boxes
    def get_player_bounds():
        x, y = player.position()
        return (x - 10, y - 10, x + 10, y + 10)
    
    def get_car_bounds():
        x, y = car.position()
        return (x - 20, y - 10, x + 20, y + 10)
    
    # Test collision
    player_bounds = get_player_bounds()
    car_bounds = get_car_bounds()
    
    collision = (player_bounds[0] < car_bounds[2] and player_bounds[2] > car_bounds[0] and
                player_bounds[1] < car_bounds[3] and player_bounds[3] > car_bounds[1])
    
    print("Collision detection result:", collision)
    print("Player bounds:", player_bounds)
    print("Car bounds:", car_bounds)
    
    screen.bye()

if __name__ == "__main__":
    test_collision()