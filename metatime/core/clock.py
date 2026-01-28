import numpy as np
from enum import Enum
from dataclasses import dataclass


class TemporalState(Enum):
    LIVING = "LIVING"
    STAGNANT = "STAGNANT"
    AWAKENING = "AWAKENING"


@dataclass
class ClockConfig:
    base_threshold: float = 0.005
    awakening_multiplier: float = 8.0   # delta > threshold * awakening_multiplier
    living_multiplier: float = 1.0      # delta > threshold * living_multiplier
    awakening_age_gain: float = 2.0     # age += delta * awakening_age_gain in awakening
    use_weighted_delta: bool = True     # important fix
    epsilon: float = 1e-12              # numerical safety


class RelationalClock:
    """
    Relational time accumulates only when coherence shifts meaningfully.
    Coherence uses Inverse-Loss for stability:
        C = 1 / (1 + loss)
    Key fix:
        delta := |C - C_prev| * C   (weighted by current coherence)
    This prevents 'always-awake' behavior when loss jitters.
    """

    def __init__(self, config: ClockConfig | None = None):
        self.cfg = config or ClockConfig()
        self.relational_age = 0.0
        self.prev_coherence = None
        self.step_counter = 0

    def get_dynamic_threshold(self) -> float:
        # Aging Law: threshold grows logarithmically with age (maturation)
        # Keep it strictly positive.
        return max(self.cfg.epsilon, self.cfg.base_threshold * (1.0 + np.log1p(max(0.0, self.relational_age))))

    def coherence(self, loss_value: float) -> float:
        # Inverse-loss coherence in (0,1]
        loss_value = float(loss_value)
        if loss_value < 0:
            # If some caller passes negative loss (rare), clamp to 0 for coherence meaning.
            loss_value = 0.0
        return 1.0 / (1.0 + loss_value)

    def tick(self, loss_value: float) -> TemporalState:
        self.step_counter += 1

        c = self.coherence(loss_value)

        if self.prev_coherence is None:
            self.prev_coherence = c
            return TemporalState.LIVING

        raw_delta = abs(c - self.prev_coherence)

        # ✅ KEY FIX: weight delta by current coherence so chaos doesn't create fake "time"
        if self.cfg.use_weighted_delta:
            delta = raw_delta * max(self.cfg.epsilon, c)
        else:
            delta = raw_delta

        threshold = self.get_dynamic_threshold()

        state = TemporalState.STAGNANT

        if delta > threshold * self.cfg.awakening_multiplier:
            state = TemporalState.AWAKENING
            self.relational_age += delta * self.cfg.awakening_age_gain
        elif delta > threshold * self.cfg.living_multiplier:
            state = TemporalState.LIVING
            self.relational_age += delta

        self.prev_coherence = c
        return state

    def density(self) -> float:
        # Safer density (prevents huge values at the first few steps)
        return self.relational_age / max(5, self.step_counter)



