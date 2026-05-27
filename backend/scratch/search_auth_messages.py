with open('live_debug.log', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

lines = content.splitlines()
matching = []
for i, line in enumerate(lines):
    if "[AUTH]" in line or "Authenticated" in line:
        matching.append(i)

print(f"Found {len(matching)} auth log lines. Showing the last 30 matching lines:")
for idx in matching[-30:]:
    print(f"{idx+1}: {lines[idx].strip()}")
