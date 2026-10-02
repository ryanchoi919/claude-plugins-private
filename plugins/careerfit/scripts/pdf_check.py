"""PDF 기계 검사: 크기·쪽수·폰트·빈 쪽·서명만 넘어간 쪽·ATS 띄어쓰기."""
from __future__ import annotations

import json
import re
import sys

from pypdf import PdfReader

SIZES = {"A4": (209.9, 297.0), "slide": (297.0, 166.9)}
SIGN_MARKERS = ("확인합니다", "작성자")
HANGUL = re.compile(r"[가-힣]")


def space_ratio(text: str) -> float:
    t = text.replace("\n", "")
    return t.count(" ") / len(t) if t else 0.0


def _fonts(reader: PdfReader) -> list[str]:
    names = set()
    for page in reader.pages:
        res = page.get("/Resources")
        fonts = res.get_object().get("/Font") if res else None
        if not fonts:
            continue
        for ref in fonts.get_object().values():
            base = str(ref.get_object().get("/BaseFont", ""))
            names.add(base.lstrip("/").split("+", 1)[-1])
    return sorted(n for n in names if n)


def check_pdf(path, kind="A4", max_pages=None, font_prefixes=("Nanum",), tol_mm=1.5) -> dict:
    reader = PdfReader(str(path))
    box = reader.pages[0].mediabox
    w = float(box.width) * 25.4 / 72
    h = float(box.height) * 25.4 / 72
    texts = [p.extract_text() or "" for p in reader.pages]
    chars = [len(re.sub(r"\s", "", t)) for t in texts]
    fonts = _fonts(reader)
    sign_only = len(texts) > 1 and chars[-1] < 80 and any(m in texts[-1] for m in SIGN_MARKERS)
    blank = [i + 1 for i, c in enumerate(chars) if c < 5]
    ratio = space_ratio("".join(texts))
    problems = []
    ew, eh = SIZES[kind]
    if abs(w - ew) > tol_mm or abs(h - eh) > tol_mm:
        problems.append({"rule": "PDF_SIZE", "severity": "필수", "message": f"{kind} 기대 {ew}×{eh}mm, 실제 {w:.1f}×{h:.1f}mm"})
    if max_pages and len(texts) > max_pages:
        problems.append({"rule": "PDF_MAX_PAGES", "severity": "필수", "message": f"{len(texts)}쪽 (상한 {max_pages}쪽)"})
    bad = [f for f in fonts if not f.startswith(tuple(font_prefixes))]
    if bad:
        problems.append({"rule": "PDF_FONT", "severity": "필수", "message": f"허용 외 폰트: {', '.join(bad)}"})
    if blank:
        problems.append({"rule": "PDF_BLANK_PAGE", "severity": "필수", "message": f"빈 쪽: {blank}"})
    if sign_only:
        problems.append({"rule": "PDF_SIGN_ONLY_PAGE", "severity": "필수", "message": "마지막 쪽에 서명만 넘어감"})
    if HANGUL.search("".join(texts)) and ratio < 0.05:
        problems.append({"rule": "PDF_ATS_SPACING", "severity": "권장",
                         "message": f"추출 텍스트의 띄어쓰기 비율 {ratio:.3f}: 채용 시스템 파싱에서 단어가 붙어 읽힐 수 있음"})
    return {"pages": len(texts), "width_mm": round(w, 1), "height_mm": round(h, 1), "fonts": fonts,
            "page_chars": chars, "blank_pages": blank, "sign_only_last_page": sign_only,
            "space_ratio": round(ratio, 4), "problems": problems}


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--kind", default="A4", choices=list(SIZES))
    ap.add_argument("--max-pages", type=int)
    a = ap.parse_args()
    r = check_pdf(a.pdf, a.kind, a.max_pages)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    sys.exit(1 if any(p["severity"] == "필수" for p in r["problems"]) else 0)
