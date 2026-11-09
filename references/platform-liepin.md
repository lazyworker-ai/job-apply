# Liepin adapter

## Search

```
https://www.liepin.com/zhaopin/?city=050090&dq=050090&key=<keyword>&salary=25$50
```

- `key` is the keyword (URL-encoded). `city`/`dq=050090` is Shenzhen —
  replace with the user's city.
- `salary=<min>$<max>` is in k/month (e.g. `25$50`).
- The `dq` filter can leak non-Shenzhen jobs. Always confirm the JD location
  on the detail page.
- Cards: collect links matching `liepin.com/(job|a)/<id>`; the card text
  holds title, `【city】`, salary like `30-40k·13薪`, experience, degree,
  company (often anonymised for headhunter posts), recruiter.

## Two page types

- `/job/<id>.shtml` (company postings): the action is **投简历**.
- `/a/<id>.shtml` (headhunter postings): the action is **聊一聊**.

### What 聊一聊 actually does (important)

Clicking **聊一聊** **immediately sends an automatic default greeting**
(e.g. "请问XX职位还在招吗？谢谢!") and opens the IM panel. There is no
chance to draft before that first message. So:

- Clicking 聊一聊 is an apply action — only for shortlist-approved items
  (`governance.md` rule 1.5). Never click it during collection.
- To actually deliver the resume: in the IM panel click **发简历** → a confirm
  dialog "确定向对方发送简历吗？" → **确定**. The chat then shows a card
  "这是我的简历，合适的话可以随时联系我～ / <name>的简历 在线简历".
- A chat with only the greeting is **not** an application. Count an `/a/`
  job as applied only when the resume card appears in **that job's own chat
  thread**.

### Verifying the resume was sent — don't search the whole page

**Pitfall:** do not judge "resume sent" by searching the whole page for
这是我的简历. The right-hand 我的沟通 list shows the last message of every
conversation, so once one resume has been sent, its preview matches on every
later page and greeting-only jobs get counted as applied.

Check inside the open conversation only (the IM panel of this job):

- Sent resume card shows as text "这是我的简历… / <name>的简历 / 在线简历", **or**
  as the web placeholder "不支持此消息查看，请登录猎聘APP查看消息内容！"
  (rich message type the web client doesn't render — this also counts as sent).
- A greeting-only thread contains just "请问XX职位还在招吗？谢谢！".
- If 发简历 or its 确定 dialog was not found, report the job as **greeting
  only**, never as applied.

## Pace — Liepin triggers a security check

Opening many job pages in a row (e.g. while reconciling) triggers a Liepin
security verification (account behaviour abnormal, image captcha). When it
appears: **stop immediately**, tell the user to complete it in their own
browser (the agent never solves captchas), then continue slowly — leave
several seconds between job pages.

## Login — may expire overnight

- Verify login state programmatically at the start of every run (e.g. the
  header greets the user by name). If expired, stop and ask the user to
  re-login (QR scan in their own browser), then re-verify. On an expired
  session 聊一聊 silently does nothing.

## IM input (React-controlled) — for custom text only

- The chat textarea is React-controlled: setting `.value` does not work.
  Focus the field, then `document.execCommand('insertText', false, text)`.
- The IM overlay's inner entry point is `.im-ui-basic-entry-c`.
- Custom text is draft-only: get the user's confirmation of the exact text
  before sending (`governance.md` rule 2).

## Screening notes

- A "基金/证券/期货" tag is **not** an auto-exclude; read the JD.
- Note headhunter (`/a/`) vs company (`/job/`) posting in the shortlist.
- Reconcile counts against Liepin's 我的投递 / 我的沟通 records before
  reporting.
