import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d

from algo.intervals import Intervals
from simulator.coverage import CoverageLatencyInference, CoverageLatencyInference4AlternationBroadcast, \
    AlternationBroadcastConfig, CLIFABL
from simulator.determined import BruteForceLossAdvdelaySimulator
import random

from simulator.sampler import PureBleSimulator, AlternationBroadcastSampler
import utils.plotter as pt
from utils import Log


def determined_test():
    for _ in range(10):
        scan_interval = random.randint(1000, 5000)
        adv_interval = random.randint(200, scan_interval - 500)
        scan_window = random.randint(30, scan_interval // 3 * 2)
        loss_rate = random.randint(0, 65)
        config = f"scan_interval: {scan_interval}, scan_window: {scan_window}," \
                 f" adv_interval: {adv_interval}, loss: {loss_rate}%"
        print(config)
        blender = BruteForceLossAdvdelaySimulator(adv_interval=adv_interval,
                                                  scan_interval=scan_interval,
                                                  scan_window=scan_window,
                                                  end_time=50000,
                                                  loss_rate=loss_rate,
                                                  max_advdelay=15)
        sampler = PureBleSimulator(adv_interval=adv_interval,
                                   scan_interval=scan_interval,
                                   scan_window=scan_window,
                                   end_time=50000,
                                   loss_rate=loss_rate,
                                   max_advdelay=15)
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


def coverage_test():
    for _ in range(10):
        # scan_interval = random.randint(1000, 5000)
        # adv_interval = random.randint(200, scan_interval - 500)
        # scan_window =random.randint(30, scan_interval // 3 * 2)
        scan_interval = 3685
        adv_interval = 3651
        scan_window = 1120
        loss_rate = random.randint(0, 65)
        config = f"scan_interval: {scan_interval}, scan_window: {scan_window}," \
                 f" adv_interval: {adv_interval}"

        blender = CoverageLatencyInference(adv_interval=adv_interval,
                                           scan_interval=scan_interval,
                                           scan_window=scan_window,
                                           end_time=50000)
        sampler = PureBleSimulator(adv_interval=adv_interval,
                                   scan_interval=scan_interval,
                                   scan_window=scan_window,
                                   end_time=50000,
                                   loss_rate=0,
                                   max_advdelay=0)
        try:
            blender_result_cdf = blender.simulate_all(to_cdf=True)
            print(np.argmax(blender_result_cdf))
            sampler_result_values = sampler.get_latency_n_times(n=50000)
            print(max(sampler_result_values))

            x = np.asarray([i for i in range(len(blender_result_cdf))])
            ax = pt.plot_cdf(x, blender_result_cdf, lc='b')
            pt.plot_values_as_cdf(sampler_result_values, ax=ax)
            plt.title(config)
            plt.show()
        except NotImplementedError as e:
            Log.E('Playground', e)

def abp_test():
    for _ in range(1):
        # scan_interval = random.randint(1000, 6000)
        # abp_config = AlternationBroadcastConfig(random.sample(range(1000, 6000), random.randint(1, 70)))
        # scan_window =random.randint(30, scan_interval // 3 * 2)

        scan_interval = 3685
        abp_config = AlternationBroadcastConfig([3651])
        scan_window = 1120

        config = f"scan_interval: {scan_interval}, scan_window: {scan_window}," \
                 f" abp_config: {abp_config}"

        blender = CoverageLatencyInference4AlternationBroadcast(abp_config=abp_config,
                                           scan_interval=scan_interval,
                                           scan_window=scan_window,
                                           end_time=50000)
        sampler = AlternationBroadcastSampler(abp_config=abp_config,
                                   scan_interval=scan_interval,
                                   scan_window=scan_window,
                                   end_time=50000,
                                   loss_rate=0)
        try:
            blender_result_cdf = blender.simulate_all(to_cdf=True)
            sampler_result_values = sampler.get_latency_n_times(n=5000)
            print(max(sampler_result_values))

            x = np.asarray([i for i in range(len(blender_result_cdf))])
            ax = pt.plot_cdf(x, blender_result_cdf, lc='b')
            pt.plot_values_as_cdf(sampler_result_values, ax=ax)
            plt.title(config)
            plt.show()
        except NotImplementedError as e:
            Log.E('Playground', e)

def abp_loss_test():
    for _ in range(20):
        scan_interval = random.randint(1000, 6000)
        abp_config = AlternationBroadcastConfig(random.sample(range(1000, 6000), random.randint(1, 70)))
        scan_window =random.randint(30, scan_interval // 3 * 2)
        loss_rate = random.randint(10, 70) / 100

        # scan_interval = 3685
        # abp_config = AlternationBroadcastConfig([3651])
        # scan_window = 1120
        # loss_rate = 0.0

        config = f"scan_interval: {scan_interval}, scan_window: {scan_window}," \
                 f" abp: {abp_config}, loss rate: {loss_rate}"
        print(config)
        blender = CLIFABL(abp_config=abp_config,
                                           scan_interval=scan_interval,
                                           scan_window=scan_window,
                                           end_time=50000,
                                           fail_rate=loss_rate)
        sampler = AlternationBroadcastSampler(abp_config=abp_config,
                                   scan_interval=scan_interval,
                                   scan_window=scan_window,
                                   end_time=50000,
                                   loss_rate=round(loss_rate * 100))
        try:
            blender_result_cdf = blender.simulate_all(to_cdf=True)
            sampler_result_values = sampler.get_latency_n_times(n=5000)
            print(max(sampler_result_values))

            x = np.asarray([i for i in range(len(blender_result_cdf))])
            ax = pt.plot_cdf(x, blender_result_cdf, lc='b')
            pt.plot_values_as_cdf(sampler_result_values, ax=ax)
            plt.title(config)
            plt.show()
        except NotImplementedError as e:
            Log.E('Playground', e)

def abp_compare():
    """
    TODO: set up at least 9 different parameter sets and run alternation broadcasting.
                Then take 200-300 random samples in realistic emulation to form a distribution.
                Calculate the RMSE between the distribution generated by simulation and emulation.
                RMSE between 0.05-0.1 is desired
    """

    # Sample Configuration
    scan_interval = 5120
    scan_window = 512
    abp_config = AlternationBroadcastConfig([1860, 1860, 1860, 1860, 1860, 2140, 2140, 2140, 2140, 2140, 2140, 2140])
    loss_rate = 0.3 # May need 2-3 different loss rates regarding different environments

    end_time = 40000
    config = f"scan_interval: {scan_interval}, scan_window: {scan_window}," \
             f" abp: {abp_config}, loss rate: {loss_rate}"
    print(config)

    # the Alternation Broadcast Simulator
    blender = CLIFABL(abp_config=abp_config,
                      scan_interval=scan_interval,
                      scan_window=scan_window,
                      end_time=end_time,
                      fail_rate=loss_rate)
    blender_result_cdf = blender.simulate_all(to_cdf=True) # A numpy array of length (end_time + 1), index is latency and value is probability

    """
    *********YOUR CODE HERE***********
    """
    # Read Emulation latency distribution
    import h5py
    f = h5py.File('yourdata.mat', 'r')
    data = f.get('data/variable1')
    emulation_data = np.array(data)  # For converting to a NumPy array

    # OR export Blender result
    np.save(blender_result_cdf, "blender_temp.npy")

    # Calculate RMSE

    """
    *********END OF YOUR CODE***********
    """

if __name__ == '__main__':
    Log.debug()
    # abp_loss_test()
    abp_compare()
