import pytest

from scripts import status

NOW = "2026-10-02T10:00:00+09:00"


def _app(root, folder, fm):
    d = root / "지원 이력" / folder
    d.mkdir(parents=True)
    (d / "공고.md").write_text(f"---\n{fm}---\n# 공고\n", encoding="utf-8")
    return d / "공고.md"


def test_set_existing_status(persona_root):
    p = _app(persona_root, "샘플커머스 AI PM", "회사: (주)샘플커머스\n상태: 준비 중\nmodified: 2026-09-30T00:00:00+09:00\n")
    assert status.set_status(p, "서류 전형", NOW) == ("준비 중", "서류 전형")
    t = p.read_text(encoding="utf-8")
    assert "상태: 서류 전형" in t and f"modified: {NOW}" in t
    assert t.endswith("---\n# 공고\n")


def test_insert_missing_status_before_aliases(persona_root):
    p = _app(persona_root, "옛 공고", "tags:\n  - 주제/커리어\naliases:\ncreated: 2026-07-01T00:00:00+09:00\n")
    assert status.set_status(p, "서류 탈락", NOW) == (None, "서류 탈락")
    t = p.read_text(encoding="utf-8")
    assert t.index("상태: 서류 탈락") < t.index("aliases:")


def test_insert_missing_status_without_aliases(persona_root):
    p = _app(persona_root, "짧은 공고", "회사: 가상회사\n")
    status.set_status(p, "면접", NOW)
    assert p.read_text(encoding="utf-8").startswith("---\n회사: 가상회사\n상태: 면접\n---\n")


def test_invalid_status(persona_root):
    p = _app(persona_root, "x", "상태: 준비 중\n")
    with pytest.raises(ValueError):
        status.set_status(p, "탈락", NOW)


def test_same_status_no_write(persona_root):
    p = _app(persona_root, "y", "상태: 면접\nmodified: 2026-09-30T00:00:00+09:00\n")
    before = p.read_text(encoding="utf-8")
    assert status.set_status(p, "면접", NOW) == ("면접", "면접")
    assert p.read_text(encoding="utf-8") == before


def test_scan_korean_folder_names(persona_root):
    _app(persona_root, "올리브영 AX 전략 담당자", "회사: 씨제이올리브영\n상태: 서류 전형\n지원일:\n")
    _app(persona_root, "대웅 웰다 AX Engineer", "tags: []\n")
    (persona_root / "지원 이력" / "올리브영 AX 전략 담당자" / "진행 상황.md").write_text("x", encoding="utf-8")
    rows = status.scan(persona_root / "지원 이력")
    assert [r["folder"] for r in rows] == ["대웅 웰다 AX Engineer", "올리브영 AX 전략 담당자"]
    assert rows[0]["status"] is None and rows[1]["status"] == "서류 전형"
    assert rows[1]["has_progress"] is True and rows[1]["company"] == "씨제이올리브영"
