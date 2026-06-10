"""
Correct-score odds model voor de Breukelen-bookmaker pool.

Input per wedstrijd: 1X2 decimale odds + over/under 2.5 decimale odds.
Output: een volledige scorematrix met faire odds en odds-met-marge per uitslag,
plus de toto (1X2) odds die we voor de 100-euro inzet gebruiken.

Aanpak: Dixon-Coles aangepaste (bivariate) Poisson. We de-viggen de inputmarkten,
fitten lambda_home, lambda_away en de DC-correctieparameter rho zo dat het model
de de-vigde 1X2-kansen en de over/under-kans reproduceert, en lezen daarna de
scorekansen af.
"""
import numpy as np
from scipy.optimize import least_squares
from math import exp, factorial

MAXG = 10  # goals 0..10 per team in de matrix


def devig_1x2(o1, ox, o2):
    inv = np.array([1.0 / o1, 1.0 / ox, 1.0 / o2])
    return inv / inv.sum()  # p_home, p_draw, p_away


def devig_ou(o_over, o_under):
    inv = np.array([1.0 / o_over, 1.0 / o_under])
    p = inv / inv.sum()
    return p[0], p[1]  # p_over25, p_under25


def _pois(k, lam):
    return exp(-lam) * lam ** k / factorial(k)


def dc_tau(i, j, lam, mu, rho):
    """Dixon-Coles low-score correction factor."""
    if i == 0 and j == 0:
        return 1.0 - lam * mu * rho
    if i == 0 and j == 1:
        return 1.0 + lam * rho
    if i == 1 and j == 0:
        return 1.0 + mu * rho
    if i == 1 and j == 1:
        return 1.0 - rho
    return 1.0


def score_matrix(lam, mu, rho):
    M = np.zeros((MAXG + 1, MAXG + 1))
    for i in range(MAXG + 1):
        for j in range(MAXG + 1):
            M[i, j] = _pois(i, lam) * _pois(j, mu) * dc_tau(i, j, lam, mu, rho)
    M = np.clip(M, 1e-12, None)
    return M / M.sum()


def model_probs(lam, mu, rho):
    M = score_matrix(lam, mu, rho)
    p_home = np.tril(M, -1).sum()   # i > j
    p_away = np.triu(M, 1).sum()    # j > i
    p_draw = np.trace(M)
    # over/under 2.5: totaal goals >= 3
    p_over = sum(M[i, j] for i in range(MAXG + 1) for j in range(MAXG + 1) if i + j >= 3)
    p_under = 1.0 - p_over
    return p_home, p_draw, p_away, p_over, p_under, M


def fit_match(o1, ox, o2, o_over=None, o_under=None):
    p1, pX, p2 = devig_1x2(o1, ox, o2)
    has_tot = o_over is not None and o_under is not None
    pOver = pUnder = None
    if has_tot:
        pOver, pUnder = devig_ou(o_over, o_under)
        targets = np.array([p1, pX, p2, pOver])
        def resid(params):
            lam, mu, rho = params
            lam = max(lam, 1e-3); mu = max(mu, 1e-3)
            ph, pd, pa, po, pu, _ = model_probs(lam, mu, rho)
            return np.array([ph, pd, pa, po]) - targets
        sol = least_squares(resid, np.array([1.4, 1.1, -0.05]),
                            bounds=([0.05, 0.05, -0.2], [6.0, 6.0, 0.2]),
                            xtol=1e-12, ftol=1e-12)
        lam, mu, rho = sol.x
    else:
        rho = -0.03
        targets = np.array([p1, pX, p2])
        def resid(params):
            lam, mu = params
            lam = max(lam, 1e-3); mu = max(mu, 1e-3)
            ph, pd, pa, po, pu, _ = model_probs(lam, mu, rho)
            return np.array([ph, pd, pa]) - targets
        sol = least_squares(resid, np.array([1.4, 1.1]),
                            bounds=([0.05, 0.05], [6.0, 6.0]), xtol=1e-12, ftol=1e-12)
        lam, mu = sol.x
    ph, pd, pa, po, pu, M = model_probs(lam, mu, rho)
    return {
        "lambda_home": lam, "lambda_away": mu, "rho": rho,
        "fit_resid_max": float(np.max(np.abs(sol.fun))),
        "target": {"p1": p1, "pX": pX, "p2": p2, "pOver": pOver, "pUnder": pUnder},
        "model": {"p1": ph, "pX": pd, "p2": pa, "pOver": po, "pUnder": pu},
        "matrix": M,
    }


def correct_score_odds(M, overround=1.40, longshot_bias=0.0):
    """
    Zet scorekansen om in odds.
    overround = som van impliciete kansen die je nastreeft (1.40 = 40% marge).
    longshot_bias > 0 laadt relatief meer marge op onwaarschijnlijke uitslagen,
    zoals echte boekmakers doen. 0 = vlakke (proportionele) marge.
    """
    p = M.copy()
    if longshot_bias > 0:
        w = p ** (1.0 - longshot_bias)        # comprimeer richting gelijk
        w = w / w.sum()
        q = w * overround
    else:
        q = p * overround
    fair = 1.0 / np.clip(p, 1e-9, None)
    marg = 1.0 / np.clip(q, 1e-9, None)
    return fair, marg


def toto_odds(fit, overround=1.06):
    """1X2 odds met realistische marge (~6%) uit de model-toto-kansen."""
    p = np.array([fit["model"]["p1"], fit["model"]["pX"], fit["model"]["p2"]])
    q = p * overround
    return (1.0 / q).tolist()


def top_scores(M, fair, marg, n=8):
    idx = np.dstack(np.unravel_index(np.argsort(-M.ravel()), M.shape))[0][:n]
    out = []
    for i, j in idx:
        out.append((int(i), int(j), float(M[i, j]), float(fair[i, j]), float(marg[i, j])))
    return out
