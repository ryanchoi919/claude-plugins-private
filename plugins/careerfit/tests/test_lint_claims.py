from datetime import date

from conftest import FIXTURES
from scripts import lint_docs as L

CLAIMS = L.parse_claims((FIXTURES / "claims.md").read_text(encoding="utf-8"))


def rules(fs):
    return [f["rule"] for f in fs]


def test_parse_claims():
    assert [c.id for c in CLAIMS] == ["C01", "C02"]
    assert CLAIMS[0].forbidden == ["최대 50% 감소"]
    assert CLAIMS[1].forbidden == ["완전 자동", "실시간"]
    assert "팀장" in CLAIMS[0].attribution


def test_forbidden_expression():
    fs = L.check_claims("품절 품목이 최대 50% 감소했음.", CLAIMS, "d")
    assert "FORBIDDEN_EXPRESSION" in rules(fs)


def test_number_not_in_claims():
    fs = L.check_claims("문의 120건 분류, 응답 시간 30% 단축", CLAIMS, "d")
    assert rules(fs) == ["NUMBER_NOT_IN_CLAIMS"]
    assert "30%" in fs[0]["message"]


def test_number_format_variants_match_claims():
    assert L.check_claims("문의 120 건을 분류, 품절 40개 → 22개, 45 % 감소", CLAIMS, "d") == []
    claims = L.parse_claims("| C09 | 요청 16,376부 중 12.6% | 16,376부, 12.6% | n | 본인 | |")
    assert L.check_claims("요청 16376부 중 12.6 %", claims, "d") == []


def test_period_two_months_vs_36_days():
    fs = L.check_periods("2개월간(2026.06.04–07.09) 운영", "d")
    assert rules(fs) == ["PERIOD_MISMATCH"]


def test_period_ok_cases():
    assert L.check_periods("약 5주간(2026.06.04–07.09) 운영", "d") == []
    assert L.check_periods("3개월간(2026.06.29–09.29) 지사 요청", "d") == []
    assert L.check_periods("약 12주간(2025.01.06–2025.03.31) 운영", "d") == []


def test_total_years():
    ref = date(2026, 10, 2)
    start = date(2014, 9, 1)
    assert rules(L.check_total_years("11년째 콘텐츠 산업에서", start, ref, "d")) == ["CAREER_YEARS"]
    assert L.check_total_years("총 12년, 12년간 콘텐츠 산업에서", start, ref, "d") == []
    assert rules(L.check_total_years("총 13년", start, ref, "d")) == ["CAREER_YEARS"]


def test_project_duration_years_not_flagged():
    assert L.check_total_years("2년간 운영한 시스템, 3년째 유지", date(2014, 9, 1), date(2026, 10, 2), "d") == []
