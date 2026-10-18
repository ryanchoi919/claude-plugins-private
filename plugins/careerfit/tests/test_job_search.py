import json

import pytest

from conftest import FIXTURES
from scripts import job_search as js

S = FIXTURES / "search"
COND = {"keywords": ["데이터 분석"], "exclude": ["인턴"], "career_years": [5, 12], "locations": ["서울", "경기"]}


def read(name):
    return (S / name).read_text(encoding="utf-8")


def test_search_urls_apply_career_filter():
    assert "exp_cd=2&exp_min=5&exp_max=12" in js.search_urls("saramin", "데이터 분석", COND)
    assert "careerType=2" in js.search_urls("jobkorea", "데이터 분석", COND)
    u = js.search_urls("bzpp", "데이터 분석", COND)
    assert "searchStartCareer=5&searchEndCareer=12" in u and "%EB%8D%B0%EC%9D%B4%ED%84%B0" in u
    assert "exp_cd" not in js.search_urls("saramin", "PM", {})
    with pytest.raises(ValueError):
        js.search_urls("wanted", "PM", {})


def test_parse_saramin():
    rs = js.parse_saramin(read("saramin.html"))
    assert len(rs) == 4  # 페이지 안 중복은 filter_and_merge가 지운다
    r = rs[0]
    assert r["id"] == "90000001" and r["company"] == "(주)샘플커머스"
    assert r["url"].endswith("rec_idx=90000001")
    assert (r["location"], r["career"], r["employment"]) == ("서울 강남구", "경력 5~10년", "정규직")
    assert r["deadline"] == "~ 11/15(일)" and r["tags"] == ["데이터분석가", "수요예측"]


def test_parse_jobkorea_picks_main_result_not_ads():
    rs = js.parse_jobkorea(read("jobkorea.html"))
    assert [r["id"] for r in rs] == ["70000001", "70000002"]
    assert rs[0]["url"] == "https://www.jobkorea.co.kr/Recruit/GI_Read/70000001"
    assert rs[0]["deadline"] == "2026-11-15" and rs[0]["career"] == "경력"
    assert rs[0]["location"] == "" and rs[0]["location_hint"] == "역삼,강남구"
    assert rs[1]["career"] == "신입·경력"


def test_parse_bzpp_ignores_templates_and_labels_headhunting():
    rs = js.parse_bzpp(read("bzpp.html"))
    assert [r["id"] for r in rs] == ["BR261001A00001", "BR261001A00002"]
    assert rs[0]["company"] == "(헤드헌팅: 가상 헤드헌터)" and rs[0]["career"] == "10~15년"
    assert rs[0]["tags"] == ["사업전략", "데이터"] and rs[0]["deadline"] == "2026-11-20"
    assert rs[1]["company"] == "(주)가상뷰티" and rs[1]["employment"] == "계약직"


def test_filter_and_merge():
    recs = js.parse_saramin(read("saramin.html")) + js.parse_jobkorea(read("jobkorea.html"))
    for r in recs:
        r["keyword"] = "데이터 분석"
    out = js.filter_and_merge(recs, COND)
    titles = [r["title"] for r in out]
    assert "물류센터 운영 인턴 모집" not in titles          # 제외어
    assert "데이터 분석 매니저" not in titles               # 부산: 지역 밖
    assert "AX 전략기획 매니저" in titles                  # 지역 모르면 남긴다
    assert next(r for r in out if r["id"] == "70000002")["kw_in_title"] is False
    first = out[0]
    assert first["source"] == "saramin" and first["kw_in_title"] is True
    assert first["also_on"] == ["https://www.jobkorea.co.kr/Recruit/GI_Read/70000001"]  # (주)/㈜ 차이 무시
    assert len([r for r in out if r["id"] == "90000001"]) == 1


def test_seen_and_mark(tmp_path):
    seen_path = tmp_path / "seen.json"
    recs = js.parse_bzpp(read("bzpp.html"))
    seen = {}
    js.apply_seen(recs, seen, "2026-10-19")
    assert all(r["new"] for r in recs)
    seen_path.write_text(json.dumps(seen, ensure_ascii=False), encoding="utf-8")
    js.mark(seen_path, "bzpp:BR261001A00002", "제외", "계약직")
    again = js.parse_bzpp(read("bzpp.html"))
    js.apply_seen(again, js.load_seen(seen_path), "2026-10-20")
    assert [r["new"] for r in again] == [False, False]
    assert again[1]["decision"] == "제외"
    with pytest.raises(ValueError):
        js.mark(seen_path, "bzpp:BR261001A00002", "보류")
    with pytest.raises(ValueError):
        js.mark(seen_path, "saramin:1", "관심")


def test_fetch_uses_renderer_for_bzpp_and_reports_empty():
    calls = []

    def getter(url):
        calls.append(("get", url))
        return read("saramin.html") if "saramin" in url else "<html></html>"

    def renderer(url):
        calls.append(("render", url))
        return read("bzpp.html")

    res = js.fetch({**COND, "pages": 2}, getter=getter, renderer=renderer, pause=0)
    assert [k for k, u in calls if "bzpp" in u] == ["render"]          # bzpp는 첫 페이지만, Chrome 렌더
    assert len([u for k, u in calls if "saramin" in u]) == 2
    assert any(e["source"] == "jobkorea" and "0건" in e["error"] for e in res["errors"])
    assert {r["source"] for r in res["postings"]} == {"saramin", "bzpp"}
    assert res["raw_counts"]["saramin:데이터 분석"] == 8


def test_cli_requires_keywords(persona_root, capsys):
    assert js.main(["job_search.py", "urls", str(persona_root / "CAREER.md")]) == 1
    assert "search.keywords" in capsys.readouterr().err


def test_chrome_args_sandboxed_by_default(monkeypatch):
    monkeypatch.delenv("CAREERFIT_CHROME_NO_SANDBOX", raising=False)
    args = js.chrome_args("chrome", "https://www.bzpp.co.kr/x")
    assert "--no-sandbox" not in args and args[-1] == "https://www.bzpp.co.kr/x"
    assert not any(a.startswith("--user-data-dir") for a in args)  # 기본 임시 프로필
    monkeypatch.setenv("CAREERFIT_CHROME_NO_SANDBOX", "1")
    assert "--no-sandbox" in js.chrome_args("chrome", "https://www.bzpp.co.kr/x")
