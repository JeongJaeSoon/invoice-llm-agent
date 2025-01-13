#!/bin/bash

# 전체 테스트 실행
function run_all_tests() {
    poetry run pytest tests/ -v
}

# 단위 테스트만 실행
function run_unit_tests() {
    poetry run pytest tests/unit/ -v -m "unit"
}

# 통합 테스트만 실행
function run_integration_tests() {
    poetry run pytest tests/integration/ -v -m "integration"
}

# E2E 테스트만 실행
function run_e2e_tests() {
    poetry run pytest tests/e2e/ -v -m "e2e"
}

# 커버리지 리포트 생성
function run_coverage() {
    poetry run pytest tests/ --cov=src --cov-report=html
}

# 명령행 인자 처리
case "$1" in
    "all")
        run_all_tests
        ;;
    "unit")
        run_unit_tests
        ;;
    "integration")
        run_integration_tests
        ;;
    "e2e")
        run_e2e_tests
        ;;
    "coverage")
        run_coverage
        ;;
    *)
        echo "사용법: $0 {all|unit|integration|e2e|coverage}"
        exit 1
        ;;
esac
