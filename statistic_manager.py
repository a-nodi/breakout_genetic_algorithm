import pickle
from matplotlib import pyplot as plt
import numpy as np
import copy


class Ploter:
    def __init__(self):
        self.high_fitness_array = None
        self.average_fitness_array = None
        self.fig = plt.figure(figsize=(64, 9))
        self.ax = plt.axes()
        self.generation_number = 0
        plt.xlabel('generation number', fontsize=10)
        plt.ylabel('fitness', fontsize=10)
        plt.show(block=False)

    def draw_plot(self):
        self.ax.plot(np.array(list(range(1, self.generation_number + 1))), self.high_fitness_array, color='#81C147')
        self.ax.plot(np.array(list(range(1, self.generation_number + 1))), self.average_fitness_array, color='#9966FF')
        # plt.legend(['high_fitness', 'average_fitness'])

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def put_high_fitness(self, _fitness_array):
        self.high_fitness_array = _fitness_array

    def put_average_fitness(self, _fitness_array):
        self.average_fitness_array = _fitness_array

    def put_gennum(self, gennum):
        self.generation_number = gennum

    def save_plot(self):
        self.ax.plot(np.array(list(range(1, self.generation_number + 1))), self.high_fitness_array, color='#81C147')
        self.ax.plot(np.array(list(range(1, self.generation_number + 1))), self.average_fitness_array, color='#9966FF')
        plt.savefig('fitness plot.png', dpi=200)


class FileManager:
    def __init__(self):
        self.id = 210515171835
        self.list_of_generation = []

        self.genome_array = []
        self.fitness_array = None
        self.high_fitness_array = None
        self.average_fitness_array = None
        self.runtime_array = None

    def read_pickle(self, path):
        with open(path, 'rb') as f:
            generation = pickle.load(f)
            self.list_of_generation.append(generation)
            f.close()

    def mkpath(self, fname):
        path = f"{self.id}\\{fname}"
        return path

    def read_all_generation(self, gennum):
        self.fitness_array = np.zeros((gennum, 25))
        self.high_fitness_array = np.zeros(gennum)
        self.average_fitness_array = np.zeros(gennum)
        self.runtime_array = np.zeros((gennum, 25))

        for gen_count in range(1, gennum + 1):
            fname = f"{gen_count}th_generation_genomes"
            self.read_pickle(self.mkpath(fname))

    def parse_generation(self):
        gen_count = 0
        for generation in self.list_of_generation:
            list_of_genome = generation['list_of_genome']
            list_of_fitness = generation['list_of_fitness']
            high_fitness = generation['high_fitness']
            average_fitness = sum(list_of_fitness) / len(list_of_fitness)
            list_of_runtime = generation['list_of_runtime']

            self.genome_array.append(list_of_genome)
            self.fitness_array[gen_count, :] = list_of_fitness
            self.high_fitness_array[gen_count] = high_fitness
            self.average_fitness_array[gen_count] = average_fitness
            self.runtime_array[gen_count, :] = list_of_runtime

            gen_count += 1

    def get_parse_data(self):
        data = (copy.deepcopy(self.genome_array), copy.deepcopy(self.fitness_array), copy.deepcopy(self.high_fitness_array), copy.deepcopy(self.average_fitness_array), copy.deepcopy(self.runtime_array))
        return data

    def get_gennum(self):
        return len(self.list_of_generation)


file_manager = FileManager()
print("read all generation")
file_manager.read_all_generation(1353)
print("paese all generation")
file_manager.parse_generation()
genome_array, fitness_array, high_fitness_array, average_fitness_array, runtime_array = file_manager.get_parse_data()
gen_num = file_manager.get_gennum()
file_manager.__init__()

ploter = Ploter()
ploter.put_high_fitness(high_fitness_array)
ploter.put_average_fitness(average_fitness_array)
ploter.put_gennum(gen_num)

ploter.save_plot()