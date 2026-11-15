/* Minimal Markdown renderer: headings, lists, code, tables, links, bold/italic. */
"use strict";
function esc(s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}
function inlineMd(s) {
  var out = esc(s);
  out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
  out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  out = out.replace(/(^|[^*\w])\*([^*\n]+)\*/g, "$1<em>$2</em>");
  out = out.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2" rel="noopener">$1</a>');
  return out;
}
function renderMarkdown(src) {
  var lines = String(src || "").replace(/\r\n?/g, "\n").split("\n");
  var html = "", i = 0, inCode = false, codeLang = "", codeBuf = [];
  var listOpen = false;
  function closeList() { if (listOpen) { html += "</ul>"; listOpen = false; } }
  function tableRow(cells, head) {
    var tag = head ? "th" : "td";
    return "<tr>" + cells.map(function (c) { return "<" + tag + ">" + inlineMd(c.trim()) + "</" + tag + ">"; }).join("") + "</tr>";
  }
  while (i < lines.length) {
    var line = lines[i];
    if (/^```/.test(line)) {
      if (inCode) {
        html += "<pre><code>" + esc(codeBuf.join("\n")) + "</code></pre>";
        codeBuf = []; inCode = false;
      } else { inCode = true; codeLang = line.slice(3).trim(); }
      i++; continue;
    }
    if (inCode) { codeBuf.push(line); i++; continue; }
    if (/^\s*$/.test(line)) { closeList(); i++; continue; }
    var hm = line.match(/^(#{1,4})\s+(.*)/);
    if (hm) { closeList(); html += "<h" + hm[1].length + ">" + inlineMd(hm[2]) + "</h" + hm[1].length + ">"; i++; continue; }
    if (/^\s*---+\s*$/.test(line)) { closeList(); html += "<hr>"; i++; continue; }
    if (/^\s*>\s?/.test(line)) { closeList(); html += "<blockquote><p>" + inlineMd(line.replace(/^\s*>\s?/, "")) + "</p></blockquote>"; i++; continue; }
    if (/^\s*[-*]\s+/.test(line)) {
      if (!listOpen) { html += "<ul>"; listOpen = true; }
      html += "<li>" + inlineMd(line.replace(/^\s*[-*]\s+/, "")) + "</li>"; i++; continue;
    }
    if (/^\s*\d+[.)]\s+/.test(line)) {
      if (!listOpen) { html += "<ul>"; listOpen = true; }
      html += "<li>" + inlineMd(line.replace(/^\s*\d+[.)]\s+/, "")) + "</li>"; i++; continue;
    }
    if (/\|/.test(line) && i + 1 < lines.length && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i + 1])) {
      closeList();
      var head = line.split("|").filter(function (c, k, a) { return !(k === 0 && c.trim() === "") && !(k === a.length - 1 && c.trim() === ""); });
      html += "<table><thead>" + tableRow(head, true) + "</thead><tbody>";
      i += 2;
      while (i < lines.length && /\|/.test(lines[i]) && !/^\s*$/.test(lines[i])) {
        var cells = lines[i].split("|").filter(function (c, k, a) { return !(k === 0 && c.trim() === "") && !(k === a.length - 1 && c.trim() === ""); });
        html += tableRow(cells, false); i++;
      }
      html += "</tbody></table>"; continue;
    }
    closeList();
    var para = [line]; i++;
    while (i < lines.length && !/^\s*$/.test(lines[i]) && !/^(#{1,4}\s|```|\s*[-*]\s+|\s*\d+[.)]\s+|\s*>)/.test(lines[i])) { para.push(lines[i]); i++; }
    html += "<p>" + inlineMd(para.join(" ").trim()) + "</p>";
  }
  closeList();
  if (inCode) html += "<pre><code>" + esc(codeBuf.join("\n")) + "</code></pre>";
  return html;
}
