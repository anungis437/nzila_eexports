import subprocess
import time
import sys

# Start server in background
print("Starting Django server...")
server = subprocess.Popen(
    [sys.executable, "manage.py", "runserver"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Wait for server to start
time.sleep(3)

# Make request
print("\nMaking request to deals API...")
import requests

try:
    response = requests.get("http://localhost:8000/api/deals/deals/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:1000]}")
except Exception as e:
    print(f"Request error: {e}")

# Check server output
print("\n=== Server Output ===")
for line in iter(server.stdout.readline, ''):
    print(line, end='')
    if "GET /api/deals/deals/" in line:
        # Read a few more lines after the request
        for _ in range(10):
            line = server.stdout.readline()
            if line:
                print(line, end='')
        break

server.terminate()
