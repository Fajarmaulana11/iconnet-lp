"""Validate the static site's crawlable SEO surface."""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://www.jatengwifipln.com"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.h1 = 0
        self.description = False
        self.canonical = ""
        self.refs: list[str] = []
        self.schema_blocks: list[str] = []
        self.in_title = False
        self.in_schema = False
        self.schema_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1 += 1
        if tag in {"img", "script", "link", "a"}:
            for attr in ("src", "href"):
                value = attributes.get(attr)
                if value:
                    self.refs.append(value)
        if tag == "meta" and attributes.get("name") == "description" and attributes.get("content"):
            self.description = True
        if tag == "link" and attributes.get("rel") == "canonical":
            self.canonical = attributes.get("href", "")
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self.in_schema = True
            self.schema_buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.in_schema:
            self.schema_blocks.append("".join(self.schema_buffer))
            self.in_schema = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data
        if self.in_schema:
            self.schema_buffer.append(data)


def resolve_ref(page: Path, ref: str) -> Path | None:
    if ref.startswith(("http://", "https://", "//", "mailto:", "tel:", "data:", "javascript:", "#")):
        return None
    clean = ref.split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return None
    if clean.startswith("/"):
        target = ROOT / clean.lstrip("/")
    else:
        target = page.parent / clean
    if target.is_dir():
        target = target / "index.html"
    return target.resolve()


def main() -> int:
    errors: list[str] = []
    sitemap_path = ROOT / "sitemap.xml"
    try:
        root = ET.parse(sitemap_path).getroot()
    except Exception as exc:
        print(f"ERROR sitemap.xml: {exc}")
        return 1

    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    sitemap_urls = [node.text for node in root.findall(f"{namespace}url/{namespace}loc") if node.text]
    if len(sitemap_urls) < 10:
        errors.append("sitemap.xml contains fewer than 10 URLs")
    if len(sitemap_urls) != len(set(sitemap_urls)):
        errors.append("sitemap.xml contains duplicate URLs")

    robots_text = (ROOT / "robots.txt").read_text(encoding="utf-8", errors="strict")
    if re.search(r"(?im)^\s*Disallow:\s*/\s*$", robots_text):
        errors.append("robots.txt blocks the entire site")
    if not re.search(r"(?im)^\s*User-agent:\s*\*\s*$", robots_text):
        errors.append("robots.txt is missing User-agent: *")
    if not re.search(r"(?im)^\s*Allow:\s*/\s*$", robots_text):
        errors.append("robots.txt is missing Allow: /")
    if "Sitemap: " + BASE_URL + "/sitemap.xml" not in robots_text:
        errors.append("robots.txt does not point to the canonical sitemap")

    for url in sitemap_urls:
        if not url.startswith(BASE_URL + "/"):
            errors.append(f"Non-canonical sitemap URL: {url}")
        if any(token in url for token in ("#", "?", "localhost", "127.0.0.1")):
            errors.append(f"Invalid sitemap URL: {url}")
        path = urlparse(url).path.strip("/")
        page = ROOT / path / "index.html" if path else ROOT / "index.html"
        if not page.exists():
            errors.append(f"Sitemap URL has no local page: {url}")

    pages = [ROOT / "index.html"]
    pages += [ROOT / urlparse(url).path.strip("/") / "index.html" for url in sitemap_urls if urlparse(url).path.strip("/")]
    checked: set[Path] = set()
    for page in pages:
        page = page.resolve()
        if page in checked or not page.exists():
            continue
        checked.add(page)
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8", errors="strict"))
        if not parser.title.strip():
            errors.append(f"Missing title: {page.relative_to(ROOT)}")
        if not parser.description:
            errors.append(f"Missing meta description: {page.relative_to(ROOT)}")
        if not parser.canonical.startswith(BASE_URL + "/"):
            errors.append(f"Invalid canonical: {page.relative_to(ROOT)} -> {parser.canonical}")
        if parser.h1 != 1:
            errors.append(f"Expected one H1, found {parser.h1}: {page.relative_to(ROOT)}")
        for block in parser.schema_blocks:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"Invalid JSON-LD in {page.relative_to(ROOT)}: {exc}")
        for ref in parser.refs:
            target = resolve_ref(page, ref)
            if target and not target.exists():
                errors.append(f"Broken local reference in {page.relative_to(ROOT)}: {ref}")

    print(f"Validated pages: {len(checked)}")
    print(f"Sitemap URLs: {len(sitemap_urls)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("SEO validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
