# doctor_run.ps1
# Run from project root: C:\meta-time-agi\
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\doctor_run.ps1

$ErrorActionPreference = "Stop"

function Banner($t) {
  Write-Host ""
  Write-Host ("=" * 85)
  Write-Host $t
  Write-Host ("=" * 85)
}

Banner "META-TIME DOCTOR :: ENV"
Write-Host "CWD        : $PWD"
Write-Host "PowerShell : $($PSVersionTable.PSVersion)"
Write-Host "Python     : " -NoNewline
python -c "import sys; print(sys.executable); print(sys.version.replace('\n',' '))"

Banner "CLEAN :: __pycache__ (project-wide)"
Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory -ErrorAction SilentlyContinue |
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Optional: remove .pyc too
Get-ChildItem -Path . -Filter "*.pyc" -Recurse -File -ErrorAction SilentlyContinue |
  Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "Clean done."

Banner "RUN :: doctor_imports.py (if exists)"
if (Test-Path ".\doctor_imports.py") {
  python .\doctor_imports.py
} else {
  Write-Host "doctor_imports.py not found -> skipping."
  Write-Host "Tip: create it next to demo_sensor_time.py"
}

Banner "RUN :: demo_sensor_time.py"
if (Test-Path ".\demo_sensor_time.py") {
  python .\demo_sensor_time.py
} else {
  throw "demo_sensor_time.py not found in project root."
}

Banner "DONE"
Write-Host "If imports ever fail again, paste the output of doctor_imports.py."

