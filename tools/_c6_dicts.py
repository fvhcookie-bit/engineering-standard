# Словари подавлений остальных экосистем (C-6) + генератор контрактов.
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DICT_DIR = ROOT / "tooling" / "dictionaries"
FIXTURES = DICT_DIR / "fixtures"


def w(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


def write_dict(name: str, ecosystem: str, patterns: list[dict], lang_ext: dict) -> None:
    doc = {
        "schema": 1,
        "ecosystem": ecosystem,
        "reason_proximity_default": "same_line",
        "patterns": patterns,
    }
    w(DICT_DIR / f"{name}.yaml", yaml.safe_dump(
        doc, allow_unicode=True, sort_keys=False))
    for pat in patterns:
        for kind, sample in (("positive", pat["positive"]), ("negative", pat["negative"])):
            w(FIXTURES / name / f"{pat['id']}.{kind}.txt", sample + "\n")
    print(f"{name}: {len(patterns)} паттернов, контракты созданы")


write_dict("typescript", "typescript", [
    {"id": "eslint_disable", "regex": r"eslint-disable(-line|-next-line)?\b", "languages": ["typescript", "javascript"],
     "positive": "// eslint-disable-next-line no-console", "negative": "// обычный комментарий"},
    {"id": "ts_ignore", "regex": r"@ts-ignore\b", "languages": ["typescript"],
     "positive": "// @ts-ignore", "negative": "// @ts-expect-error тут"},
    {"id": "ts_expect_error", "regex": r"@ts-expect-error\b", "languages": ["typescript"],
     "positive": "// @ts-expect-error: намеренно неверный тип", "negative": "// @ts-ignore"},
    {"id": "ts_nocheck", "regex": r"@ts-nocheck\b", "languages": ["typescript"],
     "positive": "// @ts-nocheck", "negative": "// обычный заголовок"},
    {"id": "as_any", "regex": r"\bas any\b", "languages": ["typescript"],
     "positive": "const v = payload as any;", "negative": "const v = payload as unknown;"},
], lang_ext={"typescript": [".ts", ".tsx"], "javascript": [".js", ".jsx"]})

write_dict("javascript", "javascript", [
    {"id": "js_eslint_disable", "regex": r"eslint-disable(-line|-next-line)?\b", "languages": ["javascript"],
     "positive": "// eslint-disable no-undef", "negative": "// eslint config example"},
    {"id": "js_noinspection", "regex": r"^\s*//\s*noinspection\b", "languages": ["javascript"],
     "positive": "// noinspection JSUnusedLocalSymbols", "negative": "// обычный комментарий"},
], lang_ext={"javascript": [".js", ".jsx"]})

write_dict("go", "go", [
    {"id": "nolint", "regex": r"//\s*nolint(?::\s*[A-Za-z, ]+)?", "languages": ["go"],
     "positive": "x := 1 //nolint:errcheck", "negative": "x := 1 // обычный комментарий"},
    {"id": "nosec", "regex": r"//\s*#nosec\b", "languages": ["go"],
     "positive": "cmd := exec.Command(a) // #nosec G204", "negative": "// #nosec как текст"},
], lang_ext={"go": [".go"]})

write_dict("rust", "rust", [
    {"id": "allow_attr", "regex": r"#\[\s*allow\(", "languages": ["rust"],
     "positive": "#[allow(dead_code)]\nfn f() {}", "negative": "#[derive(Debug)]\nstruct S;"},
    {"id": "crate_allow", "regex": r"#!\[\s*allow\(", "languages": ["rust"],
     "positive": "#![allow(clippy::too_many_arguments)]", "negative": "// #![allow — как текст"},
    {"id": "unsafe_block", "regex": r"\bunsafe\s*\{", "languages": ["rust"],
     "positive": "let p = unsafe { ptr.read() };", "negative": "let p = safe_read();"},
    {"id": "unsafe_fn", "regex": r"\bunsafe\s+fn\b", "languages": ["rust"],
     "positive": "unsafe fn raw(ptr: *mut u8) {}", "negative": "fn safe_read() {}"},
], lang_ext={"rust": [".rs"]})

write_dict("java", "java", [
    {"id": "suppresswarnings", "regex": r"@SuppressWarnings\b", "languages": ["java", "kotlin"],
     "positive": "@SuppressWarnings(\"unchecked\")\nList l = raw;", "negative": "// @SuppressWarnings как текст"},
    {"id": "disabled", "regex": r"@Disabled\b", "languages": ["java"],
     "positive": "@Disabled(\"env\")\n@Test void t() {}", "negative": "@Test void works() {}"},
], lang_ext={"java": [".java"], "kotlin": [".kt"]})

write_dict("c_cpp", "c_cpp", [
    {"id": "nolint", "regex": r"//\s*NOLINT\b", "languages": ["c", "cpp"],
     "positive": "int x = f(); // NOLINT(cppcoreguidelines-*)", "negative": "int x = f(); // обычный"},
    {"id": "nolintnextline", "regex": r"//\s*NOLINTNEXTLINE\b", "languages": ["c", "cpp"],
     "positive": "// NOLINTNEXTLINE(misc-*)", "negative": "// NOLINT — тут нет"},
    {"id": "pragma_warning", "regex": r"#pragma warning\s*\(", "languages": ["c", "cpp"],
     "positive": "#pragma warning(disable : 4996)", "negative": "#pragma once"},
], lang_ext={"c": [".c", ".h"], "cpp": [".cpp", ".cc", ".hpp", ".hxx"]})
