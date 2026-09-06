import subprocess, sys

result = subprocess.run([sys.executable, 'emit.py'], capture_output=True, text=True, encoding="utf-8")
print(result.stdout, end='')
