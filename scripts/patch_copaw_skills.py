"""
Patch CoPaw's react_agent.py to inject skill instructions into the system prompt.

CoPaw registers skills into the toolkit but never calls toolkit.get_agent_skill_prompt()
to add them to the system prompt. This means the LLM never sees skill descriptions and
cannot invoke them. This script patches that gap.

Usage:
    python scripts/patch_copaw_skills.py
    python scripts/patch_copaw_skills.py --check   # Check if patch is needed
    python scripts/patch_copaw_skills.py --revert   # Revert the patch

Must be run from the project root with the venv active, or provide --venv path.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

PATCH_MARKER = "# [CoPawClaw] Inject skill instructions into system prompt"

# The original code block we're looking for
ORIGINAL_PATTERN = (
    "        # Build system prompt\n"
    "        sys_prompt = self._build_sys_prompt()\n"
)

# The patched replacement
PATCHED_BLOCK = (
    "        # Build system prompt\n"
    "        sys_prompt = self._build_sys_prompt()\n"
    "\n"
    f"        {PATCH_MARKER}\n"
    "        skill_prompt = toolkit.get_agent_skill_prompt()\n"
    "        if skill_prompt:\n"
    "            sys_prompt = sys_prompt + \"\\n\\n\" + skill_prompt\n"
)


def find_react_agent(venv_path: Path | None = None) -> Path:
    """Locate react_agent.py in the installed copaw package."""
    if venv_path is None:
        # Auto-detect from project root
        candidates = [
            Path("venv/Lib/site-packages/copaw/agents/react_agent.py"),  # Windows
            Path("venv/lib/python3.12/site-packages/copaw/agents/react_agent.py"),  # Linux
            Path("venv/lib/python3.11/site-packages/copaw/agents/react_agent.py"),
        ]
        for c in candidates:
            if c.exists():
                return c
        # Fallback: find it via importlib
        try:
            import copaw.agents.react_agent as mod
            return Path(mod.__file__)
        except ImportError:
            pass
    else:
        agent_file = venv_path / "Lib" / "site-packages" / "copaw" / "agents" / "react_agent.py"
        if agent_file.exists():
            return agent_file
        # Try lowercase lib (Linux)
        for pyver in ["python3.12", "python3.11", "python3.10"]:
            agent_file = venv_path / "lib" / pyver / "site-packages" / "copaw" / "agents" / "react_agent.py"
            if agent_file.exists():
                return agent_file

    print("ERROR: Could not find copaw/agents/react_agent.py")
    print("Make sure you're in the project root and the venv is set up.")
    sys.exit(1)


def is_patched(content: str) -> bool:
    return PATCH_MARKER in content


def apply_patch(filepath: Path) -> bool:
    content = filepath.read_text(encoding="utf-8")

    if is_patched(content):
        print(f"Already patched: {filepath}")
        return False

    if ORIGINAL_PATTERN not in content:
        print(f"ERROR: Cannot find the expected code block in {filepath}")
        print("The file may have been modified by a CoPaw update.")
        print("Manual patching required — see README troubleshooting section.")
        sys.exit(1)

    # Backup original
    backup = filepath.with_suffix(".py.bak")
    if not backup.exists():
        shutil.copy2(filepath, backup)
        print(f"Backup saved: {backup}")

    new_content = content.replace(ORIGINAL_PATTERN, PATCHED_BLOCK, 1)
    filepath.write_text(new_content, encoding="utf-8")

    # Clear __pycache__ so Python picks up the change
    clear_pycache(filepath)

    print(f"Patched: {filepath}")
    return True


def revert_patch(filepath: Path) -> bool:
    content = filepath.read_text(encoding="utf-8")

    if not is_patched(content):
        print(f"Not patched, nothing to revert: {filepath}")
        return False

    backup = filepath.with_suffix(".py.bak")
    if backup.exists():
        shutil.copy2(backup, filepath)
        clear_pycache(filepath)
        print(f"Reverted from backup: {filepath}")
        return True

    # No backup — remove the patch lines manually
    new_content = content.replace(PATCHED_BLOCK, ORIGINAL_PATTERN, 1)
    filepath.write_text(new_content, encoding="utf-8")
    clear_pycache(filepath)
    print(f"Reverted (removed patch lines): {filepath}")
    return True


def clear_pycache(filepath: Path):
    """Remove .pyc files for the patched module."""
    cache_dir = filepath.parent / "__pycache__"
    if cache_dir.exists():
        stem = filepath.stem
        for pyc in cache_dir.glob(f"{stem}*.pyc"):
            pyc.unlink()
            print(f"  Cleared cache: {pyc.name}")


def main():
    parser = argparse.ArgumentParser(description="Patch CoPaw skill injection")
    parser.add_argument("--check", action="store_true", help="Check if patch is needed")
    parser.add_argument("--revert", action="store_true", help="Revert the patch")
    parser.add_argument("--venv", type=Path, help="Path to venv directory")
    args = parser.parse_args()

    filepath = find_react_agent(args.venv)
    content = filepath.read_text(encoding="utf-8")

    if args.check:
        if is_patched(content):
            print(f"PATCHED: {filepath}")
        else:
            print(f"NOT PATCHED: {filepath}")
            print("Run: python scripts/patch_copaw_skills.py")
        return

    if args.revert:
        revert_patch(filepath)
        return

    if apply_patch(filepath):
        print("\nDone! Restart CoPaw for changes to take effect:")
        print("  copaw app")


if __name__ == "__main__":
    main()
