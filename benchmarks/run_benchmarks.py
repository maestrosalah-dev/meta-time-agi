import torch
import torch.nn as nn
import torch.optim as optim

import metatime as mt
from metatime.core.clock import TemporalState

def run_case(case_name: str, steps: int = 200, shift_at: int | None = None, noise_at: tuple[int,int] | None = None):
    model = nn.Sequential(nn.Linear(10, 20), nn.ReLU(), nn.Linear(20, 1))
    agent = mt.awaken(model)
    optimizer = optim.Adam(agent.parameters(), lr=agent.observer.cfg.base_lr)
    criterion = nn.MSELoss()

    inputs = torch.randn(128, 10)
    targets = torch.randn(128, 1)

    for step in range(1, steps + 1):
        # inject shift
        if shift_at is not None and step == shift_at:
            targets = torch.randn(128, 1) * 5 + 10

        # inject noise window
        if noise_at is not None:
            a, b = noise_at
            if a <= step <= b:
                targets = torch.randn(128, 1) * 50 + 200  # very noisy / chaotic

        optimizer.zero_grad()
        outputs = agent(inputs)
        loss = criterion(outputs, targets)
        loss.backward()

        state = agent.observe(loss)

        lr = agent.observer.lr_for_state(state)
        agent.observer.set_optimizer_lr(optimizer, lr)
        optimizer.step()

        if agent.observer.should_bonus_step(state):
            optimizer.zero_grad()
            out2 = agent(inputs)
            loss2 = criterion(out2, targets)
            loss2.backward()
            optimizer.step()

    return {
        "Case": case_name,
        "Steps": agent.physical_steps,
        "Age": round(agent.age, 6),
        "Density": round(agent.time_density(), 6),
        "Awakenings": agent.memory.count_state("AWAKENING"),
        "Quarantines": agent.memory.count_state("QUARANTINE"),
    }

def main():
    results = []
    results.append(run_case("A: Stagnation (repeat)", steps=200, shift_at=None, noise_at=None))
    results.append(run_case("B: Shift (reality change)", steps=200, shift_at=120, noise_at=None))
    results.append(run_case("C: Noise window", steps=200, shift_at=None, noise_at=(90, 120)))

    # Print table
    headers = ["Case","Steps","Age","Density","Awakenings","Quarantines"]
    print("\n" + "-"*88)
    print("{:<26} {:>6} {:>10} {:>10} {:>11} {:>12}".format(*headers))
    print("-"*88)
    for r in results:
        print("{:<26} {:>6} {:>10} {:>10} {:>11} {:>12}".format(
            r["Case"], r["Steps"], r["Age"], r["Density"], r["Awakenings"], r["Quarantines"]
        ))
    print("-"*88 + "\n")

if __name__ == "__main__":
    main()
