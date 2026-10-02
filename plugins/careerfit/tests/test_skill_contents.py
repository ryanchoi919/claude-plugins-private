import pytest

from conftest import PLUGIN_ROOT

REQUIRED = {
    "brief": ["## 포지션 해석", "## 적합도 매트릭스", "## 이야기 설계", "## 약점과 대응 논리", "## 빈틈 질문",
              "## 인사이트 반영", "## 서류 계획", "승인: true", "claims.md", "본인 확인"],
    "write-resume": ["승인: true", "scripts/chrome.py", "scripts/pdf_check.py", "submission_name", "기본본 모드", "templates/resume.html"],
    "write-career-description": ["scripts/render_md.py", "--break-projects", "--max-pages 3", "[확인 필요]", "심층형",
                                 "공고 요구사항 (원문 발췌) | 대응 경험 | 근거", "기본본 모드"],
    "write-portfolio": ["scripts/build_variant.py", "--kind slide", "order", "결과 지표만", "기본본 모드", "templates/portfolio.html"],
    "apply": ["references/jd-capture.md", "scripts/status.py", "준비 중", "brief", "review", "## 저장 후 처리", "setup"],
}


@pytest.mark.parametrize("skill,words", REQUIRED.items())
def test_skill_contains(skill, words):
    s = (PLUGIN_ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    for w in words:
        assert w in s, f"{skill}에 '{w}' 없음"
