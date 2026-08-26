from dataclasses import dataclass
import numpy as np

@dataclass(frozen = True, slots = True)
class AnomalyPredictions:
    is_outlier: np.ndarray
    center: np.ndarray
    upper_bound: np.ndarray