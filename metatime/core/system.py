from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .clock import RelationalClock, ClockConfig, TemporalState


@dataclass
class MetaTimeSystem:
    """
    Minimal system wrapper:
    - Holds a relational clock
    - Exposes observe()/tick() bridge for demos
    """
    clock_cfg: ClockConfig = field(default_factory=ClockConfig)
    clock: RelationalClock = field(init=False)

    def __post_init__(self) -> None:
        self.clock = RelationalClock(self.clock_cfg)

    def tick(self, loss_value: float) -> TemporalState:
        return self.clock.tick(loss_value)

    def observe(self, loss_value: float) -> TemporalState:
        # backward compatible alias (old demos used observe)
        return self.tick(loss_value)


def awaken(
    base_model: Optional[Any] = None,
    clock_cfg: Optional[ClockConfig] = None,
) -> MetaTimeSystem:
    """
    Factory used by metatime/__init__.py.
    base_model is kept for compatibility (can be used later),
    but the minimal demos don't require it.
    """
    cfg = clock_cfg if clock_cfg is not None else ClockConfig()
    return MetaTimeSystem(clock_cfg=cfg)
