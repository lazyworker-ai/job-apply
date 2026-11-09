# 51job adapter

## Search — direct URL first, homepage box as fallback

1. **Try the direct search URL first:**
   ```
   https://we.51job.com/pc/search?jobArea=040000&keyword=<keyword>&salary=10
   ```
   - `jobArea=040000` is Shenzhen.
   - `salary=10` is a rough salary bucket (it returned 1.5万+ results);
     apply the user's floor afterwards.
   - This worked on every pull in the 2026-11-09 live run.
2. **If the page comes back blank** (anti-bot), fall back: open the 51job
   homepage, type the keyword into the homepage search box, then click
   search. The search button (`.search-btn`) is a `div`, not a `<button>` —
   click it by selector.
3. Confirm the area on the results page matches the user's city before
   collecting.

## Extracting job IDs

- Job cards are `.joblist-item-job[sensorsdata]`. Read the attribute with
  `getAttribute` and `JSON.parse` it — by then HTML entities are already
  decoded. Useful fields: `jobId`, `jobTitle`, `jobSalary`, `jobArea`,
  `jobYear`, `jobDegree`, `jobTime`, `companyId`.
- If matching with a regex instead, match `"jobId":"(\d+)"`, **not**
  `&quot;jobId&quot;` (a first implementation matched the encoded form and
  extracted zero IDs).
- `jobSalary` can be monthly (`2.5-4万·13薪`) or yearly (`35-70万/年`) —
  convert yearly to monthly before comparing.
- Detail page format is stable (both work):
  ```
  https://jobs.51job.com/all/<jobId>.html
  https://jobs.51job.com/<city>/<jobId>.html
  ```

## Result volatility

- The same keyword pulled twice in a row can return different cards. Treat
  each pull as a snapshot; dedupe by `jobId` across pulls.

## Applying

- On the detail page the apply control is a leaf element with the text
  **立即投递** (not necessarily a `<button>`).
- On success the tab **navigates** to:
  ```
  https://jobs.51job.com/applysuccess.php?jobid=<jobId>
  ```
  This URL is a good per-job success signal (still reconcile — see below).
- **The navigation kills any `/eval` still running on the old page.** Don't
  click and then `await`/sleep in the same `/eval` call. Click in one call
  (or schedule the click with `setTimeout(..., 100)` and return at once),
  then check the tab's URL in a separate call.
- If a "请选择需要投递的简历" dialog appears, click **立即申请** in it.

## Screening notes

- Post-filter fuzzy results by title: keyword search returns many
  off-target titles (e.g. 副总裁 returned 20 cards, all CEO / GM /
  operations / marketing / sales — zero finance VP roles).
- If a keyword returns no in-scope roles twice, stop spending pulls on it.

## Verification

- Confirm every application on the platform's own record page:
  ```
  https://i.51job.com/userset/my_apply.php
  ```
  Report counts from this page only (see `governance.md` rule 4).

## Unverified

- Stability of incremental (new-only) scans across days.
- How often the direct search URL goes blank (not seen on 2026-11-09).
