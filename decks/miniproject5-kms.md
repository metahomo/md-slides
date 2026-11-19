---
marp: true
paginate: true
---

<!-- _class: lead -->
# 미니 프로젝트 5 — KMS 논문 판정기 클라우드 배포

ML 시스템 클라우드 배포 · 2026-11

<!-- 순서: 1 아키텍처 이유와 Flow(필수) → 2 AI 활용(필수) → 3 강의 대비 개선점(옵션) → 4 AI에게 서비스 제공(옵션). 도메인은 짧게, 기술 선택의 이유에 시간을 쓴다. -->

---

# 발표 순서

1. **아키텍처 설계의 이유와 Flow** (필수)
2. **AI를 어디서 어떻게 활용했나** (필수)
3. 강의 대비 개선점 (옵션)
4. AI에게 서비스 제공하기 (옵션)

과제의 다섯 기능: Lightsail · GitHub CI/CD · 자동 학습과 검증(게이트·parity) · 모델 API 배포 · 롤백

---

# 도메인 한 줄

**논문 제목·초록 → 주제(coaching-leadership)에 맞을 확률 `p(include)`**

- KMS: 논문을 모아 로컬 LLM이 포함/제외를 판정하는 연구용 지식 관리 시스템
- 문제: LLM 판정은 GPU가 필요 → GPU 없는 Lightsail에서는 못 돌린다
- 해법: **LLM을 교사로, CPU에서 도는 작은 모델을 학생으로** (증류)

<!-- 도메인은 이 한 장으로 끝낸다. 근거: reports/2026-11-18-kms-feasibility.md, ADR-005 -->

---

# 전체 구성 — 판은 둘

```text
[코드 판]  코드 PR / v* 태그 → ci.yml: pytest → 이미지 → GHCR → 서버 배포

[모델 판]  KMS DB(읽기 전용) → 교사 LLM 라벨 → 라벨 스냅숏(원문 없음)
           → main에 push → model.yml: 학습 → 게이트·parity
           → 통과: 버킷에 승격 → API 서버 교체   / 실패: 운영 모델 유지

[롤백]     rollback.yml → 이전 버전으로 되돌리기
```

<!-- 강의 03의 "코드 판과 모델 판" 구분을 따랐다. 원본 그림: architecture/overview.md -->

---

# 기술 선택과 이유

| 구성 요소 | 선택 | 이유 |
|---|---|---|
| 학생 모델 | 해싱 글자 n-gram → TF-IDF → 로지스틱 회귀 | CPU만으로 싸고 빠르게 서빙 |
| 서빙 | FastAPI + onnxruntime 컨테이너 1종 | 배포되는 그 이미지로 parity 검사 |
| 학습 위치 | GitHub 호스팅 러너 | 서버는 서빙만, 승격·배포만 서버 러너 |
| 장부 | PostgreSQL + 트리거 | 게이트 미통과 모델의 배포 기록을 DB가 거부 |
| 공개 | 도메인 + HTTPS | 로그인·HTTPS 없는 외부 공개 금지 |

<!-- 출처: ADR-002(PostgreSQL), ADR-003(도메인), ADR-005(모델), ADR-006(게이트). "이유" 칸은 연구자의 말로 다듬어 말한다. -->

---

# 데이터 — 원문 없이 공개 저장소에

- KMS 수집 **867편** (OpenAlex + KCI), 교사 라벨: include 641 · exclude 211 · uncertain 15
- 스냅숏에는 **공개 식별자 · 라벨 · 해싱 특징**만 → 제목·초록은 넣지 않는다
  - 초록 저작권: 공개 저장소에 재배포하지 않는다
  - 해싱 특징은 원문으로 되돌릴 수 없고, 학습은 오프라인으로 재현된다
- 분할은 열쇠 해시 % 5 → 새 데이터가 와도 기존 시험 문항이 바뀌지 않는다

<!-- ADR-005. 대안이었던 "원문 저장"은 저작권, "식별자만 두고 학습 때 API로 다시 받기"는 재현성 때문에 버렸다. -->

---

# 게이트 — 셋 다 넘어야 승격

1. include F1 ≥ **0.80** (하한)
2. F1 ≥ **기준선 + 0.05** — "전부 include"라고 답해도 F1 0.88
3. 운영 모델보다 **0.02 이상 떨어지지 않을 것**

| 모델 | 학습 편수 | 게이트 F1 | 결과 |
|---|---|---|---|
| 전체 데이터 | 674 | **0.9603** | 통과 |
| 데이터 5% | 33 | 0.9021 | **실패** |

<!-- 불균형 데이터(include 79%)라 하한 하나로는 약하다. 하이퍼파라미터 C를 게이트 시험지로 고르면 시험지에 과적합하므로 미리 정한 4를 유지했다. ADR-006 -->

---

# parity — 원본과 서빙 이미지가 같은 답을 하는가

- 원본 sklearn ↔ **실제 서빙 이미지(ONNX)**의 확률 차이 ≤ **1e-5**
- 결과: 최대 차이 **5.4e-7** (게이트 178편), 원문 12편 1.8e-7
- 실제로 잡은 문제: `sublinear_tf=True`면 변환 후 **0.0018** 어긋남 → 끄고 4.4e-9

> 변환기 옵션 하나로 모델이 달라질 수 있다 → 학습 직후와 이미지, 두 곳에서 본다

<!-- float32 입력도 오차가 커서 ONNX 입력을 double로 했다. ADR-005 "확인한 사실" -->

---

# 현재 상태

| 단계 | 상태 |
|---|---|
| 코드 판 (pytest → 이미지 → GHCR → 배포) | ✔ `v0.1.1` 태그 → test·image·deploy |
| 모델 판 (학습·게이트·parity) | ✔ 통과, 5% 데이터·parity 1e-12는 promote 전에 멈춤 |
| 서버 배포 · 버킷 승격 · 롤백 | ✔ 승격 m20261119-7·8, 되돌리기 →7, 다시 →8 |
| 운영 장부 DB | ✔ 미통과 판 m20261119-9의 배포 기록을 트리거가 거부 |

- 작업용 서버 `https://54-252-22-31.sslip.io` · 지금 운영 app v0.1.2 · model m20261119-11
- PR #19 · #20 · #21 병합, 장부 DB PR #26, 릴리스 v0.1.1, 보드 Done 13/16

<!-- 승격·롤백마다 /health model_version 일치. 증거: v0.1.1 https://github.com/metahomo/miniproject5_kms/actions/runs/44513840582 · 승격 →7 https://github.com/metahomo/miniproject5_kms/actions/runs/44514427871 · →8 https://github.com/metahomo/miniproject5_kms/actions/runs/44514698446 · 되돌리기 →7 https://github.com/metahomo/miniproject5_kms/actions/runs/44514983743 · 다시 →8 https://github.com/metahomo/miniproject5_kms/actions/runs/44515052182 · 5% 차단 https://github.com/metahomo/miniproject5_kms/actions/runs/44515846566 · parity 차단 https://github.com/metahomo/miniproject5_kms/actions/runs/44519475156 · 장부 승격 m20261119-11 https://github.com/metahomo/miniproject5_kms/actions/runs/44519470540 · 코드 되돌리기 v0.1.0 https://github.com/metahomo/miniproject5_kms/actions/runs/44453216170. 버킷 paperclf-models-apse2(small_1_0, $1/월), 키 없이 리소스 액세스. Tailscale 등록, SSH 22번 닫기는 마감 직전(아직 열림). -->

---

<!-- _class: lead -->
# 2. AI 활용 방식

"그냥 딸깍"이 아니라, 사람이 계약하고 AI가 만들고 증거로 검수한다

---

# 역할 나누기

| 사람이 주도한 것 | AI에게 맡긴 것 |
|---|---|
| 진행 순서 지시: 조감도 → GitHub → 칸반 → 강의안 | 칸반보드(5열, 이슈 16개) 구성 |
| 결정 확정: ADR-005 · 006 accepted | 교사 라벨 867편, 스냅숏 형식 |
| 병합 · 태그 · 서버 작업 | 학생 모델 · 게이트 · ONNX · 서빙 API |
| 비용 드는 자원(AWS)은 연구자 승인 뒤에만 (버킷 $1/월) | ci · model · rollback 워크플로 |

- 지침 두 겹: **사령관**(`CLAUDE.md`) · **부관**(`AGENTS.md`), 위임 지시서 5요소

<!-- ai-usage/2026-11-19-student-model-pipeline.md. "계약·제약·검수 기준" 칸은 연구자가 자기 말로 채워 말한다. -->

---

# AI 산출물을 어떻게 검수했나

| 산출물 | 확인 방법 |
|---|---|
| 시험 | 로컬 pytest 15개 + GitHub Actions `ci` 통과 |
| 게이트 | 전체 데이터 통과, 5% 데이터 모델 실패를 명령 출력으로 |
| ONNX | 원본과 차이 5.4e-7, 진단 스크립트로 옵션 문제 발견 |
| API | `/health` · `/predict` 응답, parity 스크립트 |
| 저작권 | 스냅숏에 제목·초록 필드가 없음을 출력 형식으로 |
| 배포·롤백 | 승격·되돌리기마다 `/health`의 `model_version` 일치 |
| 장부 | 운영 DB 트리거가 미통과 판 배포 기록을 거부 |

- 모든 작업을 **AI 활용 기록**(`ai-usage/`)에 한 건씩 남겼다 (7건)

---

<!-- _class: lead -->
# 3. 강의 대비 개선점

---

# 강의보다 한 걸음 더

| 강의 | 내 방식 |
|---|---|
| 합성 데이터 | **실제 논문 데이터**, GPU LLM → CPU 학생 증류 |
| 모델 카드 | PostgreSQL 장부 + 트리거로 규칙을 DB가 강제 |
| 게이트 하한 하나 | 하한 · 기준선 여유 · 하락폭 **셋** |
| 수동 실행 model.yml | 모델에 닿는 **PR에서도** 학습·게이트·parity |
| Go · Rust 서빙 | Python + ONNX 한 종류, parity는 **실제 이미지**로 |
| (없음) | 공개 저장소에 **원문 대신 해싱 특징** |

<!-- 전체 12개 목록: presentation/03-improvements.md. 시간이 부족하면 증류, 게이트 셋, parity 실사례 세 개만 말한다. -->

---

<!-- _class: lead -->
# 4. AI에게 서비스 제공하기

---

# 사람 대신 AI가 쓴다면

| 방식 | AI가 보는 모습 | 이 프로젝트에서 |
|---|---|---|
| REST + OpenAPI | 기계가 읽는 명세로 호출 | FastAPI가 명세를 자동으로 만든다 |
| MCP 서버 | 도구 `classify_paper`: 제목·초록 → 확률·라벨·모델 판 | ✔ 로컬 stdio 구현, 웹 API 와 같은 값 (원격 판·인증은 아직, HTTPS는 켜짐) |
| 에이전트 스킬 | 사용법 문서 | 계획 |

**AI 사용자를 위한 설계**: 입·출력 스키마 고정 · 응답에 모델 버전과 확률 · 일정한 오류 형식 · 인증과 사용량 제한

<!-- 근거: presentation/04-service-for-ai.md, api/mcp_server.py, tests/test_mcp.py. 구현된 것은 웹 API 세 경로(/health, /predict, /model)와 로컬 MCP 도구 classify_paper 하나다. 스킬은 계획이다. -->

---

<!-- _class: lead -->
# 정리

GPU 없는 서버에서도 **LLM의 판단을 싸게 서빙**하고,
코드와 모델이 **각자 검증을 거쳐서만** 운영에 들어간다

감사합니다
