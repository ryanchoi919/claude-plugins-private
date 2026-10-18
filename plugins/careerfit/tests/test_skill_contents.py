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
    "setup": ["## 처음 실행", "references/schemas.md", "영역", "임팩트", "기본본 모드", "본인 확인", "update",
              "references/career-interview.md", "재료도 연결 도구도 없음", "## 인터뷰 진행", "MECE", "3~5문항", "search"],
    "search": ["references/job-sources.md", "scripts/job_search.py fetch", "job_search.py mark", "seen.json",
               "처음 실행", "자동", "career_years", "status.py scan", "## 경력 방향", "insights.md", "15건",
               "## 조건 조정 제안", "apply", "## 저장 후 처리"],
    "update": ["references/schemas.md", "scripts/config.py", "setup", "기본본 갱신 필요", "지우지 말고", "본인 확인",
               "기본본 모드", "build_variant", "sign_only_last_page", "chrome.py shot", "status.py scan", "## 저장 후 처리"],
    "review": ["기본본 갱신 필요", "검수 결과 ("],
    "track": ["status.py set", "status.py scan", "준비 중", "지원 취소", "insights.md", "가설", "# 결과 ("],
    "helper": ["setup", "update", "search", "apply", "track", "status.py scan", "[확인 필요]", "1~3개"],
}


@pytest.mark.parametrize("skill,words", REQUIRED.items())
def test_skill_contains(skill, words):
    s = (PLUGIN_ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    for w in words:
        assert w in s, f"{skill}에 '{w}' 없음"
