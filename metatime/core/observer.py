from __future__ import annotations
from dataclasses import dataclass
from .clock import TemporalState

@dataclass
class PlasticityConfig:
    base_lr: float = 0.02
    stagnant_factor: float = 0.10     # تعلم بطيء جدًا
    living_factor: float = 1.00       # طبيعي
    awakening_factor: float = 2.00    # دفعة
    quarantine_factor: float = 0.02   # شبه إيقاف عند الفوضى
    awakening_bonus_step: bool = True # خطوة إضافية صغيرة عند الاستيقاظ

class MetaObserver:
    """
    يترجم TemporalState إلى سياسة تعلم (plasticity policy).
    """
    def __init__(self, config: PlasticityConfig | None = None):
        self.cfg = config or PlasticityConfig()

    def lr_for_state(self, state: TemporalState) -> float:
        if state == TemporalState.STAGNANT:
            return self.cfg.base_lr * self.cfg.stagnant_factor
        if state == TemporalState.AWAKENING:
            return self.cfg.base_lr * self.cfg.awakening_factor
        if state == TemporalState.QUARANTINE:
            return self.cfg.base_lr * self.cfg.quarantine_factor
        return self.cfg.base_lr * self.cfg.living_factor  # LIVING

    def should_bonus_step(self, state: TemporalState) -> bool:
        return bool(self.cfg.awakening_bonus_step and state == TemporalState.AWAKENING)

    @staticmethod
    def set_optimizer_lr(optimizer, lr: float) -> None:
        for g in optimizer.param_groups:
            g["lr"] = float(lr)

