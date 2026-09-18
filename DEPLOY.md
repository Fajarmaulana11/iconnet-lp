# Deploy Otomatis ke Rumahweb cPanel

Repo ini adalah **static site** (HTML/CSS/JS murni). Tidak ada langkah kompilasi, jadi
"build" di sini berarti: validasi aset → sinkronisasi file ke `public_html` di hosting.

## Generate halaman SEO

Sumber data kota berada di `data/cities.json`. Jalankan generator setelah mengubah data:

```bash
python tools/generate-seo-pages.py
```

Hanya kota dengan `publish: true` yang dibuat sebagai halaman publik. Kota lain tetap
tercatat di registry sampai informasi area lokalnya dikonfirmasi, sehingga tidak membuat
halaman doorway dengan klaim coverage yang belum diverifikasi.

Sitemap dibuat otomatis dari halaman HTML yang memiliki title, meta description,
canonical yang benar, dan tepat satu H1:

```bash
python tools/generate-sitemap.py
```

## Alur

| Event                   | Yang terjadi                            |
| ----------------------- | --------------------------------------- |
| Pull request ke `main`  | Hanya job `validate` (quality gate)     |
| Push / merge ke `main`  | `validate` → `deploy` (upload via FTPS) |
| Manual dari tab Actions | Sama seperti push ke `main`             |

Workflow: `.github/workflows/deploy.yml`

## Setup sekali saja

### 1. Siapkan jalur FTP di cPanel

Di cPanel Rumahweb buka **FTP Accounts**. Dua pilihan:

- **Pakai akun FTP utama** (dibuat saat provisioning hosting). Root-nya biasanya sudah
  `public_html`, jadi `FTP_SERVER_DIR` bisa `/public_html/` atau `./`.
- **Buat FTP account khusus** yang directory-nya diarahkan ke `public_html`. Ini lebih aman
  karena kredensialnya hanya bisa menyentuh folder web.

Catat: hostname, username, password, dan direktori tujuan.

### 2. Tambahkan GitHub Secrets

Di repo GitHub → **Settings → Secrets and variables → Actions → New repository secret**.
Buat empat secret berikut:

| Secret           | Contoh                     | Catatan                              |
| ---------------- | -------------------------- | ------------------------------------ |
| `FTP_SERVER`     | `ftp.jatengwifipln.com`    | Tanpa `ftp://`, tanpa trailing slash |
| `FTP_USERNAME`   | `deploy@jatengwifipln.com` | Sesuai akun FTP                      |
| `FTP_PASSWORD`   | `••••••••`                 |                                      |
| `FTP_SERVER_DIR` | `/public_html/`            | **Wajib diakhiri `/`**               |

`FTP_SERVER_DIR` opsional; jika dikosongkan, workflow memakai `./` (root akun FTP).
Kalau akun FTP Anda di-root ke `public_html`, biarkan kosong pun aman.

### 3. Jalankan pertama kali

Push ke `main`, atau buka **Actions → Build & Deploy → Run workflow**. Run pertama akan
mengunggah seluruh file (karena server belum punya state sinkronisasi). Run berikutnya
hanya mengirim file yang berubah.

## File yang TIDAK di-deploy

Aset development sengaja dikecualikan di `exclude` workflow agar tidak bisa diakses publik:

```
SEO-AUDIT.md  DEPLOY.md  *.py  requirements.txt
seo-*.json  competitor-urls.json  blog.zip  .github/  .git/
```

Jika nanti ada file baru yang hanya untuk dev, tambahkan polanya ke blok `exclude` di
`.github/workflows/deploy.yml`.

## Catatan penting

- **`dangerous-clean-slate` sengaja tidak diaktifkan.** Artinya file di `public_html` yang
  tidak ada di repo (mis. `.well-known/`, file verifikasi Search Console, atau aplikasi lain)
  **tidak akan terhapus**. Kalau ingin `public_html` benar-benar cermin dari repo, set
  `dangerous-clean-slate: true` — tapi pahami risikonya dulu.
- **Selalu cek dulu sebelum push ke `main`.** Push ke `main` langsung tayang ke produksi.
  Kalau ingin lebih aman, buat branch `staging` + FTP account terpisah dan duplikasi workflow
  dengan `on.push.branches: [staging]`.
- **Protokol FTP.** Workflow memakai `protocol: ftp` karena koneksi FTPS Rumahweb memutus
  transfer di tengah proses. FTP tidak mengenkripsi kredensial maupun data; bila Rumahweb
  sudah mendukung FTPS secara stabil, ubah kembali ke `protocol: ftps`.
- **Alternatif tanpa action pihak ketiga:** `lftp` sudah tersedia di runner GitHub dan bisa
  dipakai untuk `mirror -R`. Action `SamKirkland/FTP-Deploy-Action` dipilih karena menangani
  incremental sync + state, yang lebih efisien untuk site yang makin banyak halaman.
- **Repo belum punya `.github/`.** Setelah file ini di-commit dan di-push, workflow langsung
  aktif.

## Verifikasi

Setelah run pertama sukses:

1. Buka `https://www.jatengwifipln.com/` — pastikan versi terbaru yang tayang.
2. Cek `https://www.jatengwifipln.com/sitemap.xml` — pastikan isinya sesuai `sitemap.xml` di repo.
3. Pastikan file dev tidak bocor, mis. `https://www.jatengwifipln.com/SEO-AUDIT.md` harus 404.
