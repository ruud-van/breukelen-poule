"""
Leest een Breukelen WK-2026 inschrijfformulier (.xls) in en valideert het.
Werkt voor alle 58 formulieren zolang ze dezelfde template aanhouden.
"""
import xlrd

# Nederlands (formulier) -> Engelse feed-naam + ISO3 voor het koppelen aan odds/uitslagen.
# LET OP: 'Congo' is dubbelzinnig (DR Congo vs Congo-Brazzaville) -> bevestigen.
TEAMS_NL_EN = {
    "Algerije": ("Algeria", "ALG"), "Argentinië": ("Argentina", "ARG"),
    "Australië": ("Australia", "AUS"), "België": ("Belgium", "BEL"),
    "Bosnië&Herz.": ("Bosnia and Herzegovina", "BIH"), "Brazilië": ("Brazil", "BRA"),
    "Canada": ("Canada", "CAN"), "Colombia": ("Colombia", "COL"),
    "Congo": ("DR Congo", "COD"), "Curacao": ("Curaçao", "CUW"),
    "Duitsland": ("Germany", "GER"), "Ecuador": ("Ecuador", "ECU"),
    "Egypte": ("Egypt", "EGY"), "Engeland": ("England", "ENG"),
    "Frankrijk": ("France", "FRA"), "Ghana": ("Ghana", "GHA"),
    "Haiti": ("Haiti", "HAI"), "Irak": ("Iraq", "IRQ"),
    "Iran": ("Iran", "IRN"), "Ivoorkust": ("Ivory Coast", "CIV"),
    "Japan": ("Japan", "JPN"), "Jordanië": ("Jordan", "JOR"),
    "Kaapverdië": ("Cape Verde", "CPV"), "Kroatië": ("Croatia", "CRO"),
    "Marokko": ("Morocco", "MAR"), "Mexico": ("Mexico", "MEX"),
    "Nederland": ("Netherlands", "NED"), "Nieuw Zeeland": ("New Zealand", "NZL"),
    "Noorwegen": ("Norway", "NOR"), "Oezbekistan": ("Uzbekistan", "UZB"),
    "Oostenrijk": ("Austria", "AUT"), "Panama": ("Panama", "PAN"),
    "Paraguay": ("Paraguay", "PAR"), "Portugal": ("Portugal", "POR"),
    "Quatar": ("Qatar", "QAT"), "Saoedi Arabië": ("Saudi Arabia", "KSA"),
    "Schotland": ("Scotland", "SCO"), "Senegal": ("Senegal", "SEN"),
    "Spanje": ("Spain", "ESP"), "Tsjechië": ("Czechia", "CZE"),
    "Tunesië": ("Tunisia", "TUN"), "Turkije": ("Turkey", "TUR"),
    "Uruguay": ("Uruguay", "URU"), "VS": ("United States", "USA"),
    "Zuid Afrika": ("South Africa", "RSA"), "Zuid Korea": ("South Korea", "KOR"),
    "Zweden": ("Sweden", "SWE"), "Zwitserland": ("Switzerland", "SUI"),
}

GROUP_ROWS = range(4, 76)  # 72 groepswedstrijden


def _cv(sh, r, c):
    v = sh.cell_value(r, c)
    if isinstance(v, float) and v == int(v):
        v = int(v)
    return v


def parse_form(path):
    """Geeft (naam, predictions, problems). predictions: list van dicts."""
    b = xlrd.open_workbook(path)
    sh = b.sheet_by_index(0)
    name = str(_cv(sh, 3, 7)).strip()
    problems = []
    preds = []
    for r in GROUP_ROWS:
        home = str(_cv(sh, r, 2)).strip()
        away = str(_cv(sh, r, 5)).strip()
        if not home or not away:
            problems.append(f"rij {r}: lege wedstrijd")
            continue
        ph, pa = _cv(sh, r, 7), _cv(sh, r, 9)
        if ph == "" or pa == "":
            problems.append(f"rij {r}: ontbrekende voorspelling {home}-{away}")
            continue
        for t in (home, away):
            if t not in TEAMS_NL_EN:
                problems.append(f"rij {r}: onbekend team '{t}'")
        preds.append({
            "row": r, "datetime": str(_cv(sh, r, 1)).strip(),
            "home": home, "away": away,
            "pred_home": int(ph), "pred_away": int(pa),
        })
    if len(preds) != 72:
        problems.append(f"verwacht 72 wedstrijden, gevonden {len(preds)}")
    return name, preds, problems


if __name__ == "__main__":
    import sys, json
    name, preds, problems = parse_form(sys.argv[1])
    print("Deelnemer:", name)
    print("Wedstrijden ingelezen:", len(preds))
    print("Problemen:", problems if problems else "geen")
