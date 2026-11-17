"""Безопасность: path-escape, лимит размера, отсутствующий файл (GUIDELINE_development §6)."""

import pytest
from core.files import PathEscape, RepoFiles


def test_refuses_escape_outside_root(tmp_path):
    rf = RepoFiles(root=tmp_path)
    secret = tmp_path.parent / "secret.txt"
    secret.write_text("x", encoding="utf-8")
    with pytest.raises(PathEscape):
        rf.read("../secret.txt")
    with pytest.raises(PathEscape):
        rf.read("sub/../../secret.txt")


def test_size_guard_returns_none(tmp_path):
    big = tmp_path / "big.txt"
    big.write_text("x" * 1025, encoding="utf-8")
    rf = RepoFiles(root=tmp_path, max_file_bytes=1024)
    assert rf.read("big.txt") is None  # слишком велик — пропуск (info на уровне гейта)
    rf2 = RepoFiles(root=tmp_path)
    assert rf2.read("big.txt") == "x" * 1025


def test_missing_file_is_none(tmp_path):
    rf = RepoFiles(root=tmp_path)
    assert rf.read("nope.txt") is None


def test_symlink_escape_refused(tmp_path):
    target = tmp_path.parent / "outside.txt"
    target.write_text("secret", encoding="utf-8")
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlink недоступен на этой системе")
    rf = RepoFiles(root=tmp_path)
    with pytest.raises(PathEscape):
        rf.read("link.txt")
