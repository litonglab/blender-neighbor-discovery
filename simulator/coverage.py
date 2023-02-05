import random
from typing import List

import numpy as np

from algo.intervals import Intervals, ProbabilityIntervals
from utils import Log


class CoverageLatencyInference:
    def __init__(self, adv_interval, scan_interval, scan_window, end_time):
        self.adv_interval = adv_interval
        self.scan_interval = scan_interval
        self.scan_window = scan_window
        self.end_time = end_time

    def try_cover(self):
        Log.V("CoverageInference", "Coverage Start")
        adv_ts = 0
        coverage_stat = Intervals((0, self.scan_interval))
        latency2prob = dict()
        while adv_ts <= self.end_time:
            latency = adv_ts
            rel_pos = adv_ts % self.scan_interval
            if rel_pos >= self.scan_window - 1:
                # print(f"Interval: ({rel_pos - self.scan_window + 1}, {rel_pos + 1})")
                prob, _ = coverage_stat.get_new_coverage(interval=(rel_pos - self.scan_window + 1, rel_pos + 1),
                                                         do_insert_after=True)
            else:
                # print(f"Interval: ({self.scan_interval - (self.scan_window - rel_pos - 1)}, {self.scan_interval}) and (0, {rel_pos + 1})")
                prob, _ = coverage_stat.get_new_coverage_all(interval_list=[
                    (self.scan_interval - (self.scan_window - rel_pos - 1), self.scan_interval), (0, rel_pos + 1)])
            latency2prob[latency] = prob
            adv_ts += self.adv_interval
            if coverage_stat.get_remain(use_int=True) < 0:
                raise ValueError("Fault in interval calculation")
            if coverage_stat.get_remain(use_int=True) == 0:
                print("No segment left")
                break
        if self.end_time in latency2prob.keys():
            latency2prob[self.end_time] += coverage_stat.get_remain(use_int=True)
        else:
            latency2prob[self.end_time] = coverage_stat.get_remain(use_int=True)
        Log.V("CoverageInference", "Coverage Complete")
        return latency2prob

    def simulate_all(self, to_cdf=True):
        base_latency2prob = self.try_cover()
        latency_pdf = np.zeros(self.end_time + 1)
        for phi_a in range(self.adv_interval):
            for latency, prob in base_latency2prob.items():
                latency_pdf[min(latency + phi_a, self.end_time)] += prob
        Log.V("CoverageInference", "Calculation Complete")
        prob_sum = sum(latency_pdf)
        pdf = latency_pdf / prob_sum
        if to_cdf:
            cdf = np.cumsum(pdf)
            cdf[-1] = 1.0
            return cdf
        return pdf


# class AlternationBroadcastConfig:
# def __init__(self):
#     self.config_list = []
#     self.cur_config_idx = 0
#
# def add(self, interval, repeat_time: int):
#     if interval <= 0:
#         Log.E("ABPConfig", "Non-positive Interval Encountered")
#         raise ValueError
#     if repeat_time <= 0:
#         Log.E("ABPConfig", "Non-positive Repeat-Time Encountered")
#         raise ValueError
#     self.config_list.append((interval, repeat_time))
#
# def refresh(self):
#     self.config_list = []
#
# def get_advseq_startat(self, config_idx: int):
#     if config_idx < 0 or config_idx >= len(self.config_list):
#         Log.E("ABPConfig", "Invalid Index for Broadcast Configuration")
#         raise ValueError
#
# class IntervalIterator:
#     def __init__(self, config_list, start_config_index, ):
#         self.config_list = config_list
#         self.start_index = start_config_index
#         self.cur_index = 0
# def next_interval(self):
#     pass

class AlternationBroadcastConfig:
    def __init__(self, root_sequence: List[int]):
        self.root_seq = root_sequence
        self.itv_sum = sum(root_sequence)
        self.seq_start_index = 0
        self.repeat_pt = 0

    def __str__(self):
        return str(self.root_seq)

    def set_seq_start_index(self, idx):
        self.seq_start_index = idx
        self.repeat_pt = (idx + 1) % len(self.root_seq)

    def next_interval(self):
        self.repeat_pt = (self.repeat_pt + 1) % len(self.root_seq)
        return self.root_seq[self.repeat_pt]

    def __len__(self):
        return len(self.root_seq)

    def __getitem__(self, item):
        return self.root_seq[item]

    def rand_start(self):
        rand_val = random.randint(0, self.itv_sum)
        s = 0
        i = 0
        while True:
            if s + self[i] >= rand_val:
                break
            s += self[i]
            i += 1
        return i, rand_val - s


class CoverageLatencyInference4AlternationBroadcast:
    def __init__(self, abp_config: AlternationBroadcastConfig, scan_interval, scan_window, end_time):
        self.abp_config = abp_config
        self.scan_interval = scan_interval
        self.scan_window = scan_window
        self.end_time = end_time

    def try_cover(self, start_index):
        Log.V("CoverageInference", "Coverage Start")
        self.abp_config.set_seq_start_index(start_index)
        adv_ts = 0
        coverage_stat = Intervals((0, self.scan_interval))
        latency2prob = dict()
        while adv_ts <= self.end_time:
            latency = adv_ts
            rel_pos = adv_ts % self.scan_interval
            if rel_pos >= self.scan_window - 1:
                # print(f"Interval: ({rel_pos - self.scan_window + 1}, {rel_pos + 1})")
                prob, _ = coverage_stat.get_new_coverage(interval=(rel_pos - self.scan_window + 1, rel_pos + 1),
                                                         do_insert_after=True)
            else:
                # print(f"Interval: ({self.scan_interval - (self.scan_window - rel_pos - 1)}, {self.scan_interval}) and (0, {rel_pos + 1})")
                prob, _ = coverage_stat.get_new_coverage_all(interval_list=[
                    (self.scan_interval - (self.scan_window - rel_pos - 1), self.scan_interval), (0, rel_pos + 1)])
            latency2prob[latency] = prob
            adv_ts += self.abp_config.next_interval()
            if coverage_stat.get_remain(use_int=True) < 0:
                raise ValueError("Fault in interval calculation")
            if coverage_stat.get_remain(use_int=True) == 0:
                break
        if self.end_time in latency2prob.keys():
            latency2prob[self.end_time] += coverage_stat.get_remain(use_int=True)
        else:
            latency2prob[self.end_time] = coverage_stat.get_remain(use_int=True)
        Log.V("CoverageInference", "Coverage Complete")
        return latency2prob

    def simulate_all(self, to_cdf=True):
        latency_pdf = np.zeros(self.end_time + 1)
        for i in range(len(self.abp_config)):
            base_latency2prob = self.try_cover(i)
            for phi_a in range(self.abp_config[i]):
                for latency, prob in base_latency2prob.items():
                    latency_pdf[min(latency + phi_a, self.end_time)] += prob
            Log.V("CoverageInference", "Calculation Complete")
        prob_sum = sum(latency_pdf)
        pdf = latency_pdf / prob_sum
        if to_cdf:
            cdf = np.cumsum(pdf)
            cdf[-1] = 1.0
            return cdf
        return pdf


class CLIFABL:
    def __init__(self, abp_config: AlternationBroadcastConfig, scan_interval, scan_window, end_time, fail_rate):
        self.abp_config = abp_config
        self.scan_interval = scan_interval
        self.scan_window = scan_window
        self.end_time = end_time
        self.fail_rate = fail_rate

    def try_cover(self, start_index):
        Log.V("CoverageInference", "Coverage Start")
        self.abp_config.set_seq_start_index(start_index)
        adv_ts = 0
        coverage_stat = ProbabilityIntervals((0, self.scan_interval))
        latency2prob = dict()
        while adv_ts <= self.end_time:
            latency = adv_ts
            rel_pos = adv_ts % self.scan_interval
            if rel_pos >= self.scan_window - 1:
                # print(f"Interval: ({rel_pos - self.scan_window + 1}, {rel_pos + 1})")
                prob = coverage_stat.get_new_coverage(interval=(rel_pos - self.scan_window + 1, rel_pos + 1, self.fail_rate),
                                                         do_insert_after=True)
            else:
                # print(f"Interval: ({self.scan_interval - (self.scan_window - rel_pos - 1)}, {self.scan_interval}) and (0, {rel_pos + 1})")
                prob = coverage_stat.get_new_coverage_all(interval_list=[
                    (self.scan_interval - (self.scan_window - rel_pos - 1), self.scan_interval, self.fail_rate), (0, rel_pos + 1, self.fail_rate)])
            latency2prob[latency] = prob
            if coverage_stat.get_remain() < 0:
                coverage_stat.coverage = 1.0
                break
            adv_ts += self.abp_config.next_interval()

        if self.end_time in latency2prob.keys():
            latency2prob[self.end_time] += coverage_stat.get_remain()
        else:
            latency2prob[self.end_time] = coverage_stat.get_remain()
        Log.V("CoverageInference", "Coverage Complete")
        return latency2prob

    def simulate_all(self, to_cdf=True):
        latency_pdf = np.zeros(self.end_time + 1)
        for i in range(len(self.abp_config)):
            base_latency2prob = self.try_cover(i)
            for phi_a in range(self.abp_config[i]):
                for latency, prob in base_latency2prob.items():
                    latency_pdf[min(latency + phi_a, self.end_time)] += prob
            Log.V("CoverageInference", "Calculation Complete")
        prob_sum = sum(latency_pdf)
        pdf = latency_pdf / prob_sum
        if to_cdf:
            cdf = np.cumsum(pdf)
            cdf[-1] = 1.0
            return cdf
        return pdf
