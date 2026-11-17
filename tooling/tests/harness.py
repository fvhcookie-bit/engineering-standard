"""Харнесс приёмочных сценариев Б: git-снапшоты base/head (гайдлайн §7.1)."""

import subprocess
import tempfile
from pathlib import Path


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=True,
    ).stdout


def make_diff(base: dict[str, str], head: dict[str, str]) -> str:
    """Реальный git diff -M -C между деревьями base и head."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        def write_tree(tree: dict[str, str]) -> None:
            for rel, content in tree.items():
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8", newline="\n")

        def remove_tree(tree: dict[str, str]) -> None:
            for rel in tree:
                p = root / rel
                if p.is_file():
                    p.unlink()
            # пустые каталоги не удаляем: git add -A их не увидит, а pruning
            # на Windows гонится за уже удалёнными родителями (FileNotFoundError)

        write_tree(base)
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "fixture@example.invalid")
        _git(root, "config", "user.name", "fixture")
        _git(root, "add", "-A")
        if base:
            _git(root, "commit", "-qm", "base")
        remove_tree(base)
        write_tree(head)
        _git(root, "add", "-A")
        return _git(root, "diff", "--cached", "-M", "-C")
