# 공고 탐색 소스와 조건 (2026-10-19 확인)

search 스킬과 `scripts/job_search.py`가 쓰는 규칙. 사이트 구조가 바뀌면 이 문서와 스크립트 파서를 같이 고친다.

## 탐색 조건: `CAREER.md` frontmatter `search`
```yaml
search:
  keywords: [수요예측, 데이터 분석, 사업기획]   # 검색어. 하나당 소스별로 한 번씩 검색
  exclude: [인턴, 신입, 계약직]                 # 제목에 있으면 버린다
  career_years: [5, 12]                         # 요구 경력 범위(년). 없으면 경력 필터 안 함
  locations: [서울, 경기]                       # 근무지 글자 포함 검사. 근무지를 모르는 공고는 남긴다
  sources: [saramin, jobkorea, bzpp]
  pages: 1                                      # 사람인·잡코리아 검색 페이지 수 (bzpp는 항상 1)
  must: [정규직]                                # (선택) 스크립트는 안 쓰고, 적합도 평가 때 Claude가 확인
  prefer: [이커머스, 플랫폼]                     # (선택) 가산점 기준
  updated: 2026-10-19
```
- 조건 근거(왜 이 키워드인지)는 본문 `## 탐색 조건 메모`에 한두 줄씩 남긴다. 다음 탐색의 자동 제안이 읽는다

## 소스별 특성

| 소스 | 검색 URL | 읽는 방법 | 경력 필터 | 특징 |
|---|---|---|---|---|
| 사람인 `saramin` | `saramin.co.kr/zf_user/search/recruit?searchword=` | 서버 렌더 HTML (`item_recruit` 카드) | `exp_cd=2&exp_min=&exp_max=` | 근무지·경력·고용형태·마감이 카드에 있음. 한 페이지 40건 |
| 잡코리아 `jobkorea` | `jobkorea.co.kr/Search/?stext=&tabType=recruit` | 페이지 안 Next.js 데이터(`self.__next_f.push`)의 검색 결과 JSON | `careerType=2` (경력 연수 범위는 상세에서 확인) | 상단 "나에게 꼭 맞는 공고" 등 광고 블록은 `totalElements`가 가장 큰 결과만 써서 거른다. 근무지는 역·구 이름만 와서 `location_hint`로만 둔다 |
| 비즈니스피플 `bzpp` | `bzpp.co.kr/recruit/recruit?srchRecruitEnterpriseList=` | 목록이 JS로 채워져 헤드리스 Chrome `--dump-dom` | `searchStartCareer=&searchEndCareer=` | 고급인재·헤드헌팅 공고 위주. 키워드 매칭이 느슨해(관련도순) `kw_in_title`이 false인 공고가 많다. 헤드헌팅 공고는 회사명이 가려져 `(헤드헌팅: <헤드헌터>)`로 나온다 |

상세 페이지:
- 사람인 `https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=<id>`: 이 페이지는 본문을 JS로 불러온다. 본문은 `https://www.saramin.co.kr/zf_user/jobs/relay/view-detail?rec_idx=<id>`를 바로 읽는다 (서버 렌더)
- 잡코리아 `https://www.jobkorea.co.kr/Recruit/GI_Read/<id>`: `jd-capture.md`의 iframe(`GI_Read_Comt_Ifrm`) 절차
- bzpp `https://www.bzpp.co.kr/biz/businessDetailView/<id>`: 서버 렌더 HTML이라 바로 읽힌다

## 수집 예절
- 로그인하지 않는다. 공개 검색 결과와, 적합도 평가 대상 상세 페이지만 연다 (한 번에 상세 최대 15건)
- 요청 사이 1초 쉰다 (스크립트 기본값). 개인 구직 용도로만 쓰고 결과를 재배포하지 않는다
- bzpp 렌더는 Chrome 샌드박스를 켜고 헤드리스 기본 임시 프로필로 연다(사용자 프로필·쿠키를 쓰지 않는다). 샌드박스가 뜨지 않는 환경(컨테이너 root, Ubuntu의 user namespace 제한)에서는 렌더가 실패하고 안내가 나온다. 그때만 사용자 동의를 받아 `CAREERFIT_CHROME_NO_SANDBOX=1`로 실행하거나 `--sources saramin,jobkorea`로 bzpp를 뺀다
- 0건이거나 오류가 나면 차단·구조 변경일 수 있다. 같은 URL을 반복해 두드리지 말고 사용자에게 알린 뒤 다른 소스로 진행한다

## 이미 본 공고: `<search>/seen.json`
- 키 `<source>:<id>` → `first_seen`, `company`, `title`, `decision`(`관심` / `제외` / `지원` / 없음), `reason`, `decided`
- fetch가 새 공고에 `new: true`를 붙이고 기록한다. 사용자의 결정은 `job_search.py mark`로 남긴다
- `제외` 사유가 쌓이면 다음 조건 제안에서 `exclude`·`must`로 옮길지 묻는다
