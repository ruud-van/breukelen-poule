import json, statistics
import numpy as np
from odds_model import fit_match, correct_score_odds, MAXG
from odds_fetch import to_nl
from parse_all import parse_all

np.random.seed(3)
raw = json.load(open("wk_odds.json"))
def med(xs): return statistics.median(xs) if xs else None
def toto_of(h, a): return "1" if h > a else ("2" if a > h else "X")
idx = {"1": 0, "X": 1, "2": 2}

cons = {}
for ev in raw:
    he, ae = ev["home_team"], ev["away_team"]; home, away = to_nl(he), to_nl(ae)
    if not home or not away: continue
    H, D, A, ov, un = [], [], [], [], []
    for bk in ev.get("bookmakers", []):
        for mk in bk.get("markets", []):
            if mk["key"] == "h2h":
                for o in mk["outcomes"]:
                    if o["name"] == he: H.append(o["price"])
                    elif o["name"] == ae: A.append(o["price"])
                    elif o["name"] == "Draw": D.append(o["price"])
            elif mk["key"] == "totals":
                for o in mk["outcomes"]:
                    if abs(o.get("point",0)-2.5) < 1e-6:
                        (ov if o["name"]=="Over" else un).append(o["price"])
    cons[f"{home}|{away}"] = (med(H), med(D), med(A), med(ov), med(un))

matches, preds, _ = parse_all("/mnt/user-data/uploads/WK_2026__allen_.xls")
mats, totopay = [], []
for m in matches:
    o1, ox, o2, oo, ou = cons[f'{m["home"]}|{m["away"]}']
    fit = fit_match(o1, ox, o2, oo, ou)
    mats.append(fit["matrix"]); totopay.append({"1": o1, "X": ox, "2": o2})

# toto-overround check
orr = [1/t["1"]+1/t["X"]+1/t["2"] for t in totopay]
print(f"Consensus toto-overround: gem. {100*np.mean(orr):.1f}% (onder 100% = licht in voordeel speler)\n")

names = list(preds); P = len(names)
pt = np.zeros((P,72),int); ph = np.zeros((P,72),int); pa = np.zeros((P,72),int)
toto_odd = np.ones((P,72))
for pi,n in enumerate(names):
    for mi in range(72):
        h,a = preds[n].get(mi,(0,0)); h,a=min(h,7),min(a,7)
        ph[pi,mi],pa[pi,mi]=h,a; t=toto_of(h,a); pt[pi,mi]=idx[t]
        toto_odd[pi,mi]=totopay[mi][t]

# vaste set gesimuleerde uitslagen, hergebruikt over scenario's
N=1500
flat=[mm.ravel()/mm.sum() for mm in mats]
AH=np.zeros((N,72),int); AA=np.zeros((N,72),int); AT=np.zeros((N,72),int)
for s in range(N):
    for mi in range(72):
        k=np.random.choice((MAXG+1)**2,p=flat[mi]); i,j=divmod(k,MAXG+1)
        AH[s,mi],AA[s,mi]=i,j; AT[s,mi]=idx[toto_of(i,j)]

def sim(margin, stake_score, stake_toto=100):
    cs=[correct_score_odds(mm,margin,0.12)[1] for mm in mats]
    cs_odd=np.ones((P,72))
    for pi in range(P):
        for mi in range(72): cs_odd[pi,mi]=cs[mi][ph[pi,mi],pa[pi,mi]]
    net=np.zeros((P,N))
    for s in range(N):
        tok = pt==AT[s][None,:]
        pr=np.where(tok, stake_toto*(toto_odd-1), -stake_toto)
        sok=(ph==AH[s][None,:])&(pa==AA[s][None,:])
        pr=pr+np.where(sok, stake_score*(cs_odd-1), -stake_score)
        net[:,s]=pr.sum(1)
    return net.ravel()

print(f"{'scenario':32}{'mediaan net':>12}{'5e pct':>9}{'→ start v. 90% boven 0':>26}")
for label, margin, ss in [
    ("marge 40%, score-inzet 50 (nu)", 1.40, 50),
    ("marge 40%, score-inzet 25",      1.40, 25),
    ("marge 20%, score-inzet 50",      1.20, 50),
    ("marge 10%, score-inzet 50",      1.10, 50),
    ("marge 20%, score-inzet 25",      1.20, 25),
]:
    net = sim(margin, ss)
    p10 = np.percentile(net,10)   # start zo dat 90% boven 0 blijft = -p10
    print(f"{label:32}{np.median(net):>12.0f}{np.percentile(net,5):>9.0f}{(-p10):>20.0f}")
