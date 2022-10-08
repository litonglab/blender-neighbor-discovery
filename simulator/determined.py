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
                    latency2pdf[adv_ts] = discovery_prob  # (discovery_prob, adv_pos_in_scan_win)

            scan_cur_up_ts += self.scan_interval

        if base_prob > 0:
            latency2pdf[self.inf] = base_prob  # (base_prob, -1)
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

        phi_s_range = (0, self.adv_interval)

        for phi_s in range(*phi_s_range):
            # START Base-Case Simulation
            latencyxprob = np.asarray(list(self.simulate_once(0, phi_s).items()))
            for (latency, prob) in latencyxprob:
                self.latency_pdf[int(latency)] += prob
            # END Base-Case Simulation

            base_adv_ts = 0
            adv_delay_max_range = 0

            # START Phase-Difference Projection
            for projection_time in range(1, phase_projection_times):
                base_adv_ts += self.adv_interval
                adv_delay_max_range += self.max_advdelay
                delay_pdf = adv_ts_delay_pdf[projection_time - 1]
                for delay in range(adv_delay_max_range + 1):
                    adv_ts = base_adv_ts + delay
                    delay_prob = delay_pdf[delay]
                    for (latency, prob) in latencyxprob:
                        self.latency_pdf[min(int(latency) + adv_ts, self.inf)] += prob * delay_prob

            # special check of last projection
            projection_time = phase_projection_times
            base_adv_ts += self.adv_interval
            adv_delay_max_range += self.max_advdelay
            delay_pdf = adv_ts_delay_pdf[projection_time - 1]
            for delay in range(adv_delay_max_range + 1):
                adv_ts = base_adv_ts + delay
                scan_win_end_ts = adv_ts + phi_s
                if scan_win_end_ts > self.scan_interval:
                    break
                delay_prob = delay_pdf[delay]
                for (latency, prob) in latencyxprob:
                    self.latency_pdf[min(int(latency) + adv_ts, self.inf)] += prob * delay_prob
            # END Phase-Difference Projection

        phase_projection_latency_pdf = self.latency_pdf.copy()

        # START Range-Entrance Projection
        for latency, prob in enumerate(phase_projection_latency_pdf):
            if prob > 0:
                for phi_s in range(1, self.adv_interval):
                    self.latency_pdf[min(self.inf, latency + phi_s)] += prob
        # END Range-Entrance Projection

        # Output process
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
