import re

import pytest
import yaml

from conftest import PLUGIN_ROOT

SKILLS = sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md"))
AGENTS = sorted((PLUGIN_ROOT / "agents").glob("*.md"))
EXPECTED = {"review", "brief", "write-resume", "write-career-description", "write-portfolio", "apply", "setup", "track", "helper"}


def fm(p):
    t = p.read_text(encoding="utf-8")
    assert t.startswith("---\n"), p
    return yaml.safe_load(t[4:t.index("\n---", 4)]), t


@pytest.mark.parametrize("p", SKILLS + AGENTS, ids=lambda p: p.parent.name if p.name == "SKILL.md" else p.stem)
def test_frontmatter_and_refs(p):
    meta, text = fm(p)
    assert meta.get("name") and meta.get("description")
    if p.name == "SKILL.md":
        assert meta["name"] == p.parent.name
    for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)", text):
        assert (PLUGIN_ROOT / ref).exists(), f"{p}: 없는 경로 {ref}"


def test_review_and_agent_exist():
    assert (PLUGIN_ROOT / "skills" / "review" / "SKILL.md").is_file()
    assert (PLUGIN_ROOT / "agents" / "consistency-reviewer.md").is_file()


def test_skill_set_complete_when_done():
    names = {p.parent.name for p in SKILLS}
    assert names <= EXPECTED
