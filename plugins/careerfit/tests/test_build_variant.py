import json
import re
import subprocess
import sys

import pytest

from conftest import FIXTURES, PLUGIN_ROOT
from scripts import build_variant as B

BASE = (FIXTURES / "deck.html").read_text(encoding="utf-8")
SPEC = {"title": "김하늘_포트폴리오_샘플커머스", "meta": "샘플커머스 AI PM 지원용 포트폴리오",
        "cover_eyebrow": "Portfolio · AI PM", "tagline": "AI로 <b>업무 흐름</b>을 바꿉니다.",
        "closing": "AI 과제를 함께 만들 사람이 필요하시다면 연락 주세요.", "order": [2, 3, 1]}


def cases(h):
    return re.findall(r'<section class="slide v2"><div class="eyebrow">(CASE 0\d)[^<]*</div><h2>([^<]+)</h2>', h)


def toc(h):
    return re.findall(r'<span class="num">(\d\d)</span>\s*<span class="title">([^<]+)</span>', h)


def test_cover_meta_closing():
    h = B.build_variant(BASE, SPEC)
    assert "<title>김하늘_포트폴리오_샘플커머스</title>" in h
    assert 'content="샘플커머스 AI PM 지원용 포트폴리오"' in h
    assert '<div class="eyebrow">Portfolio · AI PM</div>' in h
    assert '<div class="tagline">AI로 <b>업무 흐름</b>을 바꿉니다.</div>' in h
    assert '<div class="sub">AI 과제를 함께 만들 사람이 필요하시다면 연락 주세요.</div>' in h


def test_reorder_and_renumber_cases_and_toc():
    h = B.build_variant(BASE, SPEC)
    assert cases(h) == [("CASE 01", "문의 분류 에이전트"), ("CASE 02", "채널 수익성"), ("CASE 03", "재고 예측")]
    assert toc(h) == [("01", "문의 분류 에이전트"), ("02", "채널 수익성"), ("03", "재고 예측")]


def test_cross_references_remapped():
    h = B.build_variant(BASE, SPEC)
    assert "CASE 01의 분류 결과를 활용" in h  # 재고(이제 03)가 가리키던 분류(02→01)
    assert "CASE 03 참고" in h               # 채널(이제 02)이 가리키던 재고(01→03)


def test_multiline_toc_rows_with_nested_divs():
    base = BASE.replace(
        '<div class="toc-row"><span class="num">01</span><span class="title">재고 예측</span></div>',
        '<div class="toc-row">\n      <span class="num">01</span>\n      <span class="title">재고 예측</span>\n'
        '      <div class="stat"><div>40개 → 22개</div></div>\n    </div>')
    h = B.build_variant(base, SPEC)
    assert toc(h) == [("01", "문의 분류 에이전트"), ("02", "채널 수익성"), ("03", "재고 예측")]
    assert h.count('<div class="toc-row">') == 3 and "40개 → 22개" in h


def test_no_order_keeps_cases():
    spec = {k: v for k, v in SPEC.items() if k != "order"}
    assert [c[1] for c in cases(B.build_variant(BASE, spec))] == ["재고 예측", "문의 분류 에이전트", "채널 수익성"]


def test_bad_order():
    with pytest.raises(ValueError, match="order"):
        B.build_variant(BASE, {**SPEC, "order": [1, 1, 2]})


def test_cli(tmp_path):
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps(SPEC, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "o.html"
    r = subprocess.run([sys.executable, str(PLUGIN_ROOT / "scripts" / "build_variant.py"),
                        str(FIXTURES / "deck.html"), str(spec), str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "샘플커머스" in out.read_text(encoding="utf-8")
