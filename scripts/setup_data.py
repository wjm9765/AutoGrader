#!/usr/bin/env -S uv run python
import os
import zipfile
from pathlib import Path

def create_submission_zip():
    # scripts/ 폴더에서 실행하더라도 프로젝트 루트 기준 경로를 잡도록 수정
    base_dir = Path(__file__).resolve().parent.parent
    source_dir = base_dir / "data" / "submissions_pdf"
    output_path = base_dir / "data" / "temp_pdf.zip"
    
    if not source_dir.exists():
        print(f"Error: {source_dir} 폴더가 없습니다.")
        return

    # Create parent directory if not exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                # PDF 처리를 위해 확장자 변경 (.py -> .pdf) 및 폴더 내 모든 파일 포함
                if file.endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    arcname = file
                    zipf.write(file_path, arcname)
                    print(f"Added: {file}")

    print(f"✅ Created {output_path}")

if __name__ == "__main__":
    create_submission_zip()
