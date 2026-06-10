# Handoff — Breukelen-bookmaker poule (WK 2026)

## 1. Context & doel
Een webpagina die voor een vriendenpoule (58 deelnemers, WK 2026 groepsfase) laat zien
wat iedereen fictief zou hebben verdiend als ze per groepswedstrijd 100 euro op de
toto-uitslag (1X2) en 25 euro op de exacte eindstand hadden ingezet, tegen echte
bookmakers-odds, startbudget 2500 euro. De pagina staat los van de officiële poule van
organisator Ruud van Breukelen. Naast de euro-stand toont hij: ranglijst op budget (alle
namen), snelste stijger/daler, langste toto-goed en toto-fout streak, en aantal toto's
goed. Doel van de volgende sessie: het geheel live zetten met een dagelijkse,
geautomatiseerde update, bij voorkeur via Claude Code (git/`gh`/CLI).

## 2. Huidige staat
- **Pagina is inhoudelijk af** en rendert op ECHTE odds en ECHTE deelnemers
  (`index.html`, gegenereerd uit `data.json`). Chart.js via cdnjs; animatie-knop "Top 6"
  (trage progressive-line, `step=19000/np`) plus "Iedereen".
- **Odds zijn bevroren en echt**: `odds.json` is afgeleid uit `wk_odds.json` (The Odds API,
  sport_key `soccer_fifa_world_cup`, markten h2h+totals, regio eu), consensus = mediaan over
  ~24 EU-boekmakers. Alle 72 wedstrijden gekoppeld. Model reproduceert de markt (residu ~2e-8).
- **Voorspellingen**: alle 58 deelnemers + 72 groepswedstrijden ingelezen uit het master-
  Excel via `parse_all.py` (0 problemen). Tab "Uitslagenblad", deelnemersblokken van 4
  kolommen vanaf kolom 11, wedstrijden rij 2..73.
- **Model**: bivariate Poisson + Dixon-Coles (`odds_model.py`). Correct-score odds met 40%
  overround-marge (er-uit-ziend als echte odds); toto-uitbetaling = echte consensus-1X2.
- **NOG NIET af, dit is het kernwerk**: de uitslagen op de pagina zijn GESIMULEERD.
  `build_pool.py` leest het Excel nu via een hardcoded pad (`/mnt/user-data/uploads/...`)
  en SIMULEERT uitslagen. Het is nog niet gekoppeld aan echte uitslagen.
  `results_fetch.py` bestaat (openfootball zonder sleutel, of football-data.org met token),
  maar (a) de openfootball-endpoint/JSON-structuur is ONGEVERIFIEERD, (b) de teamnaam-
  vertaling is alleen gecheckt tegen The Odds API-namen, niet tegen de uitslagenfeed
  (andere spelling waarschijnlijk), (c) `build_pool.py` leest `results_state.json` nog niet.
- Action-workflow `update-pool.yml` bestaat maar verwacht een productie-build die echte
  uitslagen inleest; die koppeling moet nog gelegd worden.

## 3. Volgende stappen (in volgorde)
1. Bundel uitpakken in de werkmap; `pip install xlrd numpy scipy`.
2. **Resultaten-pipeline afmaken** (kernwerk):
   a. Kies uitslagenbron: openfootball (geen sleutel) of football-data.org (token). Verifieer
      de exacte URL + JSON-structuur voor WK 2026.
   b. Maak/valideer een vertaaltabel van de feed-teamnamen naar de Nederlandse formuliernamen
      voor ALLE 48 teams (breid `FEED_ALIASES` in `odds_fetch.py` uit; de huidige aliassen
      zijn alleen voor The Odds API gecheckt).
   c. Herzie `build_pool.py`: paden repo-relatief maken (commit het Excel + `odds.json` mee,
      geen `/mnt/...`), `results_state.json` inlezen, gespeelde wedstrijden invullen met de
      ECHTE uitslag i.p.v. simuleren, en standen/streaks/stijgers daarop berekenen.
   d. Vóór 11 juni zijn er nog geen uitslagen: lege/0-staat is prima.
3. Volledige build lokaal testen (`python build_pool.py && python build_page.py`).
4. **Eenmalige setup** (gebruiker doet de auth): `gh auth login` (+ `vercel login` indien
   Vercel). Daarna via commando's: repo aanmaken, bestanden committen/pushen
   (pagina, `odds.json`, Excel, scripts, `.github/workflows/update-pool.yml`), GitHub Pages
   aanzetten of `vercel deploy`, en bij football-data.org het token zetten met
   `gh secret set FOOTBALL_DATA_TOKEN`.
5. Action testen via `workflow_dispatch`; controleren dat hij commit + de host redeployt.
   Cron staat nu op 4x/dag (UTC) — afstemmen op speeldagen/tijdzone.
6. Vanaf 11 juni vervangen de echte uitslagen de gesimuleerde; na de groepsfase bevriest het.

## 4. Belangrijke beslissingen & waarom
- Score-inzet 25 (niet 50): budgetsimulatie liet zien dat 25 ~91% van de deelnemers boven
  nul houdt bij start 2500; met 50 was dat ~76%. Start 2500 blijft.
- 40% overround op correct-score, zodat de odds er echt uitzien (expliciete wens gebruiker).
  Gevolg: pool is per saldo negatief-som, dus de meesten eindigen onder hun startbedrag;
  "positief" = boven nul.
- Correct-score odds via Poisson-model i.p.v. een betaalde bron, want gratis correct-score
  odds voor het WK bestaan niet; toto-uitbetaling gebruikt wel echte consensus-1X2.
- Alleen groepswedstrijden (72), geen knock-out.
- Titel "Breukelen-bookmaker poule"; introtekst met gok-NB en "los van Ruud" staat verbatim
  bovenaan; voetbal-aankleding (bal + veldlijnen in kop, balpatroon op achtergrond).
- "Congo" = DR Congo (bevestigd).

## 5. Artefacten & verwijzingen (in deze bundel)
- `index.html` — de pagina (productie-output).
- `build_pool.py` — productie-build (MOET nog van simulatie naar echte uitslagen, zie stap 2).
- `build_page.py` — giet `data.json` in `index.html`.
- `odds_model.py` — Poisson+Dixon-Coles, correct-score odds met marge.
- `odds_fetch.py` — consensus uit The Odds API + teamnaam-aliassen.
- `parse_all.py` — leest alle 58 deelnemers uit het master-Excel.
- `parse_form.py` — losse-formulier parser + `TEAMS_NL_EN` vertaaltabel.
- `results_fetch.py` — uitslagen ophalen (bron/endpoint nog te verifiëren).
- `realism_check.py`, `scenario_sim.py` — model-validatie en budgetscenario's.
- `update-pool.yml` — GitHub Action (cron) → in repo onder `.github/workflows/`.
- `odds.json` — bevroren echte odds (72 wedstrijden).
- `data.json` — huidige pagina-data (nog met gesimuleerde uitslagen).
- Brondata aanleveren in de repo: het master-Excel `WK_2026__allen_.xls` en `wk_odds.json`.
- The Odds API-sleutel: `[REDACTED]` — staat in de oude chat; roteer hem en zet hem
  nooit in de repo. Voor de dagelijkse run is hij NIET nodig (odds zijn bevroren), alleen
  een eventueel uitslagen-token.

## 6. Aanbevolen skills voor de volgende sessie
- `product-self-knowledge` — verifieer actuele Claude Code / `gh` / deploy-details i.p.v. uit geheugen.
- `frontend-design` — alleen als er nog aan de pagina-styling gesleuteld wordt.
- (De meeste stappen zijn git/CLI-werk en vragen geen specifieke skill.)
