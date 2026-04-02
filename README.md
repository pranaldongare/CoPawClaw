# CoPawClaw — Enterprise Intelligence Platform

A multi-skill enterprise intelligence platform powered by [CoPaw](https://github.com/agentscope-ai/CoPaw) (an open-source Python multi-agent framework). The platform provides 8 AI-powered skills that scan, analyze, and report on technology trends, competitive landscape, patents, regulations, talent markets, and more.

---

## Table of Contents

1. [What Does This Platform Do?](#what-does-this-platform-do)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Setup on Windows](#setup-on-windows)
5. [Setup on Ubuntu](#setup-on-ubuntu)
6. [Getting Your API Keys](#getting-your-api-keys)
7. [Configuration](#configuration)
8. [Running the Platform](#running-the-platform)
9. [Using the Skills](#using-the-skills)
10. [Running via REST API](#running-via-rest-api)
11. [Running via Docker](#running-via-docker)
12. [Running Tests](#running-tests)
13. [Project Structure](#project-structure)
14. [Troubleshooting](#troubleshooting)
15. [FAQ](#faq)

---

## What Does This Platform Do?

CoPawClaw is an AI-powered enterprise intelligence system. You talk to it in plain English (via a terminal, Discord, Slack, or Telegram), and it performs complex research tasks for you using 8 specialized skills:

| # | Skill | What It Does |
|---|-------|-------------|
| 1 | **Tech Sensing** | Scans 5 data sources (RSS, DuckDuckGo, GitHub, arXiv, Hacker News), classifies articles, and generates a Technology Radar report |
| 2 | **PPTX Generation** | Converts any skill's report into a professional PowerPoint presentation |
| 3 | **Competitive Intelligence** | Tracks competitors — news, funding, product launches, strategic moves |
| 4 | **Patent Monitor** | Monitors patent filings using the USPTO API, identifies IP trends |
| 5 | **Regulation Tracker** | Tracks regulatory changes (EU AI Act, GDPR, etc.) across jurisdictions |
| 6 | **Talent Radar** | Monitors hiring trends, executive moves, and skill demand shifts |
| 7 | **Executive Brief** | Synthesizes all skill outputs into a C-suite one-page brief |
| 8 | **Email Digest** | Sends scheduled multi-skill email digests via SMTP |

**Example conversation:**
```
You: "What are the latest AI trends this week?"
Agent: [Runs Tech Sensing pipeline → scans 100+ articles → classifies → generates radar report]
Agent: "Here's your Technology Radar report. Key highlights:
        - GPT-5 moved from Assess to Trial...
        - Agent frameworks are surging..."

You: "Make a presentation from that"
Agent: [Generates a 10-slide PPTX deck]
Agent: "Deck saved to output/deck.pptx"
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  You (the User)                      │
│         Talk in plain English via any channel         │
└──────────────┬──────────────────────────┬────────────┘
               │                          │
      ┌────────▼────────┐       ┌─────────▼─────────┐
      │  CoPaw CLI Chat │       │  Discord / Slack / │
      │  (Terminal)      │       │  Telegram Bot      │
      └────────┬────────┘       └─────────┬─────────┘
               │                          │
      ┌────────▼──────────────────────────▼────────────┐
      │              CoPaw Multi-Agent System            │
      │                                                  │
      │  ┌─────────────┐ ┌───────────┐ ┌────────────┐  │
      │  │  Analyst     │ │  Reporter │ │   Admin    │  │
      │  │  5 skills    │ │  2 skills │ │  1 skill   │  │
      │  └──────┬──────┘ └─────┬─────┘ └─────┬──────┘  │
      └─────────┼──────────────┼──────────────┼─────────┘
                │              │              │
      ┌─────────▼──────────────▼──────────────▼─────────┐
      │         enterprise_skills_lib (Shared Library)    │
      │   LLM Client │ Pydantic Schemas │ Sensing Pipeline│
      └──────────────────────┬───────────────────────────┘
                             │
      ┌──────────────────────▼───────────────────────────┐
      │        FallbackProvider (LLM Fallback Chain)      │
      │   GPU Server → Gemini (6 keys) → OpenAI           │
      └──────────────────────────────────────────────────┘
```

---

## Prerequisites

Before you begin, you need **at least one** of the following LLM backends:

| Backend | Required? | Cost | Notes |
|---------|-----------|------|-------|
| **Google Gemini API** | Recommended | Free tier available | Easiest to start with. Get keys at [aistudio.google.com](https://aistudio.google.com/) |
| **OpenAI API** | Optional | Pay-per-use | Fallback option. Get key at [platform.openai.com](https://platform.openai.com/) |
| **Local GPU Server** | Optional | Free (needs GPU) | vLLM or Ollama on localhost. Needs NVIDIA GPU with 16GB+ VRAM |

**You do NOT need all three.** The system tries them in order (GPU → Gemini → OpenAI) and uses whichever is available.

**Minimum to get started:** Just 1 Google Gemini API key (free).

---

## Setup on Windows

### Step 1: Install Python 3.11 or newer

1. Open your web browser and go to: **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python 3.12.x"** button
3. Run the downloaded installer (e.g., `python-3.12.x-amd64.exe`)
4. **IMPORTANT:** On the first installer screen, check the box that says:
   ```
   ☑ Add python.exe to PATH
   ```
5. Click **"Install Now"**
6. Wait for installation to complete, then click **"Close"**

**Verify it worked:** Open a new Command Prompt (press `Win + R`, type `cmd`, press Enter) and type:
```cmd
python --version
```
You should see something like `Python 3.12.4`. If you see an error, restart your computer and try again.

### Step 2: Install Git

1. Go to: **https://git-scm.com/download/win**
2. The download should start automatically. If not, click **"Click here to download manually"**
3. Run the installer (e.g., `Git-2.45.x-64-bit.exe`)
4. Click **"Next"** through all screens (the defaults are fine)
5. Click **"Install"**, then **"Finish"**

**Verify it worked:**
```cmd
git --version
```
You should see something like `git version 2.45.2.windows.1`.

### Step 3: Download this project

Open Command Prompt and run these commands one at a time:

```cmd
cd %USERPROFILE%\Projects
```

If the `Projects` folder doesn't exist, create it first:
```cmd
mkdir %USERPROFILE%\Projects
cd %USERPROFILE%\Projects
```

Now download the project:
```cmd
git clone https://github.com/pranaldongare/CoPawClaw.git
cd CoPawClaw
```

### Step 4: Create a virtual environment

A virtual environment keeps this project's packages separate from other Python projects on your computer.

```cmd
python -m venv venv
```

Now **activate** the virtual environment:
```cmd
venv\Scripts\activate
```

You should see `(venv)` appear at the beginning of your command prompt line, like this:
```
(venv) C:\Users\YourName\Projects\CoPawClaw>
```

**Important:** Every time you open a new Command Prompt window to work on this project, you need to activate the virtual environment again by running `venv\Scripts\activate` from the project folder.

### Step 5: Install dependencies

```cmd
pip install -e ".[dev]"
```

This will download and install all required packages. It may take 2-5 minutes depending on your internet speed. You'll see a lot of text scrolling — that's normal.

If you see any red error text mentioning `Microsoft Visual C++ 14.0 or greater is required`, you need to install the Visual Studio Build Tools:
1. Go to: **https://visualstudio.microsoft.com/visual-cpp-build-tools/**
2. Download and run the installer
3. Select **"Desktop development with C++"** and click Install
4. After installation, run the `pip install` command again

### Step 6: Set up your API keys

1. Copy the example environment file:
   ```cmd
   copy .env.example .env
   ```

2. Open the `.env` file in Notepad:
   ```cmd
   notepad .env
   ```

3. Fill in your API keys (see [Getting Your API Keys](#getting-your-api-keys) section below). At minimum, fill in:
   ```
   API_KEY_1=your-gemini-api-key-here
   ```

4. Save the file (`Ctrl + S`) and close Notepad.

### Step 7: Set up CoPaw

```cmd
pip install copaw
copaw init
```

This creates a `~/.copaw/` folder with CoPaw's configuration.

Now copy our configuration files into CoPaw's config directory:

```cmd
copy copaw_config\config.json %USERPROFILE%\.copaw\config.json

mkdir %USERPROFILE%\.copaw\.secret\providers\custom 2>nul
copy copaw_config\providers\fallback.json %USERPROFILE%\.copaw\.secret\providers\custom\fallback.json
```

### Step 8: Create data directories

```cmd
mkdir data\sensing_cache data\shared_reports data\schedules
```

### Step 9: Verify installation

```cmd
python -c "from enterprise_skills_lib.config import settings; print('Config loaded OK')"
python -c "from enterprise_skills_lib.llm.output_sanitizer import sanitize_llm_json; print('Sanitizer OK')"
python -c "from enterprise_skills_lib.llm.output_schemas.sensing import TechSensingReport; print('Schemas OK')"
```

If all three print "OK" messages, you're ready to go! Jump to [Running the Platform](#running-the-platform).

---

## Setup on Ubuntu

### Step 1: Update your system

Open a Terminal (`Ctrl + Alt + T`) and run:

```bash
sudo apt update && sudo apt upgrade -y
```

Enter your password when prompted. This updates all existing software on your system.

### Step 2: Install Python 3.11+ and required tools

```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential git curl
```

Verify Python version:
```bash
python3 --version
```

You need **3.11 or newer**. If your version is older (e.g., 3.10), install a newer version:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
```

Then use `python3.12` instead of `python3` in all the commands below.

### Step 3: Download this project

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/pranaldongare/CoPawClaw.git
cd CoPawClaw
```

### Step 4: Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt:
```
(venv) user@ubuntu:~/Projects/CoPawClaw$
```

**Important:** Every time you open a new terminal to work on this project, run `source venv/bin/activate` from the project folder.

### Step 5: Install dependencies

```bash
pip install -e ".[dev]"
```

This will take 2-5 minutes. If you see errors about missing headers, install:
```bash
sudo apt install -y libxml2-dev libxslt1-dev libffi-dev
pip install -e ".[dev]"
```

### Step 6: Set up your API keys

```bash
cp .env.example .env
```

Open the file in a text editor:
```bash
nano .env
```

Fill in your API keys (see [Getting Your API Keys](#getting-your-api-keys) section below). At minimum, fill in:
```
API_KEY_1=your-gemini-api-key-here
```

Save the file:
- Press `Ctrl + O` (that's the letter O, not zero)
- Press `Enter` to confirm
- Press `Ctrl + X` to exit nano

### Step 7: Set up CoPaw

```bash
pip install copaw
copaw init
```

Copy our configuration files:

```bash
cp copaw_config/config.json ~/.copaw/config.json

mkdir -p ~/.copaw/.secret/providers/custom
cp copaw_config/providers/fallback.json ~/.copaw/.secret/providers/custom/fallback.json
```

### Step 8: Create data directories

```bash
mkdir -p data/sensing_cache data/shared_reports data/schedules
```

### Step 9: Verify installation

```bash
python3 -c "from enterprise_skills_lib.config import settings; print('Config loaded OK')"
python3 -c "from enterprise_skills_lib.llm.output_sanitizer import sanitize_llm_json; print('Sanitizer OK')"
python3 -c "from enterprise_skills_lib.llm.output_schemas.sensing import TechSensingReport; print('Schemas OK')"
```

If all three print "OK" messages, you're ready to go!

---

## Getting Your API Keys

You need **at least one** LLM API key. Here's how to get each one:

### Option A: Google Gemini API Key (Recommended — Free Tier)

1. Go to **https://aistudio.google.com/apikey** in your web browser
2. Sign in with your Google account
3. Click **"Create API key"**
4. Select an existing Google Cloud project, or click **"Create API key in new project"**
5. Your API key will appear — it starts with `AIza`
6. Click the **copy** icon to copy it
7. Paste it into your `.env` file as `API_KEY_1=AIzaSy...`

**For better reliability**, create up to 6 keys (each in a different project) and fill in `API_KEY_1` through `API_KEY_6`. The platform rotates through them automatically to avoid rate limits.

**Free tier limits:** ~60 requests per minute, ~1,500 requests per day. More than enough for normal use.

### Option B: OpenAI API Key (Paid)

1. Go to **https://platform.openai.com/api-keys**
2. Sign in or create an account
3. Click **"+ Create new secret key"**
4. Give it a name (e.g., "CoPawClaw") and click **"Create secret key"**
5. **Copy the key immediately** — it starts with `sk-` — you won't be able to see it again
6. Paste it into your `.env` file as `OPENAI_API=sk-...`

**Pricing:** OpenAI charges per token. The default model (`gpt-4o-mini`) costs approximately $0.15 per million input tokens. A typical sensing run uses ~50K tokens ($0.01).

### Option C: GitHub Token (Optional — Increases Rate Limits)

This is optional but recommended. Without it, GitHub API limits you to 60 requests/hour.

1. Go to **https://github.com/settings/tokens**
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name (e.g., "CoPawClaw")
4. Select the **"public_repo"** scope checkbox
5. Click **"Generate token"**
6. Copy the token (starts with `ghp_`)
7. Paste it into your `.env` file as `GITHUB_TOKEN=ghp_...`

### Option D: SMTP Settings (Optional — For Email Digests Only)

Only needed if you want to send email digests. If you use Gmail:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
SMTP_USE_TLS=true
```

**Gmail App Password:** Go to https://myaccount.google.com/apppasswords → Select "Mail" → Select your device → Click "Generate" → Use the 16-character password.

---

## Configuration

### Minimum `.env` Configuration

If you just want to get started quickly, you only need this in your `.env` file:

```env
# Just one Gemini key is enough to start
API_KEY_1=AIzaSyYourGeminiKeyHere

# Leave everything else as default
MAIN_MODEL=gpt-oss-20b
OPENAI_API=
API_KEY_2=
API_KEY_3=
API_KEY_4=
API_KEY_5=
API_KEY_6=
GITHUB_TOKEN=
```

The system will automatically skip GPU (not available) and use Gemini for all LLM calls.

### Feature Switches

You can enable/disable specific features by editing `enterprise_skills_lib/constants.py`:

```python
SWITCHES = {
    "FALLBACK_TO_GEMINI": True,    # Use Gemini as fallback (set False if no Gemini key)
    "FALLBACK_TO_OPENAI": True,    # Use OpenAI as fallback (set False if no OpenAI key)
    "TECH_SENSING": True,          # Enable tech sensing skill
    "COMPETITIVE_INTEL": True,     # Enable competitive intel skill
    "PATENT_MONITOR": True,        # Enable patent monitor skill
    "REGULATION_TRACKER": True,    # Enable regulation tracker skill
    "TALENT_RADAR": True,          # Enable talent radar skill
    "EXECUTIVE_BRIEF": True,       # Enable executive brief skill
    "EMAIL_DIGEST": True,          # Enable email digest skill
    "PPTX_GEN": True,             # Enable PPTX generation skill
}
```

---

## Running the Platform

There are **three ways** to use CoPawClaw. Choose the one that suits you best:

### Method 1: CoPaw Chat (Recommended)

This is the primary way to use the platform. You talk to AI agents in your terminal.

**Windows:**
```cmd
venv\Scripts\activate
copaw chat --agent analyst
```

**Ubuntu:**
```bash
source venv/bin/activate
copaw chat --agent analyst
```

Now type your requests in plain English:

```
> What are the latest AI trends this week?

> Track what OpenAI and Anthropic are doing competitively

> Scan for AI regulation changes in the EU and US

> Give me a talent market report for ML Engineers
```

**Switch agents** by exiting (`Ctrl + C`) and starting a different one:

```bash
copaw chat --agent reporter    # For PPTX and executive briefs
copaw chat --agent admin       # For email digests and scheduling
```

### Method 2: Direct Script Execution

Run skill scripts directly without CoPaw. Useful for automation or scripting.

**Windows:**
```cmd
venv\Scripts\activate

rem Run tech sensing
python skills\tech_sensing\scripts\run_pipeline.py --domain "Generative AI" --lookback-days 7 --user-id myuser

rem Run competitive analysis
python skills\competitive_intel\scripts\run_competitive_analysis.py --companies "OpenAI,Anthropic,Google" --domain "Foundation Models" --user-id myuser

rem Run patent scan
python skills\patent_monitor\scripts\run_patent_scan.py --domain "large language models" --assignees "OpenAI,Google,Microsoft" --user-id myuser

rem Run regulation scan
python skills\regulation_tracker\scripts\run_regulation_scan.py --domains "AI governance,data privacy" --jurisdictions "EU,US,UK" --user-id myuser

rem Run talent scan
python skills\talent_radar\scripts\run_talent_scan.py --roles "ML Engineer,AI Researcher" --companies "OpenAI,Anthropic,Google" --user-id myuser

rem Generate PPTX from a report
python skills\pptx_gen\scripts\skill_to_slides.py --skill tech_sensing --input "data\myuser\sensing\report_abc123.json" --output "output\deck.pptx"

rem Compose executive brief
python skills\executive_brief\scripts\cross_skill_synthesis.py --user-id myuser --domain "Generative AI"
```

**Ubuntu:**
```bash
source venv/bin/activate

# Run tech sensing
python3 skills/tech_sensing/scripts/run_pipeline.py --domain "Generative AI" --lookback-days 7 --user-id myuser

# Run competitive analysis
python3 skills/competitive_intel/scripts/run_competitive_analysis.py --companies "OpenAI,Anthropic,Google" --domain "Foundation Models" --user-id myuser

# Run patent scan
python3 skills/patent_monitor/scripts/run_patent_scan.py --domain "large language models" --assignees "OpenAI,Google,Microsoft" --user-id myuser

# Run regulation scan
python3 skills/regulation_tracker/scripts/run_regulation_scan.py --domains "AI governance,data privacy" --jurisdictions "EU,US,UK" --user-id myuser

# Run talent scan
python3 skills/talent_radar/scripts/run_talent_scan.py --roles "ML Engineer,AI Researcher" --companies "OpenAI,Anthropic,Google" --user-id myuser

# Generate PPTX from a report
python3 skills/pptx_gen/scripts/skill_to_slides.py --skill tech_sensing --input "data/myuser/sensing/report_abc123.json" --output "output/deck.pptx"

# Compose executive brief
python3 skills/executive_brief/scripts/cross_skill_synthesis.py --user-id myuser --domain "Generative AI"
```

### Method 3: REST API

Start the API server and make HTTP requests from any tool (browser, Postman, curl, or your own app).

**Windows:**
```cmd
venv\Scripts\activate
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Ubuntu:**
```bash
source venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API is now running at **http://localhost:8000**. Open http://localhost:8000/docs in your browser to see the interactive API documentation (Swagger UI).

---

## Running via REST API

Once the API server is running (see Method 3 above), you can use these endpoints:

### Health Check

```bash
curl http://localhost:8000/health
```

### Run Tech Sensing

```bash
curl -X POST http://localhost:8000/skills/tech_sensing/run \
  -H "Content-Type: application/json" \
  -d '{"domain": "Generative AI", "lookback_days": 7, "user_id": "myuser"}'
```

Response:
```json
{"tracking_id": "abc123def456", "status": "started"}
```

### Check Status

```bash
curl http://localhost:8000/skills/tech_sensing/status/abc123def456
```

### List Past Reports

```bash
curl "http://localhost:8000/skills/tech_sensing/history?user_id=myuser"
```

### Run Other Skills

```bash
# Competitive Intelligence
curl -X POST http://localhost:8000/skills/competitive_intel/run \
  -H "Content-Type: application/json" \
  -d '{"domain": "AI", "user_id": "myuser", "params": {"companies": ["OpenAI", "Anthropic"]}}'

# Patent Monitor
curl -X POST http://localhost:8000/skills/patent_monitor/run \
  -H "Content-Type: application/json" \
  -d '{"domain": "large language models", "user_id": "myuser"}'

# Regulation Tracker
curl -X POST http://localhost:8000/skills/regulation_tracker/run \
  -H "Content-Type: application/json" \
  -d '{"domain": "AI governance", "user_id": "myuser", "params": {"jurisdictions": ["EU", "US"]}}'

# Talent Radar
curl -X POST http://localhost:8000/skills/talent_radar/run \
  -H "Content-Type: application/json" \
  -d '{"domain": "AI", "user_id": "myuser", "params": {"roles": ["ML Engineer"]}}'
```

### Executive Brief

```bash
curl -X POST http://localhost:8000/brief/compose \
  -H "Content-Type: application/json" \
  -d '{"user_id": "myuser", "domain": "Generative AI"}'
```

### Manage Schedules

```bash
# Create a weekly schedule
curl -X POST http://localhost:8000/schedules \
  -H "Content-Type: application/json" \
  -d '{"user_id": "myuser", "domain": "AI", "frequency": "weekly"}'

# List schedules
curl "http://localhost:8000/schedules?user_id=myuser"

# Delete a schedule
curl -X DELETE http://localhost:8000/schedules/schedule-id-here
```

---

## Running via Docker

Docker packages the entire platform into a container, so you don't need to install Python or any dependencies on your machine.

### Step 1: Install Docker

**Windows:**
1. Go to **https://www.docker.com/products/docker-desktop/**
2. Download and install **Docker Desktop for Windows**
3. Restart your computer when prompted
4. Open Docker Desktop and wait for it to start (you'll see "Docker Desktop is running" in the system tray)

**Ubuntu:**
```bash
# Install Docker
curl -fsSL https://get.docker.com | sudo sh

# Add your user to the docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# Log out and log back in for the group change to take effect
# Or run: newgrp docker

# Verify Docker is running
docker --version
docker compose version
```

### Step 2: Set up your `.env` file

Same as before — copy `.env.example` to `.env` and fill in your API keys.

**Windows:**
```cmd
copy .env.example .env
notepad .env
```

**Ubuntu:**
```bash
cp .env.example .env
nano .env
```

### Step 3: Build and run

**Windows (in Command Prompt or PowerShell):**
```cmd
docker compose up -d --build
```

**Ubuntu:**
```bash
docker compose up -d --build
```

This will:
1. Build the Docker image (takes 3-5 minutes the first time)
2. Start the API server on port 8000

### Step 4: Verify it's running

```bash
curl http://localhost:8000/health
```

Or open **http://localhost:8000/docs** in your browser.

### Step 5: Stop the container

```bash
docker compose down
```

### View logs

```bash
docker compose logs -f app
```

---

## Running Tests

### Run all unit tests

**Windows:**
```cmd
venv\Scripts\activate
pytest tests\unit\ -v
```

**Ubuntu:**
```bash
source venv/bin/activate
pytest tests/unit/ -v
```

### Run integration tests (requires API keys configured)

**Windows:**
```cmd
pytest tests\integration\ -v -m integration
```

**Ubuntu:**
```bash
pytest tests/integration/ -v -m integration
```

### Run all tests with coverage report

**Windows / Ubuntu:**
```bash
pytest tests/ -v --cov=enterprise_skills_lib --cov-report=term-missing
```

---

## Project Structure

```
CoPawClaw/
├── .env.example                    # Template for API keys and settings
├── .gitignore                      # Git ignore rules
├── Dockerfile                      # Docker container build file
├── Makefile                        # Build/run/test shortcuts
├── docker-compose.yml              # Docker multi-service orchestration
├── pyproject.toml                  # Python project metadata and dependencies
├── README.md                       # This file
│
├── enterprise_skills_lib/          # Shared Python library (the brains)
│   ├── config.py                   # Environment variable loading
│   ├── constants.py                # Feature switches, GPU configs
│   ├── copaw_provider.py           # CoPaw <-> invoke_llm() bridge
│   ├── skill_envelope.py           # Cross-skill data envelope
│   ├── llm/
│   │   ├── client.py               # invoke_llm() — LLM fallback chain
│   │   ├── output_sanitizer.py     # JSON repair and sanitization
│   │   ├── output_schemas/         # Pydantic models for all skills
│   │   │   ├── base.py             # LLMOutputBase with Unicode cleaning
│   │   │   ├── sensing.py          # Tech Sensing schemas
│   │   │   ├── competitive.py      # Competitive Intel schemas
│   │   │   ├── patents.py          # Patent Monitor schemas
│   │   │   ├── regulations.py      # Regulation Tracker schemas
│   │   │   ├── talent.py           # Talent Radar schemas
│   │   │   └── executive.py        # Executive Brief schemas
│   │   └── prompts/                # LLM prompt templates per skill
│   └── sensing/                    # Tech Sensing pipeline modules
│       ├── pipeline.py             # 7-stage orchestrator
│       ├── ingest.py               # RSS + DuckDuckGo fetching
│       ├── dedup.py                # URL normalization + fuzzy matching
│       ├── classify.py             # LLM article classification
│       ├── report_generator.py     # 2-phase report generation
│       ├── verifier.py             # Relevance verification
│       ├── signal_score.py         # Source authority scoring
│       ├── movement.py             # Radar ring change detection
│       ├── deep_dive.py            # Focused tech analysis
│       ├── comparison.py           # Report diffing
│       ├── collaboration.py        # Share/vote/comment
│       ├── scheduler.py            # Recurring execution
│       ├── email_digest.py         # SMTP email sending
│       └── sources/                # Data source connectors
│           ├── arxiv_search.py     # arXiv paper search
│           ├── github_trending.py  # GitHub trending repos
│           └── hackernews.py       # Hacker News stories
│
├── skills/                         # CoPaw skill definitions
│   ├── tech_sensing/               # 7 scripts
│   ├── pptx_gen/                   # 4 scripts + engine
│   ├── competitive_intel/          # 2 scripts
│   ├── patent_monitor/             # 2 scripts
│   ├── regulation_tracker/         # 2 scripts
│   ├── talent_radar/               # 2 scripts
│   ├── executive_brief/            # 2 scripts
│   └── email_digest/               # 2 scripts
│
├── api/                            # FastAPI REST API
│   ├── main.py                     # App + 18 endpoints
│   ├── socket_handler.py           # Socket.IO real-time events
│   └── routes/
│       ├── sensing.py              # /skills/tech_sensing/* routes
│       ├── skills.py               # /skills/{name}/* routes
│       └── schedules.py            # /schedules/* routes
│
├── copaw_config/                   # CoPaw configuration templates
│   ├── config.json                 # Agent definitions (Analyst, Reporter, Admin)
│   └── providers/
│       └── fallback.json           # FallbackProvider registration
│
├── tests/                          # Test suite
│   ├── conftest.py                 # Shared fixtures
│   ├── unit/                       # 7 unit test files
│   └── integration/                # Network-dependent tests
│
└── data/                           # Runtime data (gitignored)
    ├── sensing_cache/              # Article classification cache
    ├── shared_reports/             # Collaboration shared reports
    ├── schedules/                  # Schedule definitions
    └── {user_id}/                  # Per-user skill outputs
        ├── sensing/
        ├── competitive/
        ├── patents/
        ├── regulations/
        ├── talent/
        └── briefs/
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'enterprise_skills_lib'"

You forgot to install the project. Run:
```bash
pip install -e .
```

Or your virtual environment is not activated. Run:
- **Windows:** `venv\Scripts\activate`
- **Ubuntu:** `source venv/bin/activate`

### "ModuleNotFoundError: No module named 'copaw'"

Install CoPaw:
```bash
pip install copaw
```

### "All fallback attempts failed (GPU + Gemini + OpenAI)"

This means none of your LLM backends are working. Check:

1. **Gemini keys:** Is `API_KEY_1` set correctly in `.env`? Try creating a new key at https://aistudio.google.com/apikey
2. **OpenAI key:** Is `OPENAI_API` set correctly in `.env`?
3. **Internet connection:** Can you access https://google.com from your machine?

### "SMTP not configured"

This only affects the Email Digest skill. Fill in `SMTP_HOST`, `SMTP_USER`, and `SMTP_PASSWORD` in your `.env` file. If you don't need email, you can ignore this.

### "Permission denied" when running scripts on Ubuntu

Make the scripts executable:
```bash
chmod +x skills/*/scripts/*.py
```

### "python: command not found" on Ubuntu

Use `python3` instead of `python`:
```bash
python3 skills/tech_sensing/scripts/run_pipeline.py --domain "AI"
```

### "pip: command not found"

Try `pip3` instead:
```bash
pip3 install -e ".[dev]"
```

### Docker build fails

Make sure Docker is running:
- **Windows:** Open Docker Desktop from the Start menu
- **Ubuntu:** `sudo systemctl start docker`

### Tests fail with "fixture not found"

Make sure you installed the dev dependencies:
```bash
pip install -e ".[dev]"
```

### "Rate limit exceeded" errors

The Gemini free tier has rate limits. Solutions:
1. Add more API keys (`API_KEY_2` through `API_KEY_6`) — the system rotates through them
2. Wait a minute and try again
3. Reduce `lookback_days` to scan fewer articles

---

## FAQ

**Q: Do I need a GPU?**
No. The system falls back to cloud APIs (Gemini, OpenAI) automatically. A GPU just makes it faster and free to run.

**Q: How much does it cost to run?**
With Gemini free tier: $0. With OpenAI: ~$0.01-0.05 per skill run. With a local GPU: $0 after hardware cost.

**Q: Can I use it without internet?**
Not currently. The skills fetch articles from the web (RSS, DuckDuckGo, arXiv, GitHub, Hacker News) and use cloud LLM APIs. With a local GPU and local data, it could work offline in principle.

**Q: How do I add my own RSS feeds?**
Edit `enterprise_skills_lib/sensing/config.py` and add URLs to `GENERAL_RSS_FEEDS` or `DOMAIN_RSS_FEEDS`.

**Q: Can I change the LLM model?**
Yes. Edit `MAIN_MODEL` in your `.env` file and the corresponding `FALLBACK_GEMINI_MODEL`/`FALLBACK_OPENAI_MODEL` in `enterprise_skills_lib/constants.py`.

**Q: Where are reports saved?**
In the `data/{user_id}/{skill_name}/` folder. Each report is a JSON file named `report_{tracking_id}.json`.

**Q: Can I connect it to Slack/Discord/Telegram?**
Yes! CoPaw has built-in support for 12+ channels. Edit `~/.copaw/config.json` and add your channel tokens. See CoPaw documentation: https://github.com/agentscope-ai/CoPaw

**Q: How do I schedule recurring reports?**
Use the Analyst agent:
```
> Schedule a weekly AI sensing report
```
Or run directly:
```bash
python3 skills/tech_sensing/scripts/manage_schedule.py --action create --domain "AI" --frequency weekly --user-id myuser
```

---

## License

This project is built on [CoPaw](https://github.com/agentscope-ai/CoPaw) (Apache 2.0 License).
