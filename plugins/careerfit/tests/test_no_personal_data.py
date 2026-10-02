import pytest

from conftest import PLUGIN_ROOT, personal_words

FILES = [p for p in PLUGIN_ROOT.rglob("*") if p.is_file() and p.name != ".personal-denylist"
         and p.suffix in {".py", ".md", ".html", ".json", ".txt"}]


def test_no_personal_words_anywhere():
    words = personal_words()
    if not words:
        pytest.skip("로컬 금지어 파일 없음 (tests/.personal-denylist)")
    hits = [(str(p.relative_to(PLUGIN_ROOT)), w) for p in FILES for w in words if w in p.read_text(encoding="utf-8")]
    assert hits == []
