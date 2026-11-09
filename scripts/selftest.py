"""Read-only self-test for the job-apply skill, driven ONLY through the
browser bridge (no other browser automation).

It checks, in order:
  1. bridge /health and /tabs answer with the expected shape
  2. a tab is connected for each platform, and the user is logged in
  3. one keyword can be collected per platform with the adapter method
     described in references/platform-*.md
It NEVER clicks an apply / chat button and never sends anything.
It navigates each platform tab to a search page during the test and puts it
back to the page it was on afterwards.

Before running:
  - start the bridge (127.0.0.1:9224) and open Chrome/Edge with the extension
  - open these 4 sites in tabs, log in yourself, and click the extension's
    "connect current tab" on each tab:
      https://www.zhipin.com   https://www.zhaopin.com
      https://we.51job.com     https://www.liepin.com

Run:
  python scripts/selftest.py                 # keyword 投资总监, Shenzhen
  python scripts/selftest.py 董事长助理

Output: a report on screen and selftest_report.json next to this script.
Paste the screen output back to your AI to diagnose failures.
"""
import json
import os
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bridge import api, evl  # noqa: E402

KEYWORD = sys.argv[1] if len(sys.argv) > 1 else "投资总监"
Q = urllib.parse.quote(KEYWORD)
REPORT = {"keyword": KEYWORD, "steps": []}


def log(step, ok, detail=""):
    mark = "PASS" if ok else ("WARN" if ok is None else "FAIL")
    print(f"[{mark}] {step}: {detail}")
    REPORT["steps"].append({"step": step, "result": mark, "detail": detail})


def value(res):
    """Unwrap an /eval response whatever its exact shape."""
    if isinstance(res, dict):
        for k in ("result", "value", "data"):
            if k in res:
                return value(res[k])
    return res


def js(tab, expr):
    v = value(evl(tab, expr))
    if isinstance(v, str):
        try:
            return json.loads(v)
        except ValueError:
            return v
    return v


def tab_list():
    t = api("GET", "/tabs")
    if isinstance(t, dict):
        t = t.get("tabs") or t.get("data") or t
    return t if isinstance(t, list) else []


def find_tab(tabs, host):
    for t in tabs:
        if host in str(t.get("url", "")):
            return t.get("id") or t.get("tabId")
    return None


def goto(tab, url, wait=4):
    api("POST", "/navigate", {"tabId": tab, "url": url})
    time.sleep(wait)


def scroll(tab, times=3, gap=2.5):
    # Scroll both the window and the last job card: some lists only load more
    # when the last card enters the viewport (and background tabs may not
    # react to window scrolling at all). Boss loads 15 cards per batch.
    for _ in range(times):
        evl(tab, "window.scrollTo(0, document.body.scrollHeight);"
                 "var c=document.querySelectorAll('.job-card-wrap, li.job-card-box, .job-card-body');"
                 "if(c.length) c[c.length-1].scrollIntoView({block:'end'}); 1")
        time.sleep(gap)


# ---------- platform checks (read-only) ----------

def boss(tab):
    goto(tab, f"https://www.zhipin.com/web/geek/jobs?query={Q}&city=101280600&salary=406", 5)
    login = js(tab, "JSON.stringify(!!document.querySelector('.user-nav .label-text, .nav-figure') "
                    "|| /简历/.test((document.querySelector('.user-nav')||{}).innerText||''))")
    log("boss login", bool(login), "logged-in header found" if login else "no logged-in header — log in yourself")
    scroll(tab)
    rows = js(tab, """JSON.stringify((()=>{for(const el of document.querySelectorAll('*')){
        const v=el.__vue__; if(!v) continue; const d=v.jobList||(v.$data&&v.$data.jobList);
        if(Array.isArray(d)&&d.length&&d[0].salaryDesc) return d.map(x=>[x.jobName,x.salaryDesc,x.brandName]);}
        return [];})())""") or []
    plain = [r for r in rows if r and "K" in str(r[1])]
    log("boss collect (Vue jobList)", len(plain) > 0,
        f"{len(rows)} cards, {len(plain)} with plain salary; e.g. {plain[:2]}"
        + ("" if len(rows) > 15 else " (only the first batch of 15 loaded - scrolling did not load more; "
           "bring the tab to the front and rerun if you need more)"))
    blocked = js(tab, "JSON.stringify(/环境存在异常|security/.test(location.href+document.title))")
    if blocked:
        log("boss anti-bot", False, "security/abnormal page — wait 45s+ and rerun once")
    return len(plain)


def zhaopin(tab):
    goto(tab, f"https://www.zhaopin.com/jobs/?jl=765&kw={Q}&sl=25001,50000")
    # Background tabs can be throttled: poll up to ~10 s for the list to appear.
    for _ in range(10):
        if js(tab, "JSON.stringify(((window.__INITIAL_STATE__||{}).positionList||[]).length)"):
            break
        time.sleep(1)
    st = js(tab, """JSON.stringify((()=>{const s=window.__INITIAL_STATE__||{};
        return {user: !!(s.user && (s.user.name || s.user.userName || Object.keys(s.user).length)),
                rows: (s.positionList||[]).map(x=>[x.name,x.salary60,x.companyName,x.hasAppliedPosition])};})())""") or {}
    log("zhaopin login", st.get("user") or None,
        "user object present" if st.get("user") else "could not confirm login from page state — check the header shows your name")
    rows = st.get("rows") or []
    log("zhaopin collect (__INITIAL_STATE__)", len(rows) > 0, f"{len(rows)} cards; e.g. {rows[:2]}")
    return len(rows)


def job51(tab):
    goto(tab, f"https://we.51job.com/pc/search?jobArea=040000&keyword={Q}&salary=10", 5)
    rows = js(tab, """JSON.stringify([...document.querySelectorAll('.joblist-item-job[sensorsdata]')]
        .map(e=>{try{const d=JSON.parse(e.getAttribute('sensorsdata'));return [d.jobId,d.jobTitle,d.jobSalary]}catch(x){return null}})
        .filter(Boolean))""") or []
    if not rows:
        log("51job direct URL", None, "blank — trying homepage-box fallback")
        goto(tab, "https://www.51job.com/", 4)
        api("POST", "/type", {"tabId": tab, "selector": "#kwdselectid, input[type=text]", "text": KEYWORD, "clear": True})
        api("POST", "/click", {"tabId": tab, "selector": ".search-btn, #search_btn"})
        time.sleep(5)
        rows = js(tab, """JSON.stringify([...document.querySelectorAll('.joblist-item-job[sensorsdata]')]
            .map(e=>{try{const d=JSON.parse(e.getAttribute('sensorsdata'));return [d.jobId,d.jobTitle,d.jobSalary]}catch(x){return null}})
            .filter(Boolean))""") or []
    login = js(tab, "JSON.stringify((()=>{const t=document.body.innerText.slice(0,2000);"
                    "return /在线简历|我的51Job|退出/.test(t);})())")
    log("51job login", login or None, "header shows a user" if login else "could not confirm login — check the header")
    log("51job collect (sensorsdata)", len(rows) > 0, f"{len(rows)} cards; e.g. {rows[:2]}")
    return len(rows)


def liepin(tab):
    goto(tab, f"https://www.liepin.com/zhaopin/?city=050090&dq=050090&key={Q}&salary=25$50")
    login = js(tab, "JSON.stringify(/你好/.test(document.body.innerText.slice(0,400)))")
    log("liepin login", bool(login), "greeted by name" if login else "not logged in (expires overnight) — QR-login yourself")
    rows = js(tab, """JSON.stringify((()=>{const seen=new Set(),out=[];for(const a of document.querySelectorAll('a')){
        const m=/liepin\\.com\\/(job|a)\\/(\\d+)/.exec(a.href); if(!m||seen.has(m[2])) continue; seen.add(m[2]);
        const t=(a.closest('[class*=job-card]')||a).innerText.replace(/\\n+/g,'|'); if(/\\d+-\\d+k/.test(t)) out.push([m[1],t.slice(0,60)]);}
        return out;})())""") or []
    log("liepin collect", len(rows) > 0,
        f"{len(rows)} cards ({sum(1 for r in rows if r[0]=='a')} headhunter /a/, "
        f"{sum(1 for r in rows if r[0]=='job')} company /job/); e.g. {rows[:2]}")
    return len(rows)


PLATFORMS = [("zhipin.com", "BOSS", boss), ("zhaopin.com", "智联", zhaopin),
             ("51job.com", "51job", job51), ("liepin.com", "猎聘", liepin)]


def main():
    try:
        h = api("GET", "/health")
        log("bridge /health", True, str(h)[:120])
    except Exception as e:  # noqa: BLE001
        log("bridge /health", False, f"{e} — is the bridge running on 127.0.0.1:9224?")
        return finish()
    tabs = tab_list()
    log("bridge /tabs", bool(tabs), f"{len(tabs)} tabs; keys={list(tabs[0].keys()) if tabs else []}")
    original = {}
    for host, name, fn in PLATFORMS:
        tab = find_tab(tabs, host)
        if not tab:
            log(f"{name} tab", False, f"no connected tab on {host} — open it and click 'connect current tab'")
            continue
        original[tab] = next((t.get("url") for t in tabs if (t.get("id") or t.get("tabId")) == tab), None)
        try:
            fn(tab)
        except Exception as e:  # noqa: BLE001
            log(f"{name}", False, f"error: {e}")
        time.sleep(3)  # pace between platforms
    for tab, url in original.items():  # put the user's tabs back where they were
        if url:
            try:
                api("POST", "/navigate", {"tabId": tab, "url": url})
            except Exception:  # noqa: BLE001
                pass
    if original:
        print("Restored your tabs to the pages they were on before the test.")
    finish()


def finish():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "selftest_report.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(REPORT, f, ensure_ascii=False, indent=2)
    fails = sum(1 for s in REPORT["steps"] if s["result"] == "FAIL")
    print(f"\n{len(REPORT['steps'])} checks, {fails} failed. Report: {path}")
    print("Nothing was applied or sent.")


if __name__ == "__main__":
    main()
