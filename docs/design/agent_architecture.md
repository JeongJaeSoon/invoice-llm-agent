# Agent 아키텍처 설계

## 1. 개요

이 문서는 Invoice LLM Agent의 핵심 아키텍처를 설명합니다.

## 2. 디렉토리 구조

```text
src/agent/
├── functions/              # 함수 관련 모듈
│   ├── base.py            # 기본 함수 인터페이스
│   ├── registry.py        # 함수 레지스트리
│   ├── decorators.py      # 함수 데코레이터
│   └── modules/           # 기능별 함수 모듈
│       ├── pdf.py         # PDF 관련 함수
│       ├── document.py    # 문서 처리 함수
│       └── search.py      # 검색 관련 함수
└── core/                  # Agent 코어
    ├── base.py           # Agent 기본 클래스
    ├── types.py          # 타입 정의
    └── exceptions.py     # 예외 클래스
```

## 3. 주요 컴포넌트

### 3.1 AgentFunction (base.py)

- Agent가 사용할 수 있는 함수의 기본 인터페이스
- 모든 Agent 함수는 이 클래스를 상속
- 함수 메타데이터(이름, 설명, 파라미터) 관리
- OpenAI Function Calling 형식 지원

### 3.2 FunctionRegistry (registry.py)

- 사용 가능한 함수들을 관리하는 레지스트리
- 함수 등록 및 조회 기능
- 모듈 자동 로딩 지원
- 함수 메타데이터 관리

### 3.3 함수 데코레이터 (decorators.py)

- 함수를 Agent 함수로 변환하는 데코레이터
- 함수 메타데이터 정의
- OpenAI Function Calling 형식 자동 변환

### 3.4 함수 모듈 (modules/)

- 기능별로 분리된 함수 모듈
- PDF 처리, 문서 관리, 검색 등
- 독립적인 기능 단위로 구성
- 쉬운 확장성 제공

## 4. 워크플로우

1. 초기화
   - FunctionRegistry 생성
   - 모듈에서 함수 자동 로드
   - Agent 초기화

2. 요청 처리
   - 사용자 입력 수신
   - LLM에 함수 목록 전달
   - 함수 실행 결과 처리
   - 응답 반환

## 5. 함수 추가 방법

새로운 함수를 추가하려면:

1. modules/ 디렉토리에 새 모듈 생성
2. @agent_function 데코레이터로 함수 정의
3. 함수 구현
4. 자동으로 레지스트리에 등록

예시:

```python
@agent_function(
    name="process_invoice",
    description="청구서를 처리합니다.",
    parameters={
        "type": "object",
        "properties": {
            "invoice_id": {
                "type": "string",
                "description": "청구서 ID"
            }
        },
        "required": ["invoice_id"]
    }
)
async def process_invoice(invoice_id: str) -> Dict[str, Any]:
    # 함수 구현
    pass
```

## 6. 에러 처리

- 함수 실행 실패 시 예외 처리
- 적절한 에러 메시지 반환
- 재시도 메커니즘 지원

## 7. 확장 계획

- 새로운 기능 모듈 추가
- 성능 모니터링 추가
- 캐싱 메커니즘 도입
- 병렬 처리 지원
