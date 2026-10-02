---
name: write-portfolio
description: careerfit 포트폴리오(가로형 덱) 작성. 회사판은 기본 포트폴리오에서 표지·클로징·케이스 순서만 바꿔 build_variant로 파생하고, 기본본 모드는 이력 저장소의 핵심 프로젝트로 케이스 덱을 만든다. apply·setup이 호출한다.
---

# 포트폴리오 작성

규칙: `${CLAUDE_PLUGIN_ROOT}/references/writing-rules.md`(포트폴리오 절), `${CLAUDE_PLUGIN_ROOT}/references/confidentiality.md`, `${CLAUDE_PLUGIN_ROOT}/references/attribution-and-facts.md`

덱 마크업 계약(표지·목차·케이스·연락처 슬라이드 클래스)은 `${CLAUDE_PLUGIN_ROOT}/scripts/build_variant.py` 첫머리 docstring에 있다. 기본본은 이 계약을 지켜야 회사판을 파생할 수 있다.

## 회사판
1. `브리프.md` frontmatter `승인: true` 확인
2. spec JSON 작성:
   ```json
   {"title": "<submission_name(career, '포트폴리오', 회사, ext=None)>",
    "meta": "<회사> <직무> 지원용 포트폴리오",
    "cover_eyebrow": "Portfolio · <직무 키워드>",
    "tagline": "<이력서 태그라인과 같은 문장, <b> 강조 가능>",
    "closing": "<공고에 맞춘 한 문장>",
    "order": [<이야기 설계 순서로 기본본 케이스 번호>]}
   ```
   `order`에서 기반이 되는 케이스는 그 위의 케이스보다 앞에 둔다. `cover_eyebrow`·`order`는 바꾸지 않으면 뺀다
3. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/build_variant.py <base>/{name}_포트폴리오.html <spec.json> <지원 폴더>/<파일명>.html`
4. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome.py pdf <html> <pdf>` → `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pdf_check.py <pdf> --kind slide`. 바뀐 표지·목차·첫 케이스는 `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome.py shot <html> <png> 1123 631`로 눈으로 확인
5. 케이스 본문을 회사에 맞게 바꿔야 하면(드물게) 기본본을 먼저 고치고 다시 파생한다

## 기본본 모드
- `${CLAUDE_PLUGIN_ROOT}/templates/portfolio.html`에서 시작. 케이스 = `임팩트: 핵심` 프로젝트(최대 5개), 보조는 "그 외의 작업" 카드
- 케이스마다 도식은 구조·워크플로(결과 수치 금지), KPI 카드 3개는 결과 지표만 (목표치·기능 개수·운영 기간 금지). 실제 대시보드 스크린샷은 쓰지 않는다
- 범위 재정의 콜아웃이 있는 프로젝트는 그 결론을 케이스 결론으로, 범위 밖 활용 사례는 "활용 사례"로 구분
- 슬라이드 전부를 스크린샷으로 넘침·겹침 확인. 파일명 `{name}_포트폴리오.html/.pdf`
