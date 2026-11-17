"""pytest: делает tooling/ импортируемым (core, gates, runner, adapters)."""

import sys
from pathlib import Path

TOOLING_DIR = Path(__file__).resolve().parents[1]
if str(TOOLING_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLING_DIR))
