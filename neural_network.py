import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def relu(x):
    return np.maximum(0, x)


class Network:
    def __init__(self):
        self.input_layer_size = 2
        self.hidden_layer1_size = 8
        self.hidden_layer2_size = 6
        self.output_layer_size = 1
        self.web1 = np.random.rand(self.input_layer_size, self.hidden_layer1_size)
        self.web2 = np.random.rand(self.hidden_layer1_size, self.hidden_layer2_size)
        self.web3 = np.random.rand(self.hidden_layer2_size, self.output_layer_size)
        self.fitness = 0
        self.runtime = 0

    def next_move(self, input_):
        z1 = np.dot(input_, self.web1)
        # a1 = sigmoid(z1)
        a1 = z1
        z2 = np.dot(a1, self.web2)
        a2 = sigmoid(z2)
        # a2 = z2
        z3 = np.dot(a2, self.web3)
        output = sigmoid(z3)
        return output

    def set_weights(self, web1, web2, web3):
        self.web1 = web1
        self.web2 = web2
        self.web3 = web3
