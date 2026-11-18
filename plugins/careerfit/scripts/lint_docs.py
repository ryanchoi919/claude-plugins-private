"""제출 서류 린트: 금지어·타사명·숨은 텍스트·title·주장 원장·기간·버전·링크·공고 용어 분포·기본본 동일 비율."""
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
    ("EMOJI", "필수", re.compile("[\U0001F000-\U0001FAFF]"), "이모지 사용 금지"),
    ("PLACEHOLDER", "필수", re.compile(r"\[확인 필요[^\]]*\]|\{\{[A-Z_]+\}\}|\[(?:회사|기간|직무|이름|프로젝트|결과|문제|행동|설명|도구|분류|요약"
                                       r"|클로징|케이스|한 줄|핵심|학교|시험|소속|직급|업종|역할|링크|연도|점수|전공|분야|작업)[^\]]*\]"),
     "자리표시자가 남아 있음: 제출본에는 0개여야 함"),
    ("MECHANICAL_JD_LABEL", "권장", re.compile(r"공고\s*대응|공고\s*요구사항|대응\s*경험"),
     "공고를 처리한 듯한 표현: JD 항목명을 앞으로 할 일로 (예: 담당할 업무와 관련 경험)"),
    ("HYPE_CANDIDATE", "권장", re.compile(r"최초|유일|전담|전국|완벽|혁신적"), "과장 수식어 후보: 출처 노트와 대조 필요"),
]


def _excerpt(text: str, start: int, end: int) -> str:
    return text[max(0, start - 20):end + 20].replace("\n", " ")


def _finding(rule, severity, doc, excerpt, message):
    return {"rule": rule, "severity": severity, "doc": str(doc), "excerpt": excerpt, "message": message}


def visible_text(path) -> str:
    p = Path(path)
    if p.suffix == ".pdf":
        text = "\n".join(pg.extract_text() or "" for pg in PdfReader(str(p)).pages)
        # 헤드리스 Chrome + 나눔 폰트 PDF는 공백을 U+0001, en dash를 U+00AD로 추출한다
        return text.replace("\x01", " ").replace("\xad", "–")
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
    stripped = re.sub(r"\(주\)|㈜|주식회사", "", text)
    flat = re.sub(r"\s+", "", stripped)
    out = []
    for k in known:
        name = normalize_company(k)
        if not name or name in target or target in name:
            continue
        # 긴 이름만 띄어쓰기 변형("가상 컴퍼니")까지 찾는다. 짧은 이름은 "다른 회사와" 같은 오탐이 난다
        hay = flat if len(name) >= 5 else stripped
        rx = (re.compile(r"(?<![A-Za-z0-9])" + re.escape(name) + r"(?![A-Za-z0-9])") if name.isascii()
              else re.compile(re.escape(name)))
        m = rx.search(hay)
        if m:
            severity = "권장" if len(name) <= 2 else "필수"
            out.append(_finding("OTHER_COMPANY", severity, doc, hay[max(0, m.start() - 15):m.end() + 15],
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
        try:
            days = (date(y2, int(m.group(8)), int(m.group(9))) - date(y1, mo1, d1)).days
        except ValueError:
            out.append(_finding("PERIOD_MISMATCH", "필수", doc, m.group(0), "존재하지 않는 날짜"))
            continue
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


CAREER_CTX = re.compile(r"경력|실무|업계|커리어|산업|직장|근무|일해|몸담")


def _career_context(text: str, m) -> bool:
    return bool(CAREER_CTX.search(text[max(0, m.start() - 12):m.end() + 12]))


def check_total_years(text: str, start: date, ref: date, doc) -> list:
    """경력 문맥(경력·산업·업계 등)이 가까이 있으면 필수, 없으면 프로젝트 기간일 수 있어 권장."""
    years = _full_years(start, ref)
    out = []
    for m in re.finditer(r"총\s*(\d+)\s*년(?!\s*\d+\s*개월)", text):
        if int(m.group(1)) != years:
            out.append(_finding("CAREER_YEARS", "필수" if _career_context(text, m) else "권장", doc, m.group(0),
                                f"총 경력은 만 {years}년"))
    for m in re.finditer(r"(\d+)\s*년(째|간)", text):
        n = int(m.group(1))
        if n in (years, years + 1):
            continue
        if _career_context(text, m):
            sev = "필수"
        elif abs(n - years) <= 2:
            sev = "권장"
        else:
            continue
        out.append(_finding("CAREER_YEARS", sev, doc, m.group(0), f"경력 연수는 만 {years}년(또는 {years + 1}년째)"))
    return out


def _flat(text: str) -> str:
    return re.sub(r"[\s\x00-\x1f\xad()]+", "", text)


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


JD_SECTION = re.compile(r"^#{1,4}\s*(?:주요\s*업무|담당\s*업무|하는\s*일|업무\s*내용)[^\n]*\n(.*?)(?=^#{1,4}\s|\Z)", re.S | re.M)
JD_STOP = {"주요", "업무", "관리", "작성", "수립", "진행", "중인", "본사", "담당", "수행", "대한", "위한", "통한", "관련", "내용",
           "경험", "능력", "보유", "세부", "참석", "운영", "업무가", "개발이", "아닌", "주업무"}
PARTICLE = re.compile(r"(으로|에서|에게|들의|들을|들|을|를|이|가|은|는|의|에|와|과|로|도|만|임)$")
INTRO_MARK = "자기소개서"


def jd_terms(jd_text: str) -> list:
    """공고.md의 주요업무(담당업무·하는 일) 절에서 2자 이상 명사 후보를 나온 순서대로 뽑는다. 절이 없으면 빈 목록."""
    m = JD_SECTION.search(jd_text)
    if not m:
        return []
    out = []
    for tok in re.findall(r"[가-힣A-Za-z]{2,}", m.group(1)):
        if len(tok) > 2:
            tok = PARTICLE.sub("", tok)
        if len(tok) >= 2 and tok not in JD_STOP and tok not in out:
            out.append(tok)
    return out


def split_intro(text: str) -> tuple:
    """이력서 본문과 자기소개서를 첫 '자기소개서' 표시에서 나눈다. 없으면 (전체, '')."""
    i = text.find(INTRO_MARK)
    return (text, "") if i == -1 else (text[:i], text[i:])


def check_jd_coverage(text: str, terms: list, doc, min_ratio: float = 0.4) -> list:
    """공고 업무 용어가 이력서 본문(자기소개서 앞)에 나오는지. 자기소개서에만 있으면 첫인상에서 직무가 안 보인다."""
    if not terms:
        return []
    body, intro = split_intro(text)
    counts = {t: (body.count(t), intro.count(t)) for t in terms}
    in_body = [t for t, (b, _) in counts.items() if b]
    only_intro = [t for t, (b, i) in counts.items() if not b and i]
    summary = ", ".join(f"{t} {b}/{i}" for t, (b, i) in counts.items())
    out = []
    if only_intro:
        out.append(_finding("JD_TERMS_ONLY_IN_INTRO", "권장", doc, ", ".join(only_intro),
                            f"공고 업무 용어가 자기소개서에만 있고 본문에는 0회: {', '.join(only_intro)} (본문/자기소개서: {summary})"))
    ratio = len(in_body) / len(terms)
    if ratio < min_ratio:
        out.append(_finding("JD_COVERAGE_LOW", "권장", doc, f"{len(in_body)}/{len(terms)}",
                            f"공고 업무 용어 {len(terms)}개 중 본문에 나온 것 {len(in_body)}개 ({ratio:.0%}). "
                            f"블록 제목·첫 줄을 공고 용어로 다시 쓸지 검토 (본문/자기소개서: {summary})"))
    return out


def body_segments(path) -> list:
    """HTML 태그 단위 텍스트 조각(8자 이상) 중 자기소개서 앞부분만. 기본본과 같은 문장인지 비교하는 데 쓴다."""
    s = Path(path).read_text(encoding="utf-8")
    s = re.sub(r"<title>.*?</title>", " ", DATA_URI.sub(" ", BLOCKS.sub(" ", COMMENT.sub(" ", s))), flags=re.S)
    out = []
    for seg in TAG.split(s):
        seg = re.sub(r"\s+", " ", _html.unescape(seg)).strip()
        if INTRO_MARK in seg and len(seg) < 30:
            break
        if len(seg) >= 8:
            out.append(seg)
    return out


def check_base_similarity(doc_html, base_html, doc, threshold: float = 0.8) -> list:
    """회사판 본문 조각 중 기본본과 똑같은 비율. 높으면 블록 문장을 공고에 맞추지 않은 것."""
    segs = body_segments(doc_html)
    if not segs:
        return []
    base = set(body_segments(base_html))
    same = sum(1 for x in segs if x in base)
    ratio = same / len(segs)
    if ratio >= threshold:
        return [_finding("BLOCKS_UNCHANGED_FROM_BASE", "권장", doc, f"{same}/{len(segs)}",
                         f"본문 문장의 {ratio:.0%}가 기본본과 같음. 브리프의 직무 거리가 '멂'이면 전면 블록 제목·첫 줄을 공고 용어로 다시 쓴다")]
    return []


def known_companies(applications_dir) -> list:
    out = []
    for d in sorted(Path(applications_dir).glob("*/")):
        f = d / "공고.md"
        if f.is_file():
            try:
                fm, _ = read_frontmatter(f)
                if fm.get("회사"):
                    out.append(str(fm["회사"]))
                    continue
            except ValueError:
                pass
        out.append(d.name.split()[0])
    return out


def lint(career_md, company, docs, claims_md=None, pairs=(), ref=None, fetch=None, jd_md=None, base_html=None) -> list:
    career = load_career(career_md)
    ref = ref or date.today()
    claims = parse_claims(Path(claims_md).read_text(encoding="utf-8")) if claims_md else []
    terms = jd_terms(Path(jd_md).read_text(encoding="utf-8")) if jd_md else []
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
            if "이력서" in d.stem:
                out += check_jd_coverage(t, terms, d.name)
                if base_html:
                    out += check_base_similarity(d, base_html, d.name)
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
    ap.add_argument("--jd", help="공고.md: 주요업무 용어가 이력서 본문에 나오는지 검사")
    ap.add_argument("--base", help="기본 이력서 HTML: 회사판 본문이 기본본과 얼마나 같은지 검사")
    ap.add_argument("docs", nargs="+")
    a = ap.parse_args(argv)
    pairs = [tuple(Path(x) for x in p.split(":", 1)) for p in a.pair]
    fs = lint(a.career, a.company, [Path(d) for d in a.docs], a.claims, pairs, fetch=None if a.offline else _head,
              jd_md=a.jd, base_html=a.base)
    print(json.dumps(fs, ensure_ascii=False, indent=2))
    return 1 if any(f["severity"] == "필수" for f in fs) else 0


if __name__ == "__main__":
    sys.exit(main())
