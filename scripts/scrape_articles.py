#!/usr/bin/env python3
"""Acquire the prose corpus: discover article URLs, then fetch and extract text.

Two-step design for reproducibility (see design spec, section 1a):

    discover  -> writes corpus_urls.jsonl   (committed: the reproducible artifact)
    fetch     -> reads corpus_urls.jsonl, writes data/articles/<id>.json (gitignored)

Binding scraping rules (design spec): robots.txt respected with our own UA,
>= 5s between requests, honest user agent, fetch-once caching, freely
accessible pages only. A Cloudflare challenge aborts the source — we treat
it as "bots unwanted" and drop the source rather than work around it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
import trafilatura
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
URLS_FILE = REPO_ROOT / "corpus_urls.jsonl"
ARTICLES_DIR = REPO_ROOT / "data" / "articles"
FAILURES_FILE = ARTICLES_DIR / "_failures.jsonl"

USER_AGENT = "ScoutingRAG-research/0.1 (private research project)"
FETCH_DELAY_S = 5.0
TIMEOUT_S = 20
MAX_ARCHIVE_PAGES = 50  # safety stop for pagination walks


@dataclass
class Source:
    name: str
    base_url: str
    lang: str
    # WordPress category archives to walk page by page (/page/N/ pagination)
    category_urls: list[str] = field(default_factory=list)
    # sitemap index whose 'post-sitemap*' children list article URLs
    sitemap_index: str | None = None
    # drop URLs matching this pattern (e.g. podcast episodes)
    exclude_pattern: str | None = None
    # cap after sorting by lastmod desc (newest first); None = no cap
    max_urls: int | None = None


SOURCES = [
    Source(
        name="spielverlagerung",
        base_url="https://spielverlagerung.de",
        lang="de",
        category_urls=[
            "https://spielverlagerung.de/spielerportrats/",
            "https://spielverlagerung.de/spielerportrats/spieleranalysen/",
            "https://spielverlagerung.de/spielerportrats/in-depth-spieleranalysen/",
            "https://spielverlagerung.de/spielerportrats/historische-spieler/",
        ],
    ),
    Source(
        name="miasanrot",
        base_url="https://miasanrot.de",
        lang="de",
        sitemap_index="https://miasanrot.de/sitemap_index.xml",
        exclude_pattern=r"podcast",
        max_urls=80,
    ),
]


class SourceBlocked(RuntimeError):
    """Source answers with a bot challenge — drop it, never work around it."""


def article_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


def parse_sitemap_entries(xml_text: str) -> list[dict]:
    """Entries of a sitemap or sitemap index: [{'loc': ..., 'lastmod': ...}]."""
    soup = BeautifulSoup(xml_text, "xml")
    entries = []
    for node in soup.find_all(["url", "sitemap"]):
        loc = node.find("loc")
        if loc is None or not loc.text.strip():
            continue
        lastmod = node.find("lastmod")
        entries.append(
            {
                "loc": loc.text.strip(),
                "lastmod": lastmod.text.strip() if lastmod is not None else "",
            }
        )
    return entries


def extract_post_links(html: str, base_url: str) -> list[str]:
    """Article links from a WordPress category archive page.

    Prefers post-title anchors inside <article>/entry-title markup; falls back
    to all in-article anchors. Navigation, taxonomy and pagination links are
    filtered out.
    """
    soup = BeautifulSoup(html, "lxml")
    host = urlparse(base_url).netloc
    candidates = soup.select(
        "article h1 a[href], article h2 a[href], article h3 a[href], "
        "h1.entry-title a[href], h2.entry-title a[href]"
    )
    if not candidates:
        candidates = soup.select("article a[href]")

    links: list[str] = []
    for anchor in candidates:
        url = urljoin(base_url, anchor["href"]).split("#")[0]
        parsed = urlparse(url)
        if parsed.netloc != host:
            continue
        if re.search(r"/(category|tag|page|author|comments|wp-)", parsed.path):
            continue
        if url.rstrip("/") == base_url.rstrip("/"):
            continue
        if url not in links:
            links.append(url)
    return links


class Fetcher:
    """Polite HTTP client: own UA, robots.txt per host, global rate limit."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self._robots: dict[str, RobotFileParser] = {}
        self._last_request = 0.0

    def _robots_for(self, url: str) -> RobotFileParser:
        parsed = urlparse(url)
        host = f"{parsed.scheme}://{parsed.netloc}"
        if host not in self._robots:
            rp = RobotFileParser()
            try:
                resp = self.session.get(f"{host}/robots.txt", timeout=TIMEOUT_S)
                rp.parse(resp.text.splitlines() if resp.ok else [])
            except requests.RequestException:
                rp.parse([])  # unreachable robots.txt -> assume allowed
            self._robots[host] = rp
        return self._robots[host]

    def get(self, url: str, *, allow_404: bool = False) -> requests.Response | None:
        if not self._robots_for(url).can_fetch(USER_AGENT, url):
            raise PermissionError(f"robots.txt disallows {url}")
        wait = FETCH_DELAY_S - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        resp = self.session.get(url, timeout=TIMEOUT_S)
        self._last_request = time.monotonic()
        if resp.status_code == 404 and allow_404:
            return None
        head = resp.text[:5000]
        if "Just a moment" in head and "challenge" in head:
            raise SourceBlocked(f"Cloudflare challenge at {url}")
        resp.raise_for_status()
        return resp


def discover_categories(fetcher: Fetcher, source: Source) -> list[dict]:
    found: dict[str, dict] = {}
    for cat_url in source.category_urls:
        for page in range(1, MAX_ARCHIVE_PAGES + 1):
            url = cat_url if page == 1 else urljoin(cat_url, f"page/{page}/")
            resp = fetcher.get(url, allow_404=True)
            if resp is None:
                break
            new_links = [u for u in extract_post_links(resp.text, source.base_url) if u not in found]
            if not new_links and page > 1:
                break
            for link in new_links:
                found[link] = {"url": link, "source": source.name, "lang": source.lang}
            print(f"  {url}: +{len(new_links)} (total {len(found)})")
    return list(found.values())


def discover_sitemap(fetcher: Fetcher, source: Source) -> list[dict]:
    assert source.sitemap_index is not None  # caller dispatches on this field
    index = fetcher.get(source.sitemap_index)
    assert index is not None  # get() only returns None with allow_404=True
    post_sitemaps = [
        e["loc"] for e in parse_sitemap_entries(index.text) if "post-sitemap" in e["loc"]
    ]
    entries: list[dict] = []
    for sm_url in post_sitemaps:
        resp = fetcher.get(sm_url)
        assert resp is not None
        entries.extend(parse_sitemap_entries(resp.text))
        print(f"  {sm_url}: total {len(entries)}")
    if source.exclude_pattern:
        entries = [e for e in entries if not re.search(source.exclude_pattern, e["loc"])]
    entries.sort(key=lambda e: e["lastmod"], reverse=True)  # newest first
    if source.max_urls:
        entries = entries[: source.max_urls]
    return [{"url": e["loc"], "source": source.name, "lang": source.lang} for e in entries]


def cmd_discover(args: argparse.Namespace) -> None:
    fetcher = Fetcher()
    records: list[dict] = []
    for source in SOURCES:
        if args.source and source.name != args.source:
            continue
        print(f"discovering {source.name} ...")
        if source.category_urls:
            records.extend(discover_categories(fetcher, source))
        if source.sitemap_index:
            records.extend(discover_sitemap(fetcher, source))
    records.sort(key=lambda r: (r["source"], r["url"]))
    with URLS_FILE.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"wrote {len(records)} urls -> {URLS_FILE.name}")


def cmd_fetch(args: argparse.Namespace) -> None:
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    records = [json.loads(line) for line in URLS_FILE.read_text(encoding="utf-8").splitlines()]
    if args.limit:
        records = records[: args.limit]
    fetcher = Fetcher()
    ok = skipped = failed = 0
    for record in records:
        aid = article_id(record["url"])
        out_path = ARTICLES_DIR / f"{aid}.json"
        if out_path.exists():
            skipped += 1
            continue
        try:
            resp = fetcher.get(record["url"])
            assert resp is not None  # get() only returns None with allow_404=True
            extracted = trafilatura.extract(
                resp.text,
                output_format="json",
                with_metadata=True,
                include_comments=False,
                url=record["url"],
            )
            if not extracted:
                raise ValueError("trafilatura returned no content")
            meta = json.loads(extracted)
            doc = {
                "id": aid,
                "url": record["url"],
                "source": record["source"],
                "lang": record["lang"],
                "title": meta.get("title"),
                "author": meta.get("author"),
                "date": meta.get("date"),
                "text": meta.get("text") or meta.get("raw_text", ""),
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
            ok += 1
            print(f"  ok [{ok+skipped+failed}/{len(records)}] {record['url']}")
        except SourceBlocked:
            raise  # never work around a bot challenge — abort loudly
        except Exception as exc:  # noqa: BLE001 - log and continue with next URL
            failed += 1
            with FAILURES_FILE.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"url": record["url"], "error": str(exc)}) + "\n")
            print(f"  FAIL {record['url']}: {exc}", file=sys.stderr)
    print(f"done: {ok} fetched, {skipped} cached, {failed} failed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_discover = sub.add_parser("discover", help="collect article URLs into corpus_urls.jsonl")
    p_discover.add_argument("--source", help="only this source name")
    p_discover.set_defaults(func=cmd_discover)
    p_fetch = sub.add_parser("fetch", help="download + extract articles from corpus_urls.jsonl")
    p_fetch.add_argument("--limit", type=int, help="only the first N urls (smoke test)")
    p_fetch.set_defaults(func=cmd_fetch)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
