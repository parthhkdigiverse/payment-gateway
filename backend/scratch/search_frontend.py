import os

def search_files(directory, queries):
    matches = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.tsx', '.ts', '.js', '.jsx')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        for query in queries:
                            if query.lower() in content:
                                matches.append((path, query))
                except Exception as e:
                    pass
    return matches

frontend_dir = r"c:\Users\admin\OneDrive\Desktop\next gateway\frontend\src"
print("Searching for signup/register keywords:")
for path, query in search_files(frontend_dir, ["register", "signup", "create-admin", "create_admin"]):
    print(f"{path} (found '{query}')")
