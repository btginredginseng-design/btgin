# btgin

QR insert-card landing pages for BTGin red ginseng customers who bought on
Naver Smart Store, built as Cafe24 skin files for btginmall.com.

## Flow

```
QR code  →  btginmall.com/qr/        language picker, centred on the phone screen
              ├─ 한국어 (Korean)  →  btginmall.com/thanks/   thank-you page inside the store layout
              └─ English          →  btginwell.com
```

| File | Cafe24 skin path | Live URL |
|---|---|---|
| `cafe24/qr/index.html` | `/qr/index.html` | `https://btginmall.com/qr/` (put this in the QR code) |
| `cafe24/thanks/index.html` | `/thanks/index.html` | `https://btginmall.com/thanks/` |

- **`/qr/`** is a standalone full-screen page with no store header or footer,
  so the two language buttons sit in the middle of the screen.
- **`/thanks/`** starts with `<!--@layout(/layout/basic/layout.html)-->`, so
  Cafe24 wraps it in the store's own header, footer and fonts. Its buttons link
  to the store's home, sign-up, reviews, Q&A and notices pages.

## Installing on Cafe24

Do this for **both the PC and the mobile design** if the store uses separate
skins (QR scans come from phones, so the mobile skin matters most). If the
store uses one responsive skin, do it once.

1. Cafe24 admin → **디자인 (Design)** → open the design that is currently in use in the
   **스마트디자인 편집 (Smart Design editor)**.
2. In the editor, add a new screen or file at `/qr/index.html` and paste in
   `cafe24/qr/index.html`.
3. Add another at `/thanks/index.html` and paste in `cafe24/thanks/index.html`.
4. Save, then open `https://btginmall.com/qr/` on a phone and tap both buttons.
5. Make the QR code from `https://btginmall.com/qr/`.

## Matching the store's look

- Colours are set as variables at the top of the `<style>` block in each file
  and were taken from btginmall.com: logo blue `#03419c`, text `#181818`,
  warm-grey cards `#eceae8`, charcoal banner, white pill buttons. The QR page
  uses the Pretendard font.
- Both pages are built for phones and tablets, since they are only reached
  by scanning the QR code. The `/thanks/` page is Korean only; English
  visitors go to btginwell.com from the language picker.
- `cafe24/qr/index.html` shows the BTGin logo, built into the page as a data
  URI so no image hosting is needed. Edit `cafe24/qr/index.src.html` (or
  replace `cafe24/qr/img/btgin-logo.webp`), then run
  `python3 cafe24/qr/build.py` to regenerate `index.html`.
- In `cafe24/thanks/index.html`, the Cafe24 store layout already supplies the
  header, footer and fonts.

## Things to check

- **Board links** use Cafe24's default board numbers (`board_no=1` notices,
  `4` reviews, `6` product Q&A). Check them under **게시판 관리 (Board management)** and edit them
  if your store's numbers are different.
- **Layout path:** if the store's main layout file isn't
  `/layout/basic/layout.html`, change the first line of the thanks page to match.

## Phones held sideways: header hides on scroll (`cafe24/motion/landscape-header.html`)

On a phone held sideways the store header and bottom menu cover about half the
screen. This block slides both away while scrolling down and brings them back
when scrolling up. PC, tablets and upright phones are unchanged, and nothing
runs on page load, so pages never flash or jump.

- **Install:** paste the file at the very end of `/_cpb/base.html` in the Smart
  Design editor (keep everything already there).
- **Undo:** delete the block (it starts with the `bth-land-hdr` comment).
- An earlier, larger motion block was removed: hiding the store's loading
  cover made pages flash while the banners were still being built.
