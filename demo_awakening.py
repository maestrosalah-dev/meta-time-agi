# demo_awakening.py
import random

from metatime.core.clock import RelationalClock, ClockConfig


def main():
    print("\n--- META-TIME DEMO: Lived Time vs Physical Steps ---\n")

    clock = RelationalClock(
        ClockConfig(
            base_threshold=0.005,
            awakening_multiplier=8.0,
            living_multiplier=1.0,
            awakening_age_gain=2.0,
            use_weighted_delta=True,
        )
    )

    # Simulate a stream of losses with a "shock" (distribution shift)
    losses = []
    for i in range(1, 11):
        if i <= 5:
            losses.append(0.20 + random.uniform(-0.02, 0.02))
        else:
            # shock: higher variance / new regime
            losses.append(0.60 + random.uniform(-0.20, 0.20))

    for ep, loss in enumerate(losses, start=1):
        state = clock.tick(loss)
        age = clock.relational_age
        print(f"Ep {ep:3d} | Loss: {loss:7.4f} | Age: {age:.6f} | {state}")

    print("\n--- FINAL ---")
    print("Total Physical Steps:", clock.step_counter)
    print("Final Cognitive Age :", clock.relational_age)


if __name__ == "__main__":
    main()
