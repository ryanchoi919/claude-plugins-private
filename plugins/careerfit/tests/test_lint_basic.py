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


def test_target_company_short_name_not_flagged():
    fs = L.find_other_companies("CJ올리브영 AX 전략 지원", "CJ올리브영", ["올리브영", "씨제이올리브영"], "r.html")
    assert fs == []


def test_mechanical_jd_label(tmp_path):
    t = L.visible_text(_html(tmp_path, "<h2>공고 대응</h2><th>공고 요구사항 (원문 발췌)</th><th>대응 경험</th>"
                                       "<h2>담당할 업무와 관련 경험</h2>"))
    fs = [f for f in L.find_banned(t, "r.html") if f["rule"] == "MECHANICAL_JD_LABEL"]
    assert len(fs) == 3 and all(f["severity"] == "권장" for f in fs)


def test_jd_quote_and_causative(tmp_path):
    t = L.visible_text(_html(tmp_path, "<p>크럭스데이타는 공고에 “주 업무가 개발이 아닌 사업관리”라고 적었습니다. "
                                       "기관의 데이터를 모아 보게 하는 사업입니다. 다음 보고에서 확인되게 하겠습니다. "
                                       "필요하다는 것을 알게 됐습니다.</p>"))
    fs = L.find_banned(t, "r.html")
    assert [f["rule"] for f in fs].count("JD_QUOTE") == 1
    assert [f["rule"] for f in fs].count("CAUSATIVE_PHRASE") == 2  # "알게 됐습니다"는 잡지 않는다


def test_ai_tells(tmp_path):
    t = L.visible_text(_html(tmp_path, "<p>운영에 있어서 경쟁력을 가지고 있습니다. 판단되어진 결과가 시스템에 의해 생성됐고, "
                                       "현장에서의 역할을 맡았지만, 결론적으로 시사하는 바가 컸습니다. "
                                       "이제 도약할 때입니다. 단순한 보고를 넘어 실행까지 맡았습니다.</p>"))
    fs = L.find_banned(t, "r.html")
    r = rules(fs)
    assert r.count("TRANSLATIONESE") == 5
    assert r.count("AI_CLICHE") == 4
    assert all(f["severity"] == "권장" for f in fs if f["rule"] in ("TRANSLATIONESE", "AI_CLICHE"))


def test_connective_commas_counted_per_doc():
    two = "생성됐고, 역할을 맡았지만, 끝냈습니다."
    assert L.check_connective_commas(two, "r.html") == []
    assert L.check_connective_commas(two + " 정의하고, 풀어서, 운영했습니다.", "r.html") == []  # 5회 미만
    fs = L.check_connective_commas(two + " 정의하고, 풀어서, 검증하며, 공유했고, 운영했습니다.", "r.html")
    assert rules(fs) == ["CONNECTIVE_COMMA"] and "6회" in fs[0]["message"] and fs[0]["severity"] == "권장"


def test_ai_tells_no_false_positive(tmp_path):
    t = L.visible_text(_html(tmp_path, "<p>선정되어 지원금을 받았습니다. 앞으로의 계획을 세웠습니다. 하지만, 그리고, 그러면서, "
                                       "재고, 광고, 최고 수준의 물류. 재고 회전 개선 후 손실 축소.</p>"))
    r = rules(L.find_banned(t, "r.html")) + rules(L.check_connective_commas(t, "r.html"))
    assert not {"TRANSLATIONESE", "CONNECTIVE_COMMA", "AI_CLICHE"} & set(r)
