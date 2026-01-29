# metatime/core/system.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional

from .clock import RelationalClock, ClockConfig, TemporalState
from .observer import RelationalObserver, ObserverConfig


@dataclass
class SystemConfig:
    clock: ClockConfig = ClockConfig()
    observer: ObserverConfig = ObserverConfig()


class MetaTimeSystem:
    """
    MetaTimeSystem:
      - Wraps: base_model (any object), RelationalClock, RelationalObserver
      - Exposes: observe(loss) -> TemporalState
    """

    def __init__(self, base_model: Any, cfg: Optional[SystemConfig] = None):
        self.base_model = base_model
        self.cfg = cfg or SystemConfig()

        self.clock = RelationalClock(self.cfg.clock)
        self.observer = RelationalObserver(self.cfg.observer)

    def observe(self, loss_value: float) -> TemporalState:
        return self.clock.tick(loss_value)

