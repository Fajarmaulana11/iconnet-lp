"""
SERP & Competitor Content Research Tool
untuk jatengwifipln.com (ICONNET Jateng & Yogyakarta)

Setup:
    pip install -r requirements.txt
    PowerShell: $env:SERPER_API_KEY = "isi-api-key-serper"
    python serp_keyword_research.py

Output:
    hasil_riset_kompetitor.xlsx

Catatan etika dan legal:
- Script ini tidak mengakses google.com secara langsung. Data SERP diambil
  melalui API Serper.dev.
- Halaman publik kompetitor hanya dianalisis untuk struktur SEO on-page.
  Jangan menyalin atau menerbitkan ulang konten kompetitor.
- Beri jeda antar request agar tidak membebani server yang dianalisis.
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

# =========================
# KONFIGURASI
# =========================
API_KEY = os.getenv("SERPER_API_KEY", "").strip()
SERPER_URL = "https://google.serper.dev/search"
OUTPUT_FILE = Path(__file__).with_name("hasil_riset_kompetitor.xlsx")
GL = "id"
HL = "id"
NUM_RESULTS = 10
DELAY_SECONDS = 2
REQUEST_TIMEOUT = 15

KEYWORDS = [
    "pasang wifi iconnet semarang",
    "iconnet jogja harga",
    "wifi fiber optik pln jawa tengah",
    "cara daftar iconnet",
    "biaya pemasangan iconnet",
    "iconnet vs indihome",
    "wifi iconnet magelang",
    "wifi iconnet solo",
    "iconnet yogyakarta terdekat",
    "internet pln fiber optic murah",
]

HEADERS_BROWSER = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def get_serp_results(session: requests.Session, keyword: str) -> list[dict[str, Any]]:
    """Ambil hasil organik top-N dari Serper.dev untuk satu keyword."""
    payload = {"q": keyword, "gl": GL, "hl": HL, "num": NUM_RESULTS}
    headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}

    try:
        response = session.post(
            SERPER_URL,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("organic", [])[:NUM_RESULTS]
    except (requests.RequestException, ValueError) as error:
        print(f"  [!] Gagal ambil SERP untuk '{keyword}': {error}")
        return []


def analyze_page(session: requests.Session, url: str) -> dict[str, Any]:
    """Ekstrak elemen SEO on-page dari satu halaman publik."""
    result: dict[str, Any] = {
        "url": url,
        "title": "",
        "meta_description": "",
        "h1": [],
        "h2": [],
        "h3": [],
        "word_count": 0,
        "has_schema": False,
    }

    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        print(f"  [!] Lewati URL tidak valid: {url}")
        return result

    try:
        response = session.get(
            url,
            headers=HEADERS_BROWSER,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        if soup.title:
            result["title"] = soup.title.get_text(" ", strip=True)

        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            result["meta_description"] = meta["content"].strip()

        result["h1"] = [heading.get_text(" ", strip=True) for heading in soup.find_all("h1")]
        result["h2"] = [heading.get_text(" ", strip=True) for heading in soup.find_all("h2")]
        result["h3"] = [heading.get_text(" ", strip=True) for heading in soup.find_all("h3")]

        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        body_text = soup.get_text(separator=" ", strip=True)
        result["word_count"] = len(re.findall(r"\w+", body_text, flags=re.UNICODE))
        result["has_schema"] = bool(
            soup.find("script", attrs={"type": "application/ld+json"})
        )
    except requests.RequestException as error:
        print(f"  [!] Gagal analisis {url}: {error}")

    return result


def main() -> None:
    if not API_KEY:
        raise SystemExit(
            "[!] SERPER_API_KEY belum diisi. "
            "Set environment variable tersebut sebelum menjalankan script."
        )

    all_rows: list[dict[str, Any]] = []
    heading_summary: list[dict[str, str]] = []

    with requests.Session() as session:
        for keyword_index, keyword in enumerate(KEYWORDS):
            print(f"[+] Riset keyword: {keyword}")
            organic_results = get_serp_results(session, keyword)

            for rank, item in enumerate(organic_results, start=1):
                url = item.get("link", "")
                if not url:
                    continue

                print(f"    - Rank {rank}: {url}")
                page_data = analyze_page(session, url)

                all_rows.append(
                    {
                        "keyword": keyword,
                        "rank": rank,
                        "url": url,
                        "serp_title": item.get("title", ""),
                        "serp_snippet": item.get("snippet", ""),
                        "page_title_tag": page_data["title"],
                        "meta_description": page_data["meta_description"],
                        "word_count": page_data["word_count"],
                        "has_schema_markup": page_data["has_schema"],
                        "jumlah_h1": len(page_data["h1"]),
                        "jumlah_h2": len(page_data["h2"]),
                        "jumlah_h3": len(page_data["h3"]),
                    }
                )

                for heading in page_data["h1"] + page_data["h2"]:
                    heading_summary.append(
                        {"keyword": keyword, "url": url, "heading": heading}
                    )

                time.sleep(DELAY_SECONDS)

            if keyword_index < len(KEYWORDS) - 1:
                time.sleep(DELAY_SECONDS)

    df_main = pd.DataFrame(all_rows)
    df_headings = pd.DataFrame(heading_summary)

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        df_main.to_excel(writer, sheet_name="Ringkasan Kompetitor", index=False)
        df_headings.to_excel(writer, sheet_name="Heading Kompetitor", index=False)

    print(f"\n[OK] Selesai! Lihat file: {OUTPUT_FILE}")
    print("     Sheet 'Ringkasan Kompetitor': title, meta, word count, schema per URL")
    print("     Sheet 'Heading Kompetitor': H1/H2 kompetitor untuk mencari gap konten")


if __name__ == "__main__":
    main()
