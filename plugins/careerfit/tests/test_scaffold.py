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


def test_evals_format():
    data = json.loads((PLUGIN_ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
    assert data["skill_name"] == "careerfit"
    assert [e["id"] for e in data["evals"]] == [1, 2, 3, 4]
    for e in data["evals"]:
        assert e["prompt"] and e["expected_output"]
        for f in e["files"]:
            assert (PLUGIN_ROOT / f).exists(), f


def test_plugin_readme_sections():
    s = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
    for w in ("/careerfit:setup", "/careerfit:apply", "/careerfit:track", "/careerfit:helper",
              "CAREERFIT_CHROME", "uv run --with pytest", "## 실사용 검증"):
        assert w in s, w
