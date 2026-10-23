/*
 * hf-timeline.js: a tiny, deterministic, seek-only subset of the GSAP timeline API.
 *
 * Load it AFTER the GSAP <script>. If real GSAP loaded, this file does nothing.
 * If GSAP is unavailable (offline render box), it defines window.gsap with:
 *   gsap.timeline({paused:true}) -> tl.to / tl.from / tl.fromTo / tl.set / tl.seek / tl.duration
 *   positions: number | "<" | ">" | "+=0.2" | "-=0.2" | "<0.1"
 *   props: x y xPercent yPercent scale scaleX scaleY rotation opacity autoAlpha blur
 *          any numeric CSS length (width, height, top, left, letterSpacing, borderRadius...)
 *          textContent (numeric counter; use snap: 1 for integers)
 *   vars: duration ease stagger delay snap (number, or {textContent: 1} like GSAP)
 *   eases: none linear power1-4.(in|out|inOut) sine.* expo.* circ.* back.out(1.7) elastic.out
 * Tweens on the same property should not overlap (a .to() starts from the previous tween's end value).
 */
(function () {
  if (window.gsap && window.gsap.timeline && !window.gsap.__hfShim) return;

  const TRANSFORM = ["x", "y", "xPercent", "yPercent", "scale", "scaleX", "scaleY", "rotation"];
  const UNITLESS = new Set(["opacity", "autoAlpha", "scale", "scaleX", "scaleY", "rotation", "zIndex", "textContent", "xPercent", "yPercent"]);
  const RESERVED = new Set(["duration", "ease", "stagger", "delay", "snap", "onUpdate", "immediateRender"]);

  const P = (k) => (p) => Math.pow(p, k);
  const out = (f) => (p) => 1 - f(1 - p);
  const inOut = (f) => (p) => (p < 0.5 ? f(p * 2) / 2 : 1 - f((1 - p) * 2) / 2);
  const family = { power1: P(2), power2: P(3), power3: P(4), power4: P(5), quad: P(2), cubic: P(3), quart: P(4), quint: P(5),
    sine: (p) => 1 - Math.cos((p * Math.PI) / 2), expo: (p) => (p === 0 ? 0 : Math.pow(2, 10 * p - 10)),
    circ: (p) => 1 - Math.sqrt(1 - p * p) };
  function ease(name) {
    if (typeof name === "function") return name;
    if (!name) name = "power1.out";
    if (name === "none" || name === "linear") return (p) => p;
    const m = /^(\w+)\.(inOut|in|out)(?:\(([\d.]+)\))?$/.exec(name);
    if (!m) return out(P(2));
    const [, fam, dir, arg] = m;
    if (fam === "back") { const s = arg ? +arg : 1.70158; const b = (p) => p * p * ((s + 1) * p - s); return dir === "in" ? b : dir === "out" ? out(b) : inOut(b); }
    if (fam === "elastic") { const e = (p) => (p === 0 || p === 1 ? p : -Math.pow(2, 10 * p - 10) * Math.sin((p * 10 - 10.75) * ((2 * Math.PI) / 3))); return dir === "in" ? e : dir === "out" ? out(e) : inOut(e); }
    const f = family[fam] || P(2);
    return dir === "in" ? f : dir === "out" ? out(f) : inOut(f);
  }

  const states = new Map(); // element -> {initial, current}
  function stateOf(el) {
    if (!states.has(el)) {
      const cs = getComputedStyle(el);
      const init = { x: 0, y: 0, xPercent: 0, yPercent: 0, scale: 1, scaleX: 1, scaleY: 1, rotation: 0, blur: 0,
        opacity: parseFloat(cs.opacity), autoAlpha: parseFloat(cs.opacity) };
      states.set(el, { init, cur: { ...init }, touched: new Set() });
    }
    return states.get(el);
  }
  function initialValue(el, k) {
    const s = stateOf(el);
    if (k in s.init) return s.init[k];
    if (k === "textContent") return (s.init[k] = parseFloat(el.textContent.replace(/[^\d.-]/g, "")) || 0);
    return (s.init[k] = parseFloat(getComputedStyle(el)[k]) || 0);
  }
  function apply(el) {
    const s = stateOf(el), c = s.cur;
    if ([...s.touched].some((k) => TRANSFORM.includes(k))) {
      el.style.transform = `translate(${c.xPercent}%, ${c.yPercent}%) translate(${c.x}px, ${c.y}px) rotate(${c.rotation}deg) scale(${c.scale * c.scaleX}, ${c.scale * c.scaleY})`;
    }
    for (const k of s.touched) {
      if (TRANSFORM.includes(k)) continue;
      const v = c[k];
      if (k === "opacity") el.style.opacity = v;
      else if (k === "autoAlpha") { el.style.opacity = v; el.style.visibility = v <= 0.001 ? "hidden" : "inherit"; }
      else if (k === "blur") el.style.filter = v > 0.01 ? `blur(${v}px)` : "none";
      else if (k === "textContent") el.textContent = c.__fmt ? c.__fmt(v) : String(v);
      else el.style[k] = UNITLESS.has(k) ? v : v + "px";
    }
  }
  function targets(t) {
    if (typeof t === "string") return [...document.querySelectorAll(t)];
    if (t instanceof Element) return [t];
    return [...t];
  }

  function timeline() {
    const tweens = [];
    let end = 0, lastStart = 0, prepared = false;
    const tl = {
      __hfShim: true,
      _add(tg, fromV, toV, pos) {
        const els = targets(tg);
        const dur = toV.duration ?? 0.5, stag = toV.stagger || 0, delay = toV.delay || 0;
        let start;
        if (typeof pos === "number") start = pos;
        else if (pos === "<") start = lastStart;
        else if (typeof pos === "string" && pos.startsWith("<")) start = lastStart + parseFloat(pos.slice(1));
        else if (typeof pos === "string" && /^[+-]=/.test(pos)) start = end + parseFloat(pos.replace("=", ""));
        else start = end; // undefined or ">"
        start += delay;
        els.forEach((el, i) => {
          const props = {};
          for (const k in toV) if (!RESERVED.has(k)) props[k] = { to: toV[k], from: fromV ? fromV[k] : undefined };
          if (fromV) for (const k in fromV) if (!RESERVED.has(k) && !(k in props)) props[k] = { to: undefined, from: fromV[k] };
          tweens.push({ el, start: start + i * stag, dur, ease: ease(toV.ease), snap: toV.snap, props });
        });
        lastStart = start;
        end = Math.max(end, start + (els.length - 1) * stag + dur);
        prepared = false;
        return tl;
      },
      to(t, v, p) { return tl._add(t, null, v, p); },
      from(t, v, p) { const to = {}; for (const k in v) if (RESERVED.has(k)) to[k] = v[k]; return tl._add(t, Object.fromEntries(Object.entries(v).filter(([k]) => !RESERVED.has(k))), { ...to, __from: true }, p); },
      fromTo(t, f, v, p) { return tl._add(t, f, v, p); },
      set(t, v, p) { return tl._add(t, null, { ...v, duration: 0 }, p); },
      duration() { return end; },
      _prepare() {
        // Resolve every tween's start/end values by playing the tween list once in start order.
        tweens.sort((a, b) => a.start - b.start);
        const store = new Map();
        const val = (el, k) => { const m = store.get(el) || store.set(el, {}).get(el); return k in m ? m[k] : initialValue(el, k); };
        for (const tw of tweens) {
          for (const k in tw.props) {
            if (k === "__from") continue;
            const pr = tw.props[k];
            const cur = val(tw.el, k);
            pr.a = pr.from !== undefined ? +pr.from : cur;
            pr.b = pr.to !== undefined ? +pr.to : cur;
            if (k === "textContent") pr.fmt = (n) => n.toLocaleString("en-US");
            store.get(tw.el)[k] = pr.b;
            stateOf(tw.el).touched.add(k);
          }
        }
        prepared = true;
      },
      seek(time) {
        if (!prepared) tl._prepare();
        for (const [, s] of states) s.cur = { ...s.init, __fmt: s.cur.__fmt };
        for (const tw of tweens) {
          const s = stateOf(tw.el);
          for (const k in tw.props) {
            if (k === "__from") continue;
            const pr = tw.props[k];
            if (time < tw.start) { if (!(k in s.cur) || tw === firstTweenFor(tw.el, k)) s.cur[k] = pr.a; continue; }
            const p = tw.dur <= 0 ? 1 : Math.min(1, (time - tw.start) / tw.dur);
            let v = pr.a + (pr.b - pr.a) * tw.ease(p);
            const sn = tw.snap && typeof tw.snap === "object" ? tw.snap[k] : tw.snap;
            if (sn) v = Math.round(v / sn) * sn;
            s.cur[k] = v;
            if (pr.fmt) s.cur.__fmt = pr.fmt;
          }
        }
        for (const [el] of states) apply(el);
        return tl;
      },
      time(t) { return t === undefined ? 0 : tl.seek(t); },
      progress(p) { return tl.seek(p * end); },
      pause() { return tl; }, play() { return tl; },
    };
    const firstCache = new Map();
    function firstTweenFor(el, k) {
      const key = el; let m = firstCache.get(key); if (!m) firstCache.set(key, (m = {}));
      if (!(k in m)) m[k] = tweens.find((t) => t.el === el && k in t.props);
      return m[k];
    }
    return tl;
  }

  window.gsap = { __hfShim: true, timeline, utils: { toArray: targets } };
})();
