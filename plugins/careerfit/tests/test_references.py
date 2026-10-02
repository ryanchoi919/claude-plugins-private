import pytest

from conftest import PLUGIN_ROOT, personal_words

R = PLUGIN_ROOT / "references"
REQUIRED = {
    "writing-rules.md": ["저는", "em dash", "두괄식", "음슴체", "스케어쿼트", "입사 후 포부"],
    "attribution-and-facts.md": ["귀속", "[확인 필요", "의사결정", "범위 재정의", "최초", "시간 순서"],
    "confidentiality.md": ["내부 시스템", "실명", "금액", "HTML 주석", "사진"],
    "filenames.md": ["{name}_{doc}_{company}", "<title>", "(주)"],
    "jd-capture.md": ["GI_Read", "GI_Read_Comt_Ifrm", "이미지", "제출 서류"],
    "korean-career-description-guide.md": ["문제 → 행동 → 결과", "A4 1~3장", "출처"],
    "schemas.md": ["CAREER.md", "claims.md", "insights.md", "준비 중", "지원 취소", "영역", "임팩트"],
}


@pytest.mark.parametrize("name,words", REQUIRED.items())
def test_reference_contains(name, words):
    s = (R / name).read_text(encoding="utf-8")
    for w in words:
        assert w in s, f"{name}에 '{w}' 없음"


@pytest.mark.parametrize("name", REQUIRED)
def test_reference_no_personal_data(name):
    s = (R / name).read_text(encoding="utf-8")
    for w in personal_words():
        assert w not in s
