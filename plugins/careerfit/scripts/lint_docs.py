"""제출 서류 린트: 금지어·타사명·숨은 텍스트·title·주장 원장·기간·버전·링크."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))

import html as _html
import re
from pathlib import Path

from pypdf import PdfReader

from scripts.config import normalize_company

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
        if not name or name == target:
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
