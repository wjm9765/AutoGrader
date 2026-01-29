import requests
import mimetypes
import os
from .config import Config

class DocumentParser:
    def __init__(self):
        self.api_key = Config.UPSTAGE_API_KEY
        self.url = Config.DOC_PARSE_URL

    def parse_file(self, file_path: str) -> str:
        """
        Routes the file to the appropriate parser based on file type.
        - Images/PDFs: Upstage Document Parse (OCR)
        - Text-based code files: Direct text read
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        
        code_extensions = {
            '.py', '.java', '.c', '.cpp', '.h', '.js', '.ts', '.html', 
            '.css', '.txt', '.md', '.json', '.xml', '.sql', '.sh'
        }

        if ext in code_extensions:
            return self._read_text_file(file_path)
        elif self._is_ocr_candidate(mime_type, ext):
            return self._parse_with_upstage(file_path)
        else:
            return f"[Warning] Unsupported file type: {ext}"

    def _is_ocr_candidate(self, mime_type: str, ext: str) -> bool:
        if ext == '.pdf':
            return True
        if mime_type and mime_type.startswith('image/'):
            return True
        return False

    def _read_text_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback for other encodings if necessary, or return error
            try:
                with open(file_path, 'r', encoding='cp949') as f:
                    return f.read()
            except Exception as e:
                return f"[Error reading text file] {str(e)}"

    def _parse_with_upstage(self, file_path: str) -> str:
        """
        Uses Upstage Document Parse API for OCR and Layout Analysis.
        Returns the content in Markdown format, which is optimal for LLM processing.
        """
        if not self.api_key:
            return "[Error] UPSTAGE_API_KEY is not set."

        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            with open(file_path, "rb") as f:
                files = {"document": f}
                # Official Parameter setting for Document Parse
                # Add ocr=True to force OCR on images within the document
                data = {
                    "model": "document-parse", 
                    "ocr": "true",  # Explicitly enable OCR
                    "base64_encoding": "['table']"
                }
                response = requests.post(self.url, headers=headers, files=files, data=data)
            
            response.raise_for_status()
            result = response.json()
            
            # # --- DEBUG LOGGING ---
            from .logger import get_logger
            #import json
            logger = get_logger()
            # # Log the full response to analyze why content might be empty
            # logger.debug(f"Full Upstage API Response: {json.dumps(result, ensure_ascii=False)}")
            # # ---------------------
            
            markdown_text = ""
            
            if "content" in result and isinstance(result["content"], dict):
                markdown_text = result["content"].get("markdown", "")
                
            if not markdown_text and "content" in result and isinstance(result["content"], dict):
                html_content = result["content"].get("html", "")
                if html_content:
                    logger.warning("Markdown content was empty. Using 'content.html'.")
                    markdown_text = html_content 

            if not markdown_text and "content" in result and isinstance(result["content"], dict):
                logger.warning("Markdown/HTML content was empty. Trying 'content.text'.")
                markdown_text = result["content"].get("text", "")

            if not markdown_text and "elements" in result:
                 logger.warning("Content fields empty. Reconstructing from 'elements'.")
                 for element in result['elements']:
                     # element usually has 'markdown', 'html' or 'content'
                     content_dict = element.get('content', {})
                     if isinstance(content_dict, dict):
                        # Try markdown first, then html, then text
                        val = content_dict.get('markdown') or content_dict.get('html') or content_dict.get('text')
                        if val:
                            markdown_text += val + "\n"
                     elif 'markdown' in element and element['markdown']:
                         markdown_text += element['markdown'] + "\n"
                     elif 'html' in element and element['html']:
                         markdown_text += element['html'] + "\n"
                     elif 'text' in element and element['text']:
                         markdown_text += element['text'] + "\n"

            if markdown_text:
                logger.info(f"Final extracted text length: {len(markdown_text)}")
            else:
                logger.error("Failed to extract any text from the document response.")
                logger.debug(f"Response dump for failure: {result}")

            return markdown_text
            
        except Exception as e:
            return f"[Error parsing document with Upstage] {str(e)}"
