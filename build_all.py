# build_all.py
# Meta-Time AGI :: Builder (v0.1.2)
# Generates a clean, consistent project layout + stable Weighted-Delta clock demo.

from __future__ import annotations
import os
from pathlib import Path

VERSION = "0.1.2"

ROOT = Path(".").resolve()
PKG = ROOT / "metatime"
CORE = PKG / "core"

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"✅ wrote: {path.relative_to(ROOT)}")

def main() -> None:
    # ----------------------------------------------------------------------------------
    # 1) Package init
    # ----------------------------------------------------------------------------------
    init_py = f'''"""
Meta-Time: Relational time + plasticity gating primitives.

Version: {VERSION}
"""
from .core.system import awaken, MetaTimeSystem  # noqa: F401

__all__ = ["awaken", "MetaTimeSystem"]
__version__ = "{VERSION}"
'''
    write(PKG / "__init__.py", init_py)

    # ----------------------------------------------------------------------------------
    # 2) Core clock (Weighted-Delta stable)
    # ----------------------------------------------------------------------------------
    clock_py = r'''from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import math

class TemporalState(Enum):
    LIVING = "LIVING"
    STAGNANT = "STAGNANT"
    AWAKENING = "AWAKENING"

@dataclass
class ClockConfig:
    # Base sensitivity (smaller => more sensitive)
    base_threshold: float = 0.001

    # How strongly big shifts (paradigm) are amplified
    awakening_factor: float = 2.0

    # Dynamic threshold grows with age (maturation)
    aging_gain: float = 1.0

    # "Massive shift" multiplier relative to threshold
    massive_mult: float = 5.0

    # Optional clamp to avoid runaway from extreme spikes
    max_delta: float | None = None

class RelationalClock:
    """
    Relational clock driven by *meaningful change* in prediction error.

    Key ideas:
    - We track error e_t.
    - We compute delta = |e_t - e_{t-1}|.
    - We apply a *weighted delta*:
        weighted = delta * (1 + min(e_t, e_{t-1}))
      This makes changes at higher error regimes "count more" (paradigm pressure),
      but still stays stable because it's linear and can be clamped.

    - Threshold increases with log(1+age): maturation => less reactive with age.
    """

    def __init__(self, config: ClockConfig | None = None):
        self.config = config or ClockConfig()
        self.relational_age: float = 0.0
        self.step_counter: int = 0
        self.prev_error: float | None = None

        # density = age / steps (useful for diagnostics)
        self.density: float = 0.0

    def get_dynamic_threshold(self) -> float:
        # Aging law (logarithmic maturation)
        return self.config.base_threshold * (1.0 + self.config.aging_gain * math.log1p(self.relational_age))

    def tick(self, error_value: float) -> TemporalState:
        self.step_counter += 1

        # First step: initialize and consider "alive"
        if self.prev_error is None:
            self.prev_error = float(abs(error_value))
            self._update_density()
            return TemporalState.LIVING

        e_prev = float(abs(self.prev_error))
        e_curr = float(abs(error_value))

        delta = abs(e_curr - e_prev)

        # Weighted delta (stable, interpretable)
        weighted = delta * (1.0 + min(e_curr, e_prev))

        if self.config.max_delta is not None:
            weighted = min(weighted, float(self.config.max_delta))

        th = self.get_dynamic_threshold()

        state = TemporalState.STAGNANT

        if weighted > th * self.config.massive_mult:
            state = TemporalState.AWAKENING
            self.relational_age += weighted * self.config.awakening_factor
        elif weighted > th:
            state = TemporalState.LIVING
            self.relational_age += weighted

        self.prev_error = e_curr
        self._update_density()
        return state

    def _update_density(self) -> None:
        if self.step_counter > 0:
            self.density = self.relational_age / float(self.step_counter)
'''
    write(CORE / "clock.py", clock_py)

    # ----------------------------------------------------------------------------------
    # 3) Core system wrapper
    # ----------------------------------------------------------------------------------
    system_py = r'''from __future__ import annotations
import torch
import torch.nn as nn
from .clock import RelationalClock, ClockConfig, TemporalState

class MetaTimeSystem(nn.Module):
    """
    Wraps any torch model and exposes:
    - observe(loss or error) -> TemporalState
    - age, density
    """

    def __init__(self, base_model: nn.Module, clock: RelationalClock | None = None):
        super().__init__()
        self.base_model = base_model
        self.clock = clock or RelationalClock(ClockConfig())

    def forward(self, x):
        return self.base_model(x)

    def observe(self, error_or_loss):
        if isinstance(error_or_loss, torch.Tensor):
            v = float(error_or_loss.detach().item())
        else:
            v = float(error_or_loss)
        return self.clock.tick(v)

    @property
    def age(self) -> float:
        return float(self.clock.relational_age)

    @property
    def density(self) -> float:
        return float(self.clock.density)

def awaken(model: nn.Module) -> MetaTimeSystem:
    return MetaTimeSystem(model)
'''
    write(CORE / "system.py", system_py)

    # ----------------------------------------------------------------------------------
    # 4) Demo: sensor meta-time
    # ----------------------------------------------------------------------------------
    demo_sensor = r'''from __future__ import annotations
import random
import math
from metatime.core.clock import RelationalClock, ClockConfig, TemporalState

def bar(x: float, width: int = 60) -> str:
    n = int(min(width, max(0.0, x * 10.0)))
    return "█" * n

def main():
    print("\n--- SENSOR META-TIME DEMO (Weighted-Delta Stable) ---")
    print("Goal: time flows when prediction error shifts meaningfully.\n")

    cfg = ClockConfig(
        base_threshold=0.001,
        awakening_factor=2.0,
        aging_gain=1.0,
        massive_mult=5.0,
        max_delta=None,  # you can set e.g. 2.0 to clamp extreme spikes
    )
    clock = RelationalClock(cfg)

    # Simple synthetic sensor stream: drifting mean + two shock events
    mu = 0.0
    obs = 0.0

    for t in range(1, 201):
        # smooth drift
        mu += random.uniform(-0.02, 0.02)
        obs = random.gauss(mu, 0.08)

        # shocks (paradigm shifts)
        if t == 71:
            mu += 2.6
        if t == 146:
            mu += 2.9

        # a naive predictor: predicts previous observation
        pred = obs  # (kept as identity to match your current style: err ~ |obs|)
        err = abs(obs - 0.0)  # error vs "baseline world"

        state = clock.tick(err)

        icon = {"LIVING":"🌱", "STAGNANT":"💤", "AWAKENING":"🔥"}[state.value]
        print(f"{t:03d} | obs={obs:+.3f} pred={pred:+.3f} err={err:.3f} | {icon} {state.value:<9} | "
              f"age={clock.relational_age:0.3f} dens={clock.density:0.3f} | | {bar(clock.relational_age)}")

    print("\n--- FINAL ---")
    print(f"Steps: {clock.step_counter}")
    print(f"Relational Age: {clock.relational_age:.6f}")
    print(f"Time Density  : {clock.density:.6f}")

if __name__ == "__main__":
    main()
'''
    write(ROOT / "demo_sensor_time.py", demo_sensor)

    # ----------------------------------------------------------------------------------
    # 5) Setup/requirements (optional but useful)
    # ----------------------------------------------------------------------------------
    setup_py = f'''from setuptools import setup, find_packages

setup(
    name="metatime",
    version="{VERSION}",
    description="Relational Time (Weighted-Delta) and Plasticity Gating primitives",
    author="Athmani Salah",
    packages=find_packages(),
    install_requires=["torch>=1.9.0"],
)
'''
    write(ROOT / "setup.py", setup_py)

    write(ROOT / "requirements.txt", "torch>=1.9.0\n")

    write(ROOT / ".gitignore", "__pycache__/\n*.py[cod]\n.DS_Store\n.venv/\nvenv/\n")

    # ----------------------------------------------------------------------------------
    # 6) README + paper placeholders (so الريبو يكون جاهز)
    # ----------------------------------------------------------------------------------
    readme_md = f'''# ⏳ Meta-Time (metatime) v{VERSION}

**Relational time flows only when prediction error changes meaningfully.**

## Core idea
We use a stable *Weighted-Delta* rule:

- error = |prediction - baseline| (or loss)
- delta = |e_t - e_(t-1)|
- weighted = delta * (1 + min(e_t, e_(t-1)))

States:
- 🌱 LIVING: weighted > threshold
- 💤 STAGNANT: weighted <= threshold
- 🔥 AWAKENING: weighted > massive_mult * threshold

Threshold matures with age:
- threshold = base_threshold * (1 + log(1 + age))

## Run demo
```powershell
python .\demo_sensor_time.py

