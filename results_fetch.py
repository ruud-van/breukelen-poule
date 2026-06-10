"""
Haalt gespeelde groepswedstrijd-uitslagen op en schrijft results_state.json.
Daarna bouwt de pipeline (build_pool.py -> build_page.py) de pagina opnieuw.

Bron: openfootball worldcup.json (geen sleutel nodig). Structuur (geverifieerd
tegen 2022 + 2026): top-level "matches" lijst, per match team1/team2 als string,
score onder match["score"]["ft"] = [thuis, uit] zodra gespeeld. Knock-out-duels
hebben placeholder-teams (1A, W73, ...) en worden overgeslagen.

Teamnaam-koppeling loopt via to_nl uit odds_fetch (EN_TO_NL + FEED_ALIASES),
dezelfde mapping als waarmee de odds zijn gekoppeld -> alle 48 teams vallen op
de Nederlandse formuliernamen.
"""
import re, json, urllib.request
from odds_fetch import to_nl

OPENFOOTBALL_URL = (
    "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
)
STATE = "results_state.json"

# placeholder-teams zoals "1A", "2L", "3A/B/C/D/F", "W73", "L101"
_PLACEHOLDER = re.compile(r"^(\d|W\d|L\d|3[A-Z])")


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_openfootball():
    """Lijst van (home_nl, away_nl, home_goals, away_goals) voor afgeronde groepsduels."""
    raw = _get(OPENFOOTBALL_URL)
    out, skipped = [], []
    for m in raw.get("matches", []):
        t1, t2 = m.get("team1"), m.get("team2")
        if not t1 or not t2 or _PLACEHOLDER.match(t1) or _PLACEHOLDER.match(t2):
            continue  # knock-out / nog niet bekend
        ft = (m.get("score") or {}).get("ft")
        if not ft:
            continue  # nog niet gespeeld
        home_nl, away_nl = to_nl(t1), to_nl(t2)
        if home_nl and away_nl:
            out.append((home_nl, away_nl, int(ft[0]), int(ft[1])))
        else:
            skipped.append(f"{t1} - {t2}")
    if skipped:
        print("WAARSCHUWING niet te koppelen feed-namen:", skipped)
    return out


def main():
    results = fetch_openfootball()
    state = {
        f"{h}|{a}": {"home": h, "away": a, "hg": hg, "ag": ag}
        for (h, a, hg, ag) in results
    }
    json.dump(state, open(STATE, "w"), ensure_ascii=False, indent=1)
    print(f"{len(state)} afgeronde groepswedstrijden weggeschreven naar {STATE}")


if __name__ == "__main__":
    main()
