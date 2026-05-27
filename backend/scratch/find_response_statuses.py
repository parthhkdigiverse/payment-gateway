with open('live_debug.log', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    
segments = content.split("--- REQUEST ")
print(f"Total requests logged: {len(segments)}")

for s in segments[-15:]:
    if "/merchant/stats" in s or "/merchant/payments" in s:
        # Print the first 4 lines and any Exception line
        lines = s.splitlines()
        print("---")
        for line in lines[:6]:
            print(line)
        for line in lines:
            if "Exception" in line or "status" in line or "Status" in line:
                print("  " + line)
