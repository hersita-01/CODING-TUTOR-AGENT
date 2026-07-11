# -----------------------------------
# WEEK 5 – MEMORY SUBSYSTEM
# week5-memory/ memory_manager.py
#
# MemoryManager is the single interface through which all other
# modules interact with learner profiles on disk.
#
# No other module should open, read, or write JSON profile files
# directly.  All operations go through MemoryManager.
#
# Design principles:
#   • Fail-safe   — corrupted or missing files never crash callers.
#   • Idempotent  — loading a profile that already exists returns
#                   the cached instance; creating one that exists
#                   returns the existing profile unchanged.
#   • Transparent — every disk operation is logged at DEBUG level
#                   so integration problems are easy to trace.
#   • Extensible  — future weeks (embeddings, RAG, multi-agent)
#                   add new methods here without touching callers.
# -----------------------------------


# ============================================================
# IMPORTS
# ============================================================

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from learner_profile import LearnerProfile, _utc_now

log = logging.getLogger("week5.memory_manager")


# ============================================================
# MEMORY MANAGER
# ============================================================

class MemoryManager:
    """Manages loading, saving, creating, and updating learner profiles.

    Parameters
    ----------
    storage_dir:
        Directory where JSON profile files are stored.
        Defaults to a ``memory/`` folder relative to this file's parent.
        Created automatically if it does not exist.

    Example
    -------
    >>> mgr = MemoryManager()
    >>> profile = mgr.get_or_create("alice")
    >>> mgr.record_error(profile, "ValueError", "invalid literal", "type casting")
    >>> mgr.save_profile(profile)
    >>> summary = mgr.get_summary("alice")
    """

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def __init__(self, storage_dir: Optional[Path] = None) -> None:
        if storage_dir is None:
            # Default: <project-root>/memory/
            storage_dir = Path(__file__).resolve().parent.parent / "memory"

        self._storage_dir: Path = Path(storage_dir)
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        log.debug("MemoryManager initialised. Storage: %s", self._storage_dir)

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def _profile_path(self, learner_name: str) -> Path:
        """Return the JSON file path for a given learner name.

        Learner names are normalised to lowercase and spaces replaced
        with underscores so the filename is always filesystem-safe.
        """
        safe_name = learner_name.strip().lower().replace(" ", "_")
        return self._storage_dir / f"{safe_name}.json"

    # ------------------------------------------------------------------
    # Core I/O
    # ------------------------------------------------------------------

    def load_profile(self, learner_name: str) -> Optional[LearnerProfile]:
        """Load a learner profile from disk.

        Parameters
        ----------
        learner_name:
            The learner's name (case-insensitive).

        Returns
        -------
        LearnerProfile if found and readable, otherwise None.
        Corrupted JSON is handled gracefully: the file is backed up
        with a ``.bak`` suffix and None is returned so the caller can
        decide to create a fresh profile.
        """
        path = self._profile_path(learner_name)

        if not path.exists():
            log.debug("No profile on disk for '%s'.", learner_name)
            return None

        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            profile = LearnerProfile.from_dict(data)
            log.debug("Loaded profile for '%s' from %s.", learner_name, path)
            return profile

        except json.JSONDecodeError as exc:
            backup = path.with_suffix(".json.bak")
            shutil.copy2(path, backup)
            log.error(
                "Corrupted JSON for '%s' — backed up to %s. Error: %s",
                learner_name, backup, exc,
            )
            return None

        except Exception as exc:
            log.error("Unexpected error loading profile for '%s': %s", learner_name, exc)
            return None

    def save_profile(self, profile: LearnerProfile) -> bool:
        """Persist a learner profile to disk as pretty-printed JSON.

        Parameters
        ----------
        profile:
            The profile to save.  ``updated_at`` is refreshed before writing.

        Returns
        -------
        True on success, False on any I/O error.
        """
        profile.updated_at = _utc_now()
        path = self._profile_path(profile.learner_name)

        try:
            # Write to a temp file first, then rename — atomic on POSIX.
            tmp = path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(profile.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            tmp.replace(path)
            log.debug("Saved profile for '%s' to %s.", profile.learner_name, path)
            return True

        except Exception as exc:
            log.error("Failed to save profile for '%s': %s", profile.learner_name, exc)
            return False

    def create_profile(self, learner_name: str) -> LearnerProfile:
        """Create a brand-new profile and immediately persist it.

        If a profile already exists for this learner, the existing
        profile is returned unchanged (no overwrite).

        Parameters
        ----------
        learner_name:
            Display name for the learner.

        Returns
        -------
        The newly created (or already existing) LearnerProfile.
        """
        existing = self.load_profile(learner_name)
        if existing is not None:
            log.debug(
                "create_profile('%s') — profile already exists, returning it.",
                learner_name,
            )
            return existing

        profile = LearnerProfile(learner_name=learner_name)
        self.save_profile(profile)
        log.info("Created new profile for '%s'.", learner_name)
        return profile

    def get_or_create(self, learner_name: str) -> LearnerProfile:
        """Return the learner's profile, creating it automatically if absent.

        This is the recommended entry point for most callers.

        Parameters
        ----------
        learner_name:
            The learner's name.

        Returns
        -------
        Always returns a valid LearnerProfile — never None.
        """
        profile = self.load_profile(learner_name)
        if profile is None:
            profile = self.create_profile(learner_name)
        return profile

    # ------------------------------------------------------------------
    # Convenience update methods
    # These wrap profile mutations and always persist afterwards so
    # callers that just want "record X and forget" don't have to manage
    # the save step themselves.
    # ------------------------------------------------------------------

    def record_error(
        self,
        profile:       LearnerProfile,
        error_type:    str,
        error_message: str,
        topic:         str = "",
    ) -> None:
        """Record a detected error on the profile and save.

        Parameters
        ----------
        profile:
            The learner profile to update (mutated in place).
        error_type:
            Python exception class name (e.g. "ValueError").
        error_message:
            Exception message string.
        topic:
            Optional topic associated with this error.
        """
        profile.add_error(error_type, error_message, topic)
        self.save_profile(profile)
        log.debug(
            "Recorded %s for '%s' (topic=%r).",
            error_type, profile.learner_name, topic,
        )

    def record_topic(self, profile: LearnerProfile, topic: str) -> None:
        """Record a studied topic on the profile and save.

        Parameters
        ----------
        profile:
            The learner profile to update (mutated in place).
        topic:
            Short label for the concept covered.
        """
        profile.add_topic(topic)
        self.save_profile(profile)
        log.debug("Recorded topic '%s' for '%s'.", topic, profile.learner_name)

    def mark_mastered(self, profile: LearnerProfile, concept: str) -> None:
        """Mark a concept as mastered on the profile and save.

        Parameters
        ----------
        profile:
            The learner profile to update (mutated in place).
        concept:
            The mastered concept label.
        """
        profile.mark_mastered(concept)
        self.save_profile(profile)
        log.debug("Marked '%s' mastered for '%s'.", concept, profile.learner_name)

    def mark_struggling(self, profile: LearnerProfile, concept: str) -> None:
        """Mark a concept as difficult on the profile and save.

        Parameters
        ----------
        profile:
            The learner profile to update (mutated in place).
        concept:
            The struggling concept label.
        """
        profile.mark_struggling(concept)
        self.save_profile(profile)
        log.debug("Marked '%s' struggling for '%s'.", concept, profile.learner_name)

    def append_interaction(
        self,
        profile:  LearnerProfile,
        role:     str,
        content:  str,
        topic:    str = "",
    ) -> None:
        """Append a conversation turn to the profile and save.

        Parameters
        ----------
        profile:
            The learner profile to update.
        role:
            "student" or "tutor".
        content:
            Message text.
        topic:
            Optional topic label for this turn.
        """
        profile.append_interaction(role, content, topic)
        self.save_profile(profile)

    # ------------------------------------------------------------------
    # Query helpers (read-only — no disk writes)
    # ------------------------------------------------------------------

    def get_summary(self, learner_name: str) -> str:
        """Return a human-readable summary for a learner by name.

        Parameters
        ----------
        learner_name:
            The learner's name.

        Returns
        -------
        Summary string, or a short message if the profile is not found.
        """
        profile = self.load_profile(learner_name)
        if profile is None:
            return f"No profile found for '{learner_name}'."
        return profile.get_summary()

    def profile_exists(self, learner_name: str) -> bool:
        """Return True if a profile file exists on disk for this learner."""
        return self._profile_path(learner_name).exists()

    def list_learners(self) -> list[str]:
        """Return the names of all learners that have profiles on disk.

        Returns
        -------
        Sorted list of learner name strings (derived from filenames).
        """
        names = [
            p.stem.replace("_", " ").title()
            for p in self._storage_dir.glob("*.json")
            if not p.name.endswith(".bak")
        ]
        return sorted(names)

    def update_from_run_result(
        self,
        profile:    LearnerProfile,
        error_type: str,
        error_msg:  str,
        topic:      str = "",
        success:    bool = False,
    ) -> None:
        """Update a profile from a safe_python_runner execution result.

        This is the primary integration point for Week 2's RunResult.
        Call this after every run_python_safely() call — on both success
        and failure — to keep the profile up to date.

        On success  → only ``topic`` is recorded (no error logged).
        On failure  → error and topic are both recorded.

        Parameters
        ----------
        profile:
            The learner profile to update.
        error_type:
            RunResult.error_type from safe_python_runner (empty string on
            success — use the ``success`` flag to distinguish).
        error_msg:
            RunResult.error_message.
        topic:
            Optional topic hint extracted from the student's code or question.
        success:
            True when RunResult.ok is True.
        """
        if topic:
            self.record_topic(profile, topic)

        if not success and error_type:
            self.record_error(profile, error_type, error_msg, topic)
        else:
            # Successful execution — save the updated topic timestamp.
            self.save_profile(profile)

        log.debug(
            "update_from_run_result: learner=%r success=%s error_type=%r topic=%r",
            profile.learner_name, success, error_type, topic,
        )