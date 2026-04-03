@echo off
REM ──────────────────────────────────────────────────────────
REM  CoPawClaw Setup Script (Windows)
REM ──────────────────────────────────────────────────────────
REM  Automates: venv, pip install, .env, CoPaw init, Ollama
REM  model config, skill installation, and verification.
REM
REM  Usage:
REM    cd C:\path\to\CoPawClaw
REM    scripts\setup_copaw.bat [OLLAMA_MODEL]
REM
REM  Examples:
REM    scripts\setup_copaw.bat                   -- uses default: gemma3:12b
REM    scripts\setup_copaw.bat llama3.1:8b       -- use a specific model
REM
REM  Prerequisites:
REM    - Python 3.11+ installed and in PATH
REM    - Ollama installed and running (https://ollama.com)
REM    - At least one Ollama model pulled (ollama pull <model>)
REM ──────────────────────────────────────────────────────────

setlocal enabledelayedexpansion

REM ── Configuration ──────────────────────────────────────────
if "%~1"=="" (
    set "OLLAMA_MODEL=gemma3:12b"
) else (
    set "OLLAMA_MODEL=%~1"
)

set "OLLAMA_PORT=11434"
set "COPAW_DIR=%USERPROFILE%\.copaw"
set "COPAW_SECRET_DIR=%USERPROFILE%\.copaw.secret"
set "PROJECT_DIR=%~dp0.."
set "ERRORS=0"

echo.
echo ========================================
echo   CoPawClaw Setup Script (Windows)
echo ========================================
echo.
echo Project directory : %PROJECT_DIR%
echo Ollama model      : %OLLAMA_MODEL%
echo CoPaw config dir  : %COPAW_DIR%
echo CoPaw secret dir  : %COPAW_SECRET_DIR%
echo.

REM ── Pre-flight checks ─────────────────────────────────────
echo [STEP 0] Pre-flight checks

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] Python 3.11+ not found. Install from https://python.org
    echo          Make sure "Add python.exe to PATH" is checked during install.
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo   [OK] Python %PYTHON_VERSION% found

REM Check Ollama
ollama --version >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] Ollama not found. Install from https://ollama.com/download
    exit /b 1
)
echo   [OK] Ollama found

REM Check Ollama server
curl -s "http://localhost:%OLLAMA_PORT%/v1/models" >nul 2>&1
if errorlevel 1 (
    echo   [WARN] Ollama server not responding on port %OLLAMA_PORT%
    echo          Start Ollama from the Start menu or system tray.
    echo          Press any key once Ollama is running...
    pause >nul
    curl -s "http://localhost:%OLLAMA_PORT%/v1/models" >nul 2>&1
    if errorlevel 1 (
        echo   [FAIL] Ollama server still not responding. Start it and re-run.
        exit /b 1
    )
)
echo   [OK] Ollama server is running on port %OLLAMA_PORT%

REM Check if model is available (pull if not)
ollama list 2>nul | findstr /C:"%OLLAMA_MODEL%" >nul 2>&1
if errorlevel 1 (
    echo   [WARN] Model '%OLLAMA_MODEL%' not found locally. Pulling now...
    ollama pull %OLLAMA_MODEL%
    if errorlevel 1 (
        echo   [FAIL] Failed to pull model '%OLLAMA_MODEL%'
        exit /b 1
    )
)
echo   [OK] Ollama model '%OLLAMA_MODEL%' is available

REM ── Step 1: Virtual environment ────────────────────────────
echo.
echo [STEP 1] Creating Python virtual environment

cd /d "%PROJECT_DIR%"

if exist "venv\Scripts\activate.bat" (
    echo   [OK] Virtual environment already exists
) else (
    python -m venv venv
    echo   [OK] Created virtual environment
)

call venv\Scripts\activate.bat
echo   [OK] Virtual environment activated

REM ── Step 2: Install dependencies ───────────────────────────
echo.
echo [STEP 2] Installing Python dependencies (this takes 2-5 minutes)

pip install --upgrade pip --quiet 2>nul
pip install -e ".[dev]" 2>&1 | findstr /C:"Successfully"
if errorlevel 1 (
    echo   [WARN] pip install may have had issues. Check output above.
) else (
    echo   [OK] All dependencies installed
)

REM ── Step 3: Configure .env ─────────────────────────────────
echo.
echo [STEP 3] Configuring .env file

if exist ".env" (
    echo   [OK] .env file already exists
) else (
    copy .env.example .env >nul
    echo   [OK] Created .env from .env.example
)

REM Update MAIN_MODEL in .env
powershell -Command "(Get-Content .env) -replace '^MAIN_MODEL=.*', 'MAIN_MODEL=%OLLAMA_MODEL%' | Set-Content .env"
echo   [OK] Set MAIN_MODEL=%OLLAMA_MODEL% in .env

REM ── Step 4: Create data directories ────────────────────────
echo.
echo [STEP 4] Creating data directories

if not exist "data\sensing_cache" mkdir "data\sensing_cache"
if not exist "data\shared_reports" mkdir "data\shared_reports"
if not exist "data\schedules" mkdir "data\schedules"
echo   [OK] Data directories created

REM ── Step 5: Initialize CoPaw ───────────────────────────────
echo.
echo [STEP 5] Initializing CoPaw

copaw --version >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] copaw CLI not found. Try: pip install copaw
    set /a ERRORS+=1
    goto step6
)
echo   [OK] CoPaw CLI available

if exist "%COPAW_DIR%" (
    echo   [OK] CoPaw already initialized (%COPAW_DIR% exists)
) else (
    echo.
    echo   Running 'copaw init'...
    echo   When prompted:
    echo     1. Accept the security warning
    echo     2. Select Ollama as the LLM provider
    echo     3. Set model to: %OLLAMA_MODEL%
    echo.
    copaw init
    echo   [OK] CoPaw initialized
)

REM ── Step 6: Configure Ollama as active LLM ─────────────────
:step6
echo.
echo [STEP 6] Setting Ollama as the active LLM provider
echo.
echo   IMPORTANT: CoPaw stores secrets in: %COPAW_SECRET_DIR%
echo   (This is NOT the same as %COPAW_DIR%\.secret)

REM Create directories
if not exist "%COPAW_SECRET_DIR%\providers\builtin" mkdir "%COPAW_SECRET_DIR%\providers\builtin"
if not exist "%COPAW_SECRET_DIR%\providers\custom" mkdir "%COPAW_SECRET_DIR%\providers\custom"

REM Write active model config
(
echo {
echo   "provider_id": "ollama",
echo   "model": "%OLLAMA_MODEL%"
echo }
) > "%COPAW_SECRET_DIR%\providers\active_model.json"
echo   [OK] Active model set to: ollama / %OLLAMA_MODEL%
echo   [OK] Written to: %COPAW_SECRET_DIR%\providers\active_model.json

REM Copy FallbackProvider config
copy /Y "%PROJECT_DIR%\copaw_config\providers\fallback.json" "%COPAW_SECRET_DIR%\providers\custom\fallback.json" >nul
echo   [OK] FallbackProvider config copied

REM ── Step 7: Install skills ─────────────────────────────────
echo.
echo [STEP 7] Installing CoPawClaw skills into CoPaw
echo.
echo   IMPORTANT: Skills go in: %COPAW_DIR%\active_skills\
echo   (NOT in workspaces\default\skills\ -- CoPaw migrates them on first launch)

set "SKILLS_DIR=%COPAW_DIR%\active_skills"
if not exist "%SKILLS_DIR%" mkdir "%SKILLS_DIR%"

for %%S in (tech_sensing pptx_gen competitive_intel patent_monitor regulation_tracker talent_radar executive_brief email_digest) do (
    if exist "%PROJECT_DIR%\skills\%%S" (
        xcopy /E /I /Y /Q "%PROJECT_DIR%\skills\%%S" "%SKILLS_DIR%\%%S" >nul 2>&1
        echo   [OK] Installed skill: %%S
    ) else (
        echo   [WARN] Skill directory not found: skills\%%S
    )
)

echo.
echo   NOTE: On first 'copaw app' launch, CoPaw auto-migrates these skills
echo   into the default agent workspace. This is expected behavior.

REM ── Step 8: Verify ─────────────────────────────────────────
echo.
echo [STEP 8] Verifying installation

python -c "from enterprise_skills_lib.config import settings; print('  [OK] Config loaded')" 2>nul
if errorlevel 1 (
    echo   [FAIL] enterprise_skills_lib.config import failed
    set /a ERRORS+=1
)

python -c "from enterprise_skills_lib.llm.output_sanitizer import sanitize_llm_json; print('  [OK] Sanitizer loaded')" 2>nul
if errorlevel 1 (
    echo   [FAIL] output_sanitizer import failed
    set /a ERRORS+=1
)

python -c "from enterprise_skills_lib.llm.output_schemas.sensing import TechSensingReport; print('  [OK] Schemas loaded')" 2>nul
if errorlevel 1 (
    echo   [FAIL] output_schemas import failed
    set /a ERRORS+=1
)

REM Check active model config
if exist "%COPAW_SECRET_DIR%\providers\active_model.json" (
    echo   [OK] CoPaw active model config exists
) else (
    echo   [FAIL] Active model config missing
    set /a ERRORS+=1
)

REM Count installed skills
set "SKILL_COUNT=0"
for %%S in (tech_sensing pptx_gen competitive_intel patent_monitor regulation_tracker talent_radar executive_brief email_digest) do (
    if exist "%SKILLS_DIR%\%%S\SKILL.md" set /a SKILL_COUNT+=1
)
echo   [OK] %SKILL_COUNT%/8 CoPawClaw skills installed

REM ── 8. Patch CoPaw skill injection ─────────────────────────
REM CoPaw registers skills but doesn't inject them into the LLM system prompt.
REM This patch fixes that so the LLM actually sees and can invoke skills.
echo.
echo [8/8] Patching CoPaw skill injection...
python "%PROJECT_DIR%\scripts\patch_copaw_skills.py"
if %ERRORLEVEL% equ 0 (
    echo   [OK] CoPaw skill injection patched
) else (
    echo   [ERROR] Failed to patch CoPaw skill injection
    set /a ERRORS+=1
)

REM ── Done ───────────────────────────────────────────────────
echo.
if %ERRORS% equ 0 (
    echo ========================================
    echo   Setup complete!
    echo ========================================
    echo.
    echo   To start the CoPaw Web UI:
    echo.
    echo     cd %PROJECT_DIR%
    echo     venv\Scripts\activate
    echo     copaw app --host 127.0.0.1 --port 8088
    echo.
    echo   Then open: http://127.0.0.1:8088
    echo.
    echo   Active LLM  : ollama / %OLLAMA_MODEL% (local, no cloud calls)
    echo   Skills loaded: 8 enterprise skills + CoPaw built-in skills
    echo.
) else (
    echo ========================================
    echo   Setup completed with %ERRORS% error(s)
    echo ========================================
    echo   Review the errors above and fix them.
    exit /b 1
)

endlocal
