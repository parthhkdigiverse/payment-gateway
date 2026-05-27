with open('live_debug.log', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    
# Print the last 1000 characters containing traceback or error
lines = content.splitlines()
matching_lines = []
for i, line in enumerate(lines):
    if "Traceback" in line or "500 Internal Server Error" in line or "ERROR" in line or "Exception" in line:
        matching_lines.append(i)

if matching_lines:
    print(f"Found {len(matching_lines)} matching lines. Showing the last matching segment:")
    last_idx = matching_lines[-1]
    start_idx = max(0, last_idx - 15)
    end_idx = min(len(lines), last_idx + 15)
    for j in range(start_idx, end_idx):
        print(f"{j+1}: {lines[j]}")
else:
    print("No tracebacks found in live_debug.log")
