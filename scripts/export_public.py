"""Export a clean copy of the skill for the PUBLIC repository.

The working repository is private and its git history and Issues contain
personal data. The public repository must therefore be created from a fresh
copy with NO history:

  python scripts/export_public.py ../job-apply-skill-public

What it does:
  1. copies only the files tracked by git (nothing ignored, no .git)
  2. runs scripts/prepublish_check.py on the copy and stops if anything is found
  3. creates a brand-new git repository there with a single initial commit

It never pushes. Review the copy, then create the public GitHub repository and
push it yourself (or ask your agent to, after you have reviewed it).
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Files that belong to the private workspace only.
EXCLUDE = {".prepublish-denylist"}


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/export_public.py <empty-target-dir>")
    dest = os.path.abspath(sys.argv[1])
    if os.path.exists(dest) and os.listdir(dest):
        sys.exit(f"target {dest} exists and is not empty - pick an empty or new folder")
    if dest.startswith(ROOT + os.sep):
        sys.exit("target must be outside this repository")

    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                           text=True, check=True).stdout.splitlines()
    os.makedirs(dest, exist_ok=True)
    n = 0
    for rel in files:
        if os.path.basename(rel) in EXCLUDE:
            continue
        src = os.path.join(ROOT, rel)
        if not os.path.isfile(src):
            continue
        out = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copy2(src, out)
        n += 1
    print(f"copied {n} files to {dest}")

    check = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "prepublish_check.py"), dest])
    if check.returncode != 0:
        sys.exit("privacy check failed - fix the findings in the PRIVATE repo, then export again. "
                 f"(the partial copy is left in {dest}; delete it)")

    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=dest, check=True)
    subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "Initial public release"], cwd=dest, check=True)
    print(f"\nclean repository ready at {dest} (1 commit, no history). Review it, then push it to the public repo.")


if __name__ == "__main__":
    main()
