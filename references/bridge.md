# Bridge (bridge-remote module)

How the agent reaches the user's browser, and how to keep that channel safe.

## The bridge

The skill drives the browser through the **Antigravity Browser Bridge**
(v1.4.1; successor: NexusBrowser, which adds token auth). The bridge is a small
local server plus a browser extension:

- WebSocket: `127.0.0.1:9223`
- HTTP API: `127.0.0.1:9224`

The agent uses the HTTP API. The browser must be running with the extension
connected, and the target tab must be "connected" (the extension needs one
click — "connect current tab" — per tab before the bridge can drive it).

## Install

Get the bridge running before you use the skill. **Install v1.4.1 — it is
the only version this skill is verified against.**

### One-click install (recommended): `scripts/setup-local.ps1`

The fastest path. Download this skill, then run the script once (right-click
-> "Run with PowerShell", or `powershell -NoProfile -ExecutionPolicy Bypass
-File .\scripts\setup-local.ps1`). It installs Python 3.12 if missing,
installs `websockets`, downloads Bridge v1.4.1 (pinned to the audited
commit `60c4c05`), creates `start-bridge.bat` (runs `server\server.py`),
starts the server and checks it answers on `127.0.0.1:9224`. After it
finishes, you only need to load the extension (below) and log in to the four
job sites — that is the whole install. The script is for the **local** path
(Path A); it installs nothing that talks to the network except the bridge
itself on `127.0.0.1`. If you prefer to do every step by hand, use the
manual install below instead.

### Download addresses / 下载地址

| Component | Address / 地址 | Notes |
| --- | --- | --- |
| Bridge v1.4.1 (verified / 已实测) | https://github.com/AshenJyy/browser-bridge/releases/tag/v1.4.1 | Release page. Download the source ZIP (`Source code (zip)`) or clone and check out the tag. The audited commit is `60c4c05` (two small daemon fixes after the v1.4.1 tag). No packaged installer — install from source below. / 发布页，下载源码 ZIP 或克隆后切到该标签。已审计提交为 `60c4c05`（v1.4.1 标签之后的两个小修复）。没有一键安装包，按下面步骤从源码安装。 |
| Bridge v2.0.3 (not supported yet / 暂不支持) | https://github.com/AshenJyy/browser-bridge/releases/tag/v2.0.3 | Packaged ZIP installer, token auth, Edge. **Different API — this skill's scripts do not work with it.** See "Why not v2" below. / 带打包安装程序、令牌认证，面向 Edge。**接口不同，本 skill 的脚本暂不支持**，见下文。 |
| Tailscale (remote mode only / 仅远程模式) | https://tailscale.com/download | Windows: download and run the installer — one-click. Only needed for remote mode (Path B). Local mode needs no Tailscale. / Windows 下下载后直接运行安装程序即可（一键安装）。只有远程模式（路径 B）需要，本地模式不需要。 |

### v1.4.1 — manual install from source (Windows, fallback)

1. Install Python 3.11+ from https://www.python.org/downloads/ (tick
   "Add python.exe to PATH" during setup).
2. Install the only dependency:
   ```powershell
   pip install websockets
   ```
   Verified with websockets 17.3; newer versions are untested.
3. Download the bridge source from
   https://github.com/AshenJyy/browser-bridge/releases/tag/v1.4.1
   (the `Source code (zip)` asset) and extract it, e.g. to
   `D:\antigravity-browser-bridge-main`. For the exact audited version,
   clone and check out commit `60c4c05` instead:
   ```powershell
   git clone https://github.com/AshenJyy/browser-bridge.git
   cd browser-bridge
   git checkout 60c4c05
   ```
   Do not take a newer commit without re-auditing.
4. Load the browser extension. In Chrome, open `chrome://extensions`
   (Edge: `edge://extensions`), enable Developer mode, choose "Load
   unpacked" and select the `extension` folder inside the bridge source.
5. Start the bridge server (keep the window open — foreground, visible,
   never a silent background service):
   ```powershell
   cd D:\antigravity-browser-bridge-main\server
   python server.py
   ```
   Run **`server.py`** — `cli.py` is the command-line *client* (`cli.py
   status`, `cli.py tabs` …) and exits with an error when run without a
   subcommand. The repo's own `start_server.bat` runs `py server.py` and is
   the closest thing to one-click start: double-click it before a run,
   close the window when done.
6. Verify. Open http://127.0.0.1:9224/health in a browser — it should
   answer with `extension_connected: true` once the extension is
   connected. Then run the skill's self-test:
   ```powershell
   python scripts/selftest.py
   ```
   Fix any FAIL before using the skill.

Use a **dedicated browser profile** for the agent (e.g. a "job-hunt"
profile) so its tabs, cookies and logins are isolated from your daily
browsing. The extension needs one click — "connect current tab" — per tab
before the bridge can drive it.

### Why not v2.0.3 (the one-click installer)?

The bridge project has moved on to v2.0.3
(`AshenJyy/browser-bridge`), which ships a packaged ZIP installer and adds
token auth — closer to one-click install. **But v2 uses a different API**
(`POST /v1/call` with a Bearer token, session/tab ownership, no raw CDP
passthrough) and targets Edge. This skill's `scripts/bridge.py` and
`scripts/selftest.py` speak the v1.4.1 API (plain endpoints, no auth). Until
someone writes a v2 adapter and re-runs the self-test against it, **install
v1.4.1**. The v2 packaged installer is the right direction for one-click
install; it is not usable with this skill yet.

### Tailscale (remote mode only)

Only needed if your agent runs in the cloud (Path B, e.g. Meta Muse).
Local mode (Path A) needs no Tailscale.

- Download: https://tailscale.com/download — Windows: download and run
  the installer, then sign in. One-click install.
- Then follow the remote-mode setup in this file (Option 1: SSH forward).
  Tailscale is the tunnel; it does not replace the SSH step.

## API reference (v1.4.1, verified by live use)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Is the bridge up? |
| GET | `/tabs` | List tabs (fresh IDs — always call before acting) |
| GET | `/active_tab` | The currently active tab |
| POST | `/new_tab` | Open a tab |
| POST | `/navigate` | `{tabId, url}` — go to a URL |
| POST | `/snap` | `{tabId}` — accessibility snapshot of the tab |
| POST | `/click` | `{tabId, selector}` — click by CSS selector |
| POST | `/type` | `{tabId, selector, text, clear}` — type into an element |
| POST | `/content` | `{tabId}` — page content |
| POST | `/screenshot` | `{tabId}` — screenshot of the **active tab only** |
| POST | `/eval` | `{tabId, expression}` — run JS in the page |
| POST | `/cdp` | Raw Chrome DevTools Protocol |

Notes:

- **`/eval` returns `{"success": true, "data": "..."}`** — the value is in
  `data` (verified 2026-11-09).
- **`/eval` does NOT await Promises.** For async work (fetch, etc.), set
  `window._r` inside a `.then()`, wait ~4s, then read `window._r` in a second
  `/eval` call.
- **The `/eval` body field is `expression`, not `js`.** (Some docs say `js`;
  1.4.1 expects `expression`.)
- **`/click` takes `{tabId, selector}`.** Element IDs and screen coordinates
  do not work.
- **Tab IDs go stale overnight.** Always `GET /tabs` fresh at the start of a
  run. Never reuse yesterday's tab IDs.
- **`/screenshot` only captures the active tab.** Switch to the tab first if
  you need its screenshot.
- **No auth in v1.4.1, no `/api` prefix.** Trust the README of the version you
  installed and probe the endpoints; do not guess newer docs. The skill ships
  a version probe: call `/health` and `/tabs` first, and stop if the shape is
  unexpected.
- **A crash / `Errno 10048` usually means a second bridge instance is
  already running.** Never relaunch blindly — check what is listening first.

## Local mode (default, ships in this skill)

Agent and browser run on the **same machine**. The agent calls
`http://127.0.0.1:9224`. Nothing leaves the machine. No Tailscale, no tunnel,
no relay. This is the mode ordinary users install in 6 steps (README → Setup).

## Remote mode (advanced, not the default)

If the agent runs on another machine (e.g. a cloud VM — this is the case for
cloud agents such as Meta Muse), the bridge must be reachable over the
network. Remote mode widens the exposure (see Security) — prefer a local
agent when you can. Two ways to connect; **use Option 1** (verified with Meta
Muse on 2026-11-09). Option 2 is an unverified fallback.

### Option 1 (preferred): SSH local forward — no port opened for the bridge

This is how the author's Meta Muse connects (verified 2026-11-09):

- The agent platform's runtime is already a node on the user's tailnet (the
  runtime registers it; nothing is installed inside the agent's VM, and a VM
  replacement does not need a new key).
- The agent opens an SSH session to the PC over the tailnet with a local
  forward, e.g. `ssh -L 19224:127.0.0.1:9224 user@<pc-tailnet-ip>`, and uses
  `BRIDGE_URL=http://127.0.0.1:19224`.
- The bridge stays bound to `127.0.0.1` on the PC. **No portproxy, no
  firewall rule for 9224.** Access requires SSH authentication on top of the
  tailnet, which compensates for the bridge having no auth.

How the runtime joins the tailnet and how it reaches SSH (the author's Muse
runtime goes through its own outbound proxy) depends on the agent platform —
check your platform's docs. The agent machine does **not** need its own
`tailscaled` or an auth key.

**Path B checklist — 12 steps** (this is the "12 steps" the README refers
to; details for the PC-side items are in the prerequisites below):

1. On the PC, run `scripts/setup-local.ps1` — installs Python, `websockets`,
   Bridge v1.4.1, creates `start-bridge.bat`, starts the server.
2. Load the browser extension (Chrome/Edge → Developer mode → Load unpacked
   → the `extension` folder).
3. Check the bridge answers locally: `http://127.0.0.1:9224/health`.
4. Install Tailscale on the PC (https://tailscale.com/download) and sign in.
5. Install OpenSSH Server on the PC (admin PowerShell — see below).
6. Set up SSH key login (agent's public key into `administrators_authorized_keys`,
   ACL-locked).
7. Turn off password login in `sshd_config` (`PasswordAuthentication no`)
   and restart sshd.
8. Tighten the Tailscale ACL so the agent node can reach only the PC's
   port 22.
9. On the agent side, open the SSH forward:
   `ssh -N -L 19224:127.0.0.1:9224 <user>@<pc-tailnet-ip>`.
10. Check the bridge answers through the forward
    (`BRIDGE_URL=http://127.0.0.1:19224`, then `curl` `/health`).
11. Log in to the four job sites in your own browser.
12. Fill in `criteria.yaml` (your AI will ask you) and run
    `python scripts/selftest.py` with `BRIDGE_URL` set.

**PC-side prerequisites (Windows, admin PowerShell):**

1. Install and auto-start OpenSSH Server:
   ```powershell
   Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
   Start-Service sshd
   Set-Service sshd -StartupType Automatic
   ```
2. Key login only. On the agent machine generate a key
   (`ssh-keygen -t ed25519`) and give the user the **public** key. For an
   account in the Administrators group, Windows reads keys from
   `C:\ProgramData\ssh\administrators_authorized_keys`, which must be locked
   down or sshd ignores it:
   ```powershell
   Add-Content C:\ProgramData\ssh\administrators_authorized_keys "<agent public key>"
   icacls C:\ProgramData\ssh\administrators_authorized_keys /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"
   ```
   (Non-admin account: `C:\Users\<you>\.ssh\authorized_keys` instead.)
3. Turn off password login in `C:\ProgramData\ssh\sshd_config`
   (`PasswordAuthentication no`), then `Restart-Service sshd`.
4. Tailscale ACL: let the agent node reach **only** the PC's SSH port, and
   keep your own devices on `autogroup:member` (replace the default
   allow-all rule):
   ```json
   {
     "acls": [
       { "action": "accept", "src": ["autogroup:member"], "dst": ["*:*"] },
       { "action": "accept", "src": ["<agent-node>"],     "dst": ["<pc-tailnet-ip>:22"] }
     ]
   }
   ```
   `<agent-node>` is the agent's tailnet IP or a tag you assigned to it.

**Agent side:**

```bash
ssh -N -L 19224:127.0.0.1:9224 <user>@<pc-tailnet-ip> &
export BRIDGE_URL=http://127.0.0.1:19224
python scripts/selftest.py
```

Never paste a private key into a chat or commit it.

### Option 2: Tailscale + portproxy (unverified, last resort)

Only if your agent can join the tailnet but cannot do an SSH forward. This
opens port 9224 on the PC's Tailscale IP, and the bridge has **no auth**, so
both restrictions below are mandatory. Nobody has verified this path
end-to-end; the author used it once and has since removed it in favour of
Option 1.

1. On the PC (admin PowerShell), with Tailscale installed and logged in:
   ```powershell
   $ip = (tailscale ip -4 | Select-Object -First 1).Trim()
   netsh interface portproxy add v4tov4 listenaddress=$ip listenport=9224 connectaddress=127.0.0.1 connectport=9224
   New-NetFirewallRule -DisplayName "job-apply bridge (tailnet only)" -Direction Inbound -Protocol TCP -LocalPort 9224 -LocalAddress $ip -RemoteAddress 100.64.0.0/10 -Action Allow
   ```
   Never use `listenaddress=0.0.0.0`. To remove:
   `netsh interface portproxy delete v4tov4 listenaddress=$ip listenport=9224`
   and `Remove-NetFirewallRule -DisplayName "job-apply bridge (tailnet only)"`.
2. Join the agent machine to the tailnet (how depends on the platform; an
   ephemeral, tagged auth key such as `tag:job-agent` is the safe default)
   and set `BRIDGE_URL=http://<pc-tailnet-ip>:9224`.
3. Tailscale ACL — the agent may reach **only** `<pc-tailnet-ip>:9224`:
   ```json
   {
     "tagOwners": { "tag:job-agent": ["autogroup:admin"] },
     "acls": [
       { "action": "accept", "src": ["autogroup:member"], "dst": ["*:*"] },
       { "action": "accept", "src": ["tag:job-agent"],   "dst": ["<pc-tailnet-ip>:9224"] }
     ]
   }
   ```

**Important (both options):** the default Tailscale policy contains an
allow-all rule (`"src": ["*"], "dst": ["*:*"]`). Tagged devices match `*`, so
**while that rule exists the agent can reach every device and port on your
tailnet.** Replace it with the `autogroup:member` rule (keep any other rules
you added yourself).

### Audit an existing setup

A leftover forward is easy to forget. On the PC (admin PowerShell):

```powershell
netsh interface portproxy show v4tov4                                   # any 9224 forward?
Get-NetFirewallRule | Where-Object DisplayName -like "*9224*"            # firewall rule present?
```

If a 9224 forward exists but you use Option 1 (SSH), delete it:
`netsh interface portproxy delete v4tov4 listenaddress=<ip> listenport=9224`.
Also review the Tailscale admin console: remove devices you don't recognise,
and replace the default allow-all ACL rule.

## Autostart

On Windows, autostart via a Startup-folder shortcut to a silent-start script
works, but it can fail silently (observed: bridge not listening after boot with
no error shown). After boot, verify with `GET /health` before assuming a run
will work. If the PC was asleep or off, a scheduled scan simply misses its
slot — skip silently and retry at the next slot, do not spam the user.

## Security — read this before installing

**The bridge HTTP API has no authentication in v1.4.1.** Anyone who can reach
port 9224 can drive the logged-in browser: read pages, click, type, navigate —
as the user, in all their logged-in accounts.

Rules:

1. **Bind to `127.0.0.1` only.** Never bind `0.0.0.0`, never port-forward 9224
   on a router, never expose it to a LAN. In remote mode, allow the port only
   on the Tailscale IP from the Tailscale range, and restrict it to the agent
   node with the Tailscale ACL (see "Tailscale setup" above).
2. **Stop the bridge when idle.** A bridge left running is a 24/7 open
   control channel into the browser. Start it for a run, stop it after.
3. **Separate browser profile.** Run the agent in a dedicated Chrome/Edge
   profile so its tabs, cookies and logins are isolated from daily browsing.
4. **Never share the tunnel.** In remote mode the tunnel network is trusted:
   any device on it can drive the browser. Do not share access.
5. **Token auth (future):** NexusBrowser / bridge v2 add token auth, but use a
   different API this skill does not support yet. Until then, rules 1-4 are
   the protection.

A skill that drives a logged-in browser is powerful exactly because the
browser is logged in. Treat the bridge like a house key: don't leave it in the
door.
