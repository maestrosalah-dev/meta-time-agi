import random
from metatime.core.clock import RelationalClock, ClockConfig, TemporalState

def label(state: TemporalState) -> str:
    return {
        TemporalState.LIVING: "🌱 LIVING",
        TemporalState.STAGNANT: "💤 STAGNANT",
        TemporalState.AWAKENING: "🔥 AWAKENING",
    }[state]

def bar(x: float, scale: float = 80.0, max_len: int = 60) -> str:
    n = int(min(max_len, max(0, x * scale)))
    return "█" * n

def main():
    print("\n--- SENSOR META-TIME DEMO (Weighted-Delta Stable) ---")
    print("Goal: time flows when prediction error shifts meaningfully.\n")

    cfg = ClockConfig(
        base_threshold=0.005,
        awakening_multiplier=8.0,
        living_multiplier=1.0,
        awakening_age_gain=2.0,
        use_weighted_delta=True,
    )
    clock = RelationalClock(cfg)

    pred = 0.0

    for k in range(1, 201):
        # A toy observation stream with regime shifts
        if k == 31:
            obs = -0.30 + random.uniform(-0.02, 0.02)
        elif k == 71:
            obs = 1.75 + random.uniform(-0.05, 0.05)
        elif k == 111:
            obs = 1.55 + random.uniform(-0.05, 0.05)
        elif k == 146:
            obs = 4.65 + random.uniform(-0.10, 0.10)
        else:
            obs = (pred + random.uniform(-0.12, 0.12))

        # simple predictor update
        err = abs(obs - pred)
        pred = obs

        state = clock.tick(err)

        print(
            f"{k:03d} | obs={obs:+.3f} pred={pred:+.3f} err={err:.3f} | "
            f"{label(state):<12} | age={clock.relational_age:.3f} dens={clock.density:.3f} | "
            f"| {bar(clock.relational_age)}"
        )

    print("\n--- FINAL ---")
    print(f"Steps: {clock.step_counter}")
    print(f"Relational Age: {clock.relational_age:.6f}")
    print(f"Time Density  : {clock.density():.6f}")

if __name__ == "__main__":
    main()

