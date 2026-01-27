import streamlit as st
import pandas as pd
import os
import shutil
import json
import re
import time  # Import time for Rate Limit handling
from src.solar_grader import SolarGrader, DocumentParser, SubmissionManager, get_logger

# Setup Logger
logger = get_logger()

st.set_page_config(page_title="Solar Grader", page_icon="📝", layout="wide")

st.title("☀️ Solar Grader")
st.markdown("""
**Upstage Solar LLM & Document Parse 기반 자동 채점 시스템**  
이 시스템은 과제 명세서(PDF)와 채점 기준, 그리고 학생들의 코드(ZIP)를 분석하여 AI 조교가 자동으로 채점해줍니다.
""")

# Custom CSS for fixed height scrollable box
st.markdown("""
<style>
.reasoning-box {
    height: 300px;
    overflow-y: auto;
    background-color: #f7f9fa;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #e6e9ef;
    font-family: monospace;
    font-size: 0.9em;
    white-space: pre-wrap;
    line-height: 1.5;
    color: #444;
    word-wrap: break-word; /* Ensure long words don't overflow horizontally */
}
</style>
""", unsafe_allow_html=True)

# Helper to clean JSON
def parse_json_output(text):
    try:
        # Strip markdown code blocks if present
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```", "", text)
        return json.loads(text)
    except json.JSONDecodeError:
        return None

# --- Sidebar: Configuration & Inputs ---
st.sidebar.header("1. 과제 설정")

uploaded_assignment = st.sidebar.file_uploader("📝 과제 명세서 (PDF/문서)", type=["pdf", "txt", "md"])
uploaded_criteria = st.sidebar.file_uploader("📏 채점 기준표 (TXT)", type=["txt"])

st.sidebar.header("2. 학생 답안 제출")
uploaded_zip = st.sidebar.file_uploader("📦 학생 답안 일괄 (ZIP)", type="zip")

if st.sidebar.button("🧹 임시 데이터 정리"):
    if os.path.exists("./data/submissions"):
        shutil.rmtree("./data/submissions")
    if os.path.exists("./data/temp"):
        shutil.rmtree("./data/temp")
    st.sidebar.success("임시 데이터 삭제 완료")

# --- Main Logic ---

if uploaded_assignment and uploaded_criteria and uploaded_zip:
    st.info("모든 파일이 준비되었습니다. 채점을 시작할 수 있습니다.")
    
    if st.button("🚀 채점 시작 (Start Grading)"):
        parser = DocumentParser()
        grader = SolarGrader()
        manager = SubmissionManager()
        
        # 1. Parse Assignment & Criteria
        with st.spinner("📄 과제 명세서 분석 중... (Upstage Document Parse)"):
            # Save uploaded assignment to temp file for path-based parser
            assign_path = f"./data/temp/{uploaded_assignment.name}"
            os.makedirs("./data/temp", exist_ok=True)
            with open(assign_path, "wb") as f:
                f.write(uploaded_assignment.getbuffer())
            
            assignment_text = parser.parse_file(assign_path)
            # st.expander("과제 명세서 내용").write(assignment_text)
            logger.info(f"Assignment Parsed:\n{assignment_text}")

        with st.spinner("📏 채점 기준 로드 중..."):
             criteria_text = uploaded_criteria.read().decode("utf-8")

        # 2. Process Student Submissions
        with st.spinner("📦 학생 답안 압축 해제 및 분류 중..."):
             extract_path = manager.handle_zip_upload(uploaded_zip)
             students_map = manager.process_students(extract_path)
             st.write(f"총 {len(students_map)}명의 학생 데이터를 발견했습니다.")

        # 3. Grading Loop
        results = []
        progress_bar = st.progress(0)
        
        # Limit context for robustness (User asked for 50 context limit assumption, but we loop per student)
        total_students = len(students_map)
        
        for idx, (student_id, info) in enumerate(students_map.items()):
            # 1. Combine all code files for this student
            student_code_full = ""
            for file_path in info['files']:
                # Add delay to prevent Rate Limit Error (Too Many Requests)
                time.sleep(1.0)
                
                file_name = os.path.basename(file_path)
                code_content = parser.parse_file(file_path) # Handles OCR automatically
                student_code_full += f"\n--- File: {file_name} ---\n{code_content}\n"
            
            # 2. Create Prompt
            system_prompt = grader.create_system_prompt(assignment_text, criteria_text)
            
            # 3. Call Solar with Reasoning Visualization
            full_reasoning = ""
            full_content = ""
            
            with st.status(f"🔍 학번 {student_id} 채점 중...", expanded=True) as status:
                st.write("### 🧠 사고 과정 (Thinking...)")
                reasoning_placeholder = st.empty()
                
                # Initial state of reasoning box
                reasoning_placeholder.markdown('<div class="reasoning-box">...</div>', unsafe_allow_html=True)
                
                # Consume the stream
                for chunk in grader.grade_submission(student_code_full, system_prompt):
                    if chunk.get("type") == "error":
                        st.error(chunk["message"])
                        full_content = '{"score": 0, "feedback_summary": "Error Occurred"}'
                        logger.error(f"Error grading {student_id}: {chunk['message']}")
                        break
                        
                    if chunk.get("type") == "reasoning":
                        full_reasoning += chunk["delta"]
                        # Real-time update of reasoning inside fixed box
                        # Escape special HTML chars slightly to prevent breaking layout if needed, 
                        # usually markdown handles it, but inside HTML div we need care if raw text.
                        # For now, simplistic injection.
                        safe_reasoning = full_reasoning.replace("<", "&lt;").replace(">", "&gt;")
                        reasoning_placeholder.markdown(f'<div class="reasoning-box">{safe_reasoning}</div>', unsafe_allow_html=True)
                    
                    if chunk.get("type") == "content":
                        full_content += chunk["delta"]
                        
                status.update(label=f"✅ 학번 {student_id} 완료", state="complete", expanded=False)

            # 4. Post-process result
            logger.info(f"Final Output for {student_id}:\n{full_content}")
            
            # 4. Post-process result
            grade_result = parse_json_output(full_content)
            if not grade_result:
                grade_result = {"score": 0, "feedback_summary": "JSON 파싱 실패 (AI 응답 오류)"}
            
            grade_result['student_id'] = student_id # Ensure ID is correct
            results.append(grade_result)
            
            # Update Progress
            progress_bar.progress((idx + 1) / total_students)

        # 4. Display Results
        st.success("🎉 채점 완료!")
        
        df = pd.DataFrame(results)
        
        # Display simplified table (exclude detailed_feedback)
        display_cols = ['student_id', 'score', 'feedback_summary']
        # Filter only existing columns just in case
        display_cols = [c for c in display_cols if c in df.columns]
        
        st.dataframe(df[display_cols], use_container_width=True)

        # Download full CSV (including details)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 결과 CSV 다운로드",
            csv,
            "grading_results.csv",
            "text/csv",
            key='download-csv'
        )
        
        # Detailed View
        st.subheader("🔍 상세 결과 보기")
        for res in results:
            with st.expander(f"학번: {res.get('student_id')} - 점수: {res.get('score')}점"):
                st.write(f"**총평**: {res.get('feedback_summary')}")
                if 'detailed_feedback' in res:
                    st.json(res['detailed_feedback'])

else:
    st.info("👈 왼쪽 사이드바에서 과제 파일(PDF), 기준표(TXT), 학생 답안(ZIP)을 모두 업로드해주세요.")
