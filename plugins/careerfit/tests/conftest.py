import shutil
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(PLUGIN_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))


@pytest.fixture
def persona_root(tmp_path):
    dst = tmp_path / "career"
    shutil.copytree(FIXTURES / "persona", dst)
    return dst


@pytest.fixture
def chrome_or_skip():
    from scripts import chrome
    try:
        return chrome.find_chrome()
    except chrome.ChromeNotFound:
        pytest.skip("헤드리스 Chrome 없음")


def personal_words() -> list:
    """실제 개인정보 금지어. 저장소에 넣지 않는 로컬 파일(tests/.personal-denylist 또는
    CAREERFIT_DENYLIST 경로)에서 한 줄에 하나씩 읽는다. 없으면 빈 목록."""
    import os
    p = Path(os.environ.get("CAREERFIT_DENYLIST", Path(__file__).resolve().parent / ".personal-denylist"))
    if not p.is_file():
        return []
    return [w.strip() for w in p.read_text(encoding="utf-8").splitlines() if w.strip() and not w.startswith("#")]
