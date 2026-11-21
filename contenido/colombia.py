"""
Contenido sobre opciones de inversión para residentes en Colombia.

IMPORTANTE: condiciones comerciales, tarifas e impuestos cambian con frecuencia.
La información es orientativa (revisada a nov-2026) y debe verificarse en la
fuente oficial de cada entidad, la Superintendencia Financiera (SFC) y la DIAN.
"""
import pandas as pd

PRODUCTOS = pd.DataFrame([
    dict(Producto="Cuenta de ahorro remunerada / 'bolsillos'", Riesgo="Muy bajo", Liquidez="Inmediata",
         Rendimiento="Variable, cercano a tasas de mercado", Protección="Fogafín*",
         Ideal_para="Fondo de emergencia, metas < 1 año",
         Dónde="Bancos y neobancos vigilados por la SFC"),
    dict(Producto="CDT", Riesgo="Muy bajo", Liquidez="Al vencimiento (30 días a 5 años)",
         Rendimiento="Tasa fija E.A. pactada", Protección="Fogafín*",
         Ideal_para="Metas de 3 meses a 3 años, perfil conservador",
         Dónde="Bancos, compañías de financiamiento; también en mercado secundario vía comisionista"),
    dict(Producto="Fondo de Inversión Colectiva (FIC)", Riesgo="Bajo a alto (según el fondo)",
         Liquidez="Desde 1 día (fondos a la vista) hasta plazos fijos", Rendimiento="Variable, no garantizado",
         Protección="Activos separados de la fiduciaria; NO Fogafín",
         Ideal_para="Empezar con montos pequeños con gestión profesional",
         Dónde="Fiduciarias, comisionistas, apps como tyba"),
    dict(Producto="TES (bonos del Gobierno)", Riesgo="Bajo-medio (sube/baja con las tasas)",
         Liquidez="Alta en mercado secundario", Rendimiento="Cupón fijo o atado a UVR (inflación)",
         Protección="Respaldo de la Nación", Ideal_para="Renta fija en pesos a mediano/largo plazo",
         Dónde="Comisionistas de bolsa, bancos; FICs de TES"),
    dict(Producto="Fondos de pensiones voluntarias / cuentas AFC",
         Riesgo="Según el portafolio elegido", Liquidez="Baja (condiciones para retirar sin perder beneficio)",
         Rendimiento="Variable", Protección="Patrimonio separado",
         Ideal_para="Largo plazo + beneficio tributario (renta exenta con límites)",
         Dónde="AFP (Porvenir, Protección, Colfondos, Skandia) y bancos (AFC)"),
    dict(Producto="Acciones y ETFs de la Bolsa de Colombia (BVC/nuam)", Riesgo="Alto",
         Liquidez="Alta (días hábiles)", Rendimiento="Variable + dividendos", Protección="Custodio (Deceval)",
         Ideal_para="Exposición a empresas colombianas, en pesos",
         Dónde="Comisionistas de bolsa y apps como trii"),
    dict(Producto="ETFs internacionales vía MGC (Mercado Global Colombiano)", Riesgo="Medio-alto",
         Liquidez="Alta", Rendimiento="Variable (incluye efecto dólar)", Protección="Custodio local",
         Ideal_para="Diversificar globalmente pagando en pesos, sin abrir cuenta en el exterior",
         Dónde="Comisionistas de bolsa y apps locales (catálogo limitado)"),
    dict(Producto="ETFs/acciones en broker internacional", Riesgo="Medio-alto",
         Liquidez="Alta", Rendimiento="Variable (en dólares)",
         Protección="Regulación del país del broker (ej. SIPC en EE.UU.); NO SFC",
         Ideal_para="Mayor catálogo y costos bajos para montos medianos/grandes",
         Dónde="Interactive Brokers, apps como Hapi, entre otros"),
]).rename(columns={"Ideal_para": "Ideal para"})

FOGAFIN_NOTA = (
    "\\* **Fogafín** (seguro de depósitos) cubre los ahorros en cuentas y CDT de entidades inscritas, "
    "hasta un tope por persona y por entidad (al momento de esta guía, **COP 50 millones**). "
    "Verifica el tope vigente en fogafin.gov.co. Los FIC, acciones y ETFs **no** están cubiertos por Fogafín."
)

PLATAFORMAS = pd.DataFrame([
    dict(Tipo="Comisionista de bolsa tradicional",
         Ejemplos="Acciones & Valores, Credicorp Capital, Davivienda Corredores, BTG Pactual, Casa de Bolsa, Itaú Comisionista",
         Acceso="BVC, MGC, TES, CDT, FIC, a veces mercados internacionales", Vigilada_SFC="Sí",
         Ventajas="Asesoría, todo en pesos, reporte tributario local", Desventajas="Comisiones y montos mínimos más altos"),
    dict(Tipo="App colombiana de inversión",
         Ejemplos="trii (acciones/ETFs), tyba (FIC y portafolios)",
         Acceso="Acciones BVC, ETFs locales, MGC, FIC; algunas ofrecen acciones de EE.UU.",
         Vigilada_SFC="Operan con/como entidades vigiladas (verifica el aliado)",
         Ventajas="Montos bajos, fácil de usar, en pesos", Desventajas="Catálogo internacional limitado"),
    dict(Tipo="Broker internacional",
         Ejemplos="Interactive Brokers (EE.UU./Irlanda)",
         Acceso="Miles de ETFs (EE.UU. y UCITS de Irlanda), acciones, bonos globales",
         Vigilada_SFC="No (regulado en el exterior)",
         Ventajas="Costos de operación muy bajos, máxima diversificación",
         Desventajas="Giro de dólares (costo + spread), más trámites, declarar activos en el exterior"),
    dict(Tipo="App internacional para Latam",
         Ejemplos="Hapi, eToro, entre otras",
         Acceso="Acciones y ETFs de EE.UU., fracciones de acción",
         Vigilada_SFC="No (reguladas en el exterior)",
         Ventajas="Fácil, fracciones desde pocos dólares",
         Desventajas="Revisa custodio, costos de fondeo/retiro y evita productos apalancados (CFDs)"),
    dict(Tipo="Bancos y neobancos",
         Ejemplos="Bancos tradicionales, Nu, Lulo Bank, Pibank, entre otros",
         Acceso="Cuentas remuneradas, CDT", Vigilada_SFC="Sí",
         Ventajas="Seguro Fogafín, liquidez", Desventajas="Rendimiento limitado a largo plazo"),
]).rename(columns={"Vigilada_SFC": "¿Vigilada por SFC?"})

CHECKLIST_PLATAFORMA = """
**Antes de abrir una cuenta, verifica:**
1. ¿La entidad (o su aliado custodio) está **vigilada por la Superintendencia Financiera**? Búscala en
   *superfinanciera.gov.co → Entidades vigiladas*. Si es extranjera, ¿qué regulador la supervisa (SEC/FINRA, CBI, etc.)?
2. ¿Quién **custodia** tus activos? (Deceval en Colombia; un custodio regulado en el exterior).
3. **Costos totales**: comisión por operación, custodia, giro, spread cambiario, retiro, inactividad.
4. ¿Ofrece **reporte tributario** (certificado para la declaración de renta)?
5. ¿Permite **fracciones** y **aportes automáticos**?
6. ¿Cómo es el **retiro** del dinero a tu cuenta en Colombia y cuánto tarda?
7. 🚩 Huye si: promete rentabilidad fija alta, pide referir personas, maneja tu dinero "por ti" sin contrato
   con entidad vigilada, o solo acepta cripto/transferencias a personas naturales.
"""

IMPUESTOS = """
> ⚠️ Resumen **general y orientativo**. Las normas tributarias cambian (reformas frecuentes). Valida con un contador
> o en **dian.gov.co** antes de tomar decisiones.

**Al mover dinero**
- **GMF (4x1000)**: se cobra al retirar/transferir desde cuentas bancarias (existe una cuenta marcada como exenta hasta cierto monto mensual).

**Rendimientos de renta fija (CDT, cuentas, bonos)**
- Se aplica **retención en la fuente** sobre los rendimientos (en CDT suele ser **4%** del rendimiento).
- Hacen parte de tus ingresos en la declaración de renta (existe el "componente inflacionario" no gravado, con reglas propias).

**Acciones de la Bolsa de Colombia**
- La utilidad en la venta de acciones inscritas en la BVC **no es renta gravada** si no vendes más del **10%** de la
  empresa en un año (Art. 36-1 del Estatuto Tributario).
- Los **dividendos** sí tributan según la tabla para dividendos de personas naturales.

**Inversiones en el exterior (ETFs de EE.UU., broker internacional)**
- Las **ganancias** al vender son gravables en Colombia: como **ganancia ocasional (15%)** si poseíste el activo
  2 años o más; si es menos, como renta ordinaria.
- Los **dividendos de EE.UU.** tienen una retención en EE.UU. de **30%** para residentes colombianos
  (no hay convenio de doble imposición Colombia–EE.UU.). Algunos inversionistas prefieren **ETFs UCITS domiciliados en
  Irlanda de acumulación** (reinvierten dividendos y tienen retención interna menor).
- **Impuesto de sucesiones de EE.UU.**: los no residentes con más de **USD 60.000** en activos situados en EE.UU.
  (ej. ETFs como SPY/VOO) podrían estar expuestos a este impuesto en caso de fallecimiento. Los ETFs irlandeses lo evitan.
- Debes **declarar los activos** y, si superan cierto valor (2.000 UVT), presentar la **declaración de activos en el exterior**.
- Convierte compras y ventas a pesos con la **TRM** del día de cada operación y guarda los extractos.

**Beneficios tributarios**
- Aportes a **pensiones voluntarias** y **cuentas AFC** pueden ser **renta exenta**, con límites (porcentaje del ingreso y
  tope en UVT) y condiciones de permanencia.

**¿Tengo que declarar renta?** Depende de tus ingresos, patrimonio, consumos con tarjeta y movimientos bancarios del año
(topes en UVT que la DIAN actualiza cada año).
"""

RUTAS_POR_MONTO = """
| Si tienes… | Ruta sugerida para empezar |
|---|---|
| **Menos de COP 1 millón** | Cuenta remunerada o FIC a la vista; empieza el hábito con aportes mensuales en una app local (ETF iCOLCAP o fondos). |
| **COP 1 – 20 millones** | Fondo de emergencia en CDT/cuenta + ETFs globales vía **MGC** o app local, o una app internacional con fracciones. |
| **Más de COP 20 millones** | Considera un **broker internacional** (costos más bajos por operación compensan el giro) con 2-4 ETFs diversificados + renta fija en pesos (CDT/TES). |

*Regla práctica:* si el costo fijo de girar dinero al exterior es mayor al **1%** de lo que vas a invertir, es mejor
acumular varios meses de aportes antes de girar, o usar opciones locales.
"""
