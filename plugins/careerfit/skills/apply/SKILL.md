---
name: apply
description: careerfit 공고 단위 지원 진입점. 채용 공고(링크·텍스트·이미지)를 받으면 JD를 캡처하고, 전략 브리프와 주장 원장을 만들어 빈틈만 묻고 승인받은 뒤, 필요한 서류(이력서·경력기술서·포트폴리오)를 기본본에서 파생해 쓰고, 최종 일관성 검수를 거쳐 지원 폴더에 기록한다. 사용자가 공고 링크를 보내거나 "이 회사 지원 준비해줘", "이 공고에 맞춰 서류 만들어줘"라고 할 때, search 스킬에서 공고를 고른 뒤에 쓴다. CAREER.md나 기본본이 없으면 setup을 먼저 안내한다.
---

# 공고 단위 지원

## 0. 선행 확인
- 작업 폴더의 `CAREER.md`를 `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/config.py <CAREER.md>`로 읽는다. 없으면 setup 스킬로 안내하고 멈춘다
- `<base>/`에 기본본 3종이 있는지, 이력 저장소보다 오래되지 않았는지 확인한다 (가장 최근 프로젝트 노트 `modified`와 기본본 파일 수정 시각 비교). 오래됐으면 update를 먼저 권한다
- `<applications>/`에 같은 회사·직무 폴더가 있으면 새로 만들지 않고 이어서 진행한다
- search에서 넘어온 공고면 지원 폴더를 만든 뒤 `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/job_search.py mark <search>/seen.json <source:id> 지원`

## 1. JD 캡처
- `${CLAUDE_PLUGIN_ROOT}/references/jd-capture.md` 절차로 `<applications>/<회사> <직무>/공고.md`를 만든다
- 상태 기록: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/status.py set <공고.md> "준비 중" "$(date "+%Y-%m-%dT%H:%M:%S%:z")"`

## 2. 브리프 (승인 게이트)
- brief 스킬을 따른다. `브리프.md`가 `승인: true`가 되기 전에는 3단계로 가지 않는다

## 3. 서류 작성
- 브리프의 서류 계획에 있는 것만: write-resume, write-career-description, write-portfolio 스킬
- 세 서류 모두 `claims.md`의 표기와 이야기 설계 순서를 따른다

## 4. 최종 검수
- review 스킬. 필수 0건이 될 때까지 수정·재검수

## 5. 기록과 마무리
- `진행 상황.md`: 무엇을 어떤 JD 문구에 맞춰 바꿨는지, 브리프 핵심 결정, 빈틈 질문과 답, 검수 결과, 제출 파일 경로
- 제출 파일명은 `${CLAUDE_PLUGIN_ROOT}/references/filenames.md`
- `CAREER.md`의 `## 저장 후 처리`를 그대로 수행한다 (예: 브랜치·PR·동기화). 없으면 파일만 둔다
- 사용자에게 알릴 것: 제출 파일 경로, 남은 권장 항목, 면접 방어가 어려운 주장, 결과가 나오면 track으로 기록하라는 안내
