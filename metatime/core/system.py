import torch
import torch.nn as nn
from .clock import RelationalClock, ClockConfig, TemporalState


class MetaTimeSystem(nn.Module):
    def __init__(self, base_model: nn.Module, clock: RelationalClock | None = None):
        super().__init__()
        self.base_model = base_model
        self.clock = clock or RelationalClock(ClockConfig())

    def forward(self, x):
        return self.base_model(x)

    def observe(self, loss_value):
        if isinstance(loss_value, torch.Tensor):
            loss_value = loss_value.item()
        return self.clock.tick(float(loss_value))

    @property
    def age(self) -> float:
        return float(self.clock.relational_age)

    @property
    def time_density(self) -> float:
        return float(self.clock.density())


def awaken(model: nn.Module) -> MetaTimeSystem:
    return MetaTimeSystem(model)

