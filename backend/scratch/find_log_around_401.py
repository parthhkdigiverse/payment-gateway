with open('live_debug.log', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

segments = content.split("--- REQUEST ")
print(f"Total request segments: {len(segments)}")

for s in segments:
    if "2026-05-19 11:50:" in s:
        # Print request path and status
        lines = s.splitlines()
        print(f"Time: {lines[0]}")
        print(f"  {lines[1]}")
        for l in lines:
            if "status" in l.lower() or "exception" in l.lower() or "auth" in l.lower():
                print(f"  {l}")
