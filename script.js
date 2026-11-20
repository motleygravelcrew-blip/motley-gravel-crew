const $ = (id) => document.getElementById(id);
const today = new Date();
if ($("today")) $("today").textContent = today.toLocaleDateString("en-AU", {weekday:"short", day:"numeric", month:"short", year:"numeric"}).toUpperCase() + "  /  MGC";
if ($("year")) $("year").textContent = today.getFullYear();
if ($("brief-date")) $("brief-date").textContent = "AWAITING FIRST EDITION";
const menu = document.querySelector(".menu-toggle");
const nav = document.querySelector("#nav");
if (menu && nav) menu.addEventListener("click", () => { nav.classList.toggle("open"); menu.setAttribute("aria-expanded", nav.classList.contains("open")); });
if (nav) nav.querySelectorAll("a").forEach(a => a.addEventListener("click", () => { nav.classList.remove("open"); if(menu) menu.setAttribute("aria-expanded", "false"); }));
fetch("brief.json").then(r => { if(!r.ok) throw new Error("No published brief"); return r.json(); }).then(data => {
  if ($("edition")) $("edition").textContent = data.edition || "001";
  if ($("brief-title")) $("brief-title").textContent = data.title || "The cycling world, in one briefing.";
  if ($("brief-summary")) $("brief-summary").textContent = data.summary || "";
  if (data.lead) { if($("lead-title")) $("lead-title").textContent = data.lead.title || ""; if($("lead-text")) $("lead-text").textContent = data.lead.summary || ""; if($("lead-link")) $("lead-link").href = data.lead.url || "#news"; }
  if (data.results) { if($("results-title")) $("results-title").textContent = data.results.title || ""; if($("results-text")) $("results-text").textContent = data.results.summary || ""; if($("results-link")) $("results-link").href = data.results.url || "#racing"; }
  if (data.technology) { if($("tech-title")) $("tech-title").textContent = data.technology.title || ""; if($("tech-text")) $("tech-text").textContent = data.technology.summary || ""; if($("tech-link")) $("tech-link").href = data.technology.url || "#technology"; }
  if (data.date && $("brief-date")) $("brief-date").textContent = data.date;
  if (data.editorNote && $("editor-note")) $("editor-note").textContent = data.editorNote;
}).catch(() => {});
fetch("config.json").then(r => r.json()).then(data => {
  if (data.facebookUrl && $("facebook-link")) $("facebook-link").href = data.facebookUrl;
  if (data.stravaUrl && $("strava-link")) $("strava-link").href = data.stravaUrl;
}).catch(() => {});
