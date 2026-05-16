"""
Knowledge aging detection engine.

Computes an aging score (0.0–1.0) for each wiki article based on three factors:
  - T (time decay, weight 0.4): days since last access / created_at
  - F (frequency factor, weight 0.3): access_count relative to peers
  - C (confidence factor, weight 0.3): inverted confidence score

Tiers:
  0.0–0.3  🟢 Active    — no action
  0.3–0.5  🟡 Notice    — frontmatter aging: true
  0.5–0.7  🟠 Aging     — flag + write event log
  0.7–1.0  🔴 Stale     — flag + archive suggestion
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from config.paths import paths
from tools.core.kb.confidence import parse_frontmatter

# Module-level cache: {filepath_str: (mtime, result_dict)}
_cache: dict[str, tuple[float, dict]] = {}

SKIP_FILES = {"index.md", "README.md", "base.md"}
AGING_LOG = paths.storage.cache / "aging_events.jsonl"

# Configurable thresholds (days)
THRESHOLD_DAYS = 90  # Full aging after this many days without access
ACCESS_DECAY_DAYS = 30  # Access count half-life

# Tier boundaries
TIER_ACTIVE = 0.3
TIER_NOTICE = 0.5
TIER_AGING = 0.7


def _days_since(iso_date_str: str | None) -> float | None:
    """Calculate days from iso_date_str to now. Returns None if absent."""
    if not iso_date_str or iso_date_str == "null":
        return None
    try:
        dt = datetime.fromisoformat(iso_date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - dt
        return max(0.0, delta.total_seconds() / 86400)
    except (ValueError, TypeError):
        return None


def compute_aging(filepath: Path) -> dict:
    """Compute aging score for a wiki article.

    Returns:
        {
            score: float,          # 0.0–1.0, higher = more aged
            tier: str,             # "active" | "notice" | "aging" | "stale"
            breakdown: {
                time_decay: float,
                frequency: float,
                confidence: float,
            },
            details: {
                days_since_created: float | None,
                days_since_access: float | None,
                access_count: int,
                confidence_score: float,
            }
        }
    """
    path_str = str(filepath)
    try:
        current_mtime = os.path.getmtime(filepath)
    except OSError:
        current_mtime = -1

    # Check cache
    if path_str in _cache:
        cached_mtime, cached_result = _cache[path_str]
        if cached_mtime == current_mtime:
            return cached_result

    # Read frontmatter
    fm = parse_frontmatter(filepath)

    created_at = fm.get("created_at")
    last_accessed = fm.get("last_accessed_at")
    access_count = fm.get("access_count", 0)
    if isinstance(access_count, str):
        try:
            access_count = int(access_count)
        except ValueError:
            access_count = 0

    # ── Factor T: Time decay (weight 0.4) ──
    days_since_created = _days_since(created_at)
    days_since_access = _days_since(last_accessed)

    # Use last_accessed if available, otherwise fall back to created_at
    ref_days = days_since_access if days_since_access is not None else days_since_created
    if ref_days is not None:
        # Exponential decay: 1 - e^(-days/threshold)
        time_decay = round(1.0 - pow(2.0, -ref_days / ACCESS_DECAY_DAYS), 4)
    else:
        # No timestamp at all → moderately aged (we know nothing)
        time_decay = 0.5

    # ── Factor F: Frequency factor (weight 0.3) ──
    # Lower access_count → higher aging. Scale: 0 access = 1.0, 10+ = 0.0
    frequency = round(max(0.0, 1.0 - min(access_count, 10) / 10), 4)

    # ── Factor C: Confidence factor (weight 0.3) ──
    # Import here to avoid circular dependency at module level
    from tools.core.kb.confidence import compute_confidence as _compute_confidence

    conf_result = _compute_confidence(filepath)
    conf_score = conf_result.get("score", 0.0)
    # Invert confidence: low confidence → high aging contribution
    confidence = round(1.0 - conf_score, 4)

    # ── Combined score ──
    score = round(time_decay * 0.4 + frequency * 0.3 + confidence * 0.3, 4)

    # ── Tier ──
    if score < TIER_ACTIVE:
        tier = "active"
    elif score < TIER_NOTICE:
        tier = "notice"
    elif score < TIER_AGING:
        tier = "aging"
    else:
        tier = "stale"

    result = {
        "score": score,
        "tier": tier,
        "breakdown": {
            "time_decay": time_decay,
            "frequency": frequency,
            "confidence": confidence,
        },
        "details": {
            "days_since_created": days_since_created,
            "days_since_access": days_since_access,
            "access_count": access_count,
            "confidence_score": conf_score,
        },
    }

    _cache[path_str] = (current_mtime, result)
    return result


def batch_aging(wiki_dir: Path | None = None, min_score: float = 0, limit: int = 0) -> list[dict]:
    """Scan all .md files and compute aging scores.

    Results sorted by score descending (most aged first).

    Args:
        wiki_dir: Directory containing .md files. Defaults to paths.wiki_dir.
        min_score: Only return results with score >= min_score.
        limit: Max results (0 = unlimited).

    Returns:
        List of {file: str, score: float, tier: str, breakdown: dict, details: dict}
    """
    if wiki_dir is None:
        wiki_dir = paths.wiki_dir

    results = []
    for md_file in sorted(wiki_dir.rglob("*.md")):
        if md_file.name in SKIP_FILES:
            continue

        aging = compute_aging(md_file)
        if aging["score"] >= min_score:
            results.append(
                {
                    "file": str(md_file.relative_to(wiki_dir).with_suffix("")),
                    "score": aging["score"],
                    "tier": aging["tier"],
                    "breakdown": aging["breakdown"],
                    "details": aging["details"],
                }
            )

    results.sort(key=lambda r: r["score"], reverse=True)
    if limit > 0:
        results = results[:limit]
    return results


def report(wiki_dir: Path | None = None) -> dict:
    """Return aging statistics summary."""
    all_results = batch_aging(wiki_dir=wiki_dir, min_score=0)
    total = len(all_results)

    tiers = {"active": 0, "notice": 0, "aging": 0, "stale": 0}
    for r in all_results:
        tiers[r["tier"]] = tiers.get(r["tier"], 0) + 1

    stale_candidates = [r for r in all_results if r["tier"] == "stale"]
    aging_candidates = [r for r in all_results if r["tier"] == "aging"]

    return {
        "total_articles": total,
        "tier_distribution": tiers,
        "stale_count": len(stale_candidates),
        "aging_count": len(aging_candidates),
        "top_aged_files": stale_candidates[:10] if stale_candidates else aging_candidates[:5],
    }


def log_aging_event(file_stem: str, action: str, reason: str):
    """Append an aging event to the JSONL log.

    Args:
        file_stem: File stem (without .md) of the affected article.
        action: Action taken ("flagged", "auto_archived", "reviewed").
        reason: Human-readable reason.
    """
    AGING_LOG.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "file": file_stem,
        "action": action,
        "reason": reason,
    }
    with open(AGING_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def get_aging_events(limit: int = 50) -> list[dict]:
    """Read recent aging events from log.

    Returns list sorted newest-first.
    """
    if not AGING_LOG.exists():
        return []

    events = []
    try:
        with open(AGING_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except OSError:
        return []

    events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    return events[:limit]


# ── 老化响应策略 ──


def _get_raw_frontmatter(text: str) -> tuple[str, str]:
    """Split markdown into (raw_frontmatter_text, body).

    Returns (fm_text_without_dashes, body_text).
    """
    if not text.startswith("---"):
        return "", text

    rest = text[3:]
    if rest.startswith("\n"):
        rest = rest[1:]

    if rest.startswith("---"):
        body = rest[3:]
        if body.startswith("\n"):
            body = body[1:]
        return "", body

    match = re.search(r"\n---", rest)
    if not match:
        return "", text

    fm_text = rest[: match.start()]
    body = rest[match.end() :]
    if body.startswith("\n"):
        body = body[1:]
    return fm_text, body


def apply_aging_flag(filepath: Path) -> dict:
    """Write frontmatter `aging: true` if tier >= notice, remove flag if active.

    Returns dict with keys: file, tier, flagged (bool), action (str).
    """
    aging = compute_aging(filepath)
    tier = aging["tier"]
    text = filepath.read_text(encoding="utf-8")
    fm_text, body = _get_raw_frontmatter(text)

    has_flag = "aging:" in fm_text if fm_text else False
    should_flag = tier != "active"

    if should_flag and not has_flag:
        lines = fm_text.split("\n") if fm_text else []
        insert_at = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip():
                insert_at = i + 1
                break
        lines.insert(insert_at, "aging: true")
        new_fm = "\n".join(lines)
        new_text = f"---\n{new_fm}\n---\n{body}"
        filepath.write_text(new_text, encoding="utf-8")
        log_aging_event(filepath.stem, "flagged", f"tier={tier}, score={aging['score']}")
        return {"file": filepath.stem, "tier": tier, "flagged": True, "action": "flagged"}
    elif not should_flag and has_flag:
        new_lines = [ln for ln in (fm_text.split("\n") if fm_text else []) if not ln.strip().startswith("aging:")]
        new_fm = "\n".join(new_lines)
        new_text = f"---\n{new_fm}\n---\n{body}"
        filepath.write_text(new_text, encoding="utf-8")
        log_aging_event(filepath.stem, "unflagged", f"tier={tier}, score={aging['score']}")
        return {"file": filepath.stem, "tier": tier, "flagged": False, "action": "unflagged"}

    return {"file": filepath.stem, "tier": tier, "flagged": should_flag, "action": "none"}


def suggest_archive(wiki_dir: Path | None = None, min_score: float = 0.7) -> list[dict]:
    """Suggest articles for archiving (stale tier by default).

    Returns sorted list of {file, score, tier, details}.
    """
    results = batch_aging(wiki_dir=wiki_dir, min_score=min_score)
    return [
        {
            "file": r["file"],
            "score": r["score"],
            "tier": r["tier"],
            "details": r["details"],
        }
        for r in results
    ]


def suggest_review(wiki_dir: Path | None = None) -> list[dict]:
    """Suggest articles needing review (notice + aging tiers)."""
    results = batch_aging(wiki_dir=wiki_dir)
    return [
        {
            "file": r["file"],
            "score": r["score"],
            "tier": r["tier"],
            "details": r["details"],
        }
        for r in results
        if r["tier"] in ("notice", "aging")
    ]


def apply_all_flags(wiki_dir: Path | None = None) -> list[dict]:
    """Scan all wiki files and update aging flags in frontmatter.

    Returns list of action results.
    """
    if wiki_dir is None:
        wiki_dir = paths.wiki_dir

    results = []
    for md_file in sorted(wiki_dir.rglob("*.md")):
        if md_file.name in SKIP_FILES:
            continue
        try:
            results.append(apply_aging_flag(md_file))
        except Exception as e:
            results.append({"file": md_file.stem, "error": str(e)})
    return results
