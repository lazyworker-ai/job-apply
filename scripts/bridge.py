"""Minimal client for the Antigravity Browser Bridge (1.4.1) / NexusBrowser.

Local mode (default): the agent and the browser run on the same machine.
    from bridge import api
    api("GET", "/health")
    api("POST", "/navigate", {"tabId": 123456789, "url": "https://www.liepin.com"})

Remote mode: set BRIDGE_URL, e.g. BRIDGE_URL=http://100.x.x.x:9224
(only if you run the agent on another machine and expose the bridge over a
private network — see references/bridge.md Security first. Never expose the
bridge to a public network: v1.4.1 has no auth.)

If the bridge is reached through an HTTP proxy, set HTTPS_PROXY; the proxy is
only used when BRIDGE_URL is not localhost.
"""
import json
import os
import urllib.request
import urllib.error

BRIDGE_URL = os.environ.get("BRIDGE_URL", "http://127.0.0.1:9224").rstrip("/")


def _opener():
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or ""
    if proxy and "127.0.0.1" not in BRIDGE_URL and "localhost" not in BRIDGE_URL:
        return urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    return urllib.request.build_opener()


def api(method, path, body=None, timeout=45):
    """Call a bridge endpoint. Returns parsed JSON (or raw text if not JSON)."""
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BRIDGE_URL + path, data=data,
                                 headers=headers, method=method)
    try:
        with _opener().open(req, timeout=timeout) as r:
            text = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"bridge {method} {path} -> HTTP {e.code}: {text[:500]}")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def health():
    return api("GET", "/health")


def tabs():
    return api("GET", "/tabs")


def navigate(tab_id, url):
    return api("POST", "/navigate", {"tabId": tab_id, "url": url})


def snap(tab_id):
    return api("POST", "/snap", {"tabId": tab_id})


def content(tab_id):
    return api("POST", "/content", {"tabId": tab_id})


def evl(tab_id, js):
    """Run JS in the page. Body field is `expression` (not `js`) on 1.4.1.
    /eval does NOT await Promises: for async work, set window._r inside a
    .then(), wait a few seconds, then read window._r in a second call."""
    return api("POST", "/eval", {"tabId": tab_id, "expression": js})


def evl_async(tab_id, js, wait_s=4):
    """Run async JS and return the value it stored in window._r."""
    import time
    evl(tab_id, js)
    time.sleep(wait_s)
    return evl(tab_id, "window._r")
