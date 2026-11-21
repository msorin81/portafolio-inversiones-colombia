"""Textos educativos de la app (en lenguaje sencillo para principiantes)."""

# ── Explicación corta de cada métrica (se usa en tooltips y en la Academia) ──
METRICAS = {
    "Rend. anual (CAGR)": dict(
        corta="Cuánto creció tu dinero en promedio cada año, con interés compuesto.",
        larga="La **tasa de crecimiento anual compuesta** responde: *si el activo hubiera crecido "
              "a un ritmo constante, ¿qué tasa anual habría tenido?* Ej.: 10.000.000 → 16.105.100 en 5 años "
              "es un CAGR de 10%. Es comparable con la tasa E.A. de un CDT.",
        bueno="Compárala con un CDT y con la inflación. Si no supera al CDT, el riesgo no se está pagando."),
    "Volatilidad": dict(
        corta="Qué tanto sube y baja el precio. Más volatilidad = viaje más movido.",
        larga="Es la desviación estándar anualizada de los rendimientos. Una volatilidad de 15% significa que, "
              "en un año típico (2 de cada 3 años), el rendimiento estará aproximadamente entre "
              "*promedio − 15%* y *promedio + 15%*.",
        bueno="Bonos de corto plazo: 1-3%. Bonos largos: 10-17%. Acciones globales: 15-20%. Acción individual: 25-40%+"),
    "Sharpe": dict(
        corta="Rendimiento extra (sobre un CDT) por cada unidad de riesgo. Más alto = mejor.",
        larga="(Rendimiento − tasa libre de riesgo) / Volatilidad. Mide si el riesgo que asumes "
              "se está pagando. Si es negativo, te habría ido mejor en un CDT o en bonos del gobierno.",
        bueno="< 0: malo · 0-0,5: regular · 0,5-1: bueno · > 1: muy bueno (y raro a largo plazo)."),
    "Sortino": dict(
        corta="Como el Sharpe, pero solo castiga las caídas (no las subidas).",
        larga="Usa solo la volatilidad de los días negativos. Es más justo con activos que suben mucho de golpe.",
        bueno="Se interpreta igual que el Sharpe; suele ser algo mayor."),
    "Máx. caída": dict(
        corta="La peor caída desde un máximo hasta un mínimo (drawdown). Es lo que más duele.",
        larga="Si un activo llegó a valer 100, cayó a 65 y luego se recuperó, su máxima caída es −35%. "
              "Pregúntate: *¿habría aguantado sin vender viendo mi inversión caer así?*. Ojo: después de caer 50% "
              "necesitas subir 100% para recuperarte.",
        bueno="La mayoría de principiantes venden en pánico con caídas de −20% a −30%. Escoge según tu estómago."),
    "Calmar": dict(
        corta="Rendimiento anual dividido entre la peor caída.",
        larga="Responde: *¿cuánto gané por cada punto de caída máxima que tuve que soportar?*",
        bueno="> 0,5 es razonable; > 1 es excelente."),
    "VaR 95% mensual": dict(
        corta="En 19 de cada 20 meses, no perderías más que este porcentaje.",
        larga="Valor en Riesgo: el 5% de los peores meses históricos tuvieron pérdidas mayores a este número. "
              "**No** es la pérdida máxima posible.",
        bueno="Útil para saber cuánto podría caer tu inversión en un mes malo 'normal'."),
    "CVaR 95% mensual": dict(
        corta="Pérdida promedio en ese 5% de peores meses.",
        larga="También llamado *Expected Shortfall*. Responde: *cuando las cosas van mal de verdad, ¿cuánto pierdo en promedio?*",
        bueno="Siempre es mayor que el VaR. Mide el riesgo de cola."),
    "Meses positivos": dict(
        corta="Porcentaje de meses en que el activo subió.",
        larga="Recuerda que incluso las mejores inversiones tienen 35-40% de meses negativos. Es normal.",
        bueno="Acciones: ~60%. Bonos cortos: 70-90%."),
    "Mejor año": dict(corta="El mejor año calendario del periodo.", larga="", bueno=""),
    "Peor año": dict(corta="El peor año calendario del periodo.", larga="", bueno=""),
    "Rend. acumulado": dict(corta="Ganancia total de todo el periodo.", larga="", bueno=""),
}

CONCEPTOS = {
    "📦 ¿Qué es un ETF?": """
Un **ETF** (*Exchange Traded Fund*) es una "canasta" de muchas acciones o bonos que compras como si fuera una sola acción.
Por ejemplo, con **una** unidad de `VT` eres dueño de un pedacito de ~9.000 empresas del mundo.

- ✅ Diversificación inmediata con poco dinero
- ✅ Costos bajos (0,03%–0,5% al año, llamado *expense ratio* o TER)
- ✅ Se compran y venden en bolsa cualquier día hábil
- ⚠️ Su valor sube y baja con el mercado: **no hay rentabilidad garantizada**

En Colombia existen ETFs locales (ej. **iCOLCAP**) y puedes comprar ETFs extranjeros vía el **Mercado Global Colombiano (MGC)**
o un broker internacional.
""",
    "🧺 Diversificación y correlación": """
**No pongas todos los huevos en la misma canasta.** Diversificar es combinar activos que **no** se mueven igual.

La **correlación** va de −1 a +1:
- **+1**: se mueven idéntico (no diversifica nada). Ej.: SPY y VOO ≈ 1,0.
- **0**: no tienen relación.
- **−1**: cuando uno sube, el otro baja (diversificación perfecta).

Combinar acciones con bonos y oro suele **reducir la volatilidad sin sacrificar tanto rendimiento**.
Es lo único "gratis" en las inversiones.
""",
    "📈 Frontera eficiente (Markowitz)": """
Harry Markowitz (Nobel de Economía, 1990) mostró que, para cada nivel de riesgo, existe una combinación de activos que da el
**máximo rendimiento posible**. La curva que une esas combinaciones es la **frontera eficiente**.

- **Máximo Sharpe**: el portafolio con la mejor relación rendimiento/riesgo.
- **Mínima volatilidad**: el más estable posible.

⚠️ **Advertencia importante**: la optimización usa datos del pasado. Tiende a sobreponderar lo que mejor le fue
recientemente (*"maximizador de errores"*). Por eso la app permite **limitar el peso máximo por activo** y ofrece
estrategias más robustas como **paridad de riesgo** o **pesos iguales**.
""",
    "⚖️ Paridad de riesgo": """
En lugar de repartir el **dinero** por partes iguales, reparte el **riesgo** por partes iguales.
Los activos más volátiles (acciones) reciben menos peso y los más estables (bonos) más.
No depende de pronosticar rendimientos, por eso suele ser más robusta fuera de muestra.
""",
    "💱 El dólar y el peso (riesgo cambiario)": """
Si inviertes en un ETF en dólares, tu rendimiento **en pesos** depende de dos cosas:

> Rendimiento en COP ≈ Rendimiento del ETF en USD + Variación del dólar (TRM)

- Si el dólar **sube** (el peso se devalúa), ganas más en pesos.
- Si el dólar **baja**, ganas menos o pierdes aunque el ETF haya subido.

Dato útil: el peso colombiano suele **devaluarse en las crisis** globales, justo cuando caen las acciones. Por eso tener
parte del portafolio en dólares **amortigua** las caídas medidas en pesos. Esta app te deja ver todo en **COP** para que
veas el efecto real en tu bolsillo.
""",
    "🗓️ Invertir mes a mes (DCA)": """
**Dollar Cost Averaging / Promedio de costo**: invertir una cantidad fija cada mes, sin importar si el mercado sube o baja.

- Compras más unidades cuando está barato y menos cuando está caro.
- Elimina la tentación de "adivinar el momento" (nadie puede hacerlo consistentemente).
- Convierte la inversión en un **hábito**, como pagar un servicio.

Para un principiante, **la constancia vale más que elegir el activo perfecto**.
""",
    "🔄 Rebalanceo": """
Con el tiempo, lo que más sube pesa más de lo planeado. **Rebalancear** es volver a los porcentajes objetivo
(vender un poco de lo que subió y comprar lo que bajó), por ejemplo **una vez al año** o cuando un activo se desvíe
más de 5 puntos de su objetivo. Tip: rebalancea usando los **aportes nuevos** para evitar costos e impuestos por vender.
""",
    "🧾 Costos: el enemigo silencioso": """
Una comisión de 2% anual parece poco, pero en 20 años se come **más de un tercio** de tu ganancia.
Revisa siempre:
- **Comisión por operación** del broker
- **Costo del giro internacional** y **diferencial cambiario** (spread) al pasar pesos a dólares
- **Expense ratio/TER** del ETF o comisión de administración del fondo
- **4x1000 (GMF)** al mover dinero en Colombia
Usa la calculadora de costos en la pestaña *Invertir desde Colombia*.
""",
}

ERRORES_COMUNES = """
1. **Invertir el dinero de emergencias.** Primero ahorra 3 a 6 meses de gastos en algo líquido y seguro.
2. **Invertir teniendo deudas caras.** Pagar una tarjeta de crédito al ~25-30% E.A. es una "inversión" garantizada imbatible.
3. **Vender en pánico** cuando el mercado cae. Las caídas son temporales; vender las vuelve permanentes.
4. **Perseguir lo que más subió** el año pasado (cripto, una acción de moda, "el ETF del momento").
5. **Concentrarse en 1-2 acciones** individuales (incluida la empresa donde trabajas).
6. **Caer en estafas**: rentabilidades "fijas" de 3-10% *mensual*, multinivel, "trading de forex automático",
   "señales" por Telegram. Si suena demasiado bueno para ser verdad, lo es.
7. **Ignorar costos e impuestos.**
8. **Revisar el portafolio todos los días.** Genera ansiedad y malas decisiones. Revisa cada mes o trimestre.
9. **Confundir esta optimización con una predicción.** El pasado no garantiza el futuro.
"""

RUTA_PRINCIPIANTE = [
    ("Ordena tus finanzas", "Presupuesto claro, sin deudas de consumo caras (tarjetas, libranzas, créditos rotativos)."),
    ("Fondo de emergencia", "3 a 6 meses de gastos en una cuenta remunerada o CDT corto, protegidos por Fogafín."),
    ("Define metas y plazos", "¿Para qué inviertes? ¿Cuándo necesitarás el dinero? (< 1 año, 1-5 años, > 5 años)."),
    ("Conoce tu perfil de riesgo", "Pestaña 🧭 Mi perfil: cuánta caída aguantas sin vender."),
    ("Escoge vehículo y plataforma", "Pestaña 🏦 Invertir desde Colombia: CDT, FIC, ETFs locales, MGC o broker internacional."),
    ("Arma tu portafolio", "Pestaña ⚖️ Portafolio: pocos ETFs diversificados, peso máximo por activo."),
    ("Automatiza aportes", "Invierte un monto fijo cada mes (DCA) y rebalancea una vez al año."),
    ("Declara e infórmate", "Lleva registro de compras/ventas para tu declaración de renta. Consulta un contador."),
]

QUIZ = [
    dict(p="Un ETF con volatilidad de 30% frente a uno con 10%...",
         o=["Rinde siempre el triple", "Tiene variaciones de precio mucho más fuertes", "Es más seguro"],
         r=1, e="La volatilidad mide cuánto se mueve el precio, no cuánto rinde."),
    dict(p="Un Sharpe ratio negativo significa que...",
         o=["El activo rindió menos que la tasa libre de riesgo (ej. CDT)", "El activo no tiene riesgo", "Es un error de cálculo"],
         r=0, e="Si el Sharpe es negativo, habrías ganado más en una inversión 'segura'."),
    dict(p="Si tu inversión cae 50%, ¿cuánto debe subir para recuperarse?",
         o=["50%", "75%", "100%"], r=2, e="De 100 a 50 es −50%; de 50 a 100 es +100%. Por eso las caídas grandes pesan tanto."),
    dict(p="Te ofrecen una rentabilidad garantizada del 5% mensual. Lo correcto es...",
         o=["Invertir rápido antes de que se acabe", "Desconfiar y verificar si la entidad está vigilada por la Superfinanciera",
            "Invertir solo una parte"],
         r=1, e="5% mensual es ~80% anual. Ninguna inversión legítima garantiza eso. Señal típica de pirámide."),
    dict(p="El peso colombiano se devalúa fuerte. Tu ETF en dólares, medido en pesos...",
         o=["Vale más", "Vale menos", "No cambia"],
         r=0, e="Cada dólar te compra más pesos, así que tu inversión vale más en COP."),
    dict(p="¿Qué debes tener ANTES de invertir en acciones?",
         o=["Un fondo de emergencia y sin deudas caras", "Un curso de trading", "Al menos 100 millones"],
         r=0, e="Sin colchón, cualquier imprevisto te obliga a vender en el peor momento."),
]

DISCLAIMER = (
    "⚠️ **Herramienta educativa.** Los resultados se basan en datos históricos y simulaciones; "
    "rendimientos pasados **no garantizan** resultados futuros. Esto **no** constituye asesoría financiera, "
    "tributaria ni legal. Antes de invertir, verifica la información vigente y, si lo necesitas, consulta un "
    "asesor certificado (AMV) y un contador."
)
