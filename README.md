# YOROSUM Glow Peptide — official site

One-page bilingual site (Russian by default, English switch) for YOROSUM Glow Peptide.

- `index.html` — the whole site (HTML, CSS and JS in one file)
- `assets/` — carton panel artwork used for the turning 3D box
- `marketing/instagram-launch-ru.md` — Instagram bio and the first six launch posts, in Russian

## Add your links

Open `index.html`, find `const LINKS` near the bottom, and paste your URLs:

```js
const LINKS = {
  telegram: "https://t.me/your_username",
  instagram: "https://instagram.com/your_handle",
  email: "you@example.com",
  whatsapp: "https://wa.me/998XXXXXXXXX",
  uzum: "",   // Uzum Market product page
  naver: "",  // Naver Smart Store page
  kakao: ""   // KakaoTalk channel
};
```

Any link left empty shows as a dashed "скоро / soon" button, so the page never shows a dead link.

## Language

Visitors whose browser is set to Russian, Uzbek, Kazakh, Kyrgyz and other CIS languages see Russian; everyone else sees English. The RU / EN switch is remembered. You can link straight to a language with `#ru` or `#en`.

## Put it online for free (GitHub Pages)

1. On GitHub, open the repository → **Settings** → **Pages**.
2. Under **Build and deployment**, pick **Deploy from a branch**, choose the branch and the `/ (root)` folder, and save.
3. After a minute the site is live at `https://<your-github-name>.github.io/<repo>/`.
4. Optional: buy a domain (for example `yorosum.com`, about $10–15 a year) and add it under **Custom domain** on the same page.

## Product facts used on the page

All figures come from the carton artwork (95 × 60 × 143 mm single-unit carton): 30 sticks × 3 g, 2,000 mg fish collagen, 100 mg vitamin C, 300 Da average molecular weight, 10 kcal per stick, peach flavour. Manufacturer Hankook CNS Pharm, Korean product report no. 20030445025-912. If the formula or label changes, update the page to match.
