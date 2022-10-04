import numpy as np
from matplotlib import pyplot as plt

from simulator.determined import BruteForceLossAdvdelaySimulator
import random

from simulator.sampler import PureBleSimulator
import utils.plotter as pt
from utils import Log

if __name__ == '__main__':
    for _ in range(10):
        scan_interval = random.randint(1000, 5000)
        adv_interval = random.randint(200, scan_interval-500)
        scan_window = random.randint(30, scan_interval // 3 * 2)
        loss_rate = random.randint(0, 65)
        config = f"scan_interval: {scan_interval}, scan_window: {scan_window}," \
                 f" adv_interval: {adv_interval}, loss: {loss_rate}%"
        print(config)
        blender = BruteForceLossAdvdelaySimulator(adv_interval=adv_interval,
                                        scan_interval=scan_interval,
                                        scan_window=scan_window,
                                        end_time=50000,
                                        loss_rate=loss_rate)
        sampler = PureBleSimulator(adv_interval=adv_interval,
                                        scan_interval=scan_interval,
                                        scan_window=scan_window,
                                        end_time=50000,
                                        loss_rate=loss_rate)
        try:
            blender_result_cdf = blender.simulate_all(to_cdf=True)
            sampler_result_values = sampler.get_latency_n_times(n=50000)

            x = np.asarray([i for i in range(len(blender_result_cdf))])
            ax = pt.plot_cdf(x, blender_result_cdf, lc='b')
            pt.plot_values_as_cdf(sampler_result_values, ax=ax)
            plt.title(config)
            plt.show()
        except NotImplementedError as e:
            Log.E('Playground', e)
