"""Proyección Monte Carlo con aportes mensuales y comparación con renta fija."""
from __future__ import annotations

import numpy as np
import pandas as pd


def stats_mensuales(r_diario: pd.Series) -> tuple[float, float]:
    """Media y desviación de los rendimientos logarítmicos mensuales."""
    lr = np.log1p(r_diario).resample("ME").sum()
    lr = lr.iloc[1:-1] if len(lr) > 6 else lr  # meses incompletos fuera
    return float(lr.mean()), float(lr.std())


def simular(capital, aporte, anios, mu_log_m, sigma_m, n=5000, semilla=42):
    """Matriz (meses+1, n) con el valor del portafolio mes a mes.
    El aporte se hace al final de cada mes."""
    rng = np.random.default_rng(semilla)
    meses = int(anios * 12)
    choques = np.exp(rng.normal(mu_log_m, sigma_m, size=(meses, n)))
    valores = np.empty((meses + 1, n))
    valores[0] = capital
    for t in range(1, meses + 1):
        valores[t] = valores[t - 1] * choques[t - 1] + aporte
    return valores


def proyeccion_fija(capital, aporte, anios, tasa_ea):
    """Crecimiento con una tasa fija efectiva anual (p. ej. CDT)."""
    meses = int(anios * 12)
    tm = (1 + tasa_ea) ** (1 / 12) - 1
    v = np.empty(meses + 1)
    v[0] = capital
    for t in range(1, meses + 1):
        v[t] = v[t - 1] * (1 + tm) + aporte
    return v


def aportado(capital, aporte, anios):
    return capital + aporte * np.arange(int(anios * 12) + 1)
