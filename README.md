# 🖥️ NL → Terminal Agent

> Convert natural language into shell commands — powered by LLM + Docker sandbox

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-6.6+-FF6B35?style=flat&logo=gradio&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-required-2496ED?style=flat&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## What is this?

A developer tool that takes what you *want to do* in plain language — Hebrew or English — and turns it into a shell command. Every command runs inside an **isolated Docker container**, so nothing touches your actual machine.

```
"הצג את כל הקבצים הגדולים מ-100MB"
        ↓
find . -size +100M -type f
        ↓
🐳 Runs in Docker sandbox → returns stdout, stderr, exit code
```

---

## Features

- **Natural language → terminal command** via LLM (Llama 3.3 70B on Groq)
- **Bilingual** — detects Hebrew or English automatically, responds in kind
- **Risk classification** — every command is classified before you can run it:

| Level | Color | Meaning |
|-------|-------|---------|
| `SAFE` | 🟢 Green | Read-only, no side effects |
| `WARNING` | 🟡 Yellow | Modifies files, network, packages |
| `DANGER` | 🔴 Red | Irreversible — requires explicit confirmation |
| `ERROR` | ⛔ Blocked | Forbidden — cannot run |

- **DANGER requires checkbox confirmation** before the Run button activates
- **Docker sandbox** — fully isolated, no network, read-only filesystem, limited memory & CPU
- **Editable command** — you can modify the generated command before running
- **Clean dark UI** — built with Gradio + custom CSS

---

## Project Structure

```
my-agent-cli/
├── main.py              # Entry point
├── interface.py         # Gradio UI + handlers
├── llm.py               # LLM client (Groq / OpenAI-compatible)
├── sandbox.py           # Docker execution engine
├── system-prompt/
│   └── prompt-7.md      # System prompt — risk classification rules
├── workdir/             # Mounted into Docker container (read/write)
├── .env                 # API keys (not committed)
├── pyproject.toml
└── uv.lock
```

---

## How It Works

```
User types request
      ↓
llm.py  →  sends to Groq API with system prompt
      ↓
LLM returns:  LEVEL|LANG: command
      e.g.    WARNING|HE: wget https://example.com
      ↓
interface.py parses → updates button color + risk badge
      ↓
User clicks Run (or confirms DANGER)
      ↓
sandbox.py → docker run --rm --network none --read-only ...
      ↓
Returns stdout / stderr / exit code
```

### Sandbox Security Flags

Every command runs with:

```bash
docker run \
  --rm                    # auto-delete container after run
  --network none          # no internet access
  --read-only             # filesystem is read-only
  --cap-drop ALL          # no Linux capabilities
  --pids-limit 64         # prevent fork bombs
  --memory 128m           # max 128MB RAM
  --user 1000:1000        # non-root user
  -v ./workdir:/workspace:rw  # only writable directory
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- [Docker Desktop](https://docs.docker.com/get-docker/) running

### 1. Clone & install

```bash
git clone <your-repo>
cd my-agent-cli
uv sync
```

### 2. Set up environment

Create a `.env` file:

```env
OPENAI_API_KEY=gsk_your_groq_api_key_here
```

> Get a free Groq API key at [console.groq.com](https://console.groq.com)

### 3. Pull the Docker image (first time only)

```bash
docker pull ubuntu:22.04
```

### 4. Run

```bash
uv run main.py
```

Open your browser at **http://127.0.0.1:7860**

---

## Usage Examples

| You type | Command generated | Level |
|----------|-------------------|-------|
| show disk usage | `df -h` | 🟢 SAFE |
| הצג קבצים לפי גודל | `du -ah . \| sort -rh \| head -20` | 🟢 SAFE |
| download google homepage | `wget https://www.google.com` | 🟡 WARNING |
| צור קובץ של 1GB | `dd if=/dev/zero of=bigfile bs=1G count=1` | 🟡 WARNING |
| delete all files in folder | `rm -rf ./*` | 🔴 DANGER |
| turn off the computer | — | ⛔ ERROR |

---

## Prompt Engineering

The system prompt (`system-prompt/prompt-7.md`) defines the classification rules. Key design decisions:

- **Format**: `LEVEL|LANG: command` — single line, machine-parseable
- **Explicit lists** — every command family is explicitly mapped to a level, no guessing
- **Examples table** — few-shot examples in Hebrew and English for each level
- **The `dd` rule** — special-cased because it appears in both WARNING and DANGER depending on the output target
- **Loops rule** — any `while/for/until` that doesn't terminate = WARNING (CPU consumption)
- **`kill/killall/pkill`** — classified as DANGER, not WARNING (irreversible)

To modify behavior, edit `system-prompt/prompt-7.md` — no code changes needed.

---

## Configuration

| Variable | Location | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | `.env` | Groq API key |
| `DOCKER_IMAGE` | `sandbox.py` | Docker image to use (default: `ubuntu:22.04`) |
| `TIMEOUT_SECONDS` | `sandbox.py` | Max execution time (default: 15s) |
| `PROMPT_PATH` | `llm.py` | Path to system prompt file |
| `model` | `llm.py` | LLM model name |

---

## Testing the Sandbox Directly

```bash
uv run python sandbox.py "ls -la"
uv run python sandbox.py "echo hello world"
uv run python sandbox.py "df -h"
```

---

## Roadmap

- [ ] Persistent session — keep files between runs
- [ ] Command history
- [ ] Multi-step agent — chain commands automatically
- [ ] Support for more languages
- [ ] Custom Docker images per user

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| UI | [Gradio](https://gradio.app) 6.6+ |
| LLM | [Groq](https://groq.com) — Llama 3.3 70B |
| Sandbox | Docker (ubuntu:22.04) |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Language | Python 3.12 |

---

> ⚠️ **Disclaimer** — This tool executes real shell commands inside Docker. The sandbox provides strong isolation, but always review generated commands before running them.

---
## 📋 Project Documentation
For the full development log, challenges, and tracking, see my project sheet:
https://docs.google.com/spreadsheets/d/1fPOmp3hTzUoQw0KfYAvKveuq4JYap_DD5vg8WQ9ajjw/edit?gid=0#gid=0
