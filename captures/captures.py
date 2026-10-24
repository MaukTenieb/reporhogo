#!/usr/bin/env python3
"""Captures: lists every capture of a web address in the public web archives.

Usage:
  python3 captures.py URL [URL ...] [options]
  python3 captures.py --queue queue.txt

Options:
  --prefix         every address under URL (a whole site or folder), sliced year by year
  --name REGEX     keep the addresses whose file name matches REGEX (with --prefix)
  --alias HOST     another host name of the same site; repeatable
  --from YEAR      first year
  --to YEAR        last year
  --sources LIST   comma-separated ids (default: all); see SOURCES
  --fetch N        download up to N distinct captures per address and keep the readable ones
  --out DIR        output folder (default: out)

Standard library only. Code under MIT; credit Mauk Tenieb & Korhogo.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import email.utils
import gzip
import hashlib
import html
import io
import json
import os
import re
import shlex
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "captures/1.0 (+https://github.com/MaukTenieb/reporhogo/tree/main/captures)"
NOW = dt.datetime.now(dt.timezone.utc).year
ERROR_MARKS = ("erreur 404", "error 404", "404 not found", "page not found", "page cannot be found",
               "la page n'existe plus", "page introuvable", "not found</title>", "wayback machine</title>")


# ---------------------------------------------------------------- network

def get(url: str, headers: dict | None = None, timeout: int = 90, tries: int = 4) -> tuple[int, bytes]:
    """HTTP GET with retries on 429 and 5xx. Returns (status, body); status 0 on a network error."""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            body = e.read() if hasattr(e, "read") else b""
            if e.code in (429, 500, 502, 503, 504) and i < tries - 1:
                time.sleep(8 * (i + 1))
                continue
            return e.code, body
        except Exception as e:  # timeouts, resets, DNS
            if i < tries - 1:
                time.sleep(8 * (i + 1))
                continue
            return 0, str(e).encode()
    return 0, b""


def q(s: str) -> str:
    return urllib.parse.quote(s, safe=":/?=&%~+")


# ---------------------------------------------------------------- records

def rec(source: str, url: str, ts: str, status="", mime="", digest="", length="", replay="") -> dict:
    return {"source": source, "url": url, "ts": re.sub(r"\D", "", str(ts))[:14],
            "status": str(status or ""), "mime": mime or "", "digest": digest or "",
            "length": int(length) if str(length).isdigit() else None, "replay": replay}


def years(frm: int | None, to: int | None, first: int) -> list[tuple[str, str]]:
    a, b = frm or first, to or NOW
    return [(str(y), str(y)) for y in range(a, b + 1)]


# ---------------------------------------------------------------- Wayback Machine (CDX)

def parse_wayback(body: bytes) -> tuple[list[dict], str | None]:
    """JSON rows from the CDX server; with showResumeKey the last row holds the resume key."""
    try:
        rows = json.loads(body or b"[]")
    except ValueError:
        return [], None
    if not rows:
        return [], None
    head, rows = rows[0], rows[1:]
    key = None
    if len(rows) >= 2 and rows[-2] == [] and len(rows[-1]) == 1:
        key, rows = rows[-1][0], rows[:-2]
    out = []
    for r in rows:
        d = dict(zip(head, r))
        out.append(rec("wayback", d.get("original", ""), d.get("timestamp", ""), d.get("statuscode"),
                       d.get("mimetype"), d.get("digest"), d.get("length"),
                       f"https://web.archive.org/web/{d.get('timestamp')}id_/{d.get('original')}"))
    return out, key


def wayback(url: str, prefix: bool, frm, to) -> list[dict]:
    out = []
    slices = years(frm, to, 1996) if prefix else [(str(frm or ""), str(to or ""))]
    for a, b in slices:
        key = None
        while True:
            p = {"url": url, "matchType": "prefix" if prefix else "exact", "output": "json",
                 "fl": "timestamp,original,statuscode,mimetype,digest,length",
                 "showResumeKey": "true", "limit": "5000"}
            if a:
                p["from"] = a
            if b:
                p["to"] = b
            if key:
                p["resumeKey"] = key
            st, body = get("https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(p))
            if st != 200:
                if st not in (0, 404):
                    log(f"wayback {url} {a}: HTTP {st}")
                break
            rows, key = parse_wayback(body)
            out += rows
            if not key:
                break
            time.sleep(1)
    return out


# ---------------------------------------------------------------- Arquivo.pt (CDX, JSON lines)

def parse_ndjson(body: bytes) -> list[dict]:
    out = []
    for line in (body or b"").decode("utf-8", "replace").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def arquivo(url: str, prefix: bool, frm, to) -> list[dict]:
    out = []
    for a, b in (years(frm, to, 1996) if prefix else [(str(frm or ""), str(to or ""))]):
        p = {"url": url + ("*" if prefix and not url.endswith("*") else ""), "output": "json", "limit": "10000"}
        if a:
            p["from"] = a
        if b:
            p["to"] = b
        st, body = get("https://arquivo.pt/wayback/cdx?" + urllib.parse.urlencode(p))
        if st != 200:
            continue
        for d in parse_ndjson(body):
            out.append(rec("arquivo", d.get("url", ""), d.get("timestamp", ""), d.get("status"), d.get("mime"),
                           d.get("digest"), d.get("length"),
                           f"https://arquivo.pt/wayback/{d.get('timestamp')}id_/{d.get('url')}"))
        time.sleep(1)
    return out


# ---------------------------------------------------------------- Common Crawl (one index per crawl)

def cc_collections(frm, to) -> list[str]:
    st, body = get("https://index.commoncrawl.org/collinfo.json")
    if st != 200:
        log(f"commoncrawl collinfo: HTTP {st}")
        return []
    ids = []
    for c in json.loads(body):
        ys = [int(y) for y in re.findall(r"(?<!\d)(\d{4})(?!\d)", c["id"])]
        if not ys:
            continue
        if (frm and max(ys) < frm) or (to and min(ys) > to):
            continue
        ids.append(c["id"])
    return ids


def parse_cc(body: bytes) -> list[dict]:
    out = []
    for d in parse_ndjson(body):
        out.append(rec("commoncrawl", d.get("url", ""), d.get("timestamp", ""), d.get("status"), d.get("mime"),
                       d.get("digest"), d.get("length"),
                       f"cc:{d.get('filename')}:{d.get('offset')}:{d.get('length')}"))
    return out


def commoncrawl(url: str, prefix: bool, frm, to) -> list[dict]:
    out = []
    for cid in cc_collections(frm, to):
        p = {"url": url, "output": "json", "matchType": "prefix" if prefix else "exact"}
        st, body = get(f"https://index.commoncrawl.org/{cid}-index?" + urllib.parse.urlencode(p), timeout=120)
        if st == 200:
            out += parse_cc(body)
        time.sleep(2)
    return out


def cc_fetch(replay: str) -> bytes:
    """One WARC record from Common Crawl: byte range of the gzip member, then the HTTP body."""
    _, filename, offset, length = replay.split(":", 3)
    a = int(offset)
    st, body = get("https://data.commoncrawl.org/" + filename,
                   headers={"Range": f"bytes={a}-{a + int(length) - 1}"})
    if st not in (200, 206):
        return b""
    try:
        raw = gzip.GzipFile(fileobj=io.BytesIO(body)).read()
    except OSError:
        return b""
    parts = raw.split(b"\r\n\r\n", 2)  # WARC headers, HTTP headers, body
    return parts[2] if len(parts) == 3 else b""


# ---------------------------------------------------------------- Memento timemaps (link format)

TIMEMAPS = {
    "archivetoday": "https://archive.ph/timemap/{url}",
    "loc": "https://webarchive.loc.gov/all/timemap/link/{url}",
    "ukwa": "https://www.webarchive.org.uk/wayback/archive/timemap/link/{url}",
    "memento": "https://timetravel.mementoweb.org/timemap/link/{url}",
}


def parse_timemap(body: bytes, source: str) -> list[dict]:
    text = (body or b"").decode("utf-8", "replace")
    out = []
    for uri, attrs in re.findall(r"<([^>]+)>\s*;([^<]*)", text):
        if not re.search(r'rel="?[^"]*\bmemento\b', attrs):
            continue
        m = re.search(r'datetime="([^"]+)"', attrs)
        ts = ""
        if m:
            try:
                ts = email.utils.parsedate_to_datetime(m.group(1)).strftime("%Y%m%d%H%M%S")
            except (TypeError, ValueError):
                pass
        host = urllib.parse.urlsplit(uri).hostname or source
        orig = re.sub(r"^https?://[^/]+/(?:[^/]+/)*?\d{14}(?:id_|im_|js_|cs_)?/", "", uri)
        out.append(rec(source if source != "memento" else "memento:" + host, orig if orig != uri else "", ts, replay=uri))
    return out


def timemap(source: str):
    def run(url: str, prefix: bool, frm, to) -> list[dict]:
        if prefix:
            return []
        st, body = get(TIMEMAPS[source].format(url=q(url)), timeout=120)
        if st != 200:
            return []
        if b"captcha" in body[:20000].lower():
            log(f"{source}: CAPTCHA, open {TIMEMAPS[source].format(url=q(url))} in a browser")
            return []
        rows = parse_timemap(body, source)
        for r in rows:
            r["url"] = r["url"] or url
        lo, hi = str(frm or 0000), str(to or 9999)
        return [r for r in rows if not r["ts"] or lo <= r["ts"][:4] <= hi]
    return run


# ---------------------------------------------------------------- Ghost Archive (search page)

def parse_ghost(body: bytes) -> list[str]:
    return sorted(set(re.findall(r'href="(/archive/[A-Za-z0-9]+)"', (body or b"").decode("utf-8", "replace"))))


def ghost(url: str, prefix: bool, frm, to) -> list[dict]:
    if prefix:
        return []
    st, body = get("https://ghostarchive.org/search?term=" + urllib.parse.quote(url, safe=""))
    return [rec("ghost", url, "", replay="https://ghostarchive.org" + p) for p in parse_ghost(body)] if st == 200 else []


SOURCES = {
    "wayback": wayback,          # Internet Archive, Wayback Machine
    "arquivo": arquivo,          # Arquivo.pt
    "commoncrawl": commoncrawl,  # Common Crawl, every crawl since 2008
    "archivetoday": timemap("archivetoday"),
    "loc": timemap("loc"),       # Library of Congress
    "ukwa": timemap("ukwa"),     # UK Web Archive
    "memento": timemap("memento"),  # Memento Time Travel, aggregator of national and university archives
    "ghost": ghost,              # Ghost Archive
}


# ---------------------------------------------------------------- address variants

def variants(url: str, aliases: list[str]) -> list[str]:
    """Same page, other spellings: scheme, www, other hosts of the site, .htm/.html, case, spaces."""
    u = urllib.parse.urlsplit(url if "://" in url else "http://" + url)
    hosts = {u.hostname or ""} | set(aliases)
    hosts |= {h[4:] if h.startswith("www.") else "www." + h for h in list(hosts) if h}
    path = u.path or "/"
    paths = {path}
    head, _, name = path.rpartition("/")
    if name:
        stem, dot, ext = name.rpartition(".")
        names = {name, name.lower()}
        if ext.lower() in ("htm", "html"):
            names |= {f"{stem}.htm", f"{stem}.html", f"{stem.lower()}.htm", f"{stem.lower()}.html"}
        dec = urllib.parse.unquote_plus(name)
        names |= {dec, dec.replace(" ", "%20"), dec.replace(" ", "+"), dec.replace(" ", "_")}
        paths = {head + "/" + n for n in names}
    return sorted({f"{h}{p}" for h in hosts if h for p in paths})


# ---------------------------------------------------------------- empty captures

def shared_digests(rows: list[dict], n: int = 3) -> set[str]:
    """Digests found under n or more different addresses: a host's error page served with code 200."""
    by = collections.defaultdict(set)
    for r in rows:
        if r["digest"]:
            by[r["digest"]].add(r["url"].split("://")[-1].lower())
    return {d for d, urls in by.items() if len(urls) >= n}


def readable(raw: bytes) -> tuple[bool, str, int]:
    """(readable, title, characters of text)."""
    if not raw or raw[:6] in (b"GIF87a", b"GIF89a") or raw[:4] in (b"\x89PNG", b"%PDF"):
        return False, "", 0
    t = raw.decode("cp1252", "replace") if b"charset=utf-8" not in raw[:3000].lower() else raw.decode("utf-8", "replace")
    title = html.unescape(re.sub(r"\s+", " ", (re.search(r"(?is)<title[^>]*>(.*?)</title>", t) or [None, ""])[1])).strip()
    body = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>|<[^>]+>", " ", t)
    body = re.sub(r"\s+", " ", html.unescape(body)).strip()
    low = (title + " " + body[:2000]).lower()
    return (len(body) >= 100 and not any(m in low or m in t[:3000].lower() for m in ERROR_MARKS)), title, len(body)


def fetch(rows: list[dict], n: int, outdir: str, bad: set[str]) -> list[dict]:
    """Per address, download up to n captures with distinct content and keep the readable ones."""
    os.makedirs(os.path.join(outdir, "pages"), exist_ok=True)
    found = []
    by = collections.defaultdict(list)
    for r in rows:
        if r["replay"] and not r["replay"].startswith("https://ghostarchive"):
            by[r["url"].split("://")[-1]].append(r)
    for addr, rs in sorted(by.items()):
        seen, tries = set(), 0
        for r in sorted(rs, key=lambda r: (r["status"] not in ("200", ""), r["digest"] in bad, -(r["length"] or 0))):
            if tries >= n:
                break
            if r["digest"] and (r["digest"] in seen or r["digest"] in bad):
                continue
            if r["status"] and r["status"] not in ("200", "-"):
                continue
            seen.add(r["digest"])
            tries += 1
            raw = cc_fetch(r["replay"]) if r["replay"].startswith("cc:") else get(r["replay"])[1]
            ok, title, chars = readable(raw)
            if ok:
                name = re.sub(r"[^\w.-]+", "_", addr)[-120:] + f"_{r['ts']}.html"
                with open(os.path.join(outdir, "pages", name), "wb") as f:
                    f.write(raw)
                found.append({**r, "title": title, "chars": chars, "sha1": hashlib.sha1(raw).hexdigest(),
                              "file": "pages/" + name})
                break
            time.sleep(1)
    return found


# ---------------------------------------------------------------- run and report

def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def run(args) -> dict:
    srcs = [s for s in (args.sources.split(",") if args.sources else SOURCES) if s in SOURCES]
    rows = []
    for url in args.urls:
        bare = re.sub(r"^https?://", "", url)
        targets = [bare.rstrip("*")] if args.prefix else variants(url, args.alias or [])
        if args.prefix:
            targets += [re.sub(r"^[^/]+", a, bare) for a in (args.alias or [])]
        for s in srcs:
            for t in targets:
                got = SOURCES[s](t, args.prefix, args.frm, args.to)
                log(f"{s:13} {t} : {len(got)}")
                rows += got
    bad = shared_digests(rows)  # before the name filter: the error page repeats across the whole site
    if args.name:
        rx = re.compile(args.name, re.I)
        rows = [r for r in rows if rx.search(urllib.parse.unquote(r["url"].split("?")[0].rstrip("/").rsplit("/", 1)[-1]))]
    seen, uniq = set(), []
    for r in rows:
        k = (r["source"], r["url"], r["ts"], r["replay"])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    res = {"query": vars(args) | {"queue": None}, "date": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "shared_digests": sorted(bad), "captures": uniq}
    if args.fetch:
        res["readable"] = fetch(uniq, args.fetch, args.out, bad)
    return res


def d8(ts: str) -> str:
    return f"{ts[6:8]}/{ts[4:6]}/{ts[:4]}" if len(ts) >= 8 else "—"


def report(results: list[dict]) -> str:
    out = [f"# Captures — {results[0]['date'][:10] if results else ''}", ""]
    for res in results:
        qy, caps = res["query"], res["captures"]
        line = " ".join(qy["urls"]) + (" (prefix)" if qy["prefix"] else "") + (f" name ~ {qy['name']}" if qy["name"] else "")
        out += [f"## {line}", ""]
        if not caps:
            out += ["Zero captures.", ""]
            continue
        by = collections.defaultdict(list)
        for r in caps:
            by[r["source"]].append(r)
        out += ["| archive | captures | addresses | first | last |", "|---|---|---|---|---|"]
        for s, rs in sorted(by.items()):
            ts = sorted(r["ts"] for r in rs if r["ts"])
            out.append(f"| {s} | {len(rs)} | {len({r['url'] for r in rs})} | {d8(ts[0]) if ts else '—'} | {d8(ts[-1]) if ts else '—'} |")
        bad = set(res["shared_digests"])
        addr = collections.defaultdict(list)
        for r in caps:
            addr[r["url"].split("://")[-1]].append(r)
        out += ["", "| address | captures | with content (status 200, distinct digest) |", "|---|---|---|"]
        for a, rs in sorted(addr.items()):
            good = [r for r in rs if r["status"] in ("200", "") and r["digest"] not in bad]
            out.append(f"| `{a}` | {len(rs)} | {len({r['digest'] or r['replay'] for r in good})} |")
        if "readable" in res:
            out += ["", "Readable captures:", ""]
            out += [f"- `{r['url']}` — {r['title'] or '—'} — {r['chars']} characters — {r['source']}, "
                    f"[{d8(r['ts'])}]({r['replay'] if not r['replay'].startswith('cc:') else 'https://data.commoncrawl.org/' + r['replay'].split(':')[1]}) — `{r['file']}`"
                    for r in res["readable"]] or ["Zero."]
        out.append("")
    return "\n".join(out)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Lists every capture of a web address in the public web archives.")
    p.add_argument("urls", nargs="*")
    p.add_argument("--prefix", action="store_true")
    p.add_argument("--name")
    p.add_argument("--alias", action="append")
    p.add_argument("--from", dest="frm", type=int)
    p.add_argument("--to", type=int)
    p.add_argument("--sources")
    p.add_argument("--fetch", type=int, default=0)
    p.add_argument("--out", default="out")
    p.add_argument("--queue")
    return p


def main(argv=None) -> None:
    a = parser().parse_args(argv)
    jobs = []
    if a.queue:
        for line in open(a.queue, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#"):
                j = parser().parse_args(shlex.split(line))
                j.out = a.out
                jobs.append(j)
    if a.urls:
        jobs.append(a)
    if not jobs:
        parser().print_help()
        return
    os.makedirs(a.out, exist_ok=True)
    results = [run(j) for j in jobs]
    with open(os.path.join(a.out, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    with open(os.path.join(a.out, "results.md"), "w", encoding="utf-8") as f:
        f.write(report(results))
    print(report(results))


if __name__ == "__main__":
    main()
