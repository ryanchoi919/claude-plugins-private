"""경력기술서 마크다운(경력기술서.md) → A4 HTML (templates/career-description.html 기반)

usage: python3 render_md.py <경력기술서.md> <out.html> --title <HTML title> --target "<회사> <직무> 지원"
         --name <이름> --contact "<메일> · <전화>" [--break-projects]

마크다운 규칙:
  - frontmatter와 "> " 콜아웃 줄, "# " 제목과 그 다음 줄은 렌더링하지 않는다 (헤더는 인자로 만든다)
  - "## 경력 요약" 표 → 요약 표(두 번째 칸 괄호 안은 회사 소개 줄), 그 외 "## " 섹션의 표 → 대응표(.fit, 3열 권장)
  - "### N. 제목" → 프로젝트 블록(제목에 "프로젝트 N ·" 부착), 다음 줄 = 메타, 그 다음 = "한 줄 요약: ..."
  - 프로젝트 안의 "**문제 정의**" 같은 굵은 줄 → 항목 행("의사결정"이 들어가면 강조 행), "- 핵심 수치: a · b" → 결과 칩
  - "## 회사별 경력 상세" 안의 "### 회사 · 소속 | 기간" → 회사 블록, "- **항목**" + "  - 내용" → 개조식 항목
  - "[확인 필요: ...]" → 노란 강조 (제출본에는 0개여야 함)
  - --break-projects: 프로젝트 2부터 새 쪽에서 시작 (심층형에서 프로젝트 제목이 쪽 끝에 걸릴 때)
"""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))

import html
import re
import sys
from pathlib import Path

DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "career-description.html"


def inline(t: str) -> str:
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"\1", t)
    t = re.sub(r"(\[확인 필요[^\]]*\])", r'<mark class="todo">\1</mark>', t)
    return t.replace(" – ", " &ndash; ").replace("→", "&rarr;")


def table(rows: list, cls: str) -> str:
    hdr = [c.strip() for c in rows[0].strip("|").split("|")]
    r = ['<table class="%s"><tr>%s</tr>' % (cls, "".join("<th>%s</th>" % inline(c) for c in hdr))]
    for row in rows[2:]:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if cls == "summary":
            m = re.match(r"(.*) \((.*)\)$", cells[1])
            c1 = (inline(m.group(1)) + '<br><span style="color:var(--muted);font-size:12.5px">%s</span>' % inline(m.group(2))
                  if m else inline(cells[1]))
            r.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (inline(cells[0]), c1, inline(cells[2])))
        else:
            r.append("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in cells))
    r.append("</table>")
    return "\n".join(r)


def render(md_text: str, title: str, target: str, name: str, contact: str,
           break_projects: bool = False, template=DEFAULT_TEMPLATE) -> str:
    body = md_text.split("\n---\n", 1)[1] if md_text.startswith("---") else md_text
    tpl = Path(template).read_text(encoding="utf-8")
    head = tpl[:tpl.index("</style>")]
    if break_projects:
        head += "  @media print{ .proj + .proj{ break-before:page; } }\n"
    head += "</style>"
    head = head.replace("{{TITLE}}", html.escape(title)).replace("{{TARGET}}", html.escape(target))

    o = ['<div class="page">']
    st = dict(section=False, proj=False, row=False, ul=False, job=False, item=False, cur="")

    def close_ul():
        if st["ul"]:
            o.append("</ul>")
            st["ul"] = False

    def close_row():
        close_ul()
        if st["row"]:
            o.append("</div></div>")
            st["row"] = False

    def close_proj():
        close_row()
        if st["proj"]:
            o.append("</article>")
            st["proj"] = False

    def close_item():
        close_ul()
        if st["item"]:
            o.append("</div>")
            st["item"] = False

    def close_job():
        close_item()
        if st["job"]:
            o.append("</div>")
            st["job"] = False

    def close_section():
        close_proj()
        close_job()
        close_ul()
        if st["section"]:
            o.append("</section>")
            st["section"] = False

    lines = body.split("\n")
    i = 0
    skip_next_text = False
    while i < len(lines):
        l = lines[i]
        if l.startswith("> "):
            i += 1
            continue
        if l.startswith("# "):
            skip_next_text = True
            i += 1
            continue
        if skip_next_text and l.strip():
            skip_next_text = False
            i += 1
            continue
        if l.startswith("## "):
            close_section()
            st["cur"] = l[3:].strip()
            o.append('<section class="section">\n<h2>%s</h2>' % inline(st["cur"]))
            st["section"] = True
            i += 1
            continue
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            o.append(table(rows, "summary" if "경력 요약" in st["cur"] else "fit"))
            continue
        company = "회사별" in st["cur"]
        if l.startswith("### ") and company:
            close_job()
            cname, _, when = l[4:].partition(" | ")
            o.append('<div class="job"><div class="job-head"><h3>%s</h3><span class="when">%s</span></div>'
                     % (inline(cname.strip()), inline(when.strip())))
            st["job"] = True
            if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].startswith("-"):
                o.append('<div class="about">%s</div>' % inline(lines[i + 1].strip()))
                i += 1
            i += 1
            continue
        if l.startswith("### "):
            close_proj()
            ptitle = re.sub(r"^(\d+)\.\s*", r"프로젝트 \1 · ", l[4:].strip())
            meta = lines[i + 1].strip()
            one = lines[i + 3].strip().replace("한 줄 요약: ", "")
            o.append('<article class="proj"><div class="proj-head"><h3>%s</h3><div class="meta">%s</div>'
                     '<div class="oneline">%s</div></div>' % (inline(ptitle), inline(meta), inline(one)))
            st["proj"] = True
            i += 4
            continue
        m = re.match(r"^\*\*(.+)\*\*$", l.strip())
        if m and st["proj"]:
            close_row()
            k = m.group(1)
            o.append('<div class="row%s"><div class="k">%s</div><div class="v">'
                     % (" decision" if "의사결정" in k else "", inline(k)))
            st["row"] = True
            i += 1
            continue
        if company and re.match(r"^- \*\*(.+)\*\*$", l.strip()):
            close_item()
            o.append('<div class="item"><div class="t">%s</div>' % inline(re.match(r"^- \*\*(.+)\*\*$", l.strip()).group(1)))
            st["item"] = True
            i += 1
            continue
        if company and l.startswith("  - "):
            if not st["ul"]:
                o.append("<ul>")
                st["ul"] = True
            o.append("<li>%s</li>" % inline(l[4:].strip()))
            i += 1
            continue
        if l.startswith("- "):
            t = l[2:].strip()
            if t.startswith("핵심 수치:"):
                close_ul()
                o.append('<div class="kpi">%s</div>'
                         % "".join("<span>%s</span>" % inline(c.strip()) for c in t.split(":", 1)[1].split(" · ")))
            else:
                if not st["ul"]:
                    o.append("<ul%s>" % (' class="strengths"' if "핵심 역량" in st["cur"] else ""))
                    st["ul"] = True
                o.append("<li>%s</li>" % inline(t))
            i += 1
            continue
        if l.strip() == "---":
            close_section()
            i += 1
            continue
        if l.startswith("위 기재 사항"):
            o.append('<div class="sign">%s</div>' % inline(l.strip()))
            i += 1
            continue
        i += 1
    close_section()
    o.append("</div>")
    header = ('<header class="head">\n  <div><h1>경력기술서 <small>%s</small></h1><div class="target">%s</div></div>\n'
              '  <div class="contact">%s</div>\n</header>') % (html.escape(name), html.escape(target), html.escape(contact))
    page = "\n".join(o).replace('<div class="page">', '<div class="page">\n' + header, 1)
    return head + "\n" + page + "\n"


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("out")
    ap.add_argument("--title", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--contact", required=True)
    ap.add_argument("--break-projects", action="store_true")
    a = ap.parse_args(argv)
    out = render(Path(a.md).read_text(encoding="utf-8"), a.title, a.target, a.name, a.contact, a.break_projects)
    Path(a.out).write_text(out, encoding="utf-8")
    print(a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
