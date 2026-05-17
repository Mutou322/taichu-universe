"""
Confidence scoring module for wiki articles.

Scores articles 0.0–1.0 based on 5 factors:
- Source field presence in YAML frontmatter
- Source citations in body (^source::)
- Content structure (## headings)
- Wiki-links ([[ in body)
- Content length (character count)
"""

import os
import re
from pathlib import Path

import yaml

# Module-level cache: {filepath_str: (mtime, result_dict)}
_cache: dict[str, tuple[float, dict]] = {}

SKIP_FILES = {"index.md", "README.md", "base.md"}

# Scoring constants
SOURCE_PRESENCE_BONUS = 0.3
MAX_CITATION_SCORE = 0.2

# Content length thresholds (character count)
BODY_LEN_LONG = 5000
BODY_LEN_MEDIUM = 2000
BODY_LEN_SHORT = 500


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Split markdown text into (frontmatter_dict, body).

    Extracts YAML frontmatter delimited by --- lines.
    Returns ({}, full_text) if no frontmatter or parse error.
    """
    if not text.startswith("---"):
        return {}, text

    # Skip the opening ---
    rest = text[3:]
    if rest.startswith("\n"):
        rest = rest[1:]
    else:
        # --- not followed by newline (e.g. end of file)
        return {}, rest

    # Check for empty frontmatter: ---\n---
    if rest.startswith("---"):
        body = rest[3:]
        if body.startswith("\n"):
            body = body[1:]
        return {}, body

    # Find closing --- on its own line
    match = re.search(r"\n---", rest)
    if not match:
        # Malformed: no closing delimiter, treat everything as body
        return {}, text

    fm_text = rest[: match.start()]
    body = rest[match.end() :]  # Points right after ---
    if body.startswith("\n"):
        body = body[1:]

    try:
        fm = yaml.safe_load(fm_text)
        if not isinstance(fm, dict):
            fm = {}
    except yaml.YAMLError:
        fm = {}

    return fm or {}, body


def parse_frontmatter(filepath: Path) -> dict:
    """Read file, extract YAML frontmatter (--- delimited), return as dict.

    Returns {} if no frontmatter or parse error.
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}

    fm, _ = _split_frontmatter(text)
    return fm


def compute_confidence(filepath: Path) -> dict:
    """Compute confidence score for a wiki article.

    Returns:
        {
            score: float,           # 0.0–1.0, rounded to 2 decimal places
            breakdown: {
                source_presence: float,    # 0.0 or 0.3
                source_citations: float,   # 0.0–0.2
                content_structure: float,  # 0.0, 0.1, or 0.2
                wiki_links: float,         # 0.0, 0.05, or 0.15
                content_length: float,     # 0.0, 0.05, 0.1, or 0.15
            }
        }

    Results are cached by file mtime — if the file hasn't changed since the
    last call, the cached result is returned.
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

    # Read file
    try:
        text = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        result = {
            "score": 0.0,
            "breakdown": {
                "source_presence": 0.0,
                "source_citations": 0.0,
                "content_structure": 0.0,
                "wiki_links": 0.0,
                "content_length": 0.0,
            },
        }
        _cache[path_str] = (current_mtime, result)
        return result

    fm, body = _split_frontmatter(text)

    # Factor 1: Source field presence in frontmatter
    source_presence = SOURCE_PRESENCE_BONUS if "source" in fm else 0.0

    # Factor 2: Source citations (lines starting with source::)
    citation_lines = len(re.findall(r"^source::", body, re.MULTILINE))
    source_citations = round(min(citation_lines / 10 * MAX_CITATION_SCORE, MAX_CITATION_SCORE), 4)

    # Factor 3: Content structure (## heading lines)
    h2_count = len(re.findall(r"^##\s", body, re.MULTILINE))
    if h2_count >= 5:
        content_structure = 0.2
    elif h2_count >= 2:
        content_structure = 0.1
    else:
        content_structure = 0.0

    # Factor 4: Wiki-links
    wiki_count = body.count("[[")
    if wiki_count >= 5:
        wiki_links = 0.15
    elif wiki_count >= 1:
        wiki_links = 0.05
    else:
        wiki_links = 0.0

    # Factor 5: Content length
    body_len = len(body)
    if body_len > BODY_LEN_LONG:
        content_length = 0.15
    elif body_len > BODY_LEN_MEDIUM:
        content_length = 0.1
    elif body_len > BODY_LEN_SHORT:
        content_length = 0.05
    else:
        content_length = 0.0

    score = round(
        source_presence + source_citations + content_structure + wiki_links + content_length,
        2,
    )

    result = {
        "score": score,
        "breakdown": {
            "source_presence": source_presence,
            "source_citations": source_citations,
            "content_structure": content_structure,
            "wiki_links": wiki_links,
            "content_length": content_length,
        },
    }

    _cache[path_str] = (current_mtime, result)
    return result


def batch_confidence(wiki_dir: Path, min_score: float = 0) -> list[dict]:
    """Scan all .md files in wiki_dir and compute confidence scores.

    Skips files listed in SKIP_FILES ('index.md', 'README.md', 'base.md').
    Results are sorted by score descending.

    Args:
        wiki_dir: Directory containing .md wiki articles.
        min_score: If > 0, only return results with score >= min_score.

    Returns:
        List of {file: str, score: float, breakdown: dict} sorted by score
        descending.
    """
    results = []

    for md_file in sorted(wiki_dir.glob("*.md")):
        if md_file.name in SKIP_FILES:
            continue

        conf = compute_confidence(md_file)
        if conf["score"] >= min_score:
            results.append(
                {
                    "file": md_file.stem,
                    "score": conf["score"],
                    "breakdown": conf["breakdown"],
                }
            )

    results.sort(key=lambda r: r["score"], reverse=True)
    return results
