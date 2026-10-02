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
