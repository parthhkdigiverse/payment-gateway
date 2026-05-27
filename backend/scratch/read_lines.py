with open('live_debug.log', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
    
for i in range(54830, min(len(lines), 54865)):
    print(f"{i+1}: {lines[i].strip()}")
