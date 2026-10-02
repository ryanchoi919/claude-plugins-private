import json

from conftest import PLUGIN_ROOT

REPO_ROOT = PLUGIN_ROOT.parent.parent


def test_plugin_json():
    data = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert data["name"] == "careerfit"
    assert data["version"] == "0.1.0"
    assert "헤드헌터" in data["description"] or "headhunter" in data["description"].lower()


def test_marketplace_entry():
    data = json.loads((REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    entries = [p for p in data["plugins"] if p["name"] == "careerfit"]
    assert len(entries) == 1
    assert entries[0]["source"] == "./plugins/careerfit"


def test_root_readme_row():
    assert "[`careerfit`](plugins/careerfit)" in (REPO_ROOT / "README.md").read_text(encoding="utf-8")
