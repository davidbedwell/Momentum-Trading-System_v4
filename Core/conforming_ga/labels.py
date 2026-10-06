"""Forward discovery labels are deliberately isolated from live features."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
@dataclass
class LabelStore:
    values:np.ndarray
    def nan_copy(self):return LabelStore(np.full_like(self.values,np.nan,dtype=float))
