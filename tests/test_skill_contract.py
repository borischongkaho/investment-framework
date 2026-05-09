"""Skill-contract guard.

Asserts that no SKILL.md file restates numerical thresholds inline. The
canonical source of truth for all thresholds is `framework/SPEC.md`. If a
SKILL.md or supporting doc inlines a threshold value, this test fails and
the build breaks — preventing the doc-drift partner Josep flagged on
2026-05-09 ("唔會 drift scope").

The check looks for **specific known threshold patterns** that should only
appear in the canonical doc. It is intentionally tight: false positives
should be rare, and the right response to a real false-positive (a number
that is genuinely owned by the cited file) is to either remove the inline
value or whitelist the file.

Origin: adapted from aaronsoa PR-1 (originally referencing
`ACCT6111E_v5_hardened.md`); rebased on our independent `SPEC.md` per
gap-analysis 2026-05-09.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Known canonical thresholds that must only appear in the canonical files.
# Patterns are intentionally specific to the wording used in SPEC.md so
# that legitimate prose discussing valuation in case studies does not
# trigger false positives.
FORBIDDEN_INLINE = [
    # Terminal value concentration (SPEC §3 Phase 4)
    (r"TV.*EV.*40-60%", "TV/EV 40-60% threshold"),
    (r"60%\s*WARN", "TV concentration WARN threshold"),
    (r"75%\s*STOP", "TV concentration STOP threshold"),
    (r">\s*70%.*forecast period", "TV >70% inline threshold"),
    # Method convergence guards (SPEC §3 Phase 4)
    (r"ratio\s*[>＞]\s*1\.50.*WARN", "Method-convergence WARN threshold"),
    (r"ratio\s*[>＞]\s*2\.00.*STOP", "Method-convergence STOP threshold"),
]

# Files allowed to contain the canonical thresholds.
# Anything not listed here that matches a forbidden pattern fails the test.
CANONICAL_FILES = {
    "framework/SPEC.md",                  # current canonical
    "framework/ACCT6111E_v2_hardened.md", # historical reference, deprecated
    "framework/change_log.md",            # records the threshold history
    "framework/v42_advanced_report_template.md",  # report format spec
    "VERSION.md",                         # release notes mention thresholds
}

# Known legacy drift — files that currently restate thresholds inline because
# they predate the SPEC.md contract. Tests temporarily allow these but track
# them in a separate set so the cleanup obligation is visible.
#
# TODO: clean up before V5.0 GA — replace inline values with SPEC.md citations,
# then remove each file from this whitelist. Each entry below is a confirmed
# debt, not an acceptable long-term home for canonical numbers.
LEGACY_DRIFT_WHITELIST = {
    "skills/mba-valuation/methodology.md",
    "skills/mba-valuation/checklist.md",
    "skills/mba-valuation/sop.md",
    "skills/mba-valuation/reference-models.md",
}

# Globs of files to scan for inline-threshold violations.
SCAN_GLOBS = [
    "skills/**/*.md",
    "framework/*.md",
    "journal/templates/*.md",
]


def _scannable_files() -> list:
    files = []
    for glob in SCAN_GLOBS:
        files.extend(REPO_ROOT.glob(glob))
    return files


@pytest.mark.parametrize(
    "pattern,description",
    FORBIDDEN_INLINE,
    ids=[d for _, d in FORBIDDEN_INLINE],
)
def test_no_inline_thresholds(pattern: str, description: str):
    """Each forbidden threshold pattern may only appear in canonical files."""
    regex = re.compile(pattern)
    violations = []

    for path in _scannable_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in CANONICAL_FILES or rel in LEGACY_DRIFT_WHITELIST:
            continue
        text = path.read_text(encoding="utf-8")
        for match in regex.finditer(text):
            line_no = text[: match.start()].count("\n") + 1
            violations.append(f"{rel}:{line_no} — '{match.group(0)}'")

    assert not violations, (
        f"Found inline {description} in non-canonical files. "
        f"All numeric thresholds must be cited from `framework/SPEC.md`, "
        f"not restated.\nViolations:\n  " + "\n  ".join(violations)
    )


def test_canonical_doc_exists():
    """SPEC.md must be present — it is the framework's contract."""
    canonical = REPO_ROOT / "framework" / "SPEC.md"
    assert canonical.exists(), "framework/SPEC.md missing — the canonical contract"


def test_canonical_doc_lists_all_phases_and_gates():
    """SPEC.md must enumerate the 8 phases + 5 gates per the architecture diagram."""
    canonical = REPO_ROOT / "framework" / "SPEC.md"
    text = canonical.read_text(encoding="utf-8")
    # 8 phases
    for phase in ["Phase 0:", "Phase 1:", "Phase 2:", "Phase 3:",
                  "Phase 4:", "Phase 5:", "Phase 6:", "Phase 7:", "Phase 8:"]:
        assert phase in text, f"SPEC.md missing {phase}"
    # 5 V4.x gates
    for gate in ["Gate 0.5:", "Gate 0.7:", "Gate 4.5:", "Gate 6.5:", "Gate 9:"]:
        assert gate in text, f"SPEC.md missing {gate}"


def test_canonical_doc_contains_drift_control_rules():
    """SPEC §6 must state the rules for any future framework change."""
    canonical = REPO_ROOT / "framework" / "SPEC.md"
    text = canonical.read_text(encoding="utf-8")
    assert "Drift control rules" in text or "drift control rules" in text, (
        "SPEC.md must include drift-control rules to prevent the scope drift "
        "that motivated this canonical contract"
    )
