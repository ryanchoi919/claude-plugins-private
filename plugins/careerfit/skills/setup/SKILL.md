---
name: setup
description: careerfit 최초 세팅 (처음 한 번). CAREER.md 설정을 만들고, 기존 이력서·경력기술서·포트폴리오·LinkedIn·메모로 프로젝트 단위 이력 저장소를 채우고, 영역·임팩트 분류와 사실관계를 인터뷰로 정리한 뒤 기본 이력서·경력기술서·포트폴리오를 처음 만든다. "커리어 정리해줘", "이력 세팅", "careerfit 시작"이라고 할 때 쓴다. CAREER.md와 기본본이 이미 있으면 update 스킬이 맡는다.
---

# 커리어 정리·세팅

스키마: `${CLAUDE_PLUGIN_ROOT}/references/schemas.md`. 사실 규칙: `${CLAUDE_PLUGIN_ROOT}/references/attribution-and-facts.md`

판정: 작업 폴더에 `CAREER.md`와 `<base>/` 기본본 3종이 모두 있으면 이미 세팅된 것이다. 새 프로젝트·정정·기본본 갱신 요청이면 update 스킬로 넘기고 멈춘다. `CAREER.md`는 있는데 기본본이 없으면 아래 5단계(기본본)부터 한다.

## 처음 실행
1. **설정**: `CAREER.md`를 만든다 (이름, 연락처와 서류 전용 여부, `career_start`, `paths`, `market: KR`, `money_policy`). 이미 프로젝트 노트 폴더가 있으면 그 경로를 `paths.projects`로 지정하고, 2~3단계는 빠진 노트만 보충한다. 만든 뒤 `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/config.py <CAREER.md>`로 경로가 맞게 풀리는지 확인한다
2. **재료 수집**: 기존 이력서·경력기술서·포트폴리오(PDF·Word·이미지·링크), LinkedIn 내보내기, 메모를 요청한다. 연결된 도구(메일·메신저)가 있으면 근거 확인용으로만 쓴다
3. **이력 저장소 작성**: 프로젝트마다 노트 하나 (스키마의 frontmatter·본문·콜아웃). 수치마다 출처, 사건마다 귀속. 근거가 약하면 `[확인 필요: ...]`
4. **정리 인터뷰**: 저장소로 판단할 수 없는 것만 묻는다
   - 프로젝트별 `영역`·`임팩트` 분류를 제안하고 확정한다. 핵심은 이후 일을 가능하게 한 기반인지, 지원할 공고 유형에서 전면에 설 만한지 함께 본다. 분류가 애매하면 사용자에게 묻는다
   - 근거 약한 수치·범위·귀속을 정정한다. 답은 노트 콜아웃 `> [!note] ... (YYYY-MM-DD 본인 확인)`으로 남긴다
5. **기본본 3종**: write-resume, write-career-description, write-portfolio 스킬의 기본본 모드 → review 스킬 기본본 모드

## 마무리
- `CAREER.md`의 `## 저장 후 처리`를 수행한다
- 이후 사실 정정·새 프로젝트·기본본 갱신은 update 스킬로 한다고 알린다
