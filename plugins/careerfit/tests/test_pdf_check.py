import pytest

from scripts import chrome, pdf_check

A4 = "<style>@page{size:A4;margin:14mm}body{font-family:'NanumGothic'}.pb{break-after:page}</style>"


def _pdf(tmp_path, body, chrome_path, name="d"):
    html = tmp_path / f"{name}.html"
    html.write_text(A4 + body, encoding="utf-8")
    return chrome.render_pdf(html, tmp_path / f"{name}.pdf", chrome_path)


def test_space_ratio():
    assert pdf_check.space_ratio("가 나 다") == pytest.approx(2 / 5)
    assert pdf_check.space_ratio("") == 0.0


def test_a4_ok(tmp_path, chrome_or_skip):
    p = _pdf(tmp_path, "<p>" + "경력 요약 문장입니다. " * 40 + "</p>", chrome_or_skip)
    r = pdf_check.check_pdf(p, "A4")
    assert r["pages"] == 1
    assert abs(r["width_mm"] - 209.9) < 1.5 and abs(r["height_mm"] - 297.0) < 1.5
    assert all(f.startswith("Nanum") for f in r["fonts"])
    assert not [x for x in r["problems"] if x["severity"] == "필수"]


def test_sign_only_last_page(tmp_path, chrome_or_skip):
    body = "<p class='pb'>" + "본문 " * 50 + "</p><p>위 기재 사항은 사실과 다름없음을 확인합니다. 작성자: 김하늘</p>"
    r = pdf_check.check_pdf(_pdf(tmp_path, body, chrome_or_skip), "A4")
    assert r["sign_only_last_page"] is True
    assert "PDF_SIGN_ONLY_PAGE" in [x["rule"] for x in r["problems"]]


def test_blank_page_and_max_pages(tmp_path, chrome_or_skip):
    body = "<p class='pb'>첫 쪽</p><div class='pb'>&nbsp;</div><p>" + "셋째 쪽 내용입니다 " * 3 + "</p>"
    r = pdf_check.check_pdf(_pdf(tmp_path, body, chrome_or_skip), "A4", max_pages=2)
    rules = [x["rule"] for x in r["problems"]]
    assert "PDF_BLANK_PAGE" in rules and "PDF_MAX_PAGES" in rules


def test_wrong_size_flagged(tmp_path, chrome_or_skip):
    html = tmp_path / "s.html"
    html.write_text("<style>@page{size:297mm 167mm;margin:0}</style><p>슬라이드</p>", encoding="utf-8")
    r = pdf_check.check_pdf(chrome.render_pdf(html, tmp_path / "s.pdf", chrome_or_skip), "A4")
    assert "PDF_SIZE" in [x["rule"] for x in r["problems"]]


def test_ats_spacing_flag(tmp_path, chrome_or_skip):
    p = _pdf(tmp_path, "<p>" + "띄어쓰기없이붙어있는문장" * 30 + "</p>", chrome_or_skip)
    assert "PDF_ATS_SPACING" in [x["rule"] for x in pdf_check.check_pdf(p, "A4")["problems"]]
