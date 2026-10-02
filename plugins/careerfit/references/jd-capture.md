# JD 캡처 → `<applications>/<회사> <직무>/공고.md`

JD 링크는 형태가 제각각이라 아래 순서로 시도한다.

1. **일반 웹 링크**: WebFetch로 먼저 시도.
2. **JobKorea 모바일 링크**(`m.jobkorea.co.kr/info/app_down.asp?Gno=...`): 앱 설치 유도 페이지라 본문이 없다. `Gno` 값을 그대로 써서 데스크톱 URL(`https://www.jobkorea.co.kr/Recruit/GI_Read/<Gno>`)로 재구성.
3. **iframe 안에 본문이 있는 경우**: WebFetch가 메타정보만 가져오고 자격요건/담당업무가 비어 있으면, 페이지에서 `GI_Read_Comt_Ifrm?Gno=...` 형태의 iframe URL을 찾아 그 URL 자체를 헤드리스 브라우저로 직접 연다.
   - Chrome 경로: `python3 -c "import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}'); from scripts.chrome import find_chrome; print(find_chrome())"`
   - `<chrome> --headless=new --no-sandbox --disable-gpu --dump-dom "<iframe URL>" > dump.html`
   - 그래도 비어 있으면(SPA 하이드레이션 대기 필요) `--virtual-time-budget=8000 --run-all-compositor-stages-before-draw` 추가
   - dump.html에서 script/style 태그를 지우고 HTML 태그를 개행으로 바꿔 텍스트만 추출
4. **본문이 통짜 이미지인 경우** (채용 공고를 이미지 한 장으로 올리는 ATS): 이미지를 내려받아 Python PIL로 세로 1200~1400px 단위로 잘라 저장한 뒤, Read 도구로 각 조각을 보고 원문을 옮겨 적는다. OCR 도구를 찾지 말고 이 방식을 바로 쓴다.
5. **다른 링크로 넘어가는 경우** (예: 회사 소개 이미지에 "커피챗 신청" 같은 별도 링크만 있는 경우): 그 링크가 진짜 JD인지 확인하고, 아니면 회사 채용 목록 페이지(`/recruit` 등)에서 실제 공고 링크를 다시 찾는다.

## `공고.md` 형식
- frontmatter: `회사`, `공고`, `지원일`, `상태`, `version`, `tags`, `aliases`, `created`, `modified` (`created`/`modified`는 `date "+%Y-%m-%dT%H:%M:%S%:z"`로 실제 시각)
- 본문: 포지션 개요 → 원문 → 자체 판단(요건 체크 표) → 관련 노트

## 공고.md에 반드시 남길 것
- 원문(담당업무·자격요건·우대사항·제출 서류·전형 절차)을 최대한 원문 그대로
- 제출 서류 요건 원문 (서류 종류, 프로젝트 개수, 분량, 형식, 파일명 지정). brief의 서류 계획과 review의 제출 요건 검사가 읽는다

## 실패 시
- 본문을 못 가져오면 사용자에게 공고 텍스트나 캡처 이미지를 요청한다. 추측으로 채우지 않는다
