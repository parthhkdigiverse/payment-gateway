import os

import os

log_path = "../live_debug.log"
if os.path.exists(log_path):
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            print("Context around matching lines in live_debug.log:")
            for i, line in enumerate(lines):
                if "post http://127.0.0.1:8000/merchant/withdraw" in line.lower():
                    print("="*60)
                    start = max(0, i - 2)
                    end = min(len(lines), i + 15)
                    for idx in range(start, end):
                        print(f"{idx+1}: {lines[idx].strip()}")
                    print("="*60)
    except Exception as e:
        print(f"Error reading log: {e}")
else:
    print("backend.log not found.")
