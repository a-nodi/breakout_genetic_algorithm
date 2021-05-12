"""
breakout genetic algorithm
arther = 강곽 27th 이윤혁
"""

import os
from multiprocessing import Process ,Queue
from generation import Generation
from breakout import game
from datetime import datetime
import pickle
import logging
from colorlog import ColoredFormatter
from matplotlib import pyplot as plt
import numpy as np


class CenterController:
    def __init__(self):
        self.generation = Generation()
        self.population = self.generation.population
        self.high_score = 0
        self.generation_number = 0
        self.current_generation_number = 0
        self.list_of_genome = []
        self.isrunning = True
        self.generation_process = {
            "list_of_genome": [],
            "high_score": 0,
            "runningtime": 0.0,
        }

        self.current_status = {
            "list_of_high_score": [],
            "list_of_running_time": [],

        }

        self.stream_handler = logging.StreamHandler()
        formatter = ColoredFormatter(
            "%(log_color)s[%(asctime)s][%(levelname)s] %(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'white,bold',
                'WARNING':  'yellow',
                'ERROR':    'red,bold',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )

        self.stream_handler.setFormatter(formatter)  # 콘솔 출력
        self.logger = logging.getLogger("log")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.stream_handler)

        self.ploter = Ploter()

        self.path = ''
        self.create_network_dir()

    def run(self):
        """
        학슴 메서드
        :return:
        """
        list_of_genome = self.generation.set_initial_genomes()

        while True:
            # 초기화
            self.generation_number += 1
            high_fitness = 0
            list_of_fitness = []
            list_of_process = []
            list_of_performanced_genome = []
            q = Queue()

            for genome in list_of_genome:
                list_of_process.append(Process(target=game, args=(genome, q)))

            q.close()
            q.join_thread()

            for process in list_of_process:
                process.join()

            survived_population = self.population

            # 학습 수행
            while survived_population > 0:
                genome = q.get(block=True)
                list_of_performanced_genome.append(genome)
                survived_population -= 1

            # 적합도 기록
            for genome in list_of_genome:
                list_of_fitness.append(genome.fitness)
                if genome.fitness > high_fitness:
                    high_fitness = genome.fitness

            # 신경망 피클링
            self.save_network(list_of_genome, list_of_fitness)
            # 세대 교체
            self.generation.set_genomes(list_of_genome)
            self.generation.keep_best_genomes()
            list_of_genome = self.generation.mutations()

            # 그래프 플롯팅
            self.ploter.put_fitness(high_fitness)
            self.ploter.draw_plot()

    def save_network(self, list_of_genome, list_of_fitness):
        """
        신경망 피클링 메서드
        :param list_of_genome:
        :param list_of_fitness:
        :return:
        """
        pickled_network = {
            "list_of_genome": list_of_genome,
            "list_of_fitness": list_of_fitness,
            "high_fitness": max(list_of_fitness),
            }  # 신경망 정보 포맷

        # 피클링
        with open(os.path.join(self.path, f"{self.generation_number}th_generation_genomes"), 'wb') as f:
            pickle.dump(pickled_network, f)
            self.logger.info(f"{self.generation_number}th generation pickled")

    def create_network_dir(self):
        """
        신경망 저장 경로 생성 메서드
        :return:
        """
        current_date = datetime.now()
        self.path = f'{current_date.strftime("%y")}{current_date.strftime("%m")}{current_date.strftime("%d")}{current_date.strftime("%H")}{current_date.strftime("%M")}{current_date.strftime("%S")}'
        os.mkdir(self.path)
        self.logger.info(f"created network dir {self.path}")


class Ploter:
    def __init___(self):
        self.list_of_high_fitness = []
        self.fig = plt.figure(figsize=(12, 5))
        self.ax = plt.axes()
        self.generation_number = 0
        plt.xlabel('generation number', fontsize=10)
        plt.ylabel('fitess', fontsize=10)
        plt.show(block=False)

    def draw_plot(self):
        self.ax.plot(np.array(list(range(self.generation_number + 1))), np.array(self.list_of_high_fitness), color='#81C147')
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def put_fitness(self, score):
        self.list_of_high_fitness.append(score)
        self.generation_number += 1


center = CenterController()
center.run()
