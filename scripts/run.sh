#!/bin/bash

cd "$(dirname "$0")/.."

echo "=========================================="
echo "    Solar Grader w/ uv"
echo "=========================================="

if ! command -v uv &> /dev/null
then
    echo "❌ uv가 설치되어 있지 않습니다. (https://github.com/astral-sh/uv)"
    echo "설치 후 다시 시도해주세요."
    exit 1
fi


uv run streamlit run app.py
