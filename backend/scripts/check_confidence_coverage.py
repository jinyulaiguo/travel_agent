import os
import re
import sys

# Define identifying terms for data display that MUST have a ConfidenceBadge
DATA_TERMS = [
    r'price', r'cost', r'amount', r'rating', r'score', r'duration', r'opening_hours', r'fee'
]

# Files to ignore (e.g., config, tests, types)
IGNORE_EXTENSIONS = ('.css', '.test.tsx', '.spec.tsx', '.d.ts', '.json')
IGNORE_DIRS = ['node_modules', 'dist', 'build', '.vite']

def check_coverage(frontend_src):
    total_files = 0
    covered_files = 0
    missing_files = []

    for root, dirs, files in os.walk(frontend_src):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file.endswith(IGNORE_EXTENSIONS) or not file.endswith(('.tsx', '.ts')):
                continue
            
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check if file contains data display terms
                has_data = any(re.search(term, content, re.IGNORECASE) for term in DATA_TERMS)
                
                if has_data:
                    total_files += 1
                    # Check if ConfidenceBadge is imported or used
                    if 'ConfidenceBadge' in content:
                        covered_files += 1
                    else:
                        missing_files.append(os.path.relpath(path, frontend_src))

    print(f"Confidence Coverage Report:")
    print(f"---------------------------")
    print(f"Total data-sensitive files: {total_files}")
    print(f"Covered files: {covered_files}")
    
    if total_files > 0:
        coverage = (covered_files / total_files) * 100
        print(f"Coverage: {coverage:.2f}%")
        
        if missing_files:
            print("\nMissing ConfidenceBadge in:")
            for f in missing_files:
                print(f"  - {f}")
            
        if coverage < 100:
            print("\nError: Confidence coverage is below 100%!")
            return False
    else:
        print("No data-sensitive files found.")
        
    return True

if __name__ == "__main__":
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/src'))
    if not check_coverage(frontend_path):
        sys.exit(1)
    sys.exit(0)
