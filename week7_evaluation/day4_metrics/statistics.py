import math
from typing import List

def calculate_mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)

def calculate_variance(values: List[float], mean: float) -> float:
    if len(values) < 2:
        return 0.0
    return sum((x - mean) ** 2 for x in values) / (len(values) - 1)

def calculate_std_dev(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = calculate_mean(values)
    return math.sqrt(calculate_variance(values, mean))

def calculate_percentile(values: List[float], percentile: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * percentile
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    d0 = sorted_vals[int(f)] * (c - k)
    d1 = sorted_vals[int(c)] * (k - f)
    return d0 + d1
