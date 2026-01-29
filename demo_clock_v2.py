from metatime.core.clock_v2 import RelationalClockV2, ClockV2Config

def main():
    c = RelationalClockV2(ClockV2Config(base_threshold=0.05, gain=1.0))
    losses = [0.10, 0.12, 0.50, 0.49, 0.51, 0.52, 0.10]
    for i, loss in enumerate(losses, start=1):
        st = c.tick(loss)
        print(f"Ep {i:3d} | Loss: {loss:7.4f} | Age: {c.relational_age:.6f} | {st}")
    print("FINAL AGE:", c.relational_age)

if __name__ == "__main__":
    main()
