"""
══════════════════════════════════════════════════════════════
  MI PORTAFOLIO INTELIGENTE — Herramienta educativa de decisión
  Autor: Oscar Mauricio · Basado en 'portafolio_analisis.py'
  Ejecutar:  python -m streamlit run app.py
══════════════════════════════════════════════════════════════
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # para importar core/ y contenido/

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from contenido import colombia as C
from contenido import educacion as E
from core import datos as D
from core import metricas as M
from core import optimizacion as O
from core import simulacion as S

st.set_page_config(page_title="Mi Portafolio Inteligente", page_icon="📈", layout="wide")

PALETA = px.colors.qualitative.Bold + px.colors.qualitative.Pastel


# ══════════════════════════════════════════════════════════════
# Utilidades de formato
# ══════════════════════════════════════════════════════════════
def cop(x: float) -> str:
    """Formato colombiano: $10.000.000"""
    if x is None or not np.isfinite(x):
        return "—"
    return "$" + f"{x:,.0f}".replace(",", ".")


def pct(x: float, dec: int = 1) -> str:
    if x is None or not np.isfinite(x):
        return "—"
    return f"{x * 100:.{dec}f}%".replace(".", ",")


def ayuda(metrica: str) -> str:
    return E.METRICAS.get(metrica, {}).get("corta", "")


def nombre(t: str) -> str:
    if t in D.UNIVERSO:
        return D.UNIVERSO[t]["nombre"]
    return {"CDT": "CDT / renta fija en pesos", "EFECTIVO": "Efectivo en USD (T-Bills)"}.get(t, t)


# ══════════════════════════════════════════════════════════════
# Perfiles de riesgo
# ══════════════════════════════════════════════════════════════
PERFILES = {
    "Conservador": dict(vol=0.06, dd=0.15, rv=30, emoji="🛡️",
                        desc="Priorizas no perder. Aceptas menor rendimiento a cambio de estabilidad. "
                             "Mayor parte en renta fija (CDT, bonos) y una porción pequeña en acciones."),
    "Moderado": dict(vol=0.11, dd=0.25, rv=60, emoji="⚖️",
                     desc="Buscas crecer tu dinero y toleras caídas temporales moderadas. "
                          "Mezcla equilibrada entre acciones y renta fija."),
    "Agresivo": dict(vol=0.16, dd=0.40, rv=85, emoji="🚀",
                     desc="Horizonte largo y buen estómago: aceptas caídas fuertes (−30% o más) "
                          "a cambio de mayor crecimiento esperado. Mayoría en acciones."),
}

PREGUNTAS = [
    ("¿En cuánto tiempo necesitarás este dinero?",
     ["Menos de 1 año", "1 a 3 años", "3 a 5 años", "5 a 10 años", "Más de 10 años"], [0, 1, 2, 3, 4]),
    ("Tu inversión cae 20% en un mes. ¿Qué haces?",
     ["Vendo todo para no perder más", "Vendo una parte", "No hago nada y espero", "Aprovecho y compro más"], [0, 1, 2, 3]),
    ("¿Tienes un fondo de emergencia (3-6 meses de gastos)?",
     ["No", "Parcialmente", "Sí, completo"], [0, 1, 2]),
    ("¿Cuánto sabes de inversiones?",
     ["Nada", "Lo básico (CDT, ahorro)", "Intermedio (fondos, ETFs)", "Avanzado"], [0, 1, 2, 3]),
    ("¿Cuál es tu objetivo principal?",
     ["Proteger mi dinero de la inflación", "Generar ingresos estables",
      "Crecimiento moderado", "Máximo crecimiento a largo plazo"], [0, 1, 2, 3]),
    ("¿Qué parte de tus ahorros totales representa esta inversión?",
     ["Más del 75%", "50% - 75%", "25% - 50%", "Menos del 25%"], [0, 1, 2, 3]),
]


def clasificar(puntaje: int) -> str:
    if puntaje <= 6:
        return "Conservador"
    if puntaje <= 12:
        return "Moderado"
    return "Agresivo"


# ══════════════════════════════════════════════════════════════
# Carga de datos (con caché)
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=6 * 3600, show_spinner="Descargando precios de Yahoo Finance…")
def cargar_reales(tickers: tuple, anios: int):
    return D.descargar_precios(list(tickers), anios)


RUTA_SNAPSHOT = Path(__file__).resolve().parent / D.ARCHIVO_SNAPSHOT


@st.cache_data(ttl=3600, show_spinner=False)
def cargar_snapshot(tickers: tuple, anios: int, _mtime: float):
    return D.cargar_snapshot(RUTA_SNAPSHOT, list(tickers), anios)


@st.cache_data(show_spinner=False)
def cargar_simulados(anios: int):
    return D.precios_simulados(anios)


# ══════════════════════════════════════════════════════════════
# BARRA LATERAL
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("⚙️ Configuración")
    fuente = st.radio("Fuente de datos", ["Reales (Yahoo Finance)", "Simulados (sin internet)"],
                      help="Los datos reales requieren internet. Los simulados usan los parámetros "
                           "históricos del script original y solo sirven para practicar.")
    base = st.radio("Moneda de análisis", ["COP", "USD"], horizontal=True,
                    help="En COP verás el efecto real en tu bolsillo, incluyendo la variación del dólar (TRM). "
                         "Recomendado si vives en Colombia y gastas en pesos.")
    anios_hist = st.select_slider("Años de historia", [3, 5, 7, 10], value=5,
                                  help="Más años = más ciclos de mercado incluidos (más confiable).")

    st.subheader("Activos")
    seleccion = st.multiselect(
        "Escoge entre 2 y 10 activos", list(D.UNIVERSO), default=D.TICKERS_DEFECTO,
        format_func=lambda t: f"{t} · {D.UNIVERSO[t]['nombre']}")
    extra = st.text_input("Otros tickers de Yahoo Finance (opcional)", placeholder="Ej.: ECOPETROL.CL, VWRA.L",
                          help="Separados por coma. Se asume que cotizan en USD, excepto los terminados en .CL (pesos).")
    seleccion += [t.strip().upper() for t in extra.split(",") if t.strip()]
    seleccion = list(dict.fromkeys(seleccion))[:12]

    incluir_rf = st.checkbox("Incluir CDT / efectivo como opción", value=True,
                             help="Agrega un activo sin riesgo que rinde la tasa de abajo. Permite que perfiles "
                                  "conservadores tengan parte en renta fija.")
    rf_pct = st.number_input("Tasa libre de riesgo (% E.A.)", min_value=0.0, max_value=30.0,
                             value=9.0 if base == "COP" else 4.0, step=0.25,
                             help="En COP usa la tasa de un CDT a 1 año o TES corto vigente. "
                                  "En USD, la tasa de los bonos del Tesoro a corto plazo. Actualízala.")
    rf = rf_pct / 100

    st.subheader("Tu dinero")
    capital = st.number_input("Capital inicial (COP)", min_value=0, value=10_000_000, step=500_000)
    aporte = st.number_input("Aporte mensual (COP)", min_value=0, value=500_000, step=50_000)
    tope = st.slider("Peso máximo por activo (%)", 15, 100, 40, step=5,
                     help="Limitar el peso evita portafolios concentrados en 1-2 activos, "
                          "un error típico de la optimización con datos pasados.") / 100
    st.caption(E.DISCLAIMER)

# ══════════════════════════════════════════════════════════════
# DATOS
# ══════════════════════════════════════════════════════════════
fx = None
aviso_datos = None
origen = "simulados"
if fuente.startswith("Reales"):
    clave = tuple(sorted(seleccion))
    try:
        nativos, fx, fallidos = cargar_reales(clave, anios_hist)
        origen = "Yahoo Finance (en vivo)"
    except Exception as e_vivo:  # sin internet / Yahoo bloquea la nube
        try:
            nativos, fx, fallidos = cargar_snapshot(clave, anios_hist, RUTA_SNAPSHOT.stat().st_mtime)
            origen = "respaldo diario del repositorio"
        except Exception:
            nativos = fx = None
            aviso_datos = f"No fue posible obtener datos reales ({e_vivo}). Se usan datos **simulados**."
    if fx is not None:
        if fallidos:
            st.warning(f"No se encontraron datos suficientes para: {', '.join(fallidos)}. Se excluyen del análisis.")
        precios = D.convertir_moneda(nativos, fx, base)
    else:
        nativos = precios = cargar_simulados(anios_hist)
else:
    nativos = precios = cargar_simulados(anios_hist)
    aviso_datos = ("Modo **simulado**: precios sintéticos con parámetros históricos de 6 ETFs (en USD). "
                   "Útil para practicar; para decidir usa datos reales.")

precios = precios.copy()  # no modificar el objeto guardado en caché
nombre_rf = "CDT" if base == "COP" else "EFECTIVO"
if incluir_rf:
    dias = np.arange(len(precios))
    precios[nombre_rf] = 100 * (1 + rf) ** (dias / 252)

if precios.shape[1] < 2:
    st.error("Selecciona al menos 2 activos con datos disponibles.")
    st.stop()

rend = M.rendimientos(precios)
tickers = list(precios.columns)
riesgosos = [t for t in tickers if t != nombre_rf]
tabla = M.tabla_metricas(rend, rf)
mu, cov = O.parametros(rend)
ultima_trm = float(fx.dropna().iloc[-1]) if fx is not None else None

# ══════════════════════════════════════════════════════════════
# ENCABEZADO
# ══════════════════════════════════════════════════════════════
st.title("📈 Mi Portafolio Inteligente")
st.caption(f"Herramienta educativa para decidir cómo invertir desde Colombia · Datos ({origen}): "
           f"{precios.index[0]:%d-%m-%Y} → **{precios.index[-1]:%d-%m-%Y}** · Moneda: {base}"
           + (f" · TRM actual: {cop(ultima_trm)}" if ultima_trm else ""))
if aviso_datos:
    st.info(aviso_datos)

tabs = st.tabs(["🏠 Inicio", "🧭 Mi perfil", "📊 Activos", "⚖️ Portafolio", "🔮 Proyección",
                "📝 Mi plan", "🏦 Invertir desde Colombia", "📚 Academia"])

# ══════════════════════════════════════════════════════════════
# 1. INICIO
# ══════════════════════════════════════════════════════════════
with tabs[0]:
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("""
### Bienvenido 👋
Esta herramienta te ayuda a **entender, construir y evaluar** un portafolio de inversión, paso a paso,
pensado para alguien que **está empezando** y vive en **Colombia**.

**¿Cómo usarla?** Sigue las pestañas en orden:
1. **🧭 Mi perfil** — responde 6 preguntas y descubre cuánto riesgo es adecuado para ti.
2. **📊 Activos** — mira cómo se han comportado los activos (en pesos) y qué significa cada métrica.
3. **⚖️ Portafolio** — compara estrategias y obtén cuánto comprar de cada activo.
4. **🔮 Proyección** — simula miles de futuros posibles y compáralos con un CDT.
5. **📝 Mi plan** — resumen para decidir, con checklist y descarga.
6. **🏦 Invertir desde Colombia** y **📚 Academia** — productos, plataformas, impuestos y conceptos.

Ajusta en la barra lateral ⬅️ los activos, tu capital y tu aporte mensual.
""")
    with c2:
        st.markdown("#### 🛤️ Ruta del inversionista principiante")
        for i, (paso, detalle) in enumerate(E.RUTA_PRINCIPIANTE, 1):
            st.markdown(f"**{i}. {paso}** — {detalle}")
    st.divider()
    st.warning(E.DISCLAIMER)

# ══════════════════════════════════════════════════════════════
# 2. PERFIL DE RIESGO
# ══════════════════════════════════════════════════════════════
with tabs[1]:
    st.header("🧭 ¿Qué tipo de inversionista eres?")
    st.markdown("Responde con honestidad: **no hay respuestas buenas o malas**. El objetivo es que no termines "
                "con un portafolio que te haga vender en pánico.")
    with st.form("form_perfil"):
        respuestas = []
        for i, (preg, opciones, _) in enumerate(PREGUNTAS):
            previo = st.session_state.get("respuestas", [None] * len(PREGUNTAS))[i]
            respuestas.append(st.radio(f"**{i + 1}. {preg}**", range(len(opciones)),
                                       format_func=lambda k, o=opciones: o[k],
                                       index=previo if previo is not None else None, key=f"preg_{i}"))
        enviado = st.form_submit_button("Calcular mi perfil", type="primary")
    if enviado:
        if None in respuestas:
            st.error("Responde todas las preguntas.")
        else:
            st.session_state["respuestas"] = respuestas
            st.session_state["puntaje"] = sum(PREGUNTAS[i][2][r] for i, r in enumerate(respuestas))
            st.session_state["perfil"] = clasificar(st.session_state["puntaje"])

    if "perfil" in st.session_state:
        p = st.session_state["perfil"]
        info = PERFILES[p]
        r = st.session_state["respuestas"]
        st.success(f"### {info['emoji']} Tu perfil es **{p}** (puntaje {st.session_state['puntaje']}/18)")
        st.markdown(info["desc"])
        k1, k2, k3 = st.columns(3)
        k1.metric("Volatilidad objetivo", pct(info["vol"], 0), help=ayuda("Volatilidad"))
        k2.metric("Caída máxima tolerable aprox.", pct(-info["dd"], 0), help=ayuda("Máx. caída"))
        k3.metric("Renta variable sugerida", f"~{info['rv']}%",
                  help="Porcentaje aproximado en acciones/ETFs de acciones; el resto en renta fija.")
        fig = go.Figure(go.Bar(x=[info["rv"], 100 - info["rv"]], y=["", ""], orientation="h",
                               marker_color=["#636EFA", "#00CC96"],
                               text=[f"Acciones {info['rv']}%", f"Renta fija {100 - info['rv']}%"],
                               textposition="inside"))
        fig.update_layout(barmode="stack", height=90, showlegend=False, margin=dict(l=0, r=0, t=0, b=0),
                          xaxis=dict(visible=False), yaxis=dict(visible=False))
        st.plotly_chart(fig, width="stretch")
        if r[0] == 0:
            st.error("⛔ **Necesitas el dinero en menos de 1 año.** No inviertas en acciones: usa una cuenta "
                     "remunerada o un CDT. Las acciones pueden caer 20-30% en meses y no darías tiempo a recuperarte.")
        if r[2] == 0:
            st.warning("⚠️ **No tienes fondo de emergencia.** Constrúyelo primero (3-6 meses de gastos en cuenta "
                       "remunerada/CDT). Sin él, un imprevisto te obliga a vender en mal momento.")
        if r[5] == 0:
            st.warning("⚠️ Vas a invertir más del 75% de tus ahorros. Considera empezar con una parte e ir aumentando.")
    else:
        st.info("Completa el cuestionario para personalizar el portafolio. Mientras tanto se usa el perfil **Moderado**.")

perfil = st.session_state.get("perfil", "Moderado")
info_perfil = PERFILES[perfil]

# ══════════════════════════════════════════════════════════════
# 3. ANÁLISIS DE ACTIVOS
# ══════════════════════════════════════════════════════════════
with tabs[2]:
    st.header("📊 ¿Cómo se han comportado los activos?")
    st.caption(f"Rendimientos medidos en **{base}**"
               + (", incluyendo el efecto de la variación del dólar." if base == "COP" else "."))

    with st.expander("🔎 ¿Qué es cada activo?", expanded=False):
        fichas = pd.DataFrame([
            dict(Ticker=t, Nombre=nombre(t),
                 Clase=D.UNIVERSO.get(t, {}).get("clase", "Renta fija" if t == nombre_rf else "Otro"),
                 Moneda=D.moneda_de(t) if t != nombre_rf else base,
                 Descripción=D.UNIVERSO.get(t, {}).get(
                     "desc", f"Rinde {pct(rf)} E.A. constante (supuesto, sin riesgo)." if t == nombre_rf
                     else "Ticker personalizado."))
            for t in tickers])
        st.dataframe(fichas, hide_index=True, width="stretch")

    # Tabla de métricas
    st.subheader("Tabla de métricas")
    pct_cols = ["Rend. anual (CAGR)", "Volatilidad", "Máx. caída", "VaR 95% mensual", "CVaR 95% mensual",
                "Meses positivos", "Mejor año", "Peor año", "Rend. acumulado"]
    vista = tabla.copy()
    vista[pct_cols] = vista[pct_cols] * 100
    vista.insert(0, "Nombre", [nombre(t) for t in vista.index])
    cfg = {c: st.column_config.NumberColumn(c, help=ayuda(c), format="%.1f%%") for c in pct_cols}
    cfg.update({c: st.column_config.NumberColumn(c, help=ayuda(c), format="%.2f") for c in ["Sharpe", "Sortino", "Calmar"]})
    st.dataframe(vista, column_config=cfg, width="stretch")
    st.caption("💡 Pasa el cursor sobre el título de cada columna para ver qué significa. "
               "Explicación completa en la pestaña 📚 Academia.")

    # Lectura automática en lenguaje sencillo
    tr = tabla.loc[riesgosos]
    if len(tr) >= 2:
        mejor_s = tr["Sharpe"].idxmax()
        mas_rent = tr["Rend. anual (CAGR)"].idxmax()
        peor_dd = tr["Máx. caída"].idxmin()
        mas_estable = tr["Volatilidad"].idxmin()
        bajo_rf = tr.index[tr["Rend. anual (CAGR)"] < rf].tolist()
        st.markdown(f"""
**🧠 Lectura rápida:**
- El que **más rindió** fue **{mas_rent}** ({nombre(mas_rent)}): {pct(tr.loc[mas_rent, 'Rend. anual (CAGR)'])} al año.
- La **mejor relación rendimiento/riesgo** (Sharpe) la tuvo **{mejor_s}** ({tr.loc[mejor_s, 'Sharpe']:.2f}).
- El **más estable** fue **{mas_estable}** (volatilidad {pct(tr.loc[mas_estable, 'Volatilidad'])}).
- La **peor caída** la sufrió **{peor_dd}**: {pct(tr.loc[peor_dd, 'Máx. caída'])}. Con {cop(capital)} invertidos,
  habrías visto tu saldo bajar hasta **{cop(capital * (1 + tr.loc[peor_dd, 'Máx. caída']))}**.
""" + (f"- ⚠️ Rindieron **menos que un CDT al {pct(rf)}**: {', '.join(bajo_rf)}. Asumir su riesgo no se pagó en este periodo."
       if bajo_rf else ""))

    c1, c2 = st.columns(2)
    with c1:
        norm = precios / precios.iloc[0] * 100
        fig = px.line(norm, labels={"value": "Valor (base 100)", "index": "", "variable": "Activo"},
                      title="Crecimiento de 100 invertidos", color_discrete_sequence=PALETA)
        st.plotly_chart(fig, width="stretch")
    with c2:
        dd = (precios / precios.cummax() - 1) * 100
        fig = px.line(dd, labels={"value": "Caída desde máximo (%)", "index": "", "variable": "Activo"},
                      title="Caídas desde el máximo (drawdown)", color_discrete_sequence=PALETA)
        st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        corr = rend[riesgosos].corr().fillna(0).round(2)
        fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdYlGn_r", zmin=-1, zmax=1,
                        title="Correlación (¿se mueven juntos?)")
        st.plotly_chart(fig, width="stretch")
        st.caption("🟥 Cerca de 1: se mueven igual (poca diversificación). 🟩 Cerca de 0 o negativo: diversifican.")
    with c2:
        fig = px.scatter(tabla.reset_index(names="Activo"), x="Volatilidad", y="Rend. anual (CAGR)", text="Activo",
                         color="Activo", color_discrete_sequence=PALETA, title="Rendimiento vs. riesgo")
        fig.update_traces(textposition="top center", marker_size=12)
        fig.update_layout(showlegend=False, xaxis_tickformat=".0%", yaxis_tickformat=".0%")
        st.plotly_chart(fig, width="stretch")
        st.caption("Lo ideal: arriba (más rendimiento) y a la izquierda (menos riesgo).")

    anual = M.rend_anuales(precios[riesgosos]) * 100
    fig = px.bar(anual.reset_index(names="Año").melt(id_vars="Año", var_name="Activo", value_name="Rend. (%)"),
                 x="Año", y="Rend. (%)", color="Activo", barmode="group", color_discrete_sequence=PALETA,
                 title="Rendimiento por año calendario (el primer y último año pueden estar incompletos)")
    st.plotly_chart(fig, width="stretch")

    if base == "COP" and fx is not None:
        st.subheader("💱 El efecto del dólar")
        fxv = fx.reindex(precios.index).ffill()
        var_trm = fxv.iloc[-1] / fxv.iloc[0] - 1
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = px.line(fxv, labels={"value": "COP por USD", "index": ""}, title="Tasa de cambio USD/COP")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, width="stretch")
        with c2:
            st.metric("Variación del dólar en el periodo", pct(var_trm))
            st.markdown("Si el dólar **subió**, tus activos en USD rindieron **más** en pesos; si **bajó**, rindieron "
                        "**menos**. Cambia la moneda de análisis a USD en la barra lateral para comparar.")

# ══════════════════════════════════════════════════════════════
# 4. PORTAFOLIO
# ══════════════════════════════════════════════════════════════
with tabs[3]:
    st.header("⚖️ Construye tu portafolio")
    n = len(tickers)
    idx_r = [tickers.index(t) for t in riesgosos]

    # Estrategias
    estrategias = {}
    w_perfil, factible = O.max_retorno_con_volatilidad(mu, cov, info_perfil["vol"], tope)
    estrategias[f"{info_perfil['emoji']} Según mi perfil ({perfil})"] = w_perfil
    estrategias["⭐ Máximo Sharpe"] = O.max_sharpe(mu, cov, rf, tope)
    estrategias["🛡️ Mínima volatilidad"] = O.min_volatilidad(mu, cov, tope)
    w_rp = np.zeros(n)
    sub_cov = cov[np.ix_(idx_r, idx_r)]
    w_rp[idx_r] = O.paridad_riesgo(sub_cov, max(tope, 1 / len(idx_r)))
    estrategias["⚖️ Paridad de riesgo"] = w_rp
    w_eq = np.zeros(n)
    w_eq[idx_r] = 1 / len(idx_r)
    estrategias["🟰 Pesos iguales"] = w_eq

    descripciones = {
        "Según mi perfil": f"Busca el mayor rendimiento sin superar la volatilidad de tu perfil ({pct(info_perfil['vol'], 0)}).",
        "Máximo Sharpe": "La mejor relación rendimiento/riesgo histórica. Sensible a los datos del pasado.",
        "Mínima volatilidad": "El portafolio más estable posible con estos activos.",
        "Paridad de riesgo": "Cada activo aporta el mismo riesgo. Robusta, no depende de predecir rendimientos.",
        "Pesos iguales": "Mismo dinero en cada activo (sin CDT). Simple y difícil de superar en la práctica.",
    }

    filas = []
    series_port = {}
    for nom, w in estrategias.items():
        r_p = rend.values @ w
        serie = pd.Series(r_p, index=rend.index)
        series_port[nom] = serie
        m = M.metricas_serie(serie, rf)
        ret_e, vol_e, sh_e = O.desempeno(w, mu, cov, rf)
        filas.append({"Estrategia": nom, "Rend. anual (CAGR)": m["Rend. anual (CAGR)"] * 100,
                      "Volatilidad": m["Volatilidad"] * 100, "Sharpe": m["Sharpe"],
                      "Máx. caída": m["Máx. caída"] * 100, "Peor año": m["Peor año"] * 100,
                      "N° activos": int((w > 0.005).sum())})
    comp = pd.DataFrame(filas).set_index("Estrategia")

    st.subheader("1️⃣ Compara estrategias")
    st.dataframe(comp, width="stretch", column_config={
        "Rend. anual (CAGR)": st.column_config.NumberColumn(format="%.1f%%", help=ayuda("Rend. anual (CAGR)")),
        "Volatilidad": st.column_config.NumberColumn(format="%.1f%%", help=ayuda("Volatilidad")),
        "Sharpe": st.column_config.NumberColumn(format="%.2f", help=ayuda("Sharpe")),
        "Máx. caída": st.column_config.NumberColumn(format="%.1f%%", help=ayuda("Máx. caída")),
        "Peor año": st.column_config.NumberColumn(format="%.1f%%"),
    })
    if not factible:
        st.warning(f"Con estos activos no se logra una volatilidad tan baja como la de tu perfil "
                   f"({pct(info_perfil['vol'], 0)}). Se muestra el portafolio de mínima volatilidad. "
                   "Activa la opción *CDT / efectivo* en la barra lateral o agrega bonos de corto plazo (SHY).")
    st.caption("⚠️ Resultados *dentro de muestra*: los pesos se calcularon con los mismos datos que se evalúan, "
               "así que el pasado luce mejor de lo que será el futuro. Prefiere estrategias diversificadas.")

    st.subheader("2️⃣ Analiza una estrategia")
    elegida = st.selectbox("Estrategia", list(estrategias), index=0)
    for k, v in descripciones.items():
        if k in elegida:
            st.caption(v)
    w_sel = estrategias[elegida]
    r_sel = series_port[elegida]
    m_sel = M.metricas_serie(r_sel, rf)

    k = st.columns(5)
    k[0].metric("Rend. anual histórico", pct(m_sel["Rend. anual (CAGR)"]), help=ayuda("Rend. anual (CAGR)"))
    k[1].metric("Volatilidad", pct(m_sel["Volatilidad"]), help=ayuda("Volatilidad"))
    k[2].metric("Sharpe", f"{m_sel['Sharpe']:.2f}".replace(".", ","), help=ayuda("Sharpe"))
    k[3].metric("Máx. caída", pct(m_sel["Máx. caída"]), help=ayuda("Máx. caída"))
    k[4].metric("VaR 95% mensual", pct(-m_sel["VaR 95% mensual"]), help=ayuda("VaR 95% mensual"))

    perdida = capital * m_sel["Máx. caída"]
    msg = (f"🧪 **Prueba de estómago:** con {cop(capital)} en esta estrategia, en el peor momento histórico habrías visto "
           f"tu saldo caer a **{cop(capital + perdida)}** (una pérdida temporal de {cop(-perdida)}). "
           "¿Podrías aguantar sin vender?")
    (st.error if abs(m_sel["Máx. caída"]) > info_perfil["dd"] else st.info)(
        msg + (f" ⚠️ Supera la caída tolerable para tu perfil ({pct(-info_perfil['dd'], 0)})."
               if abs(m_sel["Máx. caída"]) > info_perfil["dd"] else ""))

    c1, c2 = st.columns(2)
    pesos = pd.DataFrame({"Activo": tickers, "Nombre": [nombre(t) for t in tickers], "Peso": w_sel,
                          "Aporte al riesgo": O.contribucion_riesgo(w_sel, cov)})
    pesos = pesos[pesos["Peso"] > 0.001].sort_values("Peso", ascending=False)
    with c1:
        fig = px.pie(pesos, values="Peso", names="Activo", hole=0.5, title="¿Dónde está tu dinero?",
                     color_discrete_sequence=PALETA, hover_data=["Nombre"])
        fig.update_traces(textinfo="label+percent")
        st.plotly_chart(fig, width="stretch")
    with c2:
        larga = pesos.melt(id_vars=["Activo"], value_vars=["Peso", "Aporte al riesgo"])
        fig = px.bar(larga, x="Activo", y="value", color="variable", barmode="group",
                     title="Dinero vs. riesgo que aporta cada activo",
                     labels={"value": "", "variable": ""})
        fig.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig, width="stretch")
        st.caption("Un activo puede tener poco dinero pero aportar mucho riesgo (por su volatilidad).")

    # Frontera eficiente
    with st.spinner("Calculando frontera eficiente…"):
        f_vol, f_ret = O.frontera_eficiente(mu, cov, tope)
        a_vol, a_ret, a_sh = O.portafolios_aleatorios(mu, cov, rf)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=a_vol, y=a_ret, mode="markers", name="Portafolios aleatorios",
                             marker=dict(size=4, color=a_sh, colorscale="Viridis", opacity=0.45,
                                         colorbar=dict(title="Sharpe"))))
    fig.add_trace(go.Scatter(x=f_vol, y=f_ret, mode="lines", name="Frontera eficiente",
                             line=dict(color="#FFA15A", width=3)))
    for i, t in enumerate(tickers):
        fig.add_trace(go.Scatter(x=[np.sqrt(cov[i, i])], y=[mu[i]], mode="markers+text", text=[t],
                                 textposition="top center", name=t, showlegend=False,
                                 marker=dict(size=10, color="white", line=dict(width=1, color="black"))))
    for j, (nom, w) in enumerate(estrategias.items()):
        r_e, v_e, _ = O.desempeno(w, mu, cov, rf)
        fig.add_trace(go.Scatter(x=[v_e], y=[r_e], mode="markers", name=nom,
                                 marker=dict(size=16, symbol="star", color=PALETA[j],
                                             line=dict(width=1, color="white"))))
    fig.update_layout(title="Frontera eficiente de Markowitz", xaxis_title="Volatilidad anual",
                      yaxis_title="Rendimiento esperado anual", xaxis_tickformat=".0%", yaxis_tickformat=".0%",
                      height=550, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, width="stretch")
    st.caption("Cada punto es un portafolio posible. La curva naranja muestra el máximo rendimiento para cada nivel "
               "de riesgo (con el límite de peso que fijaste). Las estrellas son las estrategias.")

    # Backtest
    st.subheader("3️⃣ ¿Cómo le habría ido? (backtest)")
    crec = pd.DataFrame({nom: capital * (1 + s).cumprod() for nom, s in series_port.items()})
    fig = px.line(crec, labels={"value": "Valor (COP)" if base == "COP" else "Valor", "index": "", "variable": ""},
                  title=f"Evolución de {cop(capital)} invertidos al inicio (sin aportes)",
                  color_discrete_sequence=PALETA)
    fig.update_layout(legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, width="stretch")

    # Plan de compra
    st.subheader("4️⃣ Plan de compra")
    plan = pesos[["Activo", "Nombre", "Peso"]].copy()
    plan["Monto COP"] = plan["Peso"] * capital
    if ultima_trm:
        plan["Monto USD"] = plan["Monto COP"] / ultima_trm
        precio_nat = []
        for t in plan["Activo"]:
            if t in nativos.columns:
                precio_nat.append(float(nativos[t].dropna().iloc[-1]))
            else:
                precio_nat.append(np.nan)
        plan["Precio actual"] = precio_nat
        plan["Moneda"] = [D.moneda_de(t) if t != nombre_rf else "COP" for t in plan["Activo"]]
        plan["Unidades aprox."] = np.where(plan["Moneda"] == "USD", plan["Monto USD"] / plan["Precio actual"],
                                           plan["Monto COP"] / plan["Precio actual"])
    st.dataframe(plan, hide_index=True, width="stretch", column_config={
        "Peso": st.column_config.NumberColumn(format="%.1f%%"),
        "Monto COP": st.column_config.NumberColumn(format="$%,.0f"),
        "Monto USD": st.column_config.NumberColumn(format="US$%,.0f"),
        "Precio actual": st.column_config.NumberColumn(format="%,.2f"),
        "Unidades aprox.": st.column_config.NumberColumn(format="%.2f"),
    } if ultima_trm else {"Peso": st.column_config.NumberColumn(format="%.1f%%"),
                          "Monto COP": st.column_config.NumberColumn(format="$%,.0f")})
    st.caption("Las unidades con decimales requieren un broker que permita **fracciones**. Si no, redondea hacia abajo "
               "y deja el sobrante en efectivo. Los montos no incluyen comisiones ni costos de giro.")
    plan_csv = plan.assign(Peso=(plan["Peso"] * 100).round(2)).to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Descargar plan de compra (CSV)", plan_csv, "plan_de_compra.csv", "text/csv")

# ══════════════════════════════════════════════════════════════
# 5. PROYECCIÓN
# ══════════════════════════════════════════════════════════════
with tabs[4]:
    st.header("🔮 ¿Cuánto podría tener en el futuro?")
    st.markdown(f"Simulación **Monte Carlo** de la estrategia *{elegida}*: se generan miles de futuros posibles "
                "con la volatilidad histórica del portafolio. **No es una predicción**, es un rango de escenarios.")
    c = st.columns(4)
    horizonte = c[0].slider("Horizonte (años)", 1, 30, 10)
    supuesto = c[1].radio("Rendimiento esperado", ["Conservador", "Histórico", "Personalizado"],
                          help="El histórico de los últimos años puede ser muy optimista. "
                               "El conservador resta 3 puntos porcentuales al año.")
    mu_log_m, sig_m = S.stats_mensuales(r_sel)
    hist_anual = float(np.exp(mu_log_m * 12) - 1)
    if supuesto == "Histórico":
        esperado = hist_anual
    elif supuesto == "Conservador":
        esperado = hist_anual - 0.03
    else:
        esperado = c[1].number_input("Rend. anual esperado (%)", -10.0, 30.0, 8.0, 0.5) / 100
    inflacion = c[2].number_input("Inflación esperada (% anual)", 0.0, 20.0, 5.0, 0.5,
                                  help="Para ver el poder de compra real. Consulta la meta e inflación del Banco de la República.")
    tasa_cdt = c[3].number_input("Tasa CDT para comparar (% E.A.)", 0.0, 30.0, float(rf_pct), 0.25) / 100
    esperado = max(esperado, -0.5)
    mu_usar = np.log1p(esperado) / 12

    st.caption(f"Supuestos: rendimiento anual (mediana) {pct(esperado)} · volatilidad anual {pct(sig_m * np.sqrt(12))} · "
               f"capital {cop(capital)} + {cop(aporte)}/mes.")

    sims = S.simular(capital, aporte, horizonte, mu_usar, sig_m)
    fijo = S.proyeccion_fija(capital, aporte, horizonte, tasa_cdt)
    puesto = S.aportado(capital, aporte, horizonte)
    final = sims[-1]
    pcts = {p: np.percentile(sims, p, axis=1) for p in (5, 25, 50, 75, 95)}
    meses_eje = np.arange(sims.shape[0]) / 12
    deflactor = (1 + inflacion / 100) ** horizonte

    k = st.columns(5)
    k[0].metric("Total aportado", cop(puesto[-1]))
    k[1].metric("Escenario pesimista (P5)", cop(np.percentile(final, 5)),
                help="Solo 5 de cada 100 simulaciones terminaron por debajo de este valor.")
    k[2].metric("Escenario central (mediana)", cop(np.median(final)),
                delta=cop(np.median(final) - puesto[-1]) + " de ganancia")
    k[3].metric("Escenario optimista (P95)", cop(np.percentile(final, 95)))
    k[4].metric(f"En CDT al {pct(tasa_cdt)}", cop(fijo[-1]))

    prob_perdida = float((final < puesto[-1]).mean())
    prob_cdt = float((final > fijo[-1]).mean())
    k = st.columns(3)
    k[0].metric("Prob. de terminar con menos de lo aportado", pct(prob_perdida))
    k[1].metric("Prob. de superar al CDT", pct(prob_cdt))
    k[2].metric("Mediana en pesos de hoy (sin inflación)", cop(np.median(final) / deflactor),
                help="Lo que podrías comprar con ese dinero a precios de hoy.")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=meses_eje, y=pcts[95], line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=meses_eje, y=pcts[5], fill="tonexty", fillcolor="rgba(99,110,250,0.15)",
                             line=dict(width=0), name="Rango 5%–95%"))
    fig.add_trace(go.Scatter(x=meses_eje, y=pcts[75], line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=meses_eje, y=pcts[25], fill="tonexty", fillcolor="rgba(99,110,250,0.35)",
                             line=dict(width=0), name="Rango 25%–75%"))
    fig.add_trace(go.Scatter(x=meses_eje, y=pcts[50], name="Mediana", line=dict(color="#636EFA", width=3)))
    fig.add_trace(go.Scatter(x=meses_eje, y=fijo, name=f"CDT {pct(tasa_cdt)}", line=dict(color="#00CC96", dash="dash")))
    fig.add_trace(go.Scatter(x=meses_eje, y=puesto, name="Dinero aportado", line=dict(color="#EF553B", dash="dot")))
    fig.update_layout(title="Abanico de escenarios", xaxis_title="Años", yaxis_title="Valor (COP)", height=480,
                      legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, width="stretch")
    st.markdown(f"""
**¿Cómo leerlo?** La línea azul es el escenario central. En la mitad de los futuros simulados terminas dentro de la
banda oscura, y en 90 de cada 100 dentro de la banda clara. Observa que **la banda se ensancha con el tiempo**: la
incertidumbre crece, pero también la probabilidad de superar al CDT. Con un horizonte de {horizonte} años, la
probabilidad de terminar con menos de lo que aportaste es **{pct(prob_perdida)}**.
""")

    st.subheader("🎯 ¿Cuánto debo aportar para llegar a mi meta?")
    c1, c2, c3 = st.columns(3)
    meta = c1.number_input("Meta (COP)", min_value=1_000_000, value=100_000_000, step=5_000_000)
    confianza = c2.select_slider("Quiero lograrlo con probabilidad de", [50, 60, 70, 80, 90], value=70,
                                 format_func=lambda x: f"{x}%")
    if c3.button("Calcular aporte necesario", type="primary"):
        q = 100 - confianza
        lo, hi = 0.0, max(meta / (horizonte * 12), 1.0)
        valor = lambda a: np.percentile(S.simular(capital, a, horizonte, mu_usar, sig_m, n=2000)[-1], q)
        if valor(0) >= meta:
            st.success(f"🎉 Con tu capital actual ya alcanzarías la meta con {confianza}% de probabilidad, sin aportes.")
        else:
            for _ in range(30):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if valor(mid) < meta else (lo, mid)
            cdt_lo, cdt_hi = 0.0, meta / (horizonte * 12)
            for _ in range(40):
                mid = (cdt_lo + cdt_hi) / 2
                cdt_lo, cdt_hi = (mid, cdt_hi) if S.proyeccion_fija(capital, mid, horizonte, tasa_cdt)[-1] < meta else (cdt_lo, mid)
            st.success(f"Necesitas aportar aprox. **{cop(hi)} al mes** con esta estrategia "
                       f"(vs. **{cop(cdt_hi)} al mes** en un CDT al {pct(tasa_cdt)}) para llegar a {cop(meta)} "
                       f"en {horizonte} años con {confianza}% de probabilidad.")

    with st.expander("📐 Detalles del modelo"):
        st.markdown("""
- Rendimientos mensuales log-normales con la **volatilidad histórica** del portafolio y el rendimiento esperado elegido.
- 5.000 simulaciones; aportes al final de cada mes; sin costos ni impuestos.
- Limitaciones: asume que el futuro tiene la misma volatilidad que el pasado, ignora crisis extremas más frecuentes
  de lo que predice la distribución normal ("colas gruesas") y no incluye rebalanceo ni cambios de estrategia.
""")

# ══════════════════════════════════════════════════════════════
# 6. MI PLAN (resumen para decidir)
# ══════════════════════════════════════════════════════════════
with tabs[5]:
    st.header("📝 Mi plan de inversión")
    perfil_hecho = "perfil" in st.session_state
    resp = st.session_state.get("respuestas")

    st.subheader("✅ Checklist antes de invertir")
    ck = [
        st.checkbox("Tengo un fondo de emergencia de 3 a 6 meses de gastos", value=bool(resp and resp[2] == 2)),
        st.checkbox("No tengo deudas caras (tarjetas de crédito, créditos de consumo)"),
        st.checkbox("No necesitaré este dinero en al menos 3 años", value=bool(resp and resp[0] >= 2)),
        st.checkbox("Verifiqué que la plataforma está vigilada por la SFC o un regulador reconocido"),
        st.checkbox("Entiendo que mi inversión puede caer temporalmente y no venderé en pánico"),
        st.checkbox("Conozco los costos (comisiones, giro, spread) y cómo declarar ante la DIAN"),
    ]
    listo = sum(ck)
    st.progress(listo / len(ck), text=f"{listo} de {len(ck)} puntos cumplidos")

    # Alertas de decisión
    alertas = []
    if not ck[0]:
        alertas.append("🔴 **Prioridad 1: fondo de emergencia.** Antes de invertir en acciones, ahorra en cuenta remunerada o CDT.")
    if not ck[1]:
        alertas.append("🔴 **Paga primero las deudas caras.** Ninguna inversión supera de forma segura el interés de una tarjeta de crédito.")
    if horizonte < 3 and float(w_sel[idx_r].sum()) > 0.5:
        alertas.append("🟠 Tu horizonte es corto y más de la mitad está en activos riesgosos. Considera más CDT.")
    if abs(m_sel["Máx. caída"]) > info_perfil["dd"]:
        alertas.append(f"🟠 La estrategia elegida tuvo caídas ({pct(m_sel['Máx. caída'])}) mayores a las que tolera tu perfil.")
    if prob_perdida > 0.2:
        alertas.append(f"🟠 Probabilidad de perder frente a lo aportado: {pct(prob_perdida)}. Alarga el horizonte o reduce riesgo.")
    if not perfil_hecho:
        alertas.append("🔵 Aún no completas el cuestionario de perfil (pestaña 🧭).")
    if (pesos["Peso"] > 0.5).any():
        alertas.append("🟠 Más del 50% en un solo activo: diversifica o baja el peso máximo en la barra lateral.")

    if alertas:
        for a in alertas:
            st.markdown(a)
    else:
        st.success("🟢 Todo en orden: tu plan es coherente con tu perfil. Recuerda empezar con aportes constantes y rebalancear una vez al año.")

    st.subheader("📋 Resumen")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
- **Perfil:** {info_perfil['emoji']} {perfil}{'' if perfil_hecho else ' (por defecto)'}
- **Estrategia:** {elegida}
- **Capital inicial:** {cop(capital)} · **Aporte mensual:** {cop(aporte)}
- **Horizonte:** {horizonte} años
- **Rend. histórico:** {pct(m_sel['Rend. anual (CAGR)'])} · **Volatilidad:** {pct(m_sel['Volatilidad'])} · **Máx. caída:** {pct(m_sel['Máx. caída'])}
- **Escenarios a {horizonte} años:** pesimista {cop(np.percentile(final, 5))} · central {cop(np.median(final))} · optimista {cop(np.percentile(final, 95))}
- **Alternativa CDT:** {cop(fijo[-1])}
""")
    with c2:
        st.dataframe(plan[["Activo", "Nombre", "Peso", "Monto COP"]], hide_index=True, width="stretch",
                     column_config={"Peso": st.column_config.NumberColumn(format="%.1f%%"),
                                    "Monto COP": st.column_config.NumberColumn(format="$%,.0f")})

    st.markdown("""
**Próximos pasos sugeridos**
1. Elige la plataforma (pestaña 🏦) según tu monto y los activos del plan.
2. Haz la primera compra y **programa el aporte mensual** el mismo día de cada mes.
3. Revisa el portafolio **cada 3 meses**, no todos los días.
4. **Rebalancea una vez al año** volviendo a los pesos objetivo (idealmente con los aportes nuevos).
5. Guarda todos los extractos para la **declaración de renta**.
""")

    texto_plan = f"""MI PLAN DE INVERSIÓN — {pd.Timestamp.today():%Y-%m-%d}
Perfil: {perfil}
Estrategia: {elegida}
Capital inicial: {cop(capital)} | Aporte mensual: {cop(aporte)} | Horizonte: {horizonte} años
Rendimiento histórico: {pct(m_sel['Rend. anual (CAGR)'])} | Volatilidad: {pct(m_sel['Volatilidad'])} | Máx. caída: {pct(m_sel['Máx. caída'])}
Escenarios: P5 {cop(np.percentile(final, 5))} | Mediana {cop(np.median(final))} | P95 {cop(np.percentile(final, 95))} | CDT {cop(fijo[-1])}
Prob. de terminar con menos de lo aportado: {pct(prob_perdida)}

PESOS
""" + "\n".join(f"- {a} ({nm}): {pct(p)} = {cop(mc)}"
                for a, nm, p, mc in zip(plan["Activo"], plan["Nombre"], plan["Peso"], plan["Monto COP"])) + \
        "\n\nALERTAS\n" + ("\n".join(f"- {a}" for a in alertas) if alertas else "- Ninguna") + \
        "\n\nNota: herramienta educativa, no constituye asesoría financiera.\n"
    st.download_button("⬇️ Descargar mi plan (TXT)", texto_plan.encode("utf-8"), "mi_plan_inversion.txt", "text/plain")

# ══════════════════════════════════════════════════════════════
# 7. INVERTIR DESDE COLOMBIA
# ══════════════════════════════════════════════════════════════
with tabs[6]:
    st.header("🏦 Invertir desde Colombia")
    st.caption("Información orientativa (nov-2026). Tarifas, productos e impuestos cambian: verifica siempre en la fuente oficial.")

    st.subheader("🧰 Productos disponibles: de menor a mayor riesgo")
    st.dataframe(C.PRODUCTOS, hide_index=True, width="stretch")
    st.caption(C.FOGAFIN_NOTA)

    st.subheader("🏦 ¿Dónde invertir? Tipos de plataformas")
    st.dataframe(C.PLATAFORMAS, hide_index=True, width="stretch")
    st.caption("Las marcas se mencionan como ejemplos ilustrativos, no como recomendación.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(C.CHECKLIST_PLATAFORMA)
    with c2:
        st.markdown("#### 💰 ¿Por dónde empiezo según mi monto?")
        st.markdown(C.RUTAS_POR_MONTO)

    st.subheader("🧮 Calculadora: ¿cuánto se comen los costos?")
    st.markdown("Compara dos alternativas con el mismo rendimiento bruto. Las diferencias en costos se acumulan con los años.")
    cc = st.columns(3)
    monto_c = cc[0].number_input("Monto a invertir (COP)", 100_000, value=int(max(capital, 1_000_000)), step=500_000, key="mc")
    anios_c = cc[1].slider("Años", 1, 30, 15, key="ac")
    bruto = cc[2].number_input("Rendimiento bruto anual esperado (%)", 0.0, 30.0, 10.0, 0.5, key="bc") / 100
    a, b = st.columns(2)
    with a:
        st.markdown("**Opción A** (ej. broker internacional + ETF barato)")
        ini_a = st.number_input("Costo inicial fijo (COP) — giro, comisión", 0, value=100_000, step=10_000, key="ia")
        spr_a = st.number_input("Spread cambiario / comisión de entrada (%)", 0.0, 10.0, 1.0, 0.1, key="sa")
        anu_a = st.number_input("Costo anual (%) — TER, custodia", 0.0, 5.0, 0.10, 0.05, key="ca")
    with b:
        st.markdown("**Opción B** (ej. fondo local con comisión de administración)")
        ini_b = st.number_input("Costo inicial fijo (COP)", 0, value=0, step=10_000, key="ib")
        spr_b = st.number_input("Comisión de entrada (%)", 0.0, 10.0, 0.0, 0.1, key="sb")
        anu_b = st.number_input("Costo anual (%) — administración", 0.0, 5.0, 2.0, 0.05, key="cb")

    def valor_final(ini, spr, anu):
        neto = max(monto_c - ini, 0) * (1 - spr / 100)
        return neto * ((1 + bruto) * (1 - anu / 100)) ** anios_c

    va, vb, sin = valor_final(ini_a, spr_a, anu_a), valor_final(ini_b, spr_b, anu_b), monto_c * (1 + bruto) ** anios_c
    k = st.columns(3)
    k[0].metric("Sin costos", cop(sin))
    k[1].metric("Opción A", cop(va), delta=cop(va - sin) + " por costos", delta_color="inverse")
    k[2].metric("Opción B", cop(vb), delta=cop(vb - sin) + " por costos", delta_color="inverse")
    ganador = "A" if va > vb else "B"
    st.info(f"En {anios_c} años la **opción {ganador}** te deja **{cop(abs(va - vb))}** más. "
            "Los costos fijos pesan más en montos pequeños; los costos anuales pesan más a largo plazo.")

    with st.expander("🧾 Impuestos y aspectos legales (resumen)", expanded=False):
        st.markdown(C.IMPUESTOS)

    st.subheader("🔗 Fuentes oficiales para verificar")
    st.markdown("""
- **Superintendencia Financiera (SFC)** — entidades vigiladas y alertas de entidades no autorizadas: superfinanciera.gov.co
- **AMV** — verificar si un asesor/comercial está certificado: amvcolombia.org.co
- **Fogafín** — seguro de depósitos: fogafin.gov.co
- **Bolsa de Valores de Colombia / nuam** — acciones, ETFs y MGC: bvc.com.co
- **Banco de la República** — TRM, inflación y tasas: banrep.gov.co
- **DIAN** — obligaciones tributarias, UVT vigente: dian.gov.co
""")

# ══════════════════════════════════════════════════════════════
# 8. ACADEMIA
# ══════════════════════════════════════════════════════════════
with tabs[7]:
    st.header("📚 Academia del inversionista")
    sec = st.segmented_control("Sección", ["Conceptos", "Métricas", "Errores comunes", "Pon a prueba lo aprendido"],
                               default="Conceptos")
    if sec == "Conceptos":
        for titulo, texto in E.CONCEPTOS.items():
            with st.expander(titulo):
                st.markdown(texto)
    elif sec == "Métricas":
        st.markdown("Estas son las métricas que ves en la app. Con ellas puedes comparar **cualquier** inversión.")
        for m, d in E.METRICAS.items():
            if not d["larga"]:
                continue
            with st.expander(f"**{m}** — {d['corta']}"):
                st.markdown(d["larga"])
                if d["bueno"]:
                    st.markdown(f"📏 **Referencia:** {d['bueno']}")
                if m in tabla.columns and len(riesgosos):
                    ej = tabla.loc[riesgosos, m]
                    st.caption("En tus activos: " + " · ".join(
                        f"{t}: {pct(v) if m not in ('Sharpe', 'Sortino', 'Calmar') else f'{v:.2f}'}"
                        for t, v in ej.items()))
    elif sec == "Errores comunes":
        st.markdown(E.ERRORES_COMUNES)
    elif sec == "Pon a prueba lo aprendido":
        aciertos = 0
        respondidas = 0
        for i, q in enumerate(E.QUIZ):
            r = st.radio(f"**{i + 1}. {q['p']}**", q["o"], index=None, key=f"quiz_{i}")
            if r is not None:
                respondidas += 1
                if q["o"].index(r) == q["r"]:
                    aciertos += 1
                    st.success(f"✅ Correcto. {q['e']}")
                else:
                    st.error(f"❌ La respuesta es: *{q['o'][q['r']]}*. {q['e']}")
        if respondidas == len(E.QUIZ):
            st.metric("Tu puntaje", f"{aciertos}/{len(E.QUIZ)}")
            if aciertos == len(E.QUIZ):
                st.balloons()
