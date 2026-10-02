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
    cands = glob.glob(os.path.join(home, ".cache/ms-playwright/chromium-*/chrome-linux64/chrome"))
    cands = [c for c in cands if re.search(r"chromium-(\d+)", c)]
    if cands:
        return max(cands, key=_build_no)
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        found = shutil.which(name)
        if found:
            return found
    raise ChromeNotFound(GUIDE)


def _run(args: list[str]) -> None:
    subprocess.run(args, capture_output=True, text=True, timeout=180)


def render_pdf(html, pdf, chrome: str | None = None) -> Path:
    chrome = chrome or find_chrome()
    pdf = Path(pdf).resolve()
    _run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", f"--print-to-pdf={pdf}",
          "--no-pdf-header-footer", Path(html).resolve().as_uri()])
    if not pdf.exists():
        raise RuntimeError(f"PDF가 만들어지지 않았습니다: {pdf}")
    return pdf


def screenshot(html, png, width: int, height: int, chrome: str | None = None) -> Path:
    chrome = chrome or find_chrome()
    png = Path(png).resolve()
    _run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
          f"--window-size={width},{height}", f"--screenshot={png}", Path(html).resolve().as_uri()])
    if not png.exists():
        raise RuntimeError(f"스크린샷이 만들어지지 않았습니다: {png}")
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
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
