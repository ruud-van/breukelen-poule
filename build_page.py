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
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js" integrity="sha384-bs/nf9FbdNouRbMiFcrcZfLXYPKiPaGVGplVbv7dLGECccEXDW+S3zjqSKR5ZEaD" crossorigin="anonymous"></script>
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
.legends{position:relative;z-index:2;max-width:1120px;margin:0 auto;padding:6px 20px 22px;
  display:flex;gap:16px;flex-wrap:wrap;justify-content:center}
.legends .lg{display:inline-block;width:84px;height:84px;border-radius:50%;overflow:hidden;
  border:2px solid #F2EEDF;background:#0d4427;box-shadow:0 2px 8px rgba(0,0,0,.28)}
.legends .lg img{width:100%;height:100%;object-fit:cover;object-position:50% 14%;
  transform:scale(1.28);transform-origin:50% 14%;display:block}
.legends .lg-bk img{transform:scale(1.12);transform-origin:50% 22%;object-position:50% 22%}
.legends-credit{position:relative;z-index:2;text-align:center;padding:0 20px 16px;
  font-size:10px;color:#A9C2B5}
.legends-credit a{color:#CFE0D5}

/* tickets */
.tickets{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:26px 0 8px}
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
.val.up{color:var(--up)} .val.down{color:var(--down)} .val.gold{color:var(--brass)}
.ticket .sub{font-size:11px;color:var(--muted);margin-top:3px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

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
.rank{font-family:"Archivo",sans-serif;font-weight:700;color:var(--muted);width:52px;white-space:nowrap}
.mv{font-family:"Space Mono",monospace;font-size:9.5px;font-weight:400;color:var(--muted);margin-left:3px}
.mv.up{color:var(--up)} .mv.down{color:var(--down)}
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
.motd{padding:10px 16px;font-size:12.5px;line-height:1.55;background:#FBF6E7;
  border-bottom:1px solid var(--rule);color:#3c372f}
.motd b{font-family:"Space Mono",monospace}
.motd-lab{display:block;font-family:"Space Mono",monospace;font-size:9.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--brass);margin-bottom:2px}
.t1{color:var(--up)} .t2{color:var(--down)} .tx{color:var(--brass)}
.note{font-size:12px;color:var(--muted);margin-top:22px;border-top:1px solid var(--rule);padding-top:14px}

/* link naar de spelregels-pagina */
.rules-link{margin-top:22px;padding:15px 18px;font-size:13.5px;line-height:1.6}
.rules-link a{color:#3c372f;text-decoration:none}
.rules-link a b{font-family:"Archivo",sans-serif;color:var(--felt)}
.rules-link a:hover b{text-decoration:underline}

/* tabs */
.tabs{display:flex;gap:8px;margin-top:22px}
.tab{font-family:"Archivo",sans-serif;font-weight:700;font-size:14px;border:1px solid var(--rule);
  background:#fff;color:var(--muted);padding:8px 16px;border-radius:3px;cursor:pointer}
.tab.on{background:var(--felt);color:#F2EEDF;border-color:var(--felt)}

/* voorspellingen-tab */
.pred-tools{display:flex;gap:8px;align-items:center;padding:12px 16px 6px;flex-wrap:wrap}
.pred-tools input{flex:1;min-width:160px;font-family:"Public Sans",sans-serif;font-size:13px;
  padding:7px 10px;border:1px solid var(--rule);border-radius:3px}
.pred-day{font-family:"Space Mono",monospace;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--felt);font-weight:700;margin:14px 16px 4px;border-bottom:1px solid var(--rule);padding-bottom:5px}
.pred-match{border-bottom:1px solid var(--rule)}
.pred-match summary{display:flex;align-items:center;gap:10px;padding:9px 16px;cursor:pointer;
  list-style:none;font-size:13px}
.pred-match summary::-webkit-details-marker{display:none}
.pred-match summary:hover{background:#FBF9F2}
.pred-time{font-family:"Space Mono",monospace;font-size:11px;color:var(--muted);flex:none;width:40px}
.pred-tm{font-weight:600}
.pred-res{font-family:"Space Mono",monospace;font-weight:700;background:var(--chip);padding:1px 7px;border-radius:2px}
.pred-meta{margin-left:auto;font-size:11px;color:var(--muted)}
.pred-body{padding:2px 16px 12px}
.pred-grp{display:grid;grid-template-columns:46px 84px 36px 1fr;align-items:center;gap:8px;padding:6px 0;
  border-top:1px dashed var(--rule);font-size:12.5px}
.pred-score{font-family:"Space Mono",monospace;font-weight:700}
.pred-bar{height:8px;background:var(--chip);border-radius:4px;overflow:hidden}
.pred-bar span{display:block;height:100%;background:var(--muted);border-radius:4px}
.pred-cnt{font-family:"Space Mono",monospace;font-size:11px;color:var(--muted)}
.pred-names{color:#3c372f;line-height:1.6}
.pred-grp.toto .pred-bar span{background:var(--up)}
.pred-grp.exact{background:#FBF6E7}
.pred-grp.exact .pred-bar span{background:var(--brass)}
.pred-grp.exact .pred-score{color:var(--brass)}
.pred-legend{font-size:11px;color:var(--muted);padding:8px 16px 0;line-height:1.5}
.pn{display:inline-block}
.pn.hit{background:var(--brass);color:#fff;border-radius:2px;padding:0 4px}
.pn.dim{opacity:.28}
@media(max-width:600px){
  .pred-grp{grid-template-columns:46px 1fr 36px;grid-auto-rows:auto}
  .pred-grp .pred-names{grid-column:1/-1}
}

/* gelijkenis-netwerk */
.sim-legend{display:flex;align-items:center;gap:10px;padding:10px 16px 0;font-size:11.5px;
  color:var(--muted);flex-wrap:wrap}
#simReadout{font-family:"Space Mono",monospace;color:var(--ink)}
.sim-wrap{padding:8px 12px 8px}
.simnet{width:100%;height:auto;display:block;touch-action:none}
.simnet line{stroke:#C9BFAB}
.simnet text{font-size:8.5px;fill:#3c372f;font-family:"Public Sans",sans-serif;
  text-anchor:middle;dominant-baseline:middle;cursor:pointer;paint-order:stroke;
  stroke:var(--paper);stroke-width:2.4px}
.simnet .nd:hover text{fill:var(--brass);font-weight:700;font-size:11px}
.sim-tops{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:6px 16px 16px}
.sim-top h3{font-family:"Archivo",sans-serif;font-size:13px;margin:0 0 6px}
.sim-top ol{margin:0;padding-left:20px;font-size:12.5px;line-height:1.8}
.sim-top li{color:#3c372f}
.sim-top .pct{font-family:"Space Mono",monospace;color:var(--muted);float:right}
@media(max-width:600px){.sim-tops{grid-template-columns:1fr}}

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
</div>
  <div class="legends">
    <span class="lg" title="Ruud van Nistelrooij"><img src="img/nistelrooy.jpg" alt="Ruud van Nistelrooij"></span>
    <span class="lg" title="Ruud Gullit"><img src="img/gullit.jpg" alt="Ruud Gullit"></span>
    <span class="lg" title="Ruud Geels"><img src="img/geels.jpg" alt="Ruud Geels"></span>
    <span class="lg" id="vmorr" title="Van Morrison"><img src="img/morrison.jpg" alt="Van Morrison"></span>
    <span class="lg lg-bk" title="Hans van Breukelen"><img src="img/breukelen.jpg" alt="Hans van Breukelen"></span>
  </div>
  <div class="legends-credit">Foto's: <a href="https://commons.wikimedia.org/" target="_blank" rel="noopener">Wikimedia Commons</a></div>
</div>

<div class="wrap">
  <div class="tabs">
    <button id="tabStand" class="tab on">Stand</button>
    <button id="tabPreds" class="tab">Voorspellingen</button>
    <button id="tabSim" class="tab">Gelijkenis</button>
  </div>
  <div id="view-stand">
  <div class="intro">In dit overzicht zie je wat alle Breukelen poule deelnemers zouden hebben verdiend (of niet) als ze voor iedere groepswedstrijd een bedrag van 100 euro in hadden gezet op de toto-uitslag en 20 euro op de eindstand ten tijde van indiening van hun formulier. Opbrengsten zijn op basis van daadwerkelijk odds van online bookmakers. Er is uitgegaan van een startbudget van 2000 euro. <span class="nb">(NB gokken brengt aanzienlijke risico's met zich mee.)</span> &#128578;<span class="los">De stand op deze pagina staat los van de stand in de Breukelen WK-poule (alle correspondentie daarover via email). Slechts bedoeld om een indruk te krijgen van wie mogelijk zijn baan of uitkering op kan zeggen en een aardige zakcent bij kan verdienen met voetbalgokken.</span></div>
  <div class="upd">Uitslagen worden automatisch opgehaald om 02:10, 05:10, 08:10, 15:10 en 23:10 (NL-tijd). De planner van GitHub loopt soms uit, dus het kan af en toe wat langer duren voor een uitslag verschijnt - fingers crossed!</div>
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
        <div id="motd" hidden class="motd"></div>
        <div id="results" style="padding:4px 0 6px"></div>
      </div>
      <div class="panel">
        <div class="head"><h2>Straks te spelen</h2><span class="hint">toto-odds</span></div>
        <div id="upcoming" style="padding:4px 0 6px"></div>
        <div class="odhint">De drie getallen zijn de odds voor winst, gelijkspel en verlies van de thuisploeg. Beweeg met de muis over een wedstrijd (of tik erop) voor alle odds en wat elke uitslag zou opleveren.</div>
      </div>
      <div class="panel">
        <div class="head"><h2>Gokken of op zeker</h2><span class="hint">mediaan eindstand-odd</span></div>
        <div class="sim-tops" style="grid-template-columns:1fr;gap:8px;padding-top:10px">
          <div class="sim-top"><h3>Grootste gokkers</h3><ol id="gokTop"></ol></div>
          <div class="sim-top"><h3>Meest op zeker</h3><ol id="zekerTop"></ol></div>
        </div>
        <div class="odhint">De mediaan van de eindstand-odds van alle 72 voorspelde uitslagen: hoog betekent vaak onwaarschijnlijke scores invullen, laag betekent dicht op de verwachting van de bookmakers zitten.</div>
      </div>
    </div>
  </div>

  <div class="panel rules-link">
    <a href="regels.html"><b>Nieuwe spelregels WK 2026</b> &mdash; snellere wissels, de 8-secondenregel voor keepers, meer VAR en meer. Lees alle wijzigingen &rarr;</a>
  </div>

  <div class="note" id="note"></div>
  </div><!-- /view-stand -->

  <div id="view-preds" hidden>
    <div class="panel" style="margin-top:18px">
      <div class="head"><h2>Voorspellingen per wedstrijd</h2><span class="hint" id="predcount"></span></div>
      <div class="pred-tools">
        <input id="predFilter" type="search" placeholder="Filter op naam…" autocomplete="off">
        <button id="predExpand" class="cbtn">Alles open</button>
        <button id="predCollapse" class="cbtn on">Alles dicht</button>
      </div>
      <div class="pred-legend">Per wedstrijd staan de voorspellingen gegroepeerd per uitslag (meest gekozen bovenaan). Bij gespeelde wedstrijden is de <b style="color:var(--brass)">exacte score</b> goudkleurig en een <b style="color:var(--up)">goede toto</b> groen.</div>
      <div id="preds"></div>
    </div>
  </div>

  <div id="view-sim" hidden>
    <div class="panel" style="margin-top:18px">
      <div class="head"><h2>Wie voorspelt als wie?</h2><div class="chartbtns">
        <button id="simToto" class="cbtn on">Toto</button>
        <button id="simScore" class="cbtn">Exacte score</button></div></div>
      <div class="sim-legend"><span id="simReadout">beweeg over een stip voor de naam</span></div>
      <div class="sim-wrap"><div id="simNet"></div></div>
      <div class="pred-legend">Elke stip is een deelnemer; wie dichter bij elkaar staat (en met een lijntje verbonden is) voorspelde meer hetzelfde. De plaatsing komt uit MDS op basis van overeenkomst. Wissel tussen <b>toto</b> (1/X/2) en <b>exacte score</b>; beweeg over een stip voor de naam.</div>
      <div class="sim-tops">
        <div class="sim-top"><h3>Meest op elkaar lijkend</h3><ol id="simMost"></ol></div>
        <div class="sim-top"><h3>Minst op elkaar lijkend</h3><ol id="simLeast"></ol></div>
      </div>
    </div>
  </div>
</div>
<div id="odtip" class="odtip" role="tooltip"></div>

<script>
const DATA = __DATA__;
const eur = n => "€" + Math.round(n).toLocaleString("nl-NL");
const sgn = n => (n>=0?"+":"−") + "€" + Math.abs(Math.round(n)).toLocaleString("nl-NL");
const fmtOdd = o => (Number(o)>=10 ? Number(o).toFixed(1) : Number(o).toFixed(2));
const esc = s => String(s).replace(/[&<>"']/g, c =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

document.getElementById("title").textContent = DATA.title;
document.getElementById("subtitle").textContent = DATA.subtitle;
document.getElementById("demotag").style.display = DATA.demo ? "inline-block":"none";
document.getElementById("meta").innerHTML =
  `<div class="m"><b>${DATA.n_participants}</b><span>deelnemers</span></div>`+
  `<div class="m"><b>${DATA.n_played}/${DATA.n_matches}</b><span>gespeeld</span></div>`+
  `<div class="m"><b>${DATA.last_update||DATA.last_matchday||"–"}</b><span>verwerkt t/m</span></div>`;
document.getElementById("clab").textContent = `alle ${DATA.n_participants} deelnemers`;
const nRes = Math.min(3, DATA.results.length);
document.getElementById("reslab").textContent =
  nRes ? (nRes===1 ? "laatste wedstrijd" : `laatste ${nRes} wedstrijden`) : "";

// tickets
const h = DATA.highlights;
const kl = h.klapper, ct = h.contrarian;
document.getElementById("tickets").innerHTML = [
  ["Snelste stijger vandaag", h.riser.name, sgn(h.riser.delta), h.riser.delta>=0?"up":"down", ""],
  ["Tegen de stroom in", ct?(ct.names[0]+(ct.count>1?" +"+(ct.count-1):"")):"–",
    ct?`${ct.count}/${DATA.n_participants} kozen ${ct.toto}`:"nog geen", ct?"gold":"",
    ct?esc(ct.match)+` (${ct.h}–${ct.a})`:"&nbsp;"],
  ["Grootste wedstrijdklapper", kl?(kl.name+(kl.extra?" +"+kl.extra:"")):"–",
    kl?sgn(kl.net):"nog geen", kl?"up":"",
    kl?"op "+esc(kl.match):"&nbsp;"],
  ["Langste toto goed", h.hot.name, h.hot.longest_correct+" op rij", "up", ""],
  ["Langste toto fout", h.cold.name, h.cold.longest_wrong+" op rij", "down", ""],
  ["Grootste gokker", h.gokker.name, "mediaan odd "+String(h.gokker.med).replace(".",","), "gold",
    "meest op zeker: "+esc(h.zeker.name)+" &middot; mediaan odd "+String(h.zeker.med).replace(".",",")],
].map((t,i)=>`<div class="ticket fade" style="animation-delay:${i*60}ms">
  <div class="lab">${t[0]}</div><div class="who">${esc(t[1])}</div>
  <div class="val ${t[3]}">${t[2]}</div>${t[4]?`<div class="sub">${t[4]}</div>`:""}</div>`).join("");

// sparkline
function spark(series){
  const w=92,hh=26,pad=3,min=Math.min(...series),max=Math.max(...series);
  const rng=(max-min)||1;
  const pts=series.map((v,i)=>[pad+i*(w-2*pad)/Math.max(series.length-1,1),
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
  const rd = p.rank_delta||0;
  const mv = rd>0?`<span class="mv up">&#9650;${rd}</span>`
           : rd<0?`<span class="mv down">&#9660;${-rd}</span>`
           : `<span class="mv">&middot;</span>`;
  return `<tr class="${p.rank===1?'lead':''}">
    <td class="rank">${p.rank}${mv}</td>
    <td class="name">${esc(p.name)}</td>
    <td>${spark(p.series)}</td>
    <td class="r budget">${eur(p.budget)}</td>
    <td class="r"><span class="delta ${du?'up':'down'}">${sgn(p.delta_last_day)}</span></td>
    <td class="r toto"><b>${p.toto_correct}</b>/${p.toto_played} &middot; ${p.hit_rate}%</td>
  </tr>`;
}).join("");

// ---- odds-popover -------------------------------------------------------
const STAKE_TOTO = 100, STAKE_SCORE = 20, CS_MAX = 5;
const tip = document.getElementById("odtip");
let tipRow = null;

function tipContent(title, od){
  const T = od.toto;
  let s = `<div class="odtip-h">${esc(title)}</div>`;
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

// wedstrijd van de dag
const md = DATA.match_of_day;
if(md){
  const verb = md.total < 0
    ? `kostte de poule samen <b>${eur(-md.total)}</b>`
    : `leverde de poule samen <b>${eur(md.total)}</b> op`;
  let who;
  if(!md.n_winners) who = "niemand verdiende eraan";
  else{
    const name = `${esc(md.top[0])} (${sgn(md.top[1])})`;
    const rest = md.n_winners - 1;
    who = rest===0 ? `alleen ${name} zag het aankomen`
        : `${name} en ${rest} ${rest===1?"andere deelnemer":"anderen"} verdienden eraan`;
  }
  const el = document.getElementById("motd");
  el.innerHTML = `<span class="motd-lab">Wedstrijd van de dag</span> `+
    `<b>${esc(md.home)} – ${esc(md.away)} ${md.h}–${md.a}</b> ${verb}; ${who}.`;
  el.hidden = false;
}

// results + upcoming
const resItems = DATA.results.slice(-3).reverse()
  .map(r=>({
    title:`${r.home} – ${r.away}`, odds:r.odds,
    left:`<span>${esc(r.home)} – ${esc(r.away)} <span class="od">${esc(r.datetime.split(" ").slice(0,2).join(" "))}</span></span>`,
    right:`<span class="sc t${r.toto.toLowerCase()==='x'?'x':r.toto}">${r.h}–${r.a}</span>`}));
fillRows("results", resItems);

const upItems = DATA.upcoming.map(u=>({
  title:`${u.home} – ${u.away}`, odds:u.odds,
  left:`<span>${esc(u.home)} – ${esc(u.away)}</span>`,
  right:`<span class="od">${fmtOdd(u.odds.toto["1"])} / ${fmtOdd(u.odds.toto["X"])} / ${fmtOdd(u.odds.toto["2"])}</span>`}));
fillRows("upcoming", upItems);

// gokken-of-op-zeker top 5
const fillBold = (id, arr)=>{ document.getElementById(id).innerHTML =
  arr.map(([n,v])=>`<li>${esc(n)}<span class="pct">${String(v).replace(".",",")}</span></li>`).join(""); };
fillBold("gokTop", DATA.boldness.gok);
fillBold("zekerTop", DATA.boldness.zeker);

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
  // Progressief "tekenen" van links naar rechts, maar met een vaste per-punt-stap
  // en een korte totale duur, zodat het ook bij weinig speelrondes snel en
  // betrouwbaar rendert (de oude 19000/np-stap maakte de grafiek seconden leeg).
  const step=Math.min(260, 1400/Math.max(labels.length-1,1));
  const anim={
    x:{type:"number",easing:"linear",duration:step,
       from(ctx){ if(ctx.index===0) return ctx.chart.scales.x.getPixelForValue(0);
         const prev=ctx.chart.getDatasetMeta(ctx.datasetIndex).data[ctx.index-1];
         return prev? prev.getProps(["x"],true).x : ctx.chart.scales.x.getPixelForValue(0); },
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
function setBtn(id){ document.querySelectorAll("#bAll,#bTop").forEach(b=>b.classList.toggle("on",b.id===id)); }
document.getElementById("bAll").onclick=()=>{ setBtn("bAll"); renderAll(); };
document.getElementById("bTop").onclick=()=>{ setBtn("bTop"); renderTop(); };
renderAll();

// ---- voorspellingen-tab -------------------------------------------------
function totoOf(hh,aa){ return hh>aa?"1":(aa>hh?"2":"X"); }
function renderPreds(){
  const box = document.getElementById("preds");
  const P = DATA.predictions || [];
  let html = "", curday = null;
  P.forEach(m=>{
    const day = m.datetime.split(" ").slice(0,2).join(" ");
    if(day !== curday){ curday = day; html += `<div class="pred-day">${day}</div>`; }
    const g = {};
    m.preds.forEach(p=>{ const k = p.h+"-"+p.a; (g[k] = g[k] || []).push(p.n); });
    const groups = Object.entries(g).map(([k,ns])=>{
      const [hh,aa] = k.split("-").map(Number);
      return {hh, aa, ns, n:ns.length, tt:totoOf(hh,aa)};
    }).sort((a,b)=> b.n-a.n || a.hh-b.hh || a.aa-b.aa);
    const maxn = groups.length ? groups[0].n : 1;
    let body = "";
    groups.forEach(gr=>{
      let cls = "pred-grp";
      if(m.played){
        if(gr.hh===m.h && gr.aa===m.a) cls += " exact";
        else if(gr.tt===m.toto) cls += " toto";
      }
      const names = gr.ns.slice().sort((a,b)=>a.localeCompare(b,"nl"))
        .map(n=>`<span class="pn" data-n="${esc(n.toLowerCase())}">${esc(n)}</span>`).join(", ");
      body += `<div class="${cls}"><div class="pred-score">${gr.hh}–${gr.aa}</div>`+
        `<div class="pred-bar"><span style="width:${Math.round(100*gr.n/maxn)}%"></span></div>`+
        `<div class="pred-cnt">${gr.n}×</div><div class="pred-names">${names}</div></div>`;
    });
    const res = m.played ? `<span class="pred-res">${m.h}–${m.a}</span>` : "";
    const tijd = m.datetime.split(" ")[2] || "";
    html += `<details class="pred-match"><summary><span class="pred-time">${tijd}</span>`+
      `<span class="pred-tm">${esc(m.home)} – ${esc(m.away)}</span>`+
      `${res}<span class="pred-meta">${groups.length} verschillende</span></summary>`+
      `<div class="pred-body">${body}</div></details>`;
  });
  box.innerHTML = html;
  document.getElementById("predcount").textContent =
    `${P.length} wedstrijden · ${DATA.n_participants} deelnemers`;
}
const predFilter = document.getElementById("predFilter");
predFilter.addEventListener("input", ()=>{
  const q = predFilter.value.trim().toLowerCase();
  document.querySelectorAll("#preds .pn").forEach(s=>{
    const hit = q && s.dataset.n.includes(q);
    s.classList.toggle("hit", !!hit);
    s.classList.toggle("dim", !!q && !hit);
  });
});
document.getElementById("predExpand").onclick = ()=>
  document.querySelectorAll(".pred-match").forEach(d=>d.open = true);
document.getElementById("predCollapse").onclick = ()=>
  document.querySelectorAll(".pred-match").forEach(d=>d.open = false);

// ---- gelijkenis-netwerk -------------------------------------------------
let simMode = "toto";
function renderSim(){
  const S = DATA.similarity && DATA.similarity[simMode];
  const net = document.getElementById("simNet");
  if(!S){ net.innerHTML = "<p style='padding:12px;color:#897F70'>Geen gelijkenis-data.</p>"; return; }
  const names = S.names, nodes = S.nodes, edges = S.edges || [];
  const W = 900, H = 680, pad = 60;
  const X = v => (pad + v*(W-2*pad)), Y = v => (pad + v*(H-2*pad));
  const P = nodes.map(p=>[X(p[0]), Y(p[1])]);
  // declutter: duw overlappende namen uit elkaar (behoudt globale structuur)
  const minD = 36;
  for(let it=0; it<140; it++){
    for(let i=0;i<P.length;i++) for(let j=i+1;j<P.length;j++){
      let dx=P[j][0]-P[i][0], dy=P[j][1]-P[i][1];
      const d=Math.hypot(dx,dy)||0.01;
      if(d<minD){ const k=(minD-d)/2/d; dx*=k; dy*=k;
        P[i][0]-=dx; P[i][1]-=dy; P[j][0]+=dx; P[j][1]+=dy; }
    }
  }
  for(const p of P){ p[0]=Math.max(pad,Math.min(W-pad,p[0])); p[1]=Math.max(pad,Math.min(H-pad,p[1])); }
  const lines = edges.map(([a,b,w])=>{
    const sw = (0.4 + (w||0)/100 * 3.6).toFixed(2);   // 0% -> dun, 100% -> dik
    return `<line x1="${P[a][0].toFixed(1)}" y1="${P[a][1].toFixed(1)}" `+
      `x2="${P[b][0].toFixed(1)}" y2="${P[b][1].toFixed(1)}" `+
      `stroke-width="${sw}"><title>${esc(names[a])} ↔ ${esc(names[b])}: ${w}%</title></line>`;
  }).join("");
  const pts = P.map((c,i)=>
    `<g class="nd" data-i="${i}"><text x="${c[0].toFixed(1)}" y="${c[1].toFixed(1)}">${esc(names[i])}`+
    `<title>${esc(names[i])}</title></text></g>`).join("");
  net.innerHTML = `<svg viewBox="0 0 ${W} ${H}" class="simnet" preserveAspectRatio="xMidYMid meet" `+
    `role="img" aria-label="gelijkenis-netwerk">${lines}${pts}</svg>`;
  const ro = document.getElementById("simReadout");
  net.querySelector("svg").addEventListener("pointermove", e=>{
    const g = e.target.closest(".nd"); if(!g) return;
    ro.textContent = names[+g.dataset.i];
  });
  const fill = (id, arr)=>{ document.getElementById(id).innerHTML =
    arr.map(([a,b,p])=>`<li>${esc(a)} &amp; ${esc(b)}<span class="pct">${p}%</span></li>`).join(""); };
  fill("simMost", S.most || []);
  fill("simLeast", S.least || []);
}
function setSim(mode){
  simMode = mode;
  document.getElementById("simToto").classList.toggle("on", mode==="toto");
  document.getElementById("simScore").classList.toggle("on", mode==="score");
  renderSim();
}
document.getElementById("simToto").onclick = ()=>setSim("toto");
document.getElementById("simScore").onclick = ()=>setSim("score");

let predsRendered = false, simRendered = false;
function showView(v){
  document.getElementById("view-stand").hidden = v !== "stand";
  document.getElementById("view-preds").hidden = v !== "preds";
  document.getElementById("view-sim").hidden = v !== "sim";
  document.getElementById("tabStand").classList.toggle("on", v==="stand");
  document.getElementById("tabPreds").classList.toggle("on", v==="preds");
  document.getElementById("tabSim").classList.toggle("on", v==="sim");
  if(v==="preds" && !predsRendered){ renderPreds(); predsRendered = true; }
  if(v==="sim" && !simRendered){ renderSim(); simRendered = true; }
}
// klik op Van Morrison: start de update-workflow handmatig (workflow_dispatch).
// Het token wordt alleen lokaal in deze browser bewaard, nooit in de pagina.
const vmorr = document.getElementById("vmorr");
vmorr.style.cursor = "pointer";
function vmFlash(color){
  vmorr.style.boxShadow = "0 0 0 4px " + color;
  setTimeout(()=>{ vmorr.style.boxShadow = ""; }, 1600);
}
vmorr.addEventListener("click", async ()=>{
  let tok = localStorage.getItem("gh_dispatch_token");
  if(!tok){
    tok = prompt("GitHub-token met Actions-write op deze repo (wordt alleen in deze browser bewaard):");
    if(!tok) return;
    tok = tok.trim();
    localStorage.setItem("gh_dispatch_token", tok);
  }
  try{
    const r = await fetch("https://api.github.com/repos/ruud-van/breukelen-poule/actions/workflows/update-pool.yml/dispatches", {
      method: "POST",
      headers: {"Authorization": "Bearer " + tok, "Accept": "application/vnd.github+json"},
      body: JSON.stringify({ref: "main"})
    });
    if(r.status === 204){ vmFlash("#C8922A"); }
    else{
      if(r.status === 401 || r.status === 403) localStorage.removeItem("gh_dispatch_token");
      vmFlash("#C2402F");
    }
  }catch(e){ vmFlash("#C2402F"); }
});

document.getElementById("tabStand").onclick = ()=>showView("stand");
document.getElementById("tabPreds").onclick = ()=>showView("preds");
document.getElementById("tabSim").onclick = ()=>showView("sim");
</script>
</body>
</html>"""

REGELS = r"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nieuwe spelregels WK 2026 &middot; Breukelen-bookmaker poule</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:wght@400;500;600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{
  --felt:#1E8049; --paper:#F7F4ED; --ink:#1A1714; --brass:#C8922A;
  --rule:#E3DDCD; --muted:#897F70;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--paper);color:var(--ink);
  font-family:"Public Sans",system-ui,sans-serif;line-height:1.5;
  -webkit-font-smoothing:antialiased}
.board{background:var(--felt);color:#F2EEDF}
.board-in{max-width:880px;margin:0 auto;padding:30px 20px 26px}
.board h1{font-family:"Archivo",sans-serif;font-weight:900;font-size:clamp(24px,4vw,40px);
  letter-spacing:-.02em;line-height:1;margin:0}
.board .sub{font-family:"Space Mono",monospace;text-transform:uppercase;
  letter-spacing:.28em;font-size:11px;color:var(--brass);margin-top:10px}
.wrap{max-width:880px;margin:0 auto;padding:0 20px 64px}
.back{margin:18px 0 0;font-size:13px}
.back a{color:var(--felt);font-weight:600;text-decoration:none}
.back a:hover{text-decoration:underline}
.panel{background:#fff;border:1px solid var(--rule);border-radius:3px;margin-top:18px}
.rules-body{padding:6px 18px 18px}
.rules-intro{font-size:13.5px;color:#3c372f;margin:12px 0;line-height:1.6}
.rules-cat{font-family:"Space Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--felt);font-weight:700;margin:16px 0 8px}
.rules-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.rule{border:1px solid var(--rule);border-radius:3px;padding:12px 14px;font-size:12.5px;
  line-height:1.55;color:#3c372f;background:#FBF9F2}
.rule-h{font-family:"Archivo",sans-serif;font-weight:700;font-size:13.5px;margin-bottom:4px;color:var(--ink)}
.rules-src{font-size:12px;margin-top:14px}
.rules-src a{color:var(--felt);font-weight:600;text-decoration:none}
.rules-src a:hover{text-decoration:underline}
@media(max-width:680px){.rules-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="board"><div class="board-in">
  <h1>Nieuwe spelregels WK 2026</h1>
  <div class="sub">FIFA / IFAB &middot; toernooirichtlijnen</div>
</div></div>
<div class="wrap">
  <p class="back"><a href="index.html">&larr; Terug naar de poule</a></p>
  <div class="panel">
    <div class="rules-body">
      <p class="rules-intro">Voor dit WK voeren FIFA en spelregelcommissie IFAB een reeks wijzigingen door, met de focus op meer effectieve speeltijd, het hard aanpakken van tijdrekken en meer sportiviteit. De belangrijkste:</p>

      <div class="rules-cat">1 &middot; Harde aanpak van tijdrekken</div>
      <div class="rules-grid">
        <div class="rule"><div class="rule-h">Snellere wissels (10 sec)</div>Een gewisselde speler moet binnen 10 seconden via de kortste route van het veld. Lukt dat niet, dan mag de invaller pas bij het eerstvolgende dode spelmoment én na minimaal één minuut het veld in &mdash; tot die tijd speelt het team met 10 man.</div>
        <div class="rule"><div class="rule-h">Doeltrap &amp; inworp (5 sec)</div>Vindt de scheidsrechter dat een doeltrap of inworp te lang duurt, dan telt hij van 5 af. Te laat? Een te lange inworp gaat naar de tegenstander; een te lange doeltrap levert de tegenstander een hoekschop op.</div>
        <div class="rule"><div class="rule-h">Keeper: 8-secondenregel</div>De keeper mag de bal nog max. 8 seconden vasthouden (laatste 5 worden afgeteld). Te lang? Hoekschop voor de tegenstander (was: indirecte vrije trap na 6 sec).</div>
        <div class="rule"><div class="rule-h">Minuut eruit na blessure</div>Een op het veld medisch verzorgde speler moet daarna verplicht één minuut buiten de lijnen wachten &mdash; tenzij de tegenstander voor de overtreding een kaart kreeg.</div>
      </div>

      <div class="rules-cat">2 &middot; Gedrag en communicatie</div>
      <div class="rules-grid">
        <div class="rule"><div class="rule-h">Mond afschermen &rarr; rood</div>Wie tijdens een confrontatie zijn mond bedekt (hand of shirt) om liplezen te voorkomen, riskeert een directe rode kaart. Bedoeld om verborgen beledigingen en racisme tegen te gaan.</div>
        <div class="rule"><div class="rule-h">Alleen de aanvoerder spreekt</div>Alleen de aanvoerder mag bij een dispuut de scheidsrechter benaderen. Andere spelers die verhaal komen halen, krijgen direct geel.</div>
        <div class="rule"><div class="rule-h">Veld verlaten uit protest &rarr; rood</div>Teams die uit protest demonstratief het veld verlaten (of stafleden die daartoe aanzetten) worden bestraft met rode kaarten.</div>
      </div>

      <div class="rules-cat">3 &middot; VAR en technologie</div>
      <div class="rules-grid">
        <div class="rule"><div class="rule-h">VAR krijgt meer bevoegdheden</div>De VAR mag nu ingrijpen bij een onterechte tweede gele kaart (en dus rood), bij een kaart aan de verkeerde speler/ploeg, bij een overduidelijk onterechte hoekschop, en bij een aanvallende overtreding vlak vóór een doelpunt.</div>
        <div class="rule"><div class="rule-h">Semi-automatisch buitenspel</div>Staat een speler meer dan 10 cm buitenspel, dan krijgt de grensrechter direct een audiosignaal in zijn oortje &mdash; voor snellere beslissingen bij uitbraken.</div>
        <div class="rule"><div class="rule-h">Bodycams &amp; omgeroepen VAR</div>Bodycams op de scheidsrechter zijn toegestaan, en VAR-beslissingen worden in het stadion omgeroepen.</div>
      </div>

      <div class="rules-cat">4 &middot; Spel en toernooi</div>
      <div class="rules-grid">
        <div class="rule"><div class="rule-h">Vaste drinkpauze</div>In beide helften is er een vaste pauze van circa 3 minuten voor een adempauze, ongeacht de weersomstandigheden.</div>
        <div class="rule"><div class="rule-h">Geel kwijtgescholden na groepsfase</div>Gele kaarten worden ook na de groepsfase gewist (niet pas na de kwartfinales), zodat minder spelers schorsingen oplopen voor belangrijke duels.</div>
        <div class="rule"><div class="rule-h">Geen geel na voordeel-doelpunt</div>Maakt een speler een normaal geel-waardige overtreding, maar geeft de scheidsrechter voordeel en valt daaruit direct een doelpunt, dan vervalt de gele kaart.</div>
      </div>

      <p class="rules-src">Bronnen: <a href="https://www.theifab.com/laws/" target="_blank" rel="noopener">IFAB &ndash; Laws of the Game 2025/26</a> &middot; <a href="https://inside.fifa.com/news/offside-decisions-referee-body-cams-innovation-world-cup-2026" target="_blank" rel="noopener">FIFA &ndash; vernieuwingen WK 2026</a> &middot; <a href="https://nos.nl/artikel/2612342-nieuwe-regel-op-wk-spelers-die-mond-bedekken-tijdens-confrontaties-kunnen-rood-krijgen" target="_blank" rel="noopener">NOS</a></p>
    </div>
  </div>
  <p class="back"><a href="index.html">&larr; Terug naar de poule</a></p>
</div>
</body>
</html>"""

open("index.html", "w").write(HTML.replace("__DATA__", DATA))
open("regels.html", "w").write(REGELS)
print("index.html geschreven,", len(HTML), "tekens template")
print("regels.html geschreven,", len(REGELS), "tekens")
