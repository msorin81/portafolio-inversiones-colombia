"""
Optimización de portafolios (Markowitz y variantes) con scipy.

Reemplaza a PyPortfolioOpt para no depender de cvxpy y permitir
límites de peso por activo (evita portafolios concentrados en 1-2 activos).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize

DIAS = 252


def parametros(rend: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Rendimiento esperado anual (media aritmética) y covarianza anual."""
    mu = rend.mean().values * DIAS
    cov = rend.cov().values * DIAS
    return mu, cov


def desempeno(w, mu, cov, rf):
    ret = float(w @ mu)
    vol = float(np.sqrt(w @ cov @ w))
    return ret, vol, (ret - rf) / vol if vol > 0 else np.nan


def _resolver(objetivo, n, tope, extra=()):
    tope = max(tope, 1.0 / n + 1e-9)
    res = minimize(objetivo, np.ones(n) / n, method="SLSQP",
                   bounds=[(0.0, tope)] * n,
                   constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}, *extra],
                   options={"maxiter": 1000, "ftol": 1e-12})
    w = np.clip(res.x, 0, None)
    w[w < 1e-4] = 0
    return w / w.sum()


def max_sharpe(mu, cov, rf, tope=1.0):
    return _resolver(lambda w: -(w @ mu - rf) / np.sqrt(w @ cov @ w), len(mu), tope)


def min_volatilidad(mu, cov, tope=1.0):
    return _resolver(lambda w: w @ cov @ w, len(mu), tope)


def max_retorno_con_volatilidad(mu, cov, vol_objetivo, tope=1.0):
    """Máximo rendimiento sin superar la volatilidad que tolera tu perfil.
    Si no es posible, devuelve el portafolio de mínima volatilidad."""
    w_min = min_volatilidad(mu, cov, tope)
    if np.sqrt(w_min @ cov @ w_min) >= vol_objetivo:
        return w_min, False
    restr = {"type": "ineq", "fun": lambda w: vol_objetivo ** 2 - w @ cov @ w}
    return _resolver(lambda w: -(w @ mu), len(mu), tope, extra=(restr,)), True


def paridad_riesgo(cov, tope=1.0):
    """Cada activo aporta el mismo riesgo al portafolio."""
    n = cov.shape[0]

    def obj(w):
        var = w @ cov @ w
        contrib = w * (cov @ w) / var
        return ((contrib - 1 / n) ** 2).sum() * 1e3

    return _resolver(obj, n, tope)


def contribucion_riesgo(w, cov):
    var = w @ cov @ w
    return w * (cov @ w) / var


def frontera_eficiente(mu, cov, tope=1.0, puntos=40):
    n = len(mu)
    w_min = min_volatilidad(mu, cov, tope)
    w_max = _resolver(lambda w: -(w @ mu), n, tope)
    r_min, r_max = w_min @ mu, w_max @ mu
    vols, rets = [], []
    for objetivo in np.linspace(r_min, r_max, puntos):
        restr = {"type": "eq", "fun": lambda w, o=objetivo: w @ mu - o}
        w = _resolver(lambda w: w @ cov @ w, n, tope, extra=(restr,))
        vols.append(np.sqrt(w @ cov @ w))
        rets.append(w @ mu)
    return np.array(vols), np.array(rets)


def portafolios_aleatorios(mu, cov, rf, n=4000, semilla=42):
    rng = np.random.default_rng(semilla)
    W = rng.dirichlet(np.ones(len(mu)) * 0.7, size=n)
    rets = W @ mu
    vols = np.sqrt(np.einsum("ij,jk,ik->i", W, cov, W))
    return vols, rets, (rets - rf) / vols
