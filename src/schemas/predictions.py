from dataclasses import dataclass
import numpy as np

@dataclass(frozen = True, slots = True)
class AnomalyPredictions:
    center: np.ndarray
    upper_bound: np.ndarray