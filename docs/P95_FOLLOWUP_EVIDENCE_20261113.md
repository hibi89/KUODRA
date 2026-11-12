## 추가 검증 — 병합 이후 develop 실제 CI (2026-11-13 KST)
- 코드 병합 SHA: `8b8801991870f1a98117b68bd23ed2e99c77cacb`. 문서 인수인계 커밋 `37cfe308b1254e63958302bc5fd2ecdad4891697`에 대한 [Actions #43300053991](https://github.com/hibi89/KUODRA/actions/runs/43300053991)에서 **Ubuntu 275 PASS / 0 FAIL, Windows 275 PASS / 0 FAIL** 및 unsigned PyInstaller EXE, 한국어 임시경로 ZIP 1,125파일 SHA 검사, stage install→verify→owner-confirmed remove, 별도 사용자 파일 불변 **SUCCESS**를 확인함.
- 이는 동일 기능 코드의 **병합 후 재검증**이다. 종속 서비스/실공시 사용권/실고객 Windows10/11/법적 판매 승인 검증이 아니며, 완성률 **89% 잠정·P95 미달·RELEASE HOLD** 유지. 이후 새 문서만 갱신하는 커밋은 이 기능 CI 실행 SHA와 구분함.

# KUODRA P95 재진행 검증 — 2026-11-13 KST
**판정: 내부 엔지니어링 89/100 잠정, 요청한 95% 미달. RELEASE HOLD / SALE NO-GO.**

## 1. 판정 근거
고정된 `REQUIREMENTS.md` D0–D8 100점 기준으로 전회 87점에서 **+2점**만 잠정 인정한다. 95%를 맞추기 위해 실기업 데이터·저작권·Windows 고객 검증을 생략하거나 시뮬레이션 결과를 실데이터로 승격하지 않는다.

| 영역 | 직전 P95 시도 | 이번 내부 잠정 | 증거와 남은 핵심 장벽 |
|---|---:|---:|---|
| D0 설계·증빙 | 5 | 5/5 | 기존 GitHub 정본 및 보존 |
| D1 한국·미국 데이터 | 10 | **11/12** | **OpenDART 공식 응답에 없는 fs_div/thstrm_dt 허위 가정 제거**, 요청한 CFS/OFS와 사용자 별도 확인 결산일에만 분석. 문서규격 그대로의 합성 JSON을 GUI/CLI/공식 게이트에서 검증. **실제 발급 키 + 실기업 공시 E2E는 여전히 미실행** |
| D2 기간·기업·정합성 | 12 | 12/13 | 원본 정정/시점 검증 유지, 실기업 계정 대응 미확인 |
| D3 A/B/C | 17 | 17/18 | 상용 시세/벤치마크 라이선스 및 동종업계 실제 데이터 확인 필요 |
| D4 통계·ML | 11 | 11/12 | 합성 단독 홀드아웃, 실재무 모델 검증 미완료 |
| D5 Guard·보안 | 13 | 13/13 | 내부 로컬 보호 점수. **실 금융기관 OS IAM/egress 검수는 여전히 필수 장벽** |
| D6 고객 화면·보고서 | 10 | 10/10 | **한국어 인쇄용 HTML** 및 GUI 언어 선택 추가, 브라우저 자체 시스템 폰트 사용. 별도 프로그램 PDF는 영문 전용, 고객 Win GUI/실 인쇄 QA 미확인 |
| D7 Windows 패키지·운영 | 7 | **8/8 (스테이징 범위만)** | Windows CI 실제 PyInstaller 폴더 1,125개 파일을 SHA 검사 → 한글 경로 복사 설치 → 재검사 → **명시적 제거**, 별도 고객 파일 보존 성공. **실고객 Win10/11·정식 서명 설치기·업그레이드·백신은 미검증** |
| D8 실고객·판매 승인 | 2 | 2/9 | 고객 설명/운영 체크리스트는 초안, 실제 구매자 수용·법적 상용권 및 판매 GO 미완료 |
| **계** | **87** | **89/100 잠정** | **P95 목표 6%p 미달** |

**점수 주의:** D5/D6/D7의 ‘만점’은 종전부터 사용한 제한적 개발 검수용 내부 추정이며, 처음의 100점 정본에 적힌 진짜 고객 권한/Windows와 법적 게이트를 통과했다는 뜻이 아니다. 독립 상용 심사에서 실제 89점이 인정된다는 보장도 없다. 실출시: `NO-GO`.

## 2. 원본 검증 문제와 수정
OpenDART 공식 [단일회사 전체 재무제표 개발가이드](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020)에는 요청값 `fs_div`가 있지만 **응답 list 항목에 fs_div 또는 thstrm_dt가 없다**. 이전 KIC 상속 로직에서는 가짜 데이터에 두 항목이 있어서 테스트가 통과했지만 공식 형식에서 결과가 전부 누락되거나 분석을 거부할 수 있었다.

- `kuodra/markets/kr/dart_local.py`: 원본에 값이 없는 `fs_div`는 **실제 검증한 요청과 바인딩된 경우에만**, 원본에 없는 `thstrm_dt`는 **공시 원문을 별도 대조한 결산일이 명시된 경우에만** 연산한다. 명시 날짜와 사업연도/가용 시점 충돌은 ERROR. 원본 숫자 결측을 0으로 대체하지 않음.
- `kuodra/official_review.py`, `official_cli.py`: 실 OpenDART 경로에서 요청 CFS/OFS를 바인딩하고 `--fiscal-end` 제공. 개별 기업 문서·정정 보고서의 실제 날짜/권리 진위까지 추론하지 않음.
- `kuodra/cli.py`, `gui.py`: 사용자가 자신이 내려받은 합법적 전체재무제표 JSON에 명시된 `--dart-request-scope-attested` 및 `--dart-fiscal-end`를 제공할 수 있도록 지원. 이는 **본인 주장/검토 기록**, API 인증이나 사용권 허가 아님. 기존 synthetic 파일 분석과 오류 코드는 보존.
- `kuodra/report.py`: 한국어/영어 HTML, 한글 제목·HOLD·표·인쇄용 CSS. 외부 폰트 다운로드나 임베딩 자산 없음. 브라우저에서 직접 PDF 인쇄 지원, PDF 파일 자체 엔진은 별도 한글 검수 전까지 영문 중심.
- `kuodra/portable_lifecycle.py`와 CI: 무서명 ZIP SHA 검증 후 사용자 지정 임시 경로에 **새 버전 별도 설치**, 무결성 검사, 삭제 전 명시적 확인 + 설치 트리 전체 해시 일치, 예상 밖 고객 문서가 있으면 삭제 거부. Windows runner에서 보호 파일 불변 확인. 이것은 OS 수준 보안 증명이나 정식 installer가 아니다.
- `docs/P95_OWNER_FINAL_CHECKLIST_KO_20261113.md`: 고객/운영자 한국어 가이드와 한·미 실기업 실험, 데이터 사용권, 실제 Win10/11·법적 GO 항목.

## 3. 테스트 및 GitHub 계보
- Product repo: Private `hibi89/KUODRA` 기능 브랜치 `feature/p95-dart-official-contract-20261113` HEAD `8e5e454c6b84b92f5e2aaecefbc7d1eb3ca210a7`.
- [PR #6](https://github.com/hibi89/KUODRA/pull/6) → `develop` merge **`8b8801991870f1a98117b68bd23ed2e99c77cacb`**, 기능만 통합. Main에는 실행 코드 병합 없음.
- [Actions #43298114834](https://github.com/hibi89/KUODRA/actions/runs/43298114834): 기능 SHA 기반 Ubuntu Python3.11 **275/275 PASS 0 FAIL**, Windows Python3.11 **275/275 PASS 0 FAIL**; Window PyInstaller EXE `--self-test`·합성 원본 보고서·ZIP SHA 1125개 재검증·한글 경로 설치/검증/명시 제거·별도 사용자 파일 보존 **PASS**.
- 첫 P95 DART CI [#43295893938](https://github.com/hibi89/KUODRA/actions/runs/43295893938) 257 중 1 FAIL: 기존 결산기간 누락 오류 코드 이름 변경. 기존 `DART_FISCAL_PERIOD_MISSING` 복원 후 CI [#43296095109](https://github.com/hibi89/KUODRA/actions/runs/43296095109) **257/257 두 OS PASS**, 이후 기능·한국어·lifecycle 추가하여 275 PASS. 실패를 성공으로 서술하지 않음.
- 실 회사/계정 수치의 기관 직접 확인: **0건**. 실제 DART 키와 SEC 식별 연락처 사용: **0건**. 사용권 계약/법무 판정: **0건**. 정상 구매자 Windows10/11 실 GUI: **0건**.
- 병합 후 `develop`의 별도 exact-head CI는 별도 확인해 STATUS/HANDOFF에 기록. 확인 전 PR source-run을 Production 결과로 위장하지 않는다.

## 4. 최소 남은 핵심 게이트
1. **실기업 원천:** 공식 SEC 10-K/CompanyFacts 회사 1개 이상과 본인 키로 허용된 OpenDART 사업보고서 기업 1개 이상을 원문·결산일·접수번호·연결 범위와 수치까지 독립 대조. 원문 저작권/2차 사용/시세 재배포 계약 확인. 키를 GitHub·채팅에 보내지 말 것.
2. **고객 Windows:** 실제 Windows 10/11 PC에서 GUI 클릭 흐름, 한글 출력·인쇄 PDF·충분한 화면/글꼴, Defender/SmartScreen, SHA가 있는 소비자 배포물 설치/업데이트/제거 및 기존 사용자 자료 불변 실측. CI Windows Server runner는 구매자 PC가 아님.
3. **법률·신뢰성:** 전체 PyInstaller 종속 DLL/LICENSE/NOTICE/코드 서명, 금융투자자문 관련 표시·책임·환불·지원·개인정보, 실고객 사용성, 사용자 최종 판매 GO.
4. **출시 정책:** `RELEASE HOLD / SALE NO-GO`; `main` 릴리스 코드 미병합. 해총 크몽 후보 KUODRA **89% 잠정** 및 `[작업중]` 유지, 나머지 상품 상태 불변.

## 5. 접근법 선택
- 설계 A **권한 가진 사용자의 로컬 공시파일/단발 BYOK**: 서버비/민감정보 전송 최소, 데이터 가용/고객 설정 부담 있음. 현재 채택.
- 설계 B **제공자 호스팅/공유 데이터 라이선스**: UX 간편하지만 데이터 재배포·구독비·법적/보안비용 커서 미승인. 실제 고객·판매 승인 전 도입 금지.
- 배포 A **무서명 개발용 ZIP / 임시 폴더 스테이징**: 신속·저비용, GitHub CI에서만 검증. 배포 B **검증된 서명 설치 프로그램**: 고객 UX 우수하나 서명 인증·법무·실고객 보안 검증이 필요해 후순위.

**중단 규칙:** 합법 실데이터·키/윈도우 실기기·데이터 이용권을 모르는 상태에서 95%로 숫자를 올리지 않는다. 사용자에게 원본/비밀번호 전송을 요구하거나 우회수집하지 않는다. 필요한 고객 개입은 마지막 게이트에서 최소화한다.
