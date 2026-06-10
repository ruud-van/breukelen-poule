# Breukelen-bookmaker pool — voorbereide pijplijn

Status: werkende demo. Jouw formulier is als echte deelnemer ingelezen; de andere
namen, de odds en de uitslagen zijn placeholder zodat de pagina nu al draait.

## Onderdelen

- `index.html` — de pagina. Open in een browser. Toont klassement op budget (alle
  namen), budget-over-tijd grafiek, snelste stijger/daler, langste toto-goed en
  toto-fout streak, toto-trefpercentage, laatste uitslagen en komende odds.
- `odds_model.py` — bivariate Poisson + Dixon-Coles. Zet 1X2- en over/under-odds om
  in correct-score odds, met instelbare marge (nu 40% overround, zodat ze er als
  echte boekmakers-odds uitzien).
- `realism_check.py` — de realiteitscheck op het model (draai: `python realism_check.py`).
- `parse_form.py` — leest een .xls-formulier in, valideert (72 wedstrijden, scores
  ingevuld, bekende teams) en bevat de teamnaam-vertaaltabel NL→Engels.
- `build_demo.py` — bouwt de demo-`data.json` (placeholder-odds + gesimuleerde uitslagen).
- `build_page.py` — giet `data.json` in `index.html`.
- `results_fetch.py` — haalt echte uitslagen op (bron/endpoint nog te bevestigen).
- `update-pool.yml` — GitHub Action die een paar keer per dag de uitslagen ververst
  en de pagina herbouwt. Hoort in `.github/workflows/`.

## Wat ik nog van jou nodig heb

1. De 58 ingevulde formulieren (zelfde template). Dan vervang ik de demodeelnemers.
2. Eén snapshot van de echte 1X2- + over/under-odds voor de 72 groepswedstrijden,
   een paar dagen voor 11 juni. Dat wordt `odds.json` en blijft daarna bevroren.
3. Voor de numerieke backtest: van 8 a 10 wedstrijden de echte correct-score odds
   van een willekeurige boekmaker (overtikken of screenshot volstaat).

## Bekende keuzes / aandachtspunten

- Marge: door de gevraagde realistische marge op de correct-score odds is het
  score-potje (50 euro) gemiddeld verliesgevend. Daardoor zakt het budget over het
  toernooi licht; iedereen blijft boven nul, maar de meesten eindigen onder hun
  startbedrag van 2500. Wil je dat de meeste mensen boven 2500 blijven, verhoog het
  startbedrag of verlaag de score-inzet/marge. Dat is een knop, niet een herbouw.
- `Congo` in het formulier is dubbelzinnig (DR Congo of Congo-Brazzaville). Even
  bevestigen voor de feed-koppeling klopt.
