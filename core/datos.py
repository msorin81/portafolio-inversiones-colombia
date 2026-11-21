"""
Descarga y preparación de datos de precios.

- Datos reales: Yahoo Finance (yfinance).
- Conversión de moneda: todos los precios se expresan en la moneda base
  elegida (COP o USD) usando la tasa USD/COP (ticker 'COP=X').
- Respaldo: si no hay internet, se generan precios simulados con los
  parámetros del script original (rendimientos, volatilidades y correlaciones).
"""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

TICKER_FX = "COP=X"  # pesos colombianos por 1 dólar
ARCHIVO_SNAPSHOT = "data/precios.csv"  # respaldo diario generado por GitHub Actions

# ── Universo de activos sugeridos ─────────────────────────────────────────
# moneda: moneda en la que cotiza el activo
UNIVERSO: dict[str, dict] = {
    # Renta variable global / EE.UU.
    "VT":   dict(nombre="Acciones de todo el mundo", clase="Renta variable", moneda="USD",
                 desc="ETF con ~9.000 empresas de más de 40 países. La forma más simple de diversificar."),
    "SPY":  dict(nombre="S&P 500 (EE.UU.)", clase="Renta variable", moneda="USD",
                 desc="Las 500 empresas más grandes de EE.UU. Referencia del mercado mundial."),
    "VOO":  dict(nombre="S&P 500 (Vanguard, bajo costo)", clase="Renta variable", moneda="USD",
                 desc="Mismo índice que SPY pero con comisión anual más baja (0,03%)."),
    "QQQ":  dict(nombre="Nasdaq 100 (Tecnología)", clase="Renta variable", moneda="USD",
                 desc="100 grandes empresas no financieras del Nasdaq, muy concentrado en tecnología."),
    "VWO":  dict(nombre="Mercados emergentes", clase="Renta variable", moneda="USD",
                 desc="Empresas de China, India, Taiwán, Brasil, etc. Más riesgo y potencial."),
    # Colombia
    "ICOLCAP.CL": dict(nombre="ETF índice COLCAP (BVC)", clase="Renta variable Colombia", moneda="COP",
                       desc="ETF local que replica las acciones más líquidas de la Bolsa de Colombia. Se compra en pesos."),
    "COLO": dict(nombre="Global X MSCI Colombia", clase="Renta variable Colombia", moneda="USD",
                 desc="ETF de empresas colombianas que cotiza en EE.UU. (antes GXG)."),
    "EC":   dict(nombre="Ecopetrol (ADR)", clase="Acción individual", moneda="USD",
                 desc="Acción de Ecopetrol negociada en Nueva York. Riesgo concentrado en una empresa."),
    "CIB":  dict(nombre="Grupo Cibest / Bancolombia (ADR)", clase="Acción individual", moneda="USD",
                 desc="Acción del mayor grupo bancario colombiano negociada en Nueva York."),
    # Renta fija
    "BND":  dict(nombre="Bonos EE.UU. (total mercado)", clase="Renta fija", moneda="USD",
                 desc="Bonos del gobierno y empresas de EE.UU. Amortigua caídas de las acciones."),
    "IEF":  dict(nombre="Bonos del Tesoro 7-10 años", clase="Renta fija", moneda="USD",
                 desc="Bonos del gobierno de EE.UU. de plazo medio."),
    "TLT":  dict(nombre="Bonos del Tesoro +20 años", clase="Renta fija", moneda="USD",
                 desc="Bonos de largo plazo: muy sensibles a las tasas de interés (cayeron fuerte en 2022)."),
    "SHY":  dict(nombre="Bonos del Tesoro 1-3 años", clase="Renta fija", moneda="USD",
                 desc="Bonos de corto plazo, muy baja volatilidad. Similar a 'efectivo en dólares'."),
    # Alternativos
    "GLD":  dict(nombre="Oro", clase="Materias primas", moneda="USD",
                 desc="Oro físico. Refugio en crisis; no paga dividendos."),
    "VNQ":  dict(nombre="Bienes raíces EE.UU. (REITs)", clase="Inmobiliario", moneda="USD",
                 desc="Empresas dueñas de inmuebles que reparten rentas. Invertir en finca raíz con poco dinero."),
}

TICKERS_DEFECTO = ["SPY", "QQQ", "VWO", "ICOLCAP.CL", "BND", "GLD", "VNQ"]

# ── Parámetros del script original (para el modo simulado) ────────────────
_SIM_REND_ANUALES = {  # 2021-2025, %
    "SPY": [28.7, -18.1, 26.3, 25.0, 2.0],
    "QQQ": [26.9, -32.8, 53.5, 26.7, -13.5],
    "VWO": [1.0, -17.7, 9.3, 11.0, 5.0],
    "GLD": [-3.6, -0.8, 13.5, 27.0, 14.0],
    "TLT": [-4.6, -31.2, -2.8, -8.0, 3.0],
    "VNQ": [40.4, -26.2, -4.7, 12.0, 3.0],
}
_SIM_VOL = {"SPY": 17.5, "QQQ": 23.0, "VWO": 18.0, "GLD": 15.0, "TLT": 17.0, "VNQ": 22.0}
_SIM_CORR = np.array([
    [1.00, 0.90, 0.70, 0.05, -0.30, 0.75],
    [0.90, 1.00, 0.65, 0.00, -0.35, 0.65],
    [0.70, 0.65, 1.00, 0.20, -0.15, 0.60],
    [0.05, 0.00, 0.20, 1.00, 0.40, -0.05],
    [-0.30, -0.35, -0.15, 0.40, 1.00, -0.10],
    [0.75, 0.65, 0.60, -0.05, -0.10, 1.00],
])
SIM_TICKERS = list(_SIM_VOL.keys())


def moneda_de(ticker: str) -> str:
    if ticker in UNIVERSO:
        return UNIVERSO[ticker]["moneda"]
    return "COP" if ticker.upper().endswith(".CL") else "USD"


def _limpiar_fx(fx: pd.Series) -> pd.Series:
    """Yahoo a veces trae saltos erróneos en COP=X: se eliminan cambios diarios >8%."""
    fx = fx.dropna()
    salto = fx.pct_change().abs()
    fx = fx.mask(salto > 0.08)
    return fx.ffill()


def descargar_precios(tickers: list[str], anios: int) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Descarga precios ajustados (con dividendos) en moneda nativa + USD/COP.

    Retorna (precios_nativos, fx, tickers_fallidos).
    """
    import yfinance as yf

    fin = datetime.now()
    inicio = fin - timedelta(days=int(anios * 365.25) + 10)
    lista = sorted(set(tickers) | {TICKER_FX})
    data = yf.download(lista, start=inicio, end=fin, auto_adjust=True,
                       progress=False, threads=True)
    if data is None or data.empty:
        raise ConnectionError("Yahoo Finance no devolvió datos.")
    cierre = data["Close"] if isinstance(data.columns, pd.MultiIndex) else data[["Close"]]
    if isinstance(cierre, pd.Series):
        cierre = cierre.to_frame(lista[0])
    cierre.index = pd.to_datetime(cierre.index).tz_localize(None)

    if TICKER_FX not in cierre or cierre[TICKER_FX].dropna().empty:
        raise ConnectionError("No se pudo descargar la tasa de cambio USD/COP.")
    fx = _limpiar_fx(cierre[TICKER_FX])

    precios = cierre.drop(columns=[TICKER_FX])
    minimo = 0.6 * len(precios)  # el activo debe tener al menos 60% de los días
    fallidos = [t for t in tickers if t not in precios or precios[t].notna().sum() < minimo]
    precios = precios[[t for t in tickers if t not in fallidos]]
    return precios, fx, fallidos


def cargar_snapshot(ruta, tickers: list[str], anios: int) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Lee el respaldo diario (data/precios.csv). Mismo formato que descargar_precios()."""
    tabla = pd.read_csv(ruta, index_col=0, parse_dates=True)
    inicio = tabla.index[-1] - pd.Timedelta(days=int(anios * 365.25))
    tabla = tabla[tabla.index >= inicio]
    fx = _limpiar_fx(tabla[TICKER_FX])
    minimo = 0.6 * len(tabla)
    fallidos = [t for t in tickers if t not in tabla or tabla[t].notna().sum() < minimo]
    return tabla[[t for t in tickers if t not in fallidos]], fx, fallidos


def convertir_moneda(precios: pd.DataFrame, fx: pd.Series, base: str) -> pd.DataFrame:
    """Expresa todos los precios en la moneda base (COP o USD)."""
    fx = fx.reindex(precios.index).ffill().bfill()
    salida = precios.copy()
    for t in precios.columns:
        m = moneda_de(t)
        if base == "COP" and m == "USD":
            salida[t] = precios[t] * fx
        elif base == "USD" and m == "COP":
            salida[t] = precios[t] / fx
    # calendarios distintos (BVC vs NYSE): rellenar festivos con el último precio
    salida = salida.ffill().dropna()
    return salida


def precios_simulados(anios: int = 5, semilla: int = 42) -> pd.DataFrame:
    """Respaldo sin internet: precios sintéticos con parámetros reales (script original)."""
    rng = np.random.default_rng(semilla)
    n_dias = 252 * anios
    mu = np.array([np.mean(_SIM_REND_ANUALES[t]) / 100 / 252 for t in SIM_TICKERS])
    sig = np.array([_SIM_VOL[t] / 100 / np.sqrt(252) for t in SIM_TICKERS])
    cov = np.diag(sig) @ _SIM_CORR @ np.diag(sig)
    L = np.linalg.cholesky(cov)
    r = rng.standard_normal((n_dias, len(SIM_TICKERS))) @ L.T + mu
    base = np.array([450, 380, 50, 170, 150, 100], dtype=float)
    precios = base * np.cumprod(1 + r, axis=0)
    fechas = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n_dias)
    return pd.DataFrame(precios, index=fechas, columns=SIM_TICKERS)
