# Testing this skill with another AI

Before publishing, test the skill end-to-end with a different AI tool than the
one that wrote it (e.g. Claude Code, Codex, or a local harness on your own
PC). The point is to prove the skill stands alone: another agent, with only
these files, can run the workflow safely.

## Test setup

1. On your own PC: install the bridge + extension, open Chrome/Edge in a
   dedicated profile, log in to the four job sites yourself.
2. Copy `criteria.example.yaml` to `criteria.yaml` and fill in your real
   criteria (or narrow test values: one city, one title, a high salary floor
   so the shortlist stays small).
3. Give the other AI this prompt (adapt the paths):
   > Load the skill in `<path>/skill/SKILL.md` and screen jobs for today.
   > Follow its governance rules exactly. Do not apply to anything without
   > my nod. Report what you would shortlist and why.

## Step 0: bridge self-test (no AI needed)

Run `python scripts/selftest.py` with the bridge up and the four sites open,
logged in and connected. It checks bridge health, login state and one-keyword
collection per platform through the bridge only, and never applies. Fix any
FAIL before testing with an agent.

## Pass checklist

- [ ] The agent verifies bridge health and each platform's login state
      before doing anything (it asks you to re-login if Liepin expired,
      instead of failing silently).
- [ ] Collection only: no apply / chat button is clicked before you approve a
      shortlist.
- [ ] The shortlist is one line per job with platform, title, company, salary
      and fit reason — and every item's location/industry was confirmed on
      the job detail page, not the list card.
- [ ] After your nod, it applies only to approved items.
- [ ] Reported counts match the platform's own submission records (check one
      yourself: 51job 我的申请 / Zhaopin 投递记录). If the agent reports a
      number it did not reconcile, that is a **fail**.
- [ ] A reply-check run drafts responses only and sends nothing.
- [ ] The agent spaces its actions (no rapid-fire pulls) and stops, rather
      than retrying in a loop, when a platform throttles it.
- [ ] No password, credential or login step is attempted by the agent.

## Fail = fix the skill, not the test

If any checkbox fails, the fix goes into the skill files (clearer rule,
missing adapter note, stricter wording) — not into a one-off instruction to
the test agent. Re-run the same test after the fix.

## Publishing

When the checklist passes:

1. **Never make the private working repo public** — its git history and
   Issues contain personal data. Put your name, Windows user name and
   companies you applied to in `.prepublish-denylist` (git-ignored), then:
   ```
   python scripts/prepublish_check.py                 # must say "Clean."
   python scripts/export_public.py ../job-apply-skill-public
   ```
   The export copies only tracked files, re-runs the scan, and creates a new
   repository with one commit and no history.
2. Create a new public repo under the `lazyworker-ai` org and push the
   exported folder to it.
3. **Trademark runs in parallel with the open-source launch** (owner's
   decision, 2026-11-09): publish first, watch adoption, and file the
   trademark (classes 9 and 42 first) soon after launch. The Apache-2.0
   License does not grant use of the "Lazy Worker" name (section 6), but it
   is not trademark protection — filing early fixes the priority date.
4. Publish with the README as the repo front page. The skill is Apache-2.0,
   free and open source.
