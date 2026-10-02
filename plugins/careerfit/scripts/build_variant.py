"""기본 포트폴리오 덱에서 회사판을 파생: 표지·meta·클로징 교체, 케이스 재배치, 목차·CASE 번호 재매핑.

usage: python3 build_variant.py <base.html> <spec.json> <out.html>

spec 키: title, meta, tagline, closing (필수) / cover_eyebrow, order (선택, 1부터 시작하는 기본본 케이스 번호 목록)
덱 마크업 계약: 표지 <section class="slide cover">의 첫 .eyebrow·.tagline, 목차 .toc-list 안 .toc-row(각 행에
<span class="num">NN</span>), 케이스 <section class="slide v2">(바로 앞 HTML 주석은 케이스에 딸림),
연락처 <section class="slide contact-page">의 .sub, 케이스 번호 표기 "CASE 0N".
"""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))

import json
import re
import sys
from pathlib import Path

DIV_TAG = re.compile(r"<div\b|</div>")


def _div_end(s: str, start: int) -> int:
    """start 위치의 <div ...>와 짝이 맞는 </div> 끝 인덱스."""
    depth = 0
    for m in DIV_TAG.finditer(s, start):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            return m.end()
    raise ValueError(f"닫히지 않은 div: {s[start:start + 40]}")


def _section(s: str, cls: str) -> tuple:
    i = s.find(f'<section class="slide {cls}">')
    if i == -1:
        raise ValueError(f"'slide {cls}' 슬라이드가 없습니다")
    return i, s.index("</section>", i) + len("</section>")


def _replace_inner(s: str, section_cls: str, inner_cls: str, new_inner: str) -> str:
    a, b = _section(s, section_cls)
    open_tag = f'<div class="{inner_cls}">'
    i = s.find(open_tag, a, b)
    if i == -1:
        raise ValueError(f"'{section_cls}' 슬라이드에 .{inner_cls}가 없습니다")
    j = _div_end(s, i)
    return s[:i] + open_tag + new_inner + "</div>" + s[j:]


def _case_units(s: str) -> list:
    """(start, end) 목록: 바로 앞 주석을 포함한 각 케이스 슬라이드."""
    units = []
    for m in re.finditer(r'<section class="slide v2">', s):
        start = m.start()
        before = s[:start].rstrip()
        if before.endswith("-->"):
            start = before.rindex("<!--")
        units.append((start, s.index("</section>", m.start()) + len("</section>")))
    return units


def _reorder_toc(s: str, order: list) -> str:
    i = s.find('<div class="toc-list">')
    if i == -1:
        return s
    end = _div_end(s, i)
    body_start = i + len('<div class="toc-list">')
    rows, k = [], body_start
    while True:
        r = s.find('<div class="toc-row">', k, end)
        if r == -1:
            break
        rows.append((r, _div_end(s, r)))
        k = rows[-1][1]
    if len(rows) != len(order):
        raise ValueError(f"목차 행 수({len(rows)})와 케이스 수({len(order)})가 다릅니다")
    texts = [s[a:b] for a, b in rows]
    new = [re.sub(r'<span class="num">\d+</span>', f'<span class="num">{p:02d}</span>', texts[o - 1], count=1)
           for p, o in enumerate(order, 1)]
    out, last = [], body_start
    for (a, b), t in zip(rows, new):
        out.append(s[last:a])
        out.append(t)
        last = b
    return s[:body_start] + "".join(out) + s[last:]


def build_variant(base_html: str, spec: dict) -> str:
    s = base_html
    s = re.sub(r"<title>.*?</title>", lambda m: f"<title>{spec['title']}</title>", s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">',
               lambda m: f'<meta name="description" content="{spec["meta"]}">', s, count=1)
    if spec.get("cover_eyebrow"):
        s = _replace_inner(s, "cover", "eyebrow", spec["cover_eyebrow"])
    s = _replace_inner(s, "cover", "tagline", spec["tagline"])
    s = _replace_inner(s, "contact-page", "sub", spec["closing"])

    units = _case_units(s)
    n = len(units)
    order = list(spec.get("order") or range(1, n + 1))
    if sorted(order) != list(range(1, n + 1)):
        raise ValueError(f"order는 1..{n}을 한 번씩 포함해야 합니다: {order}")
    if order == list(range(1, n + 1)):
        return s
    for (_, b), (a, _) in zip(units, units[1:]):
        if s[b:a].strip():
            raise ValueError("케이스 슬라이드 사이에 다른 내용이 있어 재배치할 수 없습니다")
    chunks = [s[a:b] for a, b in units]
    region_start, region_end = units[0][0], units[-1][1]
    s = s[:region_start] + "\n".join(chunks[o - 1] for o in order) + s[region_end:]
    s = _reorder_toc(s, order)
    mapping = {old: new for new, old in enumerate(order, 1)}
    return re.sub(r"CASE 0(\d)", lambda m: f"CASE {mapping.get(int(m.group(1)), int(m.group(1))):02d}", s)


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 3:
        print("usage: build_variant.py <base.html> <spec.json> <out.html>", file=sys.stderr)
        return 64
    base = Path(argv[0]).read_text(encoding="utf-8")
    spec = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    Path(argv[2]).write_text(build_variant(base, spec), encoding="utf-8")
    print(argv[2])
    return 0


if __name__ == "__main__":
    sys.exit(main())
