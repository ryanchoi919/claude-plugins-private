import json
import subprocess
import sys

from conftest import FIXTURES, PLUGIN_ROOT
from scripts import lint_docs as L


def rules(fs):
    return [f["rule"] for f in fs]


def test_check_links_injected_fetch():
    t = "포트폴리오 https://example.com/ok 와 https://example.com/dead 그리고 https://claude.ai/artifact/AbC"
    codes = {"https://example.com/ok": 200, "https://example.com/dead": 404, "https://claude.ai/artifact/AbC": 200}
    fs = L.check_links(t, "d", fetch=lambda u: codes[u])
    assert sorted(rules(fs)) == ["ARTIFACT_LINK", "LINK_BROKEN"]


def test_known_companies(persona_root):
    d = persona_root / "지원 이력" / "샘플커머스 AI PM"
    d.mkdir(parents=True)
    (d / "공고.md").write_text("---\n회사: (주)샘플커머스\n상태: 준비 중\n---\n", encoding="utf-8")
    e = persona_root / "지원 이력" / "다른회사 데이터 분석가"
    e.mkdir()
    (e / "공고.md").write_text("---\n상태: 서류 탈락\n---\n", encoding="utf-8")
    ks = L.known_companies(persona_root / "지원 이력")
    assert "(주)샘플커머스" in ks and "다른회사" in ks


def test_version_mismatch(tmp_path, chrome_or_skip):
    from scripts import chrome
    html = tmp_path / "a.html"
    html.write_text("<style>@page{size:A4}</style><p>" + "첫 번째 버전의 자기소개서 문장입니다. " * 20 + "</p>", encoding="utf-8")
    pdf = chrome.render_pdf(html, tmp_path / "a.pdf", chrome_or_skip)
    assert L.check_version(html, pdf) == []
    html.write_text("<style>@page{size:A4}</style><p>" + "완전히 다른 두 번째 버전으로 고쳐 쓴 내용입니다. " * 20 + "</p>", encoding="utf-8")
    assert "VERSION_MISMATCH" in rules(L.check_version(html, pdf))


def test_cli_exit_code_and_json(persona_root, tmp_path):
    doc = tmp_path / "김하늘_이력서_샘플커머스.html"
    doc.write_text("<title>김하늘_이력서_샘플커머스</title><p>저는 최대 50% 감소를 이뤘습니다 — 총 9년</p>", encoding="utf-8")
    r = subprocess.run([sys.executable, str(PLUGIN_ROOT / "scripts" / "lint_docs.py"),
                        "--career", str(persona_root / "CAREER.md"), "--company", "샘플커머스",
                        "--claims", str(FIXTURES / "claims.md"), "--offline", str(doc)],
                       capture_output=True, text=True)
    assert r.returncode == 1, r.stderr
    found = rules(json.loads(r.stdout))
    for rule in ("FIRST_PERSON", "EM_DASH", "FORBIDDEN_EXPRESSION", "CAREER_YEARS"):
        assert rule in found
