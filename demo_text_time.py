import time
import re

from metatime.core.clock import RelationalClock, ClockConfig, TemporalState
from metatime.text.ngram_model import NGramLM, NGramConfig


def is_noise(chunk: str) -> bool:
    s = chunk.strip()
    if not s:
        return True

    digits = sum(ch.isdigit() for ch in s)
    letters = sum(ch.isalpha() for ch in s)
    non_alnum = sum((not ch.isalnum()) and (not ch.isspace()) for ch in s)

    # ضجيج حقيقي: رموز/أرقام كثيرة مع حروف قليلة
    ratio_noise = (digits + non_alnum) / max(1, letters + digits + non_alnum)

    # إذا شبه لا توجد حروف -> ضجيج
    if letters < 3 and (digits + non_alnum) > 0:
        return True

    return ratio_noise > 0.35

def print_event(i, loss, ppl, state, age, density, chunk):
    icons = {
        "LIVING": "🌱",
        "STAGNANT": "💤",
        "AWAKENING": "🔥",
        "QUARANTINE": "🧊"
    }
    icon = icons[state.value]
    bar = "█" * min(50, int(age * 25))

    print(
        f"{i:03} | loss={loss:7.4f} | ppl={ppl:7.2f} | "
        f"{icon} {state.value:<10} | age={age:6.3f} | dens={density:6.3f} | {bar}"
    )
    print("    ", chunk[:90].replace("\n", " "), "\n")
    time.sleep(0.02)


def build_stream():
    A = ["العلم نور والعقل دليل والحكمة ميزان. " * 3] * 12

    B = [
        "نعرف الزمن بأنه أثر تغيّر التماسك داخل نظام.",
        "إذا لم يتغير التماسك فلا زمن مستخرج، حتى لو مرت ساعات.",
        "عند ظهور تناقضات أو مفاجآت يتغير التماسك بقوة.",
        "نقيس التماسك عبر القدرة على التنبؤ بالنص القادم.",
        "كلما تحسن التنبؤ زاد المعنى واستقر الزمن.",
        "عندما يحدث تحول مفهومي كبير يحدث استيقاظ."
    ]

    C = [
        "xqz 999 !!! ### qqq wwww zzz",
        "asd asd asd 12345 qwe qwe ###"
    ]

    stream = []
    stream.extend(A)
    stream.extend(B)
    stream.extend(C)
    stream.extend(B)

    return stream


def main():
    physical_chunks = 0

    lm = NGramLM(NGramConfig(n=3, add_k=0.5))

    clock = RelationalClock(
        ClockConfig(
            base_threshold=0.01,
            aging_alpha=0.35,
            awakening_mult=8.0,
            c_min=0.0
        )
    )

    stream = build_stream()

    print("\n--- TEXT META-TIME DEMO ---")
    print("Goal: time advances only when meaning (predictive coherence) shifts.\n")

    for i, chunk in enumerate(stream, start=1):
        physical_chunks += 1
        loss = lm.nll_loss(chunk)
        ppl = lm.perplexity(chunk)

        if is_noise(chunk):
            state = TemporalState.QUARANTINE
        else:
            state, _, _ = clock.tick(loss)

        if state in (TemporalState.LIVING, TemporalState.AWAKENING):
            lm.update(chunk)

        age = clock.relational_age
        density = age / max(1, physical_chunks)

        print_event(i, loss, ppl, state, age, density, chunk)

    print("--- FINAL ---")
    print("Physical Chunks:", physical_chunks)
    print("Relational Age :", round(clock.relational_age, 6))
    print("Time Density   :", round(clock.relational_age / max(1, physical_chunks), 6))


if __name__ == "__main__":
    main()
