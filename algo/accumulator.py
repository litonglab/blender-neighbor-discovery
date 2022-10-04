import numpy as np


class ProbabilityDistributionAccumulator:
    def __init__(self, success_rate):
        self.success_rate = success_rate
        self.probability_space = list()
        self.remain_probability_space = list()
        self.probability_space_length = 0

    def get_probability_at(self, pos):
        while self.probability_space_length - 1 < pos:
            self.next_probability()
        return self.probability_space[pos]

    def next_probability(self):
        new_probability = np.power((1 - self.success_rate), self.probability_space_length) * self.success_rate
        remain_probability = np.power((1 - self.success_rate), self.probability_space_length + 1)
        self.probability_space.append(new_probability)
        self.remain_probability_space.append(remain_probability)
        self.probability_space_length += 1
        return new_probability

    def get_remain_probability_at(self, pos):
        if pos <= 0:
            return 1
        while self.probability_space_length - 1 < pos:
            self.next_probability()
        return self.remain_probability_space[pos]


class ProbabilitySummationAccumulator:
    def __init__(self, max_val):
        self.max_val = max_val
        self.layers = [np.ones(max_val + 1)]
        self.layers_sum = [max_val + 1]
        self.layer_count = 1

    #     self.initialize(max_layer_num)
    #
    # def initialize(self, layer_num):
    #     self.layers = [np.array([1 for i in range(self.max_val+1)], dtype=int)]
    #     self.layers_pdf = [self.layers[0]/np.sum(self.layers[0])]
    #     self.layer_count = 1
    #     while self.layer_count < layer_num:
    #         self.next_layer()
    #     self.layers_sum = [sum(layer) for layer in self.layers]
    def get_all_pdf(self):
        layers_pdf = []
        for i, l in enumerate(self.layers):
            layers_pdf.append(l / self.layers_sum[i])
        return layers_pdf

    def next_layer(self):
        last_layer = self.layers[-1]
        self.layer_count += 1
        new_layer = np.zeros(self.layer_count * self.max_val + 1)
        window_sum = 0
        for val in range(0, self.max_val + 1):
            window_sum += last_layer[val]
            new_layer[val] = window_sum

        for val in range(self.max_val + 1, (self.layer_count - 1) * self.max_val + 1):
            window_sum += last_layer[val]
            window_sum -= last_layer[val - self.max_val - 1]
            new_layer[val] = window_sum

        for val in range((self.layer_count - 1) * self.max_val + 1, self.layer_count * self.max_val + 1):
            window_sum -= last_layer[val - self.max_val - 1]
            new_layer[val] = window_sum

        self.layers.append(new_layer)
        self.layers_sum.append(self.layers_sum[-1] * (self.max_val + 1))

    def get_at(self, time, pos):
        return self.layers[time - 1][pos]

    def get_pdf_at(self, time, pos):
        return self.layers[time - 1][pos] / self.layers_sum[time - 1]

    def ban_at(self, time, pos):
        self.layers[time - 1][pos] = 0

    def reduce_at(self, time, pos, ratio):
        self.layers[time - 1][pos] *= ratio
        if self.get_pdf_at(time, pos) < 0.00001:
            self.layers[time - 1][pos] = 0
