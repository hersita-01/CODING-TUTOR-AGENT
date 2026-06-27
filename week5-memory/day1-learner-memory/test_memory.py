# -----------------------------------
# WEEK 5 – MEMORY SUBSYSTEM
# week5-memory/ test_memory.py
#
# Self-contained tests for LearnerProfile and MemoryManager.
# No dependency on Groq, Streamlit, or any Week 2–4 module.
#
# Run with:
#   cd week5-memory
#   python test_memory.py
# -----------------------------------


# ============================================================
# IMPORTS
# ============================================================

import json
import sys
import tempfile
import traceback
from pathlib import Path

# Allow running from any working directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from learner_profile import LearnerProfile, KNOWN_ERROR_TYPES
from memory_manager import MemoryManager


# ============================================================
# MINI TEST HARNESS
# (No unittest dependency — keeps output readable in the terminal)
# ============================================================

_PASSED: list[str] = []
_FAILED: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    """Assert a condition and record the result."""
    if condition:
        _PASSED.append(name)
        print(f"  ✓  {name}")
    else:
        _FAILED.append(name)
        msg = f"  ✗  {name}"
        if detail:
            msg += f"\n       → {detail}"
        print(msg)


def section(title: str) -> None:
    print(f"\n{'─' * 55}")
    print(f"  {title}")
    print(f"{'─' * 55}")


# ============================================================
# TESTS
# ============================================================

def test_create_profile() -> LearnerProfile:
    """1. Create a learner profile and verify its default state."""
    section("1 · Create Learner Profile")

    profile = LearnerProfile(learner_name="Alice")

    check("learner_name is set",       profile.learner_name == "Alice")
    check("concepts_mastered empty",   profile.concepts_mastered == [])
    check("concepts_struggling empty", profile.concepts_struggling == [])
    check("recent_errors empty",       profile.recent_errors == [])
    check("recent_topics empty",       profile.recent_topics == [])
    check("session_history empty",     profile.session_history == [])
    check("created_at is set",         bool(profile.created_at))
    check("updated_at is set",         bool(profile.updated_at))

    return profile


def test_mastered_concepts(profile: LearnerProfile) -> None:
    """2. Mark concepts as mastered and verify deduplication."""
    section("2 · Mastered Concepts")

    profile.mark_mastered("for loops")
    profile.mark_mastered("functions")
    profile.mark_mastered("for loops")    # duplicate — should not appear twice

    check("two unique mastered concepts",
          len(profile.concepts_mastered) == 2,
          str(profile.concepts_mastered))

    check("'for loops' in mastered",   "for loops"  in profile.concepts_mastered)
    check("'functions' in mastered",   "functions"  in profile.concepts_mastered)


def test_struggling_concepts(profile: LearnerProfile) -> None:
    """3. Mark concepts as struggling; verify mastery protection."""
    section("3 · Struggling Concepts")

    profile.mark_struggling("recursion")
    profile.mark_struggling("recursion")   # duplicate

    check("one struggling concept",
          len(profile.concepts_struggling) == 1,
          str(profile.concepts_struggling))

    check("'recursion' in struggling",  "recursion" in profile.concepts_struggling)

    # Mastered concept cannot be demoted to struggling.
    profile.mark_struggling("for loops")
    check("mastered concept not added to struggling",
          "for loops" not in profile.concepts_struggling)

    # Mastering a struggling concept should remove it from struggling.
    profile.mark_mastered("recursion")
    check("mastered concept removed from struggling",
          "recursion" not in profile.concepts_struggling)
    check("recursion now in mastered",
          "recursion" in profile.concepts_mastered)


def test_record_errors(profile: LearnerProfile) -> None:
    """4. Record detected errors; verify structure and topic propagation."""
    section("4 · Record Detected Errors")

    profile.add_error("ValueError",        "invalid literal for int()",    "type casting")
    profile.add_error("ZeroDivisionError", "division by zero",              "arithmetic")
    profile.add_error("NameError",         "name 'x' is not defined",      "variables")

    check("three errors recorded",
          len(profile.recent_errors) == 3,
          str(len(profile.recent_errors)))

    first = profile.recent_errors[0]
    check("error_type stored",    first["error_type"]    == "ValueError")
    check("error_message stored", "invalid literal"       in first["error_message"])
    check("topic stored",         first["topic"]          == "type casting")
    check("recorded_at present",  bool(first.get("recorded_at")))

    # Errors auto-mark the topic as struggling (unless already mastered).
    check("'type casting' in struggling",
          "type casting" in profile.concepts_struggling)
    check("'arithmetic' in struggling",
          "arithmetic"  in profile.concepts_struggling)


def test_record_topics(profile: LearnerProfile) -> None:
    """5. Record studied topics; verify recency ordering."""
    section("5 · Record Studied Topics")

    profile.add_topic("lists")
    profile.add_topic("dictionaries")
    profile.add_topic("lists")   # re-adding should move to end

    check("two unique topics",
          len(profile.recent_topics) == 2,
          str(profile.recent_topics))

    check("'lists' is the most recent topic",
          profile.recent_topics[-1] == "lists",
          str(profile.recent_topics))


def test_save_and_reload(profile: LearnerProfile, storage_dir: Path) -> LearnerProfile:
    """6 & 7. Save to disk, then reload and verify round-trip fidelity."""
    section("6 · Save to Disk")

    mgr  = MemoryManager(storage_dir=storage_dir)
    ok   = mgr.save_profile(profile)
    path = storage_dir / "alice.json"

    check("save_profile returns True",    ok)
    check("JSON file exists on disk",     path.exists())

    if path.exists():
        raw  = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        check("JSON is valid and parseable",  isinstance(data, dict))
        check("learner_name in JSON",         data.get("learner_name") == "Alice")

    section("7 · Reload from Disk")

    reloaded = mgr.load_profile("Alice")

    check("load_profile returns a LearnerProfile", isinstance(reloaded, LearnerProfile))

    if reloaded is not None:
        check("learner_name survives round-trip",
              reloaded.learner_name == profile.learner_name)
        check("concepts_mastered survives round-trip",
              set(reloaded.concepts_mastered) == set(profile.concepts_mastered),
              str(reloaded.concepts_mastered))
        check("concepts_struggling survives round-trip",
              set(reloaded.concepts_struggling) == set(profile.concepts_struggling))
        check("recent_errors count survives round-trip",
              len(reloaded.recent_errors) == len(profile.recent_errors))
        check("recent_topics count survives round-trip",
              len(reloaded.recent_topics) == len(profile.recent_topics))

    return reloaded or profile


def test_get_or_create(storage_dir: Path) -> None:
    """Extra: get_or_create is idempotent across calls."""
    section("Extra · get_or_create Idempotency")

    mgr = MemoryManager(storage_dir=storage_dir)

    p1 = mgr.get_or_create("Bob")
    p2 = mgr.get_or_create("Bob")   # should return existing, not overwrite

    check("get_or_create returns a profile",       isinstance(p1, LearnerProfile))
    check("second call returns same learner_name", p1.learner_name == p2.learner_name)
    check("second call keeps created_at intact",   p1.created_at   == p2.created_at)


def test_corrupted_json(storage_dir: Path) -> None:
    """Extra: corrupted JSON is handled without crashing."""
    section("Extra · Corrupted JSON Handling")

    bad_path = storage_dir / "corrupt_student.json"
    bad_path.write_text("{ this is not valid json !!!}", encoding="utf-8")

    mgr    = MemoryManager(storage_dir=storage_dir)
    result = mgr.load_profile("corrupt_student")

    check("load returns None for corrupted JSON", result is None)
    check("backup file created",
          bad_path.with_suffix(".json.bak").exists())


def test_update_from_run_result(storage_dir: Path) -> None:
    """Extra: update_from_run_result covers both success and failure paths."""
    section("Extra · update_from_run_result")

    mgr     = MemoryManager(storage_dir=storage_dir)
    profile = mgr.get_or_create("Charlie")

    # Simulate a failed run
    mgr.update_from_run_result(
        profile,
        error_type = "TypeError",
        error_msg  = "unsupported operand type",
        topic      = "operators",
        success    = False,
    )
    check("error recorded on failure",
          any(e["error_type"] == "TypeError" for e in profile.recent_errors))
    check("topic recorded on failure",
          "operators" in profile.recent_topics)

    # Simulate a successful run
    pre_error_count = len(profile.recent_errors)
    mgr.update_from_run_result(
        profile,
        error_type = "",
        error_msg  = "",
        topic      = "string methods",
        success    = True,
    )
    check("no new error on success",
          len(profile.recent_errors) == pre_error_count)
    check("topic recorded on success",
          "string methods" in profile.recent_topics)


def test_print_summary(profile: LearnerProfile) -> None:
    """8. Print and validate learner summary output."""
    section("8 · Learner Summary")

    summary = profile.get_summary()
    print()
    for line in summary.splitlines():
        print(f"    {line}")
    print()

    check("summary contains learner name",  "Alice"         in summary)
    check("summary contains mastered",      "Mastered"      in summary)
    check("summary contains struggling",    "Struggling"    in summary)
    check("summary contains recent topics", "Recent topics" in summary)
    check("summary contains error history", "Error history" in summary)


# ============================================================
# MAIN — run all tests in a temporary storage directory
# ============================================================

def main() -> None:
    print()
    print("=" * 55)
    print("  WEEK 5 — LEARNER MEMORY SYSTEM  ·  Test Suite")
    print("=" * 55)

    with tempfile.TemporaryDirectory() as tmp:
        storage_dir = Path(tmp)

        try:
            # Run tests in dependency order — each builds on the last.
            profile = test_create_profile()
            test_mastered_concepts(profile)
            test_struggling_concepts(profile)
            test_record_errors(profile)
            test_record_topics(profile)
            profile = test_save_and_reload(profile, storage_dir)
            test_get_or_create(storage_dir)
            test_corrupted_json(storage_dir)
            test_update_from_run_result(storage_dir)
            test_print_summary(profile)

        except Exception:
            print("\n[FATAL] Unexpected exception during tests:")
            traceback.print_exc()

    # ── Summary ─────────────────────────────────────────────
    total  = len(_PASSED) + len(_FAILED)
    passed = len(_PASSED)
    failed = len(_FAILED)

    print()
    print("=" * 55)
    print(f"  Results:  {passed}/{total} passed", end="")
    if failed:
        print(f"  ·  {failed} FAILED")
        for name in _FAILED:
            print(f"    ✗  {name}")
    else:
        print("  ·  All passed ✓")
    print("=" * 55)
    print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()