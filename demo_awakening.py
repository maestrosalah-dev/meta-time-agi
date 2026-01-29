import random
from metatime.core.clock import RelationalClock, ClockConfig

def main():
    print("\n--- META-TIME DEMO (Fixed): Lived Time vs Physical Steps ---\n")

    clock = RelationalClock(ClockConfig(
        base_threshold=0.005,
        awakening_multiplier=8.0,
        living_multiplier=1.0,
        awakening_age_gain=2.0,
        use_weighted_delta=True,
        epsilon=1e-12,
    ))

    # stable -> shift -> stable
    losses = []
    for _ in range(80):
        losses.append(max(0.03, 0.8 * random.random()))
    losses.append(10.0)
    for _ in range(79):
        losses.append(1.7 + 0.6 * random.random())

    for i, loss in enumerate(losses, 1):
        state = clock.observe(loss)
        print(f"Ep {i:3d} | Loss: {loss:7.4f} | Age: {clock.age:6.2f} | {state}")

    print("\n--- FINAL ---")
    print("Total Physical Steps:", len(losses))
    print("Final Cognitive Age :", f"{clock.age:.2f}")

if __name__ == "__main__":
    main()
