with open('live_debug.log', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for idx in range(max(0, len(lines) - 100), len(lines)):
    print(f"{idx+1}: {lines[idx].strip()}")
