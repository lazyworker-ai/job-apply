# Governance (apply-governance module)

Binding rules for every run. These are not suggestions. If a rule conflicts
with finishing faster, the rule wins.

## 1. Nod-first (no application without approval)

1. Screen and collect first. **Do not click any apply / chat button during
   collection.**
2. Present a shortlist: one line per job (platform, title, company, salary,
   why it fits). Keep it short enough to read on a phone.
3. Wait for the user's explicit approval of that list.
4. Apply only to approved items. If the user rejects an item, drop it — do
   not re-propose it in the same round.
5. **Approving the shortlist = approving the platform's default apply action
   for those items.** On every platform, applying itself sends something:

   | Platform | What the apply action sends |
   | --- | --- |
   | Boss | 立即沟通 → the platform's default greeting to the recruiter |
   | Zhaopin | 立即投递 → resume + default greeting |
   | 51job | 立即投递 → resume |
   | Liepin `/job/` | 投简历 → resume |
   | Liepin `/a/` | 聊一聊 → an **automatic** default greeting the instant it is clicked; then 发简历 → 确定 sends the online resume card |

   The user's nod on the shortlist covers exactly these default actions for
   the approved items. Tell the user this when presenting the shortlist.

## 2. Draft-only (no custom text sent without confirmation)

- HR and headhunter replies are **drafted only**. The user confirms the exact
  text before anything is sent.
- Any **custom** text (a personalised greeting, a reply, a follow-up) needs
  the user's confirmation of that exact text. Default apply actions approved
  under rule 1.5 do not need a second confirmation.
- Never accept an interview, exchange phone/WeChat, or send a resume outside
  an approved application without the user's confirmation of that exact
  action.
- If a reply arrives for a job that is now excluded (e.g. the role turns out
  to be an excluded category), tell the user and do not chase it.

## 3. The detail page is the only source of truth

- The list page is a rough filter only. Location, industry, salary and hard
  requirements are confirmed on the **job detail page** before any decision to
  apply.
- Typical traps the detail page reveals: a different base city than the
  card shows, or a role whose real requirements differ from its title.
- Never apply on list-page information alone.

## 3b. Check hard requirements before shortlisting

Read the JD's hard requirements (market/segment, years, degree, licences,
deal or fund-size track record) and compare them with the user's real
background **before** putting a job on the shortlist. A title match is not
a fit: e.g. "私募投资总监" may require a secondary-market fund manager with a
verifiable NAV track record, which a primary-market (PE/VC) candidate cannot
meet. List any gap next to the job in the shortlist; drop clear mismatches
unless the user explicitly asks to apply anyway. Headhunter postings
usually screen hard first — note them as such.

## 4. Verification before reporting (the reconciliation rule)

- **Application counts are reconciled against the platform's actual
  submission records before any number is reported.** Examples: 51job
  我的申请, Zhaopin 投递记录, Liepin 投递/沟通记录, Boss 消息 → 沟通过 list
  (Boss has no separate 投递记录 for 立即沟通 applications).
- A button changing to "applied", a toast saying "success", or "I clicked it"
  is **not** proof. Only the platform's own record counts.
- Login state is verified programmatically (page/API) at the start of every
  run — never from memory, and never from the user saying "I'm logged in".
- When a check cannot run (PC asleep, bridge down), say so plainly and roll
  to the next slot. Do not report stale numbers as current.

## 5. Exclusions are hard filters

Fill `criteria.yaml` with the user's exclusions. Illustrative examples
(adapt, don't copy blindly):

- Industries: insurance, securities / brokerage private funds, medical
  devices / pharma, real estate.
- Role traps: sales jobs disguised as investment, investor relations (IR),
  pure financing-director roles (including "investment director" titles that
  are really fundraising), strategy-operations heads, board secretary (without
  the qualification), debt-financing-led roles, culture & tourism, finance /
  accounting posts, government-enterprise project investment.
- Client traps: any role touching high-net-worth clients / wealth management /
  private banking / C-end client development.
- Salary traps: abnormally high postings (e.g. ≥ ¥100k/month) — usually scams
  or sales roles. Never apply, never engage.
- Company blocklist: a user-maintained list of companies never to touch.
  Keep your own; entries are personal history.
- **Platform-side blocking (optional, needs the user's nod).** When the user
  asks to "拉黑/屏蔽" a company, besides adding it to `company_blocklist`, the
  agent can block it inside the platform so that company can no longer see
  the resume. This changes account settings, so do it only on the user's
  explicit request. A company search can return several legal entities
  sharing one brand name — show the user which entities were blocked.
  Example (Boss): 简历 → 隐私设置 屏蔽公司 → 设置 → search the name → tick the
  entities → 屏蔽这些公司.

Borderline cases (e.g. a hybrid role mixing investment with secondary-market
work) go to the user for a call. Never auto-apply a borderline.

## 6. Never fabricate

- Rewrite a resume to match a JD; never invent experience, numbers or
  credentials. CFA "Level I & II passed" is not "charterholder". A fund that
  was not raised was not raised.
- Resume customisation workflow (when the user asks for it): snapshot the
  original first → edit in the platform's resume centre and save → apply →
  verify the application succeeded (see rule 4) → archive the customised
  version noting which company it went to → restore the original before the
  next application. The customised version is shown to the user and used only
  after their nod.
- If a JD asks for something the user has never done (e.g. a named M&A closing
  case), flag the gap instead of writing around it.

## 7. Pace like a human

- Space actions seconds apart (Boss: 30s+ between searches, or the platform
  returns code 37 "environment abnormal"). Back off on any rate-limit or
  block signal; never hammer retries.
- One keyword at a time, one platform at a time. Do not parallelise against
  the same logged-in browser.
- If the PC sleeps or Chrome exits mid-run, the run is missed — skip silently
  and continue at the next slot.

## 8. Dedupe and normalise

- Dedupe by **JD text**, not title: the same job reposted under different
  titles is one job.
- Normalise salaries before comparing: `k` / `K` / `万/月` / `万/年` plus
  `·N薪` (e.g. `30-40k·14薪`). A yearly figure is not a monthly figure.
- JD location overrides the card location. Always.

## 9. Reply monitoring

- On the schedule the user agrees (e.g. 09:45 and 20:45), scan each
  platform's message centre for new HR replies.
- For each new reply: quote it, name the job it belongs to, say whether the
  job is still in-scope or now excluded, and attach a draft response. The user
  confirms before anything is sent.
- If the bridge is unreachable, skip silently. Do not invent a "no new
  replies" report when nothing was checked.
