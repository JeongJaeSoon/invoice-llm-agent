# 테스트 가이드

## 테스트 구조

```
tests/
├── conftest.py                      # 공통 fixture 모음
├── unit/                            # 단위 테스트
│   ├── agent/                       # Agent 관련 테스트
│   ├── services/                    # 서비스 관련 테스트
│   └── core/                        # 코어 기능 테스트
├── integration/                     # 통합 테스트
│   └── api/                        # API 엔드포인트 테스트
├── e2e/                            # E2E 테스트
└── helpers/                        # 테스트 헬퍼
```

## 테스트 실행 방법

테스트는 `scripts/test.sh` 스크립트를 통해 실행할 수 있습니다:

```bash
# 전체 테스트 실행
./scripts/test.sh all

# 단위 테스트만 실행
./scripts/test.sh unit

# 통합 테스트만 실행
./scripts/test.sh integration

# E2E 테스트만 실행
./scripts/test.sh e2e

# 커버리지 리포트 생성
./scripts/test.sh coverage
```

## 새로운 테스트 추가 가이드

### 1. 테스트 파일 위치

- 단위 테스트: `tests/unit/` 하위에 적절한 디렉토리 선택
- 통합 테스트: `tests/integration/` 하위에 적절한 디렉토리 선택
- E2E 테스트: `tests/e2e/` 디렉토리

### 2. 테스트 작성 규칙

1. 테스트 함수 이름은 `test_`로 시작
2. 테스트 설명은 docstring으로 작성
3. 테스트는 독립적으로 실행 가능해야 함
4. fixture는 가능한 재사용

예시:
```python
@pytest.mark.asyncio
async def test_something():
    """테스트 설명"""
    # Given: 테스트 준비
    ...

    # When: 테스트 실행
    ...

    # Then: 결과 검증
    ...
```

### 3. Fixture 사용

공통 fixture는 `conftest.py`에 정의되어 있습니다:

- `test_app`: FastAPI 앱 인스턴스
- `async_client`: 비동기 HTTP 클라이언트
- `mock_function`: 테스트용 에이전트 함수
- `mock_llm_service`: LLM 서비스 Mock
- `mock_function_registry`: 함수 레지스트리 Mock

### 4. 헬퍼 함수 사용

테스트 헬퍼는 `tests/helpers/` 디렉토리에 있습니다:

- `assertions.py`: 검증 헬퍼 함수
- `mock_data.py`: Mock 데이터 생성 함수

## 모범 사례

1. **테스트 격리**
   - 각 테스트는 독립적으로 실행 가능해야 함
   - 테스트 간 상태 공유 금지

2. **명확한 테스트 설명**
   - 테스트 함수 이름은 의도를 명확히 표현
   - docstring으로 상세 설명 제공

3. **Given-When-Then 패턴**
   - Given: 테스트 준비
   - When: 테스트 실행
   - Then: 결과 검증

4. **적절한 Mocking**
   - 외부 의존성은 Mock으로 대체
   - Mock은 필요한 최소한으로 사용

5. **에러 케이스 테스트**
   - 정상 케이스뿐만 아니라 에러 케이스도 테스트
   - 경계값 테스트 포함
