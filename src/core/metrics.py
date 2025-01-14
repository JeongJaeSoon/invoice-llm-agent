"""Prometheus 메트릭스 정의"""

from prometheus_client import Counter, Gauge, Histogram

# API 메트릭스
API_REQUESTS = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status"],
)

API_REQUEST_DURATION = Histogram(
    "api_request_duration_seconds",
    "API request duration in seconds",
    ["method", "endpoint"],
)

# LLM 메트릭스
LLM_API_REQUESTS = Counter(
    "llm_api_requests_total",
    "Total number of LLM API requests",
    ["model"],
)

LLM_TOKEN_USAGE = Counter(
    "llm_token_usage_total",
    "Total number of tokens used",
    ["model", "usage_type"],  # prompt or completion
)

LLM_API_LATENCY = Histogram(
    "llm_api_latency_seconds",
    "LLM API request latency in seconds",
    ["model"],
)

LLM_API_ERRORS = Counter(
    "llm_api_errors_total",
    "Total number of LLM API errors",
    ["model", "error_type"],
)

# 함수 실행 메트릭스
FUNCTION_CALLS = Counter(
    "function_calls_total",
    "Total number of function calls",
    ["function_name"],
)

FUNCTION_ERRORS = Counter(
    "function_errors_total",
    "Total number of function errors",
    ["function_name", "error_type"],
)

FUNCTION_DURATION = Histogram(
    "function_duration_seconds",
    "Function execution duration in seconds",
    ["function_name"],
)

# Redis 메트릭스
REDIS_CONNECTIONS = Gauge(
    "redis_connections_total",
    "Total number of Redis connections",
)

# 시스템 메트릭스
MEMORY_USAGE = Gauge(
    "memory_usage_bytes",
    "Memory usage in bytes",
)
