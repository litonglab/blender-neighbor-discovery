import random
from simulator.coverage import AlternationBroadcastConfig
from utils import Log
import numpy as np
import os


TIMEOUT_NOTIFIER = 1
LOG_ROOT = os.path.join('C:/code', 'traces')

class AbstractSimulator:
    def __init__(self, scan_interval, scan_window, end_time, fail_rate, max_advdelay):
        if scan_interval < scan_window:
            raise ValueError('Scan Interval is unreasonably set to less than Scan Window.')
        if end_time <= 0:
            raise ValueError("Invalid simulation end time.")
        if fail_rate < 0 or fail_rate > 100:
            Log.W('Simulator Initializing', 'Invalid fail rate provided. Fail rate set to 0%.')
            fail_rate = 0 if fail_rate < 0 else 100
        self.scan_interval = scan_interval
        self.scan_window = scan_window
        self.end_time = end_time
        self.fail_rate = fail_rate
        self.max_advdelay = max_advdelay

    def simulate_once(self):
        raise NotImplementedError

    def get_discover_rate_n_times(self, target_time, n=10000):
        if n <= 0:
            raise ValueError("Invalid n provided. n must be larger than zero.")
        if target_time > self.end_time:
            Log.W('Discover Rate', 'Target_time larger than provided maximum simulation time.')
            return 1.0
        discover_count = 0
        for _ in range(n):
            if self.simulate_once() <= target_time:
                discover_count += 1
        return discover_count / n

    def to_identifier_string(self):
        return 'W%d_T%d_F%d_R%d_E%d' % \
               (self.scan_window, self.scan_interval, self.fail_rate, self.max_advdelay, self.end_time)

    def get_latency_n_times(self, n, to_file, cover_file, file_prefix):
        file_name = file_prefix + self.to_identifier_string() + ('_%d.npy' % n)
        file_exist = os.path.isfile(file_name)
        if not cover_file and file_exist:
            return np.load(file_name)
        latencies = np.array([self.simulate_once() for _ in range(n)])
        if to_file:
            if not file_exist or cover_file:
                np.save(file_name, latencies)
        return latencies


class PureBleSimulator(AbstractSimulator):
    def __init__(self, adv_interval, scan_interval, scan_window, end_time, loss_rate=0, max_advdelay=10):
        super().__init__(scan_interval, scan_window, end_time, fail_rate=loss_rate, max_advdelay=max_advdelay)
        self.adv_interval = adv_interval

    def gen_adv_seq(self):
        elapsed = np.random.randint(0, self.adv_interval)
        res = [elapsed]
        while True:
            up = elapsed + self.adv_interval
            if self.max_advdelay > 0:
                up += np.random.randint(0,  self.max_advdelay + 1)
            if up > self.end_time:
                break
            res.append(up)
            elapsed = up
        return res

    def gen_scan_seq(self):
        elapsed = -np.random.randint(0, self.scan_interval)
        res = []
        while elapsed < self.end_time:
            down = elapsed + self.scan_interval
            up = down - self.scan_window
            res.append(up)
            res.append(down)
            elapsed = down
        return res

    def to_identifier_string(self):
        return 'A%d_' % self.adv_interval + super().to_identifier_string()

    def get_latency_n_times(self, n, to_file=False, cover_file=False, file_prefix=LOG_ROOT + 'singleSource/'):
        return super().get_latency_n_times(n=n, to_file=to_file, cover_file=cover_file, file_prefix=file_prefix)

    def simulate_once(self):
        adv_seq = self.gen_adv_seq()
        scan_seq = self.gen_scan_seq()
        adv_len = len(adv_seq)
        scan_len = len(scan_seq)
        adv_idx = 0
        scan_idx = 0
        while scan_idx < scan_len:
            win_up = scan_seq[scan_idx]
            win_down = scan_seq[scan_idx + 1]
            while win_up > adv_seq[adv_idx]:
                adv_idx += 1
                if adv_idx >= adv_len:
                    # print(scan_seq, adv_seq)
                    return self.end_time + TIMEOUT_NOTIFIER
            while win_down > adv_seq[adv_idx]:
                if self.fail_rate == 0 or self.fail_rate / 100 < np.random.random():
                    return adv_seq[adv_idx]
                adv_idx += 1
                if adv_idx >= adv_len:
                    # print(scan_seq, adv_seq)
                    return self.end_time + TIMEOUT_NOTIFIER
            scan_idx += 2
       # print(scan_seq, adv_seq)
        return self.end_time + TIMEOUT_NOTIFIER

class AlternationBroadcastSampler(AbstractSimulator):
    def __init__(self, abp_config: AlternationBroadcastConfig, scan_interval, scan_window, end_time, loss_rate=0):
        super().__init__(scan_interval, scan_window, end_time, fail_rate=loss_rate, max_advdelay=0)
        self.abp_config = abp_config

    def to_identifier_string(self):
        return 'ABP_W%d_T%d_F%d_E%d' % \
               (self.scan_window, self.scan_interval, self.fail_rate, self.end_time)

    def simulate_once(self):
        start_adv_seq_index, phi_a = self.abp_config.rand_start()
        self.abp_config.set_seq_start_index(start_adv_seq_index)
        phi_s = random.randint(0, self.scan_interval)
        adv_ts = phi_a
        scan_down_ts = phi_s
        scan_up_ts = phi_s - self.scan_window
        while scan_up_ts <= self.end_time:
            while scan_up_ts > adv_ts:
                adv_ts += self.abp_config.next_interval()
            if adv_ts > self.end_time:
                return self.end_time + TIMEOUT_NOTIFIER
            while adv_ts < scan_down_ts and adv_ts <= self.end_time:
                if self.fail_rate == 0 or self.fail_rate / 100 < np.random.random():
                    return adv_ts
                adv_ts += self.abp_config.next_interval()

            scan_down_ts += self.scan_interval
            scan_up_ts = scan_down_ts - self.scan_window
        return self.end_time + TIMEOUT_NOTIFIER

    def get_latency_n_times(self, n, to_file=False, cover_file=False, file_prefix=LOG_ROOT + 'alternationBroadcast/'):
        return super().get_latency_n_times(n=n, to_file=to_file, cover_file=cover_file, file_prefix=file_prefix)