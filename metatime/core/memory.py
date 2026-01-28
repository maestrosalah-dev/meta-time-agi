from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from .clock import TemporalState

@dataclass
class TemporalEvent:
    step: int
    loss: float
    coherence: float
    delta_c: float
    state: str

class EpisodicTemporalMemory:
    def __init__(self, max_events: int = 5000):
        self.max_events = max_events
        self.events: List[TemporalEvent] = []

    def record(self, step: int, loss: float, coherence: float, delta_c: float, state: TemporalState) -> None:
        self.events.append(
            TemporalEvent(step=step, loss=float(loss), coherence=float(coherence), delta_c=float(delta_c), state=state.value)
        )
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]

    def count_state(self, state_value: str) -> int:
        return sum(1 for e in self.events if e.state == state_value)
