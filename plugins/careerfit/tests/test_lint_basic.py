from scripts import lint_docs as L


def _html(tmp_path, body, title="김하늘_이력서_샘플커머스", name="r.html"):
    p = tmp_path / name
    p.write_text(f"<title>{title}</title><style>.a::before{{content:'—'}}</style>{body}", encoding="utf-8")
    return p


def rules(fs):
    return [f["rule"] for f in fs]


def test_em_dash_and_first_person(tmp_path):
    t = L.visible_text(_html(tmp_path, "<p>성과 — 저는 이렇게 했습니다. 재고 통제가 필요했음.</p>"))
    fs = L.find_banned(t, "r.html")
    assert rules(fs).count("EM_DASH") == 1
    assert rules(fs).count("FIRST_PERSON") == 1  # "통제가"는 오탐하지 않는다


def test_comments_scripts_datauri_ignored(tmp_path):
    body = ("<!-- 주석 — 12.6% --><script>var a='—';</script>"
            "<img src='data:image/jpeg;base64,/9j/4AAQ—SkZJRg=='><p>본문 문장</p>")
    t = L.visible_text(_html(tmp_path, body))
    assert "—" not in t and "12.6" not in t and "base64" not in t
    assert "본문 문장" in t


def test_hidden_comment_flagged_separately(tmp_path):
    p = _html(tmp_path, "<!-- 내부 메모: 실제 매출 12억 --><p>본문</p>")
    assert L.hidden_text(p) == ["내부 메모: 실제 매출 12억"]
    assert rules(L.check_hidden(p)) == ["HIDDEN_COMMENT"]


def test_other_company_variants(tmp_path):
    t = L.visible_text(_html(tmp_path, "<p>(주)샘플커머스 지원. 주식회사 가상 컴퍼니의 AX팀은...</p>"))
    fs = L.find_other_companies(t, "샘플커머스", ["(주)샘플커머스", "㈜가상컴퍼니", "다른회사"], "r.html")
    assert rules(fs) == ["OTHER_COMPANY"]
    assert "가상컴퍼니" in fs[0]["message"]


def test_title_mismatch(tmp_path):
    p = _html(tmp_path, "<p>x</p>", title="김하늘 이력서")
    assert rules(L.check_title(p, "김하늘_이력서_샘플커머스")) == ["TITLE_MISMATCH"]
    assert L.check_title(_html(tmp_path, "<p>x</p>", name="ok.html"), "김하늘_이력서_샘플커머스") == []


def test_markdown_frontmatter_stripped(tmp_path):
    p = tmp_path / "경력기술서.md"
    p.write_text("---\nmodified: 2026-10-02T09:00:00+09:00\n---\n# 경력기술서\n본문 — 끝\n", encoding="utf-8")
    t = L.visible_text(p)
    assert "modified" not in t and "본문" in t
    assert rules(L.find_banned(t, "md")) == ["EM_DASH"]
