# job-apply skill

[中文](README.md) · English

**Let an AI apply to jobs for you — from your own browser, under your own
login, so job sites see a normal person, not a bot.**

The AI drives the browser you already use: **your own computer, your own IP,
your own login**. You never hand your password to anyone and never log in on
someone else's server. To the job site, it is simply you, browsing normally.

## Before you start: check if you can use this

Don't download yet. Spend 30 seconds checking whether your AI can run this
skill, or you'll waste your time.

**One-sentence test: can your AI run a command on the same PC where you are
logged in to the job sites?**

- **Yes → it works.** Pick a path below.
- **No (web chat only) → don't download.** Web-only chats (DeepSeek, Doubao,
  Qwen web, etc.) cannot run commands or reach your PC. This skill can't
  help you.

| Your AI | Path | Steps left after installing the skill |
| --- | --- | --- |
| Local desktop agent (WorkBuddy, OpenClaw, Manus Desktop, Codex, Claude Code) | A. Local bridge | 6 steps |
| Cloud agent (Meta Muse, free tier available) | B. Bridge + tunnel | 12 steps |
| Web chat only (DeepSeek / Doubao / Qwen web) | Not supported | Don't download |

This skill is for free AI users: pick A first (6 steps — simpler and safer
than B). Only use B if your AI runs in the cloud. Detailed steps are in "Setup" and
`references/bridge.md`; the full platform table is in "Which AI can run this
skill" below.

## What it does

- Screens jobs on **Boss Zhipin, Liepin, 51job and Zhaopin** against your
  criteria (title, city, minimum salary, direction, exclusions).
- Shows you a shortlist. **You nod, then it applies — never before.** Your
  nod covers each platform's default apply action (default greeting and/or
  online resume); any custom text needs its own confirmation.
- Verifies every application against the platform's own submission records
  before reporting any number.
- Scans for HR replies on a schedule and **drafts** responses for you to
  approve. It never sends a message on your behalf.

## What it never does

- Never logs in for you, never sees your password, never registers an account.
- Never applies to a job you did not approve.
- Never sends custom text to an HR or headhunter without your confirmation.
- Never invents resume content — it rewrites, never fabricates.
- Never exposes your browser to the network. The bridge binds to localhost
  only.

## Which AI can run this skill / 哪些 AI 能用

### Quick guide: pick your path / 按你用的 AI 选路径

| Your AI / 你用的 AI | Path / 路径 | Extra setup / 额外步骤 |
| --- | --- | --- |
| **Local desktop agent** — WorkBuddy, OpenClaw, Manus Desktop, Codex (CLI / desktop), Claude Code CLI | **A. Local bridge / 本地桥** | Install the bridge only. No Tailscale. / 只需装 bridge，不需要 Tailscale。 |
| **Cloud agent** — Meta Muse (free tier available / 有免费档) | **B. Bridge + Tailscale / 桥 + 隧道** | Bridge + Tailscale + SSH server on the PC; the agent connects with an SSH forward (bridge.md Option 1). Most steps. / 步骤最多：bridge + Tailscale + 电脑开 SSH，见 bridge.md Option 1。 |
| **Web chat only** — DeepSeek / 豆包 / 千问 web | Not supported / 不支持 | Can't run commands. Paste job lists in for advice only. / 只能贴内容请它判断。 |

Free users: path A with a free/low-cost local agent (OpenClaw, WorkBuddy) is
simpler and safer than path B. Use path B only if your agent lives in the
cloud.
免费用户：优先选 A（OpenClaw、WorkBuddy 等本地智能体），比 B 简单也更安全；只有 AI 跑在
云端（如 Muse）才需要走 B。

### Details

The skill needs an AI agent that can (1) read `SKILL.md` and the reference
files, and (2) send HTTP requests to the browser bridge. The bridge listens on
`127.0.0.1:9224` of **your** PC, so where the agent runs decides how it
connects.

本 skill 需要一个能读取 skill 文件、并能向浏览器桥（bridge）发 HTTP 请求的 AI
智能体。bridge 在你自己电脑的 `127.0.0.1:9224` 上监听，所以关键看 AI 跑在哪里。

| Platform / 平台 | Where the agent runs / 运行位置 | Mode / 模式 | Notes / 说明 |
| --- | --- | --- | --- |
| **WorkBuddy** (Tencent / 腾讯) | Your PC / 你的电脑 | Local / 本地 | **Verified 2026-11-09** (WorkBuddy v5.9.3): selftest 10/10, plus one full round on Boss — collect → detail-page check → user nod → apply → reconciled against the message-centre receipt (1 job). Applying on the other three platforms is not yet tested. Desktop agent; OpenClaw-compatible skills; can pick DeepSeek, Hunyuan, Kimi, GLM etc. Phone/WeChat remote control still runs on your PC. Check current pricing. / **已实测**：自检 10/10，BOSS 完整投递一轮（1 个岗位）。 |
| **OpenClaw** (open source / 开源) | Your PC / 你的电脑 | Local / 本地 | Free software; bring any model (DeepSeek API, local Ollama, …) — model usage may cost. / 软件免费，模型可接 DeepSeek API 或本地模型（API 可能收费）。 |
| **Manus Desktop** | Your PC / 你的电脑 | Local / 本地 | Local terminal execution with per-command approval. Check pricing. / 本地执行命令，逐条授权。 |
| **Claude Code (installed on your PC, incl. the Claude desktop app's Code tab in the "this computer" environment)** | Your PC / 你的电脑 | Local / 本地 | **Verified 2026-11-09**: selftest passed on the PC (9 PASS / 1 WARN / 0 FAIL, Chrome 157, 9 tabs). Paid Claude plan. Must run natively on Windows, not inside WSL's default network. Claude desktop *chat* is not the target: its shell runs in an isolated VM and cannot reach a local bridge, and it has its own Chrome plugin to drive the browser, so it does not need the bridge; it is also a paid product, while this skill is for free AI users. / **已实测**；需付费订阅。桌面版聊天对话不在目标内：它自带 Chrome 插件就能操作浏览器，不需要搭桥；且它是付费产品，本 skill 面向免费 AI 用户。 |
| **Codex (CLI / desktop app)** | Your PC / 你的电脑 | Local / 本地 | **Verified 2026-11-09:** ran `selftest.py` locally, 9 PASS / 1 WARN / 0 FAIL — bridge reachable, all four platforms collectable. Usually needs a ChatGPT plan. Its sandbox may block network by default — allow it to reach the bridge. / **已实测 2026-11-09**：本地跑 selftest 通过（9 通过 / 1 警告 / 0 失败），bridge 连通、四个站都能抓岗位。一般需 ChatGPT 订阅；默认沙箱可能禁网，需放开。 |
| **Meta Muse** | Meta's cloud machine / Meta 云端虚拟机 | **Remote / 远程** | **Verified 2026-11-09** (selftest passed). Free tier available. The Muse runtime is already on your tailnet; Muse reaches the bridge with an **SSH local forward** over the tailnet — no port opened for the bridge (`references/bridge.md` → Option 1). Needs OpenSSH Server on the PC. / **已实测**。有免费档。Muse 运行环境已在 tailnet 中，通过 SSH 本地转发连 bridge，不对外开 9224 端口；电脑需开 OpenSSH 服务。 |
| **Claude Duet** | Anthropic's cloud / 云端 | Not supported / 暂不支持 | Cloud-only agent working through connectors; US-only Pro/Max research preview; no route to a bridge on your PC. / 纯云端，靠连接器工作，仅美国 Pro/Max 预览，连不到你电脑上的 bridge。 |
| **Web chat** (DeepSeek, 豆包, 千问, Kimi web…) | Vendor's servers / 厂商服务器 | Not supported / 不支持 | Cannot execute commands or reach your PC. You can still paste `scripts/selftest.py` output or job lists into a web chat for screening advice, but it cannot apply. / 网页聊天无法执行命令或连到你电脑；只能把脚本输出贴进去让它帮你判断，不能自动投递。 |

Rule of thumb / 判断标准: **if the AI can run a command on the same PC as
your logged-in browser, it can use this skill in local mode.** Cloud agents
need remote mode, which widens exposure — prefer a local agent.
**AI 能在你登录招聘网站的那台电脑上执行命令，就能用本地模式。** 云端智能体只能走远程
模式，风险更高，优先选本地智能体。

Pricing and availability change often; check each vendor before relying on
a free tier. Only rows marked **Verified** were tested end-to-end; the others follow from
where the agent runs and are untested. Platforms not listed are untested, not
unsupported.
只有标「已实测」的行做过完整测试，其余是按运行位置推断，未实测。

## Setup (6 steps, local mode)

1. **Install the bridge (one click).** Right-click `scripts/setup-local.ps1`
   → "Run with PowerShell". It installs Python (only if missing),
   `websockets`, downloads Bridge v1.4.1, creates `start-bridge.bat` and
   starts the server. To install by hand, see the Install section in
   `references/bridge.md`.
2. **Load the browser extension.** Open `chrome://extensions`
   (Edge: `edge://extensions`), enable Developer mode, click "Load unpacked"
   and pick the `extension` folder the script prints.
3. **Check the bridge is connected.** Open `http://127.0.0.1:9224/health`;
   it should show `extension_connected: true`.
4. **Log in, in your own browser.** Open the four job sites and log in
   yourself. The agent never touches your credentials.
5. **Set criteria.** Copy `criteria.example.yaml` to `criteria.yaml` and fill
   in titles, city, salary floor and exclusions (or let your AI ask you and
   fill it in).
6. **Run the self-test.** `python scripts/selftest.py` — read-only, never
   applies. Start using the skill once everything passes.

Before each later run, just double-click `start-bridge.bat`; close its window
when done.

Then point any local AI agent (Claude Code, Codex, a local DeepSeek harness,
…) at this skill and say: "screen jobs for today."

No Tailscale, no relay, no server. Everything runs on your machine.

## How it works

```
You ──► criteria.yaml (titles, city, salary, exclusions)
Agent ──► bridge API on 127.0.0.1:9224 ──► your Chrome/Edge (already logged in)
Agent ──► collect → screen (detail page is truth) → shortlist ──► YOU NOD ──► apply
Agent ──► verify against platform records ──► report real numbers
Agent ──► scan replies on schedule ──► draft only, you confirm before sending
```

Per-platform mechanics (including anti-crawler notes and every pitfall found
in a week of live runs) live in `references/platform-*.md`. Governance —
nod-first, draft-only, verification-before-reporting — lives in
`references/governance.md` and is binding.

## Platforms

| Platform | Adapter notes |
| --- | --- |
| Boss Zhipin | Read the page's own Vue job list (plain salaries), avoid direct API calls (code 37), login wall on deep links |
| Liepin | Login may expire overnight, `/job/` vs `/a/` pages, 聊一聊 auto-sends a greeting, resume via 发简历 |
| 51job | Direct search URL first (homepage box as fallback), jobId from `sensorsdata`, apply navigates to `applysuccess.php` |
| Zhaopin | Read `window.__INITIAL_STATE__.positionList`, volatile lists, 立即投递 sends resume + greeting |

## Risk warnings / 风险提示

- **Automation may violate platform Terms of Service.** Job sites may
  restrict or ban accounts that use automation. Use at your own risk. This
  skill does not bypass logins, captchas or paywalls, and it will not help
  you apply to jobs you are not qualified for.
- **Liepin has risk controls.** Opening many job pages in rapid succession
  triggers a security verification (graphic CAPTCHA). When it appears the
  skill stops and you solve it manually. Pace your actions; do not retry
  in a loop.
- **BOSS throttles direct API calls.** High-frequency API calls return
  code 37 ("环境存在异常"). This skill reads the page's own Vue job list
  instead. Do not hammer the API.
- **Account-restriction risk.** If a platform flags the account,
  applications and replies may stop working. Keep a human pace (slow down
  between actions), do not submit many applications in a burst, and stop
  when a platform throttles you.
- **The bridge has no auth (v1.4.1).** Bind it to `127.0.0.1` only, never
  expose it to a LAN or the internet, stop it when idle. See the Security
  section in `references/bridge.md`.

## Roadmap

- **Cloud relay mode (later, paid tier):** bridge dials out via websocket so
  the agent can run in the cloud. Not in this skill.
- **NexusBrowser:** the bridge's successor, adds token auth. Candidate
  upgrade for the bridge layer.
- **Resume customisation:** tailor a resume to a target JD after screening —
  snapshot original, edit, apply, archive the version used, restore original.
  Rewrite only, never fabricate; each version used only after the user's nod.

## Status

Built from a week of live runs (November 2026) driving a real logged-in
browser. Every adapter note comes from a real pitfall, not from documentation.
Open items are marked **unverified** in the references — they are honest gaps,
not solved problems.

## License

Apache-2.0. Free and open source. See `LICENSE` and `NOTICE`. The "Lazy Worker" name and logo are not licensed (License section 6).

The Antigravity Browser Bridge that this skill downloads is a separate third-party project, also Apache-2.0.

## Disclaimer

Use your own accounts, on your own machine, at a human pace. Respect each
platform's terms and rate limits. This skill does not bypass logins, captchas
or paywalls, and it will not help you apply to jobs you are not qualified for.
