"use strict";
const $ = (s) => document.querySelector(s);
const state = { q: "", tags: new Set() };
const SVG = (p) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${p}</svg>`;
/* ── Theme ─────────────────────────────────────────────────── */
const THEMES = ["auto", "light", "dark"];
const TICON = {
  auto:  SVG('<rect width="20" height="14" x="2" y="3" rx="2"/><path d="M8 21h8M12 17v4"/>'),
  light: SVG('<circle cx="12" cy="12" r="5"/><path d="M12 1v3M12 20v3M4 12H1M23 12h-3M5.6 5.6 3.5 3.5M20.5 20.5l-2.1-2.1M5.6 18.4l-2.1 2.1M20.5 3.5l-2.1 2.1"/>'),
  dark:  SVG('<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>'),
};
function applyTheme(t) {
  document.documentElement.dataset.theme = t;
  $("#themeBtn").innerHTML = TICON[t];
  $("#themeBtn").title = "테마: " + t;
  try { localStorage.setItem("shelf-theme", t); } catch (e) {}
}
(function () { let t = "auto"; try { t = localStorage.getItem("shelf-theme") || "auto"; } catch (e) {} applyTheme(THEMES.includes(t) ? t : "auto"); })();
$("#themeBtn").addEventListener("click", () => applyTheme(THEMES[(THEMES.indexOf(document.documentElement.dataset.theme) + 1) % 3]));


/* ── URL hash (shareable) ──────────────────────────────────── */
function readHash() {
  const h = new URLSearchParams(location.hash.slice(1));
  state.q = h.get("q") || ""; state.tags = new Set((h.get("tags") || "").split(",").filter(Boolean));
  $("#search").value = state.q; $("#searchWrap").classList.toggle("has-value", !!state.q);
}
function writeHash() {
  const h = new URLSearchParams();
  if (state.q) h.set("q", state.q);
  if (state.tags.size) h.set("tags", [...state.tags].join(","));
  history.replaceState(null, "", h.toString() ? "#" + h.toString() : location.pathname + location.search);
}


/* The HTML is the catalog. JavaScript only enhances existing elements. */
const groups = [...document.querySelectorAll('#contentList .group')].map((element) => ({
  element,
  cards: [...element.querySelectorAll('.card')].map((card) => {
    const name = card.querySelector('.ctitle a');
    const desc = card.querySelector('.desc');
    const tags = [...card.querySelectorAll('[data-tag]')].map((chip) => chip.dataset.tag);
    return { element: card, tags,
      haystack: `${name.textContent} ${desc?.title || ''} ${tags.join(' ')}`.toLowerCase(),
      text: [name, desc].filter(Boolean).map((element) => ({ element, html: element.innerHTML })) };
  }),
}));
let previousQuery = '';
function highlight(element, html, terms) {
  element.innerHTML = html; // Original build-time HTML, never the search query.
  if (!terms.length) return;
  const escaped = terms.map((term) => term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const pattern = new RegExp(escaped.sort((a, b) => b.length - a.length).join('|'), 'gi');
  const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    const text = node.textContent;
    const fragment = document.createDocumentFragment();
    let last = 0;
    for (const match of text.matchAll(pattern)) {
      fragment.append(text.slice(last, match.index));
      const mark = document.createElement('mark');
      mark.textContent = match[0];
      fragment.append(mark);
      last = match.index + match[0].length;
    }
    if (last) { fragment.append(text.slice(last)); node.replaceWith(fragment); }
  }
}
function toggleTag(tag) {
  state.tags.has(tag) ? state.tags.delete(tag) : state.tags.add(tag);
  writeHash(); render();
}
function render() {
  const terms = state.q.toLowerCase().split(/\s+/).filter(Boolean);
  let shown = 0;
  for (const group of groups) {
    let count = 0;
    for (const card of group.cards) {
      const matches = [...state.tags].every((tag) => card.tags.includes(tag)) && terms.every((term) => card.haystack.includes(term));
      card.element.hidden = !matches;
      if (matches) count++;
      if (previousQuery !== state.q) for (const text of card.text) highlight(text.element, text.html, terms);
    }
    group.element.hidden = !count;
    group.element.querySelector('.badge').textContent = count;
    shown += count;
  }
  previousQuery = state.q;
  $('#empty').hidden = shown !== 0;
  $('#count').innerHTML = `<b>${shown}</b>개 표시 중`;
  $('#clearBtn').hidden = !(state.q || state.tags.size);
  $('#activeTags').replaceChildren();
  for (const tag of state.tags) {
    const button = document.createElement('button');
    button.className = 'chip active'; button.dataset.tag = tag;
    button.textContent = `#${tag} ✕`;
    button.setAttribute('aria-label', `${tag} 필터 해제`);
    $('#activeTags').append(button);
  }
  document.querySelectorAll('#taglist .chip, .card .chip').forEach((chip) => {
    const active = state.tags.has(chip.dataset.tag);
    chip.classList.toggle('active', active);
    chip.setAttribute('aria-pressed', String(active));
  });
}

/* Avatars only load near the viewport; hidden cards keep their placeholders. */
function loadImage(image) {
  image.addEventListener('error', () => image.remove(), { once: true });
  image.src = image.dataset.src;
  delete image.dataset.src;
}
function observeImages() {
  const images = document.querySelectorAll('img[data-src]');
  if (!('IntersectionObserver' in window)) { images.forEach(loadImage); return; }
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) if (entry.isIntersecting && !entry.target.closest('[hidden]')) {
      loadImage(entry.target); observer.unobserve(entry.target);
    }
  }, { rootMargin: '100px' });
  images.forEach((image) => observer.observe(image));
}
function observeSections() {
  if (!('IntersectionObserver' in window)) return;
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) if (entry.isIntersecting && !entry.target.hidden) {
      const key = entry.target.id.replace('sec-', '');
      document.querySelectorAll('.navrow').forEach((link) => link.classList.toggle('active', link.dataset.sec === key));
    }
  }, { rootMargin: '-90px 0px -75% 0px' });
  groups.forEach((group) => observer.observe(group.element));
}

/* ── Events ────────────────────────────────────────────────── */
let deb;
$("#search").addEventListener("input", (e) => {
  state.q = e.target.value; $("#searchWrap").classList.toggle("has-value", !!state.q);
  clearTimeout(deb); deb = setTimeout(() => { writeHash(); render(); }, 110);
});
$("#searchClear").addEventListener("click", () => { state.q = ""; $("#search").value = ""; $("#searchWrap").classList.remove("has-value"); writeHash(); render(); $("#search").focus(); });
$("#clearBtn").addEventListener("click", () => { state.q = ""; state.tags.clear(); $("#search").value = ""; $("#searchWrap").classList.remove("has-value"); writeHash(); render(); });
document.addEventListener("keydown", (e) => {
  if (e.key === "/" && document.activeElement !== $("#search")) { e.preventDefault(); $("#search").focus(); }
  if (e.key === "Escape") { if (document.activeElement === $("#search")) $("#searchClear").click(); document.body.classList.remove("nav-open"); }
});
$("#menuBtn").addEventListener("click", () => document.body.classList.toggle("nav-open"));
$("#scrim").addEventListener("click", () => document.body.classList.remove("nav-open"));
const toTop = $("#toTop");
addEventListener("scroll", () => toTop.classList.toggle("show", scrollY > 600), { passive: true });
toTop.addEventListener("click", () => scrollTo({ top: 0, behavior: "smooth" }));
(function () { const m = location.hostname.match(/^([^.]+)\.github\.io$/); if (m) $("#repoLink").href = `https://github.com/${m[1]}/${location.pathname.split("/").filter(Boolean)[0] || ""}`; })();


document.addEventListener('click', (event) => {
  const chip = event.target.closest('button[data-tag]');
  if (chip) toggleTag(chip.dataset.tag);
});
document.querySelectorAll('.navrow').forEach((link) => link.addEventListener('click', (event) => {
  event.preventDefault();
  document.getElementById('sec-' + link.dataset.sec)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  document.body.classList.remove('nav-open');
}));
readHash(); render(); observeImages(); observeSections();
addEventListener('hashchange', () => { readHash(); render(); });
