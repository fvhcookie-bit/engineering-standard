"""Контракт-тесты диф-парсера: добавленные строки, rename, binary, deleted."""

from core.diff import parse_unified_diff

SAMPLE = """diff --git a/src/app.py b/src/app.py
index 1111111..2222222 100644
--- a/src/app.py
+++ b/src/app.py
@@ -1,3 +1,6 @@
 existing line 1
+added clean A
 existing line 2
+FORBIDDEN-DEMO appears here
+added clean B
 existing line 3
diff --git a/old/mod.py b/new/mod.py
similarity index 90%
rename from old/mod.py
rename to new/mod.py
@@ -1,2 +1,2 @@
-pass old
+pass new
diff --git a/blob.bin b/blob.bin
index 1111111..2222222 100644
Binary files a/blob.bin and b/blob.bin differ
diff --git a/gone.py b/gone.py
deleted file mode 100644
index 1111111..0000000
--- a/gone.py
+++ /dev/null
@@ -1 +0,0 @@
-print("gone")
"""


def test_added_lines_with_numbers():
    files = parse_unified_diff(SAMPLE)
    app = files[0]
    assert app.path == "src/app.py"
    assert app.added == [
        (2, "added clean A"),
        (4, "FORBIDDEN-DEMO appears here"),
        (5, "added clean B"),
    ]
    assert app.removed_count == 0


def test_rename_is_not_new_code():
    files = parse_unified_diff(SAMPLE)
    mod = files[1]
    assert mod.is_rename is True
    assert mod.old_path == "old/mod.py"
    assert mod.path == "new/mod.py"
    assert mod.added == [(1, "pass new")]


def test_binary_marked_without_content():
    files = parse_unified_diff(SAMPLE)
    assert files[2].is_binary is True
    assert files[2].added == []


def test_deleted_file():
    files = parse_unified_diff(SAMPLE)
    gone = files[3]
    assert gone.is_deleted is True
    assert gone.path == "gone.py"
    assert gone.added == []
    assert gone.removed_count == 1
