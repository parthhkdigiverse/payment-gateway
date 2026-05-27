with open('backend.log', 'r', encoding='utf-16', errors='ignore') as f:
    lines = f.readlines()
    for line in lines[-50:]:
        print(line.strip())
