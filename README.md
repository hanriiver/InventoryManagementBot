# 바(Bar) 재고관리 카카오톡 봇

바 운영자가 카카오톡으로 재고를 관리하는 챗봇 (Phase 1 MVP).

## 실행

```bash
pip install -r requirements.txt
cp .env.example .env  # DATABASE_URL 등 설정
psql $DATABASE_URL -f migrations.sql
uvicorn app.main:app --reload
```

## 엔드포인트

- `POST /kakao/webhook` — 카카오 i 오픈빌더 웹훅
- `GET/POST/PATCH/DELETE /admin/items` — 품목 관리 API
- `GET /health` — 헬스체크

## 지원 발화

- `재고조회` — 전체 재고 현황
- `부족재고조회` — 부족 재고만 보기
- `마감입력시작` — 즐겨찾기 품목 퀵리플라이로 선택 후 수량 입력
- `잭다니엘 3, 하이볼 12` — 일괄 텍스트 입력으로 마감 처리
- `발주목록` — 부족 재고 기반 발주 목록 생성/조회

## Phase 2

- APScheduler를 이용해 매일 `NOTIFICATION_TIME`에 부족 재고를 카카오 푸시로 알림
- 매주 `WEEKLY_REPORT_DAY`(기본 월요일)에 최근 7일 소비량 기준 주간 리포트 발송
- 푸시 발송은 `KAKAO_CHANNEL_TOKEN`, `KAKAO_PUSH_API_URL`, `ADMIN_USER_ID`가 모두 설정된 경우에만 동작 (미설정 시 조용히 스킵)
