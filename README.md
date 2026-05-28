## Contexto del Mock Data

### Suministros

| ID | Nombre | Descripción |
|---|---|---|
| s=1 | Retardante AF7000 | Químico líquido que crea barreras ignífugas. Consumo masivo en temporada de incendios |
| s=2 | Combustible motobomba | Diésel para operar las bombas de agua. Se consume en cada emergencia activa |
| s=3 | EPP uniforme estructural | Traje de protección completo contra fuego y calor extremo. Larga vida útil pero alto costo |
| s=4 | Filtro ERA | Filtro de aire para equipos de respiración autónoma. Se reemplaza tras cada exposición a humo |

---

### Criticidad `we,s`

Calculada con `we,s = α·ks + β·(5 - te)`, con `α = 0.6`, `β = 0.4`.

**Índice de criticidad por suministro `ks`:**

| Suministro | ks | Justificación |
|---|---|---|
| s=1 Retardante | 9 | Sin él no se puede crear barrera química. No hay plan B en incendio forestal activo |
| s=2 Combustible | 8 | Sin combustible la motobomba no opera. Alternativas manuales son insuficientes a escala |
| s=3 EPP uniforme | 7 | Indispensable para proteger al voluntario, pero puede reutilizarse varios turnos si está en buen estado |
| s=4 Filtro ERA | 6 | Crítico en ambientes con humo denso, pero en incendios forestales abiertos puede prescindirse brevemente |

**Resultado `we,s` por estación:**

Los valores reflejan que estaciones en zonas de mayor riesgo (tipo 1, urbano-forestal) tienen criticidad más alta que estaciones rurales pequeñas (tipo 4):

| | s=1 | s=2 | s=3 | s=4 |
|---|---|---|---|---|
| e=1 (tipo 1) | 7.0 | 6.4 | 5.8 | 5.2 |
| e=2 (tipo 2) | 7.0 | 6.4 | 5.8 | 5.2 |
| e=3 (tipo 4) | 5.8 | 5.2 | 0.0 | 4.0 |

La criticidad de s=3 en e=3 es 0 porque `ae[3,3] = 0`: la estación rural no tiene infraestructura ni personal capacitado para manipular EPP estructural especializado, por lo que penalizar su déficit no tiene sentido operativo.

---

### Categorías

| ID | Nombre | Suministros | Justificación |
|---|---|---|---|
| c=1 | Agentes extintores | s=1 retardante, s=2 combustible | Insumos directamente involucrados en el combate activo del fuego. Su ausencia paraliza la operación |
| c=2 | Equipamiento personal | s=3 EPP uniforme, s=4 filtro ERA | Protegen la integridad física del voluntario. Su ausencia impide el ingreso a zonas de peligro |

La cobertura mínima `Le,c,p` exige que el inventario combinado de cada categoría no baje de un umbral operativo, independientemente de cómo se distribuya entre los suministros que la componen.

---

### Períodos

El horizonte cubre **3 meses de la temporada estival 2026** en la Región del Biobío:

| Período | Mes | Característica operativa |
|---|---|---|
| p=1 | Enero | Peak de incendios. Temperatura >35°C, vientos Puelche, humedad <20%. Demanda máxima de retardante y combustible. Presupuesto más alto ($50M) por asignación de emergencia |
| p=2 | Febrero | Temporada activa pero decreciente. Reposición de EPP dañado en p=1. Presupuesto medio ($35M) |
| p=3 | Marzo | Fin de temporada. Demanda cae, se prioriza reposición de filtros ERA consumidos y mantención de stock mínimo para emergencias tardías. Presupuesto más bajo ($30M) |

La vida útil de cada suministro en este contexto es:

| Suministro | Us | Interpretación |
|---|---|---|
| s=1 Retardante | 6 meses | Se degrada químicamente si se almacena más de 6 meses abierto |
| s=2 Combustible | 3 meses | Diésel almacenado pierde propiedades de combustión pasados 3 meses |
| s=3 EPP uniforme | 12 meses | Vida útil de un año bajo uso intensivo o dos años con uso moderado |
| s=4 Filtro ERA | 6 meses | El material filtrante se satura con humedad ambiental aunque no se use |

El combustible (s=2) con `Us=3` es el único suministro cuya vida útil coincide con el horizonte completo, lo que activa retiros desde `retiro_inicial.csv` ya en p=1 para el stock inicial que entró en bodega en octubre 2025.