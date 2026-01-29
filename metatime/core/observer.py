# metatime/core/observer.py
from __future__ import annotations
from dataclasses import dataclass

from .clock import TemporalState


@dataclass
class ObserverConfig:
    """
    Observer: controls adaptation behavior (e.g., LR schedule) based on temporal state.
    We keep it because it's a core concept: the observer is the entity that *experiences* time.
    """
    base_lr: float = 1e-3
    lr_awakening_mult: float = 3.0
    lr_stagnant_mult: float = 0.25


class RelationalObserver:
    def __init__(self, cfg: ObserverConfig = ObserverConfig()):
        self.cfg = cfg

    def lr_for_state(self, state: TemporalState) -> float:
        if state == TemporalState.AWAKENING:
            return self.cfg.base_lr * self.cfg.lr_awakening_mult
        if state == TemporalState.STAGNANT:
            return self.cfg.base_lr * self.cfg.lr_stagnant_mult
        return self.cfg.base_lr

