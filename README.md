# CoPawClaw — Enterprise Intelligence Platform

A multi-skill enterprise intelligence platform powered by [CoPaw](https://github.com/agentscope-ai/CoPaw) (an open-source Python multi-agent framework). The platform provides 8 AI-powered skills that scan, analyze, and report on technology trends, competitive landscape, patents, regulations, talent markets, and more.

---

## Table of Contents

1. [What Does This Platform Do?](#what-does-this-platform-do)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Setting Up Ollama (Local GPU Server)](#setting-up-ollama-local-gpu-server)
5. [Setup on Windows](#setup-on-windows)
6. [Setup on Ubuntu](#setup-on-ubuntu)
7. [Getting Your API Keys](#getting-your-api-keys)
8. [Configuration](#configuration)
9. [Running the Platform](#running-the-platform)
10. [Using the Web UI (Chatbot Interface)](#using-the-web-ui-chatbot-interface)
11. [Using the Skills](#using-the-skills)
12. [Running via REST API](#running-via-rest-api)
13. [Running via Docker](#running-via-docker)
14. [Running Tests](#running-tests)
15. [Project Structure](#project-structure)
16. [Troubleshooting](#troubleshooting)
17. [FAQ](#faq)

---

## What Does This Platform Do?

CoPawClaw is an AI-powered enterprise intelligence system. You talk to it in plain English — via the **browser-based chatbot UI**, terminal, Discord, Slack, or Telegram — and it performs complex research tasks for you using 8 specialized skills:

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
└───────┬──────────────┬──────────────────┬────────────┘
        │              │                  │
┌───────▼───────┐ ┌────▼────────┐ ┌──────▼──────────┐
│  CoPaw Web UI │ │ CoPaw CLI   │ │ Discord / Slack /│
│  (Browser     │ │ Chat        │ │ Telegram Bot     │
│   Chatbot)    │ │ (Terminal)  │ │                  │
└───────┬───────┘ └────┬────────┘ └──────┬──────────┘
        │              │                  │
┌───────▼──────────────▼──────────────────▼────────────┐
│              CoPaw Multi-Agent System                 │
│                                                       │
│  ┌─────────────┐ ┌───────────┐ ┌────────────┐       │
│  │  Analyst     │ │  Reporter │ │   Admin    │       │
│  │  5 skills    │ │  2 skills │ │  1 skill   │       │
│  └──────┬──────┘ └─────┬─────┘ └─────┬──────┘       │
└─────────┼──────────────┼──────────────┼──────────────┘
          │              │              │
┌─────────▼──────────────▼──────────────▼──────────────┐
│         enterprise_skills_lib (Shared Library)        │
│   LLM Client │ Pydantic Schemas │ Sensing Pipeline    │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│        FallbackProvider (LLM Fallback Chain)          │
│   GPU Server → Gemini (6 keys) → OpenAI               │
└──────────────────────────────────────────────────────┘
```

---

## Prerequisites

This platform is configured for **GPU-only mode** by default — all LLM calls stay on your local machine or your organization's network. No data is sent to external cloud APIs.

| Backend | Required? | Cost | Notes |
|---------|-----------|------|-------|
| **Ollama** (Recommended) | Yes (default) | Free | Easy to install, runs on any machine with a GPU. Supports 100+ open-source models |
| **vLLM** | Alternative to Ollama | Free | Higher throughput for production. Needs NVIDIA GPU with 16GB+ VRAM |
| **Google Gemini API** | Optional | Free tier available | Cloud fallback — disabled by default. Enable if you don't have a GPU |
| **OpenAI API** | Optional | Pay-per-use | Cloud fallback — disabled by default |

**Minimum to get started:** Install Ollama and pull a model (see next section). That's it — no API keys, no cloud accounts, no internet needed for LLM calls.

**Don't have a GPU?** You can re-enable cloud fallbacks (Gemini/OpenAI) in the [Configuration](#configuration) section.

---

## Setting Up Ollama (Local GPU Server)

Ollama is the easiest way to run LLMs locally. It handles downloading models, managing GPU memory, and serving them via an API — all with a single command.

### Install Ollama on Windows

1. Open your web browser and go to: **https://ollama.com/download**
2. Click the **"Download for Windows"** button
3. Run the downloaded installer (`OllamaSetup.exe`)
4. Follow the installer prompts — click **"Next"** through all screens and then **"Install"**
5. When the installation finishes, click **"Finish"**

Ollama will start automatically and you'll see the Ollama icon (a llama) in your system tray (bottom-right corner of your taskbar, near the clock).

**Verify it installed correctly:** Open a new Command Prompt (`Win + R`, type `cmd`, press Enter) and run:

```cmd
ollama --version
```

You should see something like `ollama version 0.6.x`. If you get an error, restart your computer and try again.

### Install Ollama on Ubuntu

Open a Terminal (`Ctrl + Alt + T`) and run:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

This downloads and installs Ollama. When it finishes, verify:

```bash
ollama --version
```

Ollama runs as a system service on Ubuntu. It starts automatically after install. You can check its status:

```bash
systemctl status ollama
```

If it's not running:
```bash
sudo systemctl start ollama
sudo systemctl enable ollama
```

### Pull a Model

Now you need to download a model. This is a one-time download — the model is cached locally.

**For machines with 16GB+ GPU VRAM (recommended):**

```bash
ollama pull llama3.1:70b
```

This downloads a 70-billion parameter model (~40 GB download). It gives the best quality results.

**For machines with 8GB GPU VRAM:**

```bash
ollama pull llama3.1:8b
```

This downloads an 8-billion parameter model (~4.7 GB download). Lighter but still good.

**For machines with 6GB GPU VRAM or CPU-only (no dedicated GPU):**

```bash
ollama pull llama3.2:3b
```

This downloads a 3-billion parameter model (~2 GB download). Fastest, works even without a GPU (will use CPU, but slower).

**Not sure which to pick?** Start with `llama3.1:8b` — it's a good balance of quality and speed, and works on most modern laptops with a dedicated GPU.

You can see which models you have installed:

```bash
ollama list
```

### Verify Ollama Is Running

Run this command to confirm Ollama's API is responding:

**Windows:**
```cmd
curl http://localhost:11434/v1/models
```

**Ubuntu:**
```bash
curl http://localhost:11434/v1/models
```

You should see a JSON response listing your installed models. If you see `Connection refused`, Ollama isn't running — check the system tray (Windows) or run `sudo systemctl start ollama` (Ubuntu).

### Configure CoPawClaw to Use Your Model

After pulling a model, update your `.env` file so `MAIN_MODEL` matches the model name exactly:

```env
# If you pulled llama3.1:70b
MAIN_MODEL=llama3.1:70b

# If you pulled llama3.1:8b
MAIN_MODEL=llama3.1:8b

# If you pulled llama3.2:3b
MAIN_MODEL=llama3.2:3b
```

The model name in `.env` must **exactly match** what `ollama list` shows.

### Ollama Quick Reference

| Command | What It Does |
|---------|-------------|
| `ollama pull <model>` | Download a model |
| `ollama list` | List installed models |
| `ollama rm <model>` | Delete a model to free disk space |
| `ollama run <model>` | Chat with a model directly (for testing) |
| `ollama serve` | Manually start the Ollama server (usually not needed — it auto-starts) |
| `ollama ps` | Show currently loaded/running models |
| `ollama show <model>` | Show model details (size, parameters, etc.) |

### Using vLLM Instead of Ollama (Advanced)

If you need higher throughput for production deployments with multiple concurrent users, use vLLM instead:

```bash
pip install vllm
vllm serve gpt-oss-20b --port 11434 --max-model-len 32768 --gpu-memory-utilization 0.9
```

vLLM serves on the same port (11434) with the same OpenAI-compatible API, so no other changes are needed. Set `MAIN_MODEL` in `.env` to match the model name you pass to vLLM.

### Running Ollama on a Separate GPU Server

If your GPU machine is different from the machine running CoPawClaw (common in organizations):

1. Install Ollama on the GPU machine
2. Configure Ollama to listen on all interfaces:

   **Ubuntu (GPU server):**
   ```bash
   sudo systemctl edit ollama
   ```
   Add these lines:
   ```
   [Service]
   Environment="OLLAMA_HOST=0.0.0.0:11434"
   ```
   Then restart:
   ```bash
   sudo systemctl restart ollama
   ```

   **Windows (GPU server):**
   Set a system environment variable:
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Go to **Advanced** tab → **Environment Variables**
   - Under **System variables**, click **New**
   - Variable name: `OLLAMA_HOST`
   - Variable value: `0.0.0.0:11434`
   - Click OK, then restart Ollama (right-click system tray icon → Quit, then reopen)

3. On the CoPawClaw machine, update `.env` to point to the GPU server's IP:
   ```env
   MAIN_MODEL=llama3.1:70b
   QUERY_URL=http://192.168.1.50:11434
   LOCAL_BASE_URL=http://192.168.1.50
   ```
   Replace `192.168.1.50` with your GPU server's actual IP address.

4. Verify connectivity from the CoPawClaw machine:
   ```bash
   curl http://192.168.1.50:11434/v1/models
   ```

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

### Minimum `.env` Configuration (GPU-Only — Default)

If you have Ollama running with a model pulled, this is all you need:

```env
# Set this to the exact model name from 'ollama list'
MAIN_MODEL=llama3.1:8b
QUERY_URL=http://localhost:11434
LOCAL_BASE_URL=http://localhost
REMOTE_GPU=false

# Cloud keys — leave empty for GPU-only mode (no data leaves your machine)
API_KEY_1=
OPENAI_API=
GITHUB_TOKEN=
```

### `.env` Configuration (Cloud Fallback Mode)

If you don't have a GPU and want to use cloud APIs instead:

```env
MAIN_MODEL=gpt-oss-20b

# Fill in at least one Gemini key (free tier)
API_KEY_1=AIzaSyYourGeminiKeyHere
API_KEY_2=
API_KEY_3=
API_KEY_4=
API_KEY_5=
API_KEY_6=

# Optional OpenAI fallback
OPENAI_API=sk-YourOpenAIKeyHere
GITHUB_TOKEN=ghp_YourGitHubToken
```

Then enable cloud fallbacks in `enterprise_skills_lib/constants.py`:
```python
"FALLBACK_TO_GEMINI": True,
"FALLBACK_TO_OPENAI": True,
```

### Feature Switches

You can enable/disable specific features by editing `enterprise_skills_lib/constants.py`:

```python
SWITCHES = {
    # LLM fallback chain — both False = GPU-only, no remote calls
    "FALLBACK_TO_GEMINI": False,   # Set True to enable Gemini cloud fallback
    "FALLBACK_TO_OPENAI": False,   # Set True to enable OpenAI cloud fallback

    # Skills
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

## Using the Web UI (Chatbot Interface)

CoPaw includes a **built-in browser-based chatbot interface** — a full web app where you type messages and your agents respond in real time, just like ChatGPT or any other chat application. No terminal needed.

### Starting the Web UI

**Windows:**
```cmd
venv\Scripts\activate
copaw app --host 127.0.0.1 --port 8088
```

**Ubuntu:**
```bash
source venv/bin/activate
copaw app --host 127.0.0.1 --port 8088
```

Now open your browser and go to:

```
http://127.0.0.1:8088
```

You'll see the CoPaw chatbot interface with a chat input box at the bottom, a sidebar for managing chat sessions, and your agents ready to respond.

### What You'll See in the Web UI

The web interface has several sections:

- **Chat Area** — The main area where you type messages and see agent responses streamed in real time
- **Session Sidebar** — Create, switch between, rename, and delete chat sessions (conversations are saved automatically)
- **Agent Panel** — View and manage which agents (Analyst, Reporter, Admin) are active
- **Skills Panel** — Enable or disable individual skills from the UI without editing config files
- **Settings Page** — Configure providers, API keys, and other options directly from the browser

### Having a Conversation

Once the Web UI is open, just type your request in plain English. The agent automatically determines which skill to use:

```
You: What are the latest AI trends this week?
Agent: [Runs Tech Sensing pipeline — scanning RSS, GitHub, arXiv, HackerNews, DuckDuckGo...]
Agent: Here's your Technology Radar report. Key highlights:
       - GPT-5 moved from Assess to Trial...
       - Agent frameworks are surging on GitHub...

You: Now track what OpenAI and Anthropic are doing
Agent: [Runs Competitive Intelligence skill...]
Agent: Competitive analysis complete. Key findings:
       - OpenAI launched ...
       - Anthropic raised ...

You: Make a presentation from the sensing report
Agent: [Runs PPTX Generation skill...]
Agent: Deck saved. Download link: output/deck.pptx

You: Give me an executive summary of everything
Agent: [Runs Executive Brief — synthesizes all skill outputs...]
Agent: Executive Brief ready. 3 critical items require attention...
```

**Responses stream in real time** — you see the agent's reply appear word by word as it generates, just like a modern chatbot.

### Chat Sessions

- **Create a new session:** Click the "+" button in the sidebar to start a fresh conversation
- **Switch sessions:** Click any previous session in the sidebar to resume it
- **Rename a session:** Click the edit icon next to a session name
- **Delete a session:** Click the delete icon next to a session (or use batch delete)
- **All sessions are saved automatically** — close the browser and come back later, your conversations are still there (stored in `~/.copaw/chats/`)

### Managing Skills from the Web UI

You don't need to edit config files to enable/disable skills. From the Web UI:

1. Navigate to the **Skills** panel
2. You'll see all 8 skills listed with toggle switches
3. Click a toggle to enable or disable a skill
4. Changes take effect immediately — no restart needed

You can also:
- **Install new skills** from the CoPaw Skill Hub (if available)
- **Create custom skills** directly from the UI
- **View skill details** — description, required parameters, and scripts

### Configuring Providers from the Web UI

Instead of editing `.env` files manually, you can configure LLM providers in the browser:

1. Go to the **Settings** page
2. Navigate to **Providers**
3. Add or update your API keys (Gemini, OpenAI, etc.)
4. Changes are saved and applied without restarting the server

### Accessing the Web UI from Another Device

To access the Web UI from another computer or phone on the same network:

**Windows:**
```cmd
copaw app --host 0.0.0.0 --port 8088
```

**Ubuntu:**
```bash
copaw app --host 0.0.0.0 --port 8088
```

Then on the other device, open a browser and go to:
```
http://<your-computer-ip>:8088
```

To find your computer's IP address:
- **Windows:** Open Command Prompt and run `ipconfig` — look for "IPv4 Address" (e.g., `192.168.1.100`)
- **Ubuntu:** Run `hostname -I` (e.g., `192.168.1.100`)

So the URL would be something like: `http://192.168.1.100:8088`

### Web UI vs CLI vs REST API — Which to Use?

| Method | Best For | How |
|--------|----------|-----|
| **Web UI** (Recommended) | Day-to-day use, non-technical users, visual chat experience | `copaw app` → open browser |
| **CLI Chat** | Quick terminal use, developers who prefer the command line | `copaw chat --agent analyst` |
| **REST API** | Building your own app, automation, programmatic access | `uvicorn api.main:app` → HTTP calls |
| **Direct Scripts** | One-off runs, CI/CD pipelines, cron jobs | `python skills/.../script.py` |

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

### "GPU-only mode: all attempts against local GPU server failed"

This means Ollama (or vLLM) is not reachable. Check:

1. **Is Ollama running?**
   - **Windows:** Look for the llama icon in your system tray. If not there, search for "Ollama" in the Start menu and open it
   - **Ubuntu:** Run `sudo systemctl start ollama`
2. **Is a model loaded?** Run `ollama list` — you need at least one model pulled
3. **Does `MAIN_MODEL` in `.env` match?** The model name must exactly match what `ollama list` shows (e.g., `llama3.1:8b`, not `llama3.1`)
4. **Is the port correct?** Run `curl http://localhost:11434/v1/models` — you should get a JSON response
5. **Is another process using port 11434?**
   - **Windows:** `netstat -ano | findstr :11434`
   - **Ubuntu:** `lsof -i :11434`

### "All fallback attempts failed (GPU + Gemini + OpenAI)"

This means no LLM backend is working. In GPU-only mode (default), check the Ollama troubleshooting above. If you've enabled cloud fallbacks, also check:

1. **Gemini keys:** Is `API_KEY_1` set correctly in `.env`?
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

### Web UI shows a blank page or won't load

1. Make sure the server is running — you should see log output in the terminal where you ran `copaw app`
2. Check the URL: it should be `http://127.0.0.1:8088` (not `https://`)
3. Try a hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
4. Check if another process is using port 8088:
   - **Windows:** `netstat -ano | findstr :8088`
   - **Ubuntu:** `lsof -i :8088`
5. Try a different port: `copaw app --port 9090` then open `http://127.0.0.1:9090`

### "Rate limit exceeded" errors

The Gemini free tier has rate limits. Solutions:
1. Add more API keys (`API_KEY_2` through `API_KEY_6`) — the system rotates through them
2. Wait a minute and try again
3. Reduce `lookback_days` to scan fewer articles

---

## FAQ

**Q: Do I need a GPU?**
Recommended but not required. By default, the platform runs in GPU-only mode using Ollama. If you don't have a GPU, you can either: (a) use Ollama in CPU mode (slower but works), or (b) re-enable cloud fallbacks (Gemini/OpenAI) in `constants.py`.

**Q: How much does it cost to run?**
With Ollama (local GPU or CPU): $0. With Gemini free tier: $0. With OpenAI: ~$0.01-0.05 per skill run.

**Q: Can I use it without internet?**
The LLM calls are fully local by default (Ollama). However, the skills themselves fetch articles from the web (RSS, DuckDuckGo, arXiv, GitHub, Hacker News), so internet is needed for data ingestion. If you provide your own data files, the LLM analysis can run fully air-gapped.

**Q: Which Ollama model should I use?**
- `llama3.1:70b` — Best quality, needs 16GB+ VRAM
- `llama3.1:8b` — Good balance, needs 8GB VRAM (recommended starting point)
- `llama3.2:3b` — Fastest, works on CPU, lower quality
- `qwen2.5:32b` — Great for structured JSON output, needs 16GB+ VRAM

**Q: How do I add my own RSS feeds?**
Edit `enterprise_skills_lib/sensing/config.py` and add URLs to `GENERAL_RSS_FEEDS` or `DOMAIN_RSS_FEEDS`.

**Q: Can I change the LLM model?**
Yes. Pull a new model with `ollama pull <model-name>`, then update `MAIN_MODEL` in your `.env` file to match. Run `ollama list` to see available model names.

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
