# Boss Zhipin adapter

## Search — read the page's own data, don't call the API yourself

Salaries in the rendered HTML are font-obfuscated, so don't scrape the visible
text. The preferred way is to let the page load normally and read the job list
the page itself already fetched:

1. Navigate to the search page:
   ```
   https://www.zhipin.com/web/geek/jobs?query=<keyword>&city=101280600&salary=406
   ```
   - `city=101280600` is Shenzhen. Replace with the user's city code.
   - `salary=406` is the 20-50K bucket (`405` = 10-20K, `407` = 50K+). It is a
     rough filter; apply the user's exact floor afterwards.
2. Wait ~2-3s, scroll to the bottom 2-3 times (2-3s apart) to load more cards
   (15 per load, ~60 after three scrolls).
3. Read the list from the page's Vue component:
   ```js
   (() => { for (const el of document.querySelectorAll('*')) {
       const v = el.__vue__; if (!v) continue;
       const d = v.jobList || (v.$data && v.$data.jobList);
       if (Array.isArray(d) && d.length && d[0].salaryDesc) return JSON.stringify(
         d.map(x => ({id: x.encryptJobId, name: x.jobName, sal: x.salaryDesc,
           co: x.brandName, ind: x.brandIndustry, exp: x.jobExperience,
           deg: x.jobDegree, area: x.areaDistrict, boss: x.bossTitle})));
     } return '[]'; })()
   ```
   `salaryDesc` is plain text here (e.g. `30-40K·15薪`).

Why not call `/wapi/zpgeek/search/joblist.json` directly: in a live run, four
direct calls worked, then every call returned **code 37 "您的环境存在异常"**.
The anti-bot token is refreshed by normal page navigation, so reading the data
the page already loaded is both safer and fewer requests. Use the direct API
only as a fallback, and only right after a normal page load.

## Throttle

- **Space searches out** (one keyword per page load, a few seconds plus
  scrolling between them). Navigation-based reading ran a whole day without
  a block; rapid direct API calls hit code 37 within seconds.
- If code 37 appears, stop, wait 45s+, do a normal page navigation, then
  retry once. If it persists, end the run and roll to the next slot.
- A first navigation of the day may bounce through
  `/web/passport/zp/security.html` and come back automatically — wait for it,
  do not treat it as a failure.

## Detail pages

```
https://www.zhipin.com/job_detail/<encryptJobId>.html
```

- The detail page title can carry information the card hides
  (e.g. card "高级投资经理" → detail "高级投资经理（出差美国）"). Read it.
- Deep links can hit a login wall. Don't force it: cool down and retry later;
  if it keeps walling, skip the job for this round and note it.

## Applying

- On the detail page, the apply control is the link **立即沟通**. Clicking it
  immediately sends the platform's default greeting to the recruiter and
  opens a chat panel showing "已发送". This is covered by the shortlist nod
  (`governance.md` rule 1.5).
- If the button reads **继续沟通**, the job was already contacted — skip it.

## Verification

- Boss has no separate 投递记录 for 立即沟通 applications. Reconcile in
  `https://www.zhipin.com/web/geek/chat`: the conversation with that job's
  recruiter shows the default greeting with a **[送达]** receipt — this is the
  decisive record. The detail page's button turning into **继续沟通** is
  supporting evidence only.
- 立即沟通 sends **only the greeting** — no resume card. The recruiter can
  still open the online profile. Sending the resume card (发简历 in the chat)
  is a separate action and needs its own confirmation.
- Background tabs: the list only loaded the first 15 cards when the tab was
  not in front. Bring the tab to the front to load more.

## Blocking a company (on user request only)

简历 → right sidebar 隐私设置 → 屏蔽公司 **设置** → search box → tick the
entities → **屏蔽这些公司**. One brand name can map to several legal entities;
report which ones were blocked.

## Screening notes

- Post-filter by title: results include fuzzy matches (sales roles titled
  "投资总监", "个股期权 投资总监" etc.).
- JD location overrides the card location (see `governance.md` rule 3).
