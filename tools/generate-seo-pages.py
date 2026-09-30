"""Generate crawlable SEO pages from data/cities.json.

Only entries marked publish=true are written as public city pages. This keeps
unverified locations out of the sitemap until local coverage data is confirmed.
"""
from __future__ import annotations

import html
import json
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "cities.json"
PACKAGES_PATH = ROOT / "data" / "packages.json"
CITY_TEMPLATE = ROOT / "templates" / "seo-page.html"
SERVICE_TEMPLATE = ROOT / "templates" / "service-page.html"
BASE_URL = "https://www.jatengwifipln.com"
PHONE = "6281339646353"
OG_IMAGE = f"{BASE_URL}/images/promo-september-1.jpg"


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def load_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def load_packages() -> dict:
    return json.loads(PACKAGES_PATH.read_text(encoding="utf-8"))


def replace_tokens(template: str, values: dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def schema_for(title: str, description: str, canonical: str, breadcrumb: str, faq: list[dict]) -> str:
    graph = [
        {
            "@type": "WebPage",
            "@id": canonical + "#webpage",
            "url": canonical,
            "name": title,
            "description": description,
            "isPartOf": {"@id": BASE_URL + "/#website"},
            "inLanguage": "id-ID",
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Beranda", "item": BASE_URL + "/"},
                {"@type": "ListItem", "position": 2, "name": breadcrumb, "item": canonical},
            ],
        },
    ]
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": faq})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))


def area_markup(areas: list[str]) -> str:
    if not areas:
        return "<p>Daftar area detail belum tersedia di project. Ketersediaan jaringan harus diverifikasi berdasarkan alamat pemasangan melalui WhatsApp.</p>"
    return "<ul>" + "".join(f"<li><i class=\"ti ti-map-pin\"></i> {esc(area)}</li>" for area in areas) + "</ul>"


def package_markup(packages: list[dict]) -> str:
    cards = []
    for package in packages:
        speed = package["speed_mbps"]
        highlight = " seo-package-highlight" if speed == 50 else ""
        is_new = speed == 150
        new_class = " seo-package-new" if is_new else ""
        badge = '<span class="seo-package-badge">Paling Dicari</span>' if speed == 50 else ""
        if is_new:
            badge = '<span class="seo-package-badge new">Paket Baru</span>'
        cards.append(
            f"<article class=\"seo-package{highlight}{new_class}\"><strong>{speed} Mbps {badge}</strong>"
            f"<b>{esc(package['price_monthly'])}<span>/bulan</span></b>"
            f"<p>{esc(package['description'])}</p></article>"
        )
    return "".join(cards)


def faq_markup(city: str) -> tuple[str, list[dict]]:
    items = [
        (f"Apakah ICONNET tersedia di {city}?", f"Ketersediaan ICONNET di {city} perlu diperiksa berdasarkan alamat pemasangan. Hubungi tim melalui WhatsApp untuk validasi jaringan di lokasi Anda."),
        (f"Berapa harga paket ICONNET di {city}?", "Harga paket mengikuti informasi yang ditampilkan di halaman harga dan dapat berubah. Konfirmasi harga terbaru sebelum pendaftaran."),
        (f"Bagaimana cara daftar ICONNET di {city}?", f"Kirim alamat pemasangan dan pilihan paket melalui WhatsApp. Tim akan membantu mengecek coverage dan mengatur proses pemasangan di {city}."),
    ]
    markup = "".join(f"<details><summary>{esc(question)}</summary><p>{esc(answer)}</p></details>" for question, answer in items)
    schema = [{"@type": "Question", "name": question, "acceptedAnswer": {"@type": "Answer", "text": answer}} for question, answer in items]
    return markup, schema


def city_page(city: dict, site: dict, packages: dict, template: str) -> str:
    name = city["name"]
    slug = city["slug"]
    canonical = f"{BASE_URL}/{slug}/"
    title = f"Pasang WiFi ICONNET {name} - Harga & Cek Coverage"
    description = f"Cek paket, harga, coverage, dan cara daftar WiFi ICONNET di {name}. Daftar online melalui WhatsApp dan validasi ketersediaan jaringan di alamat Anda."
    faq_markup_html, faq_schema = faq_markup(name)
    wa_text = quote_plus(f"Halo ICONNET, saya ingin cek coverage dan paket di {name}")
    intro = f"Pasang WiFi ICONNET di {name} dengan proses online yang praktis. Kirim alamat pemasangan melalui WhatsApp agar ketersediaan jaringan dapat diverifikasi sebelum Anda memilih paket."
    values = {
        "TITLE": esc(title), "DESCRIPTION": esc(description), "CANONICAL": canonical,
        "OG_IMAGE": OG_IMAGE, "SCHEMA": schema_for(title, description, canonical, f"ICONNET {name}", faq_schema),
        "PHONE": PHONE, "WA_TEXT": wa_text, "BREADCRUMB": esc(f"ICONNET {name}"),
        "REGION_LABEL": esc(city["region"]), "H1": esc(f"Pasang WiFi ICONNET {name}"),
        "INTRO": esc(intro), "CITY": esc(name), "PRICE_NOTE": esc(site["price_note"]),
        "AREAS": area_markup(city["areas"]), "FAQ": faq_markup_html,
        "LOCAL_NOTE": esc(city["local_note"]),
        "PACKAGE_GRID": package_markup(packages["residential"]),
    }
    return replace_tokens(template, values)


def service_page(key: str, title: str, h1: str, intro: str, content: str, template: str) -> str:
    canonical = f"{BASE_URL}/{key}/"
    description = intro
    wa_text = quote_plus("Halo ICONNET, saya ingin konsultasi layanan ICONNET")
    schema = schema_for(title, description, canonical, h1, [])
    values = {
        "TITLE": esc(title), "DESCRIPTION": esc(description), "CANONICAL": canonical,
        "OG_IMAGE": OG_IMAGE, "SCHEMA": schema, "PHONE": PHONE, "WA_TEXT": wa_text,
        "BREADCRUMB": esc(h1), "H1": esc(h1), "INTRO": esc(intro), "CONTENT": content,
    }
    return replace_tokens(template, values)


def service_content(kind: str, packages: dict) -> str:
    if kind == "harga-iconnet":
        title = "Harga Paket ICONNET Oktober 2026 Jawa Tengah & Yogyakarta"
        h1 = "Harga Paket ICONNET"
        intro = "Bandingkan harga reguler ICONNET Oktober 2026, promo XNODEBAT tiga bulan, dan bundling. Seluruh harga paket di halaman ini sudah termasuk PPN 11%."
        content = f"""<section class=\"seo-section\"><div class=\"container\"><div class=\"section-header\"><p class=\"section-label\">Harga Transparan</p><h2 class=\"section-title\">Paket ICONNET Oktober 2026</h2><p class=\"section-sub\">Harga sudah termasuk PPN 11%. Promo dan coverage dikonfirmasi berdasarkan alamat pemasangan.</p></div><div class=\"seo-package-grid\">{package_markup(packages['residential'])}</div><p class=\"seo-note\">{esc(packages['tax_note'])} Tanyakan harga Promo XNODEBAT dan tarif bundling melalui WhatsApp.</p></div></section><section class=\"seo-section seo-section-alt\"><div class=\"container seo-two-column\"><div><h2>Cek harga sesuai lokasi</h2><p>Harga dan ketersediaan dapat bergantung pada area layanan. Lanjutkan ke halaman coverage atau hubungi tim untuk validasi alamat.</p></div><div><a class=\"btn-card primary\" href=\"/cek-coverage-iconnet/\">Cek Coverage</a> <a class=\"btn-card\" href=\"/cara-daftar-iconnet/\">Cara Daftar</a></div></div></section>"""
    elif kind == "cara-daftar-iconnet":
        title = "Cara Daftar ICONNET Online Jawa Tengah & Yogyakarta"
        h1 = "Cara Daftar ICONNET Online"
        intro = "Ikuti langkah pendaftaran ICONNET melalui WhatsApp, mulai dari mengirim alamat hingga penjadwalan instalasi."
        content = """<section class=\"seo-section\"><div class=\"container\"><div class=\"section-header\"><p class=\"section-label\">Empat Langkah</p><h2 class=\"section-title\">Proses Pemasangan ICONNET</h2></div><ol class=\"seo-steps\"><li><b>01</b><span>Chat WhatsApp dan kirim share lokasi pemasangan.</span></li><li><b>02</b><span>Pilih paket sesuai kebutuhan setelah coverage diperiksa.</span></li><li><b>03</b><span>Lengkapi validasi data dan pembayaran sesuai arahan.</span></li><li><b>04</b><span>Tentukan jadwal teknisi dan tunggu instalasi selesai.</span></li></ol></div></section><section class=\"seo-section seo-section-alt\"><div class=\"container seo-two-column\"><div><h2>Siapkan informasi berikut</h2><p>Alamat lengkap, share location, nama pelanggan, nomor WhatsApp aktif, dan paket yang diminati akan membantu proses validasi.</p></div><div><a class=\"btn-primary\" href=\"https://wa.me/6281339646353?text=Halo+ICONNET%2C+saya+ingin+daftar\" target=\"_blank\" rel=\"noopener noreferrer nofollow\"><i class=\"ti ti-brand-whatsapp\"></i> Mulai Daftar</a></div></div></section>"""
    else:
        title = "Cek Coverage ICONNET Jawa Tengah & Yogyakarta"
        h1 = "Cek Coverage ICONNET"
        intro = "Cek ketersediaan jaringan ICONNET berdasarkan alamat pemasangan sebelum memilih paket dan menjadwalkan instalasi."
        content = """<section class=\"seo-section\"><div class=\"container seo-two-column\"><div><p class=\"section-label\">Validasi Alamat</p><h2>Cara cek ketersediaan jaringan</h2><p>Kirim share location atau alamat lengkap melalui WhatsApp. Tim akan membantu memeriksa jaringan yang tersedia di lokasi tersebut.</p><a class=\"btn-primary\" href=\"https://wa.me/6281339646353?text=Halo+ICONNET%2C+saya+ingin+cek+coverage\" target=\"_blank\" rel=\"noopener noreferrer nofollow\"><i class=\"ti ti-brand-whatsapp\"></i> Kirim Lokasi</a></div><div class=\"seo-area-box\"><h3>Informasi yang perlu dikirim</h3><ul><li><i class=\"ti ti-map-pin\"></i> Alamat lengkap pemasangan</li><li><i class=\"ti ti-location\"></i> Share location realtime</li><li><i class=\"ti ti-package\"></i> Pilihan paket jika sudah ada</li></ul></div></div></section><section class=\"seo-section seo-section-alt\"><div class=\"container\"><div class=\"section-header\"><p class=\"section-label\">Langkah Berikutnya</p><h2 class=\"section-title\">Setelah coverage terkonfirmasi</h2><p class=\"section-sub\">Tim akan membantu proses validasi, pembayaran, dan penjadwalan instalasi sesuai ketersediaan.</p></div><div class=\"seo-benefit-grid\"><article><i class=\"ti ti-check\"></i><h3>Pilih paket</h3><p>Sesuaikan kecepatan dengan kebutuhan rumah atau usaha.</p></article><article><i class=\"ti ti-calendar\"></i><h3>Atur jadwal</h3><p>Tentukan waktu pemasangan dengan tim teknisi.</p></article><article><i class=\"ti ti-wifi\"></i><h3>Internet aktif</h3><p>Nikmati koneksi setelah proses instalasi selesai.</p></article></div></div></section>"""
    return title, h1, intro, content


def main() -> None:
    data = load_data()
    site = data["site"]
    packages = load_packages()
    city_template = CITY_TEMPLATE.read_text(encoding="utf-8")
    service_template = SERVICE_TEMPLATE.read_text(encoding="utf-8")
    for city in data["cities"]:
        if not city.get("publish"):
            continue
        target = ROOT / city["slug"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(city_page(city, site, packages, city_template), encoding="utf-8")
    services = ["harga-iconnet", "cara-daftar-iconnet", "cek-coverage-iconnet"]
    for key in services:
        title, h1, intro, content = service_content(key, packages)
        target = ROOT / key / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(service_page(key, title, h1, intro, content, service_template), encoding="utf-8")
    print("Generated published city pages:", sum(1 for city in data["cities"] if city.get("publish")))
    print("Generated service pages:", len(services))
    print("Unpublished city entries awaiting local verification:", sum(1 for city in data["cities"] if not city.get("publish")))


if __name__ == "__main__":
    main()
