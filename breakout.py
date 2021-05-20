"""
breakout genetic algorithm
arther = 강곽 27th 이윤혁
"""
import pygame
from pygame.locals import *
from math import atan2, pi
import numpy as np
from neural_network import Network
from datetime import datetime
from copy import deepcopy

COLLISION_THRESHOLD = 10


def calculate_angle(p1: tuple, p2: tuple) -> float:
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if dy != 0:
        rad = atan2(dx, -dy)
    else:
        if dx > 0:
            rad = pi / 2
        elif dx < 0:
            rad = - pi / 2
        else:
            rad = 0

    return rad


def calculate_distance(p1: tuple, p2: tuple) -> float:
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    d = (dx ** 2 + dy ** 2) ** 0.5

    return d


def game(genome_data):
    pygame.init()

    SCREEN_WIDTH = 1600
    SCREEN_HEIGHT = 900
    SCREEN_DIAGONAL = calculate_distance((0, 0), (SCREEN_WIDTH, SCREEN_HEIGHT))
    SCREEN_RESOLUTION = (SCREEN_WIDTH, SCREEN_HEIGHT)

    screen = pygame.display.set_mode(SCREEN_RESOLUTION)
    pygame.screen = pygame.display.set_mode((1, 1))
    pygame.display.set_caption('breakout')

    BACKGROUND_COLOR = (255, 255, 255)

    TIMEOUT = 5 * 60
    # color
    cols = 20
    rows = 7
    clock = pygame.time.Clock()
    fps = 480

    class Agent:
        def __init__(self):
            self.score = 0
            self.game_over = False
            self.isAllBlocksDestroyed = False
            self.start_time = datetime.now()

        def calculate_fitness(self):
            fitness = (self.score * 1000 - self.calculate_timedelta()) / (rows * cols * 10)
            return fitness

        def calculate_timedelta(self):
            timedelta = (datetime.now() - self.start_time).total_seconds()
            return timedelta

    # 벽돌 클래스
    class Wall:
        def __init__(self, background_color, screen_width, rows_, cols_):
            self.rows = rows_
            self.cols = cols_
            self.width = screen_width // self.cols
            self.background_color = background_color
            self.height = 50
            self.list_of_block = []
            BLOCK_RED = (255, 0, 0)
            BLOCK_ORENGE = (255, 127, 0)
            BLOCK_YELLOW = (255, 255, 0)
            BLOCK_GREEN = (0, 255, 0)
            BLOCK_BLUE = (0, 0, 255)
            BLOCK_VIOLET = (148, 0, 211)
            BLOCK_PURPLE = (75, 0, 130)

            self.COLOR_COUNT = 7

            self.list_of_color = [BLOCK_PURPLE, BLOCK_VIOLET, BLOCK_BLUE, BLOCK_GREEN, BLOCK_YELLOW, BLOCK_ORENGE, BLOCK_RED]
            self.color_index = 0

        def create_wall(self):
            # 각각의 블럭을 담는 리스트
            for row in range(self.rows):
                wall_row = self.create_wall_row(row)
                self.list_of_block.append(wall_row)

        def create_wall_row(self, row):
            block_row = []
            y_biase = 100
            for col in range(self.cols):
                # 위치 생성

                block_x = col * self.width
                block_y = y_biase + row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                now_color = self.list_of_color[self.color_index // self.cols]  # 열마다 같은색, 열 변경시 다음색
                self.color_index = (self.color_index + 1) % (self.COLOR_COUNT * self.cols)
                block_individual = [rect, now_color, [block_x, block_y]]
                block_row.append(block_individual)

            return block_row

        def draw_wall(self):
            BLOCK_RECT_INDEX = 0
            BLOCK_COLOR_INDEX = 1
            for row in self.list_of_block:
                for block in row:
                    block_rect = block[BLOCK_RECT_INDEX]
                    block_color = block[BLOCK_COLOR_INDEX]
                    pygame.draw.rect(screen, block_color, block_rect)
                    pygame.draw.rect(screen, self.background_color, block_rect, 2)

    class Paddle:
        def __init__(self, screen_width, screen_height, cols_, network_data_):
            self.height = 20
            self.width = screen_width // cols_
            self.screen_width = screen_width
            self.x = screen_width // 2 - self.width // 2
            self.y = screen_height - self.height * 2
            self.speed = 10
            self.rect = Rect(self.x, self.y, self.width, self.height)
            self.direction = 0
            self.LEFT = -1
            self.RIGHT = 1
            self.network = Network()
            self.network.set_weights(network_data_[0], network_data_[1], network_data_[2])
            self.paddle_color = (128, 128, 128)
            self.paddle_outline = (100, 100, 100)

        def move(self, _environment_input):
            self.direction = 0

            network_output = self.network.next_move(_environment_input)
            # print(_environment_input, network_output)
            if 0.33 < float(network_output[0]) < 0.67 and self.rect.left > 0:
                self.rect.x -= self.speed
                self.direction = self.LEFT

            elif 0.67 <= float(network_output[0]) < 1 and self.rect.right < self.screen_width:
                self.rect.x += self.speed
                self.direction = self.RIGHT

        def draw(self):
            pygame.draw.rect(screen, self.paddle_color, self.rect)
            pygame.draw.rect(screen, self.paddle_outline, self.rect, 3)

    # 공 클래스
    class Ball:
        def __init__(self, x, y, screen_width, screen_height):
            self.ball_rad = 10
            self.x = x - self.ball_rad
            self.y = y
            self.screen_width = screen_width
            self.screen_height = screen_height
            self.rect = Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2, )
            self.speed_x = 4
            self.speed_y = -4
            self.speed_max = 5
            self.ball_color = (128, 128, 128)
            self.ball_outline = (100, 100, 100)
            self.game_over = False

        def move(self):
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y

        def draw(self):
            pygame.draw.circle(screen, self.ball_color, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)
            pygame.draw.circle(screen, self.ball_outline, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad, 3)

        def block_collision_check(self, list_of_block_, collision_threshold):
            row_count = 0
            isAllBlocksDestroyed = True
            score_increase_ = 0
            for row in list_of_block_:
                item_count = 0
                for item in row:
                    # 충돌 검사
                    if self.rect.colliderect(item[0]):
                        if abs(self.rect.bottom - item[0].top) < collision_threshold and self.speed_y > 0:
                            self.speed_y *= -1
                        if abs(self.rect.top - item[0].bottom) < collision_threshold and self.speed_y < 0:
                            self.speed_y *= -1
                        if abs(self.rect.right - item[0].left) < collision_threshold and self.speed_x > 0:
                            self.speed_x *= -1
                        if abs(self.rect.left - item[0].right) < collision_threshold and self.speed_x < 0:
                            self.speed_x *= -1

                        list_of_block_[row_count][item_count][0] = (0, 0, 0, 0)  # 파괴
                        score_increase_ += 1

                    else:
                        isAllBlocksDestroyed = False
                    item_count += 1
                row_count += 1

            return isAllBlocksDestroyed, score_increase_, list_of_block_

        def screen_border_collision_check(self):
            # 벽 충돌
            if self.rect.left < 0 or self.rect.right > self.screen_width:
                self.speed_x *= -1
            if self.rect.top < 0:
                self.speed_y *= -1
        
        def paddle_collision_check(self, paddle_rect_top, paddle_direction, collision_threshold):
            # paddle 충돌
            if self.rect.colliderect(paddle):
                # 상단면 충돌 검사
                if abs(self.rect.bottom - paddle_rect_top) < collision_threshold and self.speed_y > 0:
                    self.speed_y *= -1
                    self.speed_x += paddle_direction
                    if self.speed_x > self.speed_max:
                        self.speed_x = self.speed_max
                    elif self.speed_x < 0 and self.speed_x < -self.speed_max:
                        self.speed_x = -self.speed_max
                else:
                    self.speed_x *= -1
        
        def game_over_check(self, player_paddle_y):
            if self.rect.y > player_paddle_y:
                self.game_over = True
            
            return self.game_over
                
    wall = Wall(BACKGROUND_COLOR, SCREEN_WIDTH, rows, cols)
    wall.create_wall()
    isrunning = True

    paddle = Paddle(SCREEN_WIDTH, SCREEN_HEIGHT, cols, genome_data)
    ball = Ball(paddle.x + paddle.width // 2, paddle.y - paddle.height, SCREEN_WIDTH, SCREEN_HEIGHT)
    agent = Agent()

    while isrunning:

        clock.tick(fps)
        screen.fill(BACKGROUND_COLOR)
        wall.draw_wall()

        # 환경 계산
        angle = calculate_angle(paddle.rect.center, ball.rect.center)
        distance = calculate_distance(paddle.rect.center, ball.rect.center)
        environment_input = np.array([angle / (pi / 2), distance / SCREEN_DIAGONAL])

        # AI 행동
        paddle.draw()
        paddle.move(environment_input)

        # 공 운동
        ball.draw()
        agent.isAllBlocksDestroyed, score_increase, list_of_block = ball.block_collision_check(deepcopy(wall.list_of_block), COLLISION_THRESHOLD)
        wall.list_of_block = deepcopy(list_of_block)
        agent.score += score_increase
        ball.screen_border_collision_check()
        ball.paddle_collision_check(paddle.rect.top, paddle.direction, COLLISION_THRESHOLD)
        ball.move()
        agent.game_over = ball.game_over_check(paddle.rect.y)
        
        if agent.game_over or not agent.score < cols * rows or agent.calculate_timedelta() > TIMEOUT:
            isrunning = False

        # quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isrunning = False

        pygame.display.update()

    pygame.quit()

    genome_data.append(agent.calculate_fitness())
    genome_data.append(agent.calculate_timedelta())
