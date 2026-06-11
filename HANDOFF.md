# Handoff — Breukelen-bookmaker poule (WK 2026)

_Laatst bijgewerkt: 11 juni 2026. Lees dit op de andere laptop om verder te gaan._

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
.venv/bin/python results_fetch.py    # haalt gespeelde uitslagen op -> results_state.json
.venv/bin/python build_pool.py       # leest Excel + wk_odds.json + results_state.json -> odds.json + data.json
.venv/bin/python build_page.py       # giet data.json in index.html
open index.html                      # lokaal bekijken
```
Verifieer JS na een template-wijziging:
`node --check <(sed -n '/<script>/,/<\/script>/p' index.html | sed '1d;$d')`

## 4. Pipeline & bestanden
- `results_fetch.py` — openfootball (sleutelloos), top-level `matches`, score `score.ft`; koppelt teamnamen via `to_nl` uit `odds_fetch.py`.
- `build_pool.py` — productie-build. Constantes bovenaan: `START=2000`, `STAKE_TOTO=100`, `STAKE_SCORE=20`. Schrijft `data.json` met: `participants`, `results`, `upcoming` (incl. per-match `odds`), `predictions` (58×72), `similarity` (MDS-netwerk `nodes`/`edges[a,b,pct]` + `most`/`least` top-5, voor toto én score).
- `build_page.py` — bevat de HTML/CSS/JS template. 3 tabs: **Stand**, **Voorspellingen** (accordeon per wedstrijd, naam-filter, exacte score goud / goede toto groen), **Gelijkenis** (netwerk met namen, lijndikte ∝ overeenkomst, declutter, top-5 lijsten, toggle toto/score). Header heeft 5 spelersfoto's (`img/`).
- `odds.json` — bevroren echte odds (niet opnieuw ophalen; The Odds API-sleutel is geroteerd/niet meer nodig).
- `WK_2026__allen_.xls` — master met deelnemers + voorspellingen (repo-relatief, meegecommit).
- `img/` — 5 Wikimedia Commons-portretten (Nistelrooij, Gullit, Geels, Breukelen, Krol).
- `.github/workflows/update-pool.yml` — cron `0 0,3,6,13,21 * * *` UTC; draait fetch→build→build, commit alleen `data.json index.html results_state.json` bij wijziging.

## 5. Open punten / TODO
1. **GitHub Pages op de org aan?** check https://github.com/ruud-van/breukelen-poule/settings/pages → Deploy from branch, `main` / `/(root)`. (Na de org-transfer soms uitgezet.)
2. **Workflow permissions = Read and write** op **org-niveau**: https://github.com/organizations/ruud-van/settings/actions (repo-niveau was grijs). Nodig anders faalt de bot-push zodra er uitslagen zijn.
3. **Push-pad bot nog niet écht getest** (handmatige run was groen maar met 0 uitslagen → niets gecommit). Eerste echte uitslag = de echte test.
4. **Action Node-20 warning** (onschuldig, deprecation sept-2026). Optioneel: bump `actions/checkout@v4→v5` en `actions/setup-python@v5→v6` in de workflow.
5. Eventueel: cron-tijden fijnstellen op de exacte speeldagen.

## 6. Werkwijze-notities (handig)
- Er draait een **GateGuard-hook** die vóór elke Bash/Edit/Write om "facts" vraagt. Gewoon kort de 4 punten benoemen en de actie herhalen. (Uit te zetten met env `ECC_GATEGUARD=off` indien gewenst.)
- Bij een push-conflict doordat de **bot** op de remote committe: `git pull --rebase` of (solo, bot-output is regenereerbaar) `git push --force`.
- `data.json` is ~280 KB door de voorspellingen; dat is prima voor een statische pagina.
