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
import os, re, json, datetime, urllib.request
from odds_fetch import to_nl

_NL_MONTHS = ["januari", "februari", "maart", "april", "mei", "juni",
              "juli", "augustus", "september", "oktober", "november", "december"]


def _now_nl():
    """Huidige tijd in NL (CEST = UTC+2; het hele WK valt in de zomertijd)
    als 'D maand HH:MM', bv. '11 juni 23:14'."""
    nl = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
    return f"{nl.day} {_NL_MONTHS[nl.month - 1]} {nl:%H:%M}"


def _nl_dt(iso):
    """ESPN-UTC-tijd 'YYYY-MM-DDTHH:MMZ' -> NL 'D maand HH:MM' (UTC+2)."""
    s = (iso or "").replace("Z", "")
    dt = None
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            break
        except ValueError:
            continue
    if dt is None:
        return ""
    dt += datetime.timedelta(hours=2)
    return f"{dt.day} {_NL_MONTHS[dt.month - 1]} {dt:%H:%M}"

# Hele groepsfase WK 2026 (11 t/m 27 juni); ruime marge, knock-out wordt
# alsnog op season.slug uitgefilterd.
ESPN_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/"
    "scoreboard?dates=20260611-20260703&limit=200"
)
# Knock-outfase (28 juni t/m 19 juli).
KO_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/"
    "scoreboard?dates=20260628-20260720&limit=120"
)
STATE = "results_state.json"
KO_STATE = "knockout.json"

# ESPN season.slug -> korte rondesleutel.
KO_SLUG = {"round-of-32": "r32", "round-of-16": "r16", "quarterfinals": "qf",
           "semifinals": "sf", "3rd-place-match": "p3", "final": "fin"}
KO_TITLE = {"r32": "Laatste 32", "r16": "Laatste 16", "qf": "Kwartfinale",
            "sf": "Halve finale", "fin": "Finale", "p3": "Troostfinale"}

# Vaste bracketboom WK 2026 (afgeleid uit ESPN's wedstrijdnamen; wedstrijden
# binnen een ronde genummerd op oplopend ESPN-id). Per knooppunt de twee
# toeleverende wedstrijden [boven, onder]. De troostfinale (p3) staat los.
KO_FEEDERS = {
    ("fin", 1): [("sf", 1), ("sf", 2)],
    ("sf", 1): [("qf", 1), ("qf", 2)], ("sf", 2): [("qf", 3), ("qf", 4)],
    ("qf", 1): [("r16", 1), ("r16", 2)], ("qf", 2): [("r16", 5), ("r16", 6)],
    ("qf", 3): [("r16", 3), ("r16", 4)], ("qf", 4): [("r16", 7), ("r16", 8)],
    ("r16", 1): [("r32", 1), ("r32", 3)], ("r16", 2): [("r32", 2), ("r32", 5)],
    ("r16", 3): [("r32", 4), ("r32", 6)], ("r16", 4): [("r32", 7), ("r32", 8)],
    ("r16", 5): [("r32", 11), ("r32", 12)], ("r16", 6): [("r32", 9), ("r32", 10)],
    ("r16", 7): [("r32", 13), ("r32", 15)], ("r16", 8): [("r32", 14), ("r32", 16)],
}


def _ko_order():
    """Top-naar-onder bracketvolgorde per ronde (in-order-traversal van de
    boom), zodat een CSS-bracket met gelijke tussenruimte de juiste paren
    verbindt."""
    order = {"r32": [], "r16": [], "qf": [], "sf": [], "fin": []}

    def walk(node):
        feed = KO_FEEDERS.get(node)
        if not feed:                      # blad = r32-wedstrijd
            order["r32"].append(node[1])
            return
        walk(feed[0])
        order[node[0]].append(node[1])
        walk(feed[1])

    walk(("fin", 1))
    return order

KO_ORDER = _ko_order()


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


def _nl_team(dn):
    """ESPN-teamnaam of placeholder -> (NL-tekst, resolved?). Interne
    'winner/loser of match'-placeholders worden leeg gelaten (de bracketlijn
    laat de koppeling al zien)."""
    if not dn:
        return ("", False)
    nl = to_nl(dn)
    if nl:
        return (nl, True)
    m = re.match(r"Group ([A-Z]) Winner$", dn)
    if m:
        return (f"Winnaar groep {m.group(1)}", False)
    m = re.match(r"Group ([A-Z]) 2nd Place$", dn)
    if m:
        return (f"Nr. 2 groep {m.group(1)}", False)
    m = re.match(r"Third Place Group ([A-Z/]+)$", dn)
    if m:
        return (f"Nr. 3 ({m.group(1)})", False)
    if re.match(r"(Round of \d+|Quarterfinal|Semifinal) \d+ (Winner|Loser)$", dn):
        return ("", False)
    return (dn, True)  # onbekende, maar ogenschijnlijk echte naam: tonen


def fetch_knockout():
    """Bracket-payload {rounds:[...], third:{...}} uit de ESPN-knock-outfeed."""
    raw = _get(KO_URL)
    evs = raw.get("events", [])
    bynum = {}
    for slug, key in KO_SLUG.items():
        lst = sorted((e for e in evs if (e.get("season") or {}).get("slug") == slug),
                     key=lambda e: int(e["id"]))
        for i, e in enumerate(lst, 1):
            bynum[(key, i)] = e

    def match(key, num):
        e = bynum.get((key, num))
        if not e:
            return {"num": num, "dt": "", "completed": False, "teams": [None, None]}
        comp = (e.get("competitions") or [{}])[0]
        completed = bool((comp.get("status") or {}).get("type", {}).get("completed"))
        # Thuis-ploeg bovenaan: ESPN markeert in knock-outs de hoger geplaatste
        # ploeg als "home"; media/schema's tonen die eerst ("Nederland - Marokko").
        cs = sorted(comp.get("competitors", []),
                    key=lambda c: 0 if c.get("homeAway") == "home" else 1)
        teams = []
        for c in cs:
            name, resolved = _nl_team((c.get("team") or {}).get("displayName", ""))
            try:
                score = int(c.get("score"))
            except (TypeError, ValueError):
                score = None
            teams.append({"name": name, "resolved": resolved,
                          "score": score if completed else None,
                          "winner": bool(c.get("winner"))})
        return {"num": num, "dt": _nl_dt(e.get("date", "")),
                "completed": completed, "teams": teams}

    rounds = [{"key": k, "title": KO_TITLE[k],
               "matches": [match(k, n) for n in KO_ORDER[k]]}
              for k in ("r32", "r16", "qf", "sf", "fin")]
    return {"rounds": rounds, "third": match("p3", 1)}


def _write_idempotent(path, payload):
    """Schrijf payload + '_updated_at', maar ververs de tijd alleen als de
    inhoud wijzigt (anders geen lege bot-commit)."""
    prev = json.load(open(path)) if os.path.exists(path) else {}
    prev_ts = prev.pop("_updated_at", None)
    out = dict(payload)
    out["_updated_at"] = prev_ts if (payload == prev and prev_ts) else _now_nl()
    json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
    return out["_updated_at"]


def main():
    ko = fetch_knockout()
    ko_ts = _write_idempotent(KO_STATE, ko)
    print(f"knock-out-schema weggeschreven naar {KO_STATE} (verwerkt: {ko_ts})")

    results = fetch_espn()
    matches = {
        f"{h}|{a}": {"home": h, "away": a, "hg": hg, "ag": ag}
        for (h, a, hg, ag) in results
    }
    # "_updated_at" alleen verversen als de uitslagen écht wijzigen, zodat de
    # bot niet elke cron-run een lege commit doet.
    prev = json.load(open(STATE)) if os.path.exists(STATE) else {}
    prev_updated = prev.pop("_updated_at", None)
    # Uitslagen kunnen tijdens de groepsfase alleen groeien; minder dan vorige
    # run betekent een kapotte/lege feed -> niets overschrijven, hard falen.
    if len(matches) < len(prev):
        raise SystemExit(f"WEIGEREN: feed gaf {len(matches)} uitslagen, "
                         f"vorige run had er {len(prev)} — {STATE} blijft ongemoeid")
    state = dict(matches)
    if matches:
        keep = matches == prev and prev_updated
        state["_updated_at"] = prev_updated if keep else _now_nl()
    json.dump(state, open(STATE, "w"), ensure_ascii=False, indent=1)
    print(f"{len(matches)} afgeronde groepswedstrijden weggeschreven naar {STATE}"
          + (f" (verwerkt: {state['_updated_at']})" if matches else ""))


if __name__ == "__main__":
    main()
