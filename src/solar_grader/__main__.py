import sys
from .grader import SolarGrader
from .parser import DocumentParser

def main():
    print("==========================================")
    print("   ☀️  Solar Grader CLI Mode ")
    print("==========================================")
    print("Note: This package is optimized for the Streamlit Web Application.")
    print("Please run: streamlit run app.py")
    
    # Simple CLI Test logic could go here
    # e.g., Test parsing a file provided in args
    if len(sys.argv) > 1:
        parser = DocumentParser()
        print(f"\n[Test Parsing] {sys.argv[1]}")
        res = parser.parse_file(sys.argv[1])
        print(res[:500] + "...")

if __name__ == "__main__":
    main()
