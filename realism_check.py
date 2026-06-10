"""
Uitgebreide realiteitscheck op het correct-score odds-model.
Draait op drie representatieve wedstrijdtypes met plausibele input-odds.
"""
import numpy as np
from odds_model import (fit_match, correct_score_odds, toto_odds, top_scores,
                        score_matrix, model_probs)

np.set_printoptions(suppress=True)

CASES = {
    "Zware favoriet (bv. Frankrijk-Irak)":
        dict(o1=1.10, ox=9.5, o2=26.0, o_over=1.55, o_under=2.45),
    "Middenmoot-favoriet (bv. Nederland-Japan)":
        dict(o1=1.62, ox=4.10, o2=5.40, o_over=1.85, o_under=1.95),
    "Gelijkwaardig (bv. Brazilie-Marokko)":
        dict(o1=2.55, ox=3.30, o2=2.75, o_over=1.90, o_under=1.90),
}

OVERROUND = 1.40   # 40% marge op correct-score, zoals een echte boekmaker
LONGSHOT = 0.12    # lichte longshot-bias

def fmt_pct(x): return f"{100*x:5.1f}%"

for name, mkt in CASES.items():
    print("=" * 74)
    print(name)
    print("-" * 74)
    fit = fit_match(**mkt)
    print(f"  Verwachte goals: thuis lambda={fit['lambda_home']:.2f}  "
          f"uit lambda={fit['lambda_away']:.2f}  rho={fit['rho']:+.3f}")
    print(f"  Max fit-residu op de inputmarkten: {fit['fit_resid_max']:.2e}  "
          f"(0 = perfecte reproductie)")
    t, m = fit["target"], fit["model"]
    print("  Interne consistentie (de-vigde input  vs  uit model teruggerekend):")
    for k, lab in [("p1","thuiswinst"),("pX","gelijk"),("p2","uitwinst"),("pOver","over 2.5")]:
        print(f"    {lab:12} input {fmt_pct(t[k])}   model {fmt_pct(m[k])}")

    fair, marg = correct_score_odds(fit["matrix"], overround=OVERROUND, longshot_bias=LONGSHOT)
    print(f"  Toto-odds (1X2, ~6% marge): "
          f"1 {toto_odds(fit)[0]:.2f} | X {toto_odds(fit)[1]:.2f} | 2 {toto_odds(fit)[2]:.2f}")
    print("  Meest waarschijnlijke uitslagen  (kans | faire odd | odd met marge):")
    for i, j, p, fo, mo in top_scores(fit["matrix"], fair, marg, n=7):
        print(f"    {i}-{j}   {fmt_pct(p)}   fair {fo:6.2f}   markt {mo:6.2f}")
    # overround-controle
    implied = (1.0/marg)
    print(f"  Gerealiseerde overround op correct-score markt: "
          f"{100*implied.sum():.0f}%  (doel {100*OVERROUND:.0f}%)")

print("=" * 74)
print("DIXON-COLES EFFECT  (gelijkwaardige wedstrijd, lage uitslagen)")
print("-" * 74)
mkt = CASES["Gelijkwaardig (bv. Brazilie-Marokko)"]
fit = fit_match(**mkt)
lam, mu = fit["lambda_home"], fit["lambda_away"]
M_dc = score_matrix(lam, mu, fit["rho"])
M_indep = score_matrix(lam, mu, 0.0)
for (i, j) in [(0,0),(1,0),(0,1),(1,1),(2,1)]:
    print(f"    {i}-{j}:  zuiver Poisson {fmt_pct(M_indep[i,j])}   "
          f"met DC-correctie {fmt_pct(M_dc[i,j])}   "
          f"verschil {100*(M_dc[i,j]-M_indep[i,j]):+.1f}pp")

print("=" * 74)
print("GEVOELIGHEID  (over/under-lijn 0.25 verschuiven, effect op odd 1-1)")
print("-" * 74)
base = CASES["Middenmoot-favoriet (bv. Nederland-Japan)"]
for shift, label in [(0.0,"basis"), (-0.10,"meer goals verwacht"), (0.10,"minder goals verwacht")]:
    mkt2 = dict(base); mkt2["o_over"] = base["o_over"] + shift; mkt2["o_under"] = base["o_under"] - shift
    f2 = fit_match(**mkt2)
    fair2, marg2 = correct_score_odds(f2["matrix"], overround=OVERROUND, longshot_bias=LONGSHOT)
    print(f"    {label:24}  lambda_tot {f2['lambda_home']+f2['lambda_away']:.2f}   "
          f"odd 1-1 = {marg2[1,1]:.2f}   odd 1-0 = {marg2[1,0]:.2f}")
