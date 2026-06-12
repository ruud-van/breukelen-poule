# Handoff — Breukelen-bookmaker poule (WK 2026)

_Laatst bijgewerkt: 12 juni 2026 (avond). Lees dit op de andere laptop om verder te gaan._

## 1. Wat is het
Webpagina voor een vriendenpoule (58 deelnemers, WK 2026 groepsfase): fictieve gok-stand
op **echte bookmaker-odds**. Per groepswedstrijd zet iedereen €100 op de toto (1X2) en €20
op de exacte eindstand; startbudget €2000. Los van de officiële poule van Ruud.

- **Live (deel deze)**: https://ruud-van.github.io/breukelen-poule/
- **Repo**: https://github.com/ruud-van/breukelen-poule (org `ruud-van`, branch `main`)
- Oude URL `chrissnijders.github.io/breukelen-poule` blijft via redirect werken.

## 2. Opzetten op de nieuwe laptop
```bash
git clone https://github.com/ruud-van/breukelen-poule.git
cd breukelen-poule
python3 -m venv .venv
.venv/bin/pip install xlrd numpy scipy
```
Auth voor pushen: bij `git push` vraagt GitHub om een **Personal Access Token** (classic) met
scopes **`repo`** + **`workflow`** als wachtwoord (niet je GitHub-wachtwoord). Username = je GitHub-login.
macOS: geef **Terminal** Volledige-schijftoegang als de map op het Bureaublad staat
(Systeeminstellingen → Privacy → Volledige schijftoegang), anders "Operation not permitted".

## 3. Bouwen / draaien (lokaal)
```bash
.venv/bin/python results_fetch.py    # haalt gespeelde uitslagen op (ESPN) -> results_state.json
.venv/bin/python build_pool.py       # leest Excel + wk_odds.json + results_state.json -> odds.json + data.json
.venv/bin/python build_page.py       # giet data.json in index.html
git checkout odds.json               # gooi de (niet-te-committen) odds.json-diff weg, zie sectie 4
open index.html                      # lokaal bekijken
```
Let op: `build_pool.py` gebruikt `datetime.timezone.utc` en draait dus ook op Python 3.9
(de Action draait 3.12). Verifieer JS na een template-wijziging:
`node --check <(sed -n '/<script>/,/<\/script>/p' index.html | sed '1d;$d')`

## 4. Pipeline & bestanden
- `results_fetch.py` — **ESPN** scoreboard (sleutelloos, near-realtime; dezelfde feed als ESPN.com). Endpoint `site.api.espn.com/.../soccer/fifa.world/scoreboard?dates=20260611-20260703`. Filtert op `season.slug=="group-stage"` + `status.type.completed`, leest `competitors[].homeAway`/`score`. Koppelt teamnamen via `to_nl` uit `odds_fetch.py`. Schrijft naast de uitslagen ook `"_updated_at"` = NL-tijdstip (UTC+2, hele WK is zomertijd) van verwerking, in formaat `"11 juni 23:51"`; dat tijdstempel ververst **alleen bij een gewijzigde uitslag** (anders zou de bot elke cron-run committen). **Guardrail (12 juni):** geeft de feed mínder uitslagen dan de vorige run (lege/kapotte feed), dan stopt het script hard en blijft `results_state.json` ongemoeid. _(Overstap van openfootball gemaakt 11 juni: openfootball werd handmatig ~1×/dag bijgewerkt → uren vertraging. Geen fallback ingebouwd.)_
- `build_pool.py` — productie-build. Constantes bovenaan: `START=2000`, `STAKE_TOTO=100`, `STAKE_SCORE=20`. Schrijft `data.json` met: `participants` (incl. `rank_delta` = positieverschuiving t.o.v. vóór de laatste speeldag, competition-ranking), `results`, `upcoming` (incl. per-match `odds`), `predictions` (58×72), `similarity` (MDS-netwerk `nodes`/`edges[a,b,pct]` + `most`/`least` top-5, voor toto én score), `highlights` (riser, contrarian, hot, cold, klapper incl. ex-aequo-telling, gokker/zeker op **mediaan** eindstand-odd), `boldness` (top-5 gokkers + top-5 op zeker), `match_of_day` (grootste geldverschuiving van de laatste speeldag), `last_update` (uit `_updated_at`). **Guardrails (12 juni):** ontbrekende voorspelling of incomplete 1X2-odds stoppen de build hard (geen stille 0-0-inzet meer).
- `build_page.py` — bevat de HTML/CSS/JS template en schrijft **twee** pagina's: `index.html` én `regels.html` (standalone spelregels-pagina; op de hoofdpagina staat alleen nog een link-paneel). 3 tabs: **Stand** (6 tickets, budget-grafiek, klassement met ▲/▼-pijltjes, 'Wedstrijd van de dag', laatste 3 uitslagen, komende wedstrijden met dag+tijd, gokken-of-op-zeker-paneel), **Voorspellingen** (accordeon per wedstrijd mét aanvangstijd, naam-filter, exacte score goud / goede toto groen), **Gelijkenis** (netwerk met namen, lijndikte ∝ overeenkomst, declutter, top-5 lijsten, toggle toto/score). Header heeft 5 spelersfoto's (`img/`) en `verwerkt t/m` = `DATA.last_update` (NL-tijd op de minuut), met `last_matchday` als fallback. Alle namen/teams gaan door een `esc()`-helper (XSS-hardening); Chart.js-CDN-tag heeft een SRI-hash; `padTime()` vult schema-tijden als `3:00` aan tot `03:00` (twee regels in het Excel waren niet opgevuld). **Van Morrison-portret is klikbaar**: triggert `workflow_dispatch` via de GitHub API; vraagt eenmalig een fine-grained token (Actions: write op deze repo) dat alleen in localStorage staat; gouden gloed = gelukt, rood = mislukt (token wordt dan gewist bij 401/403).
- `odds.json` — bevroren echte odds. **Let op:** `build_pool.py` herschrijft dit bestand wel bij elke build (nieuwe `frozen_at` + minieme afrondingsruis), maar de workflow commit het **nooit**. Lokaal dus na een build `git checkout odds.json` om de diff weg te gooien.
- `WK_2026__allen_.xls` — master met deelnemers + voorspellingen incl. aftraptijden (kolom 1, NL-tijd); repo-relatief, meegecommit.
- `img/` — 5 Wikimedia Commons-portretten: Nistelrooij, Gullit, Geels, **Van Morrison**, Breukelen. _(Krol vervangen door Van Morrison op 11 juni; volgorde in `build_page.py`.)_
- `.github/workflows/update-pool.yml` — cron `10 0,3,6,13,21 * * *` UTC = 02:10/05:10/08:10/15:10/23:10 NL (tien over, zodat een net afgelopen duel zeker verwerkt is; GitHubs planner loopt soms minuten tot een kwartier uit); Python 3.12. Draait fetch→build→build, commit alleen `data.json index.html regels.html results_state.json` bij wijziging. Handmatig te starten via `workflow_dispatch` (de "Run workflow"-knop, of de Van Morrison-klik op de pagina).
- `.gitignore` — negeert o.a. `.venv/`, `__pycache__/`, `.claude/` (lokale Claude Code-config + preview `launch.json`).

## 5. Open punten / TODO
1. ~~GitHub Pages op de org aan?~~ ✅ Werkt (pagina deployt na elke bot-commit; reken op 1-2 min vertraging + browsercache, hard refresh helpt).
2. ~~Workflow permissions~~ / ~~push-pad bot testen~~ ✅ Bewezen op 12 juni: de bot pusht zelf, zowel via cron als via `workflow_dispatch` (Van Morrison-klik om 23:12 verwerkte Canada-Bosnië 1-1).
3. **Action Node-20 warning** (onschuldig, deprecation sept-2026). Optioneel: bump `actions/checkout@v4→v5` en `actions/setup-python@v5→v6` in de workflow.
4. Eventueel: cron-tijden fijnstellen op de exacte speeldagen.
5. **ESPN is een ongedocumenteerde API** (geen SLA). Werkt al jaren stabiel, maar als de structuur ooit wijzigt valt `results_fetch.py` stil (de nieuwe guardrail voorkomt dat een lege feed de stand wist). Mogelijke verbetering: openfootball als fallback terugzetten. Teamnaam-aliassen staan in `FEED_ALIASES` (`odds_fetch.py`); ESPN gebruikt o.a. `Czechia`, `South Korea`, `Bosnia-Herzegovina`, `United States`.
6. **SRI-hash Chart.js**: serveert cdnjs ooit andere bytes voor dezelfde URL, dan laadt de grafiek stil niet meer (dat is de bedoeling van SRI). Alternatief: het bestand (~200 KB) zelf in de repo zetten.
7. **Van Morrison-token zit per browser** in localStorage; op een ander apparaat moet het token opnieuw ingevoerd worden. Bij rode gloed terwijl de run wél verschijnt: cache/dubbele klik, anders token opnieuw aanmaken (fine-grained, alleen Actions: write op deze repo).

## 6. Werkwijze-notities (handig)
- Er draait een **GateGuard-hook** die vóór elke Bash/Edit/Write om "facts" vraagt. Gewoon kort de 4 punten benoemen en de actie herhalen. (Uit te zetten met env `ECC_GATEGUARD=off` indien gewenst.)
- Bij een push-conflict doordat de **bot** op de remote committe: `git pull --rebase` of (solo, bot-output is regenereerbaar) `git push --force`.
- `data.json` is ~280 KB door de voorspellingen; dat is prima voor een statische pagina.
