"""Pre-publish privacy scan. Run before every public release.

Scans the files that would be published for things that must never go public:
tailnet/private IPs, phone numbers, ID-card numbers, e-mail addresses, API
keys / auth keys / tokens, Windows user paths, recruitment-platform job IDs,
and any extra terms you list in a local deny-list file.

Usage:
  python scripts/prepublish_check.py            # scan files tracked by git
  python scripts/prepublish_check.py <dir>      # scan every file under <dir>

Extra terms (your name, your Windows user name, company names you applied to
...): put one per line in `.prepublish-denylist` at the repo root. That file
is git-ignored and is never published.

Exit code 0 = clean, 1 = findings (review every one before publishing).
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DENYLIST = os.path.join(ROOT, ".prepublish-denylist")
SKIP_FILES = {"LICENSE", "NOTICE"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".pdf"}

# Placeholders and documentation examples that are allowed.
ALLOW = [
    re.compile(r"100\.64\.0\.(10|0)"),        # example IP / CGNAT range in docs
    re.compile(r"100\.64\.0\.0/10"),
    re.compile(r"noreply@anthropic\.com"),
    re.compile(r"hr@51job\.com"),
    re.compile(r"<[^>]*>"),                    # <placeholders>
]

PATTERNS = [
    ("tailnet IP", re.compile(r"\b100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}\b")),
    ("private IP", re.compile(r"\b(192\.168|10)\.\d{1,3}\.\d{1,3}(\.\d{1,3})?\b")),
    ("CN mobile number", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
    ("CN ID-card number", re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)")),
    ("e-mail address", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    ("Tailscale auth key", re.compile(r"tskey-[\w-]{12,}")),
    ("GitHub token", re.compile(r"\b(ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{10,}")),
    ("API key", re.compile(r"\bsk-[A-Za-z0-9]{16,}")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("Windows user path", re.compile(r"C:\\Users\\(?!<|Master\b|you\b|<you>)[^\\\s`\"']+", re.I)),
    ("Boss job ID", re.compile(r"\b[0-9a-f]{16}(?=[0-9A-Za-z_-]{10,14}\b)(?=[0-9a-z_-]*[A-Z_])[0-9A-Za-z_-]{10,14}\b")),
    ("Zhaopin job number", re.compile(r"\bCC[L]?\d{8,}J\d{8,}\b")),
    ("Liepin job page", re.compile(r"/a/\d{8}\.shtml")),
]


def files_to_scan(target):
    if target:
        for dp, dn, fn in os.walk(target):
            dn[:] = [d for d in dn if d != ".git"]
            for f in fn:
                yield os.path.join(dp, f)
        return
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    for rel in out.stdout.splitlines():
        yield os.path.join(ROOT, rel)


def load_denylist():
    if not os.path.exists(DENYLIST):
        return []
    with open(DENYLIST, encoding="utf-8") as f:
        return [t.strip() for t in f if t.strip() and not t.startswith("#")]


def allowed(text):
    return any(a.fullmatch(text) for a in ALLOW)


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    deny = load_denylist()
    hits = 0
    for path in files_to_scan(target):
        name = os.path.basename(path)
        if name in SKIP_FILES or os.path.splitext(name)[1].lower() in SKIP_EXT:
            continue
        if name == ".prepublish-denylist":
            print(f"[FAIL] {path}: the deny-list file itself must not be published")
            hits += 1
            continue
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        rel = os.path.relpath(path, target or ROOT)
        for no, line in enumerate(lines, 1):
            for label, rx in PATTERNS:
                for m in rx.finditer(line):
                    if allowed(m.group(0)):
                        continue
                    print(f"[FAIL] {rel}:{no}: {label}: {m.group(0)}")
                    hits += 1
            for term in deny:
                if term in line:
                    print(f"[FAIL] {rel}:{no}: deny-list term: {term}")
                    hits += 1
    if not deny:
        print("[WARN] no .prepublish-denylist found - add your name, Windows user name, "
              "and companies you applied to, one per line, then rerun.")
    print(f"\n{hits} finding(s).", "Clean." if hits == 0 else "Review every finding before publishing.")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
