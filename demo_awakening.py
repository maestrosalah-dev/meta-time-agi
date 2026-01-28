import time
import torch
import torch.nn as nn
import torch.optim as optim

import metatime as mt
from metatime.core.clock import TemporalState

def print_status(step, loss, age, density, state):
    bar_len = min(60, int(age * 30))  # scale for visibility
    bar = "█" * bar_len

    icon = "💤"
    color = "\033[90m"  # grey
    if state == TemporalState.LIVING:
        icon, color = "🌱", "\033[92m"
    elif state == TemporalState.AWAKENING:
        icon, color = "🔥", "\033[91m"
    elif state == TemporalState.QUARANTINE:
        icon, color = "🧊", "\033[94m"

    print(f"{color}Step {step:4} | Loss: {loss:8.4f} | Age: {age:7.4f} | Density: {density:7.4f} {icon} {state.value:<10} | {bar}\033[0m")
    time.sleep(0.02)

# --- Model ---
model = nn.Sequential(nn.Linear(10, 20), nn.ReLU(), nn.Linear(20, 1))
agent = mt.awaken(model)  # Meta-Time wrapper

# --- Data (Phase 1: stable world) ---
inputs = torch.randn(128, 10)
targets = torch.randn(128, 1)

optimizer = optim.Adam(agent.parameters(), lr=agent.observer.cfg.base_lr)
criterion = nn.MSELoss()

print("\n--- META-TIME DEMO: Lived Time vs Physical Steps ---\n")

for step in range(1, 201):
    optimizer.zero_grad()
    outputs = agent(inputs)
    loss = criterion(outputs, targets)
    loss.backward()

    # observe -> state
    state = agent.observe(loss)

    # apply plasticity policy
    lr = agent.observer.lr_for_state(state)
    agent.observer.set_optimizer_lr(optimizer, lr)

    optimizer.step()

    # bonus micro-step on awakening
    if agent.observer.should_bonus_step(state):
        optimizer.zero_grad()
        outputs2 = agent(inputs)
        loss2 = criterion(outputs2, targets)
        loss2.backward()
        optimizer.step()

    print_status(step, loss.item(), agent.age, agent.time_density(), state)

    # --- Reality shift ---
    if step == 120:
        print("\n" + "="*72)
        print(">>> REALITY SHIFT: changing target distribution (new world laws) <<<")
        print("="*72 + "\n")
        targets = torch.randn(128, 1) * 5 + 10

print("\n--- FINAL REPORT ---")
print("Physical Steps:", agent.physical_steps)
print("Relational Age:", round(agent.age, 6))
print("Time Density  :", round(agent.time_density(), 6))
print("Awakenings    :", agent.memory.count_state("AWAKENING"))
print("Quarantines   :", agent.memory.count_state("QUARANTINE"))
print("Meta-Time v0.1.0 ✔")
