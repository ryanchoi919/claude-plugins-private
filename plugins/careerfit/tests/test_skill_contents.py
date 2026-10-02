import pytest

from conftest import PLUGIN_ROOT

REQUIRED = {
    "brief": ["## 포지션 해석", "## 적합도 매트릭스", "## 이야기 설계", "## 약점과 대응 논리", "## 빈틈 질문",
              "## 인사이트 반영", "## 서류 계획", "승인: true", "claims.md", "본인 확인"],
}


@pytest.mark.parametrize("skill,words", REQUIRED.items())
def test_skill_contains(skill, words):
    s = (PLUGIN_ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    for w in words:
        assert w in s, f"{skill}에 '{w}' 없음"
