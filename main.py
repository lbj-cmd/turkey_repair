import turtle
import time
import random
import sqlite3
from enum import Enum



# 定义游戏状态
class GameState(Enum):
    MAIN_MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    SHOP = 5

# 全局变量
current_state = GameState.MAIN_MENU

# 游戏设置
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

# 数据库设置
DB_NAME = "turtle_crossing.db"

# 天气系统设置
WEATHER_CYCLE_TIME = 120  # 2分钟的天气循环
RAIN_CHANCE = 0.3  # 30%的几率下雨
RAIN_DURATION = 60  # 下雨持续时间（秒）

# 昼夜循环设置
DAY_NIGHT_CYCLE_TIME = 300  # 5分钟的昼夜循环
DAY_COLOR = (135, 206, 250)  # 白天蓝色
DUSK_COLOR = (255, 165, 0)  # 黄昏橙色
NIGHT_COLOR = (0, 0, 139)  # 夜晚深蓝色

# 天气和时间变量
current_weather = "clear"
rain_start_time = 0
rain_turtles = []
is_night = False
day_night_timer = 0

# 幽灵模式变量
ghost_player = None
best_path = []
ghost_active = False
current_path = []
path_recording_start_time = 0



# 创建屏幕
screen = turtle.Screen()
screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
screen.title("Turtle Crossing")
screen.bgcolor("black")
screen.tracer(0)  # 关闭自动更新



# 数据库初始化
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 创建排行榜表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            level INTEGER,
            score INTEGER,
            date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建商店购买表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upgrade_type TEXT,
            purchased INTEGER DEFAULT 0
        )
    ''')
    
    # 初始化商店升级项
    cursor.execute('''
        INSERT OR IGNORE INTO shop_purchases (upgrade_type, purchased) VALUES
        ('speed_boost', 0),
        ('extra_life', 0)
    ''')
    
    conn.commit()
    conn.close()

# 主菜单绘制类
class MainMenu:
    def __init__(self):
        self.buttons = []
        self.selected_button = 0
        self.draw()
    
    def draw(self):
        screen.clear()
        
        # 绘制标题
        title = turtle.Turtle()
        title.color("#FF6600")
        title.penup()
        title.hideturtle()
        title.goto(0, 150)
        title.write("TURTLE CROSSING", align="center", font=("Arial", 30, "bold"))
        
        # 绘制按钮
        button_y = 50
        button_spacing = 60
        
        # 开始游戏按钮
        start_button = turtle.Turtle()
        start_button.shape("square")
        start_button.color("#00FF00", "#008000")
        start_button.shapesize(stretch_wid=2, stretch_len=10)
        start_button.penup()
        start_button.goto(0, button_y)
        self.buttons.append(start_button)
        
        start_text = turtle.Turtle()
        start_text.color("white")
        start_text.penup()
        start_text.hideturtle()
        start_text.goto(0, button_y)
        start_text.write("开始游戏", align="center", font=("Arial", 16, "bold"))
        
        button_y -= button_spacing
        
        # 排行榜按钮
        leaderboard_button = turtle.Turtle()
        leaderboard_button.shape("square")
        leaderboard_button.color("#00FFFF", "#0080FF")
        leaderboard_button.shapesize(stretch_wid=2, stretch_len=10)
        leaderboard_button.penup()
        leaderboard_button.goto(0, button_y)
        self.buttons.append(leaderboard_button)
        
        leaderboard_text = turtle.Turtle()
        leaderboard_text.color("white")
        leaderboard_text.penup()
        leaderboard_text.hideturtle()
        leaderboard_text.goto(0, button_y)
        leaderboard_text.write("排行榜", align="center", font=("Arial", 16, "bold"))
        
        button_y -= button_spacing
        
        # 商店按钮
        shop_button = turtle.Turtle()
        shop_button.shape("square")
        shop_button.color("#FF00FF", "#8000FF")
        shop_button.shapesize(stretch_wid=2, stretch_len=10)
        shop_button.penup()
        shop_button.goto(0, button_y)
        self.buttons.append(shop_button)
        
        shop_text = turtle.Turtle()
        shop_text.color("white")
        shop_text.penup()
        shop_text.hideturtle()
        shop_text.goto(0, button_y)
        shop_text.write("商店", align="center", font=("Arial", 16, "bold"))
        
        button_y -= button_spacing
        
        # 退出按钮
        exit_button = turtle.Turtle()
        exit_button.shape("square")
        exit_button.color("#FF0000", "#800000")
        exit_button.shapesize(stretch_wid=2, stretch_len=10)
        exit_button.penup()
        exit_button.goto(0, button_y)
        self.buttons.append(exit_button)
        
        exit_text = turtle.Turtle()
        exit_text.color("white")
        exit_text.penup()
        exit_text.hideturtle()
        exit_text.goto(0, button_y)
        exit_text.write("退出", align="center", font=("Arial", 16, "bold"))
    
    def check_click(self, x, y):
        for i, button in enumerate(self.buttons):
            button_x, button_y = button.position()
            if abs(x - button_x) < 100 and abs(y - button_y) < 20:
                return i
        return -1

# 玩家类
class TurtlePlayer(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.shape("turtle")
        self.color("#FF6600")
        self.penup()
        self.goto(0, -280)
        self.setheading(90)
        self.move_distance = 10
        self.current_frame = 1
    
    def up(self):
        self.forward(self.move_distance)
        
        # 下雨时的打滑效果
        if current_weather == "rain" and random.random() < 0.2:
            # 20%的几率打滑
            slip_distance = random.randint(-10, 10)
            self.setx(self.xcor() + slip_distance)
            
            # 确保玩家不会超出屏幕
            if self.xcor() < -280:
                self.setx(-280)
            elif self.xcor() > 280:
                self.setx(280)
        


    
    def reset(self):
        self.goto(0, -280)
    
    def get_bounds(self):
        # AABB碰撞检测：返回玩家的边界框
        x, y = self.position()
        return (x - 10, y - 10, x + 10, y + 10)

# 汽车类
class Car(turtle.Turtle):
    def __init__(self, x, y, color, speed, car_type="car"):
        super().__init__()
        self.car_type = car_type
        self.shape("square")
        self.color(color)
        
        # 根据车辆类型设置不同的大小
        if car_type == "truck":
            self.shapesize(stretch_len=3, stretch_wid=1.5)
            self.speed = speed * 0.5  # 卡车速度慢50%
            self.length = 60  # 碰撞检测长度
        elif car_type == "motorcycle":
            self.shapesize(stretch_len=1, stretch_wid=0.5)
            self.speed = speed * 2.0  # 摩托车速度快100%
            self.length = 20  # 碰撞检测长度
        else:  # 普通汽车
            self.shapesize(stretch_len=2, stretch_wid=1)
            self.speed = speed
            self.length = 40  # 碰撞检测长度
        
        self.penup()
        self.goto(x, y)
        self.setheading(180)
        self.lane = y  # 记录当前车道
        self.original_speed = speed
        self.lights_on = False
        self.light_turtle = None
    
    def move(self):
        self.forward(self.speed)
    
    def get_bounds(self):
        # AABB碰撞检测：返回汽车的边界框
        x, y = self.position()
        half_len = self.length / 2
        if self.car_type == "motorcycle":
            half_wid = 5
        elif self.car_type == "truck":
            half_wid = 15
        else:
            half_wid = 10
        return (x - half_len, y - half_wid, x + half_len, y + half_wid)
    
    def draw_lights(self):
        # 绘制车灯
        if self.lights_on:
            if self.light_turtle:
                self.light_turtle.clear()
            else:
                self.light_turtle = turtle.Turtle()
                self.light_turtle.penup()
                self.light_turtle.hideturtle()
            
            # 绘制黄色光束
            self.light_turtle.color("yellow")
            x, y = self.position()
            
            # 根据车辆类型绘制不同大小的光束
            if self.car_type == "truck":
                # 卡车光束
                self.light_turtle.goto(x - 30, y + 15)
                self.light_turtle.pendown()
                self.light_turtle.begin_fill()
                self.light_turtle.goto(x - 100, y + 25)
                self.light_turtle.goto(x - 100, y - 25)
                self.light_turtle.goto(x - 30, y - 15)
                self.light_turtle.goto(x - 30, y + 15)
                self.light_turtle.end_fill()
                self.light_turtle.penup()
            elif self.car_type == "motorcycle":
                # 摩托车光束
                self.light_turtle.goto(x - 10, y + 5)
                self.light_turtle.pendown()
                self.light_turtle.begin_fill()
                self.light_turtle.goto(x - 50, y + 10)
                self.light_turtle.goto(x - 50, y - 10)
                self.light_turtle.goto(x - 10, y - 5)
                self.light_turtle.goto(x - 10, y + 5)
                self.light_turtle.end_fill()
                self.light_turtle.penup()
            else:
                # 普通汽车光束
                self.light_turtle.goto(x - 20, y + 10)
                self.light_turtle.pendown()
                self.light_turtle.begin_fill()
                self.light_turtle.goto(x - 80, y + 15)
                self.light_turtle.goto(x - 80, y - 15)
                self.light_turtle.goto(x - 20, y - 10)
                self.light_turtle.goto(x - 20, y + 10)
                self.light_turtle.end_fill()
                self.light_turtle.penup()
        else:
            if self.light_turtle:
                self.light_turtle.clear()
                self.light_turtle.hideturtle()
    
    def update_lights(self, is_night):
        # 更新车灯状态
        self.lights_on = is_night
        self.draw_lights()
    
    def clear_lights(self):
        if self.light_turtle:
            self.light_turtle.clear()
            self.light_turtle.hideturtle()

# 汽车管理器类
class CarManager:
    def __init__(self):
        self.all_cars = []
        self.car_colors = ["#FFFF00", "#FF0000", "#00FF00", "#00FFFF", "#FF00FF"]
        self.lanes = list(range(-200, 201, 40))  # 定义固定车道
        self.obstacles = []  # 存储路障
    
    def make_car(self, speed_multiplier=1.0):
        random_car = random.randint(1, 6)
        if random_car == 1:
            lane = random.choice(self.lanes)
            base_speed = 5
            
            # 随机选择车辆类型
            car_type = random.choices(
                ["car", "truck", "motorcycle"],
                weights=[0.7, 0.2, 0.1]  # 70%普通汽车，20%卡车，10%摩托车
            )[0]
            
            car = Car(350, lane, random.choice(self.car_colors), base_speed * speed_multiplier, car_type)
            self.all_cars.append(car)
    
    def move_cars(self):
        for car in self.all_cars:
            # 防追尾逻辑
            self.avoid_collisions(car)
            
            # 躲避路障逻辑
            self.avoid_obstacles(car)
            
            car.move()
    
    def avoid_collisions(self, car):
        # 防追尾逻辑
        for other_car in self.all_cars:
            if car != other_car and abs(car.lane - other_car.lane) < 5:  # 同一车道
                car_x, _ = car.position()
                other_x, _ = other_car.position()
                distance = car_x - other_x
                
                if 0 < distance < 100:  # 前方有车且距离太近
                    car.speed = min(car.speed, other_car.speed * 0.9)  # 减速
                    return
        
        # 如果没有前车，恢复原速
        car.speed = car.original_speed
    
    def avoid_obstacles(self, car):
        # 躲避路障逻辑
        for obstacle in self.obstacles:
            obstacle_x, obstacle_y = obstacle.position()
            car_x, car_y = car.position()
            
            # 检查是否在同一车道且距离太近
            if abs(car_y - obstacle_y) < 10 and obstacle_x < car_x and car_x - obstacle_x < 100:
                # 尝试变道
                new_lane = self.find_safe_lane(car)
                if new_lane is not None:
                    car.lane = new_lane
                    car.sety(new_lane)
                break
    
    def find_safe_lane(self, car):
        # 寻找安全的车道
        for lane in self.lanes:
            if lane != car.lane:
                safe = True
                for other_car in self.all_cars:
                    if abs(other_car.lane - lane) < 5:
                        other_x, _ = other_car.position()
                        car_x, _ = car.position()
                        if abs(other_x - car_x) < 80:
                            safe = False
                            break
                if safe:
                    return lane
        return None
    
    def create_obstacle(self):
        # 随机生成路障
        if random.randint(1, 100) < 5:  # 5%的概率生成路障
            lane = random.choice(self.lanes)
            obstacle = turtle.Turtle()
            obstacle.shape("triangle")
            obstacle.color("red")
            obstacle.shapesize(stretch_wid=1, stretch_len=1)
            obstacle.penup()
            obstacle.goto(350, lane)
            obstacle.setheading(180)
            self.obstacles.append(obstacle)
    
    def move_obstacles(self):
        # 移动路障
        for obstacle in self.obstacles:
            obstacle.forward(3)  # 路障移动速度
    
    def clear_obstacles(self):
        # 清除路障
        for obstacle in self.obstacles:
            obstacle.hideturtle()
        self.obstacles.clear()
    
    def clear_cars(self):
        for car in self.all_cars:
            car.clear_lights()
            car.hideturtle()
        self.all_cars.clear()
    
    def update_car_lights(self, is_night):
        # 更新所有汽车的车灯
        for car in self.all_cars:
            car.update_lights(is_night)

# 分数类
class Score(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.color("white")
        self.penup()
        self.hideturtle()
        self.level = 1
        self.score = 0
        self.update_score()
    
    def update_score(self):
        self.clear()
        self.goto(-240, 260)
        self.write(f"Level: {self.level}", align="center", font=("Arial", 13, "normal"))
        self.goto(240, 260)
        self.write(f"Score: {self.score}", align="center", font=("Arial", 13, "normal"))
    
    def new_level(self):
        self.level += 1
        self.score += 10  # 每关奖励10分
        self.update_score()

    
    def game_over(self):
        self.goto(0, 0)
        self.write("GAME OVER", align="center", font=("Arial", 20, "bold"))

# 粒子效果类
class Particle(turtle.Turtle):
    def __init__(self, x, y):
        super().__init__()
        self.shape("circle")
        self.color(random.choice(["#FF0000", "#FF6600", "#FFFF00"]))
        self.shapesize(stretch_wid=0.5, stretch_len=0.5)
        self.penup()
        self.goto(x, y)
        self.speed = random.randint(5, 15)
        self.direction = random.randint(0, 360)
        self.setheading(self.direction)
    
    def move(self):
        self.forward(self.speed)
        self.speed *= 0.95  # 逐渐减速
    
    def is_dead(self):
        return self.speed < 0.5

# 粒子管理器类
class ParticleManager:
    def __init__(self):
        self.particles = []
    
    def reset(self):
        # 清除所有粒子
        for particle in self.particles:
            particle.hideturtle()
        self.particles.clear()
    
    def create_explosion(self, x, y):
        for _ in range(30):
            particle = Particle(x, y)
            self.particles.append(particle)
    
    def update_particles(self):
        for particle in self.particles[:]:
            particle.move()
            if particle.is_dead():
                particle.hideturtle()
                self.particles.remove(particle)

# 商店类
class Shop:
    def __init__(self):
        self.upgrades = [
            {"name": "速度提升", "type": "speed_boost", "cost": 50, "description": "永久提升10%移动速度"},
            {"name": "额外生命", "type": "extra_life", "cost": 100, "description": "获得额外1条生命"}
        ]
    
    def draw(self):
        screen.clear()
        
        # 绘制标题
        title = turtle.Turtle()
        title.color("#FF6600")
        title.penup()
        title.hideturtle()
        title.goto(0, 200)
        title.write("商店", align="center", font=("Arial", 24, "bold"))
        
        # 绘制当前分数
        score_text = turtle.Turtle()
        score_text.color("white")
        score_text.penup()
        score_text.hideturtle()
        score_text.goto(0, 150)
        score_text.write(f"当前分数: {score.score}", align="center", font=("Arial", 16, "bold"))
        
        # 绘制升级项
        y_pos = 100
        upgrade_spacing = 80
        
        for i, upgrade in enumerate(self.upgrades):
            # 检查是否已购买
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT purchased FROM shop_purchases WHERE upgrade_type = ?", (upgrade["type"],))
            purchased = cursor.fetchone()[0]
            conn.close()
            
            # 绘制升级按钮
            upgrade_button = turtle.Turtle()
            if purchased:
                upgrade_button.color("#808080", "#404040")
            else:
                upgrade_button.color("#00FF00", "#008000")
            upgrade_button.shape("square")
            upgrade_button.shapesize(stretch_wid=2, stretch_len=15)
            upgrade_button.penup()
            upgrade_button.goto(0, y_pos)
            upgrade_button.upgrade_type = upgrade["type"]  # 添加自定义属性
            upgrade_button.purchased = purchased
            
            # 绘制升级信息
            upgrade_info = turtle.Turtle()
            upgrade_info.color("white")
            upgrade_info.penup()
            upgrade_info.hideturtle()
            upgrade_info.goto(0, y_pos)
            
            if purchased:
                text = f"✓ {upgrade['name']} - 已购买"
            else:
                text = f"{upgrade['name']} - {upgrade['cost']}分"
            
            upgrade_info.write(text, align="center", font=("Arial", 14, "bold"))
            
            # 绘制升级描述
            desc_text = turtle.Turtle()
            desc_text.color("#808080")
            desc_text.penup()
            desc_text.hideturtle()
            desc_text.goto(0, y_pos - 25)
            desc_text.write(upgrade["description"], align="center", font=("Arial", 12, "normal"))
            
            y_pos -= upgrade_spacing
        
        # 返回主菜单按钮
        back_button = turtle.Turtle()
        back_button.shape("square")
        back_button.color("#00FFFF", "#0080FF")
        back_button.shapesize(stretch_wid=1.5, stretch_len=8)
        back_button.penup()
        back_button.goto(0, -200)
        
        back_text = turtle.Turtle()
        back_text.color("white")
        back_text.penup()
        back_text.hideturtle()
        back_text.goto(0, -200)
        back_text.write("返回主菜单", align="center", font=("Arial", 14, "bold"))
    
    def handle_click(self, x, y):
        global current_state
        
        # 检查返回主菜单按钮
        if abs(x) < 80 and abs(y + 200) < 15:
            current_state = GameState.MAIN_MENU
            screen.clear()
            main_menu.draw()
            screen.onclick(handle_click)
            return
        
        # 检查升级按钮
        y_pos = 100
        upgrade_spacing = 80
        
        for i, upgrade in enumerate(self.upgrades):
            if abs(x) < 150 and abs(y - y_pos) < 20:
                # 点击了该升级项
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT purchased FROM shop_purchases WHERE upgrade_type = ?", (upgrade["type"],))
                purchased = cursor.fetchone()[0]
                
                if not purchased and score.score >= upgrade["cost"]:
                    # 购买升级
                    cursor.execute("UPDATE shop_purchases SET purchased = 1 WHERE upgrade_type = ?", (upgrade["type"],))
                    score.score -= upgrade["cost"]
                    
                    # 应用升级效果
                    if upgrade["type"] == "speed_boost":
                        player.move_distance *= 1.1  # 提升10%速度
                    elif upgrade["type"] == "extra_life":
                        # 实现额外生命逻辑
                        player.lives += 1  # Increase player lives by 1
                        score.lives = player.lives  # 更新分数显示的生命值
                        score.update_level()  # 刷新显示
                    
                    conn.commit()
                    conn.close()
                    
                    # 重新绘制商店
                    self.draw()
                    return
                
                conn.close()
            
            y_pos -= upgrade_spacing

# 初始化游戏组件
init_db()
main_menu = MainMenu()
player = TurtlePlayer()
cars = CarManager()
score = Score()
particle_manager = ParticleManager()
shop = Shop()

# 调试日志
print("游戏组件初始化完成")

# 游戏循环
previous_state = None
game_start_time = 0
def game_loop():
    global current_state, previous_state, game_start_time, best_path, current_path, ghost_active
    
    screen.update()
    
    # 调试日志：显示当前游戏状态
    # print(f"当前游戏状态: {current_state}")
    
    # 状态切换处理
    if current_state != previous_state:
        # 清除当前界面
        screen.clear()
        screen.bgcolor("white")
        screen.onclick(None)  # 移除所有点击事件
        
        if current_state == GameState.PLAYING:
            # 进入游戏状态
            player.reset()
            cars.clear_cars()
            cars.clear_obstacles()
            score.__init__()
            particle_manager.reset()
            
            # 初始化幽灵模式
            init_ghost_mode()
            
            # 重置游戏开始时间
            game_start_time = time.time()
            
            # 开始记录当前路径
            global current_path, path_recording_start_time
            current_path = []
            path_recording_start_time = time.time()
            
            # 激活幽灵模式（如果有最佳路径）
            global ghost_active
            ghost_active = len(best_path) > 0
        
        elif current_state == GameState.PAUSED:
            # 进入暂停状态
            pass
        
        elif current_state == GameState.GAME_OVER:
            # 进入游戏结束状态
            # 保存最佳路径
            if len(current_path) > 0:
                # 如果当前路径比最佳路径更长（分数更高），则保存为最佳路径
                if len(best_path) == 0 or score.score > best_path[-1][2]:
                    best_path = current_path.copy()
            
            # 将分数添加到排行榜
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO leaderboard (player_name, level, score) VALUES (?, ?, ?)",
                          ("Player", score.level, score.score))
            conn.commit()
            conn.close()
            
            # 移除简单的"GAME OVER"文字，改为粒子爆炸效果
            # 粒子爆炸已经在碰撞时创建，这里不再显示文字
            
            # 显示最终分数
            final_score_text = turtle.Turtle()
            final_score_text.color("black")
            final_score_text.penup()
            final_score_text.hideturtle()
            final_score_text.goto(0, -50)
            final_score_text.write(f"最终关卡: {score.level} - 最终分数: {score.score}", align="center", font=("Arial", 16, "bold"))
            
            # 返回主菜单按钮
            back_button = turtle.Turtle()
            back_button.shape("square")
            back_button.color("#00FF00", "#008000")
            back_button.shapesize(stretch_wid=1.5, stretch_len=8)
            back_button.penup()
            back_button.goto(0, -150)
            
            back_text = turtle.Turtle()
            back_text.color("white")
            back_text.penup()
            back_text.hideturtle()
            back_text.goto(0, -150)
            back_text.write("返回主菜单", align="center", font=("Arial", 14, "bold"))
            
            def back_to_menu(x, y):
                global current_state
                current_state = GameState.MAIN_MENU
                screen.clear()
                main_menu.draw()
                screen.onclick(handle_click)
            
            screen.onclick(back_to_menu)
        
        elif current_state == GameState.SHOP:
            # 进入商店状态
            shop.draw()
            screen.onclick(shop.handle_click)
        
        previous_state = current_state
    
    # 状态持续处理
    if current_state == GameState.MAIN_MENU:
        # 主菜单逻辑
        pass
    
    elif current_state == GameState.PLAYING:
        # 游戏中逻辑
        
        # 更新天气
        update_weather()
        create_rain()
        move_rain()
        
        # 更新昼夜循环
        update_day_night()
        
        # 更新汽车车灯
        cars.update_car_lights(is_night)
        
        # 生成汽车
        cars.make_car(speed_multiplier=1.0 + (score.level - 1) * 0.1)
        
        # 生成路障
        cars.create_obstacle()
        
        # 移动汽车和路障
        cars.move_cars()
        cars.move_obstacles()
        
        # 碰撞检测（AABB）
        player_bounds = player.get_bounds()
        for car in cars.all_cars:
            car_bounds = car.get_bounds()
            if (player_bounds[0] < car_bounds[2] and player_bounds[2] > car_bounds[0] and
                player_bounds[1] < car_bounds[3] and player_bounds[3] > car_bounds[1]):
                # 碰撞发生
                print("碰撞发生！")
                particle_manager.create_explosion(player.xcor(), player.ycor())

                # 使用生命系统
                player.lives -= 1
                score.lives = player.lives  # 更新分数显示的生命值
                score.update_level()  # 刷新显示
                if player.lives <= 0:
                    current_state = GameState.GAME_OVER
                    break  # 跳出循环避免重复处理
                else:
                    # 重置玩家位置
                    player.reset()
                    # 清除当前路径
                    current_path.clear()
                    path_recording_start_time = time.time()
                    # 可以添加短暂的无敌时间或其他效果
                    break  # 跳出循环避免重复处理
        
        # 记录玩家路径
        if current_state == GameState.PLAYING:
            current_time = time.time() - path_recording_start_time
            current_path.append((player.xcor(), player.ycor(), current_time))
        
        # 无限滚动世界
        scroll_world()
        
        # 更新幽灵模式
        update_ghost()
        
        # 粒子效果
        particle_manager.update_particles()
    
    elif current_state == GameState.PAUSED:
        # 暂停逻辑
        pass
    
    elif current_state == GameState.GAME_OVER:
        # 游戏结束逻辑
        particle_manager.update_particles()
    
    elif current_state == GameState.SHOP:
        # 商店逻辑
        pass
    
    screen.ontimer(game_loop, 16)  # 约60fps

# 点击事件处理
def handle_click(x, y):
    global current_state
    
    if current_state == GameState.MAIN_MENU:
        button_clicked = main_menu.check_click(x, y)
        if button_clicked == 0:
            # 开始游戏
            screen.clear()
            # 重新初始化游戏组件
            player.reset()
            cars.clear_cars()
            score.__init__()
            particle_manager.reset()
            current_state = GameState.PLAYING
        elif button_clicked == 1:
            # 显示排行榜
            show_leaderboard()
        elif button_clicked == 2:
            # 打开商店
            current_state = GameState.SHOP
            shop.draw()
            screen.onclick(shop.handle_click)
        elif button_clicked == 3:
            # 退出游戏
            screen.bye()

# 显示排行榜
def show_leaderboard():
    screen.clear()
    
    title = turtle.Turtle()
    title.color("#FF6600")
    title.penup()
    title.hideturtle()
    title.goto(0, 200)
    title.write("排行榜", align="center", font=("Arial", 24, "bold"))
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT player_name, level, score, date FROM leaderboard ORDER BY level DESC, score DESC LIMIT 10")
    results = cursor.fetchall()
    conn.close()
    
    y_pos = 150
    for i, (name, level, score, date) in enumerate(results, 1):
        text = turtle.Turtle()
        text.color("white")
        text.penup()
        text.hideturtle()
        text.goto(0, y_pos)
        text.write(f"{i}. {name} - Level: {level} - Score: {score} - {date}", align="center", font=("Arial", 12, "normal"))
        y_pos -= 30
    
    # 返回主菜单按钮
    back_button = turtle.Turtle()
    back_button.shape("square")
    back_button.color("#00FF00", "#008000")
    back_button.shapesize(stretch_wid=1.5, stretch_len=8)
    back_button.penup()
    back_button.goto(0, -200)
    
    back_text = turtle.Turtle()
    back_text.color("white")
    back_text.penup()
    back_text.hideturtle()
    back_text.goto(0, -200)
    back_text.write("返回主菜单", align="center", font=("Arial", 14, "bold"))
    
    def back_to_menu(x, y):
        main_menu.draw()
        screen.onclick(handle_click)
    
    screen.onclick(back_to_menu)

# 键盘事件处理
def handle_key(key):
    global current_state
    
    if current_state == GameState.PLAYING:
        if key == "Up":
            player.up()
        elif key == "p" or key == "P":
            current_state = GameState.PAUSED
            show_pause_menu()
    
    elif current_state == GameState.PAUSED:
        if key == "p" or key == "P":
            current_state = GameState.PLAYING

# 显示暂停菜单
def show_pause_menu():
    pause_text = turtle.Turtle()
    pause_text.color("white")
    pause_text.penup()
    pause_text.hideturtle()
    pause_text.goto(0, 100)
    pause_text.write("已暂停", align="center", font=("Arial", 24, "bold"))
    
    # 继续按钮
    resume_button = turtle.Turtle()
    resume_button.shape("square")
    resume_button.color("#00FF00", "#008000")
    resume_button.shapesize(stretch_wid=2, stretch_len=10)
    resume_button.penup()
    resume_button.goto(0, 0)
    
    resume_text = turtle.Turtle()
    resume_text.color("white")
    resume_text.penup()
    resume_text.hideturtle()
    resume_text.goto(0, 0)
    resume_text.write("继续游戏", align="center", font=("Arial", 16, "bold"))
    
    # 返回主菜单按钮
    main_menu_button = turtle.Turtle()
    main_menu_button.shape("square")
    main_menu_button.color("#00FFFF", "#0080FF")
    main_menu_button.shapesize(stretch_wid=2, stretch_len=10)
    main_menu_button.penup()
    main_menu_button.goto(0, -60)
    
    main_menu_text = turtle.Turtle()
    main_menu_text.color("white")
    main_menu_text.penup()
    main_menu_text.hideturtle()
    main_menu_text.goto(0, -60)
    main_menu_text.write("返回主菜单", align="center", font=("Arial", 16, "bold"))
    
    def handle_pause_click(x, y):
        global current_state
        
        # 检查继续按钮
        resume_x, resume_y = resume_button.position()
        if abs(x - resume_x) < 100 and abs(y - resume_y) < 20:
            current_state = GameState.PLAYING
            # 清除暂停菜单
            for turtle_obj in screen.turtles():
                if turtle_obj != player and turtle_obj not in cars.all_cars and turtle_obj != score:
                    turtle_obj.hideturtle()
            screen.onclick(None)  # 移除暂停菜单的点击事件
        
        # 检查返回主菜单按钮
        main_menu_x, main_menu_y = main_menu_button.position()
        if abs(x - main_menu_x) < 100 and abs(y - main_menu_y) < 20:
            current_state = GameState.MAIN_MENU
            screen.clear()
            main_menu.draw()
            screen.onclick(handle_click)
    
    screen.onclick(handle_pause_click)

# 天气系统函数
def update_weather():
    global current_weather, rain_start_time, rain_turtles
    
    # 检查天气循环
    if time.time() % WEATHER_CYCLE_TIME < 1:
        # 随机决定是否下雨
        if random.random() < RAIN_CHANCE:
            current_weather = "rain"
            rain_start_time = time.time()
        else:
            current_weather = "clear"
    
    # 检查下雨持续时间
    if current_weather == "rain" and time.time() - rain_start_time > RAIN_DURATION:
        current_weather = "clear"
        # 清除雨滴
        for rain_turtle in rain_turtles:
            rain_turtle.hideturtle()
        rain_turtles.clear()

def create_rain():
    global rain_turtles
    
    # 创建雨滴
    if current_weather == "rain" and random.randint(1, 10) < 3:
        rain_turtle = turtle.Turtle()
        rain_turtle.shape("square")
        rain_turtle.color("blue")
        rain_turtle.shapesize(stretch_wid=0.1, stretch_len=0.5)
        rain_turtle.penup()
        rain_turtle.goto(random.randint(-300, 300), 300)
        rain_turtle.setheading(270)
        rain_turtles.append(rain_turtle)

def move_rain():
    # 移动雨滴
    for rain_turtle in rain_turtles[:]:
        rain_turtle.forward(10)
        if rain_turtle.ycor() < -300:
            rain_turtle.hideturtle()
            rain_turtles.remove(rain_turtle)

# 昼夜循环函数
def update_day_night():
    global is_night, day_night_timer
    
    # 更新计时器
    day_night_timer += 1/60  # 基于60fps
    
    # 计算当前循环进度（0到1之间）
    cycle_progress = (day_night_timer % DAY_NIGHT_CYCLE_TIME) / DAY_NIGHT_CYCLE_TIME
    
    # 计算背景颜色
    if cycle_progress < 0.25:  # 白天到黄昏
        t = cycle_progress * 4
        r = int(DAY_COLOR[0] + (DUSK_COLOR[0] - DAY_COLOR[0]) * t)
        g = int(DAY_COLOR[1] + (DUSK_COLOR[1] - DAY_COLOR[1]) * t)
        b = int(DAY_COLOR[2] + (DUSK_COLOR[2] - DAY_COLOR[2]) * t)
    elif cycle_progress < 0.5:  # 黄昏到夜晚
        t = (cycle_progress - 0.25) * 4
        r = int(DUSK_COLOR[0] + (NIGHT_COLOR[0] - DUSK_COLOR[0]) * t)
        g = int(DUSK_COLOR[1] + (NIGHT_COLOR[1] - DUSK_COLOR[1]) * t)
        b = int(DUSK_COLOR[2] + (NIGHT_COLOR[2] - DUSK_COLOR[2]) * t)
    elif cycle_progress < 0.75:  # 夜晚到黄昏
        t = (cycle_progress - 0.5) * 4
        r = int(NIGHT_COLOR[0] + (DUSK_COLOR[0] - NIGHT_COLOR[0]) * t)
        g = int(NIGHT_COLOR[1] + (DUSK_COLOR[1] - NIGHT_COLOR[1]) * t)
        b = int(NIGHT_COLOR[2] + (DUSK_COLOR[2] - NIGHT_COLOR[2]) * t)
    else:  # 黄昏到白天
        t = (cycle_progress - 0.75) * 4
        r = int(DUSK_COLOR[0] + (DAY_COLOR[0] - DUSK_COLOR[0]) * t)
        g = int(DUSK_COLOR[1] + (DAY_COLOR[1] - DUSK_COLOR[1]) * t)
        b = int(DUSK_COLOR[2] + (DAY_COLOR[2] - DUSK_COLOR[2]) * t)
    
    # 设置背景颜色
    screen.bgcolor(r/255, g/255, b/255)
    
    # 更新夜晚状态
    is_night = cycle_progress >= 0.5

# 幽灵模式函数
def init_ghost_mode():
    global ghost_player
    
    # 创建幽灵玩家
    ghost_player = turtle.Turtle()
    ghost_player.shape("turtle")
    ghost_player.color("white")
    ghost_player.shapesize(stretch_wid=0.8, stretch_len=0.8)
    ghost_player.penup()
    ghost_player.goto(0, -280)
    ghost_player.setheading(90)
    ghost_player.hideturtle()

def update_ghost():
    global ghost_active
    
    if ghost_active and best_path:
        # 复现最佳路径
        current_time = time.time() - game_start_time
        for i in range(len(best_path) - 1):
            if best_path[i][2] <= current_time < best_path[i+1][2]:
                # 插值计算当前位置
                t = (current_time - best_path[i][2]) / (best_path[i+1][2] - best_path[i][2])
                x = best_path[i][0] + (best_path[i+1][0] - best_path[i][0]) * t
                y = best_path[i][1] + (best_path[i+1][1] - best_path[i][1]) * t
                ghost_player.goto(x, y)
                ghost_player.showturtle()
                return
        # 如果路径完成，隐藏幽灵
        ghost_player.hideturtle()
        ghost_active = False

# 无限滚动世界函数
def scroll_world():
    global score
    
    if player.ycor() > 200:
        # 所有物体向下平移
        scroll_distance = 50
        
        # 玩家向下移动
        player.sety(player.ycor() - scroll_distance)
        
        # 汽车向下移动
        for car in cars.all_cars:
            car.sety(car.ycor() - scroll_distance)
            car.lane = car.ycor()  # 更新车道信息
        
        # 路障向下移动
        for obstacle in cars.obstacles:
            obstacle.sety(obstacle.ycor() - scroll_distance)
        
        # 幽灵玩家向下移动
        if ghost_player:
            ghost_player.sety(ghost_player.ycor() - scroll_distance)
        
        # 增加分数
        score.score += 5
        score.update_score()

# 设置事件监听
screen.onclick(handle_click)
screen.onkey(lambda: handle_key("Up"), "Up")
screen.onkey(lambda: handle_key("P"), "p")
screen.onkey(lambda: handle_key("P"), "P")
screen.listen()

# 启动游戏循环
game_loop()

# 保持窗口打开
screen.mainloop()
