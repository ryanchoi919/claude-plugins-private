import json
import subprocess
import sys

from conftest import PLUGIN_ROOT
from scripts import lint_docs as L

JD = """# 원문
## 주요업무
- 진행 중인 프로젝트 총괄 관리 (일정, 산출물, 리스크)
- 발주처, 협력사 커뮤니케이션과 요구사항 변경 관리
## 자격요건
- 관련 경험 5년
"""


def rules(fs):
    return [f["rule"] for f in fs]


def test_jd_terms_from_main_duties_only():
    terms = L.jd_terms(JD)
    for t in ("프로젝트", "일정", "산출물", "리스크", "발주처", "협력사", "요구사항", "변경"):
        assert t in terms
    assert "관리" not in terms and "경험" not in terms  # 불용어, 자격요건 절은 제외
    assert L.jd_terms("# 공고\n주요업무 절 없음") == []


def test_terms_only_in_intro_flagged():
    text = "요약 매출 분석과 영업 전략 수립 경력 영업 회의 운영 자기소개서 01 프로젝트 일정과 산출물, 리스크를 관리했습니다"
    fs = L.check_jd_coverage(text, L.jd_terms(JD), "이력서.html")
    assert "JD_TERMS_ONLY_IN_INTRO" in rules(fs)
    assert "JD_COVERAGE_LOW" in rules(fs)
    assert all(f["severity"] == "권장" for f in fs)


def test_terms_in_body_pass():
    text = ("시스템 구축 프로젝트 일정·산출물·리스크 관리, 발주처·협력사 요구사항 변경 관리, 커뮤니케이션 총괄 "
            "자기소개서 01 같은 이야기")
    assert L.check_jd_coverage(text, L.jd_terms(JD), "이력서.html") == []


def _html(path, lines):
    path.write_text("<title>t</title>" + "".join(f"<li>{x}</li>" for x in lines)
                    + "<h2>자기소개서</h2><p>자기소개서 본문은 비교하지 않는 긴 문장입니다</p>", encoding="utf-8")
    return path


def test_base_similarity(tmp_path):
    base = ["재고 예측 대시보드 구축과 운영", "채널 수익성 분석 보고서 작성", "고객 문의 자동 분류 에이전트 구축",
            "팀 반복 업무 자동화 표준화", "분기별 사업계획 수립과 보고"]
    b = _html(tmp_path / "base.html", base)
    same = _html(tmp_path / "김하늘_이력서_샘플.html", list(reversed(base)))
    assert "BLOCKS_UNCHANGED_FROM_BASE" in rules(L.check_base_similarity(same, b, "d"))
    changed = _html(tmp_path / "김하늘_이력서_샘플2.html",
                    ["프로젝트 범위·일정 관리와 운영 이관", "발주처 요구사항 변경 영향 분석", base[2],
                     "중간보고 자료 작성과 보고", "협력사 일정 조율과 산출물 검토"])
    assert L.check_base_similarity(changed, b, "d") == []


def test_cli_jd_and_base(persona_root, tmp_path):
    jd = tmp_path / "공고.md"
    jd.write_text(JD, encoding="utf-8")
    base = _html(tmp_path / "base.html", ["매출 분석과 영업 전략 수립", "영업 회의 자료 준비와 운영"])
    doc = tmp_path / "김하늘_이력서_샘플커머스.html"
    doc.write_text("<title>김하늘_이력서_샘플커머스</title><li>매출 분석과 영업 전략 수립</li><li>영업 회의 자료 준비와 운영</li>"
                   "<h2>자기소개서</h2><p>프로젝트 일정과 산출물, 리스크를 관리했습니다</p>", encoding="utf-8")
    r = subprocess.run([sys.executable, str(PLUGIN_ROOT / "scripts" / "lint_docs.py"),
                        "--career", str(persona_root / "CAREER.md"), "--company", "샘플커머스", "--offline",
                        "--jd", str(jd), "--base", str(base), str(doc)], capture_output=True, text=True)
    found = rules(json.loads(r.stdout))
    for rule in ("JD_TERMS_ONLY_IN_INTRO", "JD_COVERAGE_LOW", "BLOCKS_UNCHANGED_FROM_BASE"):
        assert rule in found, r.stdout
