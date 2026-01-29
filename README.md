# Meta-Time AGI (Relational Time)

**Meta-Time** is a research prototype where **time emerges from meaningful change in prediction error** — a *relational, observer-dependent clock*.

Instead of assuming uniform physical time, Meta-Time defines a **cognitive / relational time** that advances under:
- novelty,
- learning pressure,
- distribution shifts,
- or strong changes in coherence.

This repository includes:
- the core relational clock,
- optional observer scaffolding,
- simple demos (sensor / text / awakening),
- an early v2 clock experiment,
- and the paper PDF.

---

## Concept (1 minute)

We treat “time” as a derived quantity:

> **Time flows when the system’s predictive coherence changes meaningfully.**

- If the model’s error/coherence changes sharply → **time accelerates** (awakening / novelty).
- If the system is stable and predictable → **time slows** or becomes **stagnant**.

This is useful for building agents that measure **experienced time** rather than counting steps.

---

## Repository layout

metatime/
core/
clock.py # RelationalClock (stable API)
observer.py # Optional Observer utilities
system.py # MetaTimeSystem wrapper (if used)
sensors/
text/

paper/
relational_time.pdf # The paper (PDF)

demos/
(demos are at repo root: demo_*.py)

> Note: some demos live in the repository root for simplicity.

---

## Install

### 1) Create an environment (recommended)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

> Note: some demos live in the repository root for simplicity.

---

## Install

### 1) Create an environment (recommended)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
Quickstart demos
Sensor demo (relational time from loss stream)
python demo_sensor_time.py
Awakening demo (time speeds up under novelty)
python demo_awakening.py
Text demo (toy language prediction)
python demo_text_time.py
API (stable)
Paper

The paper is included here:

paper/relational_time.pdf
Citation

If you use this work, please cite:

CITATION.cff
Author
ATHMANI SALAH (ALGERIA 2025)




