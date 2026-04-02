#!/usr/bin/env bash
#
# CoPawClaw Setup Script
# ----------------------
# Automates: venv, pip install, .env, CoPaw init, Ollama model config,
# skill installation, and verification.
#
# Usage:
#   cd /path/to/CoPawClaw
#   bash scripts/setup_copaw.sh [OLLAMA_MODEL]
#
# Examples:
#   bash scripts/setup_copaw.sh                  # uses default: gemma3:12b
#   bash scripts/setup_copaw.sh llama3.1:8b      # use a specific model
#   bash scripts/setup_copaw.sh qwen2.5:32b      # use a specific model
#
# Prerequisites:
#   - Python 3.11+ installed
#   - Ollama installed and running (https://ollama.com)
#   - At least one Ollama model pulled (ollama pull <model>)

set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────
OLLAMA_MODEL="${1:-gemma3:12b}"
OLLAMA_PORT=11434
COPAW_DIR="$HOME/.copaw"
COPAW_SECRET_DIR="$HOME/.copaw.secret"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step()  { echo -e "\n${BLUE}[STEP $1]${NC} $2"; }
print_ok()    { echo -e "  ${GREEN}[OK]${NC} $1"; }
print_warn()  { echo -e "  ${YELLOW}[WARN]${NC} $1"; }
print_fail()  { echo -e "  ${RED}[FAIL]${NC} $1"; }

# ── Pre-flight checks ───────────────────────────────────────────────
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  CoPawClaw Setup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Project directory : $PROJECT_DIR"
echo "Ollama model      : $OLLAMA_MODEL"
echo "CoPaw config dir  : $COPAW_DIR"
echo "CoPaw secret dir  : $COPAW_SECRET_DIR"
echo ""

# Check Python
print_step 0 "Pre-flight checks"

PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    print_fail "Python 3.11+ is required but not found. Install from https://python.org"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    print_fail "Python 3.11+ required, found $PYTHON_VERSION"
    exit 1
fi
print_ok "Python $PYTHON_VERSION found ($PYTHON_CMD)"

# Check Ollama
if ! command -v ollama &>/dev/null; then
    print_fail "Ollama is not installed. Install from https://ollama.com"
    exit 1
fi
OLLAMA_VER=$(ollama --version 2>&1 | head -1)
print_ok "Ollama found ($OLLAMA_VER)"

# Check Ollama server is running
if ! curl -s "http://localhost:${OLLAMA_PORT}/v1/models" &>/dev/null; then
    print_warn "Ollama server not responding on port $OLLAMA_PORT"
    echo "         Attempting to start Ollama..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start ollama 2>/dev/null || ollama serve &>/dev/null &
        sleep 3
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "         On Windows: please start Ollama from the Start menu or system tray"
        echo "         Press Enter once Ollama is running..."
        read -r
    fi
    # Retry
    if ! curl -s "http://localhost:${OLLAMA_PORT}/v1/models" &>/dev/null; then
        print_fail "Ollama server still not responding. Start it manually and re-run this script."
        exit 1
    fi
fi
print_ok "Ollama server is running on port $OLLAMA_PORT"

# Check if the requested model is available
AVAILABLE_MODELS=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}')
if ! echo "$AVAILABLE_MODELS" | grep -q "^${OLLAMA_MODEL}$"; then
    print_warn "Model '$OLLAMA_MODEL' not found locally. Available models:"
    echo "$AVAILABLE_MODELS" | sed 's/^/         /'
    echo ""
    echo -e "  ${YELLOW}Pulling '$OLLAMA_MODEL' now (this may take several minutes)...${NC}"
    ollama pull "$OLLAMA_MODEL"
fi
print_ok "Ollama model '$OLLAMA_MODEL' is available"

# ── Step 1: Create virtual environment ──────────────────────────────
print_step 1 "Creating Python virtual environment"

cd "$PROJECT_DIR"

if [ -d "venv" ]; then
    print_ok "Virtual environment already exists at venv/"
else
    $PYTHON_CMD -m venv venv
    print_ok "Created virtual environment at venv/"
fi

# Activate venv
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    print_fail "Cannot find venv activation script"
    exit 1
fi
print_ok "Virtual environment activated"

# ── Step 2: Install dependencies ────────────────────────────────────
print_step 2 "Installing Python dependencies"

pip install --upgrade pip --quiet 2>/dev/null
pip install -e ".[dev]" 2>&1 | tail -3
print_ok "All dependencies installed"

# ── Step 3: Set up .env file ────────────────────────────────────────
print_step 3 "Configuring .env file"

if [ -f ".env" ]; then
    print_ok ".env file already exists"
    # Update MAIN_MODEL if it doesn't match
    CURRENT_MODEL=$(grep "^MAIN_MODEL=" .env | cut -d= -f2)
    if [ "$CURRENT_MODEL" != "$OLLAMA_MODEL" ]; then
        if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i "s/^MAIN_MODEL=.*/MAIN_MODEL=$OLLAMA_MODEL/" .env
        else
            sed "s/^MAIN_MODEL=.*/MAIN_MODEL=$OLLAMA_MODEL/" .env > .env.tmp && mv .env.tmp .env
        fi
        print_ok "Updated MAIN_MODEL from '$CURRENT_MODEL' to '$OLLAMA_MODEL'"
    fi
else
    cp .env.example .env
    # Set the model name
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i "s/^MAIN_MODEL=.*/MAIN_MODEL=$OLLAMA_MODEL/" .env
    else
        sed "s/^MAIN_MODEL=.*/MAIN_MODEL=$OLLAMA_MODEL/" .env > .env.tmp && mv .env.tmp .env
    fi
    print_ok "Created .env from .env.example with MAIN_MODEL=$OLLAMA_MODEL"
fi

# ── Step 4: Create data directories ────────────────────────────────
print_step 4 "Creating data directories"

mkdir -p data/sensing_cache data/shared_reports data/schedules
print_ok "Data directories created"

# ── Step 5: Initialize CoPaw ────────────────────────────────────────
print_step 5 "Initializing CoPaw"

# CoPaw is installed as a dependency via pyproject.toml (copaw>=1.0.0)
# Verify it's available
if ! command -v copaw &>/dev/null; then
    print_fail "copaw CLI not found. It should have been installed in Step 2."
    print_fail "Try: pip install copaw"
    exit 1
fi
print_ok "CoPaw CLI available ($(copaw --version 2>&1 | head -1))"

# Run copaw init if not already done
# copaw init is interactive, but if ~/.copaw already exists it's a no-op
if [ -d "$COPAW_DIR" ]; then
    print_ok "CoPaw already initialized ($COPAW_DIR exists)"
else
    echo ""
    echo -e "  ${YELLOW}Running 'copaw init'...${NC}"
    echo -e "  ${YELLOW}When prompted:${NC}"
    echo -e "  ${YELLOW}  1. Accept the security warning${NC}"
    echo -e "  ${YELLOW}  2. Select Ollama as the LLM provider${NC}"
    echo -e "  ${YELLOW}  3. Set model to: $OLLAMA_MODEL${NC}"
    echo ""
    copaw init
    print_ok "CoPaw initialized"
fi

# ── Step 6: Configure Ollama as the active LLM ─────────────────────
#
# IMPORTANT: CoPaw stores provider secrets in ~/.copaw.secret/ (note: NOT ~/.copaw/.secret/)
# The active model is stored in ~/.copaw.secret/providers/active_model.json
#
print_step 6 "Setting Ollama as the active LLM provider"

# Ensure the secret providers directory exists
mkdir -p "$COPAW_SECRET_DIR/providers/builtin"
mkdir -p "$COPAW_SECRET_DIR/providers/custom"

# Write active model config — this is what tells CoPaw which LLM to use
cat > "$COPAW_SECRET_DIR/providers/active_model.json" << EOF
{
  "provider_id": "ollama",
  "model": "$OLLAMA_MODEL"
}
EOF
print_ok "Active model set to: ollama / $OLLAMA_MODEL"
print_ok "Config written to: $COPAW_SECRET_DIR/providers/active_model.json"

# Copy the custom FallbackProvider config (used by enterprise_skills_lib)
cp "$PROJECT_DIR/copaw_config/providers/fallback.json" "$COPAW_SECRET_DIR/providers/custom/fallback.json"
print_ok "FallbackProvider config copied to: $COPAW_SECRET_DIR/providers/custom/fallback.json"

# ── Step 7: Install skills into CoPaw ──────────────────────────────
#
# IMPORTANT: Skills must be copied to ~/.copaw/active_skills/ (NOT workspaces/default/skills/)
# On first launch of 'copaw app', CoPaw runs a migration that copies active_skills
# into the default agent's workspace automatically.
#
print_step 7 "Installing CoPawClaw skills into CoPaw"

SKILLS_DIR="$COPAW_DIR/active_skills"
mkdir -p "$SKILLS_DIR"

SKILLS=(
    tech_sensing
    pptx_gen
    competitive_intel
    patent_monitor
    regulation_tracker
    talent_radar
    executive_brief
    email_digest
)

for skill in "${SKILLS[@]}"; do
    if [ -d "$PROJECT_DIR/skills/$skill" ]; then
        cp -r "$PROJECT_DIR/skills/$skill" "$SKILLS_DIR/$skill"
        print_ok "Installed skill: $skill"
    else
        print_warn "Skill directory not found: skills/$skill"
    fi
done

echo ""
echo -e "  ${YELLOW}NOTE: On the first launch of 'copaw app', CoPaw will auto-migrate${NC}"
echo -e "  ${YELLOW}these skills into the default agent workspace. This is normal.${NC}"

# ── Step 8: Verify everything ──────────────────────────────────────
print_step 8 "Verifying installation"

ERRORS=0

# Check enterprise_skills_lib
$PYTHON_CMD -c "from enterprise_skills_lib.config import settings; print('  Config loaded OK')" 2>/dev/null || { print_fail "enterprise_skills_lib.config import failed"; ERRORS=$((ERRORS+1)); }
$PYTHON_CMD -c "from enterprise_skills_lib.llm.output_sanitizer import sanitize_llm_json; print('  Sanitizer OK')" 2>/dev/null || { print_fail "output_sanitizer import failed"; ERRORS=$((ERRORS+1)); }
$PYTHON_CMD -c "from enterprise_skills_lib.llm.output_schemas.sensing import TechSensingReport; print('  Schemas OK')" 2>/dev/null || { print_fail "output_schemas import failed"; ERRORS=$((ERRORS+1)); }

# Check Ollama connectivity
if curl -s "http://localhost:${OLLAMA_PORT}/v1/models" | grep -q "$OLLAMA_MODEL" 2>/dev/null; then
    print_ok "Ollama model '$OLLAMA_MODEL' accessible via API"
else
    print_warn "Ollama API did not return '$OLLAMA_MODEL' — check 'ollama list'"
fi

# Check active model config
if [ -f "$COPAW_SECRET_DIR/providers/active_model.json" ]; then
    ACTIVE=$(cat "$COPAW_SECRET_DIR/providers/active_model.json")
    if echo "$ACTIVE" | grep -q "$OLLAMA_MODEL"; then
        print_ok "CoPaw active model correctly set to $OLLAMA_MODEL"
    else
        print_warn "CoPaw active model does not match $OLLAMA_MODEL"
        echo "         Content: $ACTIVE"
    fi
else
    print_fail "Active model config not found at $COPAW_SECRET_DIR/providers/active_model.json"
    ERRORS=$((ERRORS+1))
fi

# Check skills
SKILL_COUNT=$(ls -d "$SKILLS_DIR"/tech_sensing "$SKILLS_DIR"/competitive_intel "$SKILLS_DIR"/patent_monitor "$SKILLS_DIR"/regulation_tracker "$SKILLS_DIR"/talent_radar "$SKILLS_DIR"/executive_brief "$SKILLS_DIR"/pptx_gen "$SKILLS_DIR"/email_digest 2>/dev/null | wc -l)
print_ok "$SKILL_COUNT/8 CoPawClaw skills installed in $SKILLS_DIR"

# ── Done ─────────────────────────────────────────────────────────────
echo ""
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Setup complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "  To start the CoPaw Web UI:"
    echo ""
    echo "    cd $PROJECT_DIR"
    if [ -f "venv/bin/activate" ]; then
        echo "    source venv/bin/activate"
    else
        echo "    source venv/Scripts/activate"
    fi
    echo "    copaw app --host 127.0.0.1 --port 8088"
    echo ""
    echo "  Then open: http://127.0.0.1:8088"
    echo ""
    echo "  Active LLM  : ollama / $OLLAMA_MODEL (local, no cloud calls)"
    echo "  Skills loaded: 8 enterprise skills + CoPaw built-in skills"
    echo ""
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  Setup completed with $ERRORS error(s)${NC}"
    echo -e "${RED}========================================${NC}"
    echo "  Review the errors above and fix them before launching."
    exit 1
fi
