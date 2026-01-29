# demo_text_time.py
import random
from metatime.core.clock import RelationalClock, ClockConfig


def main():
    cfg = ClockConfig(
        base_threshold=0.005,
        awakening_multiplier=8.0,
        living_multiplier=1.0,
        awakening_age_gain=2.0,
        use_weighted_delta=True,
    )
    print("ClockConfig OK:", cfg)

    clock = RelationalClock(cfg)

    # Toy "text" loss signal: mostly stable, occasionally surprises
    for ep in range(1, 31):
        if ep % 9 == 0:
            loss = 0.8 + random.uniform(-0.1, 0.1)   # novelty spike
        else:
            loss = 0.25 + random.uniform(-0.02, 0.02)

        state = clock.tick(loss)
        print(f"Ep {ep:3d} | Loss: {loss:7.4f} | Age: {clock.relational_age:.6f} | {state}")

    print("\nFINAL AGE:", clock.relational_age)


if __name__ == "__main__":
    main()
