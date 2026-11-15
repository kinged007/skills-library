/* Views, routing and boot. Requires md.js + app.js (first half). */
"use strict";
function syncInputs() {
  $("q").value = S.filters.q; $("category").value = S.filters.cat;
  $("type").value = S.filters.type; $("source").value = S.filters.src;
  $("minScore").value = String(S.filters.min); $("tag").value = S.filters.tag;
  $("sort").value = S.filters.sort;
}
function renderList() {
  var list = applyFilters();
  var total = S.data.skills.length;
  $("count").textContent = "Showing " + list.length + " of " + total + " skills";
  var v = $("view");
  if (!list.length) { v.innerHTML = '<p class="empty">No skills match these filters. Try clearing search or tag.</p>'; return; }
  v.innerHTML = '<ul class="cards">' + list.map(cardHtml).join("") + "</ul>";
}
function sideHtml(e) {
  var rows = [];
  rows.push("<dt>Type</dt><dd>" + (e.type === "local" ? "Own skill (this repo)" : "Reference (upstream)") + "</dd>");
  rows.push("<dt>Category</dt><dd>" + escH(e.category) + "</dd>");
  rows.push("<dt>Rating</dt><dd>★ " + score(e) + "/5" + (reviewed(e) ? " · reviewed " + escH(reviewed(e)) : " · not reviewed") + "</dd>");
  if (e.type === "external") rows.push("<dt>Source</dt><dd>" + escH(e.source) + " · " + escH(e.skill || "") + "</dd>");
  if (e.template) rows.push("<dt>Template</dt><dd>Fill in the Project config before use.</dd>");
  if (e.derived_from) rows.push("<dt>Adapted from</dt><dd>" + escH(e.derived_from.source) + " (" + escH(e.derived_from.license) + ")</dd>");
  return '<aside class="detail-side"><div class="install" style="margin-bottom:12px"><code>' + escH(e.install) +
    '</code><button class="copy-btn" type="button" data-copy="' + escH(e.install) + '">Copy</button></div>' +
    "<dl>" + rows.join("") + "</dl>" +
    '<p style="margin:12px 0 0"><a href="' + escH(e.url) + '">GitHub folder ↗</a></p></aside>';
}
function renderDetail(id) {
  var e = S.byId[id], v = $("view");
  if (!e) { v.innerHTML = '<p class="empty">Unknown skill. <a href="#/">Back to all skills</a>.</p>'; return; }
  var tags = (e.tags || []).map(function (t) { return '<button type="button" data-tag="' + escH(t) + '">' + escH(t) + "</button>"; }).join("");
  v.innerHTML = '<div class="detail-head"><a class="back" href="#/">← All skills</a><h1>' + escH(e.title) + "</h1>" +
    '<div class="badges">' + badge(e) + "</div></div>" +
    '<p class="lead">' + escH(e.summary) + "</p>" +
    (e.notes ? '<p class="note">' + escH(e.notes) + "</p>" : "") +
    '<div class="tags" style="margin-bottom:14px">' + tags + "</div>" +
    '<div class="detail-grid">' + sideHtml(e) + '<div class="detail-body" id="skillbody"><p class="meta">Loading SKILL.md…</p></div></div>';
  var show = function (md, live) {
    var p = stripFm(md);
    var head = (p.fm.description ? "<p class=\"lead\">" + escH(p.fm.description) + "</p>" : "") +
      (live ? '<p class="meta">Live from upstream <a href="' + escH(e.rawUrl) + '">SKILL.md</a> — always latest, never vendored here.</p>' : "");
    $("skillbody").innerHTML = '<article class="markdown">' + head + renderMarkdown(p.body) + "</article>";
  };
  if (e.type === "local") { show(e.body || "", false); return; }
  fetch(e.rawUrl).then(function (r) {
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.text();
  }).then(function (md) { show(md, true); })
  .catch(function () {
    $("skillbody").innerHTML = '<p class="error">Could not load the live SKILL.md from upstream (network or rate limit). ' +
      'Read it on GitHub instead: <a href="' + escH(e.url) + '">' + escH(e.url) + "</a>.</p>";
  });
}
function route() {
  var h = location.hash || "#/";
  var m = h.match(/^#\/skill\/([\w.-]+)/);
  if (m) renderDetail(decodeURIComponent(m[1]));
  else renderList();
}
function fillFilters() {
  var cats = Object.keys(S.data.categories).sort();
  $("category").innerHTML = '<option value="">All categories</option>' +
    cats.map(function (c) { return '<option value="' + escH(c) + '">' + escH(c) + "</option>"; }).join("");
  var srcs = Array.from(new Set(S.data.skills.filter(function (e) { return e.source; }).map(function (e) { return e.source; }))).sort();
  $("source").innerHTML = '<option value="">All sources</option>' +
    srcs.map(function (s) { return '<option value="' + escH(s) + '">' + escH(s) + "</option>"; }).join("");
  var tags = Array.from(new Set(S.data.skills.flatMap(function (e) { return e.tags || []; }))).sort();
  $("taglist").innerHTML = tags.map(function (t) { return '<option value="' + escH(t) + '">'; }).join("");
}
function readInputs() {
  S.filters = {
    q: $("q").value, cat: $("category").value, type: $("type").value,
    src: $("source").value, min: parseInt($("minScore").value || "0", 10) || 0,
    tag: $("tag").value.trim(), sort: $("sort").value
  };
}
function boot() {
  document.addEventListener("click", function (ev) {
    var cp = ev.target.closest("[data-copy]");
    if (cp) {
      var txt = cp.getAttribute("data-copy");
      var done = function () { cp.textContent = "Copied ✓"; setTimeout(function () { cp.textContent = "Copy"; }, 1500); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, done);
      else { var ta = document.createElement("textarea"); ta.value = txt; document.body.appendChild(ta); ta.select(); try { document.execCommand("copy"); } catch (x) {} ta.remove(); done(); }
      return;
    }
    var tg = ev.target.closest("[data-tag]");
    if (tg) {
      if ((location.hash || "#/").indexOf("#/skill/") === 0) location.hash = "#/";
      $("tag").value = tg.getAttribute("data-tag");
      readInputs(); renderList();
      document.getElementById("filters").scrollIntoView();
    }
  });
  ["q", "category", "type", "source", "minScore", "tag", "sort"].forEach(function (id) {
    $(id).addEventListener("input", function () {
      if ((location.hash || "#/") !== "#/") { location.hash = "#/"; }
      readInputs(); renderList();
    });
    $(id).addEventListener("change", function () {
      if ((location.hash || "#/") !== "#/") { location.hash = "#/"; }
      readInputs(); renderList();
    });
  });
  $("reset").addEventListener("click", function () {
    S.filters = { q: "", cat: "", type: "", src: "", min: 0, tag: "", sort: "top" };
    syncInputs(); location.hash = "#/"; renderList();
  });
  window.addEventListener("hashchange", route);
  fetch("catalog.json").then(function (r) {
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  }).then(function (d) {
    S.data = d;
    d.skills.forEach(function (e) { S.byId[e.id] = e; });
    var own = d.skills.filter(function (e) { return e.type === "local"; }).length;
    var srcs = new Set(d.skills.filter(function (e) { return e.source; }).map(function (e) { return e.source; })).size;
    var st = $("stats");
    st.hidden = false;
    st.textContent = d.skills.length + " skills · " + own + " own · " + (d.skills.length - own) + " references · " + srcs + " sources";
    $("generated").textContent = "Catalog data generated " + (d.generated_at || "") + " (UTC).";
    $("loading") && $("loading").remove();
    fillFilters(); syncInputs(); route();
  }).catch(function (err) {
    $("view").innerHTML = '<p class="error">Could not load catalog.json (' + escH(err.message) + ").</p>";
  });
}
document.addEventListener("DOMContentLoaded", boot);
