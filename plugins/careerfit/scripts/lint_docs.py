"""제출 서류 린트: 금지어·타사명·숨은 텍스트·title·주장 원장·기간·버전·링크."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))

import html as _html
import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from pypdf import PdfReader

from scripts.config import load_career, normalize_company, read_frontmatter

COMMENT = re.compile(r"<!--(.*?)-->", re.S)
BLOCKS = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)
DATA_URI = re.compile(r"data:[a-z]+/[a-z0-9.+-]+;base64,[A-Za-z0-9+/=—\-]+", re.I)
TAG = re.compile(r"<[^>]+>")
BANNED = [
    ("EM_DASH", "필수", re.compile(r"—"), "em dash 사용 금지"),
    ("FIRST_PERSON", "필수", re.compile(r"(?<![가-힣])(저는|제가)"), "'저는/제가' 사용 금지"),
    ("EMOJI", "필수", re.compile("[\U0001F300-\U0001FAFF☀-➿]"), "이모지 사용 금지"),
    ("HYPE_CANDIDATE", "권장", re.compile(r"최초|유일|전담|전국|완벽|혁신적"), "과장 수식어 후보: 출처 노트와 대조 필요"),
]


def _excerpt(text: str, start: int, end: int) -> str:
    return text[max(0, start - 20):end + 20].replace("\n", " ")


def _finding(rule, severity, doc, excerpt, message):
    return {"rule": rule, "severity": severity, "doc": str(doc), "excerpt": excerpt, "message": message}


def visible_text(path) -> str:
    p = Path(path)
    if p.suffix == ".pdf":
        return "\n".join(pg.extract_text() or "" for pg in PdfReader(str(p)).pages)
    s = p.read_text(encoding="utf-8")
    if p.suffix == ".md":
        if s.startswith("---\n"):
            s = s[s.index("\n---", 4) + 4:]
        return COMMENT.sub("", s)
    s = COMMENT.sub(" ", s)
    s = BLOCKS.sub(" ", s)
    s = DATA_URI.sub(" ", s)
    s = re.sub(r"<title>.*?</title>", " ", s, flags=re.S)
    s = _html.unescape(TAG.sub(" ", s))
    return re.sub(r"[ \t]+", " ", s)


def hidden_text(path) -> list:
    s = Path(path).read_text(encoding="utf-8")
    out = []
    for m in COMMENT.finditer(s):
        c = m.group(1).strip()
        if c and not c.startswith("["):
            out.append(c)
    return out


def find_banned(text: str, doc) -> list:
    out = []
    for rule, sev, rx, msg in BANNED:
        for m in rx.finditer(text):
            out.append(_finding(rule, sev, doc, _excerpt(text, m.start(), m.end()), msg))
    return out


def find_other_companies(text: str, company: str, known: list, doc) -> list:
    target = normalize_company(company)
    flat = normalize_company(text)
    out = []
    for k in known:
        name = normalize_company(k)
        if not name or name in target or target in name:
            continue
        i = flat.find(name)
        if i != -1:
            out.append(_finding("OTHER_COMPANY", "필수", doc, flat[max(0, i - 15):i + len(name) + 15],
                                f"다른 회사명 '{name}'이 남아 있음"))
    return out


def check_title(html_path, expected_stem: str) -> list:
    s = Path(html_path).read_text(encoding="utf-8")
    m = re.search(r"<title>(.*?)</title>", s, re.S)
    actual = m.group(1).strip() if m else ""
    if actual != expected_stem:
        return [_finding("TITLE_MISMATCH", "필수", html_path, actual, f"<title>은 '{expected_stem}'이어야 함")]
    return []


def check_hidden(path) -> list:
    return [_finding("HIDDEN_COMMENT", "권장", path, c[:40], "HTML 주석이 남아 있음: 공유·발행 시 노출될 수 있음")
            for c in hidden_text(path)]


@dataclass
class Claim:
    id: str
    text: str
    value: str
    source: str
    attribution: str
    forbidden: list = field(default_factory=list)


QUOTED = re.compile(r"[\"“]([^\"”]+)[\"”]")


def parse_claims(md_text: str) -> list:
    out = []
    for line in md_text.splitlines():
        if not re.match(r"^\|\s*C\d+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        cells += [""] * (6 - len(cells))
        forbidden = []
        for seg in cells[5].split(";"):
            forbidden += QUOTED.findall(seg.split("→", 1)[0])
        out.append(Claim(cells[0], cells[1], cells[2], cells[3], cells[4], forbidden))
    return out


UNITS = r"%p|%|부|권|개월|개|명|년|주|일|원|억|만|회|종|건|곳|쪽|배"
NUM = re.compile(r"(?<![\d.,])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*(" + UNITS + r")")


def numbers_in(text: str) -> set:
    return {(v.replace(",", ""), u) for v, u in NUM.findall(text)}


def check_claims(text: str, claims: list, doc) -> list:
    out = []
    for c in claims:
        for phrase in c.forbidden:
            i = text.find(phrase)
            if i != -1:
                out.append(_finding("FORBIDDEN_EXPRESSION", "필수", doc, _excerpt(text, i, i + len(phrase)),
                                    f"{c.id}의 금지 표현 '{phrase}'"))
    allowed = set()
    for c in claims:
        allowed |= numbers_in(c.text) | numbers_in(c.value)
    for v, u in sorted(numbers_in(text) - allowed):
        out.append(_finding("NUMBER_NOT_IN_CLAIMS", "권장", doc, f"{v}{u}",
                            f"주장 원장에 없는 숫자 '{v}{u}': 원장에 추가하고 출처를 확인"))
    return out


PERIOD = re.compile(
    r"(약\s*)?(\d+)\s*(개월|주|일)간?\s*\(\s*(\d{4})\.(\d{1,2})\.(\d{1,2})\s*[–\-~]\s*(?:(\d{4})\.)?(\d{1,2})\.(\d{1,2})\s*\)")


def check_periods(text: str, doc) -> list:
    out = []
    for m in PERIOD.finditer(text):
        approx, n, unit = bool(m.group(1)), int(m.group(2)), m.group(3)
        y1, mo1, d1 = int(m.group(4)), int(m.group(5)), int(m.group(6))
        y2 = int(m.group(7)) if m.group(7) else y1
        days = (date(y2, int(m.group(8)), int(m.group(9))) - date(y1, mo1, d1)).days
        if unit == "개월":
            actual, tol = days / 30.44, (0.75 if approx else 0.5)
        elif unit == "주":
            actual, tol = days / 7, (1.5 if approx else 1.0)
        else:
            actual, tol = days, 1
        if abs(actual - n) > tol:
            out.append(_finding("PERIOD_MISMATCH", "필수", doc, m.group(0),
                                f"'{n}{unit}'이지만 실제 기간은 {days}일(약 {actual:.1f}{unit})"))
    return out


def _full_years(start: date, ref: date) -> int:
    return ref.year - start.year - ((ref.month, ref.day) < (start.month, start.day))


def check_total_years(text: str, start: date, ref: date, doc) -> list:
    years = _full_years(start, ref)
    out = []
    for m in re.finditer(r"총\s*(\d+)\s*년(?!\s*\d+\s*개월)", text):
        if int(m.group(1)) != years:
            out.append(_finding("CAREER_YEARS", "필수", doc, m.group(0), f"총 경력은 만 {years}년"))
    for m in re.finditer(r"(\d+)\s*년(째|간)", text):
        n = int(m.group(1))
        if abs(n - years) <= 2 and n not in (years, years + 1):
            out.append(_finding("CAREER_YEARS", "필수", doc, m.group(0), f"경력 연수는 만 {years}년(또는 {years + 1}년째)"))
    return out


def _flat(text: str) -> str:
    return re.sub(r"\s+", "", text)


def check_version(html_path, pdf_path) -> list:
    h = _flat(visible_text(html_path))
    p = _flat(visible_text(pdf_path))
    chunks = [h[i:i + 12] for i in range(0, max(len(h) - 12, 0), 12)]
    out = []
    if chunks:
        ratio = sum(1 for c in chunks if c in p) / len(chunks)
        if ratio < 0.9:
            out.append(_finding("VERSION_MISMATCH", "필수", pdf_path, f"일치율 {ratio:.2f}",
                                "PDF가 HTML 최신본과 다름: PDF를 다시 렌더링"))
    if os.path.getmtime(pdf_path) < os.path.getmtime(html_path):
        out.append(_finding("PDF_OLDER_THAN_HTML", "권장", pdf_path, "", "PDF가 HTML보다 오래됨"))
    return out


URL = re.compile(r"https?://[^\s<>\"')]+")


def _head(url: str) -> int:
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "careerfit-lint"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status
    except Exception:
        return 0


def check_links(text: str, doc, fetch=None) -> list:
    out = []
    for url in sorted(set(URL.findall(text))):
        if "claude.ai/artifact" in url:
            out.append(_finding("ARTIFACT_LINK", "권장", doc, url,
                                "아티팩트는 기본 비공개: 채용 담당자에게 공유 권한이 있는지 확인"))
            continue
        if fetch is None:
            continue
        code = fetch(url)
        if code == 0 or code >= 400:
            out.append(_finding("LINK_BROKEN", "필수", doc, url, f"링크 응답 {code or '없음'}"))
    return out


def known_companies(applications_dir) -> list:
    out = []
    for d in sorted(Path(applications_dir).glob("*/")):
        f = d / "공고.md"
        if f.is_file():
            try:
                fm, _ = read_frontmatter(f)
                if fm.get("회사"):
                    out.append(str(fm["회사"]))
            except ValueError:
                pass
        out.append(d.name.split()[0])
    return out


def lint(career_md, company, docs, claims_md=None, pairs=(), ref=None, fetch=None) -> list:
    career = load_career(career_md)
    ref = ref or date.today()
    claims = parse_claims(Path(claims_md).read_text(encoding="utf-8")) if claims_md else []
    apps = career.paths["applications"]
    known = known_companies(apps) if apps.is_dir() else []
    out = []
    for d in docs:
        d = Path(d)
        t = visible_text(d)
        out += find_banned(t, d.name)
        out += find_other_companies(t, company, known, d.name)
        out += check_periods(t, d.name)
        if career.career_start:
            out += check_total_years(t, career.career_start, ref, d.name)
        if claims:
            out += check_claims(t, claims, d.name)
        out += check_links(t, d.name, fetch)
        if d.suffix == ".html":
            out += check_title(d, d.stem)
            out += check_hidden(d)
    for h, p in pairs:
        out += check_version(h, p)
    return out


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--career", required=True)
    ap.add_argument("--company", required=True)
    ap.add_argument("--claims")
    ap.add_argument("--pair", action="append", default=[])
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("docs", nargs="+")
    a = ap.parse_args(argv)
    pairs = [tuple(Path(x) for x in p.split(":", 1)) for p in a.pair]
    fs = lint(a.career, a.company, [Path(d) for d in a.docs], a.claims, pairs, fetch=None if a.offline else _head)
    print(json.dumps(fs, ensure_ascii=False, indent=2))
    return 1 if any(f["severity"] == "필수" for f in fs) else 0


if __name__ == "__main__":
    sys.exit(main())
