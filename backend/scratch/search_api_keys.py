import os

def search_files(directory, query):
    matches = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.tsx', '.ts', '.js', '.jsx')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if query.lower() in line.lower():
                                matches.append((path, i + 1, line.strip()))
                except Exception as e:
                    pass
    return matches

frontend_dir = r"c:\Users\admin\OneDrive\Desktop\next gateway\frontend\src"
print("Searching for 'Merchant ID':")
for path, line_num, line_content in search_files(frontend_dir, "Merchant ID"):
    print(f"{path}:{line_num}: {line_content}")

print("\nSearching for 'Salt Key':")
for path, line_num, line_content in search_files(frontend_dir, "Salt Key"):
    print(f"{path}:{line_num}: {line_content}")
