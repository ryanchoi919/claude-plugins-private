import re

import pytest

from conftest import PLUGIN_ROOT, personal_words
from scripts import build_variant

T = PLUGIN_ROOT / "templates"


@pytest.mark.parametrize("name", ["resume.html", "career-description.html", "portfolio.html"])
def test_no_personal_data(name):
    s = (T / name).read_text(encoding="utf-8")
    for w in personal_words():
        assert w not in s, f"{name}에 개인정보 '{w}'"
    assert "fonts.googleapis" not in s
    assert "NanumGothic" in s
    assert "—" not in s
    assert "base64," not in s


def test_resume_markers_and_a4():
    s = (T / "resume.html").read_text(encoding="utf-8")
    for m in ("{{TITLE}}", "{{META}}", "{{NAME}}", "{{CONTACT}}", "{{TAGLINE}}", "size: A4", "break-inside:avoid-page"):
        assert m in s
    assert s.count('class="intro-item') == 3
    assert re.search(r"\d+\.\d+%", s) is None  # 예시 성과 수치가 남지 않음


def test_portfolio_contract_roundtrip():
    s = (T / "portfolio.html").read_text(encoding="utf-8")
    assert "size: 297mm 167mm" in s or "size:297mm 167mm" in s
    n = s.count('<section class="slide v2">')
    assert n >= 2
    out = build_variant.build_variant(s, {"title": "X", "meta": "M", "tagline": "T", "closing": "C",
                                          "order": list(range(n, 0, -1))})
    assert "<title>X</title>" in out and '<div class="sub">C</div>' in out
    assert re.findall(r'<div class="eyebrow">CASE (\d\d)', out) == [f"{i:02d}" for i in range(1, n + 1)]
