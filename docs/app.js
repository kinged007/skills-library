/* Skills Library site: list + filters + detail. No deps. */
"use strict";
var S = { data: null, byId: {}, filters: { q: "", cat: "", type: "", src: "", min: 0, tag: "", sort: "top" } };
function $(id) { return document.getElementById(id); }
function escH(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
function score(e) { return (e.rating && e.rating.score) || 0; }
function reviewed(e) { return (e.rating && e.rating.reviewed) || ""; }
function stripFm(md) {
  var m = String(md || "").match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!m) return { fm: {}, body: String(md || "") };
  var fm = {};
  m[1].split("\n").forEach(function (l) { var k = l.match(/^(\w+):\s*(.*)$/); if (k) fm[k[1]] = k[2]; });
  return { fm: fm, body: m[2] };
}
function badge(e) {
  var b = e.type === "local" ? '<span class="badge own">own skill</span>' : '<span class="badge ref">reference</span>';
  return b + ' <span class="badge score" title="Rating score 1–5">★ ' + score(e) + "/5</span>" +
    (e.template ? ' <span class="badge">template</span>' : "") +
    ' <span class="badge">' + escH(e.category) + "</span>";
}
function tagsHtml(e) {
  return (e.tags || []).map(function (t) { return '<button type="button" data-tag="' + escH(t) + '">' + escH(t) + "</button>"; }).join("");
}
function cardHtml(e) {
  return '<li class="card"><h2><a href="#/skill/' + escH(e.id) + '">' + escH(e.title) + "</a></h2>" +
    '<div class="badges">' + badge(e) + "</div>" +
    '<p class="summary">' + escH(e.summary) + "</p>" +
    '<p class="meta">' + escH(e.type === "local" ? e.path : e.source + " · " + (e.skill || "")) + "</p>" +
    '<div class="tags">' + tagsHtml(e) + "</div>" +
    '<div class="install"><code>' + escH(e.install) + '</code><button class="copy-btn" type="button" data-copy="' + escH(e.install) + '">Copy</button></div></li>';
}
function applyFilters() {
  var f = S.filters, q = f.q.trim().toLowerCase();
  var out = S.data.skills.filter(function (e) {
    if (f.cat && e.category !== f.cat) return false;
    if (f.type && e.type !== f.type) return false;
    if (f.src && e.source !== f.src) return false;
    if (score(e) < f.min) return false;
    if (f.tag && (e.tags || []).indexOf(f.tag) < 0) return false;
    if (q) {
      var hay = (e.title + " " + e.summary + " " + e.id + " " + (e.source || "") + " " + (e.tags || []).join(" ")).toLowerCase();
      if (hay.indexOf(q) < 0) return false;
    }
    return true;
  });
  if (f.sort === "az") out.sort(function (a, b) { return a.title.localeCompare(b.title); });
  else if (f.sort === "recent") out.sort(function (a, b) { return (reviewed(b) || "").localeCompare(reviewed(a) || "") || score(b) - score(a); });
  else out.sort(function (a, b) { return score(b) - score(a) || a.title.localeCompare(b.title); });
  return out;
}
