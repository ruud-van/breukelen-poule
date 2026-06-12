"""
Haalt EENMALIG de echte WK-odds op via The Odds API en bevriest ze in odds.json.
Bron: sport_key soccer_fifa_world_cup, markten h2h (1X2) + totals (over/under).

Draai een paar dagen voor 11 juni:
    ODDS_API_KEY=xxxx python odds_fetch.py
Daarna NOOIT meer aanraken; dit is de bevroren inzetlijn voor de hele poule.
Credits: markten(2) x regio's(1) = 2 credits per call. Eén call dekt alles.
"""
import os, json, statistics, datetime, urllib.request
from parse_form import TEAMS_NL_EN

EN_TO_NL = {en: nl for nl, (en, _iso) in TEAMS_NL_EN.items()}

# The Odds API spelt sommige namen anders dan mijn vertaaltabel. Hier gecontroleerd
# tegen de live feed en bijgesteld; rest wordt bij het draaien gemeld als 'niet te koppelen'.
FEED_ALIASES = {
    "Czech Republic": "Tsjechië",
    "Bosnia & Herzegovina": "Bosnië&Herz.",
    "Bosnia-Herzegovina": "Bosnië&Herz.",  # ESPN-schrijfwijze
    "USA": "VS",
    "Curaçao": "Curacao",
    # defensief, voor nog niet geziene varianten:
    "Congo DR": "Congo", "DR Congo": "Congo",
    "Cabo Verde": "Kaapverdië", "Türkiye": "Turkije",
    "Korea Republic": "Zuid Korea", "IR Iran": "Iran",
}

KEY = os.environ.get("ODDS_API_KEY", "")
URL = ("https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/"
       f"?regions=eu&markets=h2h,totals&oddsFormat=decimal&apiKey={KEY}")


def to_nl(name):
    return FEED_ALIASES.get(name) or EN_TO_NL.get(name)


def med(xs):
    return round(statistics.median(xs), 2) if xs else None


def fetch():
    with urllib.request.urlopen(URL, timeout=40) as r:
        events = json.load(r)

    odds, problems = {}, []
    for ev in events:
        home_en, away_en = ev["home_team"], ev["away_team"]
        home, away = to_nl(home_en), to_nl(away_en)
        if not home or not away:
            problems.append(f"niet te koppelen: {home_en} - {away_en}")
            continue

        h_home, h_draw, h_away = [], [], []
        # totals per lijn verzamelen; later 2.5 voorkeur, anders de meest gequote lijn
        over_by_line, under_by_line = {}, {}
        for bk in ev.get("bookmakers", []):
            for mk in bk.get("markets", []):
                if mk["key"] == "h2h":
                    for o in mk["outcomes"]:
                        if o["name"] == home_en: h_home.append(o["price"])
                        elif o["name"] == away_en: h_away.append(o["price"])
                        elif o["name"] == "Draw": h_draw.append(o["price"])
                elif mk["key"] == "totals":
                    for o in mk["outcomes"]:
                        ln = o.get("point")
                        if o["name"] == "Over": over_by_line.setdefault(ln, []).append(o["price"])
                        elif o["name"] == "Under": under_by_line.setdefault(ln, []).append(o["price"])

        # kies de totals-lijn: 2.5 als die er is, anders de lijn met de meeste quotes
        lines = set(over_by_line) & set(under_by_line)
        if 2.5 in lines:
            line = 2.5
        elif lines:
            line = max(lines, key=lambda L: len(over_by_line[L]) + len(under_by_line[L]))
        else:
            line = None

        rec = {
            "home": home, "away": away, "commence": ev.get("commence_time"),
            "h2h": {"1": med(h_home), "X": med(h_draw), "2": med(h_away)},
            "totals": {"line": line,
                       "over": med(over_by_line.get(line, [])) if line else None,
                       "under": med(under_by_line.get(line, [])) if line else None},
        }
        if None in rec["h2h"].values():
            problems.append(f"{home}-{away}: 1X2 incompleet")
        if line is None:
            problems.append(f"{home}-{away}: geen over/under gevonden")
        elif line != 2.5:
            problems.append(f"{home}-{away}: over/under op lijn {line} i.p.v. 2.5 (model gebruikt deze lijn)")
        odds[f"{home}|{away}"] = rec

    json.dump({"frozen_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "matches": odds},
              open("odds.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(odds)} wedstrijden bevroren in odds.json")
    if problems:
        print("Controleren:")
        for p in problems:
            print("  -", p)


if __name__ == "__main__":
    if not KEY:
        raise SystemExit("Zet ODDS_API_KEY in de omgeving.")
    fetch()
