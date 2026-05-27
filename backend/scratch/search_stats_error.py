with open('live_debug.log', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    
lines = content.splitlines()
matching_lines = []
for i, line in enumerate(lines):
    if "/merchant/stats" in line or "/merchant/payments" in line:
        matching_lines.append(i)

print(f"Found {len(matching_lines)} matching lines.")
for idx in matching_lines[-30:]:
    print(f"{idx+1}: {lines[idx]}")
    # Print adjacent lines if it was an exception or error
    if idx + 1 < len(lines) and "Exception" in lines[idx+1]:
        print(f"  -> {lines[idx+1]}")
