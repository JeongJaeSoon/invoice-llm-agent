# Invoice LLM Agent

LLM Agent for invoice processing

## Requirements

- Python 3.12+
- Poetry
- Docker & Docker Compose (선택사항)

## Installation

### Poetry를 사용한 설치

```bash
# 의존성 설치
poetry install

# pre-commit hooks 설치
poetry run pre-commit install
```

### 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env
```

## Development

### Local 개발 서버 실행

```bash
# Poetry를 사용한 실행
poetry run uvicorn src.main:app --reload
```

### Docker를 사용한 실행

#### 단일 컨테이너 실행

```bash
# 이미지 빌드
docker build -t invoice-llm-agent:latest -f deployment/docker/Dockerfile .

# 컨테이너 실행
docker run -p 8000:8000 --env-file .env invoice-llm-agent:latest
```

#### Docker Compose를 사용한 실행

```bash
# 서비스 실행 (백그라운드)
docker compose -f deployment/docker/docker-compose.yml up -d

# 로그 확인
docker compose -f deployment/docker/docker-compose.yml logs -f

# 서비스 중지
docker compose -f deployment/docker/docker-compose.yml down
```

## API 테스트

서버가 실행된 후, 다음 엔드포인트로 헬스체크를 수행할 수 있습니다:

```bash
curl http://localhost:8000/health
```

## 모니터링

### Prometheus 메트릭

Docker Compose로 실행 시 Prometheus가 자동으로 구성됩니다. 다음과 같은 주요 메트릭을 수집하고 모니터링합니다:

#### 접근 방법

- Prometheus UI: <http://localhost:9090>
- 메트릭 엔드포인트: <http://localhost:8000/metrics>

#### 수집되는 주요 메트릭

1. **HTTP 요청 관련**
   - `http_requests_total`: 전체 HTTP 요청 수 (method, endpoint, status별)
   - `http_request_duration_seconds`: 요청 처리 시간 분포

2. **Agent 처리 관련**
   - `agent_processing_duration_seconds`: Agent의 함수별 처리 시간
   - `pdf_processing_total`: PDF 처리 작업 수 및 상태
   - `agent_requests_total`: Agent 요청 수 (요청 타입, 상태별)
   - `agent_concurrent_requests`: 현재 처리 중인 동시 요청 수

3. **LLM 사용량 관련**
   - `llm_token_usage_total`: LLM 토큰 사용량 (모델별, 타입별)
   - `llm_token_cost_total`: LLM 토큰 사용 비용 (USD)

#### 모니터링 대시보드 예시

1. 요청 처리량 확인

    ```promql
    rate(http_requests_total[5m])
    ```

2. 에러율 모니터링

    ```promql
    sum(rate(http_requests_total{status=~"5.."}[5m]))
      /
    sum(rate(http_requests_total[5m]))
    ```

3. 응답 시간 분포

    ```promql
    histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
    ```

4. LLM 토큰 사용량 추적

    ```promql
    # 시간당 토큰 사용량
    rate(llm_token_usage_total[1h])

    # 모델별 비용 추적
    sum(rate(llm_token_cost_total[24h])) by (model)
    ```

5. Agent 성능 모니터링

    ```promql
    # 동시 요청 수 추적
    agent_concurrent_requests

    # 요청 타입별 성공률
    sum(rate(agent_requests_total{status="success"}[5m])) by (request_type)
      /
    sum(rate(agent_requests_total[5m])) by (request_type)
    ```

#### 알림 설정 (Alert Rules)

중요 메트릭에 대한 알림 규칙을 설정할 수 있습니다:

1. 높은 에러율

    ```yaml
    alert: HighErrorRate
    expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.1
    for: 5m
    ```

2. 느린 응답 시간

    ```yaml
    alert: SlowResponses
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    ```

3. 높은 토큰 사용량

    ```yaml
    alert: HighTokenUsage
    expr: rate(llm_token_usage_total[1h]) > 100000
    for: 15m
    ```

4. 비용 한도 초과

    ```yaml
    alert: HighCostAlert
    expr: sum(increase(llm_token_cost_total[24h])) > 50
    for: 1h
    ```

### 메트릭 활용 방법

1. **성능 모니터링**
   - 응답 시간 추적
   - 처리량 모니터링
   - 병목 구간 식별
   - 동시 요청 처리 능력 분석

2. **비용 최적화**
   - 토큰 사용량 추적
   - 모델별 비용 분석
   - 비용 효율성 개선 포인트 식별

3. **문제 해결**
   - 에러 발생 패턴 분석
   - 성능 저하 원인 파악
   - 리소스 사용량 추적

4. **용량 계획**
   - 트래픽 패턴 분석
   - 리소스 사용량 예측
   - 스케일링 결정
   - LLM 사용량 예측

5. **비즈니스 인사이트**
   - 요청 타입별 사용 패턴 분석
   - 성공/실패율 트렌드 파악
   - 비용 대비 효율성 분석

## Development Tools

- **Black**: 코드 포맷팅
- **isort**: import 문 정렬
- **ruff**: 린팅
- **mypy**: 타입 체크
- **pytest**: 테스트

## License

Apache 2.0 License
