import numpy as np


def step(x):
    return x > 0.5


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def relu(x):
    return np.maximum(0, x)


class NetWork:
    def __init__(self):
        self.input_layer_size = 2
        self.hidden_layer1_size = 30
        self.hidden_layer2_size = 15
        self.output_layer_size = 1
        self.web1 = np.random.rand(self.input_layer_size, self.hidden_layer1_size)
        self.web2 = np.random.rand(self.hidden_layer1_size, self.hidden_layer2_size)
        self.web3 = np.random.rand(self.hidden_layer2_size, self.output_layer_size)

        self.fitness = 0

    def next_move(self, input_):
        z1 = np.dot(input_, self.web1)
        a1 = np.tanh(z1)
        z2 = np.dot(a1, self.web2)
        a2 = np.tanh(z2)
        z3 = np.dot(a2, self.web3)
        output = step(z3)
        return output
