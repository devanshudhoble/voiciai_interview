$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Error "Virtual environment is missing. Follow the setup instructions in README.md first."
}

& ".\.venv\Scripts\python.exe" -m streamlit run app.py
