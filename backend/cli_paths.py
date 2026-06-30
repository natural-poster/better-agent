from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Iterable, Optional


DEFAULT_CLI_DIRS = (
    "/usr/local/lib/npm-global/bin",
    "~/.npm-global/bin",
    "~/.local/bin",
    "/opt/homebrew/bin",
    "/usr/local/bin",
)

# Windows npm global bin directories (tried after shutil.which).
_WINDOWS_NPM_DIRS = (
    "%APPDATA%\\npm",
    "%ProgramFiles%\\nodejs",
    "%ProgramFiles(x86)%\\nodejs",
    "~\\AppData\\Roaming\\npm",
)

# On Windows, npm creates both a .cmd wrapper and a .exe shim for each
# package. Prefer .exe (a native PE binary that CreateProcess can run
# directly) over .cmd (a batch script that needs cmd.exe to execute).
_WINDOWS_EXTS = (".exe", ".cmd", ".bat")


def _windows_candidates(name: str) -> list[Path]:
    dirs = [Path(os.path.expandvars(os.path.expanduser(d))) for d in _WINDOWS_NPM_DIRS]
    candidates: list[Path] = []
    for d in dirs:
        for ext in _WINDOWS_EXTS:
            candidates.append(d / (name + ext))
    return candidates


def resolve_cli_binary(name: str, extra_dirs: Iterable[str] = ()) -> Optional[str]:
    found = shutil.which(name)
    if found:
        # On Windows, shutil.which may return a .cmd batch file. Prefer a
        # sibling .exe shim in the same directory so asyncio.create_subprocess_exec
        # can run it directly without going through cmd.exe.
        if sys.platform == "win32" and found.lower().endswith(".cmd"):
            exe_sibling = Path(found[:-4] + ".exe")
            if exe_sibling.is_file():
                return str(exe_sibling)
        return found

    if sys.platform == "win32":
        for candidate in _windows_candidates(name):
            if candidate.is_file():
                return str(candidate)
        return None

    for raw_dir in [*extra_dirs, *DEFAULT_CLI_DIRS]:
        candidate = Path(os.path.expanduser(raw_dir)) / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None
