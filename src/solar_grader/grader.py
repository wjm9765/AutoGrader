from openai import OpenAI
import json
from .config import Config
from .logger import get_logger

logger = get_logger()

class SolarGrader:
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.UPSTAGE_API_KEY,
            base_url=Config.SOLAR_BASE_URL
        )

    def create_system_prompt(self, assignment_text: str, criteria_text: str) -> str:
        return f"""
        You are an expert Teaching Assistant AI. Your task is to grade a student's coding assignment based on the provided Assignment Description and Grading Criteria.

        [Assignment Description]
        {assignment_text}

        [Grading Criteria]
        {criteria_text}

        First, analyze the student's submission carefully.
        
        [IMPORTANT: HANDLING OCR NOISE & FORMATTING ISSUES]
        The "Assignment Description" or "Student Code" provided might be extracted from images/PDFs using OCR.
        This often results in:
        - Loss of indentation and newlines (code appearing as a single line).
        - Minor character recognition errors (e.g., '*' becoming '.', 'i' becoming '1').
        - Disrupted formatting in code blocks (e.g., `for i in range(5) print(i)` all on one line).
        
        DO NOT penalize the student for indentation/syntax errors IF AND ONLY IF the input text looks like it was flattened by OCR.
        Instead, please RECONSTRUCT the logical flow of the code mentally based on keywords (for, if, def, print, etc.) and grade based on the *intended logic*.
        If the logic itself is correct despite the flattened format, give full credit for execution/logic criteria.

        Check if the code meets the requirements and criteria structure (e.g., function names, logic, output format).
        If the code is handwritten (OCR text), be robust against minor typos but check logic strictly.
        
        Please provide the output in the following JSON format ONLY:
        {{
            "student_id": "Detected Student ID if available",
            "score": (Integer between 0 and 100),
            "feedback_summary": "A brief summary of feedback in Korean",
            "detailed_feedback": [
                {{"criterion": "Name of criterion 1", "score": (score for this item), "comment": "Reasoning"}},
                {{"criterion": "Name of criterion 2", "score": (score for this item), "comment": "Reasoning"}}
            ]
        }}
        """

    def grade_submission(self, student_code: str, system_prompt: str):
        """
        Grades a submission and yields the reasoning process and final content.
        Yields: {"type": "reasoning"|"content", "delta": str}
        """
        if not student_code.strip():
            yield {"type": "error", "message": "제출된 코드가 비어있거나 읽을 수 없습니다."}
            return

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"[Student Submission]\n{student_code}"}
        ]
        
        # Log input (Truncate if too long for cleaner logs)
        logger.info(f"Using Model: {Config.MODEL_NAME}")
        logger.debug(f"Input Messages: {json.dumps(messages, ensure_ascii=False)[:1000]}...") 

        try:
            stream = self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=messages,
                reasoning_effort="high", # Enable reasoning (Solar Pro 3 Feature)
                stream=True
                # response_format={"type": "json_object"} # Removed to avoid conflict with reasoning text
            )
            
            for chunk in stream:
                delta = chunk.choices[0].delta
                
                # Check for reasoning (Thought process)
                if hasattr(delta, 'reasoning') and delta.reasoning:
                    yield {"type": "reasoning", "delta": delta.reasoning}
                
                # Check for content (Final Answer)
                if hasattr(delta, 'content') and delta.content:
                    yield {"type": "content", "delta": delta.content}

        except Exception as e:
            yield {"type": "error", "message": f"System Error during grading: {str(e)}"}
