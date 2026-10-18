# careerfit (커리어핏)

헤드헌터처럼 사용자와 함께 커리어를 정리하고(setup, 이후 갱신은 update), 맞는 공고를 찾고(search), 공고마다 지원 전략을 기획해 서류를 쓰고(apply), 결과를 회고해 다음 지원에 반영하는(track) Claude Code 플러그인. 뭘 해야 할지 모를 때는 helper.

서류를 바로 쓰지 않는다. 공고를 해석하고, 어떤 경력이 맞는지 매칭하고, 무엇을 강조할지 정하고, 빠진 정보를 먼저 묻는다(전략 브리프). 숫자·주장은 출처가 있는 주장 원장(`claims.md`)에서만 가져오고, 제출 전에 세 서류의 숫자·논리·강조·용어·규칙을 교차 검수한다.

설계: `docs/superpowers/specs/2026-10-02-careerfit-design.md` · 구현 계획: `docs/superpowers/plans/2026-10-02-careerfit-mvp.md`

## 진입점

| 스킬 | 언제 | 하는 일 |
|---|---|---|
| `/careerfit:setup` | 처음 한 번 | `CAREER.md` 설정, 프로젝트 단위 이력 저장소, 영역·임팩트 분류 인터뷰, 기본 이력서·경력기술서·포트폴리오 생성. 자료도 연결 도구도 없으면 방향 → 경력 타임라인 → 회사별 책임 → 프로젝트 목록 → 프로젝트 상세 → 할 일 영역 → 나머지 7층 인터뷰(`references/career-interview.md`) |
| `/careerfit:update` | 새 프로젝트·성과·정정이 생겼을 때, 회사판 검수에서 기본본 수정 사항이 쌓였을 때 | 이력 저장소 갱신 → 기본본 3종 부분 수정·재검수 → 진행 중 회사판 파생 갱신 여부 확인 |
| `/careerfit:search` | 지원할 공고를 찾을 때 | 사람인·잡코리아·비즈니스피플(bzpp.co.kr) 수집 → 이력 저장소 기준 적합도 상/중 표 → 고른 공고를 apply로. 처음 실행하면 저장소·인사이트로 조건(키워드·경력 범위·지역·제외어)을 자동 제안해 확정, 이후 새 공고만 보여주고 조건 조정을 제안 |
| `/careerfit:apply` | 공고를 받았을 때 | JD 캡처 → 전략 브리프와 주장 원장 → 빈틈 질문 → 승인 → 서류 3종 파생 → 최종 검수 |
| `/careerfit:track` | 결과를 들었을 때 | 지원 상태 일괄 갱신, 피드백 기록, `insights.md` 회고 |
| `/careerfit:helper` | 뭘 해야 할지 모를 때 | 현재 상태를 읽고 다음 행동 1~3개 제안 |

내부 스킬: `brief`, `write-resume`, `write-career-description`, `write-portfolio`, `review`. 검수 에이전트: `consistency-reviewer`.

## 작업 폴더 구조

```
<career-root>/
├── CAREER.md                     # 설정 (이름·연락처·경로·문체 선호·고정 표기·귀속 주의·저장 후 처리)
├── projects/<프로젝트명>.md       # 이력 저장소 (영역·임팩트 frontmatter, 정정·귀속 콜아웃)
├── base/                         # 기본본 3종 (<이름>_이력서/경력기술서/포트폴리오 .html·.pdf, 경력기술서.md)
├── applications/<회사> <직무>/    # 공고.md 브리프.md claims.md 진행 상황.md + 제출 파일
├── insights.md                   # 회고 누적
└── search/                       # 탐색 결과 (<날짜> 탐색.md, 이미 본 공고 seen.json)
```
경로는 모두 `CAREER.md`의 `paths`로 바꿀 수 있다 (기존 노트 폴더를 그대로 쓰는 경우). 자세한 형식은 `references/schemas.md`.

## 의존성

- 헤드리스 Chromium (PDF 렌더, 비즈니스피플 목록 렌더): `npx playwright install chromium` (Linux·macOS Playwright 캐시, PATH의 chromium·google-chrome, macOS `/Applications` 순으로 자동 탐색) 또는 환경변수 `CAREERFIT_CHROME`에 실행 파일 경로
- Python 3 + `pypdf`, `PyYAML`
- 나눔 폰트 (NanumGothic·NanumMyeongjo) 로컬 설치. `fc-list :lang=ko`로 확인. 웹폰트는 쓰지 않는다

공고 탐색(`scripts/job_search.py`)은 로그인 없이 공개 검색 결과만 읽고 요청 사이 1초 쉰다. 비즈니스피플 목록은 샌드박스를 켠 헤드리스 Chrome(기본 임시 프로필)으로 렌더한다. 샌드박스가 뜨지 않는 환경에서만 `CAREERFIT_CHROME_NO_SANDBOX=1`로 끈다. 사이트 구조가 바뀌면 `references/job-sources.md`와 파서를 같이 고친다.

알려진 한계: 헤드리스 Chrome + 나눔 폰트 PDF는 텍스트 추출 시 공백이 U+0001로 나온다. `pdf_check.py`가 `PDF_ATS_SPACING`(권장)으로 알린다.

## 개발

```bash
uv run --with pytest --with pypdf --with pyyaml pytest plugins/careerfit/tests -q   # 저장소 루트에서
```
Chrome이 없으면 렌더 의존 테스트는 skip된다. 테스트·예시 데이터는 가상 인물(김하늘, (주)가상물산, (주)샘플커머스)만 쓴다. 이 저장소에 실제 이력을 넣지 않는다.

스킬 평가 세트: `evals/evals.json`.

## 실사용 검증 (1단계 완료 조건)
- [ ] 본인 career 폴더(예: vault)에 `CAREER.md`를 만들고 `paths`를 기존 노트 위치로 지정
- [ ] `/careerfit:update`로 기본본 3종이 기존 기본본과 같은 사실·수치를 유지하며 갱신되는지
- [ ] 실제 공고 1건을 `/careerfit:apply`로 끝까지 처리 (브리프 승인 → 서류 → review 필수 0건)
- [ ] `/careerfit:track`으로 상태 기록, `insights.md` 첫 행
- [ ] `/careerfit:search` 첫 실행 조건 제안이 본인 이력과 맞는지, 세 소스 모두 결과가 나오는지
- [ ] 빈 폴더에서 `/careerfit:setup` 처음부터 인터뷰를 1~7층 끝까지 (중간에 멈췄다 이어가기 포함)
- [ ] 위 과정에서 나온 문제를 이슈로 남기고, vault 스킬 3개를 "careerfit 사용" 안내로 줄이는 작업은 별도 PR
