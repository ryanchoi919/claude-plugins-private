"""지원 상태 갱신과 지원 폴더 스캔.

usage: python3 status.py scan <applications 폴더>
       python3 status.py set <공고.md> <상태> <now ISO 8601>
"""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))

import json
import re
import sys
from pathlib import Path

from scripts.config import STATUSES, read_frontmatter


def set_status(gonggo_md, status: str, now: str):
    if status not in STATUSES:
        raise ValueError(f"상태는 {STATUSES} 중 하나여야 합니다: {status}")
    p = Path(gonggo_md)
    text = p.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{p}: frontmatter(--- 블록)가 없습니다")
    end = text.index("\n---", 4)
    fm, rest = text[:end], text[end:]
    m = re.search(r"^상태:(.*)$", fm, flags=re.M)
    old = m.group(1).strip() if m else None
    if old == status:
        return old, status
    if m:
        fm = fm[:m.start()] + f"상태: {status}" + fm[m.end():]
    elif "\naliases:" in fm:
        fm = fm.replace("\naliases:", f"\n상태: {status}\naliases:", 1)
    else:
        fm = fm + f"\n상태: {status}"
    fm = re.sub(r"^modified:.*$", f"modified: {now}", fm, count=1, flags=re.M)
    p.write_text(fm + rest, encoding="utf-8")
    return old or None, status


def scan(applications_dir) -> list:
    rows = []
    for d in sorted(Path(applications_dir).iterdir()):
        f = d / "공고.md"
        if not d.is_dir() or not f.is_file():
            continue
        try:
            fm, _ = read_frontmatter(f)
        except ValueError:
            fm = {}
        rows.append({"folder": d.name, "company": fm.get("회사"), "status": fm.get("상태"),
                     "applied": str(fm["지원일"]) if fm.get("지원일") else None,
                     "has_progress": (d / "진행 상황.md").is_file()})
    return rows


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    try:
        if argv[:1] == ["scan"] and len(argv) == 2:
            print(json.dumps(scan(argv[1]), ensure_ascii=False, indent=2))
            return 0
        if argv[:1] == ["set"] and len(argv) == 4:
            old, new = set_status(argv[1], argv[2], argv[3])
            print(f"{old or '(없음)'} → {new}")
            return 0
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    print("usage: status.py scan <dir> | set <공고.md> <상태> <now>", file=sys.stderr)
    return 64


if __name__ == "__main__":
    sys.exit(main())
