"""Métricas de rendimiento y riesgo."""
from __future__ import annotations

import numpy as np
import pandas as pd

DIAS = 252


def rendimientos(precios: pd.DataFrame) -> pd.DataFrame:
    return precios.pct_change().dropna(how="all").fillna(0.0)


def metricas_serie(r: pd.Series, rf: float) -> dict:
    """Métricas de una serie de rendimientos diarios. rf = tasa libre de riesgo anual (decimal)."""
    r = r.dropna()
    n = len(r)
    if n < 20:
        return {}
    riqueza = (1 + r).cumprod()
    cagr = riqueza.iloc[-1] ** (DIAS / n) - 1
    vol = r.std() * np.sqrt(DIAS)
    neg = r[r < 0]
    vol_neg = neg.std() * np.sqrt(DIAS) if len(neg) > 1 else np.nan
    dd = riqueza / riqueza.cummax() - 1
    mensual = (1 + r).resample("ME").prod() - 1
    anual = (1 + r).resample("YE").prod() - 1
    var95 = -np.percentile(mensual, 5) if len(mensual) > 5 else np.nan
    cvar95 = -mensual[mensual <= -var95].mean() if len(mensual) > 5 else np.nan
    return {
        "Rend. anual (CAGR)": cagr,
        "Volatilidad": vol,
        "Sharpe": (cagr - rf) / vol if vol > 0 else np.nan,
        "Sortino": (cagr - rf) / vol_neg if vol_neg and vol_neg > 0 else np.nan,
        "Máx. caída": dd.min(),
        "Calmar": cagr / abs(dd.min()) if dd.min() < 0 else np.nan,
        "VaR 95% mensual": var95,
        "CVaR 95% mensual": cvar95,
        "Meses positivos": (mensual > 0).mean(),
        "Mejor año": anual.max(),
        "Peor año": anual.min(),
        "Rend. acumulado": riqueza.iloc[-1] - 1,
    }


def tabla_metricas(rend: pd.DataFrame, rf: float) -> pd.DataFrame:
    return pd.DataFrame({c: metricas_serie(rend[c], rf) for c in rend.columns}).T


def drawdown(r: pd.Series) -> pd.Series:
    riqueza = (1 + r).cumprod()
    return riqueza / riqueza.cummax() - 1


def rend_anuales(precios: pd.DataFrame) -> pd.DataFrame:
    anual = precios.resample("YE").last()
    primero = precios.iloc[[0]]
    anual = pd.concat([primero, anual])
    out = anual.pct_change().dropna(how="all")
    out.index = out.index.year
    out = out[~out.index.duplicated(keep="last")]
    return out
