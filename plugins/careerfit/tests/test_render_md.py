import subprocess
import sys

from conftest import FIXTURES, PLUGIN_ROOT
from scripts import render_md

MD = (FIXTURES / "경력기술서.md").read_text(encoding="utf-8")


def _render(**kw):
    return render_md.render(MD, title="김하늘_경력기술서_샘플커머스", target="샘플커머스 AI PM 지원",
                            name="김하늘", contact="haneul@example.com · 010-0000-0000", **kw)


def test_header_and_title():
    h = _render()
    assert "<title>김하늘_경력기술서_샘플커머스</title>" in h
    assert "<small>김하늘</small>" in h and "haneul@example.com" in h
    assert "{{" not in h


def test_project_numbering_and_fit_table():
    h = _render()
    assert "프로젝트 1 · 재고 예측 대시보드 구축" in h
    assert "프로젝트 2 · 고객 문의 자동 분류 에이전트" in h
    assert '<table class="fit">' in h and "<th>근거</th>" in h


def test_kpi_chips_todo_and_company_section():
    h = _render()
    assert '<div class="kpi"><span>품절 45% 감소</span><span>2개 물류센터 적용</span></div>' in h
    assert '<mark class="todo">[확인 필요: 이전 월평균 품절 건수]</mark>' in h
    assert '<div class="job"><div class="job-head"><h3>(주)가상물산 · 데이터팀 매니저</h3>' in h
    assert '<div class="item"><div class="t">채널 수익성 분석 · 2018</div>' in h


def test_callout_and_frontmatter_not_rendered():
    h = _render()
    assert "작성 기준" not in h and "모드:" not in h


def test_break_projects_flag():
    assert ".proj + .proj{ break-before:page; }" in _render(break_projects=True)
    assert ".proj + .proj{ break-before:page; }" not in _render()


def test_cli(tmp_path):
    out = tmp_path / "o.html"
    r = subprocess.run([sys.executable, str(PLUGIN_ROOT / "scripts" / "render_md.py"), str(FIXTURES / "경력기술서.md"),
                        str(out), "--title", "T", "--target", "X 지원", "--name", "김하늘", "--contact", "c"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "<title>T</title>" in out.read_text(encoding="utf-8")
