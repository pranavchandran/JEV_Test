# JEV Smart Coding Router

A simple experimental coding router that uses **JEV** to decide which coding agent should handle a task.

Instead of sending every coding request to an expensive model, JEV first evaluates the task and decides whether it should go to:

- a **free coding model**
- **Codex** for harder software engineering tasks

The selected coding agent then works directly inside the project folder and creates or edits real files.

## How It Works

```text
Your Coding Task
       ↓
      JEV
       ↓
Model Decision
       ↓
┌───────────────────┐
│                   │
↓                   ↓
Free Model         Codex
Simple Tasks       Complex Tasks
│                   │
└─────────┬─────────┘
          ↓
   Edit Project Files
```

JEV itself does **not write the code**. Its job is to analyze the task and make a routing decision.

## Project Structure

```text
jev-smart-coding-router/
│
├── jev_router.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── demo_project/
    └── .gitkeep
```

The selected coding agent works inside:

```text
demo_project/
```

and creates or modifies files there.

## Requirements

- Python 3.10+
- BeatAPI account/API key
- Codex CLI
- Claude Code CLI or another compatible free model
- Windows PowerShell for the commands below

Install the Python dependency:

```powershell
pip install requests
```

Or:

```powershell
pip install -r requirements.txt
```

`requirements.txt`:

```text
requests
```

## BeatAPI / JEV Setup

Create a BeatAPI API key, then set it in PowerShell:

```powershell
$env:BEATAPI_API_KEY="YOUR_API_KEY"
```

Do **not** put your API key directly inside the Python code.

The router currently uses:

```text
jev-1.13-free
```

## Test Codex

```powershell
codex exec --skip-git-repo-check "Say CODEX ROUTING TEST SUCCESSFUL"
```

## Test Your Free Coding Model

The example router uses Claude Code CLI as the interface for the free model:

```powershell
claude -p "Write a Python function that adds two numbers."
```

Your Claude Code installation can be connected to whichever compatible model/provider you want to use.

## Run the Router

```powershell
python jev_router.py
```

You will see something like:

```text
============================================================
        JEV SMART CODING ROUTER
============================================================

JEV will decide:

  FREE MODEL -> simple coding
  CODEX      -> difficult coding

What do you want to build?

>
```

## Example 1 — Simple Task

Enter:

```text
Create a Streamlit application.

Create app.py.

Show a text input box.

When the user types hello and presses a button,
display:

Hai, Welcome to Neeps
```

JEV may decide:

```text
JEV DECISION

Selected agent : free_model

Model probabilities:

free_model       90.0%
codex            10.0%
```

The free coding agent will then create files inside:

```text
demo_project/
```

For example:

```text
demo_project/
└── app.py
```

Run the generated Streamlit application:

```powershell
cd demo_project
streamlit run app.py
```

## Example 2 — Complex Task

Try:

```text
Investigate and fix an intermittent Python concurrency bug where
multiple workers can process the same database record simultaneously.

Identify the possible race condition and implement a production-safe fix.
```

JEV may route the task to Codex:

```text
JEV
 ↓
Codex
 ↓
Edits project files
```

## Why Use JEV?

Without routing:

```text
Simple README change
       ↓
Expensive Model

Simple Python script
       ↓
Expensive Model

Complex production bug
       ↓
Expensive Model
```

With JEV:

```text
Simple task
    ↓
Free Model

Medium task
    ↓
Free Model

Complex task
    ↓
Codex
```

The idea is to use cheaper or free models where possible and save stronger models for tasks that actually need them.

## Important

This project is an experiment/demo.

JEV makes probabilistic decisions, so its routing decision will not always be perfect.

For production systems, consider:

- confidence thresholds
- fallback models
- error handling
- retry logic
- cost limits
- security restrictions
- human approval for sensitive actions

## Security

Never commit API keys.

Your `.gitignore` should include:

```gitignore
.env
__pycache__/
*.pyc
.venv/
venv/

demo_project/*
!demo_project/.gitkeep
```

## About `.gitkeep`

Git does not track empty directories.

The file:

```text
demo_project/.gitkeep
```

exists only so the empty `demo_project` directory appears in GitHub.

Once the router starts running, coding agents can create actual files inside that directory.

## Goal of This Project

The purpose of this project is to demonstrate JEV in a practical developer workflow:

```text
Understand task
      ↓
JEV makes decision
      ↓
Choose coding agent
      ↓
Agent performs real work
      ↓
Project files are created/updated
```

JEV acts as the **decision layer**, while coding models such as Codex or other agents perform the actual software development work.
