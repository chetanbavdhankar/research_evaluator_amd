"""Launch the Gradio app in local Windows shells with mixed Path/PATH state.

Some Codex/PowerShell environments expose only ``Path`` to child Python
processes after duplicate environment cleanup. A Gradio transitive dependency
looks up ``PATH`` explicitly during import, so normalize it before loading
``app.py``.
"""

from __future__ import annotations

import os
import runpy
import sys


if "PATH" not in os.environ:
    os.environ["PATH"] = os.environ.get("Path", "")

sys.path.insert(0, os.getcwd())

runpy.run_path("app.py", run_name="__main__")
