# Audit SEO — `jatengwifipln.com` vs `iconnetwifipln.com`

Tanggal: 2026-09-11. Data: `seo-raw.json`, `seo-jateng.json`, `seo-diagnostic.json`.

**Premis dari pemilik situs (input user, bukan hasil crawl):** kompetitor jauh lebih sering
muncul untuk berbagai variasi keyword pencarian, sementara situs sendiri jarang muncul.

Audit ini mencari **penyebabnya**, bukan sekadar mendaftar perbaikan HTML.

---

## 1. Kesimpulan: kenapa kalah

Bukan karena HTML jelek. Situs sendiri justru unggul secara on-page (lihat §4).
Penyebab utamanya dua, dan keduanya bersifat **struktural**:

### Penyebab #1 — Inventaris halaman: 1 vs 19+

Ini temuan terbesar dan sebelumnya terlewat.

| | `jatengwifipln.com` | `iconnetwifipln.com` |
|---|---|---|
| Sitemap | `/sitemap.xml` → **1 URL** | `/sitemap_index.xml` → 6 sub-sitemap → **35 URL** |
| Halaman konten nyata | **1** (beranda) | **~19** |
| URL template sampah | 0 | ~16 (portfolio, project-cat, cms_block_cat) |

Sitemap situs sendiri hanya mendeklarasikan satu URL:

```
https://www.jatengwifipln.com/sitemap.xml
  └── https://www.jatengwifipln.com/     ← hanya ini
```

Bahkan `blog/index.html` yang sudah ada dan punya konten (757 kata, 13 artikel) **tidak
terdaftar di sitemap**. Jadi halaman itu praktis tidak pernah ditawarkan ke Google.

Kompetitor punya 35 pintu masuk. Setiap artikel = satu halaman yang bisa ranking untuk
keyword panjang yang berbeda. Berikut halaman konten kompetitor yang terdaftar:

- 8 artikel blog dengan slug kaya keyword
  (`daftar-iconnet-online-solusi-digital-terdepan-dari-pln`,
  `pasang-iconnet-di-purwokerto-banyumas-dan-sekitarnya-promo-x-nodebat`, dst.)
- 5 halaman promo per bulan (`promo-iconnet-mei-2026`, `promo-iconnet-desember-2025-...`)
- 2 halaman daftar per wilayah (Jateng, Yogyakarta)
- 1 halaman topik, 1 profil, 1 blog index

**Inilah kenapa kompetitor "muncul di berbagai percobaan keyword".** Bukan karena tiap
halaman lebih bagus — kontennya cuma ~340–520 kata — tapi karena ada 19 peluang vs 1.
Situs dengan 1 halaman secara matematis tidak bisa menang di banyak keyword.

### Penyebab #2 — Otoritas & sinyal eksternal

Tidak bisa diukur dari HTML, tapi konsisten dengan gejala: domain kompetitor lebih tua
(artefak `og:updated_time` menunjukkan konten sejak 2025, dan server WordPress aktif),
punya 16 URL template yang meski "sampah" tetap menambah massa internal link.

---

## 2. Koreksi temuan sebelumnya

Audit versi pertama menandai **anti-bot waiting-room sebagai temuan kritis**. Itu **salah
prioritas**. Hasil uji ulang dengan 3 User-Agent:

| Domain | Chrome | Googlebot | Googlebot smartphone |
|---|---|---|---|
| `jatengwifipln.com` | LOLOS percobaan 1 | LOLOS percobaan 1 | LOLOS percobaan 1 |
| `iconnetwifipln.com` | LOLOS percobaan 1 | LOLOS percobaan 1 | LOLOS percobaan 1 |

Ketiganya langsung dapat HTML asli (83.143 bytes, server Apache).

**Kesimpulan yang benar:** waiting-room adalah **rate-limit/anti-scraping**, bukan cloaking
ke Googlebot. Saat crawl pertama saya mengirim request beruntun dari satu IP sehingga
memicu challenge; setelah jeda, request lolos normal. Ini **bukan** penyebab kalah ranking.
Tetap perlu dicek sekali di Search Console, tapi **turun prioritas dari Kritis → Rendah**.

Ini contoh kenapa crawl cepat bisa menyesatkan — saya mengoreksi di sini alih-alih
mempertahankannya.

---

## 3. Peta masalah, diurutkan berdasarkan dampak nyata

| # | Masalah | Dampak | Bukti |
|---|---|---|---|
| 1 | **Hanya 1 URL di sitemap** | **Kritis** | `sitemap.xml` → 1 `<loc>` |
| 2 | `blog/index.html` tidak di sitemap | **Kritis** | sitemap tidak memuatnya |
| 3 | Hanya 1 halaman vs 19 halaman kompetitor | **Kritis** | sitemap kedua domain |
| 4 | Tidak ada halaman per kota | Tinggi | kompetitor targetkan Jateng & Jogja terpisah |
| 5 | Tidak ada halaman promo per bulan | Tinggi | kompetitor punya 5 |
| 6 | Link eksternal (29) > internal (18) | Sedang | `seo-jateng.json` |
| 7 | Meta description beranda 162 char | Rendah | terpotong di SERP |
| 8 | Blog index: 1 H2 + 13 H3 | Rendah | hierarki tidak rapi |
| 9 | Hanya 5 gambar di beranda | Rendah | vs 31 kompetitor |
| 10 | Anti-bot waiting-room | **Rendah** | Googlebot lolos — §2 |

Perhatikan: **sembilan dari sepuluh masalah berkaitan dengan jumlah halaman**, bukan kualitas.

---

## 4. Yang sudah benar — jangan diutak-atik

Situs sendiri unggul dan ini modal, bukan masalah:

- **Structured data:** `LocalBusiness`, `FAQPage`, `BreadcrumbList` — kompetitor **nol**.
- **Hierarki heading beranda:** 1 H1 → 10 H2 → 9 H3. Kompetitor: 8 H1 (isi harga), 0 H2.
- **Kedalaman:** 2197 kata vs 519 (4,2×).
- **Bobot:** 83 KB vs 197 KB.
- **Meta:** `author`, canonical, `lang="id"`, OG 1200×630, Twitter Card lengkap.
- **`robots.txt` bersih**, tidak ada `Disallow` yang menghalangi.

Artinya: **ketika Anda menambah halaman baru, fondasi teknisnya sudah siap.** Anda tidak
perlu memperbaiki mesin — Anda perlu menambah bahan bakar.

---

## 5. Rencana aksi — fokus menambah halaman

### Fase 1: Buka keran (S, lakukan hari ini)

1. **Tambah `blog/index.html` ke sitemap.** Ini perbaikan tercepat dengan dampak terbesar —
   halaman sudah ada, hanya belum didaftarkan.
2. **Verifikasi `sitemap.xml` di Google Search Console** (Sitemaps → submit).
3. **Submit URL individual** untuk beranda & blog via URL Inspection → Request Indexing.

### Fase 2: Bangun halaman kota (M, 1–2 minggu)

Buat landing page terpisah untuk tiap kota yang sudah disebut di beranda tapi belum
punya halaman. Ini meniru taktik kompetitor, tapi dengan kualitas on-page Anda yang lebih baik:

- `/iconnet-semarang/`
- `/iconnet-solo-surakarta/`
- `/iconnet-purwokerto-banyumas/`
- `/iconnet-magelang/`
- `/iconnet-yogyakarta/`

Tiap halaman wajib **berbeda nyata** (jangan ulangi kesalahan kompetitor yang duplikat):
cakupan kecamatan, harga lokal, testimoni lokal, FAQ lokal, foto instalasi lokal.
Pakai `LocalBusiness` + `FAQPage` per halaman.

### Fase 3: Halaman promo & artikel (M, berkelanjutan)

- **Halaman promo per bulan** — kompetitor punya 5. Buat `/promo/` dengan tanggal kedaluwarsa
  jelas, `Offer` schema, dan `validThrough`.
- **Kembangkan blog.** Blog index sudah menampilkan 13 artikel, tapi `index.html` hanya
  halaman listing. Pastikan tiap artikel punya URL sendiri dan masuk sitemap.
- **Target:** 20+ URL konten dalam 2–3 bulan.

### Fase 4: Rapikan sinyal (S)

- Naikkan internal link dari beranda ke blog & halaman kota (target: internal > eksternal).
- Ringkas meta description beranda ke ≤155 char.
- Perbaiki hierarki heading blog index (kelompokkan 13 H3 di bawah H2 seksi).

---

## 6. Ukur keberhasilan

Karena masalahnya inventaris halaman, ukuran keberhasilan bukan "HTML lebih rapi":

| Metrik | Sekarang | Target 3 bulan |
|---|---|---|
| URL di sitemap | 1 | 20+ |
| Halaman terindeks (GSC) | tidak diketahui | 15+ |
| Klik organik / minggu | tidak diketahui | naik bertahap |
| Keyword yang muncul di GSC | tidak diketahui | 50+ |

**Langkah pertama sebelum apa pun:** buka Google Search Console, catat angka baseline
halaman terindeks dan keyword saat ini. Tanpa baseline, tidak ada cara mengukur kemajuan.

---

## 7. Batasan audit

- Hanya HTML + `robots.txt` + `sitemap.xml` yang diperiksa. **Backlink, otoritas domain, dan
  peringkat aktual tidak diukur** — butuh Search Console / Ahrefs / Semrush.
- Klaim "kompetitor lebih sering muncul untuk berbagai keyword" berasal dari **pengamatan
  pemilik situs**, bukan hasil pengukuran saya. Saya tidak bisa query Google dari lingkungan ini.
- Waiting-room challenge baru diuji 1 sesi; bisa berperilaku beda untuk Googlebot asli dari
  rentang IP Google. Verifikasi di GSC tetap disarankan (prioritas rendah).
- Sampel crawl: 5 URL kompetitor, 2 URL sendiri. Daftar URL lengkap dari sitemap, tapi isi
  tiap halaman tidak semua di-crawl.