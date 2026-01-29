# Solar Grader

An automated grading system for coding assignments, leveraging Large Language Models and Document AI for analysis.

## Technologies

This project is built using the following technologies:

- **Model**: `solar-pro3`
- **Document Processing**: Upstage Document Parser

To modify configurations such as the model version or API endpoints, edit `src/solar_grader/config.py`.

## Installation

This project uses `uv` for dependency management. To install the required dependencies, run the following command:

```bash
uv sync
```

## Usage

### 1. Configure Environment Variables

Before running the application, you must set the `UPSTAGE_API_KEY` environment variable.

```bash
export UPSTAGE_API_KEY=your_api_key_here
```

### 2. Run the Application

Execute the startup script to launch the application:

```bash
./scripts/run.sh
```

### 3. Workflow

1.  **Upload Assignment Description**: Upload the assignment description file (PDF format).
2.  **Upload Grading Criteria**: Upload a text file containing the grading criteria. For higher quality grading and more detailed feedback, ensure this file contains specific and comprehensive rules.
3.  **Upload Student Submissions**: Upload a ZIP file containing student submissions.
    *   **PDF Submissions**: These will be processed using the Upstage Document Parser before the content is forwarded to the grading model.
    *   **Source Code (.py) Submissions**: These files will be read as raw text and passed directly to the model.
4.  **View Results**: The application will generate a grading table displaying the results for each student.
