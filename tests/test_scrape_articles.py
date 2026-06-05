"""Unit tests for the pure parsing/filtering logic of scrape_articles (no network)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from scrape_articles import article_id, extract_post_links, parse_sitemap_entries

BASE = "https://example-blog.de"

ARCHIVE_HTML = f"""
<html><body>
  <nav><a href="{BASE}/category/analyse/">Analyse</a></nav>
  <article>
    <h2 class="entry-title"><a href="{BASE}/2026/05/mueller-im-portrait/">Müller im Portrait</a></h2>
    <a href="{BASE}/2026/05/mueller-im-portrait/#comments">Kommentare</a>
  </article>
  <article>
    <h2 class="entry-title"><a href="/2026/04/schmidt-scouting/">Schmidt Scouting</a></h2>
  </article>
  <a href="{BASE}/page/2/">Nächste Seite</a>
  <a href="https://other-host.com/post/">extern</a>
</body></html>
"""

SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example-blog.de/post-a/</loc><lastmod>2026-01-02T10:00:00+00:00</lastmod></url>
  <url><loc>https://example-blog.de/post-b/</loc></url>
</urlset>
"""

SITEMAP_INDEX_XML = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://example-blog.de/post-sitemap1.xml</loc><lastmod>2026-02-01</lastmod></sitemap>
</sitemapindex>
"""


def test_extract_post_links_finds_entry_titles_and_resolves_relative():
    links = extract_post_links(ARCHIVE_HTML, BASE)
    assert links == [
        f"{BASE}/2026/05/mueller-im-portrait/",
        f"{BASE}/2026/04/schmidt-scouting/",
    ]


def test_extract_post_links_filters_taxonomy_pagination_and_foreign_hosts():
    links = extract_post_links(ARCHIVE_HTML, BASE)
    assert not any("/category/" in u or "/page/" in u or "other-host" in u for u in links)


def test_extract_post_links_strips_fragment_duplicates():
    links = extract_post_links(ARCHIVE_HTML, BASE)
    assert len([u for u in links if "mueller" in u]) == 1


def test_parse_sitemap_entries_reads_loc_and_optional_lastmod():
    entries = parse_sitemap_entries(SITEMAP_XML)
    assert entries == [
        {"loc": "https://example-blog.de/post-a/", "lastmod": "2026-01-02T10:00:00+00:00"},
        {"loc": "https://example-blog.de/post-b/", "lastmod": ""},
    ]


def test_parse_sitemap_entries_handles_sitemap_index():
    entries = parse_sitemap_entries(SITEMAP_INDEX_XML)
    assert entries == [{"loc": "https://example-blog.de/post-sitemap1.xml", "lastmod": "2026-02-01"}]


def test_article_id_is_stable_and_short():
    assert article_id("https://x.de/a") == article_id("https://x.de/a")
    assert article_id("https://x.de/a") != article_id("https://x.de/b")
    assert len(article_id("https://x.de/a")) == 16
