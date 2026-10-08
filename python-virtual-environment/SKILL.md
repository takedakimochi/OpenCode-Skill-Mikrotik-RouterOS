---
name: python-virtual-environment
description: Use whenever the agent writes, runs, tests, or installs dependencies for Python code/scripts (.py files, pip install, pytest, py_compile, etc). Always execute Python inside a temporary virtual environment (venv) under /tmp/opencode so system-wide Python and global packages are never modified. Trigger on keywords like "python", ".py", "pip", "run script", "test python".
---

# Python — Temporary Virtual Environment Required

## Principle

**NEVER** run any Python script directly with the system `python3`/`python`, and **NEVER** install packages into the global Python (including `pip install` without a venv, `pip install --user`, or `sudo pip`). This breaks the system environment (package conflicts, accidental version upgrades, broken dependencies).

Every Python script execution by the AI agent **MUST** use a temporary virtual environment (temporary venv).

## Standard Workflow

### 1. Check for an existing session venv (reuse it, don't recreate it)

Within a single task, reuse the same venv repeatedly. Build a slug from the project name (workspace folder).

```bash
VENV=/tmp/opencode/$(basename "$(pwd)")-venv
```

If it doesn't exist yet, create it once:

```bash
python3 -m venv "$VENV"
```

> If `python3 -m venv` fails (ensurepip/venv not installed), tell the user first — do not fall back to a system install without permission.

### 2. Run scripts with the venv python (no `source activate` needed)

Use the absolute path to the binary inside the venv, so you don't have to modify the shell:

```bash
"$VENV/bin/python" script.py
"$VENV/bin/python" -m py_compile script.py
"$VENV/bin/python" -m pytest tests/
"$VENV/bin/python" app.py --serve
```

### 3. Install dependencies ONLY inside the venv

```bash
"$VENV/bin/python" -m pip install -r requirements.txt
"$VENV/bin/python" -m pip install routeros_api python-dotenv
```

- Always prefer the `requirements.txt` / `pyproject.toml` file that already exists in the project.
- Never `pip install` outside the venv.

### 4. Clean up when done (optional but recommended)

The temporary venv may be deleted as soon as the task is finished, since its lifetime is limited to that task:

```bash
/bin/rm -rf "$VENV"
```

A venv under `/tmp/opencode` is removed automatically on reboot, so it is safe if not deleted manually. `/tmp/opencode` is already allowed for external directory access.

## Additional Rules

- **Allowed exception:** if the project already has a consistent active venv (`.venv/`, `venv/`, or a managed `pipx`/`uv`/`poetry` environment), use that — it is still an isolated venv.
- Pure one-liner scripts that only use stdlib (e.g. `python3 -c "print(1+1)"`) MUST still be run through the venv, for consistency and safety.
- `pip list`/environment inspection reports also go through `"$VENV/bin/python" -m pip list`.
- Never use `sudo` for anything Python-related.
- Never edit files that are part of the system Python installation.

## Full Example

```bash
# 1. Prepare the temporary venv
VENV=/tmp/opencode/$(basename "$(pwd)")-venv
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
fi

# 2. Install project dependencies
"$VENV/bin/python" -m pip install -r requirements.txt

# 3. Run & verify scripts
"$VENV/bin/python" script.py
"$VENV/bin/python" -m py_compile script.py
"$VENV/bin/python" -m pytest tests/ -q

# 4. Clean up
/bin/rm -rf "$VENV"
```
