---
name: job-apply
description: Drive the user's own logged-in browser to screen jobs and apply on Boss Zhipin, Liepin, 51job and Zhaopin. Local-first, nod-first, draft-only. Use when the user asks to screen jobs, apply to jobs, check job-site replies, or set up automated job hunting on their own machine.
---

# job-apply

An AI agent drives the user's **own browser, own IP, own logged-in accounts** to
screen jobs and submit applications on Chinese job platforms. The agent never
logs in for the user, never runs a datacenter browser, and never sends anything
without the user's explicit nod.

## The principle: the user's own browser

The agent drives the browser the user already uses, on the user's own
computer, under the user's own IP and login. The user never hands over a
password and never logs in on anyone else's server; to the job site it is
simply the user browsing. Protect this: never move the browsing to a cloud
machine, never perform logins, and keep a human pace.

## Architecture

```
User's PC
  Chrome / Edge (user's own profile, already logged in to job sites)
    └─ Browser bridge extension (Antigravity Browser Bridge v1.4.1)
         └─ HTTP API on 127.0.0.1:9224  ← agent talks here, localhost only
Agent (any local runtime: Claude Code, Codex, local DeepSeek harness, ...)
  └─ reads SKILL.md + references/*.md, drives the bridge, follows governance.md
```

Local mode is the default: agent and browser run on the same machine, no
network exposure, no relay, no account handed to anyone. Agents that run in
a vendor's cloud (e.g. Meta Muse) cannot reach `127.0.0.1` on the user's PC
and need the advanced remote mode in `references/bridge.md` — with all of
its security rules. Plain web chats (DeepSeek/豆包/千问 web) cannot run this
skill at all. See README "Which AI can run this skill". A cloud relay mode
(bridge dials out via websocket) is a future paid tier and is **not** part
of this skill.

## Setup (local mode, 6 steps — same as README)

1. **Install the bridge** — `scripts/setup-local.ps1` (Bridge v1.4.1, audited
   commit `60c4c05`; v2.x has a different API and is not supported). Manual
   install: `references/bridge.md`.
2. **Load the extension** (`chrome://extensions` → Developer mode → Load
   unpacked → the bridge's `extension` folder).
3. **Check** `GET http://127.0.0.1:9224/health` shows `extension_connected`.
4. **Log in, in your own browser.** Open Boss, Liepin, 51job, Zhaopin and log
   in yourself. The agent never sees your password and never performs a
   login. Account registration and login **always** run on the user's own
   devices — never from a cloud VM or datacenter IP, or the account risks a
   ban.
5. **Set criteria.** Copy `criteria.example.yaml` to `criteria.yaml` and fill
   in target titles, city, minimum salary, direction and exclusions. The
   agent screens against this file and nothing else.
6. **Run `scripts/selftest.py`** (read-only). Proceed only when it passes.

Optional but recommended: run the browser in a **dedicated profile** for the
agent, so its tabs never fight with your daily browsing.

## Workflow

Read `references/governance.md` first — it is binding, not advisory.

1. **Verify.** `GET /tabs` fresh (tab IDs go stale overnight). Check the
   bridge is up, then verify each platform's login state programmatically
   (page/API), never from memory or from the user saying "I'm logged in".
   Liepin login expires overnight — expect to re-verify every run.
2. **Collect.** One keyword at a time, per platform adapter
   (`references/platform-*.md`). Collect raw cards. Do not apply during
   collection.
3. **Screen.** Filter by criteria (title, city, salary floor, direction,
   exclusions). The list page is only a rough filter — **the job detail page
   is the only source of truth** for location, industry and hard requirements.
   Open the detail page before any decision to apply.
4. **Shortlist.** Present a shortlist (one line per job: platform, title,
   company, salary, why it fits). Wait for the user's nod. **No application
   is submitted before the user approves the list.**
5. **Apply.** Apply only to approved items, one at a time, with the
   platform's own apply control. Slow down between actions (see each adapter
   for throttle rules). On every platform the apply action itself sends the
   platform's default greeting and/or the online resume — the shortlist nod
   covers exactly that (`governance.md` rule 1.5); custom text needs its own
   confirmation.
6. **Verify.** After applying, reconcile every count against the platform's
   actual submission records (e.g. 51job 我的申请, Zhaopin 投递记录) **before
   reporting any number**. A button changing state is not proof. "I clicked"
   is not proof. Only the platform's own record counts.
7. **Monitor replies.** On a schedule the user agrees (e.g. morning and
   evening), scan each platform's message center for new HR replies. **Draft
   replies only — the user confirms before anything is sent.** Flag replies
   from already-applied-but-now-excluded jobs as excluded-category; do not
   chase them.

## Non-negotiable rules

- **Nod-first.** No application without the user's approval of that exact
  shortlist. No exceptions. The nod covers the platform's default apply
  action (default greeting / resume) for those items.
- **Draft-only.** Custom text — HR and headhunter replies, personalised
  greetings — is drafted, never sent, until the user confirms the exact text.
- **Platform blocking on request only.** Blocking a company inside a
  platform changes account settings; do it only when the user asks.
- **Never fabricate.** Rewrite a resume to match a JD, never invent
  experience, numbers or credentials. A customised resume version is shown to
  the user and used only after their nod; the original is snapshotted before
  editing and restored after applying.
- **Verify before reporting.** Login state and application counts are checked
  against the live page or API every time. Never report from memory.
- **Respect exclusions.** The user's exclusion list is a hard filter, not a
  suggestion. Borderline cases go to the user for a call, never auto-apply.
- **Bridge stays local.** The bridge HTTP API has no auth in v1.4.1. Bind it
  to `127.0.0.1` only. Never port-forward it, never expose it to a LAN or
  tailnet, stop it when idle. See `references/bridge.md` for the full warning.
- **Dedupe by JD text, not title.** Same job reposted under different titles
  is one job.

## Files

| File | What it is |
| --- | --- |
| `SKILL.md` | This file: workflow and rules. |
| `README.md` | Public introduction, setup, roadmap. |
| `references/bridge.md` | Bridge API, local vs remote mode, security. |
| `references/governance.md` | Nod-first, draft-only, exclusions, verification. |
| `references/platform-boss.md` | Boss Zhipin adapter. |
| `references/platform-liepin.md` | Liepin adapter. |
| `references/platform-51job.md` | 51job adapter. |
| `references/platform-zhaopin.md` | Zhaopin adapter. |
| `scripts/bridge.py` | Minimal bridge client (localhost default). |
| `scripts/setup-local.ps1` | One-click local install (Path A): Python + websockets + Bridge v1.4.1 download + start script + health check. Run once; then load the extension by hand. |
| `scripts/selftest.py` | Read-only self-test through the bridge: health, tabs, login, one-keyword collection per platform. Never applies. |
| `scripts/prepublish_check.py` | Maintainers: privacy scan before any public release (IPs, phone/ID numbers, keys, job IDs, local deny-list). |
| `scripts/export_public.py` | Maintainers: first public release only — clean, history-free export (runs the privacy scan). |
| `scripts/sync_public.py` | Maintainers: every later release — mirror into a clone of the public repo as one normal commit (runs the privacy scan, never pushes). |
| `criteria.example.yaml` | Screening criteria template. |
| `TESTING.md` | How to test with another AI before publishing. |
