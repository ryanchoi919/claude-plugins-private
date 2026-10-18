"""채용 공고 탐색: 사람인·잡코리아·비즈니스피플(bzpp.co.kr) 검색 결과를 모아 한 형식으로 정리한다.

usage: python3 job_search.py urls <CAREER.md>
       python3 job_search.py fetch <CAREER.md> [--out <json>] [--seen <seen.json>] [--sources saramin,jobkorea,bzpp]
       python3 job_search.py parse <saramin|jobkorea|bzpp> <저장한 HTML>
       python3 job_search.py mark <seen.json> <source:id> <관심|제외|지원> [사유]

검색 조건은 CAREER.md frontmatter의 `search` (references/job-sources.md).
로그인 없이 공개 검색 결과 첫 페이지(들)만 읽고, 요청 사이에 1초 쉰다.
"""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))

import html
import json
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

from scripts.config import load_career, normalize_company

SOURCES = ("saramin", "jobkorea", "bzpp")
DECISIONS = ("관심", "제외", "지원")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
JK_CAREER = {"1": "신입", "2": "경력", "3": "신입·경력", "4": "경력무관"}


def _text(fragment: str) -> str:
    t = re.sub(r"<[^>]+>", " ", fragment or "")
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def _q(s) -> str:
    return urllib.parse.quote(str(s))


def search_urls(source: str, keyword: str, cond: dict, page: int = 1) -> str:
    years = cond.get("career_years") or []
    lo, hi = (years + [None, None])[:2] if years else (None, None)
    if source == "saramin":
        u = (f"https://www.saramin.co.kr/zf_user/search/recruit?searchword={_q(keyword)}"
             f"&recruitPage={page}&recruitSort=relation&recruitPageCount=40")
        if lo is not None:
            u += f"&exp_cd=2&exp_min={lo}" + (f"&exp_max={hi}" if hi is not None else "")
        return u
    if source == "jobkorea":
        u = f"https://www.jobkorea.co.kr/Search/?stext={_q(keyword)}&tabType=recruit&Page_No={page}"
        return u + ("&careerType=2" if lo is not None else "")
    if source == "bzpp":
        u = f"https://www.bzpp.co.kr/recruit/recruit?srchRecruitEnterpriseList={_q(keyword)}&searchAllCareer=Y"
        if lo is not None:
            u += f"&searchStartCareer={lo}&searchEndCareer={hi if hi is not None else ''}"
        return u
    raise ValueError(f"소스는 {SOURCES} 중 하나여야 합니다: {source}")


# ---------- 파서: 각 소스 HTML → 공고 레코드 목록 ----------

def parse_saramin(doc: str) -> list:
    out = []
    parts = re.split(r'<div class="item_recruit" value="(\d+)"', doc)
    for rid, body in zip(parts[1::2], parts[2::2]):
        title = re.search(r'class="job_tit">\s*<a[^>]*title="([^"]*)"', body)
        corp = re.search(r'class="corp_name">(.*?)</strong>', body, re.S)
        cond = re.search(r'class="job_condition">(.*?)</div>', body, re.S)
        spans = [_text(s) for s in re.findall(r"<span>(.*?)</span>", cond.group(1), re.S)] if cond else []
        sector = re.search(r'class="job_sector">(.*?)<span class="job_day"', body, re.S)
        deadline = re.search(r'class="date">([^<]*)<', body)
        out.append({
            "source": "saramin", "id": rid,
            "url": f"https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx={rid}",
            "title": html.unescape(title.group(1)).strip() if title else "",
            "company": _text(corp.group(1)) if corp else "",
            "location": spans[0] if spans else "",
            "career": spans[1] if len(spans) > 1 else "",
            "employment": spans[3] if len(spans) > 3 else "",
            "deadline": _text(deadline.group(1)) if deadline else "",
            "tags": [t.strip() for t in _text(sector.group(1)).rstrip("외").split(",") if t.strip()] if sector else [],
        })
    return out


def _jk_data_blocks(doc: str):
    """Next.js flight payload(self.__next_f.push)를 풀어 검색 결과 data 객체들을 꺼낸다."""
    pushes = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', doc, re.S)
    blob = "".join(json.loads(f'"{p}"') for p in pushes) or doc
    dec = json.JSONDecoder()
    for m in re.finditer(r'\{"pageSize":', blob):
        try:
            obj, _ = dec.raw_decode(blob, m.start())
        except json.JSONDecodeError:
            continue
        if isinstance(obj.get("content"), list):
            yield obj


def parse_jobkorea(doc: str) -> list:
    blocks = sorted(_jk_data_blocks(doc), key=lambda o: o.get("totalElements") or 0, reverse=True)
    if not blocks:
        return []
    out = []
    for it in blocks[0]["content"]:
        if not it.get("id") or not it.get("title"):
            continue
        period = it.get("applicationPeriod") or {}
        out.append({
            "source": "jobkorea", "id": str(it["id"]),
            "url": f"https://www.jobkorea.co.kr/Recruit/GI_Read/{it['id']}",
            "title": it["title"].strip(),
            "company": (it.get("postingCompanyName") or it.get("companyName") or "").strip(),
            "location": "",  # 시·도 없이 역·구 이름만 와서 지역 거르기에 쓰지 않는다
            "location_hint": it.get("_internal_featureLocationCode") or "",
            "career": JK_CAREER.get(str(it.get("careerType")), ""),
            "employment": "",
            "deadline": (period.get("end") or "")[:10],
            "tags": [t for t in (it.get("_internal_featureWorkCode") or "").split(",") if t][:8],
        })
    return out


def parse_bzpp(doc: str) -> list:
    doc = re.sub(r"<script.*?</script>", "", doc, flags=re.S)
    out = []
    parts = re.split(r'<li cd_business="(BR\w+)"', doc)
    for rid, body in zip(parts[1::2], parts[2::2]):
        body = body.split("</li>", 1)[0]
        title = re.search(r'id="title"[^>]*>(.*?)</a>', body, re.S)
        hunter = re.search(r'class="hHunter-name">(.*?)</span>', body, re.S)
        corp = re.search(r'class="companyName"[^>]*>(.*?)</div>', body, re.S)
        field = lambda cls: (lambda m: _text(m.group(1)) if m else "")(
            re.search(rf'class="{cls}"[^>]*>(.*?)</span>', body, re.S))
        company = _text(corp.group(1)) if corp else ""
        out.append({
            "source": "bzpp", "id": rid,
            "url": f"https://www.bzpp.co.kr/biz/businessDetailView/{rid}",
            "title": _text(title.group(1)) if title else "",
            "company": company or (f"(헤드헌팅: {_text(hunter.group(1))})" if hunter else ""),
            "location": field("area"),
            "career": field("careers"),
            "employment": field("working-form"),
            "deadline": field("deadline-date date"),
            "tags": [t.lstrip("#") for t in re.findall(r"<span[^>]*>(#[^<]+)</span>", body)],
        })
    return out


PARSERS = {"saramin": parse_saramin, "jobkorea": parse_jobkorea, "bzpp": parse_bzpp}


# ---------- 수집 ----------

def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def chrome_args(chrome: str, url: str) -> list:
    """외부 페이지라 샌드박스를 켠다. 샌드박스가 안 뜨는 환경(컨테이너 root, user namespace 제한)만
    CAREERFIT_CHROME_NO_SANDBOX=1로 끈다. --user-data-dir를 주지 않으면 헤드리스 Chrome은 매번 새 임시
    프로필을 써서 사용자 프로필·쿠키를 읽지 않는다 (지정하면 --dump-dom 뒤에 종료되지 않는다)."""
    args = [chrome, "--headless=new", "--disable-gpu", "--disable-extensions",
            "--virtual-time-budget=12000", "--dump-dom", url]
    if os.environ.get("CAREERFIT_CHROME_NO_SANDBOX") == "1":
        args.insert(2, "--no-sandbox")
    return args


def _render(url: str) -> str:
    """bzpp 목록은 JS로 채워져서 헤드리스 Chrome으로 렌더한 DOM을 읽는다."""
    from scripts.chrome import find_chrome
    r = subprocess.run(chrome_args(find_chrome(), url), capture_output=True, text=True, timeout=90)
    if r.returncode != 0 and not r.stdout:
        hint = ""
        if "sandbox" in r.stderr.lower() or r.returncode < 0:
            hint = (" Chrome 샌드박스를 띄우지 못했을 수 있습니다. 이 환경에서 꼭 필요하면"
                    " CAREERFIT_CHROME_NO_SANDBOX=1로 다시 실행하세요 (외부 페이지를 샌드박스 없이 엽니다)")
        raise RuntimeError(f"Chrome 렌더 실패 (code {r.returncode}).{hint}")
    return r.stdout


def filter_and_merge(records: list, cond: dict) -> list:
    """제외어·지역 거르기, 소스 안 중복 제거, 소스 간 같은 공고 묶기."""
    exclude = [w.lower() for w in cond.get("exclude") or []]
    locations = cond.get("locations") or []
    seen_ids, by_key, out = set(), {}, []
    for r in records:
        key_id = f"{r['source']}:{r['id']}"
        if key_id in seen_ids:
            continue
        seen_ids.add(key_id)
        if any(w in r["title"].lower() for w in exclude):
            continue
        if locations and r.get("location") and not any(l in r["location"] for l in locations):
            continue
        kw = r.get("keyword", "").lower()
        r["kw_in_title"] = bool(kw) and any(kw in s.lower() for s in [r["title"], *r.get("tags", [])])
        dup = f"{normalize_company(r['company'])}|{re.sub(r'[^0-9A-Za-z가-힣]', '', r['title'])}"
        if r["company"] and dup in by_key:
            by_key[dup].setdefault("also_on", []).append(r["url"])
            continue
        by_key[dup] = r
        out.append(r)
    return out


def load_seen(path) -> dict:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def apply_seen(records: list, seen: dict, today: str) -> list:
    for r in records:
        k = f"{r['source']}:{r['id']}"
        prev = seen.get(k)
        r["new"] = prev is None
        r["decision"] = (prev or {}).get("decision")
        if prev is None:
            seen[k] = {"first_seen": today, "company": r["company"], "title": r["title"], "decision": None}
    return records


def mark(seen_path, key: str, decision: str, reason: str = "") -> dict:
    if decision not in DECISIONS:
        raise ValueError(f"결정은 {DECISIONS} 중 하나여야 합니다: {decision}")
    seen = load_seen(seen_path)
    if key not in seen:
        raise ValueError(f"{seen_path}에 {key}가 없습니다 (fetch로 먼저 기록)")
    seen[key].update({"decision": decision, "reason": reason, "decided": date.today().isoformat()})
    Path(seen_path).write_text(json.dumps(seen, ensure_ascii=False, indent=1), encoding="utf-8")
    return seen[key]


def fetch(cond: dict, sources=None, getter=_get, renderer=_render, pause: float = 1.0) -> dict:
    sources = [s for s in (sources or cond.get("sources") or SOURCES)]
    pages = int(cond.get("pages") or 1)
    records, errors, counts = [], [], {}
    for kw in cond.get("keywords") or []:
        for src in sources:
            for page in range(1, (1 if src == "bzpp" else pages) + 1):  # bzpp는 첫 페이지만
                url = search_urls(src, kw, cond, page)
                try:
                    doc = renderer(url) if src == "bzpp" else getter(url)
                    got = PARSERS[src](doc)
                except Exception as e:  # 한 소스가 막혀도 나머지는 계속
                    errors.append({"source": src, "keyword": kw, "url": url, "error": str(e)[:200]})
                    got = []
                if not got and not any(e["url"] == url for e in errors):
                    errors.append({"source": src, "keyword": kw, "url": url, "error": "결과 0건 (구조 변경 또는 차단 의심)"})
                for r in got:
                    r["keyword"] = kw
                counts[f"{src}:{kw}"] = counts.get(f"{src}:{kw}", 0) + len(got)
                records += got
                time.sleep(pause)
    return {"raw_counts": counts, "errors": errors, "postings": filter_and_merge(records, cond)}


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "parse":
        print(json.dumps(PARSERS[argv[2]](Path(argv[3]).read_text(encoding="utf-8")), ensure_ascii=False, indent=1))
        return 0
    if cmd == "mark":
        print(json.dumps(mark(argv[2], argv[3], argv[4], " ".join(argv[5:])), ensure_ascii=False))
        return 0
    career = load_career(argv[2])
    cond = career.search or {}
    if not cond.get("keywords"):
        print("CAREER.md의 search.keywords가 비어 있습니다. search 스킬로 조건부터 정하세요", file=_sys.stderr)
        return 1
    opts = dict(zip(argv[3::2], argv[4::2]))
    sources = opts["--sources"].split(",") if "--sources" in opts else None
    if cmd == "urls":
        for kw in cond["keywords"]:
            for src in sources or cond.get("sources") or SOURCES:
                print(f"{src}\t{kw}\t{search_urls(src, kw, cond)}")
        return 0
    if cmd == "fetch":
        result = fetch(cond, sources)
        seen_path = opts.get("--seen", str(career.paths["search"] / "seen.json"))
        seen = load_seen(seen_path)
        apply_seen(result["postings"], seen, date.today().isoformat())
        Path(seen_path).parent.mkdir(parents=True, exist_ok=True)
        Path(seen_path).write_text(json.dumps(seen, ensure_ascii=False, indent=1), encoding="utf-8")
        text = json.dumps(result, ensure_ascii=False, indent=1)
        if "--out" in opts:
            Path(opts["--out"]).parent.mkdir(parents=True, exist_ok=True)
            Path(opts["--out"]).write_text(text, encoding="utf-8")
            new = sum(r["new"] for r in result["postings"])
            print(f"{len(result['postings'])}건 (새 공고 {new}건), 오류 {len(result['errors'])}건 → {opts['--out']}")
        else:
            print(text)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    _sys.exit(main(_sys.argv))
