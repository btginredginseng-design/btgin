# 06: Photos, videos and the Reel draft

## Main lesson from the first shoot

**Shoot in daylight.** Every shot taken in the evening under room light makes the pink pack look **lilac/purple** and the white table look grey-green. The one photo taken around noon shows the true **pink**. Inconsistent colour across posts makes a brand look unprofessional.

---

## Photos received (8)

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

### Processing done for the website
- Rotated per EXIF, cropped, resized to 900 px wide, JPEG quality 82.
- **Colour correction:** white balance from the bright, low-saturation pixels (the white table), then whites lifted. Applied at 90% strength to photos #3 and #7. Photo #8 was left untouched.
- Results: `assets/stick-in-hand.jpg` (from #8, 900×1200), `assets/easy-cut.jpg` (from #3, 900×900, scissors cropped out), `assets/powder.jpg` (from #7, 900×1200).

---

## Video 1: unboxing (`20261023_213918.mp4`)

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

## Video 2: pour into water (`IMG_6301.mov`)

- 4.85 s, vertical (stored 1920×1080, rotated −90°), HEVC, **60 fps**. Silent (−60 dB). iPhone 16 Pro Max, recorded 15 Oct 2026 ~22:41 KST (same evening session).
- Table-height camera. A stick pours powder into a **clear glass mug of water** on a white table; the box is softly blurred behind on the left; no hands in shot.
- Strengths: clean, natural angle, nice powder stream; 60 fps allows smooth slow motion.
- Problems:
  - Lilac colour (evening light) and a cold grey-blue wall.
  - Box cut off at the left edge; mug handle cut off on the right; a white object in the top-right corner.
  - **No stirring:** a clump of powder floats and the water ends cloudy. Add 2–3 s of stirring next time.

---

## Reel draft (done)

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

## Reshoot list (one daytime session, about 30 minutes)

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
