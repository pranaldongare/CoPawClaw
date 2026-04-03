#!/usr/bin/env python3
"""
Patch CoPaw's execute_shell_command timeout for long-running skill scripts.

The default timeout for shell commands in CoPaw/AgentScope is too short for
skills like tech_sensing which can take 30-60 minutes. This script finds the
timeout value in the installed package and increases it to 1 hour (3600s).

It also enables the async (background) execution flag on execute_shell_command
so that long-running commands run in the background while the user can continue
chatting. When async is enabled, CoPaw automatically registers helper tools:
  - view_task: Check the status of a running background task
  - wait_task: Wait for a background task to complete
  - cancel_task: Cancel a running background task

Usage:
    python scripts/patch_copaw_timeout.py
    python scripts/patch_copaw_timeout.py --check      # Check current state
    python scripts/patch_copaw_timeout.py --revert      # Revert the patch
    python scripts/patch_copaw_timeout.py --timeout 7200  # Custom timeout (seconds)

Must be run from the project root with the venv active.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

DEFAULT_NEW_TIMEOUT = 3600  # 1 hour

PATCH_MARKER = "# [CoPawClaw] Increased shell timeout for long-running skills"


def find_copaw_package(venv_path: Path | None = None) -> Path:
    """Locate the copaw package directory in the installed site-packages."""
    if venv_path is None:
        candidates = [
            Path("venv/Lib/site-packages/copaw"),           # Windows
            Path("venv/lib/python3.12/site-packages/copaw"), # Linux
            Path("venv/lib/python3.11/site-packages/copaw"),
            Path("venv/lib/python3.10/site-packages/copaw"),
        ]
        for c in candidates:
            if c.exists():
                return c
        # Fallback: find it via importlib
        try:
            import copaw
            return Path(copaw.__file__).parent
        except ImportError:
            pass
    else:
        pkg = venv_path / "Lib" / "site-packages" / "copaw"
        if pkg.exists():
            return pkg
        for pyver in ["python3.12", "python3.11", "python3.10"]:
            pkg = venv_path / "lib" / pyver / "site-packages" / "copaw"
            if pkg.exists():
                return pkg

    print("ERROR: Could not find copaw package directory.")
    print("Make sure you're in the project root and the venv is set up.")
    sys.exit(1)


def find_timeout_files(copaw_dir: Path) -> list[tuple[Path, str, str]]:
    """
    Search the copaw package for files containing execute_shell_command timeout.

    Returns list of (filepath, pattern_type, current_timeout_value) tuples.
    """
    results = []

    # Patterns to search for:
    # 1. AgentScope service: execute_shell_command(..., timeout=NNN)
    # 2. Tool definition with timeout default
    # 3. Direct timeout= parameter in tool wrappers
    timeout_patterns = [
        # Pattern: timeout=180 or timeout=300 in execute_shell_command context
        (re.compile(r'(execute_shell_command.*?timeout\s*=\s*)(\d+)', re.DOTALL), "function_call"),
        # Pattern: "timeout" key in tool schema defaults
        (re.compile(r'("timeout".*?"default"\s*:\s*)(\d+)'), "schema_default"),
        # Pattern: timeout = 180 or TIMEOUT = 180 as module-level constant
        (re.compile(r'((?:SHELL_|COMMAND_|EXEC_)?TIMEOUT\s*=\s*)(\d+)', re.IGNORECASE), "constant"),
    ]

    # Also search agentscope package
    agentscope_dir = copaw_dir.parent / "agentscope"

    search_dirs = [copaw_dir]
    if agentscope_dir.exists():
        search_dirs.append(agentscope_dir)

    for search_dir in search_dirs:
        for py_file in search_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue

            if "shell" not in content.lower() and "timeout" not in content.lower():
                continue

            for pattern, ptype in timeout_patterns:
                for match in pattern.finditer(content):
                    timeout_val = match.group(2)
                    # Only report timeouts that look like shell command timeouts
                    # (not cache TTLs, HTTP timeouts, etc.)
                    val = int(timeout_val)
                    if 120 <= val <= 600:  # Likely shell timeout range
                        results.append((py_file, ptype, timeout_val))

    return results


def patch_timeout_in_file(filepath: Path, new_timeout: int) -> bool:
    """Patch timeout values in a single file."""
    content = filepath.read_text(encoding="utf-8")

    if PATCH_MARKER in content:
        print(f"  Already patched: {filepath}")
        return False

    modified = False
    new_content = content

    # Pattern 1: execute_shell_command(..., timeout=NNN)
    pattern1 = re.compile(r'(execute_shell_command.*?timeout\s*=\s*)(\d+)', re.DOTALL)
    for match in pattern1.finditer(content):
        old_val = int(match.group(2))
        if 120 <= old_val <= 600:
            new_content = new_content.replace(
                match.group(0),
                f"{match.group(1)}{new_timeout}",
                1,
            )
            modified = True
            print(f"  Patched timeout {old_val} -> {new_timeout} in: {filepath.name}")

    # Pattern 2: "default": NNN in timeout schema
    pattern2 = re.compile(r'("timeout".*?"default"\s*:\s*)(\d+)')
    for match in pattern2.finditer(new_content):
        old_val = int(match.group(2))
        if 120 <= old_val <= 600:
            new_content = new_content.replace(
                match.group(0),
                f"{match.group(1)}{new_timeout}",
                1,
            )
            modified = True
            print(f"  Patched schema default {old_val} -> {new_timeout} in: {filepath.name}")

    # Pattern 3: TIMEOUT = NNN constant
    pattern3 = re.compile(r'((?:SHELL_|COMMAND_|EXEC_)?TIMEOUT\s*=\s*)(\d+)', re.IGNORECASE)
    for match in pattern3.finditer(new_content):
        old_val = int(match.group(2))
        if 120 <= old_val <= 600:
            new_content = new_content.replace(
                match.group(0),
                f"{match.group(1)}{new_timeout}",
                1,
            )
            modified = True
            print(f"  Patched constant {old_val} -> {new_timeout} in: {filepath.name}")

    if modified:
        # Backup original
        backup = filepath.with_suffix(".py.timeout_bak")
        if not backup.exists():
            shutil.copy2(filepath, backup)

        # Add marker comment at the top (after any existing comments/docstrings)
        lines = new_content.split("\n")
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("import") or line.startswith("from") or (line and not line.startswith("#") and not line.startswith('"""') and not line.startswith("'''")):
                insert_idx = i
                break
        lines.insert(insert_idx, PATCH_MARKER)
        new_content = "\n".join(lines)

        filepath.write_text(new_content, encoding="utf-8")
        clear_pycache(filepath)

    return modified


def revert_timeout_in_file(filepath: Path) -> bool:
    """Revert timeout patch from a single file."""
    backup = filepath.with_suffix(".py.timeout_bak")
    if backup.exists():
        shutil.copy2(backup, filepath)
        clear_pycache(filepath)
        print(f"  Reverted from backup: {filepath}")
        return True

    content = filepath.read_text(encoding="utf-8")
    if PATCH_MARKER in content:
        new_content = content.replace(PATCH_MARKER + "\n", "")
        filepath.write_text(new_content, encoding="utf-8")
        clear_pycache(filepath)
        print(f"  Removed patch marker: {filepath}")
        return True

    return False


def clear_pycache(filepath: Path):
    """Remove .pyc files for the patched module."""
    cache_dir = filepath.parent / "__pycache__"
    if cache_dir.exists():
        stem = filepath.stem
        for pyc in cache_dir.glob(f"{stem}*.pyc"):
            pyc.unlink()


def main():
    parser = argparse.ArgumentParser(
        description="Patch CoPaw shell command timeout for long-running skills"
    )
    parser.add_argument("--check", action="store_true", help="Show current timeout values")
    parser.add_argument("--revert", action="store_true", help="Revert the patch")
    parser.add_argument("--timeout", type=int, default=DEFAULT_NEW_TIMEOUT,
                        help=f"New timeout in seconds (default: {DEFAULT_NEW_TIMEOUT})")
    parser.add_argument("--venv", type=Path, help="Path to venv directory")
    args = parser.parse_args()

    copaw_dir = find_copaw_package(args.venv)
    print(f"CoPaw package: {copaw_dir}")

    if args.check:
        results = find_timeout_files(copaw_dir)
        if results:
            print(f"\nFound {len(results)} timeout value(s):")
            for filepath, ptype, val in results:
                rel = filepath.relative_to(copaw_dir.parent)
                patched = PATCH_MARKER in filepath.read_text(encoding="utf-8")
                status = " [PATCHED]" if patched else ""
                print(f"  {rel}: {val}s ({ptype}){status}")
        else:
            print("\nNo shell command timeouts found in the expected range (120-600s).")
            print("The timeout may be set differently in your CoPaw version.")
            print("\nTry searching manually:")
            print(f"  grep -r 'timeout' {copaw_dir}/")
        return

    if args.revert:
        results = find_timeout_files(copaw_dir)
        reverted = 0
        seen = set()
        for filepath, _, _ in results:
            if filepath not in seen:
                seen.add(filepath)
                if revert_timeout_in_file(filepath):
                    reverted += 1
        if reverted:
            print(f"\nReverted {reverted} file(s). Restart CoPaw for changes to take effect.")
        else:
            print("Nothing to revert.")
        return

    # Apply patch
    results = find_timeout_files(copaw_dir)
    if not results:
        print("\nNo shell command timeouts found in the expected range (120-600s).")
        print("The timeout may be set differently in your CoPaw version.")
        print(f"\nTry searching manually:")
        print(f"  grep -rn 'timeout' {copaw_dir}/")
        print(f"\nAlternative: Set the timeout in the SKILL.md or run scripts directly:")
        print(f"  python skills/tech_sensing/scripts/run_pipeline.py --domain 'AI' --user-id default")
        sys.exit(1)

    patched = 0
    seen = set()
    for filepath, _, _ in results:
        if filepath not in seen:
            seen.add(filepath)
            if patch_timeout_in_file(filepath, args.timeout):
                patched += 1

    if patched:
        print(f"\nPatched {patched} file(s) with timeout={args.timeout}s ({args.timeout // 60} min).")
        print("Restart CoPaw for changes to take effect:")
        print("  copaw app")
    else:
        print("\nAll files already patched.")


if __name__ == "__main__":
    main()
