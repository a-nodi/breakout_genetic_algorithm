import copy
import random
from neural_network import Network


class Generation:
    def __init__(self):
        self.list_of_genome = []
        self.population = 25
        self.number_of_best_time_ones = 4
        # self.number_of_best_ones = 8
        self.number_of_best_ones = 4
        self.number_of_lucky_ones = 1
        self.list_of_best_genome = []
        self.chance_of_mutation = 0.1

    def set_initial_genomes(self):
        list_of_genome = []
        for i in range(self.population):
            list_of_genome.append(Network())
        return list_of_genome

    def set_genomes(self, genomes):
        self.list_of_genome = genomes

    def keep_best_genomes(self):
        self.list_of_genome.sort(key=lambda x: x.fitness, reverse=True)
        self.list_of_best_genome = self.list_of_genome[:self.number_of_best_ones]
        # self.list_of_best_genome.sort(key=lambda x: x.runtime)
        # self.list_of_best_genome = self.list_of_best_genome[:self.number_of_best_time_ones]
        self.list_of_genome = copy.deepcopy(self.list_of_best_genome[:])

    def mutations(self):  # 변이
        while len(self.list_of_genome) < self.number_of_best_ones * 4:
            genome1 = random.choice(self.list_of_best_genome)
            genome2 = random.choice(self.list_of_best_genome)
            self.list_of_genome.append(self.mutate(self.cross_over(genome1, genome2)))

        while len(self.list_of_genome) < self.population:
            genome = random.choice(self.list_of_best_genome)
            self.list_of_genome.append(self.mutate(genome))

        random.shuffle(self.list_of_genome)

        return self.list_of_genome

    def cross_over(self, genome1, genome2):  # 교차
        new_genome = copy.deepcopy(genome1)
        other_genome = copy.deepcopy(genome2)

        cut_location = int(len(new_genome.web1) * random.uniform(0, 1))
        for i in range(cut_location):
            new_genome.web1[i], other_genome.web1[i] = other_genome.web1[i], new_genome.web1[i]

        cut_location = int(len(new_genome.web2) * random.uniform(0, 1))
        for i in range(cut_location):
            new_genome.web2[i], other_genome.web2[i] = other_genome.web2[i], new_genome.web2[i]

        cut_location = int(len(new_genome.web3) * random.uniform(0, 1))
        for i in range(cut_location):
            new_genome.web3[i], other_genome.web3[i] = other_genome.web3[i], new_genome.web3[i]

        return new_genome

    def mutate_weights(self, weights):  # 가중치 변이

        if random.uniform(0, 1) < self.chance_of_mutation:
            return weights * (random.uniform(0, 1) - 0.5) * 3 + (random.uniform(0, 1) - 0.5)
        else:
            return 0

    def mutate(self, genome):  # 유전자 변이
        new_genome = copy.deepcopy(genome)
        new_genome.web1 += self.mutate_weights(new_genome.web1)
        new_genome.web2 += self.mutate_weights(new_genome.web2)
        new_genome.web3 += self.mutate_weights(new_genome.web3)
        return new_genome
