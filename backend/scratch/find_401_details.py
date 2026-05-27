with open('live_debug.log', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    
lines = content.splitlines()
matching = []
for i, line in enumerate(lines):
    if "[AUTH]" in line or "401" in line:
        matching.append(i)

print(f"Found {len(matching)} lines. Showing the last 20 matching segments:")
for idx in matching[-20:]:
    start = max(0, idx - 5)
    end = min(len(lines), idx + 6)
    print("---")
    for j in range(start, end):
        print(f"{j+1}: {lines[j]}")
