# Solar Grader ☀️

**Upstage Solar LLM**과 **Document Parse**를 활용한 코딩 과제 자동 채점 시스템입니다.

## 🌟 Key Features

1.  **PDF 과제 명세서 자동 분석**: Upstage Document Parse를 통해 과제 설명과 요구사항을 정확하게 추출합니다.
2.  **학생 답안 일괄 처리**: ZIP 파일로 제출된 학생들의 답안을 자동으로 압축 해제하고, 학번 기준으로 분류합니다.
3.  **하이브리드 코드 분석**:
    *   **소스 코드 파일(.py, .java 등)**: 직접 텍스트를 읽어 분석합니다.
    *   **손코딩 이미지/PDF**: Upstage Document Parse(OCR)를 이용해 텍스트로 변환 후 분석합니다.
4.  **AI 조교 채점**: Solar LLM이 과제 명세서, 채점 기준, 학생 코드를 바탕으로 공정한 피드백과 점수를 제공합니다.

## 📂 Project Structure

```text
solar-grader/
├── .env                    # API Keys
├── .gitignore
├── pyproject.toml          # Project metadata & dependencies
├── requirements.txt        # Deployment dependencies
├── app.py                  # Streamlit Application
├── data/
│   ├── assignment.pdf      # Example Assignment
│   ├── criteria.txt        # Example Criteria
│   └── submissions.zip     # Example Submissions
└── src/
    └── solar_grader/
        ├── __init__.py     # Package initialization
        ├── __main__.py     # CLI entry point
        ├── config.py       # Configuration
        ├── parser.py       # Upstage Document Parse wrapper
        ├── grader.py       # Solar LLM wrapper
        └── utils.py        # File handling (ZIP, Student Matching)
```

## 🚀 Quick Start

1. Install dependencies:
    ```bash
    pip install .
    ```

2. Set API Key in `.env`:
    ```text
    UPSTAGE_API_KEY=your_api_key_here
    ```

3. Run Streamlit App:
    ```bash
    streamlit run app.py
    ```

## 🧠 Why Upstage?

- **Solar LLM**: 한국어와 영어 문맥 처리에 탁월하여, 학생들의 주석이나 한글 변수명도 정확하게 이해하고 피드백을 제공할 수 있습니다.
- **Document Parse**: 단순히 글자만 읽는 OCR이 아니라, 문서의 **구조(Layout)**를 이해하므로 과제 명세서의 표나 복잡한 서식도 놓치지 않고 파싱합니다. 손코딩 과제 채점에 필수적입니다.
