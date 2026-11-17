# Генератор fixtures для правил Semgrep (позитивные/негативные по rule id).
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEM = ROOT / "tooling" / "semgrep"

Q17 = {
    "q17-requests-get-no-timeout": (
        "import requests\nr = requests.get(url)\n",
        "import requests\nr = requests.get(url, timeout=(3, 10))\n"),
    "q17-requests-post-no-timeout": (
        "import requests\nr = requests.post(url, data=payload)\n",
        "import requests\nr = requests.post(url, data=payload, timeout=10)\n"),
    "q17-requests-request-no-timeout": (
        "import requests\nr = requests.request('GET', url)\n",
        "import requests\nr = requests.request('GET', url, timeout=10)\n"),
    "q17-httpx-no-timeout": (
        "import httpx\nr = httpx.get(url)\n",
        "import httpx\nr = httpx.get(url, timeout=10)\n"),
    "q17-urlopen-no-timeout": (
        "from urllib.request import urlopen\nr = urlopen(url)\n",
        "from urllib.request import urlopen\nr = urlopen(url, timeout=10)\n"),
    "q17-socket-create-connection-no-timeout": (
        "import socket\ns = socket.create_connection((host, port))\n",
        "import socket\ns = socket.create_connection((host, port), timeout=10)\n"),
    "q17-psycopg-connect-no-timeout": (
        "import psycopg\nc = psycopg.connect(dsn)\n",
        "import psycopg\nc = psycopg.connect(dsn, connect_timeout=10)\n"),
    "q17-subprocess-run-no-timeout": (
        "import subprocess\nr = subprocess.run(['ls'])\n",
        "import subprocess\nr = subprocess.run(['ls'], timeout=30)\n"),
}

Q18 = {
    "q18-recursion-no-depth": (
        "def walk(node):\n    return walk(node.next)\n",
        "def walk(node, depth):\n    if depth > 64:\n        raise ValueError\n    return walk(node.next, depth + 1)\n"),
    "q18-infinite-read-loop": (
        "while True:\n    data = stream.read(1024)\n",
        "while True:\n    data = stream.read(1024)\n    if not data:\n        break\n" if False else "data = stream.read(1024)\n"),
    "q18-infinite-recv-loop": (
        "while True:\n    packet = sock.recv(4096)\n",
        "packet = sock.recv(4096)\n"),
    "q18-infinite-readline-loop": (
        "while True:\n    line = f.readline()\n",
        "line = f.readline()\n"),
}


def w(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


for pack, table in (("q17-timeouts", Q17), ("q18-recursion", Q18)):
    rules_path = SEM / pack / "python" / "rules.yaml"
    ids = [r["id"] for r in yaml.safe_load(rules_path.read_text(encoding="utf-8"))["rules"]]
    assert set(ids) == set(table), (pack, set(ids) ^ set(table))
    for rid, (pos, neg) in table.items():
        w(SEM / "fixtures" / pack / f"positive_{rid}.py", pos)
        w(SEM / "fixtures" / pack / f"negative_{rid}.py", neg)
    print(f"{pack}: правил {len(ids)}, fixtures {len(table) * 2}")
