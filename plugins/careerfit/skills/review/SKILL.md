---
name: review
description: careerfit 최종 일관성 검수. 회사판 서류(이력서·경력기술서·포트폴리오)가 모두 나온 뒤, 또는 기본본을 갱신한 뒤 실행한다. 스크립트로 기계 검사(금지어·타사명·title·원장 숫자·기간·경력 연수·버전·링크·PDF 크기·쪽수·폰트·빈 쪽·ATS 띄어쓰기)를 돌리고, consistency-reviewer 에이전트에 판단 검사를 맡긴 뒤, 결과를 심각도별로 정리해 보여주고 필수 항목 수정·재검수까지 이끈다. apply가 마지막 단계로 호출하며, "검수해줘", "서류 최종 점검"이라고 할 때도 쓴다.
---

# 최종 일관성 검수

## 0. 입력 확인
- 회사판: 지원 폴더(`<applications>/<회사> <직무>/`)에 `공고.md`·`브리프.md`·`claims.md`와 제출 서류가 있어야 한다. `claims.md`가 없으면 brief 스킬로 돌아가 원장을 먼저 만든다
- 기본본: `<base>/` 폴더. 원장 대신 이력 저장소 전체를 기준으로 한다 (`--claims` 없이 실행, `--company`에는 사용자 이름처럼 어떤 회사와도 겹치지 않는 값)
- `CAREER.md`는 사용자 작업 폴더의 것 (없으면 setup 스킬로 안내)

## 1. 스크립트 검사 (항목 1의 추출, 5, 6, 8, 9, 16·17의 측정, 18)
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_docs.py --career <CAREER.md> --company <회사명> \
  --claims <지원 폴더>/claims.md \
  --pair <이력서.html>:<이력서.pdf> --pair <경력기술서.html>:<경력기술서.pdf> --pair <포트폴리오.html>:<포트폴리오.pdf> \
  <이력서.html> <경력기술서.html> <포트폴리오.html> <지원 폴더>/경력기술서.md
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pdf_check.py <이력서.pdf> --kind A4
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pdf_check.py <경력기술서.pdf> --kind A4 --max-pages 3
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pdf_check.py <포트폴리오.pdf> --kind slide
```
- 링크 검사는 네트워크를 쓴다. 오프라인이면 `--offline` (아티팩트 링크 안내만 남는다)
- 제출본 사본(`paths.output`의 PDF)도 지원 폴더 PDF와 같은지 확인한다: `cmp <지원 폴더 PDF> <output PDF>`
- PDF 메타데이터(제목·작성자)를 본다: `python3 -c "import sys; from pypdf import PdfReader; print(PdfReader(sys.argv[1]).metadata)" <pdf>`
- 항목 7 제출 요건(서류 종류·프로젝트 개수·분량·형식·파일명)은 `공고.md` 원문과 직접 대조해 표로 만든다
- `PDF_ATS_SPACING`은 헤드리스 Chrome + 나눔 폰트 조합에서 공백이 U+0001로 추출되는 현상이다. 채용 시스템이 텍스트를 붙여 읽을 수 있다는 권장 경고로 보여주고, 회사가 PDF 텍스트 파싱을 쓰는지 모르면 그대로 둔다
- 결과 JSON을 모아 둔다

## 2. 에이전트 검사 (항목 1~4, 10~16, 19의 판단)
`consistency-reviewer` 에이전트를 부른다. 프롬프트에 지원 폴더 경로, `CAREER.md` 경로, 프로젝트 노트 폴더, 1단계 결과 요약을 넣는다. 에이전트는 고치지 않는다.

## 3. 결과 정리와 처리
- 1·2단계 결과를 합쳐 필수/권장/사소로 보여준다. 같은 문제는 한 번만
- 필수: 해당 write-* 스킬의 규칙대로 고친 뒤 1단계부터 다시 돌린다
- 사용자 판단이 필요한 것(근거 없는 표현을 유지할지, 금액 정책 등)은 질문으로 넘긴다
- "면접 방어가 어려운 주장" 목록은 그대로 사용자에게 보여주고 진행 상황에 남긴다
- 회사판 검수에서 기본본에서 그대로 이어진 문제(기본본에도 같은 문구·카드가 있는 것)는 회사판에서 고치더라도 `진행 상황.md`의 `# 기본본 갱신 필요` 섹션에 문서별로 남긴다. update 스킬이 이 섹션을 모아 기본본을 고친다
- 필수 0건이 되면 `진행 상황.md`에 `## 검수 결과 (YYYY-MM-DD)` 섹션을 만들고 남은 권장·사소 항목, 면접 방어 목록, `제출 가능 (YYYY-MM-DD)` 줄을 쓴다
- 포트폴리오를 아티팩트 링크로 내는 경우 "기본 비공개라 채용 담당자가 열 수 없다"는 안내를 반드시 덧붙인다
