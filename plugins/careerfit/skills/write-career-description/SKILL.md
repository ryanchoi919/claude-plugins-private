---
name: write-career-description
description: careerfit 경력기술서(A4) 작성. 회사판은 기본 경력기술서 마크다운을 복사해 승인된 브리프의 서류 계획(심층형/전체 경력형/회사 양식)대로 고치고 렌더링하며, 기본본 모드는 이력 저장소로 전체 경력형 기본 경력기술서를 만든다. 공고가 "주요 프로젝트 N개 상세(문제·역할·의사결정·결과)"를 요구할 때 apply가 호출한다.
---

# 경력기술서 작성

규칙: `${CLAUDE_PLUGIN_ROOT}/references/korean-career-description-guide.md`, `${CLAUDE_PLUGIN_ROOT}/references/writing-rules.md`, `${CLAUDE_PLUGIN_ROOT}/references/attribution-and-facts.md`, `${CLAUDE_PLUGIN_ROOT}/references/confidentiality.md`

마크다운 형식은 `${CLAUDE_PLUGIN_ROOT}/scripts/render_md.py` 첫머리 docstring을 따른다.

## 모드
| 공고 요구 | 모드 | 구성 | 분량 |
|---|---|---|---|
| 프로젝트 개수 지정 | 심층형 | 경력 요약 → 공고 요구사항 대응표 → 프로젝트 상세 1~2개 | A4 2~3장 |
| 형식 자유 | 전체 경력형 | 경력 요약 → 프로젝트 상세 2개 → 회사별 경력 상세 | A4 2~3장 |
| 회사 양식 | 양식 준수 | 회사 양식 항목에 내용 원칙만 적용 | 양식 따름 |

## 회사판
1. `브리프.md` frontmatter `승인: true` 확인. `<base>/경력기술서.md`를 `<지원 폴더>/경력기술서.md`로 복사
2. frontmatter `회사`·`공고`·`모드`·`version`·`created`·`modified`. 첫머리 `> [!note] 작성 기준`에 공고 제출 요건 원문 인용 (콜아웃은 렌더링되지 않는다)
3. 심층형이면 1쪽에 `## 공고 요구사항과 경험` 3열 표 `| 공고 요구사항 (원문 발췌) | 대응 경험 | 근거 |` 5~7행. 왼쪽은 공고 원문 발췌에 핵심어 굵게, 가운데는 본문 제목과 같은 이름("프로젝트 1 · ..."; 상세에 없는 경험은 "그 외 · ..."), 오른쪽은 수치·사실 한 줄. 행은 프로젝트별로 묶는다. 근거가 약하거나 요건과 직관적으로 이어지지 않는 행은 넣지 않는다. "회사별 경력 상세"는 지운다
4. 프로젝트 상세(`### N. 제목` → 메타 → 빈 줄 → `한 줄 요약:` → `**문제 정의**` `**본인 역할**` `**주요 의사결정**` `**실행 과정**` `**결과**`): 의사결정이 가장 두껍게, 출처 노트에 있는 이유만. 결과 지표는 문제 지표와 짝. `- 핵심 수치: a · b`에는 결과 지표만
5. 렌더 (파일명은 write-resume의 `submission_name` 명령에 `경력기술서`):
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_md.py <경력기술서.md> <지원 폴더>/<파일명>.html \
     --title <파일명> --target "<회사> <직무> 지원" --name <name> --contact "<email> · <phone>" [--break-projects]
   ```
6. PDF와 검사: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome.py pdf <html> <pdf>` → `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pdf_check.py <pdf> --kind A4 --max-pages 3`. 넘치면 실행 과정 → 회사별 상세 → 핵심 역량 순으로 줄인다 (의사결정·결과는 끝까지 지킨다). 프로젝트 제목이 쪽 끝에 걸리면 `--break-projects`
7. `[확인 필요]`가 남아 있으면 제출본이 아니다. 사용자에게 묻고 채운 뒤 다시 렌더
8. 마크다운은 지원 폴더에 두고(커밋 대상), HTML·PDF는 제출 파일명 규칙을 따른다

## 기본본 모드
- 전체 경력형으로 `<base>/경력기술서.md`를 만들고 `{name}_경력기술서.html/.pdf`로 렌더. 상세 프로젝트는 `임팩트: 핵심` 중 서로 다른 역량을 보여주는 2개
