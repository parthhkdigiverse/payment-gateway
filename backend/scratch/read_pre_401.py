with open('live_debug.log', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for idx in range(54780, min(len(lines), 54830)):
    print(f"{idx+1}: {lines[idx].strip()}")
