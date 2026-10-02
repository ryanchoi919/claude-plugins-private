import os
import subprocess
import sys

import pytest

from conftest import PLUGIN_ROOT
from scripts import chrome


def test_env_override(tmp_path, monkeypatch):
    fake = tmp_path / "chrome"
    fake.write_text("#!/bin/sh\n")
    monkeypatch.setenv("CAREERFIT_CHROME", str(fake))
    assert chrome.find_chrome() == str(fake)


def test_env_override_missing_file(tmp_path, monkeypatch):
    monkeypatch.setenv("CAREERFIT_CHROME", str(tmp_path / "nope"))
    with pytest.raises(chrome.ChromeNotFound):
        chrome.find_chrome()


def test_playwright_cache_picks_highest(tmp_path, monkeypatch):
    monkeypatch.delenv("CAREERFIT_CHROME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    for n in ("1228", "1234", "999"):
        d = tmp_path / ".cache" / "ms-playwright" / f"chromium-{n}" / "chrome-linux64"
        d.mkdir(parents=True)
        (d / "chrome").write_text("")
    assert chrome.find_chrome().endswith("chromium-1234/chrome-linux64/chrome")


def test_find_chrome_missing_gives_guidance(tmp_path, monkeypatch):
    monkeypatch.delenv("CAREERFIT_CHROME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("PATH", str(tmp_path))
    with pytest.raises(chrome.ChromeNotFound, match="playwright install chromium"):
        chrome.find_chrome()
    env = {k: v for k, v in os.environ.items() if k != "CAREERFIT_CHROME"}
    env.update(HOME=str(tmp_path), PATH=str(tmp_path))
    r = subprocess.run([sys.executable, str(PLUGIN_ROOT / "scripts" / "chrome.py"), "pdf", "a.html", "a.pdf"],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 2
    assert "playwright install chromium" in r.stderr
    assert "Traceback" not in r.stderr


def test_render_pdf(tmp_path, chrome_or_skip):
    html = tmp_path / "a.html"
    html.write_text("<style>@page{size:A4}</style><p>안녕하세요</p>", encoding="utf-8")
    out = chrome.render_pdf(html, tmp_path / "a.pdf", chrome_or_skip)
    assert out.exists() and out.stat().st_size > 1000
