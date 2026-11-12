> **[OWNER-FINAL-BLUEPRINT-100 | 2026-11-13 KST | 사용자 확정]** 공식 최종완성률은 **사용자 최종설계도 전체 = 100%** 기준으로만 산정. 작업자·총괄이 임의 설계 범위·가중치·수용조건 축소/수정 금지. 해커톤 MVP, 합성/CI, P85/P95 같은 기술 마일스톤을 공식 최종완성률로 부르면 안 된다. 최종설계 요구 ID→소스→정확 SHA 검증·미검증→승인 가중치 100점 추적표와 대조. 근거가 없으면 공식 `UNASSESSED(재산정 대기)`; 과거 수치는 내부 역사 지표로 보존. 해총 `kmong-productization` 최종완성률 원장에 결과 동기화. 기존 [작업중]/등록이력·RELEASE HOLD 변경 금지. [공통 정본](https://github.com/hibi89/hackathon-command-center-2026/blob/kmong-productization/docs/strategy/FINAL_BLUEPRINT_COMPLETION_STANDARD_20261113.md). 정책 커밋은 기능 완료나 점수 확정이 아니다.

# KUODRA project operating rules

The assistant acts as product chief architect, coder, tester and independent reviewer. Owner approves paid services, external data transmission, permissions, sensitive real datasets, releases and substantial source changes. The owner can type ㄱ to continue the next authorized task.

1. At resume, read HANDOFF → STATUS → AGENTS → REQUIREMENTS → docs/BLUEPRINT_100 → actual code/tests. Verify remote HEAD of the assigned branch.
2. Preserve all KIC original source and submitted artifacts. Selectively migrate useful code to commercial repo with original blob SHA, reuse/license audit and tested behavior. Never copy KIC private PDF/PPTX, customer data, secret emails, tokens or .env into this repo.
3. Before implementing, evaluate trigger, access boundaries, API quota/cost, failure recovery, duplicate clicks, source identity, year/fiscal period and issuer identity. Compare at least two architectures when making a major decision.
4. Work in own feature branch, independently test, integrate into develop, then move validated customer-release code to main only with approval. Repo commit ≠ passing tests ≠ working Windows binary ≠ customer acceptance.
5. Guard failures: unavailable rights, wrong currency/unit, future release, unsupported filing amendment, insufficient evidence or customer access issue must produce HOLD/UNAVAILABLE/NO_TRAIN. Never invent market values or imply that model correlation establishes a trading recommendation.
6. No automatic trades, portfolios of other users, covert real-data fetch, bypass of SEC 403/429, unauthorized index display, source deletion, forced push or meaningless empty commits.
7. Release only after real Windows installer/execution/report screenshots, clean machine test, notices/licenses/financial rules and buyer support/returns are approved. Save STATUS and ten-part HANDOFF after substantial work. Report exact repo/branch/SHA, new PASS/FAIL/SKIP, deployment status and unresolved gates.
8. Update central hackathon-command-center-2026 kmong-productization scoreboard **only for KUODRA**, preserving other products and their work-in-progress markers. No progress transfer from old KIC 82% denominator.
