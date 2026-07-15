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


if __name__ == "__main__":
    cfg = load()
    print(f"investment_dir: {cfg.investment_dir}")
    print(f"language: {cfg.language}")
    print(f"portfolio_path: {cfg.portfolio_path}")
    print(f"full_reports_dir: {cfg.full_reports_dir}")
