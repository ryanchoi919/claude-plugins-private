from datetime import date

import pytest

from scripts import config


def test_load_career_paths(persona_root):
    c = config.load_career(persona_root / "CAREER.md")
    assert c.name == "김하늘"
    assert c.paths["projects"] == persona_root / "projects"
    assert c.paths["insights"] == persona_root / "insights.md"
    assert c.career_start == date(2015, 3, 1)
    assert c.market == "KR"
    assert "## 고정 표기" in c.body


def test_paths_with_korean_and_spaces(persona_root):
    c = config.load_career(persona_root / "CAREER.md")
    assert c.paths["applications"] == persona_root / "지원 이력"


def test_defaults_when_paths_missing(tmp_path):
    p = tmp_path / "CAREER.md"
    p.write_text("---\nname: 이도윤\n---\n", encoding="utf-8")
    c = config.load_career(p)
    assert c.paths["applications"] == tmp_path / "applications"
    assert c.filename_pattern == "{name}_{doc}_{company}"
    assert c.career_start is None


def test_missing_name_raises(tmp_path):
    p = tmp_path / "CAREER.md"
    p.write_text("---\npaths: {}\n---\n", encoding="utf-8")
    with pytest.raises(ValueError, match="name"):
        config.load_career(p)


def test_missing_frontmatter_raises(tmp_path):
    p = tmp_path / "CAREER.md"
    p.write_text("# 설정\n", encoding="utf-8")
    with pytest.raises(ValueError, match="frontmatter"):
        config.load_career(p)


@pytest.mark.parametrize("raw", ["(주)샘플커머스", "㈜샘플커머스", "주식회사 샘플 커머스", " 샘플커머스 "])
def test_normalize_company_variants(raw):
    assert config.normalize_company(raw) == "샘플커머스"


def test_submission_name(persona_root):
    c = config.load_career(persona_root / "CAREER.md")
    assert config.submission_name(c, "이력서", "(주)샘플커머스") == "김하늘_이력서_샘플커머스.pdf"
    assert config.submission_name(c, "포트폴리오") == "김하늘_포트폴리오.pdf"
    assert config.submission_name(c, "경력기술서", "샘플커머스", ext=None) == "김하늘_경력기술서_샘플커머스"
    with pytest.raises(ValueError):
        config.submission_name(c, "자기소개서", "샘플커머스")


def test_statuses_exact():
    assert config.STATUSES == ("준비 중", "서류 제출", "서류 전형", "서류 탈락", "면접", "최종 합격", "불합격", "지원 취소")
