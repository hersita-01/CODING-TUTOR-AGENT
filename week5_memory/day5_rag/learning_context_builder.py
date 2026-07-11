"""
learning_context_builder.py

Week 5 / Day 5 - Memory + RAG Integration
------------------------------------------
Builds a compact, prompt-ready summary of a learner's history from their
`LearnerProfile` object (as produced by
`week5-memory/day1-learner-memory/learner_profile.py`).

This module is intentionally read-only with respect to the learner profile:
it never mutates state, it only *summarizes* it. All mutation happens through
`MemoryManager` methods elsewhere in the pipeline (see
`memory_rag_pipeline.py`).

Design notes
------------
- The exact attribute names on `LearnerProfile` were not available at the
  time this module was written (Day 5 was implemented without direct access
  to the Day 1 source file). To keep this module robust against small
  schema differences, every field is read defensively with `getattr(...)`
  and sensible fallbacks, rather than assuming a rigid dataclass shape.
  If your actual `LearnerProfile` uses different field names, update the
  `_ATTR_*` constants at the top of this file and nothing else needs to
  change.
- Output is plain text (not JSON) because it is designed to be dropped
  directly into a system/context prompt for the tutor LLM.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Attribute name mapping (adjust here if your LearnerProfile schema differs)
# ---------------------------------------------------------------------------
_ATTR_STUDENT_ID = "student_id"
_ATTR_ERRORS = "errors"                      # List[Dict] or List[str]
_ATTR_STRUGGLING = "struggling_concepts"     # Dict[str, int] or List[str]
_ATTR_MASTERED = "mastered_concepts"         # List[str] / Set[str]
_ATTR_TOPICS = "topics_studied"              # List[str]
_ATTR_INTERACTIONS = "interaction_history"   # List[Dict]

# How much history to surface in the prompt (keep prompts small & relevant)
MAX_RECENT_ERRORS = 5
MAX_RECENT_INTERACTIONS = 3
MAX_TOPICS = 8


def _get_field(profile: Any, name: str, default: Any) -> Any:
    """Safely read a field from a LearnerProfile regardless of whether it
    is a dataclass, a plain object, or a dict.

    Args:
        profile: The learner profile object (any shape).
        name: Attribute / key name to read.
        default: Value to return if the field is missing.

    Returns:
        The field value, or `default` if not present.
    """
    if profile is None:
        return default
    if isinstance(profile, dict):
        return profile.get(name, default)
    return getattr(profile, name, default)


def _normalize_struggling(struggling: Any) -> Dict[str, int]:
    """Normalize the struggling-concepts field into a {concept: count} dict.

    Accepts either a dict of concept -> attempt_count, or a bare list of
    concept names (in which case count defaults to 1).
    """
    if isinstance(struggling, dict):
        return {
            str(k): int(v) if isinstance(v, (int, float)) else 1
            for k, v in struggling.items()
        }
    if isinstance(struggling, (list, set, tuple)):
        return {str(c): 1 for c in struggling}
    return {}


def _normalize_list(value: Any) -> List[str]:
    """Normalize any iterable-ish field into a list of strings."""
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(v) for v in value]
    return [str(value)]


def _summarize_errors(errors: List[Any]) -> List[str]:
    """Turn raw error records into short human-readable lines.

    Each error record may be a dict like:
        {"concept": "for-loops", "message": "off-by-one", "count": 2}
    or a plain string. Both are handled.
    """
    lines: List[str] = []
    for err in errors[-MAX_RECENT_ERRORS:]:
        if isinstance(err, dict):
            concept = err.get("concept", "unknown concept")
            message = err.get("message") or err.get("error") or ""
            count = err.get("count", 1)
            if count and int(count) > 1:
                lines.append(f"- {concept}: {message} (repeated {count}x)")
            else:
                lines.append(f"- {concept}: {message}")
        else:
            lines.append(f"- {err}")
    return lines


def _summarize_interactions(interactions: List[Any]) -> List[str]:
    """Turn recent interaction records into short human-readable lines."""
    lines: List[str] = []
    for interaction in interactions[-MAX_RECENT_INTERACTIONS:]:
        if isinstance(interaction, dict):
            student_msg = interaction.get("student_message", "").strip()
            if student_msg:
                snippet = (student_msg[:100] + "...") if len(student_msg) > 100 else student_msg
                lines.append(f"- Student asked: \"{snippet}\"")
        else:
            lines.append(f"- {interaction}")
    return lines


def build_learning_context(profile: Any) -> str:
    """Summarize a learner profile into a compact, prompt-ready context block.

    This is the single public entry point for Day 5's learner-memory
    summarization requirement. It covers:
        - previous errors
        - struggling concepts
        - mastered concepts
        - topics studied
        - recent interactions

    Args:
        profile: A `LearnerProfile` instance (or dict-like equivalent)
            returned by `MemoryManager.get_or_create()`.

    Returns:
        A formatted multi-section string ready to be injected into the
        tutor's system/context prompt. Returns a minimal "new learner"
        message if the profile has no history yet.

    Example:
        >>> profile = memory_manager.get_or_create("student_42")
        >>> context = build_learning_context(profile)
        >>> print(context)
        ## Learner Profile Summary
        Student: student_42
        ...
    """
    student_id = _get_field(profile, _ATTR_STUDENT_ID, "unknown_student")
    raw_errors = _get_field(profile, _ATTR_ERRORS, [])
    raw_struggling = _get_field(profile, _ATTR_STRUGGLING, {})
    raw_mastered = _get_field(profile, _ATTR_MASTERED, [])
    raw_topics = _get_field(profile, _ATTR_TOPICS, [])
    raw_interactions = _get_field(profile, _ATTR_INTERACTIONS, [])

    struggling = _normalize_struggling(raw_struggling)
    mastered = _normalize_list(raw_mastered)
    topics = _normalize_list(raw_topics)[-MAX_TOPICS:]
    errors = raw_errors if isinstance(raw_errors, list) else _normalize_list(raw_errors)
    interactions = raw_interactions if isinstance(raw_interactions, list) else []

    is_new_learner = not (errors or struggling or mastered or topics or interactions)
    if is_new_learner:
        logger.info("Building learning context for new learner: %s", student_id)
        return (
            "## Learner Profile Summary\n"
            f"Student: {student_id}\n"
            "This is a new learner with no recorded history yet. "
            "Introduce concepts from first principles and gauge their "
            "current level with a light diagnostic question before diving in.\n"
        )

    sections: List[str] = [f"## Learner Profile Summary", f"Student: {student_id}"]

    if topics:
        sections.append("\n### Topics Studied So Far")
        sections.append(", ".join(topics))

    if mastered:
        sections.append("\n### Mastered Concepts (do NOT re-explain from scratch)")
        sections.append(", ".join(sorted(mastered)))

    if struggling:
        sorted_struggling = sorted(struggling.items(), key=lambda kv: -kv[1])
        sections.append("\n### Struggling Concepts (give extra scaffolding)")
        for concept, count in sorted_struggling:
            sections.append(f"- {concept} (flagged {count}x)")

    error_lines = _summarize_errors(errors)
    if error_lines:
        sections.append("\n### Recent Errors")
        sections.extend(error_lines)

    interaction_lines = _summarize_interactions(interactions)
    if interaction_lines:
        sections.append("\n### Recent Interactions")
        sections.extend(interaction_lines)

    sections.append(
        "\n### Personalization Directives\n"
        "- If the student repeats a mistake logged above, gently reference "
        "the earlier attempt instead of treating it as new.\n"
        "- Do not re-teach mastered concepts from scratch; briefly acknowledge "
        "mastery and build on it.\n"
        "- Provide more scaffolding and smaller steps for struggling concepts.\n"
        "- Stay Socratic: ask guiding questions rather than giving direct answers."
    )

    context = "\n".join(sections)
    logger.debug("Built learning context for %s (%d chars)", student_id, len(context))
    return context