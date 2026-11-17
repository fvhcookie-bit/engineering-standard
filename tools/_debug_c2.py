import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tooling"))

from core.registries import Registries, parse_exceptions_md  # noqa: E402
from core.files import RepoFiles  # noqa: E402

exc = (ROOT / "tooling/fixtures/b_19/head/EXCEPTIONS.md").read_text(encoding="utf-8")
print("EXC first 120:", repr(exc[:120]))
print("parsed:", parse_exceptions_md(exc))

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    for rel, c in {"src/a.py": "recv()\n# EX-2026-001\n", "EXCEPTIONS.md": exc}.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(c, encoding="utf-8", newline="\n")
    rf = RepoFiles(root=root)
    print("files:", rf.list_files())
    r = Registries.from_repo(root)
    print("from_repo exceptions:", r.exceptions)

# воспроизведение записи b_01 head (по мотивам теста)
import json  # noqa: E402

spec = json.loads((ROOT / "tooling/fixtures/b_01/scenario.json").read_text(encoding="utf-8"))
print("cfg dictionary:", spec["config"]["dictionary"])
