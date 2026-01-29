from metatime.core.clock import ClockConfig

def main():
    cfg = ClockConfig(
        base_threshold=0.005,
        awakening_multiplier=8.0,
        living_multiplier=1.0,
        awakening_age_gain=2.0,
        use_weighted_delta=True,
        epsilon=1e-12,
    )
    print("ClockConfig OK:", cfg)

if __name__ == "__main__":
    main()
