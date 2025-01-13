#!/bin/bash

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Poetry 환경 확인
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetry가 설치되어 있지 않습니다.${NC}"
    exit 1
fi

echo "린트 검사 실행 중..."

# Ruff
echo -e "\n${GREEN}Ruff 실행 중...${NC}"
poetry run ruff check .

# Black
echo -e "\n${GREEN}Black 실행 중...${NC}"
poetry run black --check .

# isort
echo -e "\n${GREEN}isort 실행 중...${NC}"
poetry run isort --check-only .

# mypy
echo -e "\n${GREEN}mypy 실행 중...${NC}"
poetry run mypy src/

echo -e "\n${GREEN}모든 린트 검사가 완료되었습니다.${NC}"
