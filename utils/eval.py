import numpy as np
from scipy.interpolate import interp1d


def mse(emulation_latencies, simulation_cdf, end_time, sample_num=10000):
    # TODO: Calculate mse between the emulation latencies and simulation cdf
    # latency_range = np.linspace(0, end_time, num=sample_num)
    # count, bins_count = np.histogram(emulation_latencies, bins=np.arange(0, end_time))
    # pdf = count / sum(count)
    # cdf = np.cumsum(pdf)
    # f = interp1d(np.concatenate(([0], bins_count[1:], [end_time])), np.concatenate((np.array([0]), cdf, np.array([1]))))
    # cdf_no = f(latency_range)
    pass