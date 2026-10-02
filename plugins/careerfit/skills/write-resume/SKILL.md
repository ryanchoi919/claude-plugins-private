---
name: write-resume
description: careerfit 이력서(자기소개서 포함, A4) 작성. 회사판은 기본 이력서를 복사해 승인된 브리프와 주장 원장대로 자기소개서·경력 블록 순서·태그라인을 맞추고, 기본본 모드는 이력 저장소로 기본 이력서를 만들거나 갱신한다. apply·setup이 호출한다.
---

# 이력서 작성

규칙: `${CLAUDE_PLUGIN_ROOT}/references/writing-rules.md`, `${CLAUDE_PLUGIN_ROOT}/references/attribution-and-facts.md`, `${CLAUDE_PLUGIN_ROOT}/references/confidentiality.md`, `${CLAUDE_PLUGIN_ROOT}/references/filenames.md`

제출 파일명은 `scripts/config.py`의 `submission_name`으로 만든다:
```bash
python3 -c "import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}'); from scripts.config import load_career, submission_name as n; print(n(load_career(sys.argv[1]), '이력서', sys.argv[2] or None, ext=None))" <CAREER.md> "<회사명 또는 빈 문자열>"
```

## 회사판
1. 확인: `브리프.md` frontmatter가 `승인: true`. 아니면 멈추고 brief로 돌아간다
2. `<base>/{name}_이력서.html`을 작업 폴더로 복사한다. 기본본이 없으면 기본본 모드부터
3. 바꾸는 것만 바꾼다
   - `<title>` = 위 명령의 결과(파일명 stem), meta = `<회사> <직무> 지원 이력서`
   - 헤더 태그라인: 브리프 포지션 해석에 맞춘 한 줄 (포트폴리오 표지와 같은 문장)
   - 자기소개서 3항목: 지원배경·포부는 새로 쓰고, 강점 문단은 이야기 설계 순서대로 전면 프로젝트를 배치. 숫자·표기는 `claims.md`만
   - 경력 블록 순서: 이야기 설계 순서 → 나머지 핵심 → 보조(짧게) → 참고. 블록 문장 자체는 기본본 유지
   - 기술 스택 순서: 공고 관련도 순
4. PDF: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome.py pdf <html> <지원 폴더>/<파일명>.pdf` 후 `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pdf_check.py <pdf> --kind A4`. 마지막 쪽에 서명만 넘어가면 자기소개서 문장을 줄이거나 긴 블록 하나만 `break-inside:auto`로 풀고 다시 렌더
5. HTML·PDF를 지원 폴더에, PDF를 `paths.output`에 같은 이름으로 둔다

## 기본본 모드
- `${CLAUDE_PLUGIN_ROOT}/templates/resume.html`에서 시작해 이력 저장소로 채운다. 블록 순서는 `임팩트` 핵심 → 보조 → 참고, 같은 임팩트는 최근순
- 자기소개서는 회사명 없는 범용 문장 (지원 때 지원배경·포부는 반드시 다시 쓴다)
- `{{NAME}}`·`{{CONTACT}}`·`{{TAGLINE}}`·`{{TITLE}}`·`{{META}}`를 채운다. 연락처는 `CAREER.md`의 `contact`. 사진은 `CAREER.md`의 `photo`가 있을 때만 PHOTO 주석 자리에 base64로 넣는다 (사진이 든 파일은 커밋하지 않는다)
- 파일명 `{name}_이력서.html/.pdf`
