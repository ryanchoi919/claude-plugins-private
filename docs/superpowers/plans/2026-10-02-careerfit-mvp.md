# 커리어핏(careerfit) 1단계 MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 헤드헌터식 기획(전략 브리프·주장 원장)과 최종 일관성 검수를 갖춘 이력서·경력기술서·포트폴리오 플러그인 `careerfit`의 1단계(MVP)를 `plugins/careerfit/`에 만든다.

**Architecture:** 사용자 진입점 스킬 4개(`setup`·`apply`·`track`·`helper`)가 내부 스킬 5개(`brief`·`write-resume`·`write-career-description`·`write-portfolio`·`review`)와 검수 에이전트 1개(`consistency-reviewer`)를 부른다. 결정적인 작업(설정 로드, PDF 렌더·검사, 문서 린트, 경력기술서 렌더, 포트폴리오 회사판 파생, 지원 상태 갱신)은 `scripts/`의 Python 모듈이 TDD로 맡고, 판단·대화가 필요한 작업은 스킬 본문이 맡는다. 규칙은 `references/`에 한 번만 둔다.

**Tech Stack:** Python 3.12, pypdf, PyYAML, pytest(uv로 실행), 헤드리스 Chromium(Playwright 캐시), Claude Code 플러그인(SKILL.md·agents).

**Spec:** `docs/superpowers/specs/2026-10-02-careerfit-design.md` (같은 브랜치 `docs/careerfit-design`)

## Global Constraints

- 플러그인 ID `careerfit`, 위치 `plugins/careerfit/`, 루트 `.claude-plugin/marketplace.json`과 루트 `README.md` 표에 등록한다.
- 시장 기본값 `KR`. 스킬 본문·레퍼런스·사용자 메시지는 한국어, 코드 식별자는 영어.
- 상태 값은 정확히 이 8개: `준비 중` / `서류 제출` / `서류 전형` / `서류 탈락` / `면접` / `최종 합격` / `불합격` / `지원 취소`.
- 제출 파일명: 회사판 `{name}_{doc}_{company}`, 범용본 `{name}_{doc}`. 문서종류는 `이력서`/`경력기술서`/`포트폴리오`. 회사명은 `(주)`·`㈜`·`주식회사`·공백 제거. HTML `<title>`은 파일명 stem과 같다.
- PDF 크기: 이력서·경력기술서 A4(약 209.9×297.0mm), 포트폴리오 297.0×166.9mm. 폰트는 로컬 Nanum 계열만(Google Fonts 금지).
- 이 저장소에는 실제 개인 이력을 넣지 않는다. 테스트·예시는 가상 인물만 쓴다(이름 "김하늘", 가상 회사 "(주)가상물산", 가상 공고사 "(주)샘플커머스").
- Python 의존성은 표준 라이브러리 + `pypdf` + `PyYAML`만. 테스트 실행: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests -q` (저장소 루트에서).
- 스크립트는 `${CLAUDE_PLUGIN_ROOT}/scripts/`에 두고 스킬은 그 경로로 호출한다. 각 스크립트는 import 가능한 함수 + `if __name__ == "__main__":` CLI를 함께 가진다.
- 커밋 메시지: `type(careerfit): 한국어 설명` 형식, 본문 한국어, 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- 작업 브랜치: `feat/careerfit-mvp`(Task 1에서 `origin/master` 기준으로 생성, 워크트리 `.claude/worktrees/careerfit-mvp`). 설계·계획 문서는 이 브랜치에 cherry-pick 하거나 같은 내용을 포함한다(Task 1 Step 1).

## Review Focus

1. **한글·공백이 들어간 경로** (예: `Career/지원 이력/올리브영 AX 전략 담당자`) — 모든 스크립트가 따옴표·이스케이프 문제 없이 처리해야 한다. → Task 2 `test_paths_with_korean_and_spaces`, Task 10 `test_scan_korean_folder_names`.
2. **회사명 표기 변형** ("(주)샘플커머스", "㈜샘플커머스", "주식회사 샘플 커머스") — 같은 제출 파일명이 나와야 하고, 타사명 잔존 검사도 변형을 잡아야 한다. → Task 2 `test_normalize_company_variants`, Task 5 `test_other_company_variants`.
3. **숫자 표기 변형** ("16,376부" vs "16376부", "12.6 %" vs "12.6%") — 원장 대조가 같은 값으로 봐야 한다. → Task 6 `test_number_format_variants_match_claims`.
4. **보이지 않는 HTML 영역** (주석·`<script>`·`<style>`·base64 사진 `data:` URI) — 린트가 여기 든 em dash·숫자를 오탐하면 안 된다(반대로 숨은 텍스트 노출 검사는 별도 규칙으로 잡는다). → Task 5 `test_comments_scripts_datauri_ignored`, `test_hidden_comment_flagged_separately`.
5. **Chrome이 없는 환경** — 트레이스백 대신 설치 안내 메시지와 종료 코드 2, 관련 테스트는 skip. → Task 3 `test_find_chrome_missing_gives_guidance`.

---

## File Structure

```
plugins/careerfit/
├── .claude-plugin/plugin.json                 # Task 1
├── README.md                                  # Task 1(뼈대), Task 19(완성)
├── scripts/
│   ├── __init__.py                            # Task 1 (빈 파일, 테스트 import용)
│   ├── config.py        # CAREER.md 로드·경로·제출 파일명                  Task 2
│   ├── chrome.py        # Chrome 탐색·PDF/스크린샷 렌더                     Task 3
│   ├── pdf_check.py     # PDF 크기·쪽수·폰트·빈 쪽·서명만 쪽·ATS 띄어쓰기     Task 4
│   ├── lint_docs.py     # 문서 린트(금지어·타사명·title·원장·기간·버전·링크) Task 5~7
│   ├── render_md.py     # 경력기술서 md → A4 HTML                          Task 8
│   ├── build_variant.py # 포트폴리오 회사판 파생                             Task 9
│   └── status.py        # 지원 상태 갱신·지원 목록 스캔                       Task 10
├── templates/
│   ├── resume.html  career-description.html  portfolio.html               # Task 11
├── references/
│   ├── writing-rules.md  attribution-and-facts.md  confidentiality.md     # Task 12
│   ├── filenames.md  jd-capture.md  korean-career-description-guide.md  schemas.md
├── agents/consistency-reviewer.md                                         # Task 13
├── skills/
│   ├── review/SKILL.md                                                    # Task 13
│   ├── brief/SKILL.md                                                     # Task 14
│   ├── write-resume/ write-career-description/ write-portfolio/  SKILL.md # Task 15
│   ├── apply/SKILL.md                                                     # Task 16
│   ├── setup/SKILL.md                                                     # Task 17
│   ├── track/SKILL.md  helper/SKILL.md                                    # Task 18
├── evals/evals.json                                                       # Task 19
└── tests/
    ├── conftest.py                                                        # Task 1
    ├── fixtures/persona/  (가상 인물 김하늘의 career-root)                  # Task 2에서 생성, 이후 확장
    ├── test_scaffold.py  test_config.py  test_chrome.py  test_pdf_check.py
    ├── test_lint_basic.py  test_lint_claims.py  test_lint_cli.py
    ├── test_render_md.py  test_build_variant.py  test_status.py
    ├── test_templates.py  test_references.py  test_skills_wellformed.py
```

---

### Task 1: 플러그인 뼈대·마켓플레이스 등록·테스트 하네스

**Files:**
- Create: `plugins/careerfit/.claude-plugin/plugin.json`
- Create: `plugins/careerfit/README.md`
- Create: `plugins/careerfit/scripts/__init__.py`
- Create: `plugins/careerfit/tests/conftest.py`
- Create: `plugins/careerfit/tests/test_scaffold.py`
- Modify: `.claude-plugin/marketplace.json` (plugins 배열에 항목 추가)
- Modify: `README.md` (Plugins 표에 행 추가)

**Interfaces:**
- Produces: `tests/conftest.py`의 fixture `PLUGIN_ROOT: Path`(플러그인 루트), `FIXTURES: Path`(`tests/fixtures`), pytest fixture `persona_root` (Task 2에서 사용, `tests/fixtures/persona`를 tmp로 복사해 반환). `scripts`는 `import scripts.config` 형태로 import 한다(conftest가 `sys.path`에 플러그인 루트를 넣는다).

- [ ] **Step 1: 브랜치·워크트리 만들기**

```bash
cd /home/ryanchoi/claude-plugins-private
git fetch origin
git worktree add .claude/worktrees/careerfit-mvp -b feat/careerfit-mvp origin/master
cd .claude/worktrees/careerfit-mvp
git checkout origin/docs/careerfit-design -- docs/superpowers/specs/2026-10-02-careerfit-design.md docs/superpowers/plans/2026-10-02-careerfit-mvp.md
```
이후 모든 Task는 이 워크트리에서 진행한다.

- [ ] **Step 2: 실패하는 테스트 작성** — `plugins/careerfit/tests/test_scaffold.py`

```python
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
```

`plugins/careerfit/tests/conftest.py`:

```python
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
```

- [ ] **Step 3: 실패 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_scaffold.py -q`
Expected: FAIL (plugin.json 없음)

- [ ] **Step 4: 구현**

`plugins/careerfit/.claude-plugin/plugin.json`:
```json
{
  "name": "careerfit",
  "version": "0.1.0",
  "description": "헤드헌터처럼 함께 커리어를 정리하고, 공고마다 전략 브리프를 기획하고, 근거 기반으로 이력서·경력기술서·포트폴리오를 쓰고, 지원 결과를 회고하는 플러그인 (setup / apply / track / helper).",
  "author": { "name": "ryanchoi" }
}
```
`plugins/careerfit/scripts/__init__.py`: 빈 파일.
`plugins/careerfit/README.md` (뼈대, Task 19에서 완성):
```markdown
# careerfit (커리어핏)

헤드헌터처럼 사용자와 함께 커리어를 정리하고(setup), 공고마다 지원 전략을 기획해 서류를 쓰고(apply), 결과를 회고해 다음 지원에 반영하는(track) Claude Code 플러그인. 뭘 해야 할지 모를 때는 helper.

설계: `docs/superpowers/specs/2026-10-02-careerfit-design.md`
```
루트 `.claude-plugin/marketplace.json`의 `plugins` 배열 끝에 추가:
```json
{
  "name": "careerfit",
  "source": "./plugins/careerfit",
  "description": "Headhunter-style career kit: organize your career history into an evidence-backed store, plan a strategy brief per job posting, then write resume / career description / portfolio with a claims ledger and a final consistency review, and track results to learn what works."
}
```
루트 `README.md` Plugins 표 끝에 행 추가:
```markdown
| [`careerfit`](plugins/careerfit) | 헤드헌터식 커리어 키트: 이력 저장소 정리 → 공고별 전략 브리프 → 근거 기반 이력서·경력기술서·포트폴리오 → 지원 결과 회고 |
```

- [ ] **Step 5: 통과 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_scaffold.py -q`
Expected: `3 passed`

- [ ] **Step 6: 커밋**

```bash
git add plugins/careerfit .claude-plugin/marketplace.json README.md docs/superpowers
git commit -m "feat(careerfit): 플러그인 뼈대와 마켓플레이스 등록

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: `scripts/config.py` — CAREER.md 로드·경로·제출 파일명, 가상 인물 fixture

**Files:**
- Create: `plugins/careerfit/scripts/config.py`
- Create: `plugins/careerfit/tests/fixtures/persona/CAREER.md`
- Create: `plugins/careerfit/tests/fixtures/persona/projects/재고 예측 대시보드 구축.md`
- Create: `plugins/careerfit/tests/fixtures/persona/projects/고객 문의 자동 분류 에이전트.md`
- Create: `plugins/careerfit/tests/fixtures/persona/projects/채널 수익성 분석.md`
- Test: `plugins/careerfit/tests/test_config.py`

**Interfaces:**
- Produces:
  - `DOC_TYPES: tuple[str, ...] = ("이력서", "경력기술서", "포트폴리오")`
  - `STATUSES: tuple[str, ...]` (Global Constraints의 8개, 그 순서)
  - `class Career` (dataclass): `root: Path`, `name: str`, `contact: dict`, `paths: dict[str, Path]`(키 `projects`·`applications`·`base`·`insights`·`output`), `market: str`, `career_start: date | None`, `filename_pattern: str`, `money_policy: str`, `body: str`
  - `load_career(path: str | Path) -> Career` — 파일 없음·frontmatter 없음·name 없음이면 `ValueError`(한국어 메시지)
  - `normalize_company(name: str) -> str`
  - `submission_name(career: Career, doc: str, company: str | None = None, ext: str | None = "pdf") -> str`
  - `read_frontmatter(path: Path) -> tuple[dict, str]` — 다른 스크립트도 쓴다

- [ ] **Step 1: fixture 작성**

`tests/fixtures/persona/CAREER.md`:
```markdown
---
name: 김하늘
contact:
  email: haneul@example.com
  phone: 010-0000-0000
  in_documents_only: true
paths:
  projects: projects
  applications: 지원 이력
  base: 기본본
  insights: insights.md
  output: 제출
market: KR
career_start: 2015-03-01
money_policy: allow
---
## 문체 선호
- 자기소개서는 두괄식.

## 고정 표기
- "Metabase MCP" (별도 MCP 서버를 만든 것이 아님)

## 귀속 주의
- 재고 예측 대시보드 도입 제안은 팀장, 설계·구현은 본인.

## 저장 후 처리
- 없음
```
`tests/fixtures/persona/projects/재고 예측 대시보드 구축.md`:
```markdown
---
회사: (주)가상물산
역할: 매니저
시작일: 2024-03-01
종료일: 2024-09-30
영역:
  - AX
  - 데이터
임팩트: 핵심
tags:
  - 주제/커리어
created: 2026-10-02T09:00:00+09:00
modified: 2026-10-02T09:00:00+09:00
version: "1.0"
---
# 개요
재고 회전 데이터를 매일 수집해 품절 위험을 예측하는 대시보드.

# 성과
- 3개월간(2024.06.03–09.02) 품절 발생 품목 수 40개 → 22개 (45% 감소)

> [!note] 귀속
> 도입 제안은 팀장, 설계·구현은 본인.
```
`tests/fixtures/persona/projects/고객 문의 자동 분류 에이전트.md`:
```markdown
---
회사: (주)가상물산
역할: 매니저
시작일: 2025-01-06
종료일: 2025-03-31
영역:
  - AX
임팩트: 핵심
tags:
  - 주제/커리어
created: 2026-10-02T09:00:00+09:00
modified: 2026-10-02T09:00:00+09:00
version: "1.0"
---
# 개요
LLM 에이전트가 고객 문의를 분류하고 담당자가 승인하는 큐.

# 성과
- 약 12주간(2025.01.06–03.31) 운영, 일평균 문의 120건 분류
```
`tests/fixtures/persona/projects/채널 수익성 분석.md`:
```markdown
---
회사: (주)가상물산
역할: 사원
시작일: 2018-01-02
종료일: 2019-12-31
영역:
  - 전략기획
임팩트: 보조
tags:
  - 주제/커리어
created: 2026-10-02T09:00:00+09:00
modified: 2026-10-02T09:00:00+09:00
version: "1.0"
---
# 개요
유통 채널별 공급률과 수익성 시뮬레이션.
```

- [ ] **Step 2: 실패하는 테스트 작성** — `tests/test_config.py`

```python
from datetime import date

import pytest

from scripts import config


def test_load_career_paths(persona_root):
    c = config.load_career(persona_root / "CAREER.md")
    assert c.name == "김하늘"
    assert c.paths["projects"] == persona_root / "projects"
    assert c.paths["insights"] == persona_root / "insights.md"
    assert c.career_start == date(2015, 3, 1)
    assert c.market == "KR"
    assert "## 고정 표기" in c.body


def test_paths_with_korean_and_spaces(persona_root):
    c = config.load_career(persona_root / "CAREER.md")
    assert c.paths["applications"] == persona_root / "지원 이력"


def test_defaults_when_paths_missing(tmp_path):
    p = tmp_path / "CAREER.md"
    p.write_text("---\nname: 이도윤\n---\n", encoding="utf-8")
    c = config.load_career(p)
    assert c.paths["applications"] == tmp_path / "applications"
    assert c.filename_pattern == "{name}_{doc}_{company}"
    assert c.career_start is None


def test_missing_name_raises(tmp_path):
    p = tmp_path / "CAREER.md"
    p.write_text("---\npaths: {}\n---\n", encoding="utf-8")
    with pytest.raises(ValueError, match="name"):
        config.load_career(p)


def test_missing_frontmatter_raises(tmp_path):
    p = tmp_path / "CAREER.md"
    p.write_text("# 설정\n", encoding="utf-8")
    with pytest.raises(ValueError, match="frontmatter"):
        config.load_career(p)


@pytest.mark.parametrize("raw", ["(주)샘플커머스", "㈜샘플커머스", "주식회사 샘플 커머스", " 샘플커머스 "])
def test_normalize_company_variants(raw):
    assert config.normalize_company(raw) == "샘플커머스"


def test_submission_name(persona_root):
    c = config.load_career(persona_root / "CAREER.md")
    assert config.submission_name(c, "이력서", "(주)샘플커머스") == "김하늘_이력서_샘플커머스.pdf"
    assert config.submission_name(c, "포트폴리오") == "김하늘_포트폴리오.pdf"
    assert config.submission_name(c, "경력기술서", "샘플커머스", ext=None) == "김하늘_경력기술서_샘플커머스"
    with pytest.raises(ValueError):
        config.submission_name(c, "자기소개서", "샘플커머스")


def test_statuses_exact():
    assert config.STATUSES == ("준비 중", "서류 제출", "서류 전형", "서류 탈락", "면접", "최종 합격", "불합격", "지원 취소")
```

- [ ] **Step 3: 실패 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_config.py -q`
Expected: FAIL (`scripts.config` 없음)

- [ ] **Step 4: 구현** — `scripts/config.py`

```python
"""CAREER.md 설정 로더와 제출 파일명 규칙."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

DOC_TYPES = ("이력서", "경력기술서", "포트폴리오")
STATUSES = ("준비 중", "서류 제출", "서류 전형", "서류 탈락", "면접", "최종 합격", "불합격", "지원 취소")
DEFAULT_PATHS = {
    "projects": "projects",
    "applications": "applications",
    "base": "base",
    "insights": "insights.md",
    "output": "output",
}


@dataclass
class Career:
    root: Path
    name: str
    contact: dict
    paths: dict
    market: str = "KR"
    career_start: date | None = None
    filename_pattern: str = "{name}_{doc}_{company}"
    money_policy: str = "allow"
    body: str = ""


def read_frontmatter(path: Path) -> tuple[dict, str]:
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: frontmatter(--- 블록)가 없습니다")
    end = text.index("\n---", 4)
    data = yaml.safe_load(text[4:end]) or {}
    return data, text[end + 4:].lstrip("\n")


def _resolve(root: Path, value: str) -> Path:
    s = str(value)
    if s.startswith("~") or s.startswith("/"):
        return Path(s).expanduser()
    return root / s


def load_career(path) -> Career:
    path = Path(path).expanduser()
    if not path.is_file():
        raise ValueError(f"CAREER.md를 찾을 수 없습니다: {path}")
    fm, body = read_frontmatter(path)
    if not fm.get("name"):
        raise ValueError("CAREER.md의 name이 비어 있습니다")
    root = path.parent
    raw = {**DEFAULT_PATHS, **(fm.get("paths") or {})}
    start = fm.get("career_start")
    if isinstance(start, str):
        start = date.fromisoformat(start)
    return Career(
        root=root,
        name=str(fm["name"]),
        contact=fm.get("contact") or {},
        paths={k: _resolve(root, v) for k, v in raw.items()},
        market=fm.get("market", "KR"),
        career_start=start,
        filename_pattern=fm.get("filename_pattern", "{name}_{doc}_{company}"),
        money_policy=fm.get("money_policy", "allow"),
        body=body,
    )


_CORP = re.compile(r"\(주\)|㈜|주식회사|\s+")


def normalize_company(name: str) -> str:
    return _CORP.sub("", name).strip()


def submission_name(career: Career, doc: str, company: str | None = None, ext: str | None = "pdf") -> str:
    if doc not in DOC_TYPES:
        raise ValueError(f"문서종류는 {DOC_TYPES} 중 하나여야 합니다: {doc}")
    if company:
        stem = career.filename_pattern.format(name=career.name, doc=doc, company=normalize_company(company))
    else:
        stem = f"{career.name}_{doc}"
    return f"{stem}.{ext}" if ext else stem


if __name__ == "__main__":
    import json
    import sys

    c = load_career(sys.argv[1])
    print(json.dumps({"name": c.name, "paths": {k: str(v) for k, v in c.paths.items()},
                      "career_start": str(c.career_start) if c.career_start else None}, ensure_ascii=False, indent=2))
```

- [ ] **Step 5: 통과 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_config.py -q`
Expected: 모두 PASS

- [ ] **Step 6: 커밋**

```bash
git add plugins/careerfit/scripts/config.py plugins/careerfit/tests
git commit -m "feat(careerfit): CAREER.md 설정 로더와 제출 파일명 규칙

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: `scripts/chrome.py` — Chrome 탐색과 PDF·스크린샷 렌더

**Files:**
- Create: `plugins/careerfit/scripts/chrome.py`
- Test: `plugins/careerfit/tests/test_chrome.py`

**Interfaces:**
- Produces:
  - `class ChromeNotFound(RuntimeError)`
  - `find_chrome() -> str` — 우선순위: 환경변수 `CAREERFIT_CHROME` → `~/.cache/ms-playwright/chromium-<번호>/chrome-linux64/chrome` 중 번호가 가장 큰 것 → PATH의 `chromium`·`chromium-browser`·`google-chrome`·`google-chrome-stable`. 없으면 `ChromeNotFound`(설치 안내 포함)
  - `render_pdf(html: Path, pdf: Path, chrome: str | None = None) -> Path`
  - `screenshot(html: Path, png: Path, width: int, height: int, chrome: str | None = None) -> Path`
  - CLI: `python3 chrome.py pdf <html> <pdf>` / `python3 chrome.py shot <html> <png> <w> <h>`; Chrome 없으면 stderr에 안내, 종료 코드 2
- Test helper (다음 Task들이 씀): `tests/conftest.py`에 `chrome_or_skip` fixture 추가

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_chrome.py`

```python
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
    r = subprocess.run([sys.executable, str(PLUGIN_ROOT / "scripts" / "chrome.py"), "pdf", "a.html", "a.pdf"],
                       capture_output=True, text=True, env={**os.environ, "HOME": str(tmp_path), "PATH": str(tmp_path)})
    assert r.returncode == 2
    assert "playwright install chromium" in r.stderr
    assert "Traceback" not in r.stderr


def test_render_pdf(tmp_path, chrome_or_skip):
    html = tmp_path / "a.html"
    html.write_text("<style>@page{size:A4}</style><p>안녕하세요</p>", encoding="utf-8")
    out = chrome.render_pdf(html, tmp_path / "a.pdf", chrome_or_skip)
    assert out.exists() and out.stat().st_size > 1000
```

`tests/conftest.py`에 추가:
```python
@pytest.fixture
def chrome_or_skip():
    from scripts import chrome
    try:
        return chrome.find_chrome()
    except chrome.ChromeNotFound:
        pytest.skip("헤드리스 Chrome 없음")
```

- [ ] **Step 2: 실패 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_chrome.py -q`
Expected: FAIL (`scripts.chrome` 없음)

- [ ] **Step 3: 구현** — `scripts/chrome.py`

```python
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
        return max(cands, key=lambda c: int(re.search(r"chromium-(\d+)", c).group(1)))
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        found = shutil.which(name)
        if found:
            return found
    raise ChromeNotFound(GUIDE)


def _run(args: list[str]) -> None:
    subprocess.run(args, capture_output=True, text=True, timeout=180)


def render_pdf(html, pdf, chrome: str | None = None) -> Path:
    chrome = chrome or find_chrome()
    pdf = Path(pdf)
    _run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", f"--print-to-pdf={pdf}",
          "--no-pdf-header-footer", "--print-to-pdf-no-header", Path(html).resolve().as_uri()])
    if not pdf.exists():
        raise RuntimeError(f"PDF가 만들어지지 않았습니다: {pdf}")
    return pdf


def screenshot(html, png, width: int, height: int, chrome: str | None = None) -> Path:
    chrome = chrome or find_chrome()
    png = Path(png)
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
```

- [ ] **Step 4: 통과 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_chrome.py -q`
Expected: 모두 PASS (Chrome이 없는 환경이면 `test_render_pdf`만 SKIP)

- [ ] **Step 5: 커밋**

```bash
git add plugins/careerfit/scripts/chrome.py plugins/careerfit/tests
git commit -m "feat(careerfit): 헤드리스 Chrome 탐색과 PDF·스크린샷 렌더

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: `scripts/pdf_check.py` — PDF 크기·쪽수·폰트·빈 쪽·서명만 쪽·ATS 띄어쓰기

**Files:**
- Create: `plugins/careerfit/scripts/pdf_check.py`
- Test: `plugins/careerfit/tests/test_pdf_check.py`

**Interfaces:**
- Consumes: `chrome.render_pdf` (테스트에서 PDF 생성)
- Produces:
  - `SIZES = {"A4": (209.9, 297.0), "slide": (297.0, 166.9)}`
  - `space_ratio(text: str) -> float` — 공백 문자(`' '`) 수 / 전체 문자 수(줄바꿈 제외)
  - `check_pdf(path, kind: str = "A4", max_pages: int | None = None, font_prefixes: tuple[str, ...] = ("Nanum",), tol_mm: float = 1.5) -> dict` 반환 키: `pages:int`, `width_mm:float`, `height_mm:float`, `fonts:list[str]`, `page_chars:list[int]`, `blank_pages:list[int]`, `sign_only_last_page:bool`, `space_ratio:float`, `problems:list[dict]`(각 `{"rule": str, "severity": "필수"|"권장", "message": str}`)
  - 규칙 ID: `PDF_SIZE`(필수), `PDF_MAX_PAGES`(필수), `PDF_FONT`(필수), `PDF_BLANK_PAGE`(필수), `PDF_SIGN_ONLY_PAGE`(필수), `PDF_ATS_SPACING`(권장, 한글이 있고 space_ratio < 0.05)
  - CLI: `python3 pdf_check.py <pdf> [--kind A4|slide] [--max-pages N]` → JSON 출력, `problems`에 필수가 있으면 종료 코드 1

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_pdf_check.py`

```python
import pytest

from scripts import chrome, pdf_check

A4 = "<style>@page{size:A4;margin:14mm}body{font-family:'NanumGothic'}.pb{break-after:page}</style>"


def _pdf(tmp_path, body, chrome_path, name="d"):
    html = tmp_path / f"{name}.html"
    html.write_text(A4 + body, encoding="utf-8")
    return chrome.render_pdf(html, tmp_path / f"{name}.pdf", chrome_path)


def test_space_ratio():
    assert pdf_check.space_ratio("가 나 다") == pytest.approx(2 / 5)
    assert pdf_check.space_ratio("") == 0.0


def test_a4_ok(tmp_path, chrome_or_skip):
    p = _pdf(tmp_path, "<p>" + "경력 요약 문장입니다. " * 40 + "</p>", chrome_or_skip)
    r = pdf_check.check_pdf(p, "A4")
    assert r["pages"] == 1
    assert abs(r["width_mm"] - 209.9) < 1.5 and abs(r["height_mm"] - 297.0) < 1.5
    assert all(f.startswith("Nanum") for f in r["fonts"])
    assert not [x for x in r["problems"] if x["severity"] == "필수"]


def test_sign_only_last_page(tmp_path, chrome_or_skip):
    body = "<p class='pb'>" + "본문 " * 50 + "</p><p>위 기재 사항은 사실과 다름없음을 확인합니다. 작성자: 김하늘</p>"
    r = pdf_check.check_pdf(_pdf(tmp_path, body, chrome_or_skip), "A4")
    assert r["sign_only_last_page"] is True
    assert "PDF_SIGN_ONLY_PAGE" in [x["rule"] for x in r["problems"]]


def test_blank_page_and_max_pages(tmp_path, chrome_or_skip):
    body = "<p class='pb'>첫 쪽</p><div class='pb'></div><p>셋째 쪽 내용입니다 " * 3 + "</p>"
    r = pdf_check.check_pdf(_pdf(tmp_path, body, chrome_or_skip), "A4", max_pages=2)
    rules = [x["rule"] for x in r["problems"]]
    assert "PDF_BLANK_PAGE" in rules and "PDF_MAX_PAGES" in rules


def test_wrong_size_flagged(tmp_path, chrome_or_skip):
    html = tmp_path / "s.html"
    html.write_text("<style>@page{size:297mm 167mm;margin:0}</style><p>슬라이드</p>", encoding="utf-8")
    r = pdf_check.check_pdf(chrome.render_pdf(html, tmp_path / "s.pdf", chrome_or_skip), "A4")
    assert "PDF_SIZE" in [x["rule"] for x in r["problems"]]
```

- [ ] **Step 2: 실패 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_pdf_check.py -q`
Expected: FAIL (`scripts.pdf_check` 없음)

- [ ] **Step 3: 구현** — `scripts/pdf_check.py`

```python
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
    last = texts[-1]
    sign_only = len(texts) > 1 and chars[-1] < 80 and any(m in last for m in SIGN_MARKERS)
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
                         "message": f"추출 텍스트의 띄어쓰기 비율 {ratio:.3f} — 채용 시스템 파싱에서 단어가 붙어 읽힐 수 있음"})
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
```

- [ ] **Step 4: 통과 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_pdf_check.py -q`
Expected: 모두 PASS (Chrome 없으면 렌더 테스트 SKIP, `test_space_ratio`는 PASS)

- [ ] **Step 5: 커밋**

```bash
git add plugins/careerfit/scripts/pdf_check.py plugins/careerfit/tests/test_pdf_check.py
git commit -m "feat(careerfit): PDF 기계 검사 (크기·쪽수·폰트·빈 쪽·서명만 쪽·ATS 띄어쓰기)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: `scripts/lint_docs.py` (1) — 보이는 텍스트 추출·금지어·타사명·숨은 텍스트·title

**Files:**
- Create: `plugins/careerfit/scripts/lint_docs.py`
- Test: `plugins/careerfit/tests/test_lint_basic.py`

**Interfaces:**
- Consumes: `config.normalize_company`
- Produces:
  - `Finding = dict` 키 `rule:str`, `severity:"필수"|"권장"|"사소"`, `doc:str`, `excerpt:str`(앞뒤 20자), `message:str`
  - `visible_text(path) -> str` — `.html`: 주석·`<script>`·`<style>`·`data:` URI 제거 후 태그 제거·엔티티 해제·공백 정리. `.md`: frontmatter·HTML 주석 제거. `.pdf`: pypdf 추출
  - `hidden_text(path) -> list[str]` — `.html`의 HTML 주석 내용 목록(빈 주석·조건부 주석 제외)
  - `find_banned(text: str, doc: str) -> list[Finding]` — 규칙 `EM_DASH`(필수, `—`), `FIRST_PERSON`(필수, `(?<![가-힣])(저는|제가)`), `EMOJI`(필수), `HYPE_CANDIDATE`(권장, `최초|유일|전담|전국|완벽|혁신적` — 노트 대조는 에이전트가 함)
  - `find_other_companies(text: str, company: str, known: list[str], doc: str) -> list[Finding]` — 규칙 `OTHER_COMPANY`(필수). `known`의 각 회사명을 `normalize_company`로 정규화해 본문(공백 제거본)에서 찾고, 대상 회사는 제외
  - `check_title(html_path, expected_stem: str) -> list[Finding]` — 규칙 `TITLE_MISMATCH`(필수)
  - `check_hidden(path) -> list[Finding]` — 규칙 `HIDDEN_COMMENT`(권장, 주석이 있으면 내용 앞 40자 보고)

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_lint_basic.py`

```python
from scripts import lint_docs as L


def _html(tmp_path, body, title="김하늘_이력서_샘플커머스", name="r.html"):
    p = tmp_path / name
    p.write_text(f"<title>{title}</title><style>.a::before{{content:'—'}}</style>{body}", encoding="utf-8")
    return p


def rules(fs):
    return [f["rule"] for f in fs]


def test_em_dash_and_first_person(tmp_path):
    t = L.visible_text(_html(tmp_path, "<p>성과 — 저는 이렇게 했습니다. 재고 통제가 필요했음.</p>"))
    fs = L.find_banned(t, "r.html")
    assert rules(fs).count("EM_DASH") == 1
    assert rules(fs).count("FIRST_PERSON") == 1  # "통제가"는 오탐하지 않는다


def test_comments_scripts_datauri_ignored(tmp_path):
    body = ("<!-- 주석 — 12.6% --><script>var a='—';</script>"
            "<img src='data:image/jpeg;base64,/9j/4AAQ—SkZJRg=='><p>본문 문장</p>")
    t = L.visible_text(_html(tmp_path, body))
    assert "—" not in t and "12.6" not in t and "base64" not in t
    assert "본문 문장" in t


def test_hidden_comment_flagged_separately(tmp_path):
    p = _html(tmp_path, "<!-- 내부 메모: 실제 매출 12억 --><p>본문</p>")
    assert L.hidden_text(p) == ["내부 메모: 실제 매출 12억"]
    assert rules(L.check_hidden(p)) == ["HIDDEN_COMMENT"]


def test_other_company_variants(tmp_path):
    t = L.visible_text(_html(tmp_path, "<p>(주)샘플커머스 지원. 주식회사 가상 컴퍼니의 AX팀은...</p>"))
    fs = L.find_other_companies(t, "샘플커머스", ["(주)샘플커머스", "㈜가상컴퍼니", "다른회사"], "r.html")
    assert rules(fs) == ["OTHER_COMPANY"]
    assert "가상컴퍼니" in fs[0]["message"]


def test_title_mismatch(tmp_path):
    p = _html(tmp_path, "<p>x</p>", title="김하늘 이력서")
    assert rules(L.check_title(p, "김하늘_이력서_샘플커머스")) == ["TITLE_MISMATCH"]
    assert L.check_title(_html(tmp_path, "<p>x</p>", name="ok.html"), "김하늘_이력서_샘플커머스") == []


def test_markdown_frontmatter_stripped(tmp_path):
    p = tmp_path / "경력기술서.md"
    p.write_text("---\nmodified: 2026-10-02T09:00:00+09:00\n---\n# 경력기술서\n본문 — 끝\n", encoding="utf-8")
    t = L.visible_text(p)
    assert "modified" not in t and "본문" in t
    assert rules(L.find_banned(t, "md")) == ["EM_DASH"]
```

- [ ] **Step 2: 실패 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_lint_basic.py -q`
Expected: FAIL (`scripts.lint_docs` 없음)

- [ ] **Step 3: 구현** — `scripts/lint_docs.py` (이 Task에서는 아래 함수만. Task 6·7에서 이어 붙인다)

```python
"""제출 서류 린트: 금지어·타사명·숨은 텍스트·title·주장 원장·기간·버전·링크."""
from __future__ import annotations

import html as _html
import re
from pathlib import Path

from pypdf import PdfReader

from scripts.config import normalize_company

COMMENT = re.compile(r"<!--(.*?)-->", re.S)
BLOCKS = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)
DATA_URI = re.compile(r"data:[a-z]+/[a-z0-9.+-]+;base64,[A-Za-z0-9+/=—\-]+", re.I)
TAG = re.compile(r"<[^>]+>")
BANNED = [
    ("EM_DASH", "필수", re.compile(r"—"), "em dash 사용 금지"),
    ("FIRST_PERSON", "필수", re.compile(r"(?<![가-힣])(저는|제가)"), "'저는/제가' 사용 금지"),
    ("EMOJI", "필수", re.compile("[\U0001F300-\U0001FAFF☀-➿]"), "이모지 사용 금지"),
    ("HYPE_CANDIDATE", "권장", re.compile(r"최초|유일|전담|전국|완벽|혁신적"), "과장 수식어 후보 — 출처 노트와 대조 필요"),
]


def _excerpt(text: str, start: int, end: int) -> str:
    return text[max(0, start - 20):end + 20].replace("\n", " ")


def _finding(rule, severity, doc, excerpt, message):
    return {"rule": rule, "severity": severity, "doc": str(doc), "excerpt": excerpt, "message": message}


def visible_text(path) -> str:
    p = Path(path)
    if p.suffix == ".pdf":
        return "\n".join(pg.extract_text() or "" for pg in PdfReader(str(p)).pages)
    s = p.read_text(encoding="utf-8")
    if p.suffix == ".md":
        if s.startswith("---\n"):
            s = s[s.index("\n---", 4) + 4:]
        return COMMENT.sub("", s)
    s = COMMENT.sub(" ", s)
    s = BLOCKS.sub(" ", s)
    s = DATA_URI.sub(" ", s)
    s = re.sub(r"<title>.*?</title>", " ", s, flags=re.S)
    s = _html.unescape(TAG.sub(" ", s))
    return re.sub(r"[ \t]+", " ", s)


def hidden_text(path) -> list[str]:
    s = Path(path).read_text(encoding="utf-8")
    out = []
    for m in COMMENT.finditer(s):
        c = m.group(1).strip()
        if c and not c.startswith("["):
            out.append(c)
    return out


def find_banned(text: str, doc) -> list[dict]:
    out = []
    for rule, sev, rx, msg in BANNED:
        for m in rx.finditer(text):
            out.append(_finding(rule, sev, doc, _excerpt(text, m.start(), m.end()), msg))
    return out


def find_other_companies(text: str, company: str, known: list[str], doc) -> list[dict]:
    target = normalize_company(company)
    flat = re.sub(r"\s+", "", text.replace("(주)", "").replace("㈜", "").replace("주식회사", ""))
    out = []
    for k in known:
        name = normalize_company(k)
        if not name or name == target:
            continue
        i = flat.find(name)
        if i != -1:
            out.append(_finding("OTHER_COMPANY", "필수", doc, flat[max(0, i - 15):i + len(name) + 15],
                                f"다른 회사명 '{name}'이 남아 있음"))
    return out


def check_title(html_path, expected_stem: str) -> list[dict]:
    s = Path(html_path).read_text(encoding="utf-8")
    m = re.search(r"<title>(.*?)</title>", s, re.S)
    actual = m.group(1).strip() if m else ""
    if actual != expected_stem:
        return [_finding("TITLE_MISMATCH", "필수", html_path, actual, f"<title>은 '{expected_stem}'이어야 함")]
    return []


def check_hidden(path) -> list[dict]:
    return [_finding("HIDDEN_COMMENT", "권장", path, c[:40], "HTML 주석이 남아 있음 — 공유·발행 시 노출될 수 있음")
            for c in hidden_text(path)]
```

- [ ] **Step 4: 통과 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_lint_basic.py -q`
Expected: 모두 PASS

- [ ] **Step 5: 커밋**

```bash
git add plugins/careerfit/scripts/lint_docs.py plugins/careerfit/tests/test_lint_basic.py
git commit -m "feat(careerfit): 문서 린트 1단계 (보이는 텍스트·금지어·타사명·숨은 주석·title)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: `scripts/lint_docs.py` (2) — 주장 원장 대조·기간 계산·총 경력 연수

**Files:**
- Modify: `plugins/careerfit/scripts/lint_docs.py` (함수 추가)
- Create: `plugins/careerfit/tests/fixtures/claims.md`
- Test: `plugins/careerfit/tests/test_lint_claims.py`

**Interfaces:**
- Produces:
  - `class Claim` (dataclass): `id:str`, `text:str`, `value:str`, `source:str`, `attribution:str`, `forbidden:list[str]`
  - `parse_claims(md_text: str) -> list[Claim]` — `| C\d+ |`로 시작하는 표 행만 읽는다. 6열(ID·주장·값·출처·귀속·금지). 금지 열에서 큰따옴표(`"…"` 또는 `“…”`) 안 문구 중 `→`의 왼쪽에 있는 것만 금지 표현으로 본다
  - `numbers_in(text: str) -> set[tuple[str, str]]` — `(값, 단위)` 쌍. 값은 쉼표 제거, 단위 목록 `%p|%|부|권|개|명|년|개월|주|일|원|억|만|회|종|건|곳|쪽|배`
  - `check_claims(text: str, claims: list[Claim], doc) -> list[Finding]` — `FORBIDDEN_EXPRESSION`(필수), `NUMBER_NOT_IN_CLAIMS`(권장)
  - `check_periods(text: str, doc) -> list[Finding]` — `PERIOD_MISMATCH`(필수). 패턴: `[약 ]N(개월|주|일)[간] (YYYY.MM.DD–[YYYY.]MM.DD)`. 허용 오차: 개월 0.5(약이 붙으면 0.75), 주 1(약 1.5), 일 1
  - `check_total_years(text: str, start: date, ref: date, doc) -> list[Finding]` — `CAREER_YEARS`(필수). `총 N년`은 만 연수와 같아야 하고, `N년째`·`N년간`은 만 연수 또는 +1

- [ ] **Step 1: fixture 작성** — `tests/fixtures/claims.md`

```markdown
| ID | 주장(서류에 쓸 표기) | 값 | 출처 노트 | 귀속 | 금지·주의 표현 |
|---|---|---|---|---|---|
| C01 | 3개월간 품절 발생 품목 수 40개 → 22개 (45% 감소) | 40개, 22개, 45%, 2024.06.03–09.02 | projects/재고 예측 대시보드 구축.md | 제안: 팀장, 설계·구현: 본인 | "최대 50% 감소" → "45% 감소" |
| C02 | 일평균 문의 120건 분류 | 120건 | projects/고객 문의 자동 분류 에이전트.md | 본인 | "완전 자동" → "담당자 승인" ; "실시간" |
```

- [ ] **Step 2: 실패하는 테스트 작성** — `tests/test_lint_claims.py`

```python
from datetime import date

from conftest import FIXTURES
from scripts import lint_docs as L

CLAIMS = L.parse_claims((FIXTURES / "claims.md").read_text(encoding="utf-8"))


def rules(fs):
    return [f["rule"] for f in fs]


def test_parse_claims():
    assert [c.id for c in CLAIMS] == ["C01", "C02"]
    assert CLAIMS[0].forbidden == ["최대 50% 감소"]
    assert CLAIMS[1].forbidden == ["완전 자동", "실시간"]
    assert "팀장" in CLAIMS[0].attribution


def test_forbidden_expression():
    fs = L.check_claims("품절 품목이 최대 50% 감소했음.", CLAIMS, "d")
    assert "FORBIDDEN_EXPRESSION" in rules(fs)


def test_number_not_in_claims():
    fs = L.check_claims("문의 120건 분류, 응답 시간 30% 단축", CLAIMS, "d")
    assert rules(fs) == ["NUMBER_NOT_IN_CLAIMS"]
    assert "30%" in fs[0]["message"]


def test_number_format_variants_match_claims():
    assert L.check_claims("문의 120 건을 분류, 품절 40개 → 22개, 45 % 감소", CLAIMS, "d") == []
    claims = L.parse_claims("| C09 | 요청 16,376부 중 12.6% | 16,376부, 12.6% | n | 본인 | |")
    assert L.check_claims("요청 16376부 중 12.6 %", claims, "d") == []


def test_period_two_months_vs_36_days():
    fs = L.check_periods("2개월간(2026.06.04–07.09) 운영", "d")
    assert rules(fs) == ["PERIOD_MISMATCH"]


def test_period_ok_cases():
    assert L.check_periods("약 5주간(2026.06.04–07.09) 운영", "d") == []
    assert L.check_periods("3개월간(2026.06.29–09.29) 지사 요청", "d") == []
    assert L.check_periods("약 12주간(2025.01.06–2025.03.31) 운영", "d") == []


def test_total_years():
    ref = date(2026, 10, 2)
    start = date(2014, 9, 1)
    assert rules(L.check_total_years("11년째 콘텐츠 산업에서", start, ref, "d")) == ["CAREER_YEARS"]
    assert L.check_total_years("총 12년, 12년간 콘텐츠 산업에서", start, ref, "d") == []
    assert rules(L.check_total_years("총 13년", start, ref, "d")) == ["CAREER_YEARS"]
```

- [ ] **Step 3: 실패 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_lint_claims.py -q`
Expected: FAIL (`parse_claims` 없음)

- [ ] **Step 4: 구현** — `scripts/lint_docs.py` 끝에 추가 (파일 상단 import에 `from dataclasses import dataclass, field`, `from datetime import date` 추가)

```python
@dataclass
class Claim:
    id: str
    text: str
    value: str
    source: str
    attribution: str
    forbidden: list = field(default_factory=list)


QUOTED = re.compile(r"[\"“]([^\"”]+)[\"”]")


def parse_claims(md_text: str) -> list:
    out = []
    for line in md_text.splitlines():
        if not re.match(r"^\|\s*C\d+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        cells += [""] * (6 - len(cells))
        forbidden = []
        for seg in cells[5].split(";"):
            left = seg.split("→", 1)[0]
            forbidden += QUOTED.findall(left)
        out.append(Claim(cells[0], cells[1], cells[2], cells[3], cells[4], forbidden))
    return out


UNITS = r"%p|%|부|권|개월|개|명|년|주|일|원|억|만|회|종|건|곳|쪽|배"
NUM = re.compile(r"(?<![\d.,])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*(" + UNITS + r")")


def numbers_in(text: str) -> set:
    return {(v.replace(",", ""), u) for v, u in NUM.findall(text)}


def check_claims(text: str, claims: list, doc) -> list:
    out = []
    for c in claims:
        for phrase in c.forbidden:
            i = text.find(phrase)
            if i != -1:
                out.append(_finding("FORBIDDEN_EXPRESSION", "필수", doc, _excerpt(text, i, i + len(phrase)),
                                    f"{c.id}의 금지 표현 '{phrase}'"))
    allowed = set()
    for c in claims:
        allowed |= numbers_in(c.text) | numbers_in(c.value)
    for v, u in sorted(numbers_in(text) - allowed):
        out.append(_finding("NUMBER_NOT_IN_CLAIMS", "권장", doc, f"{v}{u}",
                            f"주장 원장에 없는 숫자 '{v}{u}' — 원장에 추가하고 출처를 확인"))
    return out


PERIOD = re.compile(
    r"(약\s*)?(\d+)\s*(개월|주|일)간?\s*\(\s*(\d{4})\.(\d{1,2})\.(\d{1,2})\s*[–\-~]\s*(?:(\d{4})\.)?(\d{1,2})\.(\d{1,2})\s*\)")


def check_periods(text: str, doc) -> list:
    out = []
    for m in PERIOD.finditer(text):
        approx, n, unit = bool(m.group(1)), int(m.group(2)), m.group(3)
        y1, mo1, d1 = int(m.group(4)), int(m.group(5)), int(m.group(6))
        y2 = int(m.group(7)) if m.group(7) else y1
        days = (date(y2, int(m.group(8)), int(m.group(9))) - date(y1, mo1, d1)).days
        if unit == "개월":
            actual, tol = days / 30.44, (0.75 if approx else 0.5)
        elif unit == "주":
            actual, tol = days / 7, (1.5 if approx else 1.0)
        else:
            actual, tol = days, 1
        if abs(actual - n) > tol:
            out.append(_finding("PERIOD_MISMATCH", "필수", doc, m.group(0),
                                f"'{n}{unit}'이지만 실제 기간은 {days}일(≈{actual:.1f}{unit})"))
    return out


def _full_years(start: date, ref: date) -> int:
    return ref.year - start.year - ((ref.month, ref.day) < (start.month, start.day))


def check_total_years(text: str, start: date, ref: date, doc) -> list:
    years = _full_years(start, ref)
    out = []
    for m in re.finditer(r"총\s*(\d+)\s*년(?!\s*\d+\s*개월)", text):
        if int(m.group(1)) != years:
            out.append(_finding("CAREER_YEARS", "필수", doc, m.group(0), f"총 경력은 만 {years}년"))
    for m in re.finditer(r"(\d+)\s*년(째|간)", text):
        if int(m.group(1)) not in (years, years + 1):
            out.append(_finding("CAREER_YEARS", "필수", doc, m.group(0), f"경력 연수는 만 {years}년(또는 {years + 1}년째)"))
    return out
```

- [ ] **Step 5: 통과 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_lint_claims.py plugins/careerfit/tests/test_lint_basic.py -q`
Expected: 모두 PASS

- [ ] **Step 6: 커밋**

```bash
git add plugins/careerfit/scripts/lint_docs.py plugins/careerfit/tests
git commit -m "feat(careerfit): 문서 린트 2단계 (주장 원장 대조·기간 계산·총 경력 연수)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: `scripts/lint_docs.py` (3) — 제출본 버전 일치·링크·통합 CLI

**Files:**
- Modify: `plugins/careerfit/scripts/lint_docs.py`
- Test: `plugins/careerfit/tests/test_lint_cli.py`

**Interfaces:**
- Consumes: Task 5·6의 함수, `config.load_career`, `config.normalize_company`, `config.read_frontmatter`
- Produces:
  - `check_version(html_path, pdf_path) -> list[Finding]` — `VERSION_MISMATCH`(필수): HTML 보이는 텍스트(공백 제거)의 12자 조각 중 PDF 텍스트(공백 제거)에 있는 비율이 0.9 미만. `PDF_OLDER_THAN_HTML`(권장): PDF mtime < HTML mtime
  - `URL = re.compile(r"https?://[^\s<>\"')]+")`
  - `check_links(text: str, doc, fetch=None) -> list[Finding]` — `fetch(url) -> int`(상태 코드, 기본은 `urllib` HEAD, timeout 8초, 실패 시 0). `LINK_BROKEN`(필수, 0 또는 400 이상), `ARTIFACT_LINK`(권장, `claude.ai/artifact` 링크는 항상 "공유 권한 확인")
  - `known_companies(applications_dir: Path) -> list[str]` — 각 하위 폴더 `공고.md`의 `회사` 값 + 폴더명 첫 단어
  - `lint(career_md, company, docs: list[Path], claims_md=None, pairs: list[tuple[Path, Path]] = (), ref: date | None = None, fetch=None) -> list[Finding]`
  - CLI: `python3 lint_docs.py --career CAREER.md --company 샘플커머스 [--claims claims.md] [--pair a.html:a.pdf ...] [--offline] doc1 doc2 ...` → JSON 배열 출력, 필수가 있으면 종료 코드 1. `--offline`이면 링크 검사에서 fetch를 하지 않고 `ARTIFACT_LINK`만 낸다

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_lint_cli.py`

```python
import json
import subprocess
import sys

from conftest import FIXTURES, PLUGIN_ROOT
from scripts import lint_docs as L


def rules(fs):
    return [f["rule"] for f in fs]


def test_check_links_injected_fetch():
    t = "포트폴리오 https://example.com/ok 와 https://example.com/dead 그리고 https://claude.ai/artifact/AbC"
    codes = {"https://example.com/ok": 200, "https://example.com/dead": 404, "https://claude.ai/artifact/AbC": 200}
    fs = L.check_links(t, "d", fetch=lambda u: codes[u])
    assert sorted(rules(fs)) == ["ARTIFACT_LINK", "LINK_BROKEN"]


def test_known_companies(persona_root):
    d = persona_root / "지원 이력" / "샘플커머스 AI PM"
    d.mkdir(parents=True)
    (d / "공고.md").write_text("---\n회사: (주)샘플커머스\n상태: 준비 중\n---\n", encoding="utf-8")
    e = persona_root / "지원 이력" / "다른회사 데이터 분석가"
    e.mkdir()
    (e / "공고.md").write_text("---\n상태: 서류 탈락\n---\n", encoding="utf-8")
    ks = L.known_companies(persona_root / "지원 이력")
    assert "(주)샘플커머스" in ks and "다른회사" in ks


def test_version_mismatch(tmp_path, chrome_or_skip):
    from scripts import chrome
    html = tmp_path / "a.html"
    html.write_text("<style>@page{size:A4}</style><p>" + "첫 번째 버전의 자기소개서 문장입니다. " * 20 + "</p>", encoding="utf-8")
    pdf = chrome.render_pdf(html, tmp_path / "a.pdf", chrome_or_skip)
    assert L.check_version(html, pdf) == []
    html.write_text("<style>@page{size:A4}</style><p>" + "완전히 다른 두 번째 버전으로 고쳐 쓴 내용입니다. " * 20 + "</p>", encoding="utf-8")
    assert "VERSION_MISMATCH" in rules(L.check_version(html, pdf))


def test_cli_exit_code_and_json(persona_root, tmp_path):
    doc = tmp_path / "김하늘_이력서_샘플커머스.html"
    doc.write_text("<title>김하늘_이력서_샘플커머스</title><p>저는 최대 50% 감소를 이뤘습니다 — 총 9년</p>", encoding="utf-8")
    r = subprocess.run([sys.executable, str(PLUGIN_ROOT / "scripts" / "lint_docs.py"),
                        "--career", str(persona_root / "CAREER.md"), "--company", "샘플커머스",
                        "--claims", str(FIXTURES / "claims.md"), "--offline", str(doc)],
                       capture_output=True, text=True)
    assert r.returncode == 1
    found = rules(json.loads(r.stdout))
    for rule in ("FIRST_PERSON", "EM_DASH", "FORBIDDEN_EXPRESSION", "CAREER_YEARS"):
        assert rule in found
```

- [ ] **Step 2: 실패 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_lint_cli.py -q`
Expected: FAIL (`check_links` 없음)

- [ ] **Step 3: 구현** — `scripts/lint_docs.py` 끝에 추가 (상단 import에 `import json, os, sys, urllib.request`, `from scripts.config import load_career, read_frontmatter` 추가)

```python
def _flat(text: str) -> str:
    return re.sub(r"\s+", "", text)


def check_version(html_path, pdf_path) -> list:
    h = _flat(visible_text(html_path))
    p = _flat(visible_text(pdf_path))
    chunks = [h[i:i + 12] for i in range(0, max(len(h) - 12, 0), 12)]
    out = []
    if chunks:
        ratio = sum(1 for c in chunks if c in p) / len(chunks)
        if ratio < 0.9:
            out.append(_finding("VERSION_MISMATCH", "필수", pdf_path, f"일치율 {ratio:.2f}",
                                "PDF가 HTML 최신본과 다름 — PDF를 다시 렌더링"))
    if os.path.getmtime(pdf_path) < os.path.getmtime(html_path):
        out.append(_finding("PDF_OLDER_THAN_HTML", "권장", pdf_path, "", "PDF가 HTML보다 오래됨"))
    return out


URL = re.compile(r"https?://[^\s<>\"')]+")


def _head(url: str) -> int:
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "careerfit-lint"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status
    except Exception:
        return 0


def check_links(text: str, doc, fetch=None) -> list:
    out = []
    for url in sorted(set(URL.findall(text))):
        if "claude.ai/artifact" in url:
            out.append(_finding("ARTIFACT_LINK", "권장", doc, url, "아티팩트는 기본 비공개 — 채용 담당자에게 공유 권한이 있는지 확인"))
            continue
        if fetch is None:
            continue
        code = fetch(url)
        if code == 0 or code >= 400:
            out.append(_finding("LINK_BROKEN", "필수", doc, url, f"링크 응답 {code or '없음'}"))
    return out


def known_companies(applications_dir) -> list:
    out = []
    for d in sorted(Path(applications_dir).glob("*/")):
        f = d / "공고.md"
        if f.is_file():
            try:
                fm, _ = read_frontmatter(f)
                if fm.get("회사"):
                    out.append(str(fm["회사"]))
            except ValueError:
                pass
        out.append(d.name.split()[0])
    return out


def lint(career_md, company, docs, claims_md=None, pairs=(), ref=None, fetch=None) -> list:
    career = load_career(career_md)
    ref = ref or date.today()
    claims = parse_claims(Path(claims_md).read_text(encoding="utf-8")) if claims_md else []
    apps = career.paths["applications"]
    known = known_companies(apps) if apps.is_dir() else []
    out = []
    for d in docs:
        d = Path(d)
        t = visible_text(d)
        out += find_banned(t, d.name)
        out += find_other_companies(t, company, known, d.name)
        out += check_periods(t, d.name)
        if career.career_start:
            out += check_total_years(t, career.career_start, ref, d.name)
        if claims:
            out += check_claims(t, claims, d.name)
        out += check_links(t, d.name, fetch)
        if d.suffix == ".html":
            out += check_title(d, d.stem)
            out += check_hidden(d)
    for h, p in pairs:
        out += check_version(h, p)
    return out


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--career", required=True)
    ap.add_argument("--company", required=True)
    ap.add_argument("--claims")
    ap.add_argument("--pair", action="append", default=[])
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("docs", nargs="+")
    a = ap.parse_args(argv)
    pairs = [tuple(Path(x) for x in p.split(":", 1)) for p in a.pair]
    fs = lint(a.career, a.company, [Path(d) for d in a.docs], a.claims, pairs, fetch=None if a.offline else _head)
    print(json.dumps(fs, ensure_ascii=False, indent=2))
    return 1 if any(f["severity"] == "필수" for f in fs) else 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    sys.exit(main())
```

주의: CLI로 직접 실행할 때 `from scripts.config import ...`가 동작하도록, 파일 맨 위(다른 import보다 먼저)에 다음 두 줄을 둔다:
```python
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
```
(같은 두 줄을 `render_md.py`·`build_variant.py`·`status.py` 맨 위에도 둔다.)

- [ ] **Step 4: 통과 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests -q`
Expected: 모두 PASS (Chrome 없으면 렌더 의존 테스트만 SKIP)

- [ ] **Step 5: 커밋**

```bash
git add plugins/careerfit/scripts/lint_docs.py plugins/careerfit/tests/test_lint_cli.py
git commit -m "feat(careerfit): 문서 린트 3단계 (제출본 버전 일치·링크·통합 CLI)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: `scripts/render_md.py` — 경력기술서 마크다운 → A4 HTML (vault 렌더러 이식)

**Files:**
- Create: `plugins/careerfit/scripts/render_md.py` (원본: `/home/ryanchoi/vault/.claude/skills/career-description/scripts/render_md.py`)
- Create: `plugins/careerfit/templates/career-description.html` (원본: `/home/ryanchoi/vault/.claude/skills/career-description/templates/career-description-template.html`)
- Create: `plugins/careerfit/tests/fixtures/경력기술서.md`
- Test: `plugins/careerfit/tests/test_render_md.py`

**Interfaces:**
- Produces:
  - `render(md_text: str, title: str, target: str, name: str, contact: str, break_projects: bool = False, template: Path = <plugin>/templates/career-description.html) -> str` (HTML 문자열)
  - CLI: `python3 render_md.py <md> <out.html> --title T --target "회사 직무 지원" --name 이름 --contact "메일 · 전화" [--break-projects]` (이름·연락처를 하드코딩하지 않는다)

- [ ] **Step 1: 템플릿 이식** — 원본 템플릿을 `templates/career-description.html`로 복사하고 다음을 바꾼다.
  1. `<title><실명> 경력기술서</title>` → `<title>{{TITLE}}</title>`, meta description 내용 → `{{TARGET}} 경력기술서`
  2. 헤더 예시의 `<실명>`·`[이메일] · [전화번호]` → `{{NAME}}`·`{{CONTACT}}`
  3. `</style>` 바로 앞에 vault 렌더러가 주입하던 CSS를 고정으로 넣는다:
```css
  @media print{ .proj-head{ break-inside:avoid-page; } .job-head{ break-after:avoid-page; } .row.decision{ break-inside:auto; } .row.decision li{ break-inside:avoid-page; } .sign{ margin-top:10px; } }
  table.fit td:first-child{ width:38%; } table.fit td:nth-child(2){ width:22%; font-weight:700; color:var(--accent-strong); } table.fit b{ color:var(--ink); }
```
  4. 본문 예시 중 실제 회사명 `(주)<현 직장>`·`(주)<전 직장>`가 있으면 `(주)회사명`으로 바꾼다.

- [ ] **Step 2: fixture 작성** — `tests/fixtures/경력기술서.md`

```markdown
---
모드: 심층형
---
> [!note] 작성 기준
> 테스트용

# 경력기술서 · 김하늘
샘플커머스 AI PM 지원

## 경력 요약 (총 11년)

| 기간 | 회사 · 소속 · 직급 | 주요 역할 |
|---|---|---|
| 2015.03 – 재직중 | (주)가상물산 · 데이터팀 · 매니저 (생활용품 유통) | 재고 예측·AI 자동화 |

## 공고 요구사항과 경험

| 공고 요구사항 (원문 발췌) | 대응 경험 | 근거 |
|---|---|---|
| **지표** 기반 문제 정의 | 프로젝트 1 · 재고 예측 | 품절 품목 40개 → 22개 |

## 주요 프로젝트 상세

### 1. 재고 예측 대시보드 구축
(주)가상물산 · 2024.03 – 2024.09 · 기획·구현 1인

한 줄 요약: 품절 위험을 미리 보게 만듦.

**문제 정의**
- 품절을 사후에만 알았음. [확인 필요: 이전 월평균 품절 건수]

**주요 의사결정**
- **일 단위 수집**: 주간 집계로는 늦었음.

**결과**
- 3개월간(2024.06.03–09.02) 품절 품목 40개 → 22개.
- 핵심 수치: 품절 45% 감소 · 2개 물류센터 적용

### 2. 고객 문의 자동 분류 에이전트
(주)가상물산 · 2025.01 – 2025.03 · 기획·운영

한 줄 요약: 에이전트 분류, 담당자 승인.

**결과**
- 일평균 문의 120건 분류.

## 회사별 경력 상세

### (주)가상물산 · 데이터팀 매니저 | 2015.03 – 재직중
- **채널 수익성 분석 · 2018**
  - 유통 채널별 공급률 분석

---
위 기재 사항은 사실과 다름없음을 확인합니다. 작성자: 김하늘
```

- [ ] **Step 3: 실패하는 테스트 작성** — `tests/test_render_md.py`

```python
import subprocess
import sys

from conftest import FIXTURES, PLUGIN_ROOT
from scripts import render_md

MD = (FIXTURES / "경력기술서.md").read_text(encoding="utf-8")


def _render(**kw):
    return render_md.render(MD, title="김하늘_경력기술서_샘플커머스", target="샘플커머스 AI PM 지원",
                            name="김하늘", contact="haneul@example.com · 010-0000-0000", **kw)


def test_header_and_title():
    h = _render()
    assert "<title>김하늘_경력기술서_샘플커머스</title>" in h
    assert "<small>김하늘</small>" in h and "haneul@example.com" in h
    assert "<실명>" not in h and "{{" not in h


def test_project_numbering_and_fit_table():
    h = _render()
    assert "프로젝트 1 · 재고 예측 대시보드 구축" in h
    assert "프로젝트 2 · 고객 문의 자동 분류 에이전트" in h
    assert '<table class="fit">' in h and "<th>근거</th>" in h


def test_kpi_chips_todo_and_company_section():
    h = _render()
    assert '<div class="kpi"><span>품절 45% 감소</span><span>2개 물류센터 적용</span></div>' in h
    assert '<mark class="todo">[확인 필요: 이전 월평균 품절 건수]</mark>' in h
    assert '<div class="job"><div class="job-head"><h3>(주)가상물산 · 데이터팀 매니저</h3>' in h
    assert '<div class="item"><div class="t">채널 수익성 분석 · 2018</div>' in h


def test_callout_and_frontmatter_not_rendered():
    h = _render()
    assert "작성 기준" not in h and "모드:" not in h


def test_break_projects_flag():
    assert ".proj + .proj{ break-before:page; }" in _render(break_projects=True)
    assert ".proj + .proj{ break-before:page; }" not in _render()


def test_cli(tmp_path):
    out = tmp_path / "o.html"
    r = subprocess.run([sys.executable, str(PLUGIN_ROOT / "scripts" / "render_md.py"), str(FIXTURES / "경력기술서.md"),
                        str(out), "--title", "T", "--target", "X 지원", "--name", "김하늘", "--contact", "c"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "<title>T</title>" in out.read_text(encoding="utf-8")
```

- [ ] **Step 4: 실패 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_render_md.py -q`
Expected: FAIL (`scripts.render_md` 없음)

- [ ] **Step 5: 구현** — 원본 `render_md.py`를 함수형으로 옮긴다. 원본 본문 로직(표·프로젝트·행·칩·회사별 상세 파싱, `inline`, `table`, 상태 dict `st`, `close_*` 함수들, 메인 루프)은 그대로 쓰고 다음만 바꾼다.
  1. 모듈 최상단의 `sys.argv` 처리·`CONTACT` 상수·`TPL` 상수·`extra` CSS 문자열 주입을 지운다.
  2. 메인 루프를 `def render(md_text, title, target, name, contact, break_projects=False, template=DEFAULT_TEMPLATE) -> str:` 안으로 넣고, `md = open(...)` 대신 인자 `md_text`를 쓴다. `o`, `st`는 함수 지역 변수로, `close_*`는 내부 함수로 둔다.
  3. head 생성:
```python
DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "career-description.html"

    tpl = Path(template).read_text(encoding="utf-8")
    head = tpl[:tpl.index("</style>")]
    if break_projects:
        head += "  @media print{ .proj + .proj{ break-before:page; } }\n"
    head += "</style>"
    head = head.replace("{{TITLE}}", html.escape(title)).replace("{{TARGET}}", html.escape(target))
```
  4. 헤더 문자열의 `경력기술서 <small><실명></small>`과 `CONTACT`를 `name`·`contact` 인자로 바꾼다: `'<h1>경력기술서 <small>%s</small></h1>' % html.escape(name)`, `'<div class="contact">%s</div>' % html.escape(contact)`.
  5. CLI:
```python
def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("md"); ap.add_argument("out")
    ap.add_argument("--title", required=True); ap.add_argument("--target", required=True)
    ap.add_argument("--name", required=True); ap.add_argument("--contact", required=True)
    ap.add_argument("--break-projects", action="store_true")
    a = ap.parse_args(argv)
    out = render(Path(a.md).read_text(encoding="utf-8"), a.title, a.target, a.name, a.contact, a.break_projects)
    Path(a.out).write_text(out, encoding="utf-8")
    print(a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
  6. 모듈 docstring의 usage 예시를 새 CLI로 바꾼다(실명 예시 제거).

- [ ] **Step 6: 통과 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_render_md.py -q`
Expected: 모두 PASS

- [ ] **Step 7: 커밋**

```bash
git add plugins/careerfit/scripts/render_md.py plugins/careerfit/templates/career-description.html plugins/careerfit/tests
git commit -m "feat(careerfit): 경력기술서 마크다운 → A4 HTML 렌더러 (이름·연락처 인자화)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: `scripts/build_variant.py` — 포트폴리오 회사판 파생

**Files:**
- Create: `plugins/careerfit/scripts/build_variant.py` (원본 참고: `/home/ryanchoi/.claude/jobs/7a30251d/tmp/portfolio-v3/build_variants.py`)
- Create: `plugins/careerfit/tests/fixtures/deck.html`
- Test: `plugins/careerfit/tests/test_build_variant.py`

**Interfaces:**
- Produces:
  - `build_variant(base_html: str, spec: dict) -> str` — spec 키: `title`(필수), `meta`(필수), `cover_eyebrow`(선택, HTML 문자열), `tagline`(필수, `<div class="tagline">` 안쪽 HTML), `closing`(필수, 연락처 슬라이드 `<div class="sub">` 안쪽 텍스트), `order`(선택, 1부터 시작하는 케이스 번호 목록. 길이는 케이스 수와 같고 각 번호가 한 번씩)
  - 덱 마크업 계약(템플릿·기본본이 지켜야 함): 표지 `<section class="slide cover">` 안의 첫 `<div class="eyebrow">`·`<div class="tagline">`; 목차 `<div class="toc-list">` 안 `<div class="toc-row">` 행들(각 행에 `<span class="num">NN</span>`); 케이스 `<section class="slide v2">`; 그 외 작업 `<section class="slide more">`; 연락처 `<section class="slide contact-page">` 안 `<div class="sub">`; 케이스 번호 표기는 `CASE 0N`
  - 잘못된 `order`면 `ValueError("order는 1..N을 한 번씩 포함해야 합니다")`
  - CLI: `python3 build_variant.py <base.html> <spec.json> <out.html>`

- [ ] **Step 1: fixture 작성** — `tests/fixtures/deck.html`

```html
<title>김하늘_포트폴리오</title>
<meta name="description" content="김하늘 포트폴리오">
<style>@page{size:297mm 167mm;margin:0}</style>
<section class="slide cover">
  <div class="eyebrow">Portfolio · AI · Data</div>
  <h1>김하늘</h1>
  <div class="tagline">데이터로 <b>문제를 푸는</b> 실행가.</div>
</section>
<section class="slide toc">
  <div class="toc-list">
    <div class="toc-row"><span class="num">01</span><span class="title">재고 예측</span></div>
    <div class="toc-row"><span class="num">02</span><span class="title">문의 분류 에이전트</span></div>
    <div class="toc-row"><span class="num">03</span><span class="title">채널 수익성</span></div>
  </div>
</section>
<!-- CASE 01 -->
<section class="slide v2"><div class="eyebrow">CASE 01 · 가상물산</div><h2>재고 예측</h2><p>CASE 02의 분류 결과를 활용</p></section>
<!-- CASE 02 -->
<section class="slide v2"><div class="eyebrow">CASE 02 · 가상물산</div><h2>문의 분류 에이전트</h2></section>
<!-- CASE 03 -->
<section class="slide v2"><div class="eyebrow">CASE 03 · 가상물산</div><h2>채널 수익성</h2><p>CASE 01 참고</p></section>
<section class="slide more"><h2>그 외의 작업</h2></section>
<section class="slide contact-page"><h2>함께 일해요.</h2><div class="sub">언제든 연락 주세요.</div></section>
```

- [ ] **Step 2: 실패하는 테스트 작성** — `tests/test_build_variant.py`

```python
import json
import re
import subprocess
import sys

import pytest

from conftest import FIXTURES, PLUGIN_ROOT
from scripts import build_variant as B

BASE = (FIXTURES / "deck.html").read_text(encoding="utf-8")
SPEC = {"title": "김하늘_포트폴리오_샘플커머스", "meta": "샘플커머스 AI PM 지원용 포트폴리오",
        "cover_eyebrow": "Portfolio · AI PM", "tagline": "AI로 <b>업무 흐름</b>을 바꿉니다.",
        "closing": "AI 과제를 함께 만들 사람이 필요하시다면 연락 주세요.", "order": [2, 3, 1]}


def cases(h):
    return re.findall(r'<section class="slide v2"><div class="eyebrow">(CASE 0\d)[^<]*</div><h2>([^<]+)</h2>', h)


def test_cover_meta_closing():
    h = B.build_variant(BASE, SPEC)
    assert "<title>김하늘_포트폴리오_샘플커머스</title>" in h
    assert 'content="샘플커머스 AI PM 지원용 포트폴리오"' in h
    assert '<div class="eyebrow">Portfolio · AI PM</div>' in h
    assert '<div class="tagline">AI로 <b>업무 흐름</b>을 바꿉니다.</div>' in h
    assert '<div class="sub">AI 과제를 함께 만들 사람이 필요하시다면 연락 주세요.</div>' in h


def test_reorder_and_renumber_cases_and_toc():
    h = B.build_variant(BASE, SPEC)
    assert cases(h) == [("CASE 01", "문의 분류 에이전트"), ("CASE 02", "채널 수익성"), ("CASE 03", "재고 예측")]
    assert re.findall(r'<span class="num">(\d\d)</span><span class="title">([^<]+)</span>', h) == [
        ("01", "문의 분류 에이전트"), ("02", "채널 수익성"), ("03", "재고 예측")]


def test_cross_references_remapped():
    h = B.build_variant(BASE, SPEC)
    assert "CASE 01의 분류 결과를 활용" in h  # 재고(이제 03)가 가리키던 분류(02→01)
    assert "CASE 03 참고" in h               # 채널(이제 02)이 가리키던 재고(01→03)


def test_no_order_keeps_cases():
    spec = {k: v for k, v in SPEC.items() if k != "order"}
    assert [c[1] for c in cases(B.build_variant(BASE, spec))] == ["재고 예측", "문의 분류 에이전트", "채널 수익성"]


def test_bad_order():
    with pytest.raises(ValueError, match="order"):
        B.build_variant(BASE, {**SPEC, "order": [1, 1, 2]})


def test_cli(tmp_path):
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps(SPEC, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "o.html"
    r = subprocess.run([sys.executable, str(PLUGIN_ROOT / "scripts" / "build_variant.py"),
                        str(FIXTURES / "deck.html"), str(spec), str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "샘플커머스" in out.read_text(encoding="utf-8")
```

- [ ] **Step 3: 실패 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_build_variant.py -q`
Expected: FAIL (`scripts.build_variant` 없음)

- [ ] **Step 4: 구현** — `scripts/build_variant.py`

```python
"""기본 포트폴리오 덱에서 회사판을 파생: 표지·meta·클로징 교체, 케이스 재배치, 목차·CASE 번호 재매핑."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))

import json
import re
import sys
from pathlib import Path


def _replace_in_section(s: str, section_cls: str, inner_cls: str, new_inner: str) -> str:
    i = s.index(f'<section class="slide {section_cls}">')
    j = s.index("</section>", i)
    seg = s[i:j]
    m = re.search(rf'<div class="{inner_cls}">.*?</div>', seg, re.S)
    if not m:
        raise ValueError(f"{section_cls} 슬라이드에 {inner_cls}가 없습니다")
    return s[:i] + seg[:m.start()] + f'<div class="{inner_cls}">{new_inner}</div>' + seg[m.end():] + s[j:]


def build_variant(base_html: str, spec: dict) -> str:
    s = base_html
    s = re.sub(r"<title>.*?</title>", f"<title>{spec['title']}</title>", s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{spec["meta"]}">', s, count=1)
    if spec.get("cover_eyebrow"):
        s = _replace_in_section(s, "cover", "eyebrow", spec["cover_eyebrow"])
    s = _replace_in_section(s, "cover", "tagline", spec["tagline"])
    s = _replace_in_section(s, "contact-page", "sub", spec["closing"])

    starts = [m.start() for m in re.finditer(r'<section class="slide v2">', s)]
    n = len(starts)
    order = spec.get("order") or list(range(1, n + 1))
    if sorted(order) != list(range(1, n + 1)):
        raise ValueError("order는 1..N을 한 번씩 포함해야 합니다")
    if order != list(range(1, n + 1)):
        end = s.index('<section class="slide more">')
        chunks = []
        for k, a in enumerate(starts):
            b = starts[k + 1] if k + 1 < n else end
            c = s[a:b]
            cut = c.rfind("<!--")
            if cut != -1 and c[cut:].strip().endswith("-->"):
                c = c[:cut]
            chunks.append(c.rstrip() + "\n")
        region_start = s.rfind("<!--", 0, starts[0])
        if region_start == -1 or region_start < s.index('<section class="slide toc">'):
            region_start = starts[0]
        tail = s.rfind("<!--", starts[-1], end)
        end = tail if tail != -1 else end
        s = s[:region_start] + "".join(chunks[o - 1] for o in order) + s[end:]

        i = s.index('<div class="toc-list">') + len('<div class="toc-list">')
        j = s.index("</section>", i)
        j = s.rindex("</div>", i, j)
        rows = re.findall(r'\s*<div class="toc-row">.*?</div>(?=\s*<div class="toc-row">|\s*$)', s[i:j], re.S)
        if len(rows) == n:
            new_rows = [re.sub(r'<span class="num">\d+</span>', f'<span class="num">{p:02d}</span>', rows[o - 1])
                        for p, o in enumerate(order, 1)]
            s = s[:i] + "".join(new_rows) + "\n  " + s[j:]
        mapping = {old: new for new, old in enumerate(order, 1)}
        s = re.sub(r"CASE 0(\d)", lambda m: f"CASE {mapping.get(int(m.group(1)), int(m.group(1))):02d}", s)
    return s


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    if len(argv) != 3:
        print("usage: build_variant.py <base.html> <spec.json> <out.html>", file=sys.stderr)
        return 64
    base = Path(argv[0]).read_text(encoding="utf-8")
    spec = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    Path(argv[2]).write_text(build_variant(base, spec), encoding="utf-8")
    print(argv[2])
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

목차 행 정규식이 fixture에서 3개를 정확히 잡는지 Step 5에서 확인한다. 못 잡으면 `rows` 추출을 "`<div class="toc-row">`로 split한 뒤 각 조각 앞에 다시 붙이는" 방식으로 바꾼다(테스트 `test_reorder_and_renumber_cases_and_toc`가 판정).

- [ ] **Step 5: 통과 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_build_variant.py -q`
Expected: 모두 PASS

- [ ] **Step 6: 커밋**

```bash
git add plugins/careerfit/scripts/build_variant.py plugins/careerfit/tests
git commit -m "feat(careerfit): 포트폴리오 회사판 파생 (표지·클로징 교체, 케이스 재배치, CASE 번호 재매핑)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: `scripts/status.py` — 지원 상태 갱신·지원 목록 스캔

**Files:**
- Create: `plugins/careerfit/scripts/status.py`
- Test: `plugins/careerfit/tests/test_status.py`

**Interfaces:**
- Consumes: `config.STATUSES`, `config.read_frontmatter`
- Produces:
  - `set_status(gonggo_md: Path, status: str, now: str) -> tuple[str | None, str]` — `(이전 상태, 새 상태)`. `status`가 `STATUSES`에 없으면 `ValueError`. frontmatter에 `상태`가 없으면 `aliases:` 줄 앞에(없으면 frontmatter 끝에) `상태: <값>`을 넣는다. `modified:`가 있으면 `now`(ISO 8601 문자열)로 바꾼다. 같은 상태면 파일을 바꾸지 않고 `(같은 값, 같은 값)` 반환
  - `scan(applications_dir: Path) -> list[dict]` — 각 항목 `{"folder": str, "company": str | None, "status": str | None, "applied": str | None, "has_progress": bool}`, 폴더명 정렬
  - CLI: `python3 status.py scan <dir>` → JSON / `python3 status.py set <공고.md> <상태> <now>` → `이전 → 새` 출력

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_status.py`

```python
import pytest

from scripts import status

NOW = "2026-10-02T10:00:00+09:00"


def _app(root, folder, fm):
    d = root / "지원 이력" / folder
    d.mkdir(parents=True)
    (d / "공고.md").write_text(f"---\n{fm}---\n# 공고\n", encoding="utf-8")
    return d / "공고.md"


def test_set_existing_status(persona_root):
    p = _app(persona_root, "샘플커머스 AI PM", "회사: (주)샘플커머스\n상태: 준비 중\nmodified: 2026-09-30T00:00:00+09:00\n")
    assert status.set_status(p, "서류 전형", NOW) == ("준비 중", "서류 전형")
    t = p.read_text(encoding="utf-8")
    assert "상태: 서류 전형" in t and f"modified: {NOW}" in t


def test_insert_missing_status_before_aliases(persona_root):
    p = _app(persona_root, "옛 공고", "tags:\n  - 주제/커리어\naliases:\ncreated: 2026-07-01T00:00:00+09:00\n")
    assert status.set_status(p, "서류 탈락", NOW) == (None, "서류 탈락")
    t = p.read_text(encoding="utf-8")
    assert t.index("상태: 서류 탈락") < t.index("aliases:")


def test_invalid_status(persona_root):
    p = _app(persona_root, "x", "상태: 준비 중\n")
    with pytest.raises(ValueError):
        status.set_status(p, "탈락", NOW)


def test_same_status_no_write(persona_root):
    p = _app(persona_root, "y", "상태: 면접\nmodified: 2026-09-30T00:00:00+09:00\n")
    before = p.read_text(encoding="utf-8")
    assert status.set_status(p, "면접", NOW) == ("면접", "면접")
    assert p.read_text(encoding="utf-8") == before


def test_scan_korean_folder_names(persona_root):
    _app(persona_root, "올리브영 AX 전략 담당자", "회사: 씨제이올리브영\n상태: 서류 전형\n지원일:\n")
    _app(persona_root, "대웅 웰다 AX Engineer", "tags: []\n")
    (persona_root / "지원 이력" / "올리브영 AX 전략 담당자" / "진행 상황.md").write_text("x", encoding="utf-8")
    rows = status.scan(persona_root / "지원 이력")
    assert [r["folder"] for r in rows] == ["대웅 웰다 AX Engineer", "올리브영 AX 전략 담당자"]
    assert rows[0]["status"] is None and rows[1]["status"] == "서류 전형"
    assert rows[1]["has_progress"] is True and rows[1]["company"] == "씨제이올리브영"
```

- [ ] **Step 2: 실패 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_status.py -q`
Expected: FAIL (`scripts.status` 없음)

- [ ] **Step 3: 구현** — `scripts/status.py`

```python
"""지원 상태 갱신과 지원 폴더 스캔."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))

import json
import re
import sys
from pathlib import Path

from scripts.config import STATUSES, read_frontmatter


def set_status(gonggo_md, status: str, now: str):
    if status not in STATUSES:
        raise ValueError(f"상태는 {STATUSES} 중 하나여야 합니다: {status}")
    p = Path(gonggo_md)
    text = p.read_text(encoding="utf-8")
    end = text.index("\n---", 4)
    fm, rest = text[:end], text[end:]
    m = re.search(r"^상태:(.*)$", fm, flags=re.M)
    old = m.group(1).strip() if m else None
    if old == status:
        return old, status
    if m:
        fm = fm[:m.start()] + f"상태: {status}" + fm[m.end():]
    elif "\naliases:" in fm:
        fm = fm.replace("\naliases:", f"\n상태: {status}\naliases:", 1)
    else:
        fm = fm + f"\n상태: {status}"
    fm = re.sub(r"^modified:.*$", f"modified: {now}", fm, count=1, flags=re.M)
    p.write_text(fm + rest, encoding="utf-8")
    return old or None, status


def scan(applications_dir) -> list:
    rows = []
    for d in sorted(Path(applications_dir).iterdir()):
        f = d / "공고.md"
        if not d.is_dir() or not f.is_file():
            continue
        try:
            fm, _ = read_frontmatter(f)
        except ValueError:
            fm = {}
        rows.append({"folder": d.name, "company": fm.get("회사"), "status": fm.get("상태"),
                     "applied": str(fm["지원일"]) if fm.get("지원일") else None,
                     "has_progress": (d / "진행 상황.md").is_file()})
    return rows


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    if argv[:1] == ["scan"] and len(argv) == 2:
        print(json.dumps(scan(argv[1]), ensure_ascii=False, indent=2))
        return 0
    if argv[:1] == ["set"] and len(argv) == 4:
        old, new = set_status(argv[1], argv[2], argv[3])
        print(f"{old or '(없음)'} → {new}")
        return 0
    print("usage: status.py scan <dir> | set <공고.md> <상태> <now>", file=sys.stderr)
    return 64


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 통과 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_status.py -q`
Expected: 모두 PASS

- [ ] **Step 5: 커밋**

```bash
git add plugins/careerfit/scripts/status.py plugins/careerfit/tests/test_status.py
git commit -m "feat(careerfit): 지원 상태 갱신과 지원 폴더 스캔

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 11: 템플릿 — 이력서(A4)·포트폴리오(가로), 개인정보 없음 검증

**Files:**
- Create: `plugins/careerfit/templates/resume.html`
- Create: `plugins/careerfit/templates/portfolio.html`
- Test: `plugins/careerfit/tests/test_templates.py`

**Interfaces:**
- Consumes: Task 9 덱 마크업 계약, Task 8 `templates/career-description.html`
- Produces: 템플릿 자리표시자 — `{{TITLE}}`, `{{META}}`, `{{NAME}}`, `{{NAME_EN}}`, `{{CONTACT}}`, `{{TAGLINE}}`. 이력서 블록 마크업(`.project` > `.p-title`/`.tagline`/`.field`(`.tag` 배경·한 일·성과·기여)), 자기소개서 `.intro-item` 3개(`지원배경`·`강점 및 경험`·`입사 후 포부`), 사진 자리 `<!-- PHOTO: <div class="photo"><img src="data:..."></div> -->`

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_templates.py`

```python
import re

import pytest

from conftest import PLUGIN_ROOT
from scripts import build_variant

T = PLUGIN_ROOT / "templates"
PERSONAL = ["<실명>", "<영문명>", "<메일>", "<전화>", "<현 직장>", "<현 직장>", "<전 직장>", "<회사 도메인>", "<주소>", "1988"]


@pytest.mark.parametrize("name", ["resume.html", "career-description.html", "portfolio.html"])
def test_no_personal_data(name):
    s = (T / name).read_text(encoding="utf-8")
    for w in PERSONAL:
        assert w not in s, f"{name}에 개인정보 '{w}'"
    assert "fonts.googleapis" not in s
    assert "NanumGothic" in s


def test_resume_markers_and_a4():
    s = (T / "resume.html").read_text(encoding="utf-8")
    for m in ("{{TITLE}}", "{{META}}", "{{NAME}}", "{{CONTACT}}", "{{TAGLINE}}", "size: A4", "break-inside:avoid-page"):
        assert m in s
    assert s.count('class="intro-item') == 3
    assert re.search(r"\d+\.\d+%", s) is None  # 예시 성과 수치(정정 전 97.8% 등)가 남지 않음


def test_portfolio_contract_roundtrip():
    s = (T / "portfolio.html").read_text(encoding="utf-8")
    assert "size: 297mm 167mm" in s or "size:297mm 167mm" in s
    n = s.count('<section class="slide v2">')
    assert n >= 2
    out = build_variant.build_variant(s, {"title": "X", "meta": "M", "tagline": "T", "closing": "C",
                                          "order": list(range(n, 0, -1))})
    assert "<title>X</title>" in out and '<div class="sub">C</div>' in out
```

- [ ] **Step 2: 실패 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_templates.py -q`
Expected: FAIL (템플릿 없음)

- [ ] **Step 3: `templates/resume.html` 만들기** — `/home/ryanchoi/vault/.claude/skills/job-application/templates/resume-template.html`을 복사한 뒤:
  1. `<title>`·meta를 `{{TITLE}}`·`{{META}}`로.
  2. 헤더의 이름·영문 이름·연락처·주소·생년월일을 `{{NAME}}`·`{{NAME_EN}}`·`{{CONTACT}}` 한 줄로 바꾸고, 사진 영역은 위 PHOTO 주석으로 바꾼다.
  3. 헤더 태그라인을 `{{TAGLINE}}`으로.
  4. 경력사항: `.job` 1개만 남기고 회사명 `(주)회사명`, 직함 `소속 · 직급`, 기간 `YYYY.MM – 재직중`. 그 안 `.project` 블록은 1개만 남기고 텍스트를 `[프로젝트명] · [연도]`, `[한 줄 태그라인]`, 배경 `[문제 1~2문장]`, 한 일 `<li>[행동 1]</li><li>[행동 2]</li>`, 성과 `[결과 수치 1문장 — 주장 원장 표기]`, 기여 `[본인 역할]`로 바꾼다.
  5. 학력·어학·기술 스택은 구조만 남기고 값은 `[학교] [전공]`, `[시험] [점수]`, `[도구]`로.
  6. 자기소개서 3항목의 예시 문단을 각각 `<p>[회사명]을 첫 문장에 넣은 두괄식 문단. 규칙은 references/writing-rules.md]</p>`로.
  7. 모든 em dash(`—`)는 주석 포함 제거(`·` 또는 `:`로).

- [ ] **Step 4: `templates/portfolio.html` 만들기** — `/home/ryanchoi/vault/Career/<실명>_포트폴리오.html`에서 `<style>` 블록 전체(첫 `<style>`부터 `</style>`까지)만 가져오고, 본문은 아래 뼈대로 새로 쓴다(케이스별 도식 JS는 가져오지 않는다):

```html
<title>{{TITLE}}</title>
<meta name="description" content="{{META}}">
<!-- (가져온 <style> 블록) -->
<section class="slide cover">
  <div class="eyebrow">Portfolio · [분야]</div>
  <h1>{{NAME}}</h1>
  <div class="en">{{NAME_EN}}</div>
  <div class="tagline">{{TAGLINE}}</div>
  <div class="contact">{{CONTACT}}</div>
</section>
<section class="slide toc">
  <div class="eyebrow">Selected Work</div>
  <h2>선정 작업</h2>
  <div class="toc-list">
    <div class="toc-row"><span class="num">01</span><span class="title">[케이스 1 제목]</span><span class="stat">[핵심 결과 한 줄]</span></div>
    <div class="toc-row"><span class="num">02</span><span class="title">[케이스 2 제목]</span><span class="stat">[핵심 결과 한 줄]</span></div>
  </div>
</section>
<section class="slide v2">
  <div class="head"><div class="eyebrow">CASE 01 · [회사] · [기간]</div><h2>[케이스 1 제목]</h2></div>
  <div class="split">
    <div class="stack">
      <div class="lead">[한 문장 결론]</div>
      <div><div class="h">PROBLEM</div><p class="txt">[문제]</p></div>
      <div><div class="h">ACTION</div><p class="txt">[행동]</p></div>
    </div>
    <div class="note">[구조·워크플로 도식 자리: 결과 수치는 넣지 않는다]</div>
  </div>
  <div class="stats">
    <div><div class="v">[결과 수치]</div><div class="k">[설명]</div></div>
    <div><div class="v">[결과 수치]</div><div class="k">[설명]</div></div>
    <div><div class="v">[결과 수치]</div><div class="k">[설명]</div></div>
  </div>
</section>
<section class="slide v2">
  <div class="head"><div class="eyebrow">CASE 02 · [회사] · [기간]</div><h2>[케이스 2 제목]</h2></div>
  <div class="rows"><div class="lead">[한 문장 결론]</div></div>
  <div class="stats"><div><div class="v">[결과 수치]</div><div class="k">[설명]</div></div></div>
</section>
<section class="slide more">
  <div class="eyebrow">More Work</div><h2>그 외의 작업</h2>
  <div class="more-grid"><div class="more-card"><div class="meta">[회사 · 기간]</div><h3>[작업]</h3><p>[한두 문장]</p></div></div>
</section>
<section class="slide skills-career">
  <div><h2>Skills</h2><div class="skill-row"><span class="k">[분류]</span><span>[도구]</span></div></div>
  <div><h2>Career</h2><div class="career-item"><div class="when">[기간]</div><div class="co">[회사 · 소속 · 직급]</div><div class="detail">[요약]</div></div></div>
</section>
<section class="slide contact-page">
  <div class="eyebrow">Get in touch</div>
  <h2>함께 일해요.</h2>
  <div class="sub">[클로징 한 문장]</div>
  <div class="links"><div><div class="k">Email</div><div class="v">{{CONTACT}}</div></div></div>
</section>
```
가져온 `<style>` 안의 em dash·실명 주석은 지운다.

- [ ] **Step 5: 통과 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_templates.py -q`
Expected: 모두 PASS

- [ ] **Step 6: 커밋**

```bash
git add plugins/careerfit/templates plugins/careerfit/tests/test_templates.py
git commit -m "feat(careerfit): 이력서·포트폴리오 템플릿 (개인정보 없는 구조, 덱 마크업 계약 준수)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 12: 공통 규칙 `references/` 7종

**Files:**
- Create: `plugins/careerfit/references/writing-rules.md`
- Create: `plugins/careerfit/references/attribution-and-facts.md`
- Create: `plugins/careerfit/references/confidentiality.md`
- Create: `plugins/careerfit/references/filenames.md`
- Create: `plugins/careerfit/references/jd-capture.md`
- Create: `plugins/careerfit/references/korean-career-description-guide.md`
- Create: `plugins/careerfit/references/schemas.md`
- Test: `plugins/careerfit/tests/test_references.py`

**Interfaces:**
- Produces: 스킬들이 `${CLAUDE_PLUGIN_ROOT}/references/<파일>`로 참조하는 규칙. 각 파일의 필수 문구는 아래 테스트가 고정한다.

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_references.py`

```python
import pytest

from conftest import PLUGIN_ROOT

R = PLUGIN_ROOT / "references"
REQUIRED = {
    "writing-rules.md": ["저는", "em dash", "두괄식", "음슴체", "스케어쿼트", "입사 후 포부"],
    "attribution-and-facts.md": ["귀속", "[확인 필요", "의사결정", "범위 재정의", "최초", "시간 순서"],
    "confidentiality.md": ["내부 시스템", "실명", "금액", "HTML 주석", "사진"],
    "filenames.md": ["{name}_{doc}_{company}", "<title>", "(주)"],
    "jd-capture.md": ["GI_Read", "GI_Read_Comt_Ifrm", "이미지", "제출 서류"],
    "korean-career-description-guide.md": ["문제 → 행동 → 결과", "A4 1~3장", "출처"],
    "schemas.md": ["CAREER.md", "claims.md", "insights.md", "준비 중", "지원 취소", "영역", "임팩트"],
}


@pytest.mark.parametrize("name,words", REQUIRED.items())
def test_reference_contains(name, words):
    s = (R / name).read_text(encoding="utf-8")
    for w in words:
        assert w in s, f"{name}에 '{w}' 없음"


@pytest.mark.parametrize("name", REQUIRED)
def test_reference_no_personal_data(name):
    s = (R / name).read_text(encoding="utf-8")
    for w in ("<실명>", "<현 직장>", "<현 직장>", "<회사 도메인>", "<동료 실명>", "<동료 실명>"):
        assert w not in s
```

- [ ] **Step 2: 실패 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_references.py -q`
Expected: FAIL

- [ ] **Step 3: 파일 작성**

`references/writing-rules.md`:
```markdown
# 문체 규칙 (이력서·경력기술서·포트폴리오 공통)

사용자 `CAREER.md`의 `## 문체 선호`가 이 규칙에 덧붙거나 우선한다.

## 자기소개서 (이력서 안)
- 각 항목(지원배경·강점 및 경험·입사 후 포부) 첫 문장에 회사명 + 핵심 주장 (두괄식)
- "저는"/"제가" 사용 금지
- 성과는 과거·경험형 시제("~했습니다"). 습관형 현재시제("~합니다")로 반복 업무를 서술하지 않는다
- 이모지·em dash(—) 금지
- "첫째/둘째/셋째" 같은 나열형 금지, 짧은 문장으로 이어간다
- 스스로 지어낸 표현에 따옴표 금지 (스케어쿼트). 실제 인용·고유명사는 예외
- 실존 임원은 이름 대신 직책("대표이사", "경영진")
- "입사 후 포부"는 긍정적·전향적 문장으로 끝낸다. 약점·경험 부족을 먼저 꺼내지 않는다
- 한 문장에 한 내용
- 지원배경·포부는 공고마다 새로 쓴다(기본본 문장 재사용 금지)

## 경력기술서
- 개조식은 명사형 종결(~구축, ~달성, ~결정), 문장이 필요한 곳은 짧은 음슴체(~커짐, ~없었음, ~통제함). "~했습니다"체는 쓰지 않는다
- "기여함", "효과가 있었음", "다양한", "성공적으로" 같은 모호어는 수치·구체적 변화로 바꾼다
- 기술 이름은 의사결정과 연결될 때만. 툴 나열 금지
- 자기소개서 문장을 그대로 옮기지 않는다 (자기소개서 = 동기·강점, 경력기술서 = 과정·근거)

## 포트폴리오
- 케이스 = 핵심 프로젝트, 도식 = 구조·워크플로, KPI 카드 = 결과 지표만 (목표치·기능 개수·운영 기간은 카드에 넣지 않는다)
- 보이는 텍스트에 em dash·이모지 금지
```

`references/attribution-and-facts.md`:
```markdown
# 사실관계·귀속·과장어 규칙

서류는 면접에서 한 줄씩 검증당한다. 이력 저장소(프로젝트 노트)에 없는 내용은 쓰지 않는다.

## 귀속
- 누가 제안·승인·지시·실행했는지는 프로젝트 노트의 귀속 콜아웃과 `CAREER.md`의 `## 귀속 주의`를 그대로 따른다. 다른 사람이 제안한 것을 본인이 제안했다고 쓰지 않는다
- 주장 원장(`claims.md`)의 귀속 열을 서류 문장의 주어와 대조한다

## 상태·시제
- 중단된 프로젝트를 "운영 중"으로, 설계안을 "구축"으로 쓰지 않는다
- 노트의 `[!note] 사실관계 정정`·`[!note] 범위 재정의`·`[!note] 신뢰도 메모`를 먼저 읽고 따른다. 범위 재정의가 있으면 그 결론을 쓰고, 범위 밖 활용 사례는 활용 사례로 구분한다

## 의사결정
- 노트에 판단 근거가 있으면 그대로 쓴다
- 없으면 노트에서 실제로 선택이 드러나는 지점(무엇을 택했는지)만 쓰고, 이유는 `[확인 필요: ...]`로 남겨 사용자에게 묻는다
- 흔한 함정(노트에 이유가 없으면 창작): "자동으로 막는 대신 사람이 결정하게 했다", "위험이 낮은 단계부터 검증했다", "빠르게 출시하려고 기존 시스템을 고치지 않았다"
- 시간 순서 표현("먼저", "부터", "이후")은 노트의 날짜로 확인한다. 동시에 시작한 일에 "먼저"를 쓰지 않는다

## 과장 수식어
- "최초", "유일", "전담", "전국", "완벽", "혁신적", "외주"처럼 노트에 없는 강조어는 쓰지 않는다. 쓰려면 노트에 근거가 있어야 한다
- 근거가 약한 수치는 원장에 넣기 전에 출처를 확인하고, 표본이 작은 지표(예: 소수 표본·하루 평가)는 대외 지표로 쓰지 않는다

## 숫자 표기
- 서류는 주장 원장의 표기만 쓴다. 원장에 없는 숫자가 필요하면 원장에 먼저 추가하고 출처를 적는다
- 기간은 날짜로 계산해 맞춘다 ("2개월"이라고 쓰기 전에 실제 일수를 센다)
- 범위·분포는 정확히 쓴다 ("최대 17% 차이"가 아니라 "4.8%~17.0%")
```

`references/confidentiality.md`:
```markdown
# 기밀·개인정보 규칙

- 전 직장 내부 시스템의 도메인·URL·저장소명·DB/테이블명·사내 채널명을 쓰지 않는다. 일반 명칭으로 바꾼다 (예: "S&OP 전용 시스템", "# 저작권-모니터링")
- 동료·외부 자문가·거래처(지사·총판·고객사)의 실명을 쓰지 않는다. 임원은 직책으로
- 금액: `CAREER.md`의 `money_policy`를 따른다. `allow`가 아니면 절대 금액 대신 비율·전후 비교
- 민감한 개별 품목명은 익명화 (예: "브랜드 A~D")
- 숨은 텍스트: HTML 주석, PDF 메타데이터(제목·작성자), 템플릿 잔존 문구에 내부 메모를 남기지 않는다
- 사진·연락처가 든 HTML/PDF는 git에 커밋하지 않는다 (사용자 `CAREER.md`의 `## 저장 후 처리`가 정한 위치에만 둔다)
- 톤: 전 직장·경영진을 비판하거나 반박하는 것처럼 읽히는 표현을 피한다 ("대표이사 수치를 정정" → "경영진 분석을 데이터로 재검증해 원인 규명")
```

`references/filenames.md`:
```markdown
# 제출 파일명 규칙

- 회사판: `{name}_{doc}_{company}.<확장자>` (기본 패턴, `CAREER.md`의 `filename_pattern`으로 바꿀 수 있음)
- 범용본(기본본): `{name}_{doc}.<확장자>`
- `doc`: `이력서` / `경력기술서` / `포트폴리오`
- `company`: 회사명만. 직무는 넣지 않는다. `(주)`·`㈜`·`주식회사`·공백을 뺀다 (`scripts/config.py`의 `normalize_company`)
- HTML `<title>`은 파일명 stem과 같다 (아티팩트 이름·PDF 제목·브라우저 저장 파일명이 여기서 나온다)
- 제출 PDF는 `paths.output`에, 지원 폴더에도 같은 이름의 PDF·HTML 사본을 둔다
- 커밋하는 마크다운(`공고.md`, `브리프.md`, `claims.md`, `진행 상황.md`, `경력기술서.md`)은 이 규칙 대상이 아니다
```

`references/jd-capture.md`: `/home/ryanchoi/vault/.claude/skills/job-application/SKILL.md`의 "## 1. JD 캡처" 절(일반 링크 → JobKorea 모바일 링크 `GI_Read/<Gno>` 재구성 → `GI_Read_Comt_Ifrm` iframe 직접 열기 → 통짜 이미지 분할 판독 → 리다이렉트 링크 확인)을 그대로 옮기고, 끝에 다음 두 절을 덧붙인다:
```markdown
## 공고.md에 반드시 남길 것
- 원문(담당업무·자격요건·우대사항·제출 서류·전형 절차)을 최대한 원문 그대로
- 제출 서류 요건 원문 (서류 종류, 프로젝트 개수, 분량, 형식, 파일명 지정) — brief의 서류 계획과 review의 제출 요건 검사가 읽는다

## 실패 시
- 본문을 못 가져오면 사용자에게 공고 텍스트나 캡처 이미지를 요청한다. 추측으로 채우지 않는다
```
경로 예시의 vault 경로(`Career/지원 이력/...`)는 `<applications>/<회사> <직무>/`로 바꾼다.

`references/korean-career-description-guide.md`: `/home/ryanchoi/vault/.claude/skills/career-description/references/korean-guide.md`를 그대로 복사하고, 첫 줄 설명의 "SKILL.md의 규칙"을 "write-career-description 스킬의 규칙"으로 바꾼다. 본문에 "문제 → 행동 → 결과", "A4 1~3장"이 이미 있는지 확인하고, 출처 목록 절의 제목을 "## 7. 출처"로 유지한다.

`references/schemas.md`: 설계 문서 4.2~4.6을 옮긴다(CAREER.md 키, 프로젝트 노트 frontmatter·본문·콜아웃, 지원 폴더 파일, 상태 8개, `claims.md` 6열 형식과 금지 열 표기법("큰따옴표 안 문구 → 대체 표기", 여러 개는 `;`), `insights.md` 표 형식). 4.2의 예시 고정 표기는 일반 예시("<도구명> MCP — 별도 서버를 만든 것이 아님")로 바꾼다.

- [ ] **Step 4: 통과 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_references.py -q`
Expected: 모두 PASS

- [ ] **Step 5: 커밋**

```bash
git add plugins/careerfit/references plugins/careerfit/tests/test_references.py
git commit -m "feat(careerfit): 공통 규칙 references 7종 (문체·사실·기밀·파일명·JD 캡처·경력기술서 가이드·스키마)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 13: 검수 — `agents/consistency-reviewer.md`와 `skills/review/SKILL.md`, 스킬 형식 테스트

**Files:**
- Create: `plugins/careerfit/agents/consistency-reviewer.md`
- Create: `plugins/careerfit/skills/review/SKILL.md`
- Test: `plugins/careerfit/tests/test_skills_wellformed.py`

**Interfaces:**
- Consumes: `scripts/lint_docs.py` CLI, `scripts/pdf_check.py` CLI, `references/*`
- Produces: `review` 스킬 — 입력: 지원 폴더 경로(또는 기본본 폴더 + `--base`), 출력: 지원 폴더 `진행 상황.md`의 "검수 결과" 섹션과 사용자에게 보여줄 심각도별 목록. 통과 시 `진행 상황.md`에 `제출 가능 (YYYY-MM-DD)` 줄
- `test_skills_wellformed.py`는 이후 Task의 스킬도 검사한다(존재하는 SKILL.md 전부)

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_skills_wellformed.py`

```python
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
    assert "<실명>" not in text and "<현 직장>" not in text


def test_skill_set_complete_when_done():
    names = {p.parent.name for p in SKILLS}
    assert names <= EXPECTED
```

- [ ] **Step 2: 실패 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_skills_wellformed.py -q`
Expected: 파라미터 없음으로 `test_frontmatter_and_refs` 0건 수집 + `test_skill_set_complete_when_done` PASS. 이 상태가 기준선이고, Step 3 뒤에 review·agent 2건이 추가로 수집돼 PASS해야 한다.

- [ ] **Step 3: 작성** — `agents/consistency-reviewer.md`

```markdown
---
name: consistency-reviewer
description: careerfit 제출 서류(이력서·경력기술서·포트폴리오)를 만든 맥락 없이 처음 보는 사람의 눈으로 교차 검수한다. 주장 원장·브리프·프로젝트 노트와 대조해 숫자·논리·강조·용어·규칙과 신뢰·노출·톤·전략 항목을 판정하고, 발견만 보고하며 고치지 않는다. careerfit review 스킬이 스크립트 검사 뒤에 호출한다.
tools: Read, Glob, Grep, Bash
---

너는 지원 서류 검수자다. 서류를 쓴 사람이 아니고, 고치지 않는다. 발견만 보고한다.

## 입력 (호출 프롬프트로 받는다)
- 지원 폴더 경로: `공고.md`, `브리프.md`, `claims.md`, 회사판 서류(HTML·PDF·`경력기술서.md`)
- `CAREER.md` 경로와 프로젝트 노트 폴더
- 스크립트 검사 결과(JSON) — 이미 잡힌 항목은 반복하지 않는다

## 판정 항목
1. 숫자: 서류의 숫자·기간·직함이 `claims.md`의 표기와 같은가, 문서끼리 같은가
2. 논리: 문제 지표와 결과 지표의 짝, 의사결정 이유가 출처 노트에 있는가, 시간 순서 표현이 노트 날짜와 맞는가
3. 강조: `브리프.md`의 이야기 설계(전면 프로젝트·순서·부각 포인트)가 자기소개서·경력기술서 대응표·포트폴리오 케이스 순서에 같게 반영됐는가
4. 용어: 같은 대상의 같은 이름 (회사 표기, 프로젝트명, `CAREER.md`의 `## 고정 표기`)
5. 과장 수식어: 노트에 없는 강조어 (스크립트의 HYPE_CANDIDATE 후보를 노트와 대조해 확정)
6. 시제·상태: 중단·설계안·진행 중 표현
7. 귀속·주어: `claims.md` 귀속 열과 문장 주어
8. 면접 방어 가능성: 근거를 물으면 답하기 어려운 주장 목록 (별도 목록)
9. 기밀·개인정보: `${CLAUDE_PLUGIN_ROOT}/references/confidentiality.md` 기준
10. 톤 리스크: 전 직장·경영진 비판·반박으로 읽히는 표현
11. 첫 장 30초: 1쪽만 보고 직무 적합성과 핵심 수치가 보이는가 (PDF 1쪽 텍스트 또는 스크린샷)
12. JD 커버리지·지면 배분: 브리프에서 "강점"으로 판정한 요건이 서류에 나오는가, JD와 무관한 내용이 지면을 크게 차지하는가 (권장)

규칙 근거: `${CLAUDE_PLUGIN_ROOT}/references/writing-rules.md`, `${CLAUDE_PLUGIN_ROOT}/references/attribution-and-facts.md`.

## 출력 (한국어, 이 형식 그대로)
### 필수
- [항목번호] 문서·위치 인용 → 문제 → 근거(노트·원장 인용) → 수정 제안 문구
### 권장
- (같은 형식)
### 사소
- (같은 형식)
### 면접 방어가 어려운 주장
- 주장 인용 → 왜 약한가 → 보강에 필요한 정보
### 문제 없음
- 항목번호 나열
```

`skills/review/SKILL.md`:
```markdown
---
name: review
description: careerfit 최종 일관성 검수. 회사판 서류(이력서·경력기술서·포트폴리오)가 모두 나온 뒤, 또는 기본본을 갱신한 뒤 실행한다. 스크립트로 기계 검사(금지어·타사명·title·원장 숫자·기간·경력 연수·버전·링크·PDF 크기·쪽수·폰트·빈 쪽·ATS 띄어쓰기)를 돌리고, consistency-reviewer 에이전트로 판단 검사를 맡긴 뒤, 결과를 심각도별로 정리해 사용자에게 보여주고 필수 항목 수정·재검수까지 이끈다. apply가 마지막 단계로 호출하며, "검수해줘", "서류 최종 점검"이라고 할 때도 쓴다.
---

# 최종 일관성 검수

## 0. 입력 확인
- 회사판: 지원 폴더(`<applications>/<회사> <직무>/`)에 `공고.md`·`브리프.md`·`claims.md`와 제출 서류가 있어야 한다. `claims.md`가 없으면 brief 스킬로 돌아가 원장을 먼저 만든다
- 기본본: `<base>/` 폴더. 원장 대신 이력 저장소 전체를 기준으로 한다(`--claims` 없이 실행)
- `CAREER.md` 경로는 사용자 작업 폴더의 `CAREER.md`(없으면 setup 스킬로 안내)

## 1. 스크립트 검사
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_docs.py --career <CAREER.md> --company <회사명> \
  --claims <지원 폴더>/claims.md --pair <이력서.html>:<이력서.pdf> --pair <경력기술서.html>:<경력기술서.pdf> \
  --pair <포트폴리오.html>:<포트폴리오.pdf> <이력서.html> <경력기술서.html> <포트폴리오.html> <경력기술서.md>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pdf_check.py <이력서.pdf> --kind A4
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pdf_check.py <경력기술서.pdf> --kind A4 --max-pages 3
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pdf_check.py <포트폴리오.pdf> --kind slide
```
- 공고의 제출 요건(서류 종류·프로젝트 개수·분량·형식·파일명)을 `공고.md` 원문과 대조해 표로 확인한다 (스크립트 밖, 직접)
- 결과 JSON을 모아 둔다

## 2. 에이전트 검사
`consistency-reviewer` 에이전트를 부른다. 프롬프트에 지원 폴더 경로, `CAREER.md` 경로, 프로젝트 노트 폴더, 1단계 결과 JSON 요약을 넣는다. 에이전트는 고치지 않는다.

## 3. 결과 정리와 처리
- 1·2단계 결과를 합쳐 필수/권장/사소로 사용자에게 보여준다. 같은 문제는 한 번만
- 필수: 고친 뒤(해당 write-* 스킬의 규칙대로) 1단계부터 다시 돌린다
- 사용자 판단이 필요한 것(근거 없는 표현을 유지할지, 금액 정책 등)은 질문으로 넘긴다
- "면접 방어가 어려운 주장" 목록은 그대로 사용자에게 보여주고 진행 상황에 남긴다
- 필수 0건이 되면 `진행 상황.md`에 `## 검수 결과 (YYYY-MM-DD)` 섹션을 만들고 남은 권장·사소 항목, 면접 방어 목록, `제출 가능 (YYYY-MM-DD)` 줄을 쓴다
- 아티팩트 링크를 쓰는 경우 "기본 비공개라 채용 담당자가 열 수 없다"는 안내를 반드시 덧붙인다
```

- [ ] **Step 4: 통과 확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_skills_wellformed.py -q`
Expected: `review`·`consistency-reviewer` 2건 포함 모두 PASS

- [ ] **Step 5: 커밋**

```bash
git add plugins/careerfit/agents plugins/careerfit/skills/review plugins/careerfit/tests/test_skills_wellformed.py
git commit -m "feat(careerfit): 최종 일관성 검수 스킬과 검수 에이전트

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 14: `skills/brief/SKILL.md` — 전략 브리프·주장 원장

**Files:**
- Create: `plugins/careerfit/skills/brief/SKILL.md`

**Interfaces:**
- Consumes: `공고.md`(jd-capture 결과), 이력 저장소, `insights.md`, `references/schemas.md`·`attribution-and-facts.md`
- Produces: 지원 폴더의 `브리프.md`(7개 절, 아래 순서와 제목 그대로)와 `claims.md`(schemas.md 6열 형식). 승인 상태를 `브리프.md` frontmatter `승인: false|true`로 기록. write-* 스킬과 review가 이 두 파일을 읽는다

- [ ] **Step 1: 작성** — `skills/brief/SKILL.md`

```markdown
---
name: brief
description: 공고 하나에 대한 지원 전략 브리프와 주장 원장(claims.md)을 만든다. 헤드헌터처럼 포지션을 해석하고, 요건별 적합도 매트릭스를 그리고, 전면에 세울 프로젝트와 부각 포인트를 설계하고, 약점 대응 논리와 빈틈 질문을 정리한 뒤 사용자 승인을 받는다. apply가 1단계로 호출하며, "이 공고 전략 짜줘", "어떤 경력을 강조해야 해", "브리프 다시 써줘"라고 할 때도 쓴다. 승인 전에는 서류를 쓰지 않는다.
---

# 전략 브리프와 주장 원장

## 0. 읽을 것
- `<applications>/<회사> <직무>/공고.md` (없으면 apply 스킬의 JD 캡처부터)
- 이력 저장소 전체의 frontmatter(`영역`·`임팩트`·기간)와 본문, 특히 `[!note]` 콜아웃 (정정·범위 재정의·귀속·신뢰도)
- `insights.md` (없으면 건너뜀)
- `CAREER.md`의 `## 고정 표기`·`## 귀속 주의`
- 규칙: `${CLAUDE_PLUGIN_ROOT}/references/attribution-and-facts.md`, `${CLAUDE_PLUGIN_ROOT}/references/schemas.md`

## 1. `브리프.md` 초안 (이 7개 절, 이 순서)
frontmatter: `회사`, `공고`, `승인: false`, `created`, `modified` (`date "+%Y-%m-%dT%H:%M:%S%:z"`로 실제 시각)

1. `## 포지션 해석` — 공고 문구의 빈도·순서·팀 소개·우대사항으로 "이 자리가 진짜 해결하려는 문제"를 3~5문장. 공고 유형 판정(예: AX 실행형 / 전략기획형 / PO형 / 데이터형) 한 줄
2. `## 적합도 매트릭스` — 표 `| 요건(원문 발췌) | 구분(자격/우대/업무) | 대응 프로젝트 | 근거 | 판정 |`. 판정은 `강점`/`부분 충족`/`갭`. 후보는 `임팩트: 핵심` 먼저, 공고 유형에 맞는 `영역` 우선
3. `## 이야기 설계` — 전면 프로젝트 2~4개와 순서, 프로젝트별 이 공고용 부각 포인트 1~2줄, 버릴 것(관련 낮음·비해당 영역). `보조`를 전면에 쓰면 이유 한 줄
4. `## 약점과 대응 논리` — 산업 경험·직함·결과 수치 약점과 각각의 대응 논리
5. `## 빈틈 질문` — 저장소로 판단할 수 없는 것만, 중요도 순 번호 목록. 각 질문에 "답에 따라 무엇이 바뀌는지" 한 줄
6. `## 인사이트 반영` — `insights.md`에서 비슷한 공고 유형의 결과와 시사점 (없으면 "기록 없음")
7. `## 서류 계획` — 공고 제출 요건 원문 인용, 만들 서류와 모드(경력기술서 심층형/전체 경력형/회사 양식), 분량 상한

## 2. `claims.md` 초안
- 이야기 설계에 쓸 숫자·핵심 주장을 6열 표로 (`${CLAUDE_PLUGIN_ROOT}/references/schemas.md`의 claims 형식)
- 각 행: 서류에 쓸 표기, 값, 출처 노트 경로, 귀속, 금지·주의 표현(노트의 정정 콜아웃에서 온 것 포함)
- 출처가 없는 숫자는 넣지 않는다. 필요하면 빈틈 질문으로 돌린다

## 3. 빈틈 질문 → 반영
- 질문을 사용자에게 한 번에 보여주되, 답하기 쉬운 형태(예/아니오, 수치 하나)로
- 답에서 나온 새 사실은 해당 프로젝트 노트에 먼저 기록한다(콜아웃 `[!note] ... (YYYY-MM-DD 본인 확인)`) → 그다음 브리프·원장에 반영
- 답이 없거나 "모름"이면 그 주장은 원장에서 빼거나 정성 서술로 바꾼다

## 4. 승인
- 브리프 요약(포지션 해석 한 줄, 전면 프로젝트와 순서, 큰 약점 1~2개, 서류 계획)을 보여주고 승인을 요청한다
- 승인되면 frontmatter `승인: true`, `modified` 갱신. 수정 요청이면 반영 후 다시 요청
- 승인 전에는 write-* 스킬을 부르지 않는다
```

- [ ] **Step 2: 형식 테스트**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_skills_wellformed.py -q`
Expected: `brief` 포함 모두 PASS

- [ ] **Step 3: 커밋**

```bash
git add plugins/careerfit/skills/brief
git commit -m "feat(careerfit): 전략 브리프·주장 원장 스킬

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 15: 서류 작성 스킬 3종 — `write-resume`·`write-career-description`·`write-portfolio`

**Files:**
- Create: `plugins/careerfit/skills/write-resume/SKILL.md`
- Create: `plugins/careerfit/skills/write-career-description/SKILL.md`
- Create: `plugins/careerfit/skills/write-portfolio/SKILL.md`

**Interfaces:**
- Consumes: `브리프.md`(`승인: true`), `claims.md`, 기본본(`<base>/`), 템플릿, `scripts/chrome.py`·`render_md.py`·`build_variant.py`·`pdf_check.py`, `config.submission_name`
- Produces: 지원 폴더의 `{name}_{doc}_{company}.html/.pdf`, `paths.output`의 같은 이름 PDF, 회사판 `경력기술서.md`. 기본본 모드(`--base`)면 `<base>/`에 `{name}_{doc}.html/.pdf`

- [ ] **Step 1: 작성** — `skills/write-resume/SKILL.md`

```markdown
---
name: write-resume
description: careerfit 이력서(자기소개서 포함, A4) 작성. 회사판은 기본 이력서를 복사해 승인된 브리프와 주장 원장대로 자기소개서·경력 블록 순서·태그라인을 맞추고, 기본본 모드는 이력 저장소로 기본 이력서를 만들거나 갱신한다. apply·setup이 호출한다.
---

# 이력서 작성

규칙: `${CLAUDE_PLUGIN_ROOT}/references/writing-rules.md`, `${CLAUDE_PLUGIN_ROOT}/references/attribution-and-facts.md`, `${CLAUDE_PLUGIN_ROOT}/references/confidentiality.md`, `${CLAUDE_PLUGIN_ROOT}/references/filenames.md`

## 회사판
1. 확인: `브리프.md`의 `승인: true`. 아니면 멈추고 brief로 돌아간다
2. `<base>/{name}_이력서.html`을 작업 폴더로 복사한다. 기본본이 없으면 기본본 모드부터
3. 바꾸는 것만 바꾼다
   - `<title>` = `scripts/config.py`의 `submission_name(career, "이력서", 회사, ext=None)`, meta = `<회사> <직무> 지원 이력서`
   - 헤더 태그라인: 브리프 포지션 해석에 맞춘 한 줄
   - 자기소개서 3항목: 지원배경·포부는 새로 쓰고, 강점 문단은 이야기 설계 순서대로 전면 프로젝트를 배치. 숫자·표기는 `claims.md`만
   - 경력 블록 순서: 이야기 설계 순서 → 나머지 핵심 → 보조(짧게) → 참고. 블록 문장 자체는 기본본 유지
   - 기술 스택 순서: 공고 관련도 순
4. PDF: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome.py pdf <html> <지원 폴더>/<파일명>.pdf` 후 `pdf_check.py --kind A4`. 마지막 쪽이 서명만 넘어가면 자기소개서 문장을 줄이거나 긴 블록만 `break-inside:auto`로 풀고 다시 렌더
5. HTML·PDF를 지원 폴더에, PDF를 `paths.output`에 같은 이름으로 둔다

## 기본본 모드
- `${CLAUDE_PLUGIN_ROOT}/templates/resume.html`에서 시작해 이력 저장소로 채운다. 블록 순서는 `임팩트` 핵심 → 보조 → 참고, 같은 임팩트는 최근순
- 자기소개서는 회사명 없는 범용 문장(지원배경·포부는 지원 때 반드시 다시 쓴다는 점을 진행 기록에 남긴다)
- `{{NAME}}`·`{{CONTACT}}`는 `CAREER.md` 값으로. 사진은 `CAREER.md`의 `photo`가 있을 때만 PHOTO 주석 자리에 base64로 넣는다
- 파일명 `{name}_이력서.html/.pdf`
```

`skills/write-career-description/SKILL.md`:
```markdown
---
name: write-career-description
description: careerfit 경력기술서(A4) 작성. 회사판은 기본 경력기술서 마크다운을 복사해 승인된 브리프의 서류 계획(심층형/전체 경력형/회사 양식)대로 고치고 렌더링하며, 기본본 모드는 이력 저장소로 전체 경력형 기본 경력기술서를 만든다. 공고가 "주요 프로젝트 N개 상세(문제·역할·의사결정·결과)"를 요구할 때 apply가 호출한다.
---

# 경력기술서 작성

규칙: `${CLAUDE_PLUGIN_ROOT}/references/korean-career-description-guide.md`, `${CLAUDE_PLUGIN_ROOT}/references/writing-rules.md`, `${CLAUDE_PLUGIN_ROOT}/references/attribution-and-facts.md`

## 모드
| 공고 요구 | 모드 | 구성 | 분량 |
|---|---|---|---|
| 프로젝트 개수 지정 | 심층형 | 경력 요약 → 공고 요구사항 대응표 → 프로젝트 상세 1~2개 | A4 2~3장 |
| 형식 자유 | 전체 경력형 | 경력 요약 → 프로젝트 상세 2개 → 회사별 경력 상세 | A4 2~3장 |
| 회사 양식 | 양식 준수 | 회사 양식 항목에 내용 원칙만 적용 | 양식 따름 |

## 회사판
1. `브리프.md` `승인: true` 확인. `<base>/경력기술서.md`를 `<지원 폴더>/경력기술서.md`로 복사
2. frontmatter `회사`·`공고`·`모드`·`version`·`created`·`modified`. 첫머리 `> [!note] 작성 기준`에 공고 제출 요건 원문 인용
3. 심층형이면 1쪽에 `## 공고 요구사항과 경험` 3열 표 `| 공고 요구사항 (원문 발췌) | 대응 경험 | 근거 |` 5~7행, 핵심어 굵게, 가운데 칸은 본문 제목과 같은 이름("프로젝트 1 · ..."), 상세에 없는 경험은 "그 외 · ...", 행은 프로젝트별로 묶는다. 근거 약한 요건은 행을 뺀다. "회사별 경력 상세"는 지운다
4. 프로젝트 상세(`### N. 제목` → 메타 → `한 줄 요약:` → `**문제 정의**` `**본인 역할**` `**주요 의사결정**` `**실행 과정**` `**결과**`): 의사결정이 가장 두껍게, 출처 노트에 있는 이유만. 결과 지표는 문제 지표와 짝. `- 핵심 수치: a · b`에는 결과 지표만
5. 렌더: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_md.py <md> <html> --title <submission_name(...,ext=None)> --target "<회사> <직무> 지원" --name <name> --contact "<email> · <phone>" [--break-projects]`
6. PDF와 검사: `chrome.py pdf` → `pdf_check.py --kind A4 --max-pages 3`. 넘치면 실행 과정 → 회사별 상세 → 핵심 역량 순으로 줄인다(의사결정·결과는 끝까지 지킨다). 프로젝트 제목이 쪽 끝에 걸리면 `--break-projects`
7. `[확인 필요]`가 남아 있으면 제출본이 아니다 — 사용자에게 묻고 채운 뒤 다시 렌더

## 기본본 모드
- 전체 경력형으로 `<base>/경력기술서.md`를 만들고 `{name}_경력기술서.html/.pdf`로 렌더. 상세 프로젝트는 `임팩트: 핵심` 중 서로 다른 역량을 보여주는 2개
```

`skills/write-portfolio/SKILL.md`:
```markdown
---
name: write-portfolio
description: careerfit 포트폴리오(가로형 덱) 작성. 회사판은 기본 포트폴리오에서 표지·클로징·케이스 순서만 바꿔 build_variant로 파생하고, 기본본 모드는 이력 저장소의 핵심 프로젝트로 케이스 덱을 만든다. apply·setup이 호출한다.
---

# 포트폴리오 작성

규칙: `${CLAUDE_PLUGIN_ROOT}/references/writing-rules.md`(포트폴리오 절), `${CLAUDE_PLUGIN_ROOT}/references/confidentiality.md`

## 회사판
1. `브리프.md` `승인: true` 확인
2. spec JSON 작성: `title`(= `submission_name(career, "포트폴리오", 회사, ext=None)`), `meta`, `cover_eyebrow`(선택), `tagline`(이력서 태그라인과 같은 문장), `closing`(공고에 맞춘 한 문장), `order`(이야기 설계 순서로 기본본 케이스 번호 재배치. 기반이 되는 케이스는 그 위의 케이스보다 앞에)
3. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/build_variant.py <base>/{name}_포트폴리오.html <spec.json> <지원 폴더>/<파일명>.html`
4. `chrome.py pdf` → `pdf_check.py --kind slide`. 바뀐 표지·목차·첫 케이스는 `chrome.py shot <html> <png> 1123 631`로 눈으로 확인
5. 케이스 본문을 회사에 맞게 바꿔야 하면(드물게) 기본본을 먼저 고치고 다시 파생한다

## 기본본 모드
- `${CLAUDE_PLUGIN_ROOT}/templates/portfolio.html`에서 시작. 케이스 = `임팩트: 핵심` 프로젝트(최대 5개), 보조는 "그 외 작업" 카드
- 케이스마다 도식은 구조·워크플로(결과 수치 금지), KPI 카드 3개는 결과 지표만(목표치·기능 개수·운영 기간 금지). 실제 대시보드 스크린샷은 쓰지 않는다
- 범위 재정의 콜아웃이 있는 프로젝트는 그 결론을 케이스 결론으로, 활용 사례는 점선 "활용"으로 구분
- 슬라이드 전부 스크린샷으로 넘침·겹침 확인. 파일명 `{name}_포트폴리오.html/.pdf`
```

- [ ] **Step 2: 형식 테스트**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_skills_wellformed.py -q`
Expected: 3개 스킬 포함 모두 PASS

- [ ] **Step 3: 커밋**

```bash
git add plugins/careerfit/skills/write-resume plugins/careerfit/skills/write-career-description plugins/careerfit/skills/write-portfolio
git commit -m "feat(careerfit): 이력서·경력기술서·포트폴리오 작성 스킬

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 16: `skills/apply/SKILL.md` — 공고 단위 지원 진입점

**Files:**
- Create: `plugins/careerfit/skills/apply/SKILL.md`

**Interfaces:**
- Consumes: `references/jd-capture.md`, brief, write-*, review, `scripts/status.py`(초기 상태 `준비 중`)
- Produces: 지원 폴더 전체(`공고.md`, `브리프.md`, `claims.md`, 회사판 서류, `진행 상황.md`)

- [ ] **Step 1: 작성** — `skills/apply/SKILL.md`

```markdown
---
name: apply
description: careerfit 공고 단위 지원 진입점. 채용 공고(링크·텍스트·이미지)를 받으면 JD를 캡처하고, 전략 브리프와 주장 원장을 만들어 빈틈만 묻고 승인받은 뒤, 필요한 서류(이력서·경력기술서·포트폴리오)를 기본본에서 파생해 쓰고, 최종 일관성 검수를 거쳐 지원 폴더에 기록한다. 사용자가 공고 링크를 보내거나 "이 회사 지원 준비해줘", "이 공고에 맞춰 서류 만들어줘"라고 할 때 반드시 쓴다. CAREER.md나 기본본이 없으면 setup을 먼저 안내한다.
---

# 공고 단위 지원

## 0. 선행 확인
- 작업 폴더의 `CAREER.md`를 `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/config.py <CAREER.md>`로 읽는다. 없으면 setup 스킬로 안내하고 멈춘다
- `<base>/`에 기본본 3종이 있는지, 이력 저장소보다 오래되지 않았는지 확인한다(가장 최근 프로젝트 노트 `modified`와 비교). 오래됐으면 setup 업데이트를 먼저 권한다
- `<applications>/`에 같은 회사·직무 폴더가 있으면 이어서 진행한다

## 1. JD 캡처
- `${CLAUDE_PLUGIN_ROOT}/references/jd-capture.md` 절차로 `<applications>/<회사> <직무>/공고.md`를 만든다
- `상태`는 `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/status.py set <공고.md> "준비 중" <now>`로 기록

## 2. 브리프 (승인 게이트)
- brief 스킬을 따른다. 승인 전에는 3단계로 가지 않는다

## 3. 서류 작성
- 브리프의 서류 계획에 있는 것만: write-resume, write-career-description, write-portfolio 스킬
- 세 서류 모두 `claims.md`의 표기와 이야기 설계 순서를 따른다

## 4. 최종 검수
- review 스킬. 필수 0건이 될 때까지 수정·재검수

## 5. 기록과 마무리
- `진행 상황.md`: 무엇을 어떤 JD 문구에 맞춰 바꿨는지, 브리프 핵심 결정, 빈틈 질문과 답, 검수 결과, 제출 파일 경로
- 제출 파일명은 `${CLAUDE_PLUGIN_ROOT}/references/filenames.md`
- `CAREER.md`의 `## 저장 후 처리`를 그대로 수행한다(예: 브랜치·PR·동기화). 없으면 파일만 둔다
- 사용자에게: 제출 파일 경로, 남은 권장 항목, 면접 방어가 어려운 주장, 결과가 나오면 track으로 기록하라는 안내
```

- [ ] **Step 2: 형식 테스트**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_skills_wellformed.py -q`
Expected: PASS

- [ ] **Step 3: 커밋**

```bash
git add plugins/careerfit/skills/apply
git commit -m "feat(careerfit): 공고 단위 지원 진입점 apply 스킬

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 17: `skills/setup/SKILL.md` — 커리어 정리·세팅 진입점

**Files:**
- Create: `plugins/careerfit/skills/setup/SKILL.md`

**Interfaces:**
- Consumes: `references/schemas.md`, write-*(기본본 모드), review(기본본 모드), `scripts/config.py`, `scripts/status.py scan`
- Produces: `CAREER.md`, 이력 저장소 노트, 기본본 3종, 업데이트 시 "영향받는 진행 중 회사판" 목록

- [ ] **Step 1: 작성** — `skills/setup/SKILL.md`

```markdown
---
name: setup
description: careerfit 커리어 정리·세팅 진입점. 처음에는 CAREER.md 설정을 만들고, 기존 이력서·경력기술서·포트폴리오·LinkedIn·메모로 프로젝트 단위 이력 저장소를 채우고, 영역·임팩트 분류와 사실관계를 인터뷰로 정리한 뒤 기본 이력서·경력기술서·포트폴리오를 만든다. 이후에는 새 프로젝트·성과·정정·분류 변경을 반영하고 기본본과 진행 중 회사판을 갱신한다. "커리어 정리해줘", "이력 세팅", "새 프로젝트 추가", "이 수치 고쳐줘", "핵심 프로젝트 바꾸자"라고 할 때 쓴다.
---

# 커리어 정리·세팅

스키마: `${CLAUDE_PLUGIN_ROOT}/references/schemas.md`. 사실 규칙: `${CLAUDE_PLUGIN_ROOT}/references/attribution-and-facts.md`

판정: 작업 폴더에 `CAREER.md`가 없으면 "처음 실행", 있으면 "업데이트".

## 처음 실행
1. **설정**: `CAREER.md`를 만든다(이름, 연락처와 서류 전용 여부, `career_start`, `paths`, `market: KR`, `money_policy`). 이미 프로젝트 노트 폴더가 있으면 그 경로를 `paths.projects`로 지정하고 2~3단계는 빠진 노트만 보충한다
2. **재료 수집**: 기존 이력서·경력기술서·포트폴리오(PDF·Word·이미지·링크), LinkedIn 내보내기, 메모를 요청한다. 연결된 도구(메일·메신저)가 있으면 근거 확인용으로만 쓴다
3. **이력 저장소 작성**: 프로젝트마다 노트 하나(스키마의 frontmatter·본문·콜아웃). 수치마다 출처, 사건마다 귀속. 근거가 약하면 `[확인 필요: ...]`
4. **정리 인터뷰**: 저장소로 판단할 수 없는 것만 묻는다
   - 프로젝트별 `영역`·`임팩트` 분류 제안 → 확정 (핵심은 "이후 일을 가능하게 한 기반"인지, 지원 공고 유형에서 전면에 설 만한지 함께 본다)
   - 근거 약한 수치·범위·귀속 정정. 답은 노트 콜아웃 `[!note] ... (YYYY-MM-DD 본인 확인)`으로
5. **기본본 3종**: write-resume, write-career-description, write-portfolio 스킬의 기본본 모드 → review 스킬 기본본 모드

## 업데이트
1. 무엇을 바꾸는지 확인한다: 새 프로젝트 / 성과·수치 / 사실 정정 / 분류 변경 / 범위 재정의
2. 프로젝트 노트를 먼저 고친다(기존 문장은 지우지 말고 맥락에 맞지 않는 것만 삭제, 정정은 콜아웃으로 남김)
3. 기본본 3종을 갱신하고 review(기본본 모드)
4. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/status.py scan <applications>`로 상태가 `준비 중`·`서류 제출`·`서류 전형`·`면접`인 지원 건을 찾아, 바뀐 프로젝트를 쓰는 회사판 목록을 보여주고 파생 갱신 여부를 묻는다. 갱신하면 각 건에서 write-* → review
5. `CAREER.md`의 `## 저장 후 처리`를 수행한다
```

- [ ] **Step 2: 형식 테스트**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests/test_skills_wellformed.py -q`
Expected: PASS

- [ ] **Step 3: 커밋**

```bash
git add plugins/careerfit/skills/setup
git commit -m "feat(careerfit): 커리어 정리·세팅 진입점 setup 스킬

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 18: `skills/track/SKILL.md`·`skills/helper/SKILL.md`

**Files:**
- Create: `plugins/careerfit/skills/track/SKILL.md`
- Create: `plugins/careerfit/skills/helper/SKILL.md`

**Interfaces:**
- Consumes: `scripts/status.py` (`set`, `scan`), `config.STATUSES`, `insights.md` 형식
- Produces: 상태 갱신된 `공고.md`들, `진행 상황.md` 결과 섹션, `insights.md`

- [ ] **Step 1: 작성** — `skills/track/SKILL.md`

```markdown
---
name: track
description: careerfit 지원 진행 내역 업데이트와 회고. "A사 서류 탈락", "B·C는 서류 전형, 나머지는 탈락", "면접 봤어"처럼 결과를 들으면 지원 상태를 한 번에 갱신하고, 피드백·면접 질문을 기록하고, 결과가 쌓이면 어떤 강조점·프로젝트 선택이 통했는지 회고해 insights.md에 반영한다. 다음 apply의 브리프가 이 인사이트를 읽는다.
---

# 진행 내역·회고

## 1. 상태 갱신
- 상태는 이 8개만: 준비 중 / 서류 제출 / 서류 전형 / 서류 탈락 / 면접 / 최종 합격 / 불합격 / 지원 취소. 사용자 표현을 이 중 하나로 옮기고(예: "준비중" → 준비 중, "진행 중" → 서류 전형), 애매하면 묻는다
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/status.py scan <applications>`로 대상 폴더를 확인하고, "나머지 전부" 같은 표현은 대상 목록을 보여주고 확인받는다. 이미 다른 결과(예: 지원 취소)인 건은 바꾸지 않고 알린다
- 각 건: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/status.py set <공고.md> <상태> <now>` (`now`는 `date "+%Y-%m-%dT%H:%M:%S%:z"`)

## 2. 결과 기록
- `진행 상황.md`가 있으면 `# 결과 (YYYY-MM-DD)` 섹션에 상태와 받은 피드백·면접 질문·사용자 판단을 한두 줄로
- 잘못 기록했다 되돌리는 경우 결과 섹션도 함께 지우거나 고친다

## 3. 회고
- 결과(서류 전형 이상 또는 탈락)가 새로 생기면 `insights.md` 표에 행을 추가: 공고 유형, 결과, 전면 프로젝트, 강조점, 갭, 메모 (브리프의 이야기 설계·적합도 매트릭스에서 가져온다)
- 같은 공고 유형이 3건 이상 쌓이면 패턴 요약을 갱신한다. 표본이 적으면 "가설"로 표시하고 단정하지 않는다
- `CAREER.md`의 `## 저장 후 처리`를 수행한다
```

`skills/helper/SKILL.md`:
```markdown
---
name: helper
description: careerfit 길잡이. 뭘 해야 할지 모를 때, 또는 "공고 하나 받았어", "떨어졌어", "새 프로젝트 끝났어", "지금 상태 어때"처럼 말할 때 현재 상태(설정·이력 저장소·기본본 최신 여부·진행 중 지원·최근 결과)를 읽고 다음 행동 1~3개를 제안해 setup·apply·track으로 연결한다.
---

# 길잡이

## 1. 상태 읽기
- `CAREER.md` 유무 → 없으면 "setup으로 커리어 정리부터"
- 이력 저장소 노트 수, `[확인 필요]`가 남은 노트 수
- 기본본 3종 유무와, 가장 최근 프로젝트 노트 `modified`보다 오래됐는지
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/status.py scan <applications>` → 상태별 건수, `준비 중`이면서 검수 결과에 "제출 가능"이 없는 건
- `insights.md` 마지막 갱신일

## 2. 제안
상황별 기본 제안 (해당하는 것 1~3개):
- 설정 없음 → setup
- 기본본이 저장소보다 오래됨 → setup 업데이트
- `[확인 필요]`가 많은 핵심 프로젝트 → setup 정리 인터뷰
- 공고를 받았다고 함 → apply
- 준비 중인데 미검수 → apply 이어서(검수)
- 결과를 들었다고 함 / 서류 전형·면접 대기 건 → track
- 결과가 3건 이상 쌓였는데 인사이트가 오래됨 → track 회고

## 3. 연결
- 사용자가 고르면 해당 스킬로 넘긴다. 자연어 요청이 한 스킬에 분명히 해당하면 제안 없이 바로 그 스킬로
```

- [ ] **Step 2: 형식 테스트와 전체 스킬 세트 확인**

`tests/test_skills_wellformed.py`의 `test_skill_set_complete_when_done`을 `assert names == EXPECTED`로 바꾼다.

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests -q`
Expected: 모두 PASS

- [ ] **Step 3: 커밋**

```bash
git add plugins/careerfit/skills/track plugins/careerfit/skills/helper plugins/careerfit/tests/test_skills_wellformed.py
git commit -m "feat(careerfit): 진행 내역·회고 track과 길잡이 helper 스킬

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 19: 스킬 평가 세트·가상 JD·README 완성·실사용 검증 체크리스트

**Files:**
- Create: `plugins/careerfit/evals/evals.json`
- Create: `plugins/careerfit/tests/fixtures/jd-sample-commerce.txt`
- Modify: `plugins/careerfit/README.md`
- Test: `plugins/careerfit/tests/test_scaffold.py` (평가 세트 형식 검사 추가)

**Interfaces:**
- Produces: skill-creator 형식 평가 세트(`skill_name`, `evals[]`의 `id`·`prompt`·`expected_output`·`files`)

- [ ] **Step 1: 가상 JD 작성** — `tests/fixtures/jd-sample-commerce.txt`

```text
[(주)샘플커머스] AI PM
담당업무
- 고객 문의·주문 데이터를 분석해 AI Agent가 맡을 업무와 사람이 판단할 업무를 구분
- AI Agent 서비스의 기능·사용자 흐름·데이터 요구사항 기획
- 과제별 KPI와 성공 기준 정의, PoC 검증
자격요건
- 서비스 기획 또는 PM 경력 7년 이상
- 재고·주문 등 지표로 문제를 정의하고 성과를 판단한 경험
우대사항
- LLM·AI Agent를 실제 업무에 적용한 경험
- 이커머스 산업 경험
제출 서류
- 이력서, 경력기술서(주요 프로젝트 2개: 문제·역할·의사결정·결과), 포트폴리오(선택)
```
persona fixture에는 지원 폴더를 만들지 않는다 (Task 7·10 테스트가 tmp 복사본에 지원 폴더를 직접 만들고 목록을 정확히 비교하기 때문). 평가 2번은 apply가 지원 폴더를 새로 만드는 흐름을 본다.

- [ ] **Step 2: 평가 세트 작성** — `evals/evals.json`

```json
{
  "skill_name": "careerfit",
  "evals": [
    {"id": 1, "prompt": "tests/fixtures/persona 폴더를 내 커리어 폴더로 쓰고 있어. CAREER.md는 있으니 기본 이력서·경력기술서·포트폴리오를 만들어줘.",
     "expected_output": "setup 업데이트 흐름. 핵심 프로젝트 2개(재고 예측, 문의 분류)를 전면에, 채널 수익성은 보조로. 기본본 3종 파일명이 김하늘_<문서종류>. review 기본본 모드 실행. 노트에 없는 수치 없음", "files": ["tests/fixtures/persona"]},
    {"id": 2, "prompt": "이 공고 지원 준비해줘. tests/fixtures/jd-sample-commerce.txt",
     "expected_output": "apply → brief. 브리프.md에 7개 절(포지션 해석·적합도 매트릭스·이야기 설계·약점과 대응 논리·빈틈 질문·인사이트 반영·서류 계획), 매트릭스에 '이커머스 산업 경험'은 갭, 빈틈 질문에 '재고 예측 이전 품절 건수' 류 포함, claims.md에 출처 있는 행만, 승인 전 서류 미작성", "files": ["tests/fixtures/persona", "tests/fixtures/jd-sample-commerce.txt"]},
    {"id": 3, "prompt": "샘플커머스는 서류 전형, 나머지는 다 서류 탈락으로 기록해줘.",
     "expected_output": "track. status.py scan으로 대상 목록을 보여주고 확인, 상태 값은 고정 8개 중에서, 진행 상황.md가 있는 건만 결과 섹션 추가", "files": ["tests/fixtures/persona"]},
    {"id": 4, "prompt": "뭐부터 해야 할지 모르겠어.",
     "expected_output": "helper. CAREER.md 유무·기본본 최신 여부·준비 중 지원 건을 읽고 1~3개 제안, 기본본이 없으면 setup을 첫 제안으로", "files": ["tests/fixtures/persona"]}
  ]
}
```
`tests/test_scaffold.py`에 추가:
```python
def test_evals_format():
    data = json.loads((PLUGIN_ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
    assert data["skill_name"] == "careerfit"
    assert [e["id"] for e in data["evals"]] == [1, 2, 3, 4]
    for e in data["evals"]:
        assert e["prompt"] and e["expected_output"]
        for f in e["files"]:
            assert (PLUGIN_ROOT / f).exists(), f
```

- [ ] **Step 3: README 완성** — `plugins/careerfit/README.md`를 다음 절로 채운다: 한 줄 소개 / 진입점 4개 표(설계 문서 3장 표) / 처음 쓰는 법(`/careerfit:setup` → 공고가 생기면 `/careerfit:apply` → 결과는 `/careerfit:track`, 모를 때 `/careerfit:helper`) / 작업 폴더 구조(설계 문서 4.1) / 의존성(헤드리스 Chromium: `npx playwright install chromium` 또는 `CAREERFIT_CHROME`, Python 3 + `pypdf`·`PyYAML`, Nanum 폰트 `fc-list :lang=ko`로 확인) / 개발: 테스트 명령(`uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests -q`) / 실사용 검증 체크리스트(아래).

실사용 검증 체크리스트(README 마지막 절):
```markdown
## 실사용 검증 (1단계 완료 조건)
- [ ] 본인 career 폴더(예: vault)에 `CAREER.md`를 만들고 `paths`를 기존 노트 위치로 지정
- [ ] `/careerfit:setup` 업데이트로 기본본 3종이 기존 기본본과 같은 사실·수치로 나오는지
- [ ] 실제 공고 1건을 `/careerfit:apply`로 끝까지 처리 (브리프 승인 → 서류 → review 필수 0건)
- [ ] `/careerfit:track`으로 상태 기록, `insights.md` 첫 행
- [ ] 위 과정에서 나온 문제를 이슈로 남기고, vault 스킬 3개를 "careerfit 사용" 안내로 줄이는 작업은 별도 PR
```

- [ ] **Step 4: 전체 테스트**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests -q`
Expected: 모두 PASS (Chrome 없으면 렌더 의존만 SKIP)

- [ ] **Step 5: 커밋**

```bash
git add plugins/careerfit/evals plugins/careerfit/tests plugins/careerfit/README.md
git commit -m "feat(careerfit): 스킬 평가 세트·가상 JD·README 완성

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 20: 브랜치 마무리 — 푸시·draft PR

**Files:** 없음 (git 작업)

- [ ] **Step 1: 전체 테스트 재확인**

Run: `uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests -q`
Expected: 모두 PASS

- [ ] **Step 2: 개인정보 최종 검색**

Run: `grep -rn -F -f plugins/careerfit/tests/.personal-denylist plugins/careerfit --exclude=.personal-denylist || echo clean` (금지어 파일은 로컬 전용, gitignore)
Expected: `clean`

- [ ] **Step 3: 푸시와 draft PR**

```bash
git push -u origin feat/careerfit-mvp
gh pr create --draft --base master --title "feat(careerfit): 커리어핏 1단계 MVP" --body "설계: docs/superpowers/specs/2026-10-02-careerfit-design.md
계획: docs/superpowers/plans/2026-10-02-careerfit-mvp.md

- 진입점 setup / apply / track / helper, 내부 스킬 brief / write-* / review, 검수 에이전트
- scripts: config, chrome, pdf_check, lint_docs, render_md, build_variant, status (pytest)
- templates 3종, references 7종, evals

실사용 검증(README 체크리스트)은 머지 후 별도 진행.

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```
