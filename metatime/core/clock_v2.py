from dataclasses import dataclass
from enum import Enum, auto

class TemporalState(Enum):
    AWAKENING = auto()
    LIVING = auto()
    STAGNANT = auto()

@dataclass
class ClockV2Config:
    base_threshold: float = 0.005
    gain: float = 1.0
    epsilon: float = 1e-12

class RelationalClockV2:
    def __init__(self, cfg: ClockV2Config = ClockV2Config()):
        self.cfg = cfg
        self.step_counter = 0
        self.relational_age = 0.0
        self.prev_loss = None

    def tick(self, loss_value: float) -> TemporalState:
        self.step_counter += 1

        if self.prev_loss is None:
            self.prev_loss = float(loss_value)
            return TemporalState.LIVING

        loss_value = float(loss_value)
        delta = abs(loss_value - self.prev_loss)
        self.prev_loss = loss_value

        # age increases when delta exceeds threshold
        if delta > self.cfg.base_threshold:
            self.relational_age += self.cfg.gain * delta
            return TemporalState.AWAKENING

        return TemporalState.STAGNANT
