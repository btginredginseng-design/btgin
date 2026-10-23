# design.md template

Copy to `projects/<p>/design/design.md` and fill every section. Sub-agents building graphics get this file and
nothing else about style, so if it isn't written here, it will be improvised (and that improvising is what makes graphics look generic).

```markdown
# Design system: <video / series>

## Intent (one sentence)
e.g. "Calm authority: graphics confirm what she says, they never compete with her face."

## Frame
- Resolution / fps: 1920x1080 @ 30 (or 1080x1920 for shorts: redo all positions, don't scale)
- Title-safe: 6% x, 8% y. Nothing with text crosses it (QC enforces this)
- Speaker zone: where the face is (e.g. center-right third). Graphics avoid it unless full-screen
- Graphic zones: left third for cards, top-left for section labels, lower third for keyword pops

## Type
- Display: <font>, weight 800, tracking -2%. Used for numbers and headlines only
- Body: <font>, weight 500
- Sizes (1080p): hero 132 / title 84 / body 46. Never below 40 px (phone legibility)
- Max words on screen: headline 6, keyword pop 3, card item 5

## Color
- Ink #FFFFFF on footage, ink-dark #0B0B0F on accent
- Accent #FFD400: ONE per frame, for the single most important word or number
- Secondary #2F6BFF: data/comparisons only
- Plate rgba(11,11,15,.78) behind any text over busy footage
- Why: <accent chosen against these frames: wardrobe blue, warm set → yellow pops, doesn't clash>

## Motion
- Personality: e.g. "confident, quick in, gentle out"
- In: 0.25–0.35 s, power3.out / back.out(1.6-2.2) for pops. Out: 0.2–0.25 s, power2.in
- Hold: at least reading time = 0.3 s + 0.25 s/word
- Land rule: text lands ON the spoken word (≤ 2 frames early), never after it
- Music: big moments land on downbeats/hits when within 120 ms
- Forbidden: spinning, bouncing loops, drop shadows over 30px blur, more than 2 graphics on screen

## Treatments (what each beat type looks like here)
| Beat | Treatment | Position | Notes |
|---|---|---|---|
| hook | kinetic-headline | center | words land on word timings, longest word = accent |
| stat | number-counter | top-right | counts up, lands on the spoken number |
| list | list-card | left third | items reveal as spoken |
| emphasis | keyword-pop | lower third center | 1–3 words |
| section | section-title | top-left | index + name + rule |
| turn | punch-in | edit-level | 110% scale, 6 frames, no graphic |

## Anti-generic rules
- Every graphic cites a beat ID and its `why`. No beat, no graphic
- No stock "subscribe" animations, no emoji stickers, no whoosh on every graphic
- Same treatment = same position, size and motion every time it appears in the video
- One idea per graphic; if it needs two lines of explanation it's a B-roll shot, not a graphic
```

## How to choose well
- **Contrast is measured, not felt**: accent vs the 3 most common background colors should be ≥ 3:1 (text ≥ 4.5:1 on plates).
- **Restraint scales with runtime**: long-form ≈ 1 graphic / 15–25 s; shorts ≈ 1 / 3–5 s.
- **Motion signals meaning**: in-animations that echo the content (a counter for growth, a strike-through for a myth)
  beat decorative motion every time.
