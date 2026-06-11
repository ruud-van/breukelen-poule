"""
Productie-build voor de Breukelen-bookmaker pool op ECHTE data.
- leest wk_odds.json (de bevroren odds-snapshot van The Odds API)
- leest alle 58 deelnemers uit het master-Excel
- fit het correct-score model per wedstrijd
- schrijft odds.json (bevroren: toto-uitbetaling + correct-score odds met marge)
- leest results_state.json (echte, afgeronde uitslagen; leeg vóór 11 juni)
- berekent budget/standen/streaks op de ECHTE gespeelde wedstrijden
- schrijft data.json voor de pagina
"""
import json, os, statistics, datetime
import numpy as np
from odds_model import fit_match, correct_score_odds, MAXG
from odds_fetch import to_nl
from parse_all import parse_all

ODDS_RAW = "wk_odds.json"
MASTER = "WK_2026__allen_.xls"        # repo-relatief; meegecommit in de repo
RESULTS_STATE = "results_state.json"  # output van results_fetch.py (echte uitslagen)
START = 2000
STAKE_TOTO, STAKE_SCORE = 100, 20
OVERROUND_CS, LONGSHOT = 1.40, 0.12
N_SIM = 4000
GRID = 7   # correct-score odds opslaan voor 0..7 per team
np.random.seed(11)

def med(xs): return round(statistics.median(xs), 2) if xs else None
def toto_of(h, a): return "1" if h > a else ("2" if a > h else "X")
def daykey(dt): return " ".join(dt.split()[:2])

# ---- 1. consensus per wedstrijd uit de ruwe feed --------------------------
raw = json.load(open(ODDS_RAW))
cons = {}
for ev in raw:
    he, ae = ev["home_team"], ev["away_team"]
    home, away = to_nl(he), to_nl(ae)
    if not home or not away:
        print("WAARSCHUWING niet te koppelen:", he, "-", ae); continue
    H, D, A = [], [], []
    over25, under25 = [], []
    for bk in ev.get("bookmakers", []):
        for mk in bk.get("markets", []):
            if mk["key"] == "h2h":
                for o in mk["outcomes"]:
                    if o["name"] == he: H.append(o["price"])
                    elif o["name"] == ae: A.append(o["price"])
                    elif o["name"] == "Draw": D.append(o["price"])
            elif mk["key"] == "totals":
                for o in mk["outcomes"]:
                    if abs(o.get("point", 0) - 2.5) < 1e-6:
                        (over25 if o["name"] == "Over" else under25).append(o["price"])
    cons[f"{home}|{away}"] = {
        "toto": {"1": med(H), "X": med(D), "2": med(A)},
        "over": med(over25), "under": med(under25),
    }

# ---- 2. koppelen aan de 72 canonieke wedstrijden + voorspellingen ---------
matches, preds, probs = parse_all(MASTER)
if probs: print("Parser-meldingen:", probs)

unmatched = []
models = []   # per match: dict met true matrix, cs margin grid, toto payout
for m in matches:
    key = f'{m["home"]}|{m["away"]}'
    c = cons.get(key)
    if not c:
        unmatched.append(key); models.append(None); continue
    fit = fit_match(c["toto"]["1"], c["toto"]["X"], c["toto"]["2"], c["over"], c["under"])
    fair, marg = correct_score_odds(fit["matrix"], OVERROUND_CS, LONGSHOT)
    models.append({
        "matrix": fit["matrix"], "marg": marg,
        "toto_payout": c["toto"],            # echte consensus 1X2 als uitbetaling
        "resid": fit["fit_resid_max"],
    })
print("Gekoppeld:", sum(1 for x in models if x), "/ 72 | niet gekoppeld:", unmatched or "geen")

# ---- 3. odds.json bevriezen ----------------------------------------------
frozen = {"frozen_at": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "matches": {}}
for m, mm in zip(matches, models):
    if not mm: continue
    cs = {f"{i}-{j}": round(float(mm["marg"][i, j]), 2)
          for i in range(GRID + 1) for j in range(GRID + 1)}
    frozen["matches"][f'{m["home"]}|{m["away"]}'] = {
        "home": m["home"], "away": m["away"], "datetime": m["datetime"],
        "toto": mm["toto_payout"], "correct_score": cs,
    }
json.dump(frozen, open("odds.json", "w"), ensure_ascii=False, indent=1)

# ---- 4. realisme: hoe goed reproduceert het model de markt? ---------------
resids = [mm["resid"] for mm in models if mm]
print(f"\nRealisme-fit over 72 wedstrijden: max residu gem. {np.mean(resids):.2e}, "
      f"slechtste {max(resids):.2e}  (0 = perfecte reproductie van de marktkansen)")

# ---- 5. voorspellingen naar arrays ---------------------------------------
names = list(preds.keys())
P = len(names)
pred_toto = np.zeros((P, 72), int)
pred_toto_odd = np.ones((P, 72))
pred_h = np.zeros((P, 72), int); pred_a = np.zeros((P, 72), int)
pred_cs_odd = np.ones((P, 72))
idx = {"1": 0, "X": 1, "2": 2}
for pi, n in enumerate(names):
    for mi in range(72):
        mm = models[mi]
        ph, pa = preds[n].get(mi, (0, 0))
        ph, pa = min(ph, GRID), min(pa, GRID)
        pred_h[pi, mi], pred_a[pi, mi] = ph, pa
        t = toto_of(ph, pa); pred_toto[pi, mi] = idx[t]
        if mm:
            pred_toto_odd[pi, mi] = mm["toto_payout"][t]
            pred_cs_odd[pi, mi] = float(mm["marg"][ph, pa])

# ---- 6. Monte Carlo budgetsimulatie (alleen ter info, niet voor de pagina) -
flat = [(mm["matrix"].ravel() / mm["matrix"].sum()) if mm else None for mm in models]
finals = np.zeros((P, N_SIM))
for s in range(N_SIM):
    ah = np.zeros(72, int); aa = np.zeros(72, int); at = np.zeros(72, int)
    for mi in range(72):
        if flat[mi] is None:
            continue
        k = np.random.choice((MAXG + 1) ** 2, p=flat[mi])
        i, j = divmod(k, MAXG + 1)
        ah[mi], aa[mi] = i, j
        at[mi] = idx[toto_of(i, j)]
    tot_ok = pred_toto == at[None, :]
    prof = np.where(tot_ok, STAKE_TOTO * (pred_toto_odd - 1), -STAKE_TOTO)
    sc_ok = (pred_h == ah[None, :]) & (pred_a == aa[None, :])
    prof = prof + np.where(sc_ok, STAKE_SCORE * (pred_cs_odd - 1), -STAKE_SCORE)
    finals[:, s] = START + prof.sum(1)
allv = finals.ravel()
print(f"\nBudgetsimulatie ({N_SIM} toernooien, startbudget {START}):")
print(f"  mediaan eindbudget: {np.median(allv):.0f} | kans boven 0: {100*np.mean(allv>0):.1f}%")

# ---- 7. ECHTE gespeelde uitslagen inlezen --------------------------------
state = json.load(open(RESULTS_STATE)) if os.path.exists(RESULTS_STATE) else {}
# gespeelde wedstrijden in canonieke wedstrijd-volgorde (mi oplopend)
results = []
for mi, m in enumerate(matches):
    rs = state.get(f'{m["home"]}|{m["away"]}')
    if rs is not None:
        results.append((mi, int(rs["hg"]), int(rs["ag"])))

played_idx = [r[0] for r in results]
last_day = daykey(matches[played_idx[-1]]["datetime"]) if played_idx else None
played_keys = {f'{matches[mi]["home"]}|{matches[mi]["away"]}' for mi in played_idx}

# ---- 8. stand/streaks per deelnemer op de echte uitslagen ----------------
parts = []
for pi, n in enumerate(names):
    budget = START; series = [START]; seq = []; net_last = 0.0; correct = 0
    for (mi, ah, aa) in results:
        net = 0.0; at = toto_of(ah, aa); pt = ["1", "X", "2"][pred_toto[pi, mi]]
        if pt == at: net += STAKE_TOTO * (pred_toto_odd[pi, mi] - 1); correct += 1; ok = True
        else: net += -STAKE_TOTO; ok = False
        if pred_h[pi, mi] == ah and pred_a[pi, mi] == aa:
            net += STAKE_SCORE * (pred_cs_odd[pi, mi] - 1)
        else: net += -STAKE_SCORE
        budget += net; series.append(round(budget, 2)); seq.append(ok)
        if daykey(matches[mi]["datetime"]) == last_day: net_last += net
    def longest(s, v):
        b = c = 0
        for x in s:
            c = c + 1 if x == v else 0; b = max(b, c)
        return b
    cur = 0; ct = None
    for x in reversed(seq):
        if ct is None: ct = x
        if x == ct: cur += 1
        else: break
    np_played = len(results)
    parts.append({"name": n, "budget": round(budget, 2), "series": series,
                  "toto_correct": correct, "toto_played": np_played,
                  "hit_rate": round(100 * correct / np_played, 1) if np_played else 0.0,
                  "longest_correct": longest(seq, True), "longest_wrong": longest(seq, False),
                  "current_streak": cur,
                  "current_streak_type": "goed" if ct else "fout",
                  "delta_last_day": round(net_last, 2)})
parts.sort(key=lambda p: -p["budget"])
for i, p in enumerate(parts): p["rank"] = i + 1
riser = max(parts, key=lambda p: p["delta_last_day"])
faller = min(parts, key=lambda p: p["delta_last_day"])

# odds (toto-uitbetaling + correct-score 0..5) per wedstrijd, voor de hover-popover
CS_MAX = 5
def _odds_for(m):
    fm = frozen["matches"].get(f'{m["home"]}|{m["away"]}')
    if not fm:
        return None
    cs = {k: v for k, v in fm["correct_score"].items()
          if int(k.split("-")[0]) <= CS_MAX and int(k.split("-")[1]) <= CS_MAX}
    return {"toto": fm["toto"], "cs": cs}

# ---- 9. data.json voor de pagina -----------------------------------------
data = {
    "title": "Breukelen-bookmaker poule", "subtitle": "WK 2026 · groepsfase",
    "demo": False,
    "demo_note": "echte deelnemers, echte odds en echte uitslagen",
    "start_budget": START, "n_participants": len(parts), "n_matches": 72,
    "n_played": len(results), "last_matchday": last_day,
    "played_labels": [f'{matches[mi]["home"]}-{matches[mi]["away"]}' for mi in played_idx],
    "participants": parts,
    "highlights": {"riser": {"name": riser["name"], "delta": riser["delta_last_day"]},
                   "faller": {"name": faller["name"], "delta": faller["delta_last_day"]},
                   "hot": max(parts, key=lambda p: p["longest_correct"]),
                   "cold": max(parts, key=lambda p: p["longest_wrong"])},
    "results": [{"home": matches[mi]["home"], "away": matches[mi]["away"],
                 "datetime": matches[mi]["datetime"], "h": ah, "a": aa,
                 "toto": toto_of(ah, aa),
                 "odds": _odds_for(matches[mi])}
                for (mi, ah, aa) in results],
    "upcoming": [{"home": matches[mi]["home"], "away": matches[mi]["away"],
                  "datetime": matches[mi]["datetime"],
                  "odds": _odds_for(matches[mi])}
                 for mi in range(72)
                 if f'{matches[mi]["home"]}|{matches[mi]["away"]}' in frozen["matches"]
                 and f'{matches[mi]["home"]}|{matches[mi]["away"]}' not in played_keys][:8],
}
# ---- 10. voorspellingen per wedstrijd (voor het 'Voorspellingen'-tabblad) --
# wedstrijden in canonieke (= chronologische schema-)volgorde; per wedstrijd
# alle deelnemers met hun voorspelde score, plus de echte uitslag indien gespeeld.
played_map = {mi: (ah, aa) for (mi, ah, aa) in results}
predictions = []
for mi, m in enumerate(matches):
    entry = {"home": m["home"], "away": m["away"], "datetime": m["datetime"],
             "played": mi in played_map}
    if mi in played_map:
        ah, aa = played_map[mi]
        entry.update({"h": ah, "a": aa, "toto": toto_of(ah, aa)})
    entry["preds"] = [{"n": n, "h": int(pred_h[pi, mi]), "a": int(pred_a[pi, mi])}
                      for pi, n in enumerate(names)]
    predictions.append(entry)
data["predictions"] = predictions

# ---- 11. gelijkenis-matrices (toto + exacte score) ------------------------
# per paar deelnemers: % wedstrijden met dezelfde toto (1/X/2) resp. exacte score.
# Namen geordend via hiërarchische clustering zodat gelijkende mensen naast
# elkaar komen (rode blokken in de heatmap).
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import squareform

def _order(sim):
    if len(sim) < 3:
        return list(range(len(sim)))
    d = 1.0 - sim
    np.fill_diagonal(d, 0.0)
    d = (d + d.T) / 2
    return [int(i) for i in leaves_list(linkage(squareform(d, checks=False), method="average"))]

toto_sim = (pred_toto[:, None, :] == pred_toto[None, :, :]).mean(2)
score_sim = ((pred_h[:, None, :] == pred_h[None, :, :]) &
             (pred_a[:, None, :] == pred_a[None, :, :])).mean(2)

def _pack(sim):
    order = _order(sim)
    return {"names": [names[i] for i in order],
            "matrix": [[int(round(100 * sim[i, j])) for j in order] for i in order]}

data["similarity"] = {"toto": _pack(toto_sim), "score": _pack(score_sim)}

json.dump(data, open("data.json", "w"), ensure_ascii=False, indent=1)
print(f"\ndata.json geschreven. Gespeeld: {len(results)}/72.",
      ("Leider: %s %.0f | hekkensluiter: %s %.0f"
       % (parts[0]["name"], parts[0]["budget"], parts[-1]["name"], parts[-1]["budget"]))
      if results else "(nog geen wedstrijden gespeeld; iedereen staat op start.)")
