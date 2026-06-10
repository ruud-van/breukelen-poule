"""
Bouwt een demo data.json voor de Breukelen-bookmaker pool.
- Echte wedstrijdlijst + Chris' echte voorspellingen uit het formulier.
- Placeholder 1X2/over-under odds afgeleid uit de LF-sterktefactoren in het
  formulier (CLEAR: demo-odds, in productie vervangen door de echte feed-snapshot).
- ~24 verzonnen mededeelnemers, gesimuleerde uitslagen voor de eerste speelrondes.
"""
import json, random
import numpy as np
import xlrd
from math import exp, factorial
from odds_model import fit_match, correct_score_odds, toto_odds, MAXG
from parse_form import parse_form, TEAMS_NL_EN, _cv

FORM = "/mnt/user-data/uploads/Chris_Snijders_-_Inschrijfformulier_WK_2026.xls"
START = 2500
N_PLAYED = 17           # eerste speelrondes t/m 16 juni "gespeeld"
OVERROUND_CS = 1.40
LONGSHOT = 0.12
random.seed(7); np.random.seed(7)

# ---- 1. wedstrijdlijst + LF-factoren uit het formulier -------------------
b = xlrd.open_workbook(FORM); sh = b.sheet_by_index(0)
chris_name, chris_preds, _ = parse_form(FORM)
LF = {}
for r in range(4, 76):
    LF[str(_cv(sh, r, 2)).strip()] = float(_cv(sh, r, 3))
    LF[str(_cv(sh, r, 5)).strip()] = float(_cv(sh, r, 6))

matches = []
for p in chris_preds:
    matches.append({"id": len(matches), "datetime": p["datetime"],
                    "home": p["home"], "away": p["away"]})

# ---- 2. placeholder odds via een sterktemodel uit LF ---------------------
def rating(team): return 1.0 / LF[team]
def true_lambdas(home, away):
    rh, ra = rating(home), rating(away)
    sup = 2.2 * (rh - ra) + 0.25                 # incl. thuisvoordeel
    tot = 2.5 + 0.45 * (rh + ra)
    lh = max((tot + sup) / 2, 0.15); la = max((tot - sup) / 2, 0.15)
    return lh, la
def pois(k, lam): return exp(-lam) * lam ** k / factorial(k)
def odds_from_lambdas(lh, la, margin=1.05):
    P = np.array([[pois(i, lh) * pois(j, la) for j in range(11)] for i in range(11)])
    P /= P.sum()
    p1 = np.tril(P, -1).sum(); pX = np.trace(P); p2 = np.triu(P, 1).sum()
    pOver = sum(P[i, j] for i in range(11) for j in range(11) if i + j >= 3)
    pUnder = 1 - pOver
    f = lambda p: round(1.0 / (p * margin), 2)
    return f(p1), f(pX), f(p2), f(pOver), f(pUnder)

match_models = []
for m in matches:
    lh, la = true_lambdas(m["home"], m["away"])
    o1, ox, o2, oo, ou = odds_from_lambdas(lh, la)
    fit = fit_match(o1, ox, o2, oo, ou)
    fair, marg = correct_score_odds(fit["matrix"], OVERROUND_CS, LONGSHOT)
    t = toto_odds(fit)
    m["toto_odds"] = {"1": round(t[0], 2), "X": round(t[1], 2), "2": round(t[2], 2)}
    match_models.append({"lh": lh, "la": la, "matrix": fit["matrix"],
                         "cs_marg": marg, "toto": t})

# ---- 3. uitslagen simuleren voor de eerste N wedstrijden -----------------
def sim_score(mm):
    P = mm["matrix"].ravel()
    k = np.random.choice(len(P), p=P / P.sum())
    return int(k // (MAXG + 1)), int(k % (MAXG + 1))
for i, m in enumerate(matches):
    if i < N_PLAYED:
        h, a = sim_score(match_models[i])
        m["status"] = "played"; m["result"] = {"home": h, "away": a}
    else:
        m["status"] = "upcoming"; m["result"] = None

def toto_of(h, a): return "1" if h > a else ("2" if a > h else "X")

# ---- 4. deelnemers: Chris + verzonnen mededeelnemers ---------------------
NAMES = ["Chris Snijders", "Rob van Breukelen", "Patty de Wit", "Willem Kahr",
         "Martijn Bosch", "Sanne Verhoeven", "Bram Willemsen", "Eva Janssen",
         "Tom de Vries", "Lotte Smit", "Daan Mulder", "Fenna Bakker",
         "Joost Hendriks", "Iris van Dijk", "Pim Visser", "Noor Jansen",
         "Sven Maas", "Anouk Peters", "Ruben Kok", "Lieke de Boer",
         "Bas Vermeer", "Maud Scholten", "Teun Dekker", "Nina Postma",
         "Gijs Hofman"]

def gen_predictions(skill):
    """skill in [0,1]: hoger = vaker de favoriet en realistischer scores."""
    preds = {}
    for i, m in enumerate(matches):
        lh, la = match_models[i]["lh"], match_models[i]["la"]
        if random.random() < 0.45 + 0.4 * skill:        # volg de verwachting
            ph = max(0, int(round(lh + np.random.normal(0, 0.6))))
            pa = max(0, int(round(la + np.random.normal(0, 0.6))))
        else:                                            # eigenwijs
            ph = random.choice([0, 1, 1, 2, 2, 3])
            pa = random.choice([0, 0, 1, 1, 2, 3])
        preds[i] = (min(ph, 6), min(pa, 6))
    return preds

participants = []
for n in NAMES:
    if n == "Chris Snijders":
        pr = {p["row"] - 4: (p["pred_home"], p["pred_away"]) for p in chris_preds}
        pr = {i: pr[i] for i in range(72)}
    else:
        pr = gen_predictions(skill=random.uniform(0.2, 0.95))
    participants.append({"name": n, "preds": pr})

# ---- 5. afrekenen: budget, streaks, trefpercentage, recente mutatie ------
played = [m for m in matches if m["status"] == "played"]
played_labels = [f'{m["home"]}-{m["away"]}' for m in played]
last_day = played[-1]["datetime"].split()[0] + " " + played[-1]["datetime"].split()[1] \
    if played else None
# speeldag = kalenderdatum (eerste twee tokens: "11 juni")
def daykey(dt): return " ".join(dt.split()[:2])
last_daykey = daykey(played[-1]["datetime"]) if played else None

out_parts = []
for part in participants:
    budget = START; series = [START]
    toto_seq = []; net_last_day = 0.0; correct = 0
    for i, m in enumerate(played):
        mm = match_models[i]
        ph, pa = part["preds"][i]
        ph, pa = min(ph, MAXG), min(pa, MAXG)
        ah, aa = m["result"]["home"], m["result"]["away"]
        # toto-inzet 100
        pt = toto_of(ph, pa); at = toto_of(ah, aa)
        if pt == at:
            net = 100 * (mm["toto"][{"1": 0, "X": 1, "2": 2}[pt]] - 1); correct += 1; ok = True
        else:
            net = -100; ok = False
        # score-inzet 50
        if (ph, pa) == (ah, aa):
            net += 50 * (mm["cs_marg"][ph, pa] - 1)
        else:
            net += -50
        budget += net; series.append(round(budget, 2)); toto_seq.append(ok)
        if daykey(m["datetime"]) == last_daykey:
            net_last_day += net

    # streaks
    def longest(seq, val):
        best = cur = 0
        for x in seq:
            cur = cur + 1 if x == val else 0
            best = max(best, cur)
        return best
    cur_streak = 0; cur_type = None
    for x in reversed(toto_seq):
        if cur_type is None: cur_type = x
        if x == cur_type: cur_streak += 1
        else: break

    out_parts.append({
        "name": part["name"],
        "budget": round(budget, 2),
        "series": series,
        "toto_correct": correct,
        "toto_played": len(played),
        "hit_rate": round(100 * correct / len(played), 1) if played else 0,
        "longest_correct": longest(toto_seq, True),
        "longest_wrong": longest(toto_seq, False),
        "current_streak": cur_streak,
        "current_streak_type": "goed" if cur_type else "fout",
        "delta_last_day": round(net_last_day, 2),
    })

out_parts.sort(key=lambda p: -p["budget"])
for i, p in enumerate(out_parts): p["rank"] = i + 1

riser = max(out_parts, key=lambda p: p["delta_last_day"])
faller = min(out_parts, key=lambda p: p["delta_last_day"])

data = {
    "title": "Breukelen-bookmaker pool",
    "subtitle": "WK 2026 \u00b7 groepsfase",
    "demo": True,
    "start_budget": START,
    "n_participants": len(out_parts),
    "n_matches": len(matches),
    "n_played": len(played),
    "last_matchday": last_daykey,
    "played_labels": played_labels,
    "participants": out_parts,
    "highlights": {
        "riser": {"name": riser["name"], "delta": riser["delta_last_day"]},
        "faller": {"name": faller["name"], "delta": faller["delta_last_day"]},
        "hot": max(out_parts, key=lambda p: p["longest_correct"]),
        "cold": max(out_parts, key=lambda p: p["longest_wrong"]),
    },
    "results": [
        {"home": m["home"], "away": m["away"], "datetime": m["datetime"],
         "h": m["result"]["home"], "a": m["result"]["away"],
         "toto": toto_of(m["result"]["home"], m["result"]["away"])}
        for m in played
    ],
    "upcoming": [
        {"home": m["home"], "away": m["away"], "datetime": m["datetime"],
         "odds": m["toto_odds"]}
        for m in matches if m["status"] == "upcoming"
    ][:8],
}

with open("data.json", "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print("Deelnemers:", len(out_parts), "| gespeeld:", len(played), "| laatste speeldag:", last_daykey)
print("Leider:", out_parts[0]["name"], out_parts[0]["budget"])
print("Hekkensluiter:", out_parts[-1]["name"], out_parts[-1]["budget"])
print("Snelste stijger:", riser["name"], riser["delta_last_day"])
print("Snelste daler:", faller["name"], faller["delta_last_day"])
print("Langste goed-streak:", data["highlights"]["hot"]["name"], data["highlights"]["hot"]["longest_correct"])
print("Langste fout-streak:", data["highlights"]["cold"]["name"], data["highlights"]["cold"]["longest_wrong"])
budgets = [p["budget"] for p in out_parts]
print("Positief gebleven:", sum(1 for x in budgets if x >= START), "/", len(budgets), "(>= start 2500)")
print("Boven nul:", sum(1 for x in budgets if x > 0), "/", len(budgets))
