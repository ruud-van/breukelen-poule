"""
Haalt gespeelde groepswedstrijd-uitslagen op en schrijft results_state.json.
Daarna bouwt de pipeline (build_pool.py -> build_page.py) de pagina opnieuw.

Bron: ESPN scoreboard (geen sleutel nodig) — dezelfde feed als ESPN.com/-app,
near-realtime. Endpoint per dag/datumbereik:
  site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=YYYYMMDD-YYYYMMDD
Per "event" zit de wedstrijd onder competitions[0]: status.type.completed == True
zodra afgelopen, competitors[] met homeAway ("home"/"away") en score (string).
Groepsduels herkenbaar aan season.slug == "group-stage"; knock-out (placeholder-
teams als "Round of 32 X Winner") valt daar buiten en wordt overgeslagen.

Teamnaam-koppeling loopt via to_nl uit odds_fetch (EN_TO_NL + FEED_ALIASES),
dezelfde mapping als waarmee de odds zijn gekoppeld -> alle 48 teams vallen op
de Nederlandse formuliernamen.
"""
import json, urllib.request
from odds_fetch import to_nl

# Hele groepsfase WK 2026 (11 t/m 27 juni); ruime marge, knock-out wordt
# alsnog op season.slug uitgefilterd.
ESPN_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/"
    "scoreboard?dates=20260611-20260703&limit=200"
)
STATE = "results_state.json"


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "breukelen-poule"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_espn():
    """Lijst van (home_nl, away_nl, home_goals, away_goals) voor afgeronde groepsduels."""
    raw = _get(ESPN_URL)
    out, skipped = [], []
    for ev in raw.get("events", []):
        if (ev.get("season") or {}).get("slug") != "group-stage":
            continue  # knock-out / ander toernooi-onderdeel
        comp = (ev.get("competitions") or [{}])[0]
        if not (comp.get("status") or {}).get("type", {}).get("completed"):
            continue  # nog niet afgelopen
        home = away = None
        for c in comp.get("competitors", []):
            side = c.get("homeAway")
            name = (c.get("team") or {}).get("displayName")
            try:
                goals = int(c.get("score"))
            except (TypeError, ValueError):
                goals = None
            if side == "home":
                home = (name, goals)
            elif side == "away":
                away = (name, goals)
        if not home or not away or home[1] is None or away[1] is None:
            continue
        home_nl, away_nl = to_nl(home[0]), to_nl(away[0])
        if home_nl and away_nl:
            out.append((home_nl, away_nl, home[1], away[1]))
        else:
            skipped.append(f"{home[0]} - {away[0]}")
    if skipped:
        print("WAARSCHUWING niet te koppelen feed-namen:", skipped)
    return out


def main():
    results = fetch_espn()
    state = {
        f"{h}|{a}": {"home": h, "away": a, "hg": hg, "ag": ag}
        for (h, a, hg, ag) in results
    }
    json.dump(state, open(STATE, "w"), ensure_ascii=False, indent=1)
    print(f"{len(state)} afgeronde groepswedstrijden weggeschreven naar {STATE}")


if __name__ == "__main__":
    main()
