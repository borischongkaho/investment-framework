"""Runtime config for the boris_trade investment framework.

Resolves user-specific paths and language preferences from environment variables,
with safe defaults that work out-of-the-box on a fresh clone.

Read order:
1. Environment variable (if set)
2. config.local.toml at repo root (if present, gitignored)
3. config.example.toml at repo root (committed, default values)
4. Hardcoded fallback constant in this module
"""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

# Hardcoded fallbacks. Match config.example.toml.
_DEFAULTS = {
    "investment_dir": "data",
    "language": "zh-HK",
}


@dataclass(frozen=True)
class Config:
    investment_dir: Path
    language: str

    @property
    def portfolio_path(self) -> Path:
        return self.investment_dir / "portfolio.md"

    @property
    def research_dir(self) -> Path:
        return self.investment_dir / "research"

    @property
    def full_reports_dir(self) -> Path:
        return self.research_dir / "full_reports"

    @property
    def reviews_dir(self) -> Path:
        return self.investment_dir / "reviews"

    @property
    def sourcing_dir(self) -> Path:
        return self.investment_dir / "sourcing"

    @property
    def journal_dir(self) -> Path:
        return self.investment_dir / "journal"

    @property
    def forward_predictions_path(self) -> Path:
        return self.investment_dir / "forward_predictions.json"

    # v5.2.0 — V4.9 operations layer (decision_log / backtest_runner / pre_trade_gate / stress_test / portfolio_sync)
    @property
    def decisions_path(self) -> Path:
        return self.investment_dir / "decision_log" / "decisions.json"

    @property
    def scorecard_path(self) -> Path:
        return self.investment_dir / "backtest" / "scorecard.md"

    @property
    def positions_path(self) -> Path:
        return self.investment_dir / "positions.json"

    @property
    def models_dir(self) -> Path:
        return self.investment_dir / "models"


def _load_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def load() -> Config:
    """Return the active Config. Cached behavior intentionally not added — call
    sites are short-lived; correctness over micro-optimization."""
    example = _load_toml(REPO_ROOT / "config.example.toml")
    local = _load_toml(REPO_ROOT / "config.local.toml")

    investment_dir = (
        os.environ.get("BT_INVESTMENT_DIR")
        or local.get("investment_dir")
        or example.get("investment_dir")
        or _DEFAULTS["investment_dir"]
    )
    language = (
        os.environ.get("BT_LANGUAGE")
        or local.get("language")
        or example.get("language")
        or _DEFAULTS["language"]
    )

    investment_path = Path(investment_dir)
    if not investment_path.is_absolute():
        investment_path = REPO_ROOT / investment_path

    return Config(investment_dir=investment_path, language=language)


EXAMPLE_POSITIONS_PATH = REPO_ROOT / "portfolio_structure" / "positions.example.json"


def resolve_positions_path() -> Path:
    """Where the machine-readable portfolio state lives (pre_trade_gate / stress_test / portfolio_sync).

    Order: BT_POSITIONS_PATH env var -> <investment_dir>/positions.json (if it exists) ->
    the bundled, fake positions.example.json so the tools run out-of-the-box as a demo.
    """
    override = os.environ.get("BT_POSITIONS_PATH")
    if override:
        return Path(override).expanduser()
    candidate = load().positions_path
    if candidate.exists():
        return candidate
    return EXAMPLE_POSITIONS_PATH


if __name__ == "__main__":
    cfg = load()
    print(f"investment_dir: {cfg.investment_dir}")
    print(f"language: {cfg.language}")
    print(f"portfolio_path: {cfg.portfolio_path}")
    print(f"full_reports_dir: {cfg.full_reports_dir}")
    print(f"positions_path: {resolve_positions_path()}")
