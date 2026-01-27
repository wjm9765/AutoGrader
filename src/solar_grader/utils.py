import zipfile
import os
import re
import shutil

class SubmissionManager:
    def __init__(self, upload_dir="./data/submissions"):
        self.upload_dir = upload_dir
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

    def handle_zip_upload(self, uploaded_file) -> str:
        """
        Saves and extracts the uploaded ZIP file.
        Returns the path to the extracted directory.
        """
        # Clean up old data if needed or create a unique folder per session
        extract_path = os.path.join(self.upload_dir, "extracted")
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        os.makedirs(extract_path)

        zip_path = os.path.join(self.upload_dir, "temp_submissions.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            return extract_path
        except zipfile.BadZipFile:
            return ""

    def process_students(self, root_dir: str) -> dict:
        """
        Organizes files by Student ID.
        Expected formats:
        - 20231234_Name/code.py
        - 20231234.py
        - [Assignment]_20231234_Name.zip
        
        Returns:
        {
            "20231234": {
                "name": "Name (if detected)",
                "files": ["/path/to/extracted/code.py", ...]
            },
            ...
        }
        """
        students = {}
        # Regex for finding 8-digit student ID (most common in Korea)
        id_pattern = re.compile(r"(\d{8})")
        
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.startswith('.') or file.startswith('__MACOSX'):
                    continue
                
                full_path = os.path.join(root, file)
                
                # Check path for Student ID
                match = id_pattern.search(full_path)
                if match:
                    student_id = match.group(1)
                    if student_id not in students:
                        students[student_id] = {"files": [], "name": "Unknown"}
                    
                    students[student_id]["files"].append(full_path)
                    
                    # Try to guess name from filename (simple heuristic)
                    # e.g., 20231234_HongGilDong.py
                    # This is naive but helpful for display
                    pass 
                
        # Sort by student ID
        sorted_students = dict(sorted(students.items()))
        return sorted_students
