"""
breakout genetic algorithm
arther = 강곽 27th 이윤혁
"""

import datetime

import pygame
from pygame.locals import *
import logging
from math import atan2, pi
import numpy as np
from neural_network import Network


def calculate_angle(p1: tuple, p2: tuple) -> float:
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if dy != 0:
        rad = atan2(dx, -dy)
        rad %= 2 * pi
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


def game(genome):
    pygame.init()

    SCREEN_WIDTH = 1600
    SCREEN_HEIGHT = 900

    SCREEN_RESOLUTION = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(SCREEN_RESOLUTION)
    pygame.display.set_caption('breakout')

    BACKGROUND_COLOR = (255, 255, 255)

    # color
    cols = 20
    rows = 7
    clock = pygame.time.Clock()
    fps = 60

    class Agent:
        def __init__(self):
            self.score = 0
            self.game_over = False
            self.isAllBlocksDestroyed = False
            self.live_ball = False

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
                block_individual = [rect, now_color, [block_x, block_y]]  # TODO: 9:38 part 4 리스트 안에 생명력(0, 1) 이랑 다른 곳에서 리스트 접근하는거 수정할 것
                block_row.append(block_individual)

            return block_row

        def draw_wall(self):
            BLOCK_RECT_INDEX = 0
            BLOCK_COLOR_INDEX = 1
            BLOCK_TUPLE_COORDINATE_INDEX = 3
            BLOCK_X_INDEX = 0
            BLOCK_Y_INDEX = 1
            for row in self.list_of_block:
                for block in row:
                    block_rect = block[BLOCK_RECT_INDEX]
                    block_color = block[BLOCK_COLOR_INDEX]
                    pygame.draw.rect(screen, block_color, block_rect)
                    pygame.draw.rect(screen, self.background_color, (block_rect), 2)

    class Paddle:
        def __init__(self, screen_width, screen_height, cols_):
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

            self.paddle_color = (128, 128, 128)
            self.paddle_outline = (100, 100, 100)

        def move(self, _environment_input):
            self.direction = 0
            network_output = genome.next_move(_environment_input)

            if 0 < network_output < 0.5 and self.rect.left > 0:
                self.rect.x -= self.speed
                self.direction = self.LEFT

            elif 0.5 <= network_output < 1 and self.rect.right < self.screen_width:
                self.rect.x += self.speed
                self.direction = self.RIGHT

        def draw(self):
            pygame.draw.rect(screen, self.paddle_color, self.rect)
            pygame.draw.rect(screen, self.paddle_outline, self.rect, 3)

    # 공 클래스
    class game_ball:
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

        def move(self, paddle_rect_top, paddle_direction, list_of_block):
            row_count = 0
            collision_threshold = 5
            isAllBlocksDestroyed = True
            for row in list_of_block:
                item_count = 0
                for item in row:
                    # 충돌 검사
                    if self.rect.colliderect(item[0]):
                        if abs(self.rect.bottom - item[0].top) < collision_threshold and self.speed_y > 0:
                            self.speed_y *= -1
                        if abs(self.rect.top - item[0].bottom) < collision_threshold and self.speed_y < 0:
                            self.speed_y *= -1
                        if abs(self.rect.right - item[0].right) < collision_threshold and self.speed_x > 0:
                            self.speed_x *= -1
                        if abs(self.rect.left - item[0].left) < collision_threshold and self.speed_x < 0:
                            self.speed_x *= -1

                        wall.list_of_block[row_count][item_count][0] = (0, 0, 0, 0)  # 파괴
                        agent.score += 1

                    else:
                        isAllBlocksDestroyed = False
                    item_count += 1
                row_count += 1

            agent.isAllBlocksDestroyed = isAllBlocksDestroyed

            # 벽 충돌
            if self.rect.left < 0 or self.rect.right > self.screen_width:
                self.speed_x *= -1
            if self.rect.top < 0:
                self.speed_y *= -1
            if self.rect.bottom > self.screen_height:
                self.game_over = True

            # paddle 충돌
            if self.rect.colliderect(player_paddle):
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

            self.rect.x += self.speed_x
            self.rect.y += self.speed_y

            if self.rect.y > player_paddle.rect.y:
                self.game_over = True

            agent.game_over = self.game_over

        def draw(self):
            pygame.draw.circle(screen, self.ball_color, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)
            pygame.draw.circle(screen, self.ball_outline, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad, 3)

    wall = Wall(BACKGROUND_COLOR, SCREEN_WIDTH, rows, cols)
    wall.create_wall()
    isrunning = True

    player_paddle = Paddle(SCREEN_WIDTH, SCREEN_HEIGHT, cols)
    ball = game_ball(player_paddle.x + player_paddle.width // 2, player_paddle.y - player_paddle.height, SCREEN_WIDTH, SCREEN_HEIGHT)
    agent = Agent()
    while isrunning:

        clock.tick(fps)
        screen.fill(BACKGROUND_COLOR)
        wall.draw_wall()

        # 환경 계산
        angle = calculate_angle(player_paddle.rect.center, ball.rect.center)
        distance = calculate_distance(player_paddle.rect.center, ball.rect.center)
        environment_input = np.array([angle, distance])
        print(angle, distance)

        # AI 행동
        player_paddle.draw()
        player_paddle.move(environment_input)

        # 공 운동
        ball.draw()
        ball.move(player_paddle.rect.top, player_paddle.direction, wall.list_of_block)
        # print(ball.rect.x, ball.rect.y)
        print(player_paddle.x, player_paddle.y)
        if agent.game_over:
            isrunning = False

        # quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isrunning = False

        pygame.display.update()

    pygame.quit()

    genome.fitness = agent.score
    print(genome.fitness)
    return genome


game(Network())
