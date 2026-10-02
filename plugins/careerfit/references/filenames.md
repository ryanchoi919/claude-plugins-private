# 제출 파일명 규칙

- 회사판: `{name}_{doc}_{company}.<확장자>` (기본 패턴, `CAREER.md`의 `filename_pattern`으로 바꿀 수 있음)
- 범용본(기본본): `{name}_{doc}.<확장자>`
- `doc`: `이력서` / `경력기술서` / `포트폴리오`
- `company`: 회사명만. 직무는 넣지 않는다. `(주)`·`㈜`·`주식회사`·공백을 뺀다 (`scripts/config.py`의 `normalize_company`, 이름은 `submission_name`이 만든다)
- HTML `<title>`은 파일명 stem과 같다 (아티팩트 이름·PDF 제목·브라우저 저장 파일명이 여기서 나온다)
- 제출 PDF는 `paths.output`에, 지원 폴더에도 같은 이름의 PDF·HTML 사본을 둔다
- 커밋하는 마크다운(`공고.md`, `브리프.md`, `claims.md`, `진행 상황.md`, `경력기술서.md`)은 이 규칙 대상이 아니다
