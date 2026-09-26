import os
import subprocess
from pathlib import Path

import requests


# ============================================================
# CONFIG
# ============================================================

BEATAPI_KEY = os.environ.get("BEATAPI_API_KEY")

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR / "demo_project"

PROJECT_DIR.mkdir(exist_ok=True)

JEV_URL = "https://api.beatapi.io/v1/systemone"


# ============================================================
# SHOW CHANGED FILES
# ============================================================

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__"
}


def get_project_snapshot():
    snapshot = {}

    for file in PROJECT_DIR.rglob("*"):
        if not file.is_file():
            continue

        if any(part in IGNORE_DIRS for part in file.parts):
            continue

        # Don't inspect secret env files
        if file.name == ".env":
            continue

        try:
            stat = file.stat()

            snapshot[str(file.relative_to(PROJECT_DIR))] = (
                stat.st_size,
                stat.st_mtime_ns
            )
        except OSError:
            pass

    return snapshot


def show_changes(before, after):
    print("\n" + "=" * 60)
    print("FILES CHANGED")
    print("=" * 60)

    changed = False

    for file in sorted(after):

        if file not in before:
            print(f"[CREATED]  {file}")
            changed = True

        elif before[file] != after[file]:
            print(f"[MODIFIED] {file}")
            changed = True

    for file in sorted(before):

        if file not in after:
            print(f"[DELETED]  {file}")
            changed = True

    if not changed:
        print("No project files changed.")


# ============================================================
# JEV ROUTER
# ============================================================

def ask_jev(task):

    payload = {
        "model": "jev-1.13-free",

        "state": task,

        "questions": {

            "model_choice": {

                "type": "choice",

                "instructions":
                    "Choose the most suitable coding agent for this task.",

                "criteria": {

                    "free_model":
                        "Use for simple coding tasks, small applications, "
                        "basic Python, Streamlit apps, formatting, README changes, "
                        "simple bug fixes, small scripts and easy development work.",

                    "codex":
                        "Use for difficult software engineering tasks, "
                        "complex debugging, concurrency problems, architecture, "
                        "repository-wide changes, difficult bugs, multi-file refactoring "
                        "or tasks requiring strong reasoning."
                }
            },

            "difficulty": {

                "type": "score",

                "instructions":
                    "Rate the software engineering difficulty.",

                "criteria": [
                    "trivial",
                    "easy",
                    "medium",
                    "hard",
                    "very_hard"
                ]
            }
        }
    }

    response = requests.post(
        JEV_URL,
        headers={
            "Authorization": f"Bearer {BEATAPI_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# CODEX
# ============================================================

def run_codex(task):

    print("\n🚀 ROUTING TO CODEX")
    print(f"📁 Working directory: {PROJECT_DIR}\n")

    agent_task = f"""
You are working inside this project directory:

{PROJECT_DIR}

TASK:

{task}

IMPORTANT:

- Work directly on the project files.
- Create files when required.
- Edit existing files when required.
- Do NOT only explain the solution.
- Actually implement the requested task.
- Do not modify anything outside this project directory.
- Keep the implementation simple and working.
"""

    subprocess.run(
        [
            "cmd.exe",
            "/d",
            "/s",
            "/c",
            "codex",
            "exec",
            "--skip-git-repo-check",
            "--sandbox",
            "workspace-write",
            "-"
        ],
        cwd=PROJECT_DIR,
        input=agent_task,
        text=True
    )


# ============================================================
# FREE MODEL THROUGH CLAUDE CODE
# ============================================================

def run_free_model(task):

    print("\n🆓 ROUTING TO FREE MODEL")
    print(f"📁 Working directory: {PROJECT_DIR}\n")

    agent_task = f"""
TASK:

{task}

You are operating as a coding agent.

Work directly inside the current project directory.

IMPORTANT:

- Create the required files.
- Edit existing files when necessary.
- Do NOT merely return code in the response.
- Actually use your file tools and implement the task.
- Do not change anything outside the current directory.
- Keep the solution simple and working.
"""

    subprocess.run(
        [
            "cmd.exe",
            "/d",
            "/s",
            "/c",
            "claude",
            "-p",
            "--permission-mode",
            "acceptEdits",
            "--tools",
            "Read,Edit,Write",
            "Read the coding task provided through stdin and implement it directly in the current project."
        ],
        cwd=PROJECT_DIR,
        input=agent_task,
        text=True
    )


# ============================================================
# MAIN LOOP
# ============================================================

if not BEATAPI_KEY:
    print("ERROR: BEATAPI_API_KEY environment variable is missing.")
    print("")
    print('PowerShell:')
    print('$env:BEATAPI_API_KEY="YOUR_KEY"')
    raise SystemExit(1)


print("")
print("=" * 60)
print("        JEV SMART CODING ROUTER")
print("=" * 60)

print("")
print("Project:")
print(PROJECT_DIR)

print("")
print("JEV will decide:")
print("")
print("  🆓 FREE MODEL  -> simple coding")
print("  🚀 CODEX       -> difficult coding")
print("")

while True:

    print("\n" + "=" * 60)

    task = input(
        "\nWhat do you want to build? (type exit to stop)\n\n> "
    ).strip()

    if task.lower() in {"exit", "quit", "q"}:
        print("\nBye 👋")
        break

    if not task:
        continue

    try:

        print("\n🧠 Asking JEV which coding agent should handle this...")

        result = ask_jev(task)

        choice_data = result["answers"]["model_choice"]

        choice = choice_data["choice"]

        probabilities = choice_data["probabilities"]

        difficulty = result["answers"]["difficulty"]

        print("\n" + "=" * 60)
        print("JEV DECISION")
        print("=" * 60)

        print(f"\nSelected agent : {choice}")

        print("\nModel probabilities:")

        for model, probability in probabilities.items():

            percentage = probability * 100

            print(
                f"  {model:<15} {percentage:>6.1f}%"
            )

        print(
            f"\nDifficulty score: "
            f"{difficulty.get('score')}"
        )

        before = get_project_snapshot()

        # ====================================================
        # ROUTE
        # ====================================================

        if choice == "codex":

            run_codex(task)

        elif choice == "free_model":

            run_free_model(task)

        else:

            print(
                f"\nUnknown JEV choice: {choice}"
            )

            continue

        # ====================================================
        # CHECK FILES
        # ====================================================

        after = get_project_snapshot()

        show_changes(before, after)

        print("\n✅ Task finished.")

        print(
            f"\n📁 Open this folder:\n{PROJECT_DIR}"
        )

    except requests.exceptions.HTTPError as e:

        print("\n❌ JEV API error:")

        try:
            print(e.response.text)
        except Exception:
            print(e)

    except Exception as e:

        print("\n❌ ERROR:")
        print(e)