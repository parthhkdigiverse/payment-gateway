import sys
import py_compile

try:
    py_compile.compile(r"c:\Users\admin\OneDrive\Desktop\next gateway\backend\main.py", doraise=True)
    print("Syntax OK")
except Exception as e:
    print(f"Syntax Error: {e}")
