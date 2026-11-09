# Zhaopin adapter

## Search

```
https://www.zhaopin.com/jobs/?jl=765&kw=<keyword>&sl=25001,50000
```

- `jl=765` is Shenzhen. Replace with the user's city code.
- `kw` is the keyword (URL-encoded).
- `sl=<min>,<max>` is a monthly-salary filter. It is loose (it still returns
  e.g. `1.5-3万`), so apply the user's floor afterwards.
- Do **not** use the `/sou/jl765/kw.../` path format — a hand-built path was
  redirected to an unrelated keyword in a live run.

## Read the page's initial state (preferred)

The server-rendered page carries the full result set in
`window.__INITIAL_STATE__.positionList` (20 items per page):

```js
JSON.stringify((window.__INITIAL_STATE__.positionList || []).map(x => ({
  id: x.number, name: x.name, sal: x.salary60, co: x.companyName,
  ind: x.industryName, size: x.companySize, exp: x.workingExp,
  deg: x.education, area: x.cityDistrict, applied: x.hasAppliedPosition })))
```

- `salary60` is plain text, e.g. `2.5-5万·13薪`.
- `hasAppliedPosition` tells you the job was already applied — skip it.
- `number` (e.g. `CCxxxxxxxxxJxxxxxxxxxxx`) builds the detail URL.

Fallbacks, in order: the page's visible text (titles did render as text in
the 2026-11 live run), then the search API
`fe-api.zhaopin.com/c/i/sou?...&cityId=765&kw=<encoded>&kt=3` from page
context with `credentials: "include"`. Never infer a title from the keyword.

## List volatility

- The same keyword pulled twice can differ. Pull each keyword at least twice
  and merge by `number` before screening.

## Detail pages and applying

```
https://www.zhaopin.com/jobdetail/<number>.htm
```

- The apply control is the button **立即投递**. On success a dialog appears:
  "已向对方发送简历和打招呼语" (resume + default greeting are both sent —
  covered by the shortlist nod, `governance.md` rule 1.5).
- **先聊聊** opens a chat instead; don't use it for applying.
- JD location overrides the card location.
- Read the JD before shortlisting: a senior-sounding title (e.g. 副总经理)
  can turn out to be a sales/marketing role on the detail page.

## Verification

- Verify login state programmatically at the start of every run.
- Confirm every application against Zhaopin's 求职进展 → 投递成功 list
  (matched by job `number`, verified 3/3 on 2026-11-09) before reporting any
  number (see `governance.md` rule 4).
