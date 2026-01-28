from __future__ import annotations
from dataclasses import dataclass
import math
import random

@dataclass
class SensorConfig:
    noise_std: float = 0.05
    shift_at: int = 120
    shift_magnitude: float = 1.8

class SimpleSensorWorld:
    """
    قراءة حساس 1D: موجة جيبية + ضجيج.
    ثم يحدث Reality Shift بتغيير القانون عند shift_at.
    """
    def __init__(self, cfg: SensorConfig | None = None, seed: int = 42):
        self.cfg = cfg or SensorConfig()
        random.seed(seed)

    def read(self, t: int) -> float:
        base = math.sin(t * 0.1)
        if t >= self.cfg.shift_at:
            base = base * self.cfg.shift_magnitude + 0.8
        return base + random.gauss(0.0, self.cfg.noise_std)

class EWMA_Predictor:
    """
    متنبئ بسيط: متوسط أسي متحرك.
    """
    def __init__(self, alpha: float = 0.15):
        self.alpha = alpha
        self.mu = None

    def predict(self) -> float:
        return 0.0 if self.mu is None else self.mu

    def update(self, x: float) -> None:
        if self.mu is None:
            self.mu = x
        else:
            self.mu = (1 - self.alpha) * self.mu + self.alpha * x

def prediction_error(pred: float, obs: float) -> float:
    return abs(obs - pred)
