# KUODRA 상용화 P95 — 최소 사용자 개입 검수 체크리스트 (2026-11-13 KST)
**개발용 안내 초안. 구매자 배포/판매 허가 아님 · RELEASE HOLD.**

## 0. 확인된 범위와 할 수 없는 범위
- 현재 프로그램은 원본 공시를 **확인할 수 있도록 근거와 계산식을 제시하는 보조 도구**이며 투자추천/수익률 예측·자동매매를 제공하지 않는다.
- 한국 OpenDART 형식과 미국 SEC CompanyFacts 형식을 지원한다. DART API 조회가 성공해도 회사가 작성한 공시 원문·저작물, KRX/Nasdaq 시세 데이터의 **재배포 권리**가 자동으로 허가되는 것은 아니다.
- KIC 해커톤 제출물·기관 비공개자료는 상용 사용자 문서와 별개이며 배포 대상에서 제외한다.
- 분석 결과 상태는 기본 **HOLD(검토 보류)**이고 `원천발행기관 확인·이용권 검수·실 고객 검증`과 동일한 뜻이 아니다.
- GitHub Actions Windows 실행파일/ZIP은 **미서명 개발 스테이징**이다. 다운로드 가능한 정식 구매자 설치 프로그램이나 인증 완료 소프트웨어라고 표시하면 안 된다.

## 1. 고객이 실제로 보게 될 UX — 검증해야 할 사항
- 국가 KR/US, 회사 고유번호(KR 8자리 / US CIK 10자리), 회계기준일, 연결/별도, 합법 보유한 파일 선택, 결과 저장 경로, 한국어/영어 HTML을 선택한다.
- 로컬 공시 근거·재무 산식·표·그래프와 위험 검토 사유를 확인한다. 한국어 HTML은 **운영체제 내장/설치된 폰트**만 참조하므로 별도 폰트 파일을 포함하지 않는다. 브라우저 인쇄 → PDF 저장을 권장한다.
- 별도 ReportLab PDF는 **ASCII/영문 중심**이다. 한국어 텍스트는 라이선스/폰트 검수 전에는 조용히 깨뜨리지 않고 오류로 차단한다.
- 정상 재검증: 저장한 HTML/JSON/(PDF) 및 `*.receipt.json`의 바이트 무결성을 독립 확인한다. 영수증은 **무서명**, 공시 진위·출처 인증 아님.
- 과거 보고서 이름이 있거나 사용자 문서가 있는 폴더에는 자동 덮어쓰기하지 않는다. 실패한 부분 파일은 사용자가 확인할 때까지 임의 삭제하지 않는다.

## 2. 마지막에 사용자가 직접 확인해야 할 최소 항목
실제 API 키/민감 원본을 ChatGPT·메일·GitHub에 붙여넣지 않는다.

| 항목 | 사용자가 할 최종 작업 | 지금 상태 |
|---|---|---|
| SEC 1개 실제 발행사 | 본인의 실제 연락처가 들어간 식별 User-Agent를 본인 PC의 `KUODRA_SEC_USER_AGENT`로 설정하고 공식 CIK를 골라 승인된 1회 조회/재무 원본 대조 | 미실행 |
| OpenDART 1개 실제 발행사 | 공식 회원에게 발급된 40자리 본인 API 키를 본인 PC 환경변수 `KUODRA_DART_API_KEY`에 보관, 실제 corp_code/bsns_year/fiscal_end 확인 | 미실행 |
| 자료 이용권 | 서비스/API 약관, 원문 저작물·수치/가공 결과 재배포, 시세·지수 데이터 권리 범위를 상품 SKU별 확인 | 미확인 |
| 고객 Windows 10/11 | 실 PC에서 패키지 실행·한글 폴더·GUI 조작·HTML/인쇄 PDF·백신 반응·재시작·새 버전 병행 설치·삭제 및 사용자 파일 보존 확인 | 미실행 |
| 판매/법률 | 한국 금융 관련 행위 범위·표시광고·개인정보·소프트웨어 종속 라이선스/NOTICE·환불·AS·가격·지원 범위 및 사업자 요건 확인 | 승인 대기 |

## 3. 실제 입력을 사용할 때의 안전한 로컬 명령 (PC 개발자 점검용)
아래는 사용자가 본인 PC에서만 수행할 수 있는 **검증 명령 예시**다. 제3자 계정의 키 사용이나 임의 개인정보 전송을 허가하지 않는다.

```powershell
# Windows PowerShell, USER LOCAL ONLY
# SEC: 설정 예시는 형식이며 실제 식별 가능한 본인 연락처로 교체해야 함
# $env:KUODRA_SEC_USER_AGENT = 'KUODRA/1.0 (real-operator-contact@example.com)'
python -m kuodra.official_cli --country US --issuer-id 0000320193 --as-of 2026-11-13 --output-dir 'C:\Temp\kuodra-us-empty' --name us-1 --html-language ko --consent

# DART: 실제 API 키는 별도 공식 발급, 채팅/저장소에 붙여넣지 말 것
# $env:KUODRA_DART_API_KEY = <owner local secure input>
# 회계기간 종료일은 OpenDART fnlttSinglAcntAll 응답에 없으므로 원문 사업보고서에서 별도 대조해 입력
python -m kuodra.official_cli --country KR --issuer-id 00126380 --business-year 2024 --fiscal-end 2024-12-31 --as-of 2026-11-13 --output-dir 'C:\Temp\kuodra-kr-empty' --name kr-1 --html-language ko --consent
```

**중요:** 위 코드는 인증정보와 권한을 가진 사용자의 명시적 동의가 있을 때만 사용한다. 출력 폴더는 사용자가 미리 만든 빈 폴더여야 한다. 특정 실기업의 응답 형식/수치·원본 진위 또는 2024년 자료의 회계기간이 실제로 정확한지 **이 문서에서는 보장하지 않는다**. 회사별 결산일은 반드시 개별 확인한다. 호출 오류(403/429/DART 010/013/020) 시 우회하지 말고 중단한다.

### 이미 적법하게 보유한 DART JSON
OpenDART `fnlttSinglAcntAll`의 실제 응답 항목에는 `fs_div`와 `thstrm_dt`가 없다. `fs_div`는 API *요청* 항목이다. 공식 API를 직접 호출해 저장한 사용자 파일이라면, 호출 당시 연결/별도 범위를 본인이 확인한 경우에 한해 다음과 같이 분석한다. 아무 파일의 scope를 임의로 확인했다고 주장하지 않는다.

```powershell
python -m kuodra.cli --country KR --issuer-id 00126380 --as-of 2026-11-13 --source 'C:\Temp\my-authorized-dart-2024.json' --statement CFS --dart-fiscal-end 2024-12-31 --dart-request-scope-attested --output-dir 'C:\Temp\kuodra-offline-empty' --name local-kr --html-language ko
```
이 옵션은 *사용자 확인 기록*이지 기관 인증이 아니다. 원본 파일이 연결 CFS인지 모르면 **확인 체크를 하지 말고 중단**한다. 잘못된 기업·회계기간·공시 시점에는 HOLD 또는 ERROR가 정상이다.

## 4. 품질·지원·가격 문구 (초안 / 법무·운영 미승인)
- 고객 문의 시 원본 기업/금액/연락처/키를 먼저 요구하지 않는다. 제품 버전/SHA, 오류코드, 사용 국가/문서 형식과 **합성 재현 사례**를 우선 받는다.
- `HOLD`: 수치 검토 또는 사용권/출처·기간 확인이 필요하다. 오류를 무시하고 매수·매도 판단에 바로 사용하지 않는다.
- `NO_TRAIN`: ML 표본 또는 검증 설계 부족. 예측 성공률 보장·자동거래 권유 금지.
- `OUTPUT_EXISTS_NO_OVERWRITE`: 새로운 저장 이름과 빈 폴더를 사용하되 기존 보고서/고객파일을 삭제하지 않는다.
- 초기 BASIC/PRO 가격은 기존 별도 상품 기획의 **시장검증 가설**이지 현재 승인된 판매가 아니다. 고객 지원 시간, 환불 책임, 계약 및 데이터 권리 확보 전 판매 등록 금지.
- 미서명 실행파일에 대해 Windows Defender/SmartScreen 경고가 나오면, 사용자에게 보안 설정을 강제로 해제하라고 안내하지 말고 검증을 중단한다.

## 5. 완료 판정
개발자의 합성 테스트 PASS, GitHub CI SUCCESS, SHA 맞는 ZIP, 무서명 영수증은 **제품 95%/100%·실사용 적합성·상업적 권리 증거로 자동 승격되지 않는다.** 실제 기업 KR/US 근거, 고객 Windows 물리 환경, 라이선스·환불·법률·판매자 승인까지 모두 확인되어야 릴리스 GO를 검토한다.

원본 문서: [OpenDART fnlttSinglAcntAll](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020), [SEC API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces).
