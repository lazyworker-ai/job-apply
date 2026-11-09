"""Sync the private working repo into a clone of the PUBLIC repository.

Use this for every release after the first one (the first was created with
export_public.py). It keeps the public repo's own, normal history and never
carries over the private history or Issues.

  git clone https://github.com/lazyworker-ai/job-apply ../job-apply
  python scripts/sync_public.py ../job-apply -m "Describe what changed"

What it does:
  1. checks the target is a git clone whose working tree is clean
  2. mirrors the files tracked by git here into it: adds/updates files,
     deletes files that no longer exist here (never touches .git)
  3. runs scripts/prepublish_check.py on the target and stops if anything
     is found
  4. shows the change summary and creates ONE normal commit

It never pushes and never force-pushes. Review `git -C <target> show`, then
push with a plain `git push`.
"""
import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUDE = {".prepublish-denylist"}


def git(cwd, *args, capture=True):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=capture, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="path to a clone of the public repository")
    ap.add_argument("-m", "--message", required=True, help="commit message for the public repo")
    a = ap.parse_args()

    dest = os.path.abspath(a.target)
    if not os.path.isdir(os.path.join(dest, ".git")):
        sys.exit(f"{dest} is not a git clone - clone the public repo first")
    if dest == ROOT or dest.startswith(ROOT + os.sep):
        sys.exit("target must be outside this repository")
    if git(dest, "status", "--porcelain").strip():
        sys.exit(f"{dest} has uncommitted changes - commit, stash or discard them first")

    src_files = {f for f in git(ROOT, "ls-files").splitlines()
                 if os.path.basename(f) not in EXCLUDE and os.path.isfile(os.path.join(ROOT, f))}
    dst_files = set(git(dest, "ls-files").splitlines())

    for rel in sorted(src_files):
        out = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, rel), out)
    for rel in sorted(dst_files - src_files):
        git(dest, "rm", "-q", "--", rel)

    check = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "prepublish_check.py"), dest])
    if check.returncode != 0:
        git(dest, "checkout", "-q", "--", ".")
        git(dest, "clean", "-fdq")
        git(dest, "reset", "-q", "--hard")
        sys.exit("privacy check failed - target restored. Fix the findings in the PRIVATE repo and sync again.")

    git(dest, "add", "-A")
    if not git(dest, "status", "--porcelain").strip():
        print("public repo is already up to date - nothing to commit.")
        return
    print(git(dest, "diff", "--cached", "--stat"))
    git(dest, "commit", "-q", "-m", a.message)
    print(f"committed in {dest}: {git(dest, 'log', '--oneline', '-1').strip()}")
    print("review with:  git -C", dest, "show --stat   then push with a plain:  git push")


if __name__ == "__main__":
    main()
