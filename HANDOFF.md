# Handoff — Breukelen-bookmaker poule (WK 2026)

_Laatst bijgewerkt: 11 juni 2026 (avond). Lees dit op de andere laptop om verder te gaan._

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
- `results_fetch.py` — **ESPN** scoreboard (sleutelloos, near-realtime; dezelfde feed als ESPN.com). Endpoint `site.api.espn.com/.../soccer/fifa.world/scoreboard?dates=20260611-20260703`. Filtert op `season.slug=="group-stage"` + `status.type.completed`, leest `competitors[].homeAway`/`score`. Koppelt teamnamen via `to_nl` uit `odds_fetch.py`. Schrijft naast de uitslagen ook `"_updated_at"` = NL-tijdstip (UTC+2, hele WK is zomertijd) van verwerking, in formaat `"11 juni 23:51"`; dat tijdstempel ververst **alleen bij een gewijzigde uitslag** (anders zou de bot elke cron-run committen). _(Overstap van openfootball gemaakt 11 juni: openfootball werd handmatig ~1×/dag bijgewerkt → uren vertraging. Geen fallback ingebouwd.)_
- `build_pool.py` — productie-build. Constantes bovenaan: `START=2000`, `STAKE_TOTO=100`, `STAKE_SCORE=20`. Schrijft `data.json` met: `participants`, `results`, `upcoming` (incl. per-match `odds`), `predictions` (58×72), `similarity` (MDS-netwerk `nodes`/`edges[a,b,pct]` + `most`/`least` top-5, voor toto én score), `last_update` (uit `_updated_at`). Leest `_updated_at` uit de state maar negeert die bij het matchen (key matcht geen `home|away`).
- `build_page.py` — bevat de HTML/CSS/JS template. 3 tabs: **Stand**, **Voorspellingen** (accordeon per wedstrijd, naam-filter, exacte score goud / goede toto groen), **Gelijkenis** (netwerk met namen, lijndikte ∝ overeenkomst, declutter, top-5 lijsten, toggle toto/score). Header heeft 5 spelersfoto's (`img/`) en `verwerkt t/m` = `DATA.last_update` (NL-tijd op de minuut), met `last_matchday` als fallback.
- `odds.json` — bevroren echte odds. **Let op:** `build_pool.py` herschrijft dit bestand wel bij elke build (nieuwe `frozen_at` + minieme afrondingsruis), maar de workflow commit het **nooit**. Lokaal dus na een build `git checkout odds.json` om de diff weg te gooien.
- `WK_2026__allen_.xls` — master met deelnemers + voorspellingen incl. aftraptijden (kolom 1, NL-tijd); repo-relatief, meegecommit.
- `img/` — 5 Wikimedia Commons-portretten: Nistelrooij, Gullit, Geels, **Van Morrison**, Breukelen. _(Krol vervangen door Van Morrison op 11 juni; volgorde in `build_page.py`.)_
- `.github/workflows/update-pool.yml` — cron `10 0,3,6,13,21 * * *` UTC (tien over, zodat een net afgelopen duel zeker verwerkt is); Python 3.12. Draait fetch→build→build, commit alleen `data.json index.html results_state.json` bij wijziging.
- `.gitignore` — negeert o.a. `.venv/`, `__pycache__/`, `.claude/` (lokale Claude Code-config + preview `launch.json`).

## 5. Open punten / TODO
1. **GitHub Pages op de org aan?** check https://github.com/ruud-van/breukelen-poule/settings/pages → Deploy from branch, `main` / `/(root)`. (Na de org-transfer soms uitgezet.)
2. **Workflow permissions = Read and write** op **org-niveau**: https://github.com/organizations/ruud-van/settings/actions (repo-niveau was grijs). Nodig anders faalt de bot-push zodra er uitslagen zijn.
3. **Push-pad bot nog niet écht getest.** De eerste uitslag (Mexico 2-0 Zuid Afrika, 11 juni) is **handmatig** gecommit, niet door de bot. De eerstvolgende cron-run die een nieuwe uitslag oppakt is de echte test of de bot zelf mag pushen (hangt aan punt 2).
4. **Action Node-20 warning** (onschuldig, deprecation sept-2026). Optioneel: bump `actions/checkout@v4→v5` en `actions/setup-python@v5→v6` in de workflow.
5. Eventueel: cron-tijden fijnstellen op de exacte speeldagen.
6. **ESPN is een ongedocumenteerde API** (geen SLA). Werkt al jaren stabiel, maar als de structuur ooit wijzigt valt `results_fetch.py` stil. Mogelijke verbetering: openfootball als fallback terugzetten. Teamnaam-aliassen staan in `FEED_ALIASES` (`odds_fetch.py`); ESPN gebruikt o.a. `Czechia`, `South Korea`, `Bosnia-Herzegovina`, `United States`.

## 6. Werkwijze-notities (handig)
- Er draait een **GateGuard-hook** die vóór elke Bash/Edit/Write om "facts" vraagt. Gewoon kort de 4 punten benoemen en de actie herhalen. (Uit te zetten met env `ECC_GATEGUARD=off` indien gewenst.)
- Bij een push-conflict doordat de **bot** op de remote committe: `git pull --rebase` of (solo, bot-output is regenereerbaar) `git push --force`.
- `data.json` is ~280 KB door de voorspellingen; dat is prima voor een statische pagina.
