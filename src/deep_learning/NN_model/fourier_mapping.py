# Created by danctorres

import numpy as np
import math


def mapping(agg: np.ndarray, size_map: int) -> np.ndarray:
    mapping_matrix = np.zeros((1, size_map * 2))
    for i in range(0, size_map):
        mapping_matrix[0, i * 2] = math.sin((i + 1) * agg)
        mapping_matrix[0, i * 2 + 1] = math.sin((i + 1) * agg)
    return mapping_matrix
