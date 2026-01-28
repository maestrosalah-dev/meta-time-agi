
# doctor_imports.py
from __future__ import annotations

import os
import sys
import site
import importlib
from pathlib import Path


def banner(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def show_paths() -> None:
    banner("PYTHON ENV")
    print("Python exe :", sys.executable)
    print("Version    :", sys.version.replace("\n", " "))
    print("CWD        :", os.getcwd())

    banner("SITE-PACKAGES")
    try:
        print("site.getsitepackages():")
        for p in site.getsitepackages():
            print(" -", p)
    except Exception as e:
        print("site.getsitepackages() failed:", e)

    print("\nsite.getusersitepackages():")
    try:
        print(" -", site.getusersitepackages())
    except Exception as e:
        print("failed:", e)

    banner("sys.path (top 25)")
    for i, p in enumerate(sys.path[:25]):
        print(f"{i:02} - {p}")


def locate(name: str) -> None:
    banner(f"LOCATE MODULE: {name}")
    try:
        spec = importlib.util.find_spec(name)
        if spec is None:
            print("NOT FOUND.")
            return
        print("spec.origin:", spec.origin)
        if spec.submodule_search_locations:
            print("package dirs:")
            for d in spec.submodule_search_locations:
                print(" -", d)
    except Exception as e:
        print("find_spec failed:", e)


def find_duplicates(package_dir_name: str = "metatime") -> None:
    banner("DUPLICATE PACKAGE CHECK")
    hits: list[str] = []
    for p in sys.path:
        try:
            cand = Path(p) / package_dir_name
            if cand.exists() and cand.is_dir():
                hits.append(str(cand.resolve()))
        except Exception:
            pass

    if not hits:
        print("No package directories found on sys.path (unexpected).")
        return

    print(f"Found {len(hits)} candidate '{package_dir_name}' dirs:")
    for h in hits:
        print(" -", h)

    if len(hits) > 1:
        print("\nWARNING: multiple candidates can cause import confusion.")
        print("If you want only the project one, ensure CWD is first on sys.path and")
        print("avoid installing another metatime in site-packages with same name.")


def check_metatime() -> None:
    banner("IMPORT CHECK: metatime.core.clock")

    try:
        clock_mod = importlib.import_module("metatime.core.clock")
    except Exception as e:
        print("IMPORT FAILED:", repr(e))
        return

    clock_file = getattr(clock_mod, "__file__", None)
    print("clock.__file__:", clock_file)

    RelationalClock = getattr(clock_mod, "RelationalClock", None)
    ClockConfig = getattr(clock_mod, "ClockConfig", None)
    TemporalState = getattr(clock_mod, "TemporalState", None)

    print("RelationalClock:", "OK" if RelationalClock else "MISSING")
    print("ClockConfig    :", "OK" if ClockConfig else "MISSING")
    print("TemporalState  :", "OK" if TemporalState else "MISSING")

    # إذا الكلاسات ناقصة لا نكمل
    if not RelationalClock or not ClockConfig:
        return

    # ------------------------------
    # INSTANCE CHECK (RelationalClock)
    # ------------------------------
    try:
        # حاول إنشاء cfg إن أمكن
        try:
            cfg = ClockConfig()  # إذا لها defaults
        except Exception:
            cfg = None

        # حاول إنشاء clock
        try:
            clock_obj = RelationalClock(cfg) if cfg is not None else RelationalClock()
        except TypeError:
            clock_obj = RelationalClock(ClockConfig())

        has_step_counter = hasattr(clock_obj, "step_counter")
        has_rel_age = hasattr(clock_obj, "relational_age")
        has_density = hasattr(clock_obj, "density")
        has_tick = hasattr(clock_obj, "tick")

        print("\nINSTANCE CHECK: RelationalClock()")
        print(f" - tick          : {'YES' if has_tick else 'NO'}")
        print(f" - density       : {'YES' if has_density else 'NO'}")
        print(f" - relational_age: {'YES' if has_rel_age else 'NO'}")
        print(f" - step_counter  : {'YES' if has_step_counter else 'NO'}")

        if has_step_counter:
            print("   step_counter value:", getattr(clock_obj, "step_counter"))
        if has_rel_age:
            # قد تكون property؛ فقط اعرضها (لا تعدّلها)
            try:
                print("   relational_age value:", getattr(clock_obj, "relational_age"))
            except Exception as e:
                print("   relational_age read failed:", repr(e))

    except Exception as e:
        print("\nINSTANCE CHECK: FAILED")
        print("Reason:", repr(e))


def main() -> None:
    show_paths()
    locate("metatime")
    locate("metatime.core")
    locate("metatime.core.clock")
    find_duplicates("metatime")
    check_metatime()

    banner("DONE")
    print("If demo runs but imports fail sometimes, most likely cache/duplicate package or IDE run-dir.")


if __name__ == "__main__":
    main()
