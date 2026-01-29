# Meta-Time AGI (Relational & Meta-Time)

Meta-Time is a research prototype where **time emerges from meaningful prediction-error change**.
Instead of assuming uniform physical time, we define **relational time** that flows under novelty, learning pressure, or distribution shifts.

This repo contains:
- a minimal Meta-Time core (`metatime/`)
- demos (sensor stream, calibrated “awakening”, text stream)
- a PDF paper (see `paper/relational_time.pdf`)
- (v2) an extended clock with **meta-time, density, and curvature**

---

## Install

```bash
pip install -r requirements.txt

Quickstart
v1 demos
python demo_sensor_time.py
python demo_awakening.py
python demo_text_time.py

v2 demo (TR + TM + density + curvature)
python demo_clock_v2.py

Concept
Let loss be loss_k. Define coherence:
C_k = 1 / (1 + loss_k)
ΔC_k = |C_k - C_{k-1}|
Relational time flows only when:
ΔC_k > threshold
We define:
T_R : relational time (accumulated meaningful coherence shifts)
T_M : meta-time (dT_R)
ρ_T : time density (T_R / steps)
κ_T : time curvature (dT_M)
