# Majalah Bitcoin

Selamat datang ke Majalah Bitcoin, sumber berita Bitcoin dan kripto terkini dalam Bahasa Melayu. Laman web ini dibina sebagai laman statik moden, diinspirasikan oleh reka bentuk Bitcoin Magazine, dengan ciri-ciri automasi untuk mendapatkan dan menterjemah berita secara berterusan.

## Ciri-ciri Utama

- **Laman Statik Moden**: Dibina dengan HTML, CSS, dan JavaScript untuk prestasi pantas dan mudah alih.
- **Berita dalam Bahasa Melayu**: Semua kandungan berita diterjemahkan ke Bahasa Melayu menggunakan Gemini API.
- **Data Berasaskan JSON**: Kandungan berita disimpan dalam fail JSON (`data/news.json`) untuk kemudahan pengurusan dan portabiliti.
- **Automasi GitHub Actions**: Aliran kerja GitHub Actions berjalan setiap jam untuk:
    - Mengambil suapan RSS berita Bitcoin percuma.
    - Menterjemah tajuk, ringkasan, dan kandungan berita ke Bahasa Melayu menggunakan Gemini API (percuma).
    - Menyimpan berita yang diterjemah ke dalam `data/news.json`.
    - Melakukan commit perubahan ke repositori.
- **Penyebaran GitHub Pages**: Laman web ini direka untuk disebarkan dengan mudah ke GitHub Pages, dengan sokongan domain tersuai (`majalahbitcoin.com`).
- **Percuma Sepenuhnya**: Menggunakan perkhidmatan dan sumber percuma sepenuhnya.

## Struktur Projek

```
majalahbitcoin/
├── .github/
│   └── workflows/
│       └── fetch_news.yml  # GitHub Actions workflow untuk mengambil berita
├── data/
│   └── news.json           # Fail JSON yang mengandungi data berita
├── scripts/
│   └── fetch_news.py       # Skrip Python untuk mengambil, menterjemah, dan menyimpan berita
├── CNAME                   # Fail untuk domain tersuai GitHub Pages
├── index.html              # Laman utama (senarai berita)
├── berita.html             # Templat laman butiran berita
├── styles.css              # Gaya CSS untuk laman web
├── app.js                  # Logik JavaScript untuk memuatkan dan memaparkan berita
├── detail.js               # Logik JavaScript khusus untuk laman butiran (jika ada)
└── README.md               # Fail ini
```

## Persediaan Projek (Untuk Pembangun)

Untuk menjalankan projek ini secara tempatan atau menyediakannya di repositori GitHub anda:

1.  **Clone Repositori**: 
    ```bash
    git clone https://github.com/majalahbitcoin/majalahbitcoin.git
    cd majalahbitcoin
    ```

2.  **Konfigurasi GitHub Pages**: 
    Pastikan repositori anda dikonfigurasi untuk menggunakan GitHub Pages dari cawangan `main` (atau `gh-pages`) dan direktori root.

3.  **Sediakan Kunci API Gemini**: 
    Aliran kerja GitHub Actions memerlukan `GEMINI_API_KEY` untuk menterjemah berita. Anda perlu mendapatkan kunci API daripada Google AI Studio (percuma) dan menambahkannya sebagai rahsia (secret) di repositori GitHub anda.

    -   Pergi ke [Google AI Studio](https://aistudio.google.com/app/apikey) untuk mendapatkan `GEMINI_API_KEY` anda.
    -   Di repositori GitHub anda, pergi ke `Settings` > `Secrets and variables` > `Actions`.
    -   Klik `New repository secret`.
    -   Namakan rahsia tersebut sebagai `GEMINI_API_KEY` dan masukkan kunci API anda sebagai nilai.

4.  **Uji Skrip Pengambilan Berita (Tempatan)**:
    Anda boleh menguji skrip pengambilan berita secara tempatan (pastikan anda telah menetapkan `GEMINI_API_KEY` sebagai pemboleh ubah persekitaran).
    ```bash
    pip install feedparser requests google-generativeai
    export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    python scripts/fetch_news.py
    ```
    Ini akan mengemas kini `data/news.json` dengan berita terkini.

5.  **Domain Tersuai (majalahbitcoin.com)**:
    Fail `CNAME` disertakan untuk domain tersuai `majalahbitcoin.com`. Pastikan anda mengkonfigurasi rekod DNS di penyedia domain anda untuk menunjuk ke GitHub Pages. Untuk maklumat lanjut, rujuk [Dokumentasi GitHub Pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site).

## Menambah Suapan RSS Baharu

Untuk menambah lebih banyak sumber berita, edit fail `scripts/fetch_news.py` dan tambahkan URL suapan RSS ke dalam senarai `RSS_FEEDS`.

## Sumbangan

Sumbangan dialu-alukan! Sila buka isu atau hantar permintaan tarik (pull request).

## Lesen

Projek ini dilesenkan di bawah lesen MIT. Lihat fail `LICENSE` untuk butiran lanjut. (Nota: Fail LICENSE tidak disertakan dalam persediaan awal ini, tetapi boleh ditambah kemudian.)
