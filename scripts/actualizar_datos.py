"""
Descarga diaria de precios (la ejecuta GitHub Actions cada día hábil).

Guarda en data/precios.csv los precios de cierre ajustados (moneda nativa)
de todo el universo de activos + la tasa USD/COP, para que la app funcione
aunque Yahoo Finance bloquee la descarga en vivo desde la nube.

Uso local:  python scripts/actualizar_datos.py
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402

from core.datos import ARCHIVO_SNAPSHOT, TICKER_FX, UNIVERSO, descargar_precios  # noqa: E402

ANIOS = 10


def main() -> int:
    tickers = list(UNIVERSO)
    precios, fx, fallidos = descargar_precios(tickers, ANIOS)
    if precios.empty or fx.dropna().empty:
        print("ERROR: no se descargaron datos; se conserva el archivo anterior.")
        return 1
    tabla = precios.copy()
    tabla[TICKER_FX] = fx.reindex(tabla.index).ffill()
    tabla.index.name = "Fecha"

    destino = RAIZ / ARCHIVO_SNAPSHOT
    destino.parent.mkdir(exist_ok=True)
    # Si hoy falló algún activo, conservar su historia anterior
    if fallidos and destino.exists():
        previo = pd.read_csv(destino, index_col=0, parse_dates=True)
        for t in fallidos:
            if t in previo:
                tabla[t] = previo[t].reindex(tabla.index)
    tabla.round(4).to_csv(destino)
    (destino.parent / "ultima_actualizacion.txt").write_text(
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), encoding="utf-8")
    print(f"OK: {tabla.shape[0]} días × {tabla.shape[1]} series hasta {tabla.index[-1]:%Y-%m-%d}."
          + (f" Fallidos hoy: {fallidos}" if fallidos else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
