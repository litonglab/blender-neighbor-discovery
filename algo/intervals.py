import bisect
from typing import Tuple, List


class Intervals:
    def __init__(self, limit: Tuple[int, int]):
        self.interval_sorted: List[Tuple[int, int]] = [(limit[0], limit[0]), (limit[1], limit[1])]
        self.limit: Tuple[int, int] = limit
        self.coverage = 0.0
        self.int_coverage = 0
        self.length = limit[1] - limit[0]

    def insert(self, interval: Tuple[int, int]):
        if interval[0] < self.limit[0] or interval[1] > self.limit[1]:
            raise ValueError(
                f"Interval [{interval[0]}, {interval[1]}) exceeds the interval limit [{self.limit[0]}, {self.limit[1]}).")
        position = bisect.bisect(self.interval_sorted, interval)
        self.interval_sorted.insert(position, interval)

        new_sorted = []
        for i in range(len(self.interval_sorted)):
            if not new_sorted or self.interval_sorted[i][0] > new_sorted[-1][1]:
                new_sorted.append(self.interval_sorted[i])
            else:
                new_sorted[-1] = (new_sorted[-1][0], max(new_sorted[-1][1], self.interval_sorted[i][1]))

        self.interval_sorted = new_sorted

    def get_new_coverage_all(self, interval_list: List[Tuple[int, int]]):
        coverage_int, coverage_ratio = 0, 0.0
        for i in interval_list:
            ci, cr = self.get_new_coverage(i, do_insert_after=True)
            coverage_int, coverage_ratio = coverage_int + ci, coverage_ratio + cr
        return coverage_int, coverage_ratio

    def get_new_coverage(self, interval: Tuple[int, int], do_insert_after=False):
        coverage_int = interval[1] - interval[0]
        for i in range(len(self.interval_sorted)):
            itvi = self.interval_sorted[i]
            itv_st = itvi[0]
            itv_ed = itvi[1]
            if itv_st <= interval[0] < itv_ed:
                for j in range(i, len(self.interval_sorted)):
                    itvj = self.interval_sorted[j]
                    if itvj[0] >= interval[1]:
                        break
                    coverage_int -= min(itvj[1], interval[1]) - max(itvj[0], interval[0])
                break
            if itv_st < interval[1] <= itv_ed:
                for j in range(i, -1, -1):
                    itvj = self.interval_sorted[j]
                    if itvj[1] <= interval[0]:
                        break
                    coverage_int -= min(itvj[1], interval[1]) - max(itvj[0], interval[0])
                break
        if do_insert_after:
            self.insert(interval)
        coverage_int = max(0, coverage_int)
        coverage_ratio = coverage_int / (self.limit[1] - self.limit[0])
        self.coverage += coverage_ratio
        self.int_coverage += coverage_int
        return coverage_int, coverage_ratio

    def get_remain(self, use_int=False):
        if use_int:
            return self.length - self.int_coverage
        return 1 - self.coverage


class ProbabilityIntervals:
    def __init__(self, limit: Tuple[int, int]):
        self.interval_sorted: List[Tuple[int, int, float]] = [(limit[0], limit[0], 0.0), (limit[1], limit[1], 0.0)]
        self.limit: Tuple[int, int] = limit
        self.coverage = 0.0
        self.length = limit[1] - limit[0]

    def insert(self, interval: Tuple[int, int, float]):
        if interval[0] < self.limit[0] or interval[1] > self.limit[1]:
            raise ValueError(
                f"Interval [{interval[0]}, {interval[1]}) exceeds the interval limit [{self.limit[0]}, {self.limit[1]}).")

        new_sorted: List[Tuple[int, int, float]] = []
        passed = False
        for i in range(len(self.interval_sorted)):
            cur_itv = self.interval_sorted[i]
            if not new_sorted or cur_itv[1] <= interval[0] or passed:
                new_sorted.append(cur_itv)
                continue
            if cur_itv[0] >= interval[1]:
                new_sorted.append(interval)
                new_sorted.append(cur_itv)
                passed = True
                continue
            # collided
            if interval[0] < cur_itv[0]:
                new_sorted.append((interval[0], min(interval[1], cur_itv[0]), interval[2]))
            new_sorted.append(cur_itv)
            if interval[1] > cur_itv[1]:
                interval = (cur_itv[1], interval[1], interval[2])
            else:
                passed = True
        self.interval_sorted = new_sorted

    def get_new_coverage_all(self, interval_list: List[Tuple[int, int, float]]):
        coverage_ratio = 0.0
        for i in interval_list:
            cr = self.get_new_coverage(i, do_insert_after=True)
            coverage_ratio = coverage_ratio + cr
        return coverage_ratio

    def get_new_coverage(self, interval: Tuple[int, int, float], do_insert_after=False):
        interval_copy = interval + tuple()
        interval_length = interval[1] - interval[0]
        coverage_int = interval_length
        cover_info_list = []
        for i in range(len(self.interval_sorted)):
            itvi = self.interval_sorted[i]
            itv_st = itvi[0]
            itv_ed = itvi[1]
            if itv_st > interval[0] and itv_ed < interval[1]:
                cover_info_list.append({
                    "prev_idx": i,
                    "prev_interval": itvi,
                    "recover_interval": (itv_st, itv_ed, itvi[2] * interval[2]),
                    "coverage_int": itv_ed - itv_st,
                    "cover_prob": itvi[2] * (1 - interval[2])
                })
                coverage_int -= itv_ed - itv_st
                interval = (itv_ed, interval[1], interval[2])
                continue
            if itv_st <= interval[0] < itv_ed:
                for j in range(i, len(self.interval_sorted)):
                    itvj = self.interval_sorted[j]
                    if itvj[0] >= interval[1]:
                        break
                    cover_info_list.append({
                        "prev_idx": j,
                        "prev_interval": itvj,
                        "recover_interval": (
                        max(itvj[0], interval[0]), min(itvj[1], interval[1]), itvj[2] * interval[2]),
                        "coverage_int": min(itvj[1], interval[1]) - max(itvj[0], interval[0]),
                        "cover_prob": itvj[2] * (1 - interval[2])
                    })
                    coverage_int -= min(itvj[1], interval[1]) - max(itvj[0], interval[0])
                break
            if itv_st < interval[1] <= itv_ed:
                for j in range(i, -1, -1):
                    itvj = self.interval_sorted[j]
                    if itvj[1] <= interval[0]:
                        break
                    cover_info_list.append({
                        "prev_idx": j,
                        "prev_interval": itvj,
                        "recover_interval": (
                        max(itvj[0], interval[0]), min(itvj[1], interval[1]), itvj[2] * interval[2]),
                        "coverage_int": min(itvj[1], interval[1]) - max(itvj[0], interval[0]),
                        "cover_prob": itvj[2] * (1 - interval[2])
                    })
                    coverage_int -= min(itvj[1], interval[1]) - max(itvj[0], interval[0])
                break
        if do_insert_after:
            self.remove([cinfo["prev_idx"] for cinfo in cover_info_list])
            for cinfo in cover_info_list:
                self.insert(cinfo["recover_interval"])
            for cinfo in cover_info_list:
                self.insert(cinfo["prev_interval"])
            self.insert(interval_copy)
        coverage_ratio = (sum(
            [cinfo["coverage_int"] * cinfo["cover_prob"] for cinfo in cover_info_list]) + coverage_int * (
                                      1 - interval[2])) / self.length
        self.coverage += coverage_ratio
        return coverage_ratio

    def remove(self, indexes: List[int]):
        for index in sorted(indexes, reverse=True):
            del self.interval_sorted[index]

    def get_remain(self):
        return 1 - self.coverage


if __name__ == '__main__':
    itv = ProbabilityIntervals((0, 100))
    # itv_list = [(1, 11, 0.5), (12, 22, 0.5), (31, 41, 0.5), (25, 32, 0.5), (70, 75, 0.5), (79, 84, 0.5), (75, 79, 0.5),(75, 79, 0.5)]
    itv_list = [(5, 10, 0.3), (15, 20, 0.3), (20, 25, 0.3), (12, 27, 0.3), (20, 90, 0.3), (20, 90, 0.3)]
    for it in itv_list:
        print(f"IT: {it}")
        print(itv.get_new_coverage(it, do_insert_after=True))
        print(itv.interval_sorted)
        print(itv.get_remain())


    # itv = Intervals((0, 3474))
    # itv_list = [(0, 1), (1256, 3474), (639, 2858), (22, 2241), (0, 1624), (2879, 3474)]
    # for it in itv_list:
    #     print(f"interval: {it}")
    #     print(itv.get_new_coverage(it, do_insert_after=True))
    #     print(itv.get_remain())
