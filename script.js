const $ = (id) => document.getElementById(id);
const today = new Date();
$("today").textContent = today.toLocaleDateString("en-AU",{weekday:"short",day:"numeric",month:"short",year:"numeric"}).toUpperCase()+"  /  MGC DAILY BRIEF";
$("year").textContent = today.getFullYear();
$("brief-date").textContent = today.toLocaleDateString("en-AU",{day:"numeric",month:"long",year:"numeric"}).toUpperCase();
const menu = document.querySelector(".menu-toggle");
menu.addEventListener("click",()=>{const nav=document.querySelector("nav");nav.classList.toggle("open");menu.setAttribute("aria-expanded",nav.classList.contains("open"));});
document.querySelectorAll("nav a").forEach(a=>a.addEventListener("click",()=>document.querySelector("nav").classList.remove("open")));
fetch("brief.json").then(r=>r.json()).then(data=>{
  $("edition").textContent=data.edition||"001";
  $("brief-title").textContent=data.title||"The cycling world, in one briefing.";
  $("brief-summary").textContent=data.summary||"";
  $("lead-title").textContent=data.lead.title;
  $("lead-text").textContent=data.lead.summary;
  $("lead-link").href=data.lead.url||"#";
  $("results-title").textContent=data.results.title;
  $("results-text").textContent=data.results.summary;
  $("results-link").href=data.results.url||"#";
  $("tech-title").textContent=data.technology.title;
  $("tech-text").textContent=data.technology.summary;
  $("tech-link").href=data.technology.url||"#";
  $("editor-note").textContent=data.editorNote||"";
}).catch(()=>{});
fetch("config.json").then(r=>r.json()).then(data=>{
  if(data.facebookUrl){$("facebook-link").href=data.facebookUrl;$("facebook-link").target="_blank";}
  if(data.stravaUrl){$("strava-link").href=data.stravaUrl;$("strava-link").target="_blank";}
  if(data.facebookUrl&&data.stravaUrl)$("link-note").textContent="Find the crew on Facebook and Strava.";
});
