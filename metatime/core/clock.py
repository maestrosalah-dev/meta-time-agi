# metatime/core/clock.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import math


class TemporalState(str, Enum):
    STAGNANT = "STAGNANT"
    LIVING = "LIVING"
    AWAKENING = "AWAKENING"


@dataclass
class ClockConfig:
    # Threshold base for "meaningful change" (prediction error change)
    base_threshold: float = 0.005

    # Multipliers to convert "meaningful delta" into lived time gain
    awakening_multiplier: float = 8.0
    living_multiplier: float = 1.0

    # Extra boost when awakening happens
    awakening_age_gain: float = 2.0

    # Use weighted delta for smoother behavior
    use_weighted_delta: bool = True

    # Numerical stability
    epsilon: float = 1e-12


@dataclass
class TickResult:
    state: TemporalState
    age: float
    delta: float
    threshold: float
    coherence: float


class RelationalClock:
    """
    RelationalClock:
      - Input: loss_value (prediction error proxy)
      - Output: TemporalState + updates relational_age
      - Principle: time advances when prediction error changes meaningfully.
    """

    def __init__(self, cfg: ClockConfig):
        self.cfg = cfg

        self.step_counter: int = 0
        self.relational_age: float = 0.0

        self._prev_loss: Optional[float] = None
        self._ema_delta: float = 0.0

        # Exposed metrics
        self.coherence: float = 1.0
        self.prev_coherence: float = 1.0
        self.density: float = 0.0

    def get_dynamic_threshold(self) -> float:
        """
        Dynamic threshold = base + small term from running delta (optional).
        Keeps the clock stable if noise is high.
        """
        base = self.cfg.base_threshold
        extra = 0.25 * self._ema_delta  # small adaptivity
        return base + extra

    def tick(self, loss_value: float) -> TemporalState:
        """
        Advance the relational clock one step given a new loss_value.
        Returns the TemporalState.
        """
        self.step_counter += 1

        if self._prev_loss is None:
            self._prev_loss = float(loss_value)
            self.prev_coherence = self.coherence
            self.coherence = 1.0
            self.density = 0.0
            return TemporalState.LIVING

        loss_value = float(loss_value)
        raw_delta = abs(loss_value - self._prev_loss)

        # EMA of delta (for smoothing)
        # alpha is small => stable; bigger => reactive
        alpha = 0.12
        self._ema_delta = (1 - alpha) * self._ema_delta + alpha * raw_delta

        threshold = self.get_dynamic_threshold()

        # coherence is an inverse-ish measure of surprise
        self.prev_coherence = self.coherence
        self.coherence = 1.0 / (1.0 + raw_delta + self.cfg.epsilon)

        # density = "how much time is happening" per step (proxy)
        self.density = raw_delta

        # Determine state
        if raw_delta <= threshold:
            state = TemporalState.STAGNANT
            age_gain = 0.0
        else:
            # Awakening if delta is significantly above threshold
            if raw_delta >= 3.0 * threshold:
                state = TemporalState.AWAKENING
                age_gain = (
                    self.cfg.awakening_age_gain
                    + self.cfg.awakening_multiplier * (raw_delta - threshold)
                )
            else:
                state = TemporalState.LIVING
                age_gain = self.cfg.living_multiplier * (raw_delta - threshold)

        # Weighted delta option (slightly reduces jitter)
        if self.cfg.use_weighted_delta and age_gain > 0.0:
            weight = 1.0 / (1.0 + math.exp(-10.0 * (raw_delta - threshold)))
            age_gain *= weight

        self.relational_age += float(age_gain)
        self._prev_loss = loss_value
        return state

    def tick_result(self, loss_value: float) -> TickResult:
        """
        Convenience function if you want debug info in demos/logs.
        """
        prev_age = self.relational_age
        state = self.tick(loss_value)
        age = self.relational_age
        delta = 0.0 if self._prev_loss is None else abs(float(loss_value) - float(self._prev_loss))
        thr = self.get_dynamic_threshold()
        return TickResult(
            state=state,
            age=age,
            delta=delta,
            threshold=thr,
            coherence=self.coherence,
        )

