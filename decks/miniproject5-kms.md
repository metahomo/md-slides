---
marp: true
paginate: true
theme: orange
footer: 미니 프로젝트 5 · KMS 논문 보고서 작성기
---

<!-- _class: lead -->
# 미니 프로젝트 5

### KMS 논문 보고서 작성기 — ML 시스템 클라우드 배포

가용 가능한 GPU를 점검하여 서버에서 LLM의 판단을 효과적으로 제공하고, 검증을 통과한 것만 운영에 들인다 · 2026-11

<!-- 부제 한 줄이 발표 전체의 결론이다. 순서: 1 아키텍처 이유와 Flow(필수) → 2 AI 활용(필수) → 3 강의 대비 개선점(옵션) → 4 AI에게 서비스(옵션). 도메인은 짧게, 기술 선택의 이유에 시간을 쓴다. -->

---

## 발표 순서 — 필수 둘, 옵션 둘

| 절 | 답하는 질문 |
|---|---|
| **1. 아키텍처 이유와 Flow** (필수) | 무엇을, 왜 이렇게, 실제로 돌았나 |
| **2. AI 활용** (필수) | AI에게 무엇을 맡기고 어떻게 믿었나 |
| 3. 강의 대비 개선점 (옵션) | 강의보다 무엇을 더 했나 |
| 4. AI에게 서비스 (옵션) | AI가 쓴다면 어떻게 내놓나 |

<p class="fragment"><b>시연은 한 줄</b>: 코드 변경 → 배포 · 데이터 변경 → 학습·게이트 → 승격 → 롤백</p>

<!-- 과제의 다섯 기능(R1~R5): Lightsail · GitHub CI/CD · 자동 학습과 검증 · 모델 API 배포 · 롤백. 시연은 이 흐름 하나로 묶는다. 시연 대본: presentation/05-demo-script.md -->

---

<!-- _class: lead -->
# 1. 아키텍처 설계의 이유와 Flow

<!-- 절 구분 장. -->

---

## GPU가 없어 LLM은 교사로, CPU 학생 모델을 배포했다

*문제와 해법 — 도메인 설명은 이 한 장으로 끝낸다*

- **무엇을**: 논문 제목·초록 → 주제(coaching-leadership)에 맞을 확률 `p(include)`
- **문제**: KMS의 LLM 판정은 GPU가 필요 → Lightsail에서는 못 돌린다
- **해법**: LLM은 **교사**(라벨), CPU 모델은 **학생**(서빙) — 증류

<!-- KMS: 논문을 모아 로컬 LLM 이 포함/제외를 판정하는 연구용 지식 관리 시스템. 근거: reports/2026-11-18-kms-feasibility.md, ADR-005 -->

---

## 전체 흐름 — pipeline 은 둘

*코드와 모델은 다른 길로, 각자 검증을 거쳐서만 운영에 들어간다*

```text {1,3}
[code]     PR / v* 태그 → ci: pytest → 이미지(GHCR) → 서버 교체 → /health
[model]    KMS → 교사 라벨 → snapshot(원문 없음) → model: 학습
           → 게이트 → ONNX → parity → 버킷 → 서버 → current.json
[rollback] rollback.yml(모델) · 직전 태그 ci 재실행(코드)
[ledger]   실행·배포·예측 → PostgreSQL (미통과 version 배포 기록은 트리거가 거부)
```

<!-- 강조한 두 줄이 검증 지점(pytest, 게이트·parity)이다. 강의 03의 "코드 판과 모델 판" 구분. 원본 그림: architecture/overview.md. 시연 장에서 이 그림을 한 칸씩 실제 실행으로 보여 준다. -->

---

<!-- _class: dense -->

## CPU로 싸게 · 배포되는 그 이미지로 · 규칙은 DB가

*기술 선택의 이유*

| 구성 요소 | 선택 | 이유 |
|---|---|---|
| 학생 모델 | 해싱 글자 n-gram → TF-IDF → 로지스틱 회귀 | CPU만으로 싸고 빠르게 |
| 서빙 | FastAPI + onnxruntime 컨테이너 1종 | 그 이미지로 parity 검사 |
| 학습 위치 | GitHub-hosted runner | 서버는 서빙·승격만 |
| ledger | PostgreSQL + 트리거 | 미통과 version 배포를 DB가 거부 |
| 공개 | HTTPS + 토큰 + rate limit | 보호 없는 공개 금지 |

<!-- 출처: ADR-002(PostgreSQL), ADR-003(도메인), ADR-005(모델), ADR-006(게이트). 이유 칸은 연구자의 말로 다듬어 말한다. -->

---

<!-- _class: small -->
## 데이터 — 원문 없이 공개해도 학습은 재현된다

*공개 저장소에는 해싱 특징만 올린다*

<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5em">
<div>

### snapshot 에 넣는 것

- 공개 식별자 · 라벨 · 해싱 특징
- 분할 = key hash % 5 (test set 고정)

</div>
<div>

### 넣지 않는 것

- 제목 · 초록 원문 (저작권)
- 해싱 특징은 원문으로 되돌릴 수 없다

</div>
</div>

<p class="fragment">첫 snapshot <b>867편</b> — include 641 · exclude 211 · uncertain 15 · 11-20 새 7편 더해 874편</p>

<!-- ADR-005. 분할: 열쇠 해시 % 5 == 0 → 게이트 시험지(약 20%, 178편). 새 데이터가 와도 기존 논문의 분할은 바뀌지 않는다. 대안이었던 원문 저장은 저작권, 식별자만 두고 학습 때 API 로 다시 받기는 재현성 때문에 버렸다. -->

---

## 시연 ① 시험을 통과한 코드만 서버로 간다

*코드 변경 → 배포*

```text {3}
PR · main → ci test(pytest) → 통과해야 image
  → v* 태그면 GHCR 푸시 → 서버 runner 가 server.sh image 로 교체
  → /health 실패하면 이전 version 으로 스스로 복귀
```

<!-- 작업용 서버 https://54-252-22-31.sslip.io (Let's Encrypt, HTTP→308). image 잡은 needs: test — 시험 실패 코드는 이미지조차 만들지 않는다. -->

---

## 태그마다 한 겹씩 더했다

*v0.1.1 첫 자동 배포 → 지금 운영은 v0.1.5*

| 태그 | 바뀐 것 |
|---|---|
| v0.1.1 | 작업용 서버 첫 자동 배포 (릴리스) |
| v0.1.2 | 예측 로그 — 원문 없이 해시·점수만 ledger 에 |
| v0.1.3 | 공개 API 보호 — 토큰 401/200, 분당 60 초과 429 |
| v0.1.4 | 원격 MCP `POST /mcp` (릴리스) |
| **v0.1.5** | 입력 검증 버그 3건 · 시험 32→87 (릴리스) |

<!-- 릴리스는 v0.1.1 · v0.1.4 · v0.1.5 (v0.1.5 = PR #54·#55, 11-20; v0.1.4 릴리스에 v0.1.2~0.1.4 묶음: 예측 로그·API 보호·원격 MCP·자동 복귀 보강·복구 훈련·스킬). 증거: v0.1.1 https://github.com/metahomo/miniproject5_kms/actions/runs/44513840582 · v0.1.4 https://github.com/metahomo/miniproject5_kms/actions/runs/44543294166 -->

---

## 시연 ② 게이트 셋 — 하한 하나로는 약한 모델을 못 거른다

*test set 이 불균형(include 140/178 = 79%)이라 2번이 핵심이다*

1. include F1 ≥ **0.80** (하한)
2. F1 ≥ **기준선 + 0.05** — "전부 include"만 답해도 F1 0.8805
3. 운영 모델보다 **0.02** 넘게 떨어지지 않을 것

<p class="fragment">test set = 교사 라벨 고정 20% (178편)</p>

<!-- ADR-006. 기준선은 데이터마다 다시 잰다 — 11-19 0.8805, 새 7편을 더한 11-20 0.882. 하이퍼파라미터 C 를 게이트 시험지로 고르면 시험지에 과적합하므로 미리 정한 4를 유지했다. -->

---

## 시연 ② 검증이 실제로 막았다

*F1 0.9021 — 하한은 넘었지만 baseline 조건(0.9305)에서 멈췄다*

| 모델 | 학습 편수 | 게이트 F1 | 결과 |
|---|---|---|---|
| 전체 데이터 | 674 | **0.9603** | 통과 |
| 데이터 5% (m20261119-9) | 33 | 0.9021 | **실패** → 승격 건너뜀 |

> [!IMPORTANT]
> 하한 하나였다면 **통과했을 모델**이다

<!-- 배포를 켠 상태의 차단 실행: https://github.com/metahomo/miniproject5_kms/actions/runs/44515846566 (F1 0.9021 < 기준선 0.8805 + 0.05, parity·promote 건너뜀). 학습 편수 출처: ADR-006. -->

---

## parity — 배포 이미지가 원본과 같은 답이어야 승격

*허용 1e-5*

- 원본 sklearn ↔ **실제 서빙 이미지(ONNX)** 확률 차이: Actions **5.8e-7** · 최신 version 5.5e-7
- 잡은 문제: `sublinear_tf=True` → 변환 뒤 **0.0018** 어긋남 → 끄고 4.4e-9
- 허용치를 1e-12로 좁히면 parity에서 멈추고 승격 건너뜀 (m20261119-12)

<p class="fragment">변환기 옵션 하나로 모델이 달라진다 → 학습 직후와 이미지, 두 곳에서 본다</p>

<!-- float32 입력도 오차가 커서 ONNX 입력을 double 로 했다. 최신 판 = m20261120-24(11-20 최종 서버 개통 때 같은 데이터로 재학습, F1 0.9609 · parity 4.1e-7). 새 데이터 판은 m20261120-17(PR #44). parity 차단 실행: https://github.com/metahomo/miniproject5_kms/actions/runs/44519475156 -->

---

<!-- _class: dense -->

## 시연 ③ 통과한 version 만 승격, 미통과 version 은 DB가 거부

*승격 — 학습 run 기록과 ledger*

| model version | 게이트 | parity | 승격 |
|---|---|---|---|
| m20261119-7 · 8 · 11 | 통과 | 통과 | **승격** |
| m20261119-9 (데이터 5%) | 실패 | — | 보류 |
| m20261119-12 (허용 1e-12) | 통과 | 실패 | 보류 |
| m20261120-17 (새 데이터) | 통과 | 통과 | 승격 |
| **m20261120-24** (최종 서버 개통) | 통과 | 통과 | **승격 — 두 서버 운영** |

<p class="fragment">ledger 트리거: <code>ERROR: model m20261119-9 has not passed gate and parity</code></p>

<!-- 정본은 운영 장부 DB model_versions, 사본은 experiments/. 버킷 paperclf-models-apse2(키 없이 리소스 액세스). 증거: 승격 →7 https://github.com/metahomo/miniproject5_kms/actions/runs/44514427871 · →11 https://github.com/metahomo/miniproject5_kms/actions/runs/44519470540 -->

---

## 새 데이터가 들어오면 — 사람 손 없이 재학습·승격

*R3의 실제 흐름: KMS가 모은 새 논문 7편으로 자동 재학습*

```text {3}
KMS 수집 새 논문 7편 → 교사 라벨(include 6 · exclude 1) → snapshot PR
  → main 병합 = data/snapshots 변경 → model 자동 실행
  → 게이트 F1 0.9609 → parity 5.5e-7 → 승격 m20261120-17 → ledger 기록
```

> [!TIP]
> 사람이 한 일은 **병합 한 번**

<!-- PR #44, 실행 https://github.com/metahomo/miniproject5_kms/actions/runs/44643935701. snapshot이 여러 개면 이름순으로 합치고(뒤 파일 우선) 장부는 데이터셋 하나로 센다. -->

---

## 시연 ④ 롤백 — 되돌렸다가 다시 앞으로

*매번 `/health`의 version 번호가 일치했다*

| 무엇을 | rollback | roll-forward | 그대로 |
|---|---|---|---|
| 모델 (`rollback.yml`) | m20261119-8 → 7 | 7 → 8 | 이미지 |
| 코드 (직전 태그 ci 재실행) | v0.1.1 → v0.1.0 | → v0.1.1 | 모델 |

<!-- runbooks/rollback.md. 증거: →7 https://github.com/metahomo/miniproject5_kms/actions/runs/44514983743 · →8 https://github.com/metahomo/miniproject5_kms/actions/runs/44515052182 · 코드 v0.1.0 https://github.com/metahomo/miniproject5_kms/actions/runs/44453216170 -->

---

## 깨진 version 은 37초 만에 스스로 돌아왔다

*롤백 순서와 자동 복귀*

- 이전 version 을 먼저 띄우고 `current.json`은 **마지막에** 바꾼다
- 일부러 깨진 version(가짜 ONNX)을 넣었다 → `/health` 30초 실패
- 이전 version m20261119-11로 **복귀·확인까지 37초**

<!-- 자동 복귀 시연은 PR #36(server.sh 보강). 2026-11-19 22:55. -->

---

## 운영 — 지금 실제로 돌고 있다

*작업용 서버 하나에 code version·model version 이 함께*

| 항목 | 지금 |
|---|---|
| 주소 | `https://54-252-22-31.sslip.io` |
| version | app **v0.1.5** · model **m20261120-24** (F1 0.9609 · parity 4.1e-7) |
| 보호 | 토큰 · 분당 60 · 보안 헤더(HSTS · nosniff · no-referrer) |
| 릴리스 | v0.1.1 · v0.1.4 · v0.1.5 |
| 보드 | Done **13/16** |

<!-- 보안 헤더는 Caddy(PR #41), Server 헤더도 숨김. 자원 정리는 runbooks/teardown.md. -->

---

## 운영을 지키는 장치

*배포가 끝난 뒤에도 사람 대신 본다*

- 매시간 밖에서 `/health` (uptime 워크플로, 실패하면 알림)
- ledger 백업: 승격·롤백 직후 + 매일
- 백업 **restore drill** 통과 — 건수 · 운영 version · 트리거 일치

<p class="fragment">남은 것: 22번 닫기·정리(#1·#8), 마감·발표(#11)</p>

<!-- uptime PR #42(첫 실행 성공). 복구 훈련: 버킷 최신 덤프 → 임시 DB, 건수·운영 판·트리거 일치(PR #37) — 복원해 보니 API 계정이 없어 권한 줄이 실패하는 것을 찾아 절차에 선생성을 넣었다. -->

---

<!-- _class: dense -->

## 학습·검증은 작업용 계정, 서비스는 최종 서버

*AWS 계정이 둘이다 — 버킷을 함께 쓸 수 없어 같은 Actions run 의 artifact 로 version 을 건넨다*

| 항목 | 작업용 서버 | 최종 서버 |
|---|---|---|
| 주소 | `54-252-22-31.sslip.io` (54.252.22.31) | **`https://nlpwizard.eta.pyhub.kr`** (54.253.32.153) |
| 맡는 일 | 승격 · 롤백 · ledger — 검증의 현장 | 최종 서비스 |
| model version 받는 길 | 버킷 | 같은 Actions run 의 artifact (`model-artifacts`) |
| runner | `paperclf` | `paperclf-final` (label `final`) |
| 상태 | **운영 중** | **운영 중** (v0.1.5 · m20261120-24) |

<!-- runbooks/final-server.md(PR #45·#56). 최종 서버 = 연구자 계정 새 Lightsail 인스턴스, 고정 IP 54.253.32.153. 11-20 bootstrap.sh final → 러너 paperclf-final → FINAL_ENABLED=true → model 실행(promote-final) → v0.1.5 태그 재실행(deploy-final). 첫 promote-final 은 이미지가 없어 실패했고 deploy-final 뒤 정상. 11-20 도메인 nlpwizard.eta.pyhub.kr 을 새 고정 IP 54.253.32.153 으로 바꿈(연구자) → Caddy 가 Let's Encrypt 인증서 자동 발급, https 운영. 시연은 https://nlpwizard.eta.pyhub.kr/health. -->

---

## 스위치 하나 — `FINAL_ENABLED`를 켜면 두 서버에 함께

*최종 서버 job 은 작업용 서버가 통과시킨 version 만 받는다*

```text {2,4}
ci        v* 태그 → test → image → deploy(작업용)
                                  → deploy-final(최종)
model     train → 게이트 → parity → promote(작업용, 버킷)
                                  → promote-final(최종, run artifact)
rollback  rollback(작업용) · rollback-final(최종, 서버에 남은 version 으로)
```

> [!WARNING]
> 강조한 줄은 `vars.FINAL_ENABLED == 'true'` 일 때만 돈다 — 11-20 **켰다**: 태그 하나로 두 서버에 함께 배포

<!-- promote-final 은 needs: [train, promote] — 작업용 서버 승격이 끝난 판만 간다. 끄기: gh variable set FINAL_ENABLED --body false. 출처: PR #45 의 ci.yml · model.yml · rollback.yml. -->

---

<!-- _class: lead -->
# 2. AI 활용

<!-- 절 구분 장. -->

---

<!-- _class: small -->
## 사람이 정하고, AI가 만들고, 증거로 검수한다

*"그냥 딸깍"이 아니라 사람이 계약하고 AI가 만든다*

<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5em">
<div>

### 사람이 주도

- 진행 순서: 조감도 → GitHub → 칸반 → 강의안
- 결정 확정: ADR-005 · 006
- 병합 · 서버 권한 · 비용 드는 자원 승인

</div>
<div>

### AI에게 맡김

- 칸반 · 이슈 16 · 마일스톤 구성
- 교사 라벨 · 학생 모델 · ONNX · API
- 워크플로 ci · model · rollback · uptime

</div>
</div>

<p class="fragment">지침 두 겹: <b>사령관</b>(<code>CLAUDE.md</code>) · <b>부관</b>(<code>AGENTS.md</code>), 위임 지시서 5요소</p>

<!-- 사령관(Claude 메인 세션)이 부관(서브에이전트)을 병렬로 지휘했다. ai-usage/ 9건. -->

---

## AI의 설명이 아니라 증거로 받았다

*산출물(artifact)마다 확인한 방법*

| 산출물 | 확인한 방법 |
|---|---|
| 코드 | pytest 87개 + Actions `ci` |
| 게이트 · parity | 통과·실패를 실행 출력으로 |
| 배포 · 롤백 | 매번 `/health`의 version 번호 일치 |
| ledger | 운영 DB 트리거가 미통과 version 거부 |
| 보호 | 실제 요청으로 401 · 200 · 429 |

<p class="fragment">작업마다 <b>AI 활용 기록</b>(<code>ai-usage/</code>) 한 건 — 9건</p>

<!-- AI 가 실수한 예: sublinear_tf=True 로 ONNX 가 0.0018 어긋남 → parity 로 잡았다. 각 AI 활용 기록의 "연구자 검수" 칸은 발표 전에 연구자가 채운다. -->

---

<!-- _class: lead -->
# 3. 강의 대비 개선점

<!-- 절 구분 장. 시간이 부족하면 증류, 게이트 셋, parity 실사례 세 개만 말한다. -->

---

## 강의 뼈대는 그대로, 검증이 실제로 막게

*데이터 · 게이트 · 서빙 · ledger · 실행 시점*

| 강의 | 내 방식 |
|---|---|
| 합성 데이터 | **실제 논문**, GPU LLM → CPU 학생 증류 |
| 게이트 하한 하나 | 하한 · baseline margin · max drop **셋** |
| Go · Rust 서빙 | Python + ONNX 하나, parity는 **실제 이미지**로 |
| 모델 카드 | PostgreSQL ledger + **트리거**가 규칙 강제 |
| 수동 model 실행 | **PR에서도** 학습·게이트·parity |

<!-- 전체 15개: presentation/03-improvements.md. -->

---

## 운영까지 — 강의에 없던 것

*배포 뒤에도 검증한다*

| 무엇 | 확인 |
|---|---|
| 배포 뒤 `/health`, 실패 시 **자동 복귀** | 깨진 version → 37초 복귀 |
| 백업을 **복원해 보는 훈련** | 건수 · 트리거 일치 |
| 매시간 **uptime monitoring** | uptime 워크플로 |
| HTTPS 위 **토큰 · rate limit · 보안 헤더** | 401 · 200 · 429 |
| 공개 저장소에 **원문 대신 해싱 특징** | 저작권 |

<!-- PR #36(자동 복귀), #37(복구 훈련), #42(감시), #30·#41(보호). -->

---

<!-- _class: lead -->
# 4. AI에게 서비스 제공하기

<!-- 절 구분 장. -->

---

## 같은 예측을 세 겹으로 내놓는다

*REST · MCP · 스킬*

| 방식 | AI가 보는 모습 | 상태 |
|---|---|---|
| REST + OpenAPI | 명세를 읽고 `POST /predict` | ✔ v0.1.0, 보호 v0.1.3 |
| MCP 서버 | 도구 `classify_paper` | ✔ 로컬 stdio + 원격 `POST /mcp`(v0.1.4) |
| 에이전트 스킬 | 언제 쓰나 · 결과 읽기 · 오류 | ✔ `skills/paperclf-classify` |

> [!NOTE]
> `/predict`와 `/mcp`는 같은 보호 뒤에 있다 — 토큰 없으면 **401**, IP당 분당 60 넘으면 **429**

<!-- presentation/04-service-for-ai.md. 원격 MCP 는 v0.1.4(PR #38), 스킬은 PR #39. 토큰은 서버 .env 에만 있다. -->

---

## AI가 믿을 정도를 스스로 판단하게 한다

*응답과 오류의 약속*

- 응답마다 **model version**(`model_version`) · **확률**(`p_include`) · `label`
- MCP는 **임계값**(include ≥ 0.7 · exclude ≤ 0.3)까지 준다
- `uncertain`(0.3~0.7)은 **사람에게 넘긴다**
- 오류는 일정한 형식: JSON-RPC `-32602` · `isError` + `no_model` · REST 401 / 429 / 503

<!-- presentation/04-service-for-ai.md, skills/paperclf-classify/SKILL.md. 이 확률은 교사(LLM) 판정과의 일치를 배운 값이다. -->

---

## 보고서 도우미 LLM — 웹에서 근거 인용 보고서를 쓴다

*KMS 웹 "연구 보고서" 화면 `/research-reports` · 공용 Ollama*

| 역할 | 모델 | 하는 일 |
|---|---|---|
| 보고서 작성 | **qwen3:4b-instruct-2507** (4B · Q4_K_M) | 근거 30편 묶음 요약 → 절마다 문장 + 인용 |
| 근거 찾기 | **bge-m3** (임베딩) | 질문에 맞는 논문을 의미 검색 |
| 참고문헌 | (모델 안 씀) | DB 서지 값만 — LLM이 지어내지 않음 |

<p class="fragment"><b>실제 생성</b>: 볼트에 5편 · 11-21 14:42 보고서 66초 · 인용 <b>27 / 30</b></p>

<!-- 확인(11-23): 웹 /api/llm/status 가 generation_model = qwen3:4b-instruct-2507-q4_K_M, embedding_model = bge-m3 로 응답. 보고서 파일 머리 model 값도 같은 모델. 서비스용 paperclf 학생 모델과 달리 이쪽은 LLM 이 직접 글을 쓴다 — 대신 문장마다 인용을 강제하고 참고문헌은 DB 에서만 가져온다. -->

---

<!-- _class: lead -->
# 정리

<p>검증을 통과한 것만 운영에 들어갔고,<br><b>실제로 돌았다</b></p>
<p class="fragment">코드 변경 → 배포 · 데이터 변경 → 학습·게이트 → 승격 → 롤백</p>
<p class="fragment">감사합니다</p>

<!-- 마무리에서 시연 흐름 한 줄을 다시 읽는다. -->
