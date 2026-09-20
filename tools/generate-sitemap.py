"""Generate sitemap.xml from crawlable static HTML pages."""
from __future__ import annotations

import re
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://www.jatengwifipln.com"
SITEMAP_PATH = ROOT / "sitemap.xml"
EXCLUDED_SITEMAP_PATHS = {"privacy-policy.html", "syarat-ketentuan.html"}


def is_crawlable(page: Path, text: str) -> bool:
    if page.stat().st_size == 0:
        return False
    if not re.search(r"(?is)<title\b[^>]*>\s*.+?\s*</title>", text):
        return False
    if not re.search(r'(?is)<meta\b[^>]+name=["\']description["\'][^>]+content=["\'][^"\']+?["\']', text):
        return False
    canonical = re.search(r'(?is)<link\b[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', text)
    if not canonical or canonical.group(1) != page_url(page):
        return False
    if len(re.findall(r"(?is)<h1\b", text)) != 1:
        return False
    if re.search(r'(?is)<meta\b[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', text):
        return False
    return True


def page_url(page: Path) -> str:
    relative = page.relative_to(ROOT).as_posix()
    if relative == "index.html":
        return BASE_URL + "/"
    if relative.endswith("/index.html"):
        return BASE_URL + "/" + relative[:-len("index.html")]
    return BASE_URL + "/" + relative


def main() -> None:
    urls: list[str] = []
    for page in ROOT.rglob("*.html"):
        if any(part in {".git", "backup", "templates"} for part in page.parts):
            continue
        if page.relative_to(ROOT).as_posix() in EXCLUDED_SITEMAP_PATHS:
            continue
        text = page.read_text(encoding="utf-8", errors="ignore")
        if is_crawlable(page, text):
            urls.append(page_url(page))

    urls = sorted(set(urls), key=lambda url: (url != BASE_URL + "/", url))
    root = Element("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
    for url in urls:
        item = SubElement(root, "url")
        SubElement(item, "loc").text = url
    xml = minidom.parseString(tostring(root, encoding="utf-8")).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    SITEMAP_PATH.write_text(xml, encoding="utf-8")
    print(f"Generated sitemap URLs: {len(urls)}")
    for url in urls:
        print(url)


if __name__ == "__main__":
    main()
