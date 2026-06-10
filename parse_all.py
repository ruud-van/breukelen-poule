"""
Leest het master-bestand van de organisator (tabblad 'Uitslagenblad') met alle
deelnemers in één keer. Layout: wedstrijden in de rijen (2..73 = 72 groeps-
wedstrijden), per deelnemer een blok van 4 kolommen vanaf kolom 11
(thuisscore, '-', uitscore, punten); deelnemersnaam in rij 1 boven het blok.

Geeft: matches (NL namen + datum) en predictions {naam: {match_index: (h,a)}}.
"""
import xlrd
from parse_form import TEAMS_NL_EN

SHEET = "Uitslagenblad"
FIRST_BLOCK_COL = 11
BLOCK = 4
MATCH_ROW_START = 2
N_GROUP = 72


def _cv(sh, r, c):
    v = sh.cell_value(r, c)
    return int(v) if isinstance(v, float) and v == int(v) else v


def parse_all(path):
    sh = xlrd.open_workbook(path).sheet_by_name(SHEET)
    problems = []

    # deelnemers
    participants = []
    c = FIRST_BLOCK_COL
    while c < sh.ncols:
        name = str(_cv(sh, 1, c)).strip()
        if name:
            participants.append((name, c))
        c += BLOCK
    if len({n for n, _ in participants}) != len(participants):
        problems.append("dubbele deelnemersnamen gevonden")

    # wedstrijden
    rows = list(range(MATCH_ROW_START, MATCH_ROW_START + N_GROUP))
    matches = []
    for i, r in enumerate(rows):
        home, away = str(_cv(sh, r, 2)).strip(), str(_cv(sh, r, 5)).strip()
        if not home or not away:
            problems.append(f"rij {r}: lege wedstrijd")
            continue
        for t in (home, away):
            if t not in TEAMS_NL_EN:
                problems.append(f"rij {r}: onbekend team '{t}'")
        matches.append({"id": i, "datetime": str(_cv(sh, r, 1)).strip(),
                        "home": home, "away": away})

    # voorspellingen
    preds = {}
    for name, col in participants:
        pr = {}
        for i, r in enumerate(rows):
            ph, pa = _cv(sh, r, col), _cv(sh, r, col + 2)
            if ph == "" or pa == "":
                problems.append(f"{name}: ontbrekende voorspelling wedstrijd {i}")
                continue
            pr[i] = (int(ph), int(pa))
        preds[name] = pr

    return matches, preds, problems


if __name__ == "__main__":
    import sys
    m, p, probs = parse_all(sys.argv[1])
    print(f"Deelnemers: {len(p)} | wedstrijden: {len(m)} | "
          f"voorspellingen: {sum(len(v) for v in p.values())}")
    print("Problemen:", probs if probs else "geen")
