# 📈 Mi Portafolio Inteligente

Herramienta educativa en Streamlit para analizar, construir y proyectar un portafolio de inversión desde Colombia.

## Ejecutar
- **Doble clic** en `ejecutar_app.bat`, o en una terminal dentro de esta carpeta:
  ```
  python -m pip install -r requirements.txt
  python -m streamlit run app.py
  ```
  Se abre en http://localhost:8501

## Estructura
| Archivo | Qué hace |
|---|---|
| `app.py` | Interfaz (8 pestañas) |
| `core/datos.py` | Descarga Yahoo Finance, conversión USD→COP, datos simulados de respaldo |
| `core/metricas.py` | CAGR, volatilidad, Sharpe, Sortino, drawdown, VaR/CVaR… |
| `core/optimizacion.py` | Máx. Sharpe, mín. volatilidad, según perfil, paridad de riesgo, frontera eficiente |
| `core/simulacion.py` | Monte Carlo con aportes mensuales y comparación con CDT |
| `contenido/educacion.py` | Textos de la Academia, glosario de métricas, quiz |
| `contenido/colombia.py` | Productos, plataformas, impuestos (actualizar periódicamente) |

## Datos actualizados automáticamente
- La app descarga precios **en vivo** de Yahoo Finance (caché de 6 horas).
- Si Yahoo bloquea la descarga (frecuente en servidores en la nube), usa `data/precios.csv`.
- Ese archivo lo actualiza **GitHub Actions** de lunes a viernes a las 5:30 p. m. (hora Colombia)
  — ver `.github/workflows/actualizar_datos.yml`. Para forzarlo: pestaña **Actions → Actualizar datos diarios → Run workflow**.

## Publicar en internet (Streamlit Community Cloud, gratis)
1. Entra a https://share.streamlit.io con tu cuenta de GitHub.
2. **Create app → Deploy a public app from GitHub**.
3. Repositorio: este repo · Branch: `main` · Main file path: `app.py`.
4. **Deploy**. Cada vez que el robot actualiza `data/`, la app se redespliega sola con los datos nuevos.

## Mantenimiento
- Actualiza en la barra lateral la **tasa libre de riesgo** (CDT/TES vigente).
- Revisa `contenido/colombia.py` cuando cambien normas tributarias o topes (Fogafín, UVT).

> Herramienta educativa. No constituye asesoría financiera.
