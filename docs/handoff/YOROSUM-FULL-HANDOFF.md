# YOROSUM Glow Peptide: full project handoff

All handoff files in one document (sections 00–07), plus the full Instagram launch kit as Appendix A. Last updated 23 October 2026.

---

<!-- source: docs/handoff/00-START-HERE.md -->

## YOROSUM Glow Peptide: project handoff (start here)

This folder is the full record of the first planning and build session for **YOROSUM Glow Peptide**, a collagen stick brand. It is written so that a new Claude chat, or any person, can continue the work without reading the old conversation.

Last updated: **23 October 2026**.

---

### How to use these files in a new Claude chat

1. Open a new chat.
2. Attach **`YOROSUM-FULL-HANDOFF.md`**. It contains every file below in one document. Or attach the numbered files one by one.
3. Paste the starter prompt below as your first message.
4. If you want the new chat to edit the website or the Reel, also give it access to the GitHub repository `btginredginseng-design/btgin` (branch `claude/charming-turing-l5793z`).

#### Starter prompt (copy and paste)

```
I'm the founder of YOROSUM, a collagen supplement brand. I work alone with a small budget.
The attached handoff file is the full record of my previous planning session: business numbers,
product facts from the label, sales strategy, brand rules, the website, the Instagram plan,
photo and video analysis, and an open-questions list.

Please read all of it first. Treat the product facts as exact (they come from the printed label)
and follow the claims rules in the brand file: no medical or beauty-effect claims.

Then help me with the next step: [WRITE WHAT YOU WANT TO DO NEXT]
```

---

### Files in this folder

| File | What it covers |
|---|---|
| `00-START-HERE.md` | This page: how to use the files, snapshot, index |
| `01-business-and-goals.md` | Founder situation, stock, prices, revenue maths, goals |
| `02-product-facts.md` | Everything printed on the carton and stick: formula, nutrition, ingredients, allergens, legal data, print spec |
| `03-sales-strategy-and-channels.md` | Market priorities, channels per country, regulatory checks, 30-day plan, AI automation |
| `04-brand-and-content-rules.md` | Brand identity, colours, fonts, voice, claims rules (what you may and may not say), Instagram launch kit |
| `05-website.md` | The bilingual website: repo, files, sections, how to edit links, how to publish |
| `06-media-assets-and-reel.md` | Analysis of all photos and videos, the Reel draft and how it was made, reshoot list |
| `07-status-open-questions-next-steps.md` | What is done, what is waiting on the founder, prioritised next steps, decision log |
| `YOROSUM-FULL-HANDOFF.md` | All of the above in one file |

---

### 60-second snapshot

- **Brand:** YOROSUM (Korean: 여러숨, read "yeo-reo-sum"). **Product:** Glow Peptide, low-molecular fish collagen in daily sticks.
- **Format:** 30 sticks × 3 g per box (90 g). Per stick: **2,000 mg fish collagen** (average molecular weight **300 Da**), **100 mg vitamin C**, peach flavour, 10 kcal.
- **Made in Korea** by an OEM (Hankook CNS Pharm Co., Ltd.). Registered in Korea as a **general food (기타가공품, "other processed food")**, not as a health functional food. Use-by date of this batch: **15 Sep 2028**.
- **Stock:** 1,500 boxes in **Uzbekistan** and 1,500 boxes in **South Korea**.
- **Prices:**
  - Uzbekistan: B2B 120,000 sum, retail 250,000 sum.
  - Korea: B2B 10,500 won + VAT, retail list 34,900 won, lowest promo 19,900 won.
- **Main target:** Russian-speaking countries. Content is in **Russian**; the brand presents itself in **English** to look international.
- **Founder:** works alone, no employees, small budget, no plan to hire yet. Writes to Claude in English.
- **Built so far:**
  - A bilingual website (Russian default, English switch) in the GitHub repo.
  - A Russian Instagram launch kit: bio plus six posts.
  - Colour-corrected product photos on the site.
  - A 15.6-second Instagram Reel draft with Russian captions.
- **Not done yet:**
  - No social accounts, marketplace listings or contact links exist yet.
  - The website is not public yet; GitHub Pages is not switched on.
  - A daylight photo reshoot is needed.

---

<!-- source: docs/handoff/01-business-and-goals.md -->

## 01: Business situation and goals

### The founder

- Founded the brand **YOROSUM** and had the first product, **Glow Peptide**, made by a Korean OEM manufacturer.
- Works **completely alone**: no employees, and no plan to hire yet because the budget is limited.
- At the start of the session there was **no sales plan, no sales channel, no social media pages, nothing**. The product was finished and in stock.
- Wants to use **AI to automate the digital work**: sales planning, building an online presence, making content.
- Writes to Claude in English. Customer-facing content must be in **Russian**.
- Wants an **official website in English** so the product looks international, with the **main content in Russian** because the core market is Russian-speaking countries.

### Stock

| Location | Units (boxes of 30 sticks) |
|---|---|
| Uzbekistan | 1,500 |
| South Korea | 1,500 |
| **Total** | **3,000** |

The batch on the artwork is lot **RA88201**, use by **15 Sep 2028**. That leaves almost two years, so there is no pressure to discount to clear stock.

### Prices set by the founder

#### Uzbekistan (sum, UZS)
| Level | Price per box |
|---|---|
| B2B (wholesale) | 120,000 sum |
| B2C (retail) | 250,000 sum |

- A shop buying at 120,000 and selling at 250,000 keeps 130,000 sum: **52% of the retail price** (a 108% markup). That is attractive for pharmacies, salons and resellers.
- Retail per day of use: 250,000 ÷ 30 = **about 8,333 sum per stick**.

#### South Korea (won, KRW)
| Level | Price per box |
|---|---|
| B2B (wholesale) | 10,500 won + VAT (10% VAT → 11,550 won) |
| B2C list price | 34,900 won |
| Lowest promotional price | 19,900 won |

- B2B is 70% below the list price and 47% below the lowest promo price.
- Retail per day: 34,900 ÷ 30 ≈ **1,163 won per stick**; at promo, 19,900 ÷ 30 ≈ **663 won per stick**.

### Revenue ceilings (gross, before any costs)

The OEM cost per unit is **not known yet** (open question), so margins can't be calculated.

| Scenario | Uzbekistan (1,500 boxes) | Korea (1,500 boxes) |
|---|---|---|
| All sold B2B | 180,000,000 sum | 15,750,000 won + VAT |
| All sold at retail list price | 375,000,000 sum | 52,350,000 won |
| All sold at lowest promo | — | 29,850,000 won |

In practice the mix will be partly B2B and partly retail. Each sample given away to bloggers lowers these totals; the plan is 100–150 units, 7–10% of the Uzbekistan stock.

### The real goal of this first batch

With 1,500 units per country, this is a **test batch, not a full launch**. Its job is to answer one question cheaply: **do people buy a second box?**

Collagen is taken every day and one box lasts exactly 30 days, so **repeat purchase** decides whether the brand works. Track these:
- Which channel sells (marketplace, Instagram/Telegram direct orders, B2B partners).
- Who reorders, and after how many days.
- Which content and bloggers bring buyers.

### Markets in priority order

1. **Uzbekistan**: main focus. Russian-speaking, and the stock is already there.
2. **South Korea**: low-effort channels only. The collagen market there is crowded.
3. **Russia and Kazakhstan**: later. Supplements in Russia and the EAEU need separate state registration (СГР), and Uzbekistan is not an EAEU member, so stock cannot simply be shipped across.

Full channel plan: `03-sales-strategy-and-channels.md`.

---

<!-- source: docs/handoff/02-product-facts.md -->

## 02: Product facts (from the printed carton and stick)

Everything here was read from the founder's carton artwork file (`Glow_Peptide_Carton.html`, a print-proof viewer with every panel translated) and from photos of the real sticks. **Treat these as exact.** If the label changes, update this file and the website.

---

### Identity

| Field | Value |
|---|---|
| Brand | **YOROSUM** (Korean: **여러숨**, pronounced "yeo-reo-sum") |
| Product name (KR) | 여러숨 글로우 펩타이드 |
| Product name (EN) | **YOROSUM Glow Peptide** |
| Subtitle (KR) | 저분자 생선콜라겐 데일리 스틱 |
| Subtitle (EN, printed on box) | LOW MOLECULAR FISH COLLAGEN DAILY STICK |
| Brand line on the side panel | 하루 한 포로 채우는 이너뷰티 루틴: "An inner-beauty routine you fill with one stick a day" |
| Logo | A small filled dot followed by two curved "sound wave" arcs, then **YOROSUM** in wide-spaced capitals, often followed by 여러숨. The dot is berry, the arcs are gold. |

### Format

| Field | Value |
|---|---|
| Format | Powder in single-dose sticks |
| Sticks per box | **30** |
| Weight per stick | **3 g** |
| Net weight per box | **90 g** |
| Energy | **10 kcal per stick**, **335 kcal per box** |
| Daily dose | One stick, once a day, **with water** |
| Flavour | **Peach** (peach-flavour powder is 10% of the formula) |
| Days per box | 30 |

### Headline figures (per stick)

| Figure | Meaning |
|---|---|
| **2,000 mg** | fish collagen (생선콜라겐) |
| **100 mg** | vitamin C (비타민 C) = 100% of the Korean daily reference value |
| **300 Da** | average molecular weight of the low-molecular fish collagen (저분자 생선콜라겐의 평균분자량) |

Also on the front panel: elastin hydrolysate **0.1%** · bamboo sap extract powder **1%** · peach-flavour powder **10%**.

**What "300 Da" means (approved explanation used on the website):** a dalton (Da) is a unit of molecular mass. The smaller the number, the shorter the peptide chains. The collagen's average molecular weight is 300 Da, which is why the box calls it low-molecular. Do **not** turn this into an absorption or effect claim.

---

### Nutrition facts (영양정보)

Total 90 g (3 g × 30 sticks). % Daily Value is based on 2,000 kcal (Korean reference values); individual needs vary.

| Nutrient | Per stick (3 g) | % DV | Whole box (90 g) | % DV |
|---|---|---|---|---|
| Energy | 10 kcal | | 335 kcal | |
| Sodium (나트륨) | 10 mg | 1% | 250 mg | 13% |
| Carbohydrate (탄수화물) | < 1 g | 0% | 24 g | 7% |
| — Sugars (당류) | < 0.5 g | 0% | 13 g | 13% |
| Fat (지방) | 0 g | 0% | 0 g | 0% |
| — Trans fat | 0 g | | 0 g | |
| — Saturated fat | 0 g | 0% | 0 g | 0% |
| Cholesterol | – | – | – | – |
| Protein (단백질) | 2 g | 4% | 60 g | 109% |
| Vitamin C (비타민C) | 100 mg | 100% | 3,000 mg | 3,000% |

Check: (24 g carbohydrate + 60 g protein) × 4 kcal = 336 kcal, which rounds to 335. Matches the front panel.

---

### Full ingredient list

#### Korean label (원재료명), translated to English
Fish collagen (India), peach-flavour powder [crystalline fructose, anhydrous glucose, peach concentrate powder {dextrin, peach concentrate (peach: USA)}, flavouring (peach), dextrin, citric acid, silicon dioxide, enzyme-treated stevia (sweetener), refined salt (Korea)], anhydrous glucose, mixed preparation (dextrin, propylene glycol, synthetic flavouring, ethanol, gum arabic, ethyl acetate), vitamin C, xylitol (sweetener), anhydrous citric acid, DL-malic acid, bamboo sap extract powder (India), enzyme-treated stevia (sweetener), elastin hydrolysate, milk protein concentrate powder, sucralose (sweetener).

#### Russian translation (used on the website)
Рыбный коллаген (Индия), персиковый порошок [кристаллическая фруктоза, безводная глюкоза, порошок персикового концентрата {декстрин, персиковый концентрат (персик: США)}, ароматизатор (персик), декстрин, лимонная кислота, диоксид кремния, ферментированная стевия (подсластитель), поваренная соль (Корея)], безводная глюкоза, смесь (декстрин, пропиленгликоль, синтетический ароматизатор, этанол, гуммиарабик, этилацетат), витамин C, ксилит (подсластитель), безводная лимонная кислота, DL-яблочная кислота, порошок экстракта сока бамбука (Индия), ферментированная стевия (подсластитель), гидролизат эластина, концентрат молочного белка, сукралоза (подсластитель).

Sweeteners present: crystalline fructose, glucose, xylitol, stevia, sucralose.

### Allergens

- **Korean label says:** contains **milk, peach** (우유, 복숭아 함유).
- **Also contains fish** (the collagen is fish collagen). Korea's mandatory allergen list doesn't cover fish in general, but **EAEU / Russian-speaking market rules do**. The website says: «Содержит рыбу (рыбный коллаген), молоко и персик.» Keep that on any Russian label or listing.
- **Shared facility (cross-contact) statement:** made in a facility that also handles eggs (poultry), buckwheat, peanuts, soybeans, wheat, mackerel, crab, shrimp, pork, tomato, sulphites, walnuts, chicken, beef, squid, shellfish (incl. oyster, abalone, mussel) and pine nuts.

### Directions, storage, cautions

- **How to take (섭취방법):** once a day, one stick, with water.
- **Storage:** keep in a cool place out of direct sunlight, out of reach of children.
- **Cautions:**
  - Check the use-by date and follow the directions.
  - If you have allergies or a sensitive constitution, check the ingredients first.
  - Take care not to cut yourself on the packaging.
  - Children may choke, so supervise them.
  - The powder absorbs moisture, so take it right after opening.

---

### Legal and company data on the box

| Field | Value |
|---|---|
| Food type | **기타가공품** ("other processed food"), a **general food in Korea, not a health functional food (건강기능식품)**. This limits advertising; see `03` and `04`. |
| Korean product report no. (품목보고번호) | **20030445025-912** |
| Manufacturer (제조원) | **(주)한국씨엔에스팜 / Hankook CNS Pharm Co., Ltd.**, 충청북도 음성군 원남면 상경로 16 (Eumseong-gun, Chungcheongbuk-do) |
| Distributor / sales agent (유통전문판매원) | **신라글로벌트레이딩 / Shilla Global Trading**, 대전광역시 유성구 은구비서로 24번길 46, 1층 103호 (Yuseong-gu, Daejeon). *Open question: is this the founder's own company?* |
| Customer service on box | 070-8080-5163; returns and exchanges at the place of purchase |
| Consumer-protection lines | Report unsafe food: 1399. Exchange/compensation under the Fair Trade Commission's consumer dispute standards. |
| Inner packaging (stick film) | Polyethylene (PE) |
| Lot no. (제조번호) | **RA88201** |
| Use by (소비기한) | **15 Sep 2028** (2028.09.15) |
| Barcode | **8800342991316** (EAN-13, Korea prefix 880; check digit verified correct) |
| Label language | **Korean only.** Retail in Uzbekistan needs a Russian/Uzbek sticker label. |

---

### Carton (single-unit box, 단상자) print spec

| Item | Value |
|---|---|
| Size (W × D × H, closed) | **95 × 60 × 143 mm** |
| Colours | CMYK + 1 spot colour **Pantone 517 C** (the pale pink on front, back and lid) |
| Board | 350 g/m² CCP coated paperboard |
| Finish | Matte lamination over everything; **spot epoxy** (raised clear gloss) and **embossing** on the logo/name elements |
| Construction | Glue flap 15 mm; crash-lock (auto) bottom with 45 mm flaps (plain cream, no print); 30 mm dust flaps; pink 60 × 95 mm tuck lid hinged on the front, logo only, raised gloss |
| Panels | Front: name, figures, peach image. Right side: brand line, legal notices. Back: nutrition table, company info, lot/use-by, barcode. Left side: report no., ingredients, allergens, directions, storage, cautions. |
| Type sizes | Product name 29 pt, English name 19 pt, figures 16 pt, labels 12 pt, net-content line 10 pt; info panels at the 10 pt Korean legal minimum |
| Print contact on spec sheet | Manager Yoo Su-young (유수영 부장), 031-932-6994 |

**Pre-press notes from the artwork review.** The boxes are already printed, so these are only for the next print run:
1. Gloss plate said 피쉬콜라겐 while the print says 생선콜라겐 (both mean "fish collagen"), so the gloss wouldn't line up. Fix the plate to 생선콜라겐 or drop that line from it.
2. The spec note said 90 g/340 kcal; the box and nutrition maths say **335 kcal**.
3. One plate was marked for both spot epoxy and embossing; these need separate plates/dies.

### The stick (from photos)

- About 3 g stick pouch, mostly **pink** (matching Pantone 517 C) with a **cream band at the bottom** showing "3 g".
- Printed (Korean/English, running vertically):
  - **EASY CUT** dashed tear line at the top
  - the YOROSUM logo
  - 여러숨 글로우 펩타이드 / YOROSUM GLOW PEPTIDE
  - 1포당 (per stick) **2,000mg 생선콜라겐**, **100mg 비타민 C**
  - **3 g**
- It **tears open by hand** at the Easy Cut line; no scissors needed, as shown in the founder's photos and video.
- Powder: fine, off-white, with **small pink specks**, presumably the peach powder. Don't state that as fact without checking with the OEM.
- In daylight the stick reads **pink**. Under evening indoor light it photographs **lilac/purple**. See `06`.

---

<!-- source: docs/handoff/03-sales-strategy-and-channels.md -->

## 03: Sales strategy, channels, regulation, 30-day plan

Recommended in the first session. These are recommendations; the founder hasn't confirmed or started any channel yet.

### Core principle

Treat the 3,000 units as a **test of repeat purchase**, not a full launch. With one person and a small budget, focus on a few channels, get real reviews, and find people who buy a second box. Put more into what works by week 4.

---

### Uzbekistan (main market)

| Channel | Why | When |
|---|---|---|
| **Uzum Market** | The biggest marketplace in Uzbekistan. Its fulfillment service can store and deliver orders, which saves a solo founder time. Listings need Russian and Uzbek descriptions and product documents. | Apply in week 1, listing live in week 2 |
| **Instagram + Telegram** | Instagram is where people in Uzbekistan discover products; Telegram is where they talk and order. Take orders by DM and deliver with a local courier. | Week 1 |
| **Micro-blogger seeding (5k–50k followers)** | Bloggers sell more than paid ads in Uzbekistan. Give **100–150 units** to 20–30 micro-bloggers in exchange for **honest** reviews. It costs stock, not cash. | Weeks 2–4, only after the Instagram profile has its first posts |
| **B2B at 120,000 sum** | **Cosmetologists**, beauty salons, fitness clubs, pharmacies, health-food stores. A salon that reorders every month is worth a lot. Cosmetologists are the most natural fit for collagen. | Week 3 onward |
| Wildberries (Uzbekistan) | A second marketplace once Uzum works | Later |

Telegram plan: a channel with the same content as Instagram, plus direct ordering. A simple Telegram order/FAQ bot can be built later.

### South Korea (secondary, low effort)

The collagen category in Korea is crowded. **Don't fight Coupang ad wars.**

| Channel | Why |
|---|---|
| **Naver Smart Store** | Cheap to open. Run the 19,900 won promo price there. |
| **B2B to K-product resellers (байеры)** | Many Korea-based "buyers" resell Korean products to CIS customers through Instagram/Telegram. "Made in Korea" sells well in Russian-speaking markets, and 10,500 won + VAT gives them margin. |
| **The Russian-speaking community living in Korea** | Workers and residents from Central Asia and Russia (e.g. around Ansan). Small, but already reads Russian content. |
| KakaoTalk channel | Customer contact in Korea (the website has a slot for it) |

### Russia and Kazakhstan: later

Supplements in Russia/EAEU need **state registration (СГР, Rospotrebnadzor)**. Uzbekistan is not an EAEU member, so stock can't simply be shipped across. Revisit after the first stock sells. In Kazakhstan the main marketplace is Kaspi.kz.

---

### Regulatory checklist (check before selling)

> These are flags to verify with local authorities or advisers, not legal advice.

#### Uzbekistan
- [ ] Confirm the product's import/registration documents and the certificate needed for retail and Uzum.
- [ ] **Labeling:** the box is in Korean only. Add a **Russian/Uzbek sticker label** (name, ingredients, allergens including **fish**, directions, storage, use-by, manufacturer, importer).
- [ ] Uzum will ask for documents during seller onboarding.

#### South Korea
- [ ] The product is registered as **기타가공품 (general food)**, not 건강기능식품 (health functional food). So **no functional, health or beauty-effect claims at all** in ads, listings or posts. Making such claims for a general food counts as misleading health-food advertising. Describe only ingredients, amounts, taste and how to take it. (The functional-food pre-review, 자율심의, applies only to registered functional foods, so it doesn't apply here, but neither do functional claims.)
- [ ] Business registration (사업자등록) and online-sales registration (**통신판매업 신고**) before selling on Naver or your own site.

#### Everywhere
- Never write that it treats, cures, prevents, fixes, rejuvenates or removes anything. Full do/don't list in `04-brand-and-content-rules.md`.
- **No fake reviews and no AI-generated "customers."** Marketplaces ban for it and it can be illegal.

---

### 30-day plan

| Week | Actions |
|---|---|
| **1** | Create the Instagram account and Telegram channel. Post the first launch posts at a normal pace. Start the Uzum seller application. Put the website online (GitHub Pages). Reshoot photos in daylight. |
| **2** | Uzum listing goes live. Send samples to the first 10 micro-bloggers. Open Naver Smart Store. |
| **3** | Samples to 10–20 more bloggers. Contact **30 salons/cosmetologists in Tashkent** and **10 K-product resellers in Korea**. |
| **4** | Review what sold, which channel, which blogger, who reordered. Put more into the winners. |

### What to measure (simple spreadsheet)
- Orders by channel (Uzum / Instagram DM / Telegram / B2B / Naver).
- Units given as samples, and to whom.
- Blogger → orders attributed (use a unique promo word per blogger).
- Repeat buyers and days between orders (the key metric).
- B2B partners and reorder dates.

---

### Using AI to cover the digital work

| Task | Tool |
|---|---|
| Sales plan, pricing maths, B2B price list, pitch deck | Claude |
| Marketplace product descriptions (Russian + Uzbek for Uzum, Korean for Naver) | Claude, then a **native speaker checks the Uzbek** |
| 30-day content calendar, Russian captions | Claude |
| Messages to bloggers, salons, resellers | Claude (in the first session, Gmail was connected so drafts could go straight to the founder's Gmail) |
| Post templates and product visuals | Canva (connected in the first session) |
| Reels with captions | CapCut (free), or ffmpeg as in `06` |
| Post scheduling | Meta Business Suite (free) |
| Customer FAQ and order bot | A simple Telegram bot, to be built later |

The founder's own time should go to filming real content, talking to B2B buyers, and shipping orders.

---

<!-- source: docs/handoff/04-brand-and-content-rules.md -->

## 04: Brand identity, voice and content rules

### Positioning

- **What it is:** a Korean-made, low-molecular fish collagen stick: 2,000 mg collagen + 100 mg vitamin C, peach flavour, one stick a day.
- **How it should feel:** an international brand with Korean origin. The brand name and product name stay in **English (Latin letters)** everywhere, including in Russian content. Korean (여러숨) appears small, as a sign of origin.
- **Who it's for:** Russian-speaking women and men who already care about daily self-care routines, first in Uzbekistan. B2B: cosmetologists, salons, fitness clubs, pharmacies, K-product resellers.
- **Proof points to use (all factual, from the label):**
  - Made in Korea, by Hankook CNS Pharm
  - 2,000 mg fish collagen and 100 mg vitamin C per stick
  - 300 Da average molecular weight
  - 30 sticks = 30 days
  - Peach flavour, 10 kcal per stick
  - Easy Cut: the stick tears open by hand

### Languages

| Use | Language |
|---|---|
| Main customer content (Instagram, Telegram, Uzum, website default) | **Russian** |
| Brand name, product name, the "official" international face | **English** |
| Uzum listing, Uzbekistan sticker label | Russian + **Uzbek** (have a native speaker check the Uzbek) |
| Naver / Korean customers | Korean |

### Visual identity (taken from the carton)

| Token | Hex | Where it comes from / use |
|---|---|---|
| Pink | `#F2C7D0` | Pantone 517 C, the carton's solid pink. Backgrounds, hero band. |
| Berry | `#8F2148` | Product-name ink. Headings, buttons, caption text. |
| Cream | `#F8F1EA` | The carton's lower cream band. Page background. |
| Paper | `#FFFBF8` | Light surfaces |
| Ink | `#3A1E28` | Body text |
| Mute | `#7A5A65` | Secondary text |
| Gold | `#B9834B` | The logo's two sound-wave arcs |

Dark-mode versions exist in the website CSS (`05-website.md`).

**Fonts (website; all from Google Fonts, all support Cyrillic):**
- **Unbounded**: display/headings. It's wide and geometric, echoing the spaced YOROSUM capitals.
- **Golos Text**: body text; designed for Russian.
- **IBM Plex Mono**: small labels and units.
- **Noto Sans KR**: the Korean 여러숨.

The Reel captions use **Inter SemiBold**, which was the Cyrillic font available offline.

**Logo:** a filled dot followed by two curved arcs (like a sound wave or breath, "숨" means breath), then **YOROSUM** in wide-spaced capitals.

**Photo style:** daylight, white or warm-plain background, nothing else in the frame, the true **pink** colour of the pack. See `06`.

### Voice

- Plain, warm, direct. Short sentences. Facts over hype.
- Talk about the **routine** (one stick a day, with water, peach taste) and **what's inside**, not about results.
- Use "мы" for the brand. The founder's own story is told in first person ("я") in the founder post.
- Emoji are fine on Instagram in moderation (🍑 🇰🇷 📦). Don't use them on the website.

---

### Claims rules (most important)

The product is a **general food** in Korea (기타가공품), and supplement advertising is regulated in every target market. Breaking these rules gets posts removed, accounts restricted, marketplace listings blocked, or worse.

#### ✅ Allowed: describe what it is and how to use it
- «2 000 мг рыбного коллагена и 100 мг витамина C в одном стике»
- «Низкомолекулярный рыбный коллаген, 300 Да» (with the dalton explanation, as a fact)
- «Один стик в день, запивая водой» · «30 стиков — на 30 дней»
- «Вкус персика» · «10 ккал» · «Сделано в Корее»
- «Открывается без ножниц (Easy Cut)»
- «Бьюти-ритуал / ежедневный ритуал»: lifestyle wording, based on the box's own "inner-beauty routine" line. Keep it about the routine, not an effect.
- Footer on the site: «Пищевой продукт. Не является лекарственным средством.»

#### ❌ Not allowed: any effect, health or medical claim
Don't write that it:
- treats, cures or prevents (лечит, вылечивает, предотвращает)
- **rejuvenates** or is anti-aging (омолаживает, антиэйдж-эффект)
- removes wrinkles, tightens or lifts skin (убирает/разглаживает морщины, подтягивает кожу)
- makes skin glow or more elastic or moisturised as a result (кожа сияет, упругость, увлажнение кожи изнутри как результат)
- strengthens hair, nails or joints, or helps bones (укрепляет волосы, ногти, суставы)
- is absorbed better or faster because it's low-molecular (лучше/быстрее усваивается). State 300 Da as a fact only.

Also not allowed:
- Before/after photos, doctor or white-coat imagery, "clinically proven," percentages of improvement.
- **Fake reviews** or AI-generated customers. Only repost real customer stories, with their permission.

Note: the product's own name is "Glow Peptide." Using the name is fine. Don't build claims on top of it ("для сияния кожи").

---

### Instagram launch kit (summary)

The full ready-to-post text is in the repo at `marketing/instagram-launch-ru.md` and is reproduced in the appendix of `YOROSUM-FULL-HANDOFF.md`.

- **Handle:** `@yorosum.official` (or `@yorosum` if free). **Name field:** `YOROSUM · Glow Peptide коллаген`, because Instagram search reads this field.
- **Bio:** Glow Peptide 🍑 рыбный коллаген в стиках / 2 000 мг коллагена + 100 мг витамина C / 1 стик в день · Сделано в Корее 🇰🇷 / Доставка по Узбекистану ⬇️
- **Highlights:** Состав · Как принимать · Отзывы · Доставка · Где купить · Опт
- **First six posts. None of them is a sales post.** Spread them over about a week.
  1. The product alone on a plain background
  2. Box close-up explaining 300 Da
  3. "Why I made YOROSUM," in the founder's own words. The template has placeholders; the founder must fill in the real story.
  4. The product in a real routine (morning, a glass of water)
  5. Behind the scenes: the first shipment, made in Korea
  6. Carousel: what's inside, with the full ingredients and allergens
- **Post 7** can be the first sales post.
- **Reel draft:** about the 4th–5th post (`06`).

General Instagram guidance the founder supplied, and which the plan follows:
- Don't open with an ad.
- Have a clear profile.
- Put up 5–6 real posts before anything else, at a human pace.
- Use candid, well-lit photos.
- No medical claims.

---

<!-- source: docs/handoff/05-website.md -->

## 05: The official website

### Where it is

| Item | Value |
|---|---|
| GitHub repository | `btginredginseng-design/btgin` |
| Working branch | **`claude/charming-turing-l5793z`**. All work is pushed here. Not merged into the default branch; no pull request opened. |
| Commits so far | `84f27ae` site + Instagram kit · `6c7b3dd` real photos · `b9d1208` Reel draft · plus this handoff folder |
| Private preview | https://claude.ai/artifact/XDRoPVXC7EMLKbTc9TcJ8H (Claude artifact; only the founder can open it unless they share it) |
| Public URL | **None yet.** GitHub Pages hasn't been switched on. |
| Domain | None yet. Suggested `yorosum.com` or similar, about $10–15/year. |

### Files

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

### Page structure (top to bottom)

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

### How the language works

- The Russian text is written directly in the HTML; the English text is in a JS dictionary `EN` inside `index.html`. Each translatable element has `data-i18n="key"`; image alt text uses `data-i18n-alt`.
- **First visit:** browsers set to ru, uz, kk, ky, tg, be, uk, az, hy, ka, tk or mn get **Russian**; everyone else gets **English**.
- The visitor's choice is remembered (localStorage). Direct links: `…/#ru` or `…/#en`.
- To add a language (e.g. Uzbek or Korean): add a dictionary like `EN`, a button in `.lang`, and handle it in `setLang()`.

### How to add contact and store links

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

### How to publish (free, GitHub Pages)

1. GitHub → repository → **Settings → Pages**.
2. **Deploy from a branch** → pick the branch (merge `claude/charming-turing-l5793z` into the default branch first, or select it directly) → folder `/ (root)` → Save.
3. The site goes live at `https://btginredginseng-design.github.io/btgin/` after about a minute.
4. Optional: add a custom domain on the same page and point the domain's DNS to GitHub.

After a domain exists, add an `og:image` meta tag with an absolute URL, so links shared in Telegram/Instagram show a preview picture.

### Design notes

- Layout idea: the page is the **carton opened up**. The pink top band is the box front; the cream panels below read like the side and back panels.
- Colours and fonts: see `04-brand-and-content-rules.md`. All colours are CSS variables at the top of the `<style>` block, with a full **dark mode**.
- Works at phone width (tested down to 400 px), with safe-area padding for phones with notches.

### Known gaps on the site

- No contact links yet (all «скоро»).
- No Uzbek or Korean version.
- Photos are from an evening shoot and were colour-corrected. Swap them for daylight reshoots when available (`06`).
- No `og:image` (needs a public URL first).
- No analytics. Options: GA4 or Yandex Metrica, which is common in CIS, once the site is public.
- No real order form: a static site can't receive form submissions. Orders go through Telegram/Instagram/marketplaces.

---

<!-- source: docs/handoff/06-media-assets-and-reel.md -->

## 06: Photos, videos and the Reel draft

### Main lesson from the first shoot

**Shoot in daylight.** Every shot taken in the evening under room light makes the pink pack look **lilac/purple** and the white table look grey-green. The one photo taken around noon shows the true **pink**. Inconsistent colour across posts makes a brand look unprofessional.

---

### Photos received (8)

| # | What it shows | Camera / time | Verdict |
|---|---|---|---|
| 1 | Stick held in hand over a white round table; open box and loose sticks behind | iPhone 16 Pro Max, 15 Oct 2026 22:35 | Usable for Stories. Cluttered background, evening colour. |
| 2 | Close-up of the stick top with the "EASY CUT" line | iPhone, 22:36 | Detail shot. Lilac cast. |
| 3 | Stick torn open at Easy Cut, torn piece above it | iPhone, 22:37 | Good Easy Cut proof, **but scissors visible** in the background (contradicts "no scissors"). Cropped out for the site. |
| 4 | Powder poured from stick, close | iPhone, 22:39 | Duplicate of #7. Green-grey cast. |
| 5 | Top-down: stick + powder pile on white, sticks in a corner | iPhone, 22:38 | Best flat-lay layout, but scissors, a plate and loose sticks in frame. |
| 6 | Powder close-up | iPhone, 22:39 | Duplicate of #7. |
| 7 | Powder very close, pink specks visible | iPhone, 22:39 | Good texture shot. **Used on the site** after colour correction. |
| 8 | Stick lying on an open palm, wooden floor | Galaxy S25 Ultra, 18 Oct 2026 12:22 (daylight) | **Best photo.** Sharp, true pink. **Used on the site** with no colour correction. |

#### Processing done for the website
- Rotated per EXIF, cropped, resized to 900 px wide, JPEG quality 82.
- **Colour correction:** white balance from the bright, low-saturation pixels (the white table), then whites lifted. Applied at 90% strength to photos #3 and #7. Photo #8 was left untouched.
- Results: `assets/stick-in-hand.jpg` (from #8, 900×1200), `assets/easy-cut.jpg` (from #3, 900×900, scissors cropped out), `assets/powder.jpg` (from #7, 900×1200).

---

### Video 1: unboxing (`20261023_213918.mp4`)

- 19.9 s, vertical **1080×1920**, HEVC, 30 fps. Audio almost silent (mean −44.7 dB, just handling noise). Recorded in the evening.
- Shot top-down on a **beige patterned rug with dark squares**, and a black object visible at the bottom of the frame.

| Time | Action |
|---|---|
| 0.0–1.4 s | Box front shown, then turned |
| 1.5–4.5 s | Lid opened; back panel / nutrition visible; sticks inside |
| 5.0–7.5 s | Box tipped, sticks spill out, one stick picked up |
| 8.0–13.8 s | Stick held, then **torn open by hand** at Easy Cut |
| 14–16 s | Torn stick shown |
| 16.5–19.9 s | Powder poured into an open palm |

Problems: busy rug, flat evening light, ends with powder in a bare palm (the product is taken with water), no sound, HEVC (some browsers can't play it on a website).

### Video 2: pour into water (`IMG_6301.mov`)

- 4.85 s, vertical (stored 1920×1080, rotated −90°), HEVC, **60 fps**. Silent (−60 dB). iPhone 16 Pro Max, recorded 15 Oct 2026 ~22:41 KST (same evening session).
- Table-height camera. A stick pours powder into a **clear glass mug of water** on a white table; the box is softly blurred behind on the left; no hands in shot.
- Strengths: clean, natural angle, nice powder stream; 60 fps allows smooth slow motion.
- Problems:
  - Lilac colour (evening light) and a cold grey-blue wall.
  - Box cut off at the left edge; mug handle cut off on the right; a white object in the top-right corner.
  - **No stirring:** a clump of powder floats and the water ends cloudy. Add 2–3 s of stirring next time.

---

### Reel draft (done)

File: **`marketing/yorosum-reel-draft.mp4`**, 15.6 s, 1080×1920, H.264 High, 30 fps, 10.8 MB, silent AAC track. Add music inside Instagram; library tracks there don't get muted.

| Time | Source | Caption (Russian) |
|---|---|---|
| 0.0–1.5 s | Video 1, 0.0–1.5 s (box front) | «Мой коллаген из Кореи». Placed low, under the box, so it doesn't cover the title. |
| 1.5–3.5 s | Video 1, 2.0–4.0 s (opening) | «30 стиков — на 30 дней» |
| 3.5–6.0 s | Video 1, 5.5–8.0 s (sticks spill, stick in hand) | «2 000 мг коллагена / + 100 мг витамина C» |
| 6.0–9.3 s | Video 1, 10.5–13.8 s (tearing) | «Открывается без ножниц» |
| 9.3–14.15 s | Video 2, full (pour) | «1 стик в день / вкус персика» |
| 14.15–15.65 s | Last frame of video 2, frozen | End card: **«YOROSUM / Glow Peptide»** + «Где купить — ссылка в профиле» |

**Caption style:** ASS subtitles, font **Inter SemiBold**:
- Sizes: 72 px for captions, 100 px for the end title, 56 px for the end subtitle.
- Colour: berry `#8F2148` text on near-opaque white boxes (BorderStyle 3).
- Position: kept in the upper-middle of the frame, away from Instagram's bottom UI.
- Caption file: **`marketing/reel-draft-captions.ass`**. Edit the text or timing there and re-render.

**Render command used** (inputs: V1 = video 1, V2 = video 2):

```bash
N="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,format=yuv420p"
ffmpeg -i "$V1" -i "$V2" -f lavfi -t 15.65 -i anullsrc=r=48000:cl=stereo -filter_complex "\
[0:v]trim=0:1.5,setpts=PTS-STARTPTS,$N[a];\
[0:v]trim=2.0:4.0,setpts=PTS-STARTPTS,$N[b];\
[0:v]trim=5.5:8.0,setpts=PTS-STARTPTS,$N[c];\
[0:v]trim=10.5:13.8,setpts=PTS-STARTPTS,$N[d];\
[1:v]trim=0:4.85,setpts=PTS-STARTPTS,$N,tpad=stop_mode=clone:stop_duration=1.5[e];\
[a][b][c][d][e]concat=n=5:v=1:a=0,subtitles=reel-draft-captions.ass[v]" \
-map "[v]" -map 2:a -c:v libx264 -preset medium -crf 21 -profile:v high -pix_fmt yuv420p \
-c:a aac -b:a 96k -shortest -movflags +faststart yorosum-reel-draft.mp4
```

The original video files are **not** in the repo; they're only in the first chat's uploads. Keep the originals on your phone or in cloud storage.

**When to post:** as the 4th or 5th Instagram post, after the photo posts.

---

### Reshoot list (one daytime session, about 30 minutes)

Set-up: next to a window in daylight; a white table or white paper sheet; **nothing else in frame** (no scissors, plates, cables, rugs). Phone at table height or straight top-down.

**Photos**
1. **The box alone**, upright, slightly turned so the front and side both show. Needed for Instagram post 1; this shot doesn't exist yet.
2. Close-up of the box front showing **2,000 mg · 100 mg · 300 Da** (post 2).
3. A hand tearing a stick at the Easy Cut line, no scissors anywhere.
4. The box with 4–5 sticks fanned out in front.
5. A real routine: a glass of water and a stick on a kitchen table in the morning (post 4).
6. Founder holding the box (post 3); a real face builds trust.

**Video clips** (vertical, 4K or 1080p, 60 fps if possible)
1. Box front, slow turn (2–3 s)
2. Opening the lid, sticks inside (3 s)
3. Pulling out a stick (2 s)
4. Tearing at Easy Cut, close (3 s)
5. **Pouring into a glass of water and stirring** with a spoon until even (5–6 s)
6. Optional: drinking it (2 s)

With these, the Reel can be re-cut in daylight colour, and the website photos replaced.

---

<!-- source: docs/handoff/07-status-open-questions-next-steps.md -->

## 07: Status, open questions, next steps, decision log

### Done

- [x] Market and channel strategy for Uzbekistan, Korea, and Russia/Kazakhstan later (`03`)
- [x] Regulatory flags: Korean general-food status → no effect claims; Uzbekistan needs RU/UZ labels; fish allergen added (`03`, `04`)
- [x] Product facts extracted from the carton artwork (`02`)
- [x] Bilingual website: Russian default, English switch, 3D carton, real photos (`05`)
- [x] Instagram launch kit in Russian: bio, highlights, 6 posts (`marketing/instagram-launch-ru.md`)
- [x] Photo and video analysis, colour correction of 3 photos (`06`)
- [x] 15.6 s Reel draft with Russian captions (`marketing/yorosum-reel-draft.mp4`)
- [x] This handoff folder

### Waiting on the founder

- [ ] **Contact details** for the site and Instagram: Telegram username, Instagram handle, business email, WhatsApp number
- [ ] **Create accounts:** Instagram, Telegram channel; later a KakaoTalk channel
- [ ] **Switch on GitHub Pages** (Settings → Pages); optionally buy a domain
- [ ] **Daylight reshoot**: photos and clips listed in `06`
- [ ] **Founder story**: 3–5 honest sentences for Instagram post 3 (where they're from, what bothered them about other collagen, why Korea)
- [ ] **Uzum Market** seller application; **Naver Smart Store** account
- [ ] Check **Uzbekistan documents and labeling** (RU/UZ sticker labels)
- [ ] Korea: business registration and **통신판매업 신고** before selling online

### Open questions (answers change the plan)

1. **OEM cost per unit** in each country, landed with shipping and duties. Needed for margins, blogger budgets and minimum B2B order sizes.
2. **Is Shilla Global Trading (신라글로벌트레이딩) the founder's company?** It's on the box as distributor and on the website.
3. Where exactly is the Uzbekistan stock (city), and who ships orders there? The founder alone, a 3PL, or Uzum fulfillment?
4. Where is the founder based day-to-day: Korea or Uzbekistan? The photos suggest Korea.
5. Does the Uzbekistan stock already have import clearance and the documents Uzum and pharmacies will ask for?
6. Minimum order quantity and payment terms for B2B partners?
7. Is there a budget for samples and shipping to bloggers, and for small paid boosts?
8. Should the website add an **Uzbek** version, and a **Korean** one for Naver traffic?
9. Are the pink specks in the powder the peach powder? Confirm with the OEM before saying so.

### Next steps, in priority order

1. **Create Instagram + Telegram**, fill in the bio, then send the handles. Claude adds them to the website `LINKS`.
2. **Daylight reshoot** (30 min) → Claude swaps the site photos, re-cuts the Reel, and makes Canva templates for the six launch posts.
3. **Publish the website** on GitHub Pages so the Instagram bio has a link.
4. **Post the six launch posts** over about a week, then the Reel.
5. **Uzum listing**: Claude writes the Russian and Uzbek listing text from `02` (native check for the Uzbek), plus a document checklist.
6. **Blogger seeding**: Claude makes a shortlist template and a Russian outreach message; set aside 100–150 units.
7. **B2B outreach**:
   - A one-page Russian B2B price sheet/deck (120,000 sum, minimum order, margin for the partner).
   - Messages to 30 Tashkent salons/cosmetologists and 10 K-product resellers in Korea.
8. **Naver Smart Store**: Korean listing text with the 19,900 won promo. No effect claims (general food).
9. **Simple sales tracker** (Google Sheet): orders by channel, samples, repeat buyers, days between orders.
10. Week 4: review numbers and focus on the channels that work.

### Decision log

| Date | Decision |
|---|---|
| 20 Oct 2026 | Uzbekistan is the lead market; Korea is low-effort only (Naver + B2B resellers); Russia/Kazakhstan wait for EAEU registration. |
| 20 Oct 2026 | Website is a single static page on GitHub Pages: Russian default, English switch; brand and product names stay in English. |
| 20 Oct 2026 | No public B2B prices on the site; retail prices shown (250,000 sum / 34,900 won). |
| 20 Oct 2026 | Fish listed as an allergen in Russian content even though the Korean label lists only milk and peach. |
| 20 Oct 2026 | Instagram starts with 5–6 non-sales posts; no medical or effect claims anywhere. |
| 20 Oct 2026 | Founder's email is **not** published on the site unless they choose to add it to `LINKS`. |
| 23 Oct 2026 | Real photos added to the site after colour correction; the daylight photo (#8) is the reference for true pack colour. |
| 23 Oct 2026 | Reel draft cut at 15.6 s with Russian captions and a silent track, so music is added in Instagram. |

### Tools and access used in the first chat

- GitHub repository access (read/write on `btginredginseng-design/btgin`).
- Claude artifact for the private website preview.
- Connected in that session (may differ in a new chat): **Canva** (post templates), **Gmail** (drafting outreach emails as drafts), **Google Drive**.
- Local tools: ffmpeg (video), Python/PIL (photo processing), headless Chromium (screenshots).

---

## Appendix A: Instagram launch kit (full text from `marketing/instagram-launch-ru.md`)

### Instagram launch kit: YOROSUM Glow Peptide

Six posts that come before any sales post. Space them out over about a week, 1 post per day or every other day. Photos from a phone are fine: daylight, plain background.

Caption rule: say what is inside and how you take it. Do not write that it treats, cures, fixes, rejuvenates or "removes wrinkles". Words like «омолаживает», «лечит», «избавляет от морщин» get posts removed and break supplement advertising rules.

---

#### Profile

**Handle:** `@yorosum.official` (or `@yorosum` if it's free)

**Name field:** `YOROSUM · Glow Peptide коллаген`. Instagram search reads this field, so the word «коллаген» helps people find you.

**Bio:**

```
Glow Peptide 🍑 рыбный коллаген в стиках
2 000 мг коллагена + 100 мг витамина C
1 стик в день · Сделано в Корее 🇰🇷
Доставка по Узбекистану ⬇️
```

**Link:** your website, or Telegram until the site is online.

**Highlights (stories saved to the profile):** Состав · Как принимать · Отзывы · Доставка · Где купить · Опт

---

#### Post 1. The product, nothing else

*Photo:* the box standing upright on a plain light background, slightly turned so the pink front and the side are both visible.

```
Знакомьтесь: YOROSUM Glow Peptide.

Низкомолекулярный рыбный коллаген в ежедневных стиках.
В одном стике — 2 000 мг коллагена и 100 мг витамина C.
Вкус персика. 30 стиков в коробке, один стик в день.

Сделано в Корее 🇰🇷

#yorosum #glowpeptide #коллаген #рыбныйколлаген #корейскаякосметика #ташкент
```

#### Post 2. Close-up of the box (what 300 Da means)

*Photo:* close-up of the three figures on the front: 2,000 mg · 100 mg · 300 Da.

```
Что значит «300 Да» на коробке?

Дальтон (Да) — единица массы молекул. Чем меньше число, тем короче цепочки пептидов.
Средняя молекулярная масса нашего рыбного коллагена — 300 Да. Поэтому на упаковке он назван низкомолекулярным.

Сохраните, чтобы сравнивать с другими коллагенами 📌

#yorosum #коллаген #низкомолекулярныйколлаген #пептиды
```

#### Post 3. Why I made this (write it in your own words)

*Photo:* you holding the box, or your hands with the box. A real person's face builds the most trust.

Use this as a frame and fill in your own story. Readers can tell when a story is invented.

```
Почему я создал(а) YOROSUM.

[1–2 предложения: откуда вы и чем занимаетесь.]
[Что вас не устраивало в коллагенах, которые вы видели: вкус, формат, цена, непонятный состав?]
[Почему решили производить в Корее.]

Glow Peptide — это то, что я хотел(а) пить сам(а): один стик в день, понятный состав, вкус персика.

Расскажите в комментариях: вы уже пробовали коллаген? В каком формате? 👇

#yorosum #историябренда #коллаген
```

#### Post 4. In a real routine

*Photo or Reel (7–10 s):* morning at the kitchen table: open a stick, take it with a glass of water, coffee in the background. Or after training, with a gym bag.

```
Утро: стакан воды и один стик Glow Peptide 🍑

Порошок впитывает влагу, поэтому принимаем сразу после вскрытия.
30 стиков — ровно на месяц.

А когда удобнее вам: утром или вечером?

#yorosum #утреннийритуал #коллаген #glowpeptide
```

#### Post 5. Behind the scenes

*Photo:* the boxes in the warehouse, unpacking the shipment, or the cartons stacked up. If you have photos from the factory in Korea, use those.

```
Первая партия YOROSUM приехала 📦

Glow Peptide производится в Корее, на заводе Hankook CNS Pharm в провинции Чхунчхон-Пукто.
Сейчас товар уже на складе в Узбекистане.

Скоро расскажем, где купить. Включите уведомления 🔔

#yorosum #madeinkorea #новыйбренд #ташкент
```

#### Post 6. What's inside (carousel)

*Carousel of 4–5 images made in Canva:* 1) the box; 2) "2 000 мг коллагена"; 3) "100 мг витамина C"; 4) "Вкус персика · 10 ккал"; 5) the full ingredient list.

```
Что внутри одного стика Glow Peptide:

• 2 000 мг рыбного коллагена (300 Да)
• 100 мг витамина C
• гидролизат эластина и экстракт сока бамбука
• вкус персика, 10 ккал

Полный состав — в последней карточке. Аллергены: рыба, молоко, персик.

#yorosum #состав #коллаген #glowpeptide
```

---

#### After these six

- Post 7 can be the first sales post: price, where to buy, delivery.
- Start sending samples to micro-bloggers only after the six posts are up, so they land on a profile that looks alive.
- Repost every real customer story to the "Отзывы" highlight, with the customer's permission. Never write reviews yourself.
