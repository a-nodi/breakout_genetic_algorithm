"""
breakout genetic algorithm
arther = 강곽 27th 이윤혁
"""
import copy
import os
from multiprocessing import Process, Manager, freeze_support
from generation import Generation
from breakout import game
from datetime import datetime
import pickle
import logging
from colorlog import ColoredFormatter
from matplotlib import pyplot as plt
import numpy as np
import time

global_list_of_genome = []


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
        self.list_of_performanced_genome = []

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
            list_of_manager = []
            list_of_genome_container = []
            list_of_runtime = []
            self.list_of_performanced_genome = []
            self.logger.info(f"current generation = {self.generation_number}")

            genome_count = 0
            for genome in list_of_genome:
                manager = Manager()
                list_of_manager.append(manager)
                genome_container = [list_of_manager[genome_count].list([genome.web1, genome.web2, genome.web3])]
                list_of_genome_container.append(genome_container)
                process = Process(target=game, args=(genome_container))
                list_of_process.append(process)
                self.logger.info(f"genome {genome_count + 1} process start")
                list_of_process[genome_count].start()
                genome_count += 1

            genome_count = 0
            for genome in list_of_genome:
                list_of_process[genome_count].join()
                performanced_genome = copy.deepcopy(genome)
                performanced_genome.fitness = list_of_genome_container[genome_count][0][3]
                performanced_genome.runtime = list_of_genome_container[genome_count][0][4]
                self.logger.info(f"genome {genome_count + 1}, fitness = {performanced_genome.fitness}")
                self.list_of_performanced_genome.append(performanced_genome)
                genome_count += 1

            temp_population = 0
            # 학습 수행
            while len(self.list_of_performanced_genome) < self.population:
                global global_list_of_genome
                if global_list_of_genome:
                    self.list_of_performanced_genome.append(global_list_of_genome.pop())

                if temp_population < len(self.list_of_performanced_genome):
                    temp_population = len(self.list_of_performanced_genome)
                self.logger.info(f"remaining_population = {self.population - len(self.list_of_performanced_genome)}")

            # 적합도 기록
            self.logger.info("searching high fitness")
            for genome in self.list_of_performanced_genome:
                list_of_fitness.append(genome.fitness)
                if genome.fitness > high_fitness:
                    high_fitness = genome.fitness

            for genome in self.list_of_performanced_genome:
                list_of_runtime.append(genome.runtime)

            # 신경망 피클링
            self.save_network(self.list_of_performanced_genome, list_of_fitness, list_of_runtime)
            # 세대 교체
            self.generation.set_genomes(list_of_genome)
            self.generation.keep_best_genomes()
            list_of_genome = self.generation.mutations()

            # 그래프 플롯팅
            self.ploter.put_fitness(high_fitness)
            self.ploter.draw_plot()

    def save_network(self, list_of_genome, list_of_fitness, list_of_runtime):
        """
        신경망 피클링 메서드
        :param list_of_genome:
        :param list_of_fitness:
        :param list_of_runtime:
        :return:
        """
        pickled_network = {
            "list_of_genome": list_of_genome,
            "list_of_fitness": list_of_fitness,
            "high_fitness": max(list_of_fitness),
            "list_of_runtime": list_of_runtime
            }  # 신경망 정보 포맷

        # 피클링
        with open(os.path.join(self.path, f"{self.generation_number}th_generation_genomes"), 'wb') as f:
            pickle.dump(pickled_network, f)
            self.logger.info(f"{self.generation_number}th generation pickled")
            f.close()

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
    def __init__(self):
        self.list_of_high_fitness = []
        self.fig = plt.figure(figsize=(12, 5))
        self.ax = plt.axes()
        self.generation_number = 0
        plt.xlabel('generation number', fontsize=10)
        plt.ylabel('fitess', fontsize=10)
        plt.show(block=False)

    def draw_plot(self):

        self.ax.plot(np.array(list(range(1, self.generation_number + 1))), np.array(self.list_of_high_fitness), color='#81C147')
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def put_fitness(self, score):
        self.list_of_high_fitness.append(score)
        self.generation_number += 1


if __name__ == '__main__':
    center = CenterController()
    freeze_support()
    center.run()
