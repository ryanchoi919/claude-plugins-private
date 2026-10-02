"""헤드리스 Chrome 탐색과 HTML → PDF/PNG 렌더."""
from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

GUIDE = ("헤드리스 Chrome을 찾지 못했습니다. `npx playwright install chromium`으로 설치하거나 "
         "환경변수 CAREERFIT_CHROME에 Chrome 실행 파일 경로를 지정하세요.")


CACHE_GLOBS = (
    ".cache/ms-playwright/chromium-*/chrome-linux64/chrome",
    "Library/Caches/ms-playwright/chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
    "Library/Caches/ms-playwright/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium",
)
MAC_APPS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)


class ChromeNotFound(RuntimeError):
    pass


def _build_no(path: str) -> int:
    return int(re.search(r"chromium-(\d+)", path).group(1))


def find_chrome() -> str:
    env = os.environ.get("CAREERFIT_CHROME")
    if env:
        if Path(env).is_file():
            return env
        raise ChromeNotFound(f"CAREERFIT_CHROME 경로에 파일이 없습니다: {env}. {GUIDE}")
    home = os.environ.get("HOME", str(Path.home()))
    cands = []
    for pattern in CACHE_GLOBS:
        cands += glob.glob(os.path.join(home, pattern))
    cands = [c for c in cands if re.search(r"chromium-(\d+)", c)]
    if cands:
        return max(cands, key=_build_no)
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        found = shutil.which(name)
        if found:
            return found
    for app in MAC_APPS:
        if Path(app).is_file():
            return app
    raise ChromeNotFound(GUIDE)


def _run(args: list[str], out: Path) -> None:
    """Chrome을 실행하고, 실패하면 stderr를 담아 RuntimeError. 이전 산출물이 성공으로 보이지 않게 먼저 지운다."""
    out.unlink(missing_ok=True)
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Chrome이 180초 안에 끝나지 않았습니다: {out}")
    if r.returncode != 0 or not out.exists():
        raise RuntimeError(f"Chrome 렌더 실패 (종료 코드 {r.returncode}): {out}\n{r.stderr.strip()[-800:]}")


def render_pdf(html, pdf, chrome: str | None = None) -> Path:
    chrome = chrome or find_chrome()
    pdf = Path(pdf).resolve()
    _run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", f"--print-to-pdf={pdf}",
          "--no-pdf-header-footer", Path(html).resolve().as_uri()], pdf)
    return pdf


def screenshot(html, png, width: int, height: int, chrome: str | None = None) -> Path:
    chrome = chrome or find_chrome()
    png = Path(png).resolve()
    _run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
          f"--window-size={width},{height}", f"--screenshot={png}", Path(html).resolve().as_uri()], png)
    return png


def main(argv: list[str]) -> int:
    try:
        if argv[:1] == ["pdf"] and len(argv) == 3:
            print(render_pdf(argv[1], argv[2]))
        elif argv[:1] == ["shot"] and len(argv) == 5:
            print(screenshot(argv[1], argv[2], int(argv[3]), int(argv[4])))
        else:
            print("usage: chrome.py pdf <html> <pdf> | shot <html> <png> <w> <h>", file=sys.stderr)
            return 64
    except ChromeNotFound as e:
        print(str(e), file=sys.stderr)
        return 2
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
