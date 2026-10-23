# 05: The official website

## Where it is

| Item | Value |
|---|---|
| GitHub repository | `btginredginseng-design/btgin` |
| Working branch | **`claude/charming-turing-l5793z`**. All work is pushed here. Not merged into the default branch; no pull request opened. |
| Commits so far | `84f27ae` site + Instagram kit · `6c7b3dd` real photos · `b9d1208` Reel draft · plus this handoff folder |
| Private preview | https://claude.ai/artifact/XDRoPVXC7EMLKbTc9TcJ8H (Claude artifact; only the founder can open it unless they share it) |
| Public URL | **None yet.** GitHub Pages hasn't been switched on. |
| Domain | None yet. Suggested `yorosum.com` or similar, about $10–15/year. |

## Files

```
index.html                     the whole site: HTML + CSS + JS in one file (~39 KB)
assets/carton-front.jpg        carton panels from the print artwork, used for the 3D box
assets/carton-right.jpg
assets/carton-back.jpg
assets/carton-left.jpg
assets/carton-top.jpg
assets/stick-in-hand.jpg       real photos, colour-corrected, 900 px wide
assets/easy-cut.jpg
assets/powder.jpg
README.md                      how to add links and publish
marketing/                     Instagram kit, Reel draft (see 04 and 06)
docs/handoff/                  these handoff files
```

No build step, framework or dependencies: just a static page. Fonts come from Google Fonts.

## Page structure (top to bottom)

| Section (id) | Content |
|---|---|
| Sticky header | Logo (dot + arcs + YOROSUM + 여러숨), nav (Продукт / Состав / Где купить / Оптом), **RU / EN** switch |
| Hero (pink band) | Eyebrow "Made in Korea · 30 стиков · вкус персика"; big **"YOROSUM / Glow Peptide"**; one-line description; buttons «Где купить» and «Оптовым партнёрам». On the right, a **3D carton built from the real print artwork** that turns slowly by itself and can be dragged to spin (no motion if the visitor has "reduce motion" on). |
| `#product` | "Что в одном стике": four figures (2 000 мг collagen · 100 мг vitamin C · 300 Да · 10 ккал), the 300 Da explanation, then **"Внутри коробки"**: three real photos (stick in hand / Easy Cut / powder). On phones the photos scroll sideways. |
| `#how` | "Как принимать": one stick a day; with water, right after opening; 30 sticks for 30 days. Peach note. |
| `#ingredients` | Full ingredient list in Russian, chips (elastin 0.1% · bamboo 1% · peach 10%), allergens (fish, milk, peach + facility list), storage, cautions; nutrition table per stick and per box |
| `#origin` | "Made in Korea" stamp; manufacturer, distributor, product type (general food / 기타가공품), Korean report no. |
| `#buy` | Two cards: **Uzbekistan 250 000 сум** (Uzum Market, Telegram, Instagram) and **Korea 34 900 ₩** (Naver Smart Store, KakaoTalk) |
| `#wholesale` | Berry block "Оптовым партнёрам": who it's for (pharmacies, cosmetologists, salons, fitness clubs, K-product resellers), stock held in Uzbekistan and Korea, buttons Telegram / Email / WhatsApp |
| Footer | © 2026 · «Пищевой продукт. Не является лекарственным средством.» |

B2B prices are **not** shown publicly ("wholesale price list on request").

## How the language works

- The Russian text is written directly in the HTML; the English text is in a JS dictionary `EN` inside `index.html`. Each translatable element has `data-i18n="key"`; image alt text uses `data-i18n-alt`.
- **First visit:** browsers set to ru, uz, kk, ky, tg, be, uk, az, hy, ka, tk or mn get **Russian**; everyone else gets **English**.
- The visitor's choice is remembered (localStorage). Direct links: `…/#ru` or `…/#en`.
- To add a language (e.g. Uzbek or Korean): add a dictionary like `EN`, a button in `.lang`, and handle it in `setLang()`.

## How to add contact and store links

At the bottom of `index.html`:

```js
const LINKS = {
  telegram: "",   // https://t.me/username
  instagram: "",  // https://instagram.com/handle
  email: "",      // plain address, no "mailto:"
  whatsapp: "",   // https://wa.me/998XXXXXXXXX
  uzum: "",       // Uzum Market product page
  naver: "",      // Naver Smart Store page
  kakao: ""       // KakaoTalk channel
};
```

**All are empty right now**, so every store and contact button shows as a dashed «скоро / soon» chip. Filling a value turns that button into a real link.

## How to publish (free, GitHub Pages)

1. GitHub → repository → **Settings → Pages**.
2. **Deploy from a branch** → pick the branch (merge `claude/charming-turing-l5793z` into the default branch first, or select it directly) → folder `/ (root)` → Save.
3. The site goes live at `https://btginredginseng-design.github.io/btgin/` after about a minute.
4. Optional: add a custom domain on the same page and point the domain's DNS to GitHub.

After a domain exists, add an `og:image` meta tag with an absolute URL, so links shared in Telegram/Instagram show a preview picture.

## Design notes

- Layout idea: the page is the **carton opened up**. The pink top band is the box front; the cream panels below read like the side and back panels.
- Colours and fonts: see `04-brand-and-content-rules.md`. All colours are CSS variables at the top of the `<style>` block, with a full **dark mode**.
- Works at phone width (tested down to 400 px), with safe-area padding for phones with notches.

## Known gaps on the site

- No contact links yet (all «скоро»).
- No Uzbek or Korean version.
- Photos are from an evening shoot and were colour-corrected. Swap them for daylight reshoots when available (`06`).
- No `og:image` (needs a public URL first).
- No analytics. Options: GA4 or Yandex Metrica, which is common in CIS, once the site is public.
- No real order form: a static site can't receive form submissions. Orders go through Telegram/Instagram/marketplaces.
