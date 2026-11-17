"""Парсер unified diff (git diff -M -C): файлы, hunk'и, добавленные строки.

- rename/copy detection включён: переименование не считается «новым кодом» (Б-10).
- Добавленные строки извлекаются с номерами в НОВОМ файле; удалённые — только счётчиком.
- Binary-файлы помечаются без содержимого.
"""

from __future__ import annotations

from dataclasses import dataclass, field

DIFF_HEAD = "diff --git "
DEV_NULL = "/dev/null"


@dataclass
class FileDiff:
    path: str  # путь в новом дереве (для удалённого файла — путь в старом)
    old_path: str | None = None  # при rename/copy
    is_new: bool = False
    is_deleted: bool = False
    is_binary: bool = False
    is_rename: bool = False
    added: list[tuple[int, str]] = field(default_factory=list)  # (line_no_in_new, text)
    removed_count: int = 0


def _strip_a_b(token: str) -> str:
    """'a/src/app.py' -> 'src/app.py'; '/dev/null' -> '/dev/null'."""
    if token.startswith("a/"):
        return token[2:]
    if token.startswith("b/"):
        return token[2:]
    return token


def parse_unified_diff(diff_text: str) -> list[FileDiff]:
    files: list[FileDiff] = []
    cur: FileDiff | None = None
    new_line = 0

    for raw in diff_text.splitlines():
        line = raw.rstrip("\r")

        if line.startswith(DIFF_HEAD):
            pair = line[len(DIFF_HEAD):]
            b_side = pair.split(" b/", 1)
            cur = FileDiff(path=_strip_a_b(b_side[1]) if len(b_side) == 2 else pair)
            files.append(cur)
            continue
        if cur is None:
            continue

        if line.startswith("new file mode"):
            cur.is_new = True
            continue
        if line.startswith(("delete mode", "deleted file mode")):
            cur.is_deleted = True
            continue
        if line.startswith("rename from "):
            cur.is_rename = True
            cur.old_path = _strip_a_b(line[len("rename from "):])
            continue
        if line.startswith("copy from "):
            cur.is_rename = True
            cur.old_path = _strip_a_b(line[len("copy from "):])
            continue
        if line.startswith("Binary files "):
            cur.is_binary = True
            continue
        if line.startswith("--- "):
            old = _strip_a_b(line[4:])
            if old == DEV_NULL:
                cur.is_new = True
            else:
                if cur.old_path is None:
                    cur.old_path = old
                if cur.path == "":
                    cur.path = old
            continue
        if line.startswith("+++ "):
            new = _strip_a_b(line[4:])
            if new == DEV_NULL:
                cur.is_deleted = True
                cur.path = cur.old_path or cur.path
            else:
                cur.path = new
            continue
        if line.startswith("@@"):
            # @@ -a,b +c,d @@ meta
            m = line.split("+", 1)
            try:
                new_line = int(m[1].split(",", 1)[0].split(" ", 1)[0].split("@")[0])
            except (IndexError, ValueError):
                new_line = 1
            continue
        if line.startswith("+"):
            cur.added.append((new_line, line[1:]))
            new_line += 1
            continue
        if line.startswith("-"):
            cur.removed_count += 1
            continue
        if line.startswith(" ") or line == "":
            new_line += 1
            continue
        # '\ No newline at end of file' и прочее — игнорируем

    return files
