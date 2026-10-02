"""최종 리뷰 지적 사항 재현 테스트."""
import os
from datetime import date

import pytest

from conftest import FIXTURES
from scripts import chrome, config, lint_docs as L, status


def rules(fs):
    return [f["rule"] for f in fs]


def sev(fs, rule):
    return [f["severity"] for f in fs if f["rule"] == rule]


# C1: Chrome+나눔 PDF의 U+0001 공백·U+00AD 때문에 갓 렌더한 PDF가 버전 불일치로 잡힘
def test_version_check_on_real_render(tmp_path, chrome_or_skip):
    from scripts import render_md
    html = tmp_path / "cd.html"
    html.write_text(render_md.render((FIXTURES / "경력기술서.md").read_text(encoding="utf-8"), "T", "X 지원",
                                     "김하늘", "haneul@example.com"), encoding="utf-8")
    pdf = chrome.render_pdf(html, tmp_path / "cd.pdf", chrome_or_skip)
    assert L.check_version(html, pdf) == []
    assert "\x01" not in L.visible_text(pdf)


# I1: 짧은 경력에서 프로젝트 기간이 경력 연수 필수 오류로 잡힘
def test_project_duration_short_career_not_required():
    start, ref = date(2021, 3, 1), date(2026, 10, 2)  # 만 5년
    fs = L.check_total_years("3년간 운영한 대시보드, 총 3년 운영", start, ref, "d")
    assert "필수" not in [f["severity"] for f in fs]


def test_career_context_still_required():
    start, ref = date(2014, 9, 1), date(2026, 10, 2)
    assert sev(L.check_total_years("11년째 콘텐츠 산업에서", start, ref, "d"), "CAREER_YEARS") == ["필수"]
    assert sev(L.check_total_years("경력 요약 (총 13년)", start, ref, "d"), "CAREER_YEARS") == ["필수"]


# I2: 짧은·영문 회사명, 띄어쓰기 제거로 인한 오탐
def test_other_company_no_false_positive_inside_words():
    fs = L.find_other_companies("SKU 단위 재고 관리, 토스트 굽기, 다른 회사와 협업", "샘플커머스",
                                ["SK", "토스", "다른회사"], "d")
    assert "필수" not in [f["severity"] for f in fs]


def test_other_company_real_hits_still_found():
    fs = L.find_other_companies("SK 하이닉스 지원. 토스에서 일하고 싶습니다", "샘플커머스", ["SK", "토스"], "d")
    assert len(fs) == 2


def test_known_companies_prefers_frontmatter(tmp_path):
    d = tmp_path / "CJ올리브영 AX 전략"
    d.mkdir()
    (d / "공고.md").write_text("---\n회사: 씨제이올리브영\n---\n", encoding="utf-8")
    assert L.known_companies(tmp_path) == ["씨제이올리브영"]


# I3: Chrome 실패 시 오래된 PDF를 성공으로 보고
def test_render_pdf_failure_not_masked_by_stale_file(tmp_path):
    fake = tmp_path / "chrome"
    fake.write_text("#!/bin/sh\necho boom >&2\nexit 1\n")
    fake.chmod(0o755)
    html = tmp_path / "a.html"
    html.write_text("<p>x</p>", encoding="utf-8")
    stale = tmp_path / "a.pdf"
    stale.write_bytes(b"%PDF-old")
    with pytest.raises(RuntimeError, match="boom"):
        chrome.render_pdf(html, stale, str(fake))


# I4: macOS Playwright 캐시
def test_macos_playwright_cache(tmp_path, monkeypatch):
    monkeypatch.delenv("CAREERFIT_CHROME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("PATH", str(tmp_path / "nobin"))
    exe = (tmp_path / "Library/Caches/ms-playwright/chromium-1300/chrome-mac-arm64"
           / "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing")
    exe.parent.mkdir(parents=True)
    exe.write_text("")
    assert chrome.find_chrome() == str(exe)


# I5: 남은 자리표시자
def test_placeholders_flagged():
    t = "[확인 필요: 이전 건수] 그리고 CASE 01 · [회사] · [기간], 이름 {{NAME}}"
    fs = L.find_banned(t, "d")
    assert rules(fs).count("PLACEHOLDER") == 4
    assert set(sev(fs, "PLACEHOLDER")) == {"필수"}


def test_ordinary_brackets_not_placeholder():
    assert "PLACEHOLDER" not in rules(L.find_banned("[참고] 2024년 [Python] 사용", "d"))


# M1: 깨진 YAML 하나가 전체를 멈춤
def test_bad_yaml_does_not_crash(tmp_path):
    d = tmp_path / "옛 공고"
    d.mkdir()
    (d / "공고.md").write_text("---\n직무: 데이터: 커머스\n---\n", encoding="utf-8")
    with pytest.raises(ValueError, match="옛 공고"):
        config.read_frontmatter(d / "공고.md")
    assert status.scan(tmp_path)[0]["status"] is None
    assert L.known_companies(tmp_path) == ["옛"]


# M3: 이력서에 흔한 기호가 이모지 필수로 잡힘
def test_common_symbols_not_emoji():
    assert "EMOJI" not in rules(L.find_banned("✓ 완료 ★ 핵심 ☎ 연락", "d"))
    assert "EMOJI" in rules(L.find_banned("성과 🚀", "d"))


# M4: 없는 날짜가 린트를 멈춤
def test_impossible_date_reported_not_crash():
    assert rules(L.check_periods("2개월간(2024.02.30–04.30)", "d")) == ["PERIOD_MISMATCH"]
