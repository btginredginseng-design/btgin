# ACE NADI: handoff for the detail-page session

Start here in a new session. The user makes and sells **ACE NADI Tencel Essence Mask** (manufacturer BTGin). Sales are in **Korea only** for now.

## Next task: build the product detail page (상세페이지)

The page goes on **Naver Smart Store** and **cafe24**.

### Agreed requirements

| Item | Decision |
|---|---|
| Width | **860px**. Deliver JPG slices (keep each slice ≲ 1,500–2,000px tall) plus GIFs, upload-ready for both stores. |
| Look | Premium and professional, in ACE NADI's colors and fonts. Information and visuals must follow a logical order. |
| AI images (Gemini API) | Mood shots and lifestyle shots. **Realistic AI models are allowed, but the product must stay recognizable** (use the real pouch cutouts and photos as the reference or composite). |
| GIFs | Must look professional and deliver the message in a premium way. Sources: `assets/ace-nadi/footage/`. |
| Pricing section | **No price or bundle section.** Pricing stays in the store's own options. |
| PDRN | **Supporting role only.** It appears as one item in the ferment block, worded as "함유" with the footnote "*PDRN: 소듐디엔에이 함유, 원료 특성에 한함". Never a headline, never in the product name. |
| Fake efficacy visuals | **Never.** No AI before/after images, measurement images or invented % numbers. The product has no human-trial data yet. |
| Coming from the user | Marketing details and raw images (they will upload them). |

### Environment prerequisites (the user is configuring these)
- Network: the user set the allow list to **All domains**. Gemini and Google Fonts should be reachable.
- Gemini key: environment variable **`GEMINI_API_KEY`**. Never ask for it in chat.
- Check both first:
  ```
  curl -sS -o /dev/null -w "%{http_code}" https://generativelanguage.googleapis.com/v1beta/models
  echo ${GEMINI_API_KEY:+set}
  ```

## Source of truth documents

All in `docs/ace-nadi-tencel-essence-mask/`:

| File | What it holds |
|---|---|
| `product-details.md` | Final facts: 정보고시 table, verbatim 전성분 (59 ingredients), functional actives, usage text, cautions, COA results, open issues (§9) |
| `marketing-analysis.md` | Positioning, USP ranking, 10-section page storyboard, Korean copy bank, **ad-law do/don't table** |
| `competitor-medicube-pdrn-gel-mask.md` | Medicube page teardown and a revised section order for ACE NADI (§6). Use structure only; don't copy their images, wording or layout. |

### Open issues to keep honoring
1. ✅ Resolved: the user confirmed **홍삼**. Use "홍삼 발효" on the page.
2. ✅ Resolved: the user said to use **"텐셀 시트"**.
3. There are no human-trial numbers. Leave a placeholder section for future results; don't invent any.

## Brand system

| Token | Hex | Use |
|---|---|---|
| Deep purple | `#4A2470` | Headlines |
| Purple | `#7646A8` | Accents, labels |
| Lavender | `#C4B4E2` | Lines, tints |
| Ink | `#484258` | Body text |
| Background | `#FAF8FD` | Base |

- **Fonts:** Korean is Pretendard or Noto Sans KR (once fonts are reachable). English labels are Inter Medium, tracked caps. Big numbers are Inter Thin / InterDisplay ExtraLight. Inter is installed system-wide.
- **Style used in the film:** bright, clean white grade with a soft glow, lavender gradients, mask-rise text reveals, thin purple rule + tracked English label above each Korean headline.

## Assets in this repo (`assets/ace-nadi/`)

| Path | Contents |
|---|---|
| `brand/emblem_mask.png`, `wordmark_mask.png`, `kname_mask.png` | Logo alpha masks extracted from the pouch. Colorize with `#4A2470`. |
| `brand/pouch1.png`, `pouch2.png` | Front and back pouch cutouts (RGBA). The front looks grey in the photo; the film lifted it with `(rgb-20)*1.42`. |
| `photos/pouch_front.jpg`, `pouch_back.jpg` | Original pouch photos |
| `footage/c01–c15.mp4` | Production clips: 1080p, no audio, re-encoded from the user's 15 uploads |
| `video-pipeline/` | Scripts that rendered the 57.6s film (`build.py`), the score (`music.py`), SFX (`sfx.py`) and Canva text motions (`export_text.py`). Paths inside point at the old scratchpad, so adjust them before reuse. |
| `text-motions/ACE_NADI_text_motions.zip` | 13 transparent WebM text animations + PNG stills + README |

### Footage index

| Clip | Shows |
|---|---|
| c01 | Sealing line with gowned staff (wide) |
| c02 | Worker placing pouches at the batch-code printer (wide) |
| c03 | Batch-number printer head coding pouches (close) |
| c04 | Worker inserting mask into pouch at the filler |
| c05 | Pouches feeding into the sealer |
| c06 | Sealed pouches on conveyor, hands aligning |
| c07 | Overhead: finished pouches on blue conveyor |
| c08 | Essence filling nozzle (best in slow motion, 0.3–2.3s) |
| c09 | Heat-seal rollers close-up |
| c10–c13 | Mixing tanks, hall, fermentation vessels. **The user asked not to emphasize these.** |
| c14 | QC hand inspection (wide; the calculator at bottom-left needs cropping) |
| c15 | Hands inspecting pouches (close) |

Workers' faces are visible in c01, c02 and c14. Confirm consent before public use.

## Previously delivered (for context)
- Production film v2: 57.6s, 16:9, with original synthesized music + SFX, tank shots removed. The user has it; the file is not in the repo (64MB).
- Canva text-motion pack (in the repo, as above).
