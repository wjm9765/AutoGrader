#!/bin/bash

# 스크립트 실행 위치와 관계없이 프로젝트 루트로 이동 (solar-grader 폴더)
cd "$(dirname "$0")/.."

echo "=========================================="
echo "   ☀️  Solar Grader w/ uv"
echo "=========================================="

# uv가 설치되어 있는지 확인
if ! command -v uv &> /dev/null
then
    echo "❌ uv가 설치되어 있지 않습니다. (https://github.com/astral-sh/uv)"
    echo "설치 후 다시 시도해주세요."
    exit 1
fi

echo "🚀 uv를 통해 의존성을 확인하고 앱을 실행합니다..."

# uv run을 사용하여 프로젝트 환경에서 streamlit 실행
uv run streamlit run app.py
