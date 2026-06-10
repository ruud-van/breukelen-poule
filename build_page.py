import json

d = json.load(open("data.json"))
DATA = json.dumps(d, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Breukelen-bookmaker poule</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:wght@400;500;600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{
  --felt:#1E8049; --felt2:#176B40; --paper:#F7F4ED; --ink:#1A1714;
  --brass:#C8922A; --up:#1F8A5B; --down:#C2402F; --rule:#E3DDCD; --muted:#897F70;
  --chip:#EDE8DA;
}
*{box-sizing:border-box}
html,body{margin:0;overflow-x:hidden}
body{background:var(--paper);color:var(--ink);
  font-family:"Public Sans",system-ui,sans-serif;line-height:1.5;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px 64px}
.mono{font-family:"Space Mono",monospace;font-variant-numeric:tabular-nums}
.bg{position:fixed;inset:0;width:100%;height:100%;z-index:-1;opacity:.05;pointer-events:none}

/* header board */
.board{background:var(--felt);color:#F2EEDF;width:100%;position:relative;overflow:hidden}
.pitch{position:absolute;inset:0;width:100%;height:100%;z-index:1}
.board-in{max-width:1120px;margin:0 auto;padding:34px 20px 28px;position:relative;z-index:2;
  display:flex;justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap}
.titlerow{display:flex;align-items:center;gap:15px}
.ball{width:48px;height:48px;flex:none}
.intro{background:#fff;border:1px solid var(--rule);border-left:4px solid var(--felt);
  border-radius:3px;padding:18px 22px;margin-top:22px;font-size:15px;line-height:1.7;color:#3c372f}
.intro .nb{color:inherit;font-weight:400}
.intro .los{display:block;margin-top:8px;font-size:13.5px;color:var(--muted)}
.upd{margin-top:10px;font-size:12.5px;color:var(--muted)}
.odhint{padding:2px 16px 12px;font-size:11.5px;color:var(--muted);line-height:1.5}
.chartbtns{display:flex;gap:6px}
.cbtn{font-family:"Space Mono",monospace;font-size:11px;border:1px solid var(--rule);background:#fff;color:var(--muted);padding:4px 11px;border-radius:3px;cursor:pointer}
.cbtn.on{background:var(--felt);color:#F2EEDF;border-color:var(--felt)}
.brand h1{font-family:"Archivo",sans-serif;font-weight:900;font-size:clamp(30px,5vw,52px);
  letter-spacing:-.02em;line-height:.95;margin:0}
.brand .sub{font-family:"Space Mono",monospace;text-transform:uppercase;
  letter-spacing:.28em;font-size:12px;color:var(--brass);margin-top:10px}
.meta{display:flex;gap:26px;text-align:right}
.meta .m{}
.meta .m b{font-family:"Archivo",sans-serif;font-weight:700;font-size:22px;display:block}
.meta .m span{font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:#A9C2B5}
.demo-tag{display:inline-block;margin-top:14px;font-family:"Space Mono",monospace;
  font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--felt);
  background:var(--brass);padding:3px 9px;border-radius:2px}

/* tickets */
.tickets{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0 8px}
.ticket{background:#fff;border:1px solid var(--rule);border-radius:3px;padding:15px 16px;position:relative;
  box-shadow:0 1px 0 rgba(0,0,0,.02)}
.ticket::before,.ticket::after{content:"";position:absolute;width:11px;height:11px;border-radius:50%;
  background:var(--paper);border:1px solid var(--rule);top:50%;transform:translateY(-50%)}
.ticket::before{left:-6px;border-right-color:var(--paper)}
.ticket::after{right:-6px;border-left-color:var(--paper)}
.ticket .lab{font-family:"Space Mono",monospace;font-size:10.5px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--muted)}
.ticket .who{font-family:"Archivo",sans-serif;font-weight:700;font-size:18px;margin:6px 0 2px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ticket .val{font-family:"Space Mono",monospace;font-weight:700;font-size:15px}
.val.up{color:var(--up)} .val.down{color:var(--down)}

/* chart */
.panel{background:#fff;border:1px solid var(--rule);border-radius:3px;margin-top:22px;overflow:hidden}
.panel .head{display:flex;justify-content:space-between;align-items:baseline;
  padding:16px 18px 0}
.panel h2{font-family:"Archivo",sans-serif;font-weight:700;font-size:16px;margin:0;
  letter-spacing:-.01em}
.panel .hint{font-size:11.5px;color:var(--muted)}
.chartbox{padding:8px 14px 16px;height:300px}

/* main grid */
.cols{display:grid;grid-template-columns:1fr 320px;gap:22px;margin-top:22px;align-items:start}

/* leaderboard */
table{width:100%;border-collapse:collapse}
thead th{font-family:"Space Mono",monospace;font-size:10.5px;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted);text-align:left;padding:0 10px 9px;font-weight:400;
  border-bottom:1px solid var(--ink)}
th.r,td.r{text-align:right}
tbody td{padding:10px;border-bottom:1px solid var(--rule);vertical-align:middle}
tbody tr:hover{background:#FBF9F2}
.rank{font-family:"Archivo",sans-serif;font-weight:700;color:var(--muted);width:34px}
tr.lead .rank{color:var(--brass)}
.name{font-weight:600}
tr.lead .name::after{content:"\2605";color:var(--brass);margin-left:7px;font-size:12px}
.budget{font-family:"Space Mono",monospace;font-weight:700;font-size:15px}
.delta{font-family:"Space Mono",monospace;font-size:12px;padding:2px 7px;border-radius:2px;background:var(--chip)}
.delta.up{color:var(--up)} .delta.down{color:var(--down)}
.toto{font-family:"Space Mono",monospace;font-size:12px;color:var(--muted)}
.toto b{color:var(--ink)}
.spark{display:block}
.me{box-shadow:inset 3px 0 0 var(--brass)}

/* side */
.side .panel{margin-top:0}
.side .panel + .panel{margin-top:16px}
.rrow{display:flex;justify-content:space-between;align-items:center;padding:8px 16px;
  border-bottom:1px solid var(--rule);font-size:13px}
.rrow.odp{cursor:pointer}
.rrow:last-child{border-bottom:0}
.rrow.odp:hover{background:#FBF9F2}
.rrow .sc{font-family:"Space Mono",monospace;font-weight:700}
.rrow .od{font-family:"Space Mono",monospace;font-size:11px;color:var(--muted)}
.t1{color:var(--up)} .t2{color:var(--down)} .tx{color:var(--brass)}
.note{font-size:12px;color:var(--muted);margin-top:22px;border-top:1px solid var(--rule);padding-top:14px}

/* odds-popover */
.odtip{position:fixed;z-index:60;background:#fff;border:1px solid var(--ink);border-radius:4px;
  box-shadow:0 10px 30px rgba(0,0,0,.20);padding:13px 15px;width:308px;max-width:calc(100vw - 24px);
  font-size:12px;display:none}
.odtip.show{display:block}
.odtip-h{font-family:"Archivo",sans-serif;font-weight:700;font-size:14px;margin-bottom:2px}
.odtip-sec{font-family:"Space Mono",monospace;font-size:9.5px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--muted);margin:11px 0 5px}
.odtip-toto{width:100%;border-collapse:collapse;font-family:"Space Mono",monospace}
.odtip-toto td{padding:3px 4px;border-bottom:1px solid var(--rule)}
.odtip-toto td.r{text-align:right}
.odtip-toto td.o{color:var(--muted)}
.odtip-toto td.p{font-weight:700}
.odtip-cs{border-collapse:collapse;font-family:"Space Mono",monospace;font-size:10px;width:100%}
.odtip-cs td,.odtip-cs th{border:1px solid var(--rule);padding:2px 0;text-align:center;font-weight:400}
.odtip-cs th{color:var(--muted);background:var(--chip);font-size:9px}
.odtip-cs td.diag{background:#FBF6E7}
.odtip-cap{font-size:9.5px;color:var(--muted);margin-top:5px;line-height:1.4}
@media(max-width:860px){
  .cols{grid-template-columns:1fr} .tickets{grid-template-columns:repeat(2,1fr)}
  .meta{text-align:left}
}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
.fade{opacity:0;transform:translateY(6px);animation:f .5s ease forwards}
@keyframes f{to{opacity:1;transform:none}}
</style>
</head>
<body>
<svg class="bg" aria-hidden="true"><defs>
<pattern id="ballpat" width="130" height="130" patternUnits="userSpaceOnUse" patternTransform="rotate(9)">
<g transform="translate(65,65)" fill="none" stroke="#1A1714" stroke-width="2" stroke-linecap="round">
<circle r="27"/>
<polygon points="0,-12 11.4,-3.7 7,9.7 -7,9.7 -11.4,-3.7"/>
<line x1="0" y1="-12" x2="0" y2="-27"/>
<line x1="11.4" y1="-3.7" x2="25.7" y2="-8.3"/>
<line x1="7" y1="9.7" x2="15.9" y2="21.8"/>
<line x1="-7" y1="9.7" x2="-15.9" y2="21.8"/>
<line x1="-11.4" y1="-3.7" x2="-25.7" y2="-8.3"/>
</g></pattern></defs>
<rect width="100%" height="100%" fill="url(#ballpat)"/></svg>
<div class="board">
  <svg class="pitch" viewBox="0 0 1200 320" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <g fill="none" stroke="rgba(242,238,223,0.18)" stroke-width="2">
      <line x1="600" y1="6" x2="600" y2="314"/>
      <circle cx="600" cy="160" r="76"/>
      <rect x="-2" y="64" width="150" height="192"/>
      <rect x="-2" y="116" width="60" height="88"/>
      <path d="M148 116 A 58 58 0 0 1 148 204"/>
      <rect x="1052" y="64" width="150" height="192"/>
      <rect x="1142" y="116" width="60" height="88"/>
      <path d="M1052 116 A 58 58 0 0 0 1052 204"/>
    </g>
    <circle cx="600" cy="160" r="3.5" fill="rgba(242,238,223,0.22)"/>
  </svg>
  <div class="board-in">
  <div class="brand">
    <div class="titlerow">
      <svg class="ball" viewBox="0 0 100 100" aria-hidden="true">
        <circle cx="50" cy="50" r="46" fill="none" stroke="#F2EEDF" stroke-width="3"/>
        <polygon points="50,35 64.3,45.4 58.8,62.1 41.2,62.1 35.7,45.4" fill="#F2EEDF"/>
        <g stroke="#F2EEDF" stroke-width="2.6" stroke-linecap="round">
          <line x1="50" y1="35" x2="50" y2="9"/>
          <line x1="64.3" y1="45.4" x2="89" y2="37"/>
          <line x1="58.8" y1="62.1" x2="74" y2="83"/>
          <line x1="41.2" y1="62.1" x2="26" y2="83"/>
          <line x1="35.7" y1="45.4" x2="11" y2="37"/>
        </g>
      </svg>
      <h1 id="title"></h1>
    </div>
    <div class="sub" id="subtitle"></div>
    <div class="demo-tag" id="demotag">voorbeeld &middot; uitslagen nog gesimuleerd</div>
  </div>
  <div class="meta" id="meta"></div>
</div></div>

<div class="wrap">
  <div class="intro">In dit overzicht zie je wat alle Breukelen poule deelnemers zouden hebben verdiend (of niet) als ze voor iedere groepswedstrijd een bedrag van 100 euro in hadden gezet op de toto-uitslag en 25 euro op de eindstand ten tijde van indiening van hun formulier. Opbrengsten zijn op basis van daadwerkelijk odds van online bookmakers. Er is uitgegaan van een startbudget van 2500 euro. <span class="nb">(NB gokken brengt aanzienlijke risico's met zich mee.)</span> &#128578;<span class="los">De stand op deze pagina staat volledig los van de door Ruud beheerde WK-poule. Slechts bedoeld om een indruk te krijgen van wie mogelijk zijn baan of uitkering op kan zeggen en een aardige zakcent bij kan verdienen met voetbalgokken.</span></div>
  <div class="upd">Wedstrijden worden dagelijks (geautomatiseerd) bijgewerkt - fingers crossed!</div>
  <div class="tickets" id="tickets"></div>

  <div class="panel">
    <div class="head"><h2>Budget over de tijd</h2><div class="chartbtns"><button id="bAll" class="cbtn on">Iedereen</button><button id="bTop" class="cbtn">Top 6</button></div></div>
    <div class="chartbox"><canvas id="chart"></canvas></div>
  </div>

  <div class="cols">
    <div class="panel" style="margin-top:0">
      <div class="head"><h2>Klassement</h2><span class="hint" id="clab"></span></div>
      <div style="padding:6px 8px 4px">
        <table>
          <thead><tr>
            <th class="rank">#</th><th>Naam</th><th>Verloop</th>
            <th class="r">Budget</th><th class="r">Laatste dag</th><th class="r">Toto correct</th>
          </tr></thead>
          <tbody id="rows"></tbody>
        </table>
      </div>
    </div>

    <div class="side">
      <div class="panel">
        <div class="head"><h2>Laatste uitslagen</h2><span class="hint" id="reslab"></span></div>
        <div id="results" style="padding:4px 0 6px"></div>
      </div>
      <div class="panel">
        <div class="head"><h2>Straks te spelen</h2><span class="hint">toto-odds</span></div>
        <div id="upcoming" style="padding:4px 0 6px"></div>
        <div class="odhint">De drie getallen zijn de odds voor winst, gelijkspel en verlies van de thuisploeg. Beweeg met de muis over een wedstrijd (of tik erop) voor alle odds en wat elke uitslag zou opleveren.</div>
      </div>
    </div>
  </div>

  <div class="note" id="note"></div>
</div>
<div id="odtip" class="odtip" role="tooltip"></div>

<script>
const DATA = __DATA__;
const eur = n => "€" + Math.round(n).toLocaleString("nl-NL");
const sgn = n => (n>=0?"+":"−") + "€" + Math.abs(Math.round(n)).toLocaleString("nl-NL");
const fmtOdd = o => (Number(o)>=10 ? Number(o).toFixed(1) : Number(o).toFixed(2));

document.getElementById("title").textContent = DATA.title;
document.getElementById("subtitle").textContent = DATA.subtitle;
document.getElementById("demotag").style.display = DATA.demo ? "inline-block":"none";
document.getElementById("meta").innerHTML =
  `<div class="m"><b>${DATA.n_participants}</b><span>deelnemers</span></div>`+
  `<div class="m"><b>${DATA.n_played}/${DATA.n_matches}</b><span>gespeeld</span></div>`+
  `<div class="m"><b>${DATA.last_matchday||"–"}</b><span>verwerkt t/m</span></div>`;
document.getElementById("clab").textContent = `alle ${DATA.n_participants} deelnemers`;
document.getElementById("reslab").textContent = DATA.last_matchday||"";

// tickets
const h = DATA.highlights;
document.getElementById("tickets").innerHTML = [
  ["Snelste stijger", h.riser.name, sgn(h.riser.delta), h.riser.delta>=0?"up":"down"],
  ["Snelste daler", h.faller.name, sgn(h.faller.delta), h.faller.delta>=0?"up":"down"],
  ["Langste toto goed", h.hot.name, h.hot.longest_correct+" op rij", "up"],
  ["Langste toto fout", h.cold.name, h.cold.longest_wrong+" op rij", "down"],
].map((t,i)=>`<div class="ticket fade" style="animation-delay:${i*60}ms">
  <div class="lab">${t[0]}</div><div class="who">${t[1]}</div>
  <div class="val ${t[3]}">${t[2]}</div></div>`).join("");

// sparkline
function spark(series){
  const w=92,hh=26,pad=3,min=Math.min(...series),max=Math.max(...series);
  const rng=(max-min)||1;
  const pts=series.map((v,i)=>[pad+i*(w-2*pad)/(series.length-1),
     hh-pad-(v-min)/rng*(hh-2*pad)]);
  const up=series[series.length-1]>=series[0];
  const base=DATA.start_budget;
  const by=hh-pad-(base-min)/rng*(hh-2*pad);
  const d=pts.map((p,i)=>(i?"L":"M")+p[0].toFixed(1)+" "+p[1].toFixed(1)).join(" ");
  return `<svg class="spark" width="${w}" height="${hh}" viewBox="0 0 ${w} ${hh}">
    <line x1="0" y1="${by.toFixed(1)}" x2="${w}" y2="${by.toFixed(1)}" stroke="#E3DDCD" stroke-dasharray="2 2"/>
    <path d="${d}" fill="none" stroke="${up?'#1F8A5B':'#C2402F'}" stroke-width="1.6"/></svg>`;
}

// leaderboard
document.getElementById("rows").innerHTML = DATA.participants.map(p=>{
  const du = p.delta_last_day>=0;
  return `<tr class="${p.rank===1?'lead':''}">
    <td class="rank">${p.rank}</td>
    <td class="name">${p.name}</td>
    <td>${spark(p.series)}</td>
    <td class="r budget">${eur(p.budget)}</td>
    <td class="r"><span class="delta ${du?'up':'down'}">${sgn(p.delta_last_day)}</span></td>
    <td class="r toto"><b>${p.toto_correct}</b>/${p.toto_played} &middot; ${p.hit_rate}%</td>
  </tr>`;
}).join("");

// ---- odds-popover -------------------------------------------------------
const STAKE_TOTO = 100, STAKE_SCORE = 25, CS_MAX = 5;
const tip = document.getElementById("odtip");
let tipRow = null;

function tipContent(title, od){
  const T = od.toto;
  let s = `<div class="odtip-h">${title}</div>`;
  s += `<div class="odtip-sec">Toto &middot; inzet &euro;${STAKE_TOTO}</div>`;
  s += `<table class="odtip-toto">`+
       [["1","thuis wint"],["X","gelijkspel"],["2","uit wint"]].map(([k,lab])=>
         `<tr><td>${k} &middot; ${lab}</td><td class="r o">${fmtOdd(T[k])}</td>`+
         `<td class="r p">${eur(T[k]*STAKE_TOTO)}</td></tr>`).join("")+`</table>`;
  if(od.cs){
    s += `<div class="odtip-sec">Exacte eindstand &middot; odds</div>`;
    s += `<table class="odtip-cs"><tr><th>th\\uit</th>`;
    for(let a=0;a<=CS_MAX;a++) s += `<th>${a}</th>`;
    s += `</tr>`;
    for(let hg=0;hg<=CS_MAX;hg++){
      s += `<tr><th>${hg}</th>`;
      for(let ag=0;ag<=CS_MAX;ag++){
        const o = od.cs[hg+"-"+ag];
        s += `<td class="${hg===ag?'diag':''}">${o?fmtOdd(o):"–"}</td>`;
      }
      s += `</tr>`;
    }
    s += `</table>`;
    s += `<div class="odtip-cap">Eindstand-odd &times; &euro;${STAKE_SCORE} inzet = uitbetaling. Bv. odd 7,0 &rarr; ${eur(7*STAKE_SCORE)}.</div>`;
  }
  return s;
}
function placeTip(row){
  const r = row.getBoundingClientRect();
  const tw = tip.offsetWidth, th = tip.offsetHeight;
  let left = r.left - tw - 10, top = r.top;
  if(left < 8){ left = Math.min(r.left, window.innerWidth - tw - 8); top = r.bottom + 8; }
  if(top + th > window.innerHeight - 8) top = Math.max(8, window.innerHeight - th - 8);
  tip.style.left = Math.max(8,left) + "px";
  tip.style.top = top + "px";
}
function showTip(row, title, od){
  tip.innerHTML = tipContent(title, od);
  tip.classList.add("show");
  placeTip(row);
  tipRow = row;
}
function hideTip(){ tip.classList.remove("show"); tipRow = null; }

function fillRows(id, items){
  const el = document.getElementById(id);
  el.innerHTML = items.length
    ? items.map(it=>`<div class="rrow odp">${it.left}${it.right}</div>`).join("")
    : `<div class="rrow"><span>nog geen uitslagen</span></div>`;
  [...el.querySelectorAll(".rrow.odp")].forEach((row,i)=>{
    const it = items[i];
    if(!it || !it.odds) return;
    row.addEventListener("mouseenter", ()=>showTip(row, it.title, it.odds));
    row.addEventListener("mouseleave", ()=>{ if(tipRow===row) hideTip(); });
    row.addEventListener("click", (e)=>{
      e.stopPropagation();
      if(tipRow===row) hideTip(); else showTip(row, it.title, it.odds);
    });
  });
}
document.addEventListener("click", ()=>hideTip());
window.addEventListener("resize", hideTip);
window.addEventListener("scroll", ()=>{ if(tipRow) placeTip(tipRow); }, true);

// results + upcoming
const resItems = DATA.results.slice().reverse()
  .filter(r=>r.datetime.split(" ").slice(0,2).join(" ")===DATA.last_matchday)
  .map(r=>({
    title:`${r.home} – ${r.away}`, odds:r.odds,
    left:`<span>${r.home} – ${r.away}</span>`,
    right:`<span class="sc t${r.toto.toLowerCase()==='x'?'x':r.toto}">${r.h}–${r.a}</span>`}));
fillRows("results", resItems);

const upItems = DATA.upcoming.map(u=>({
  title:`${u.home} – ${u.away}`, odds:u.odds,
  left:`<span>${u.home} – ${u.away}</span>`,
  right:`<span class="od">${fmtOdd(u.odds.toto["1"])} / ${fmtOdd(u.odds.toto["X"])} / ${fmtOdd(u.odds.toto["2"])}</span>`}));
fillRows("upcoming", upItems);

document.getElementById("note").innerHTML =
  (DATA.demo_note ? DATA.demo_note.charAt(0).toUpperCase()+DATA.demo_note.slice(1)+"." : "");

// chart
const palette=["#C8922A","#1F8A5B","#2C6FB0","#9B4DCA","#C2402F","#3B8C8C"];
const topN = DATA.participants.slice(0,6).map(p=>p.name);
const labels = ["start", ...DATA.played_labels];
let chart;
function startDS(){ return {label:"start", data:labels.map(()=>DATA.start_budget),
  borderColor:"#1A1714", borderWidth:1, borderDash:[4,4], pointRadius:0, order:0}; }
function baseOpts(anim){ return {responsive:true,maintainAspectRatio:false,
  interaction:{mode:"nearest",intersect:false}, animation: anim || {duration:650},
  plugins:{legend:{display:true,labels:{filter:i=>topN.includes(i.text)||i.text==="start",
    font:{family:"Public Sans",size:11},boxWidth:14,usePointStyle:true}},
    tooltip:{callbacks:{label:c=>c.dataset.label+": "+eur(c.parsed.y)}}},
  scales:{y:{ticks:{callback:v=>eur(v),font:{family:"Space Mono",size:10}},grid:{color:"#EEE9DB"}},
    x:{ticks:{maxTicksLimit:8,font:{family:"Space Mono",size:9},color:"#897F70"},grid:{display:false}}}}; }
function renderAll(){
  const ds = DATA.participants.map(p=>{ const t=topN.includes(p.name);
    return {label:p.name,data:p.series,borderColor:t?palette[topN.indexOf(p.name)]:"rgba(140,127,112,.16)",
      borderWidth:t?2.2:1,pointRadius:0,tension:.18,order:t?1:2}; });
  ds.push(startDS());
  if(chart) chart.destroy();
  chart=new Chart(document.getElementById("chart"),{type:"line",data:{labels,datasets:ds},options:baseOpts()});
}
function renderTop(){
  const np=labels.length, step=19000/np;
  const anim={
    x:{type:"number",easing:"linear",duration:step,from:NaN,
       delay(ctx){ if(ctx.type!=="data"||ctx.xStarted) return 0; ctx.xStarted=true; return ctx.index*step; }},
    y:{type:"number",easing:"linear",duration:step,
       from(ctx){ if(ctx.index===0) return ctx.chart.scales.y.getPixelForValue(DATA.start_budget);
         const prev=ctx.chart.getDatasetMeta(ctx.datasetIndex).data[ctx.index-1];
         return prev? prev.getProps(["y"],true).y : ctx.chart.scales.y.getPixelForValue(DATA.start_budget); },
       delay(ctx){ if(ctx.type!=="data"||ctx.yStarted) return 0; ctx.yStarted=true; return ctx.index*step; }}
  };
  const ds=DATA.participants.slice(0,6).map((p,i)=>({label:p.name,data:p.series,
    borderColor:palette[i],borderWidth:2.6,pointRadius:0,tension:.18}));
  ds.push(startDS());
  if(chart) chart.destroy();
  chart=new Chart(document.getElementById("chart"),{type:"line",data:{labels,datasets:ds},options:baseOpts(anim)});
}
function setBtn(id){ document.querySelectorAll(".cbtn").forEach(b=>b.classList.toggle("on",b.id===id)); }
document.getElementById("bAll").onclick=()=>{ setBtn("bAll"); renderAll(); };
document.getElementById("bTop").onclick=()=>{ setBtn("bTop"); renderTop(); };
renderAll();
</script>
</body>
</html>"""

open("index.html", "w").write(HTML.replace("__DATA__", DATA))
print("index.html geschreven,", len(HTML), "tekens template")
