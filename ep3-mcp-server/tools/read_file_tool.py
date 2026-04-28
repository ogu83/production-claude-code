"""read_file_tool.py — Path-bounded file read tool.

Design principles demonstrated:
  1. Path bounding — uses pathlib.resolve() + is_relative_to() for a safe
     containment check. startswith() on strings is not safe (sibling paths
     like /data_evil/ pass a /data prefix check).
  2. Size and encoding limits — rejects files over 50 KB and binary files.
     Prevents accidental context blowups from large or non-text files.
  3. Explicit error returns — never raises. All failures return a JSON error
     object so Claude receives a parseable, predictable response.
"""

from __future__ import annotations

import json
from pathlib import Path

MAX_BYTES = 50_000  # 50 KB — prevents large file reads blowing up context


def read_file(path: str, allowed_dir: Path) -> str:
    """Read a file, enforcing that it is inside allowed_dir.

    Args:
        path:        The file path requested (may be relative or absolute).
        allowed_dir: The directory that bounds all readable files.
                     Resolved to an absolute path before comparison.

    Returns:
        File content as a plain string on success.
        JSON string {"error": "message"} on any failure.
    """
    allowed = allowed_dir.resolve()

    # Resolve the candidate path to its absolute real form.
    # This collapses ../ traversal attempts before any check.
    try:
        candidate = Path(path).resolve()
    except Exception as e:
        return json.dumps({"error": f"Invalid path: {e}"})

    # Safe containment check: is_relative_to() handles sibling paths correctly.
    # e.g. /data_evil is NOT relative to /data even though "data" is a prefix.
    try:
        candidate.relative_to(allowed)
    except ValueError:
        return json.dumps({
            "error": f"Path outside allowed directory. "
                     f"Requested: {candidate} | Allowed: {allowed}"
        })

    if not candidate.exists():
        return json.dumps({"error": f"File not found: {candidate.name}"})

    if not candidate.is_file():
        return json.dumps({"error": f"Path is a directory, not a file: {candidate.name}"})

    file_size = candidate.stat().st_size
    if file_size > MAX_BYTES:
        return json.dumps({
            "error": f"File too large ({file_size:,} bytes). "
                     f"Limit is {MAX_BYTES:,} bytes."
        })

    try:
        return candidate.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return json.dumps({
            "error": f"File is not valid UTF-8 (binary file?): {candidate.name}"
        })
    except PermissionError:
        return json.dumps({"error": "Permission denied"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})
