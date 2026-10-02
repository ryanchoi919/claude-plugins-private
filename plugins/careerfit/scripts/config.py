"""CAREER.md 설정 로더와 제출 파일명 규칙."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

DOC_TYPES = ("이력서", "경력기술서", "포트폴리오")
STATUSES = ("준비 중", "서류 제출", "서류 전형", "서류 탈락", "면접", "최종 합격", "불합격", "지원 취소")
DEFAULT_PATHS = {
    "projects": "projects",
    "applications": "applications",
    "base": "base",
    "insights": "insights.md",
    "output": "output",
}


@dataclass
class Career:
    root: Path
    name: str
    contact: dict
    paths: dict
    market: str = "KR"
    career_start: date | None = None
    filename_pattern: str = "{name}_{doc}_{company}"
    money_policy: str = "allow"
    body: str = ""


def read_frontmatter(path: Path) -> tuple[dict, str]:
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: frontmatter(--- 블록)가 없습니다")
    end = text.index("\n---", 4)
    try:
        data = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"{path}: frontmatter YAML 오류: {e}") from e
    return data, text[end + 4:].lstrip("\n")


def _resolve(root: Path, value) -> Path:
    s = str(value)
    if s.startswith("~") or s.startswith("/"):
        return Path(s).expanduser()
    return root / s


def load_career(path) -> Career:
    path = Path(path).expanduser()
    if not path.is_file():
        raise ValueError(f"CAREER.md를 찾을 수 없습니다: {path}")
    fm, body = read_frontmatter(path)
    if not fm.get("name"):
        raise ValueError("CAREER.md의 name이 비어 있습니다")
    root = path.parent
    raw = {**DEFAULT_PATHS, **(fm.get("paths") or {})}
    start = fm.get("career_start")
    if isinstance(start, str):
        start = date.fromisoformat(start)
    return Career(
        root=root,
        name=str(fm["name"]),
        contact=fm.get("contact") or {},
        paths={k: _resolve(root, v) for k, v in raw.items()},
        market=fm.get("market", "KR"),
        career_start=start,
        filename_pattern=fm.get("filename_pattern", "{name}_{doc}_{company}"),
        money_policy=fm.get("money_policy", "allow"),
        body=body,
    )


_CORP = re.compile(r"\(주\)|㈜|주식회사|\s+")


def normalize_company(name: str) -> str:
    return _CORP.sub("", name).strip()


def submission_name(career: Career, doc: str, company: str | None = None, ext: str | None = "pdf") -> str:
    if doc not in DOC_TYPES:
        raise ValueError(f"문서종류는 {DOC_TYPES} 중 하나여야 합니다: {doc}")
    if company:
        stem = career.filename_pattern.format(name=career.name, doc=doc, company=normalize_company(company))
    else:
        stem = f"{career.name}_{doc}"
    return f"{stem}.{ext}" if ext else stem


if __name__ == "__main__":
    import json
    import sys

    c = load_career(sys.argv[1])
    print(json.dumps({"name": c.name, "paths": {k: str(v) for k, v in c.paths.items()},
                      "career_start": str(c.career_start) if c.career_start else None}, ensure_ascii=False, indent=2))
