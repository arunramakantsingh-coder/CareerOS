# Pre-warm WSL to ensure the virtualization stack is ready
wsl.exe --status > $null 2>&1

# Start Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"