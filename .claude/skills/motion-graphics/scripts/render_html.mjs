#!/usr/bin/env node
/*
 * Render a Hyperframes-style HTML composition to video, frame by frame.
 *
 *   node render_html.mjs graphics/B09/index.html -o graphics/B09/out.mov [--fps 30] [--opaque] [--engine auto|hyperframes|playwright]
 *   node render_html.mjs graphics/B09/index.html --still 1.2 -o graphics/B09/check.png    # one frame, for self-review
 *
 * Engine "hyperframes" shells out to `npx hyperframes render` (if installed).
 * Engine "playwright" (the fallback) loads the page in headless Chromium, and for every frame:
 *   1. seeks window.__timelines[<data-composition-id>] to t   (GSAP or hf-timeline.js shim)
 *   2. toggles .clip[data-start][data-duration] elements visible only inside their window
 *   3. screenshots with a transparent background and pipes PNGs into FFmpeg
 * Output with alpha is ProRes 4444 (.mov); --opaque gives H.264 (.mp4).
 * Size, duration come from the root's data-width / data-height / data-duration.
 */
import { spawn, spawnSync } from "node:child_process";
import { createRequire } from "node:module";
import { existsSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : def; };
const flag = (name) => args.includes(name);
const input = args.find((a) => !a.startsWith("-") && a.endsWith(".html"));
if (!input) { console.error("usage: render_html.mjs comp.html -o out.mov [--fps 30] [--opaque] [--still T]"); process.exit(2); }
const out = opt("-o", input.replace(/\.html$/, flag("--opaque") ? ".mp4" : ".mov"));
const fps = parseFloat(opt("--fps", "30"));
const engine = opt("--engine", "auto");
const still = opt("--still", null);

function loadPlaywright() {
  const req = createRequire(import.meta.url);
  const roots = [process.cwd(), path.dirname(process.execPath) + "/../lib/node_modules", "/opt/node22/lib/node_modules", "/usr/lib/node_modules", "/usr/local/lib/node_modules"];
  for (const r of roots) { try { return req(req.resolve("playwright", { paths: [r] })); } catch {} }
  throw new Error("playwright not found: npm i -g playwright");
}

function tryHyperframes() {
  const which = spawnSync("npx", ["--no-install", "hyperframes", "--version"], { encoding: "utf8" });
  if (which.status !== 0) return false;
  const r = spawnSync("npx", ["--no-install", "hyperframes", "render", input, "--output", out, "--fps", String(fps)], { stdio: "inherit" });
  return r.status === 0;
}

if (!still && (engine === "hyperframes" || engine === "auto") && tryHyperframes()) {
  console.log(`[render_html] hyperframes -> ${out}`);
  process.exit(0);
}
if (engine === "hyperframes") { console.error("hyperframes CLI not available"); process.exit(1); }

const { chromium } = loadPlaywright();
const browser = await chromium.launch(existsSync("/opt/pw-browsers/chromium") ? {} : {});
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.error("[page error]", e.message));
// Fail fast on blocked CDNs instead of hanging; hf-timeline.js covers GSAP offline.
await page.route(/^https?:\/\//, (route) => route.abort().catch(() => {}));
await page.goto(pathToFileURL(path.resolve(input)).href, { waitUntil: "load" });
await page.addStyleTag({ content: "*,*::before,*::after{animation-play-state:paused!important;transition:none!important;caret-color:transparent!important}" });
await page.evaluate(() => document.fonts && document.fonts.ready);

const meta = await page.evaluate(() => {
  const root = document.querySelector("[data-composition-id]");
  if (!root) return null;
  return { id: root.dataset.compositionId, w: +root.dataset.width || 1920, h: +root.dataset.height || 1080,
           d: +root.dataset.duration || 0, hasTl: !!(window.__timelines && window.__timelines[root.dataset.compositionId]) };
});
if (!meta) { console.error("no element with data-composition-id"); process.exit(1); }
if (!meta.hasTl) console.error(`[warn] window.__timelines["${meta.id}"] not registered; rendering static frames`);
await page.setViewportSize({ width: meta.w, height: meta.h });

async function seek(t) {
  await page.evaluate(([id, t]) => {
    const tl = window.__timelines && window.__timelines[id];
    if (tl) (tl.seek ? tl.seek(t, false) : tl.time(t));
    document.querySelectorAll(".clip[data-start]").forEach((el) => {
      const s = +el.dataset.start, d = +(el.dataset.duration || 1e9);
      el.style.visibility = t >= s && t < s + d ? "visible" : "hidden";
    });
  }, [meta.id, t]);
}
const root = await page.$("[data-composition-id]");
const shot = () => root.screenshot({ omitBackground: !flag("--opaque"), type: "png" });

if (still) {
  await seek(parseFloat(still));
  await root.screenshot({ path: out, omitBackground: !flag("--opaque") });
  console.log(`[render_html] still t=${still}s -> ${out}`);
  await browser.close();
  process.exit(0);
}

const frames = Math.max(1, Math.round(meta.d * fps));
const enc = flag("--opaque")
  ? ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16"]
  : ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-vendor", "apl0"];
const ff = spawn("ffmpeg", ["-y", "-v", "error", "-f", "image2pipe", "-framerate", String(fps), "-i", "-", ...enc, out], { stdio: ["pipe", "inherit", "inherit"] });
for (let i = 0; i < frames; i++) {
  await seek(i / fps);
  const buf = await shot();
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
}
ff.stdin.end();
await new Promise((r) => ff.on("close", r));
await browser.close();
console.log(`[render_html] playwright ${frames} frames @${fps} (${meta.w}x${meta.h}) -> ${out}`);
