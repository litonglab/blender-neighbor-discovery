import numpy as np

from algo.accumulator import ProbabilitySummationAccumulator


class BruteForceLossAdvdelaySimulator:
    def __init__(self, adv_interval, scan_interval, scan_window, end_time, loss_rate=0, max_advdelay=10):
        self.adv_interval = adv_interval
        self.scan_interval = scan_interval
        self.scan_window = scan_window
        self.end_time = end_time
        self.inf = self.end_time + 1
        self.latency_pdf = np.zeros(self.inf + 1)
        self.winpos2latency = dict()
        self.loss_rate_percentage = loss_rate
        self.loss_rate = loss_rate / 100
        self.max_advdelay = max_advdelay

    def simulate_once(self, first_adv_ts, first_scan_down_ts):
        adv_cur_base_ts = first_adv_ts
        scan_cur_up_ts = first_scan_down_ts - self.scan_window
        adv_evt_count = 1
        discovery_times = 0
        adv_ts_delay_range = self.max_advdelay
        base_prob = 1
        latency2pdf = dict()
        prob_accumulator = ProbabilitySummationAccumulator(self.max_advdelay)

        while scan_cur_up_ts <= self.end_time:
            while adv_cur_base_ts + adv_ts_delay_range < scan_cur_up_ts:
                # Current scan window occur after all possible positions of current advertise event
                adv_cur_base_ts += self.adv_interval
                adv_ts_delay_range += self.max_advdelay
                adv_evt_count += 1
                prob_accumulator.next_layer()
            scan_cur_down_ts = scan_cur_up_ts + self.scan_window
            if adv_cur_base_ts < scan_cur_down_ts:
                # At least a partition of possible positions of current advertise event occurs in current scan window
                discovery_times += 1
                for adv_ts in range(max(adv_cur_base_ts, scan_cur_up_ts),
                                    min(adv_cur_base_ts + adv_ts_delay_range + 1, scan_cur_down_ts, self.end_time + 1)):
                    delay = adv_ts - adv_cur_base_ts
                    if prob_accumulator.get_at(adv_evt_count, delay) <= 0:
                        continue
                    # Get the probability of current discovery occurring
                    discovery_prob = prob_accumulator.get_pdf_at(adv_evt_count, delay) * (1 - self.loss_rate)

                    # Update acumulator
                    prob_accumulator.reduce_at(adv_evt_count, delay, self.loss_rate)

                    adv_pos_in_scan_win = adv_ts - scan_cur_up_ts
                    base_prob -= discovery_prob
                    latency2pdf[adv_ts] = (discovery_prob, adv_pos_in_scan_win)

            scan_cur_up_ts += self.scan_interval

        if base_prob > 0:
            latency2pdf[self.inf] = (base_prob, -1)
        return latency2pdf

    def simulate_all(self, to_cdf=True):
        if self.scan_interval <= self.adv_interval:
            raise NotImplementedError(r"$T_a > T_s$ is under refining.")
        if self.adv_interval <= self.scan_window:
            raise NotImplementedError(r"Validity of this implementation when $T_a < d_s$ is under discussion.")
        phase_projection_times = self.scan_interval // self.adv_interval
        remain_cases = self.scan_interval % self.adv_interval
        prob_accumulator = ProbabilitySummationAccumulator(self.max_advdelay)

        for _ in range(phase_projection_times):
            prob_accumulator.next_layer()
        adv_ts_delay_pdf = prob_accumulator.get_all_pdf()

        delta2latency_pdf = [None]
        for delta in range(1, self.max_advdelay * phase_projection_times + 1):
            delta2latency_pdf.append(self.simulate_once(0, -delta))

        for first_scan_down_ts in range(self.adv_interval):
            # START Base-case Simulation
            latency2pdf = self.simulate_once(0, first_scan_down_ts)

            for latency, (prob, _) in latency2pdf.items():
                self.latency_pdf[latency] += prob
            # END Base-case Simulation

            # START Phase-Difference Projection
            projection_times = (phase_projection_times + 1) if first_scan_down_ts < remain_cases \
                else phase_projection_times
            for projection_time in range(1, projection_times):
                base_adv_ts = projection_time * self.adv_interval
                adv_ts_delay_range = projection_time * self.max_advdelay
                # if base_adv_ts + adv_ts_delay_range >= self.scan_interval:
                #     adv_ts_delay_range -= (base_adv_ts + adv_ts_delay_range) - self.scan_interval + 1

                delay_pdf = adv_ts_delay_pdf[projection_time - 1]
                for adv_delay in range(first_scan_down_ts + 1, adv_ts_delay_range + 1):
                    if delay_pdf[adv_delay] > 0:
                        delta = adv_delay - first_scan_down_ts
                        adv_ts = adv_delay + base_adv_ts
                        for latency, (prob, _) in delta2latency_pdf[delta].items():
                            if prob > 0:
                                self.latency_pdf[min(self.inf, latency + adv_ts)] += \
                                    prob * delay_pdf[adv_delay]

                for adv_delay in range(0, min(adv_ts_delay_range, first_scan_down_ts) + 1):
                    if delay_pdf[adv_delay] > 0:
                        adv_ts = adv_delay + base_adv_ts
                        for latency, (prob, _) in latency2pdf.items():
                            if prob > 0:
                                self.latency_pdf[min(self.inf, latency + adv_ts)] += \
                                    prob * delay_pdf[adv_delay]

            # END Phase-Difference Projection

        phase_projection_latency_pdf = self.latency_pdf.copy()

        for latency, prob in enumerate(phase_projection_latency_pdf):
            if prob > 0:
                for phi_s in range(1, self.adv_interval):
                    self.latency_pdf[min(self.inf, latency + phi_s)] += prob

        prob_sum = sum(self.latency_pdf)
        pdf = self.latency_pdf / prob_sum

        if to_cdf:
            cdf = np.cumsum(pdf)
            cdf[-1] = 1.0
            return cdf

        return pdf

# TODO: Faster Projection
class DynamicProjectionLossAdvdelaySimulator(BruteForceLossAdvdelaySimulator):
    def __init__(self):
        pass

if __name__ == '__main__':
    blender = BruteForceLossAdvdelaySimulator(adv_interval=1860,
                                    scan_interval=5120,
                                    scan_window=512,
                                    end_time=50000,
                                    loss_rate=0)
    blender.simulate_all()
