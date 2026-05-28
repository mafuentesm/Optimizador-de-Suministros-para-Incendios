import csv

def leer_datos():
    E = []        # estaciones de bomberos
    S = []        # suministros
    T = [1,2,3,4] # tipologias de cuarteles
    P = []        # periodos de planificacion
    C = []        # categorias de suministros

    te = {}    # tipo de cuartel de estacion e                                  -> te[e]
    Bp = {}    # presupuesto disponible en periodo p                            -> Bp[p]
    cs = {}    # costo unitario de compra del suministro s                      -> cs[s]
    hs = {}    # costo unitario de almacenamiento del suministro s por periodo  -> hs[s]
    vs = {}    # volumen requerido por unidad del suministro s                  -> vs[s]
    Cape = {}    # capacidad volumetrica de almacenamiento de la estacion e     -> Cape[e]
    Maxt = {}    # inventario maximo del suministro s en cuartel tipo t         -> Maxt[t,s]
    Mint = {}    # inventario minimo del suministro s en cuartel tipo t         -> Mint[t,s]
    I0 = {}    # inventario inicial del suministro s en estacion e              -> I0[e,s]
    we = {}    # grado de criticidad del suministro s en estacion e             -> we[e,s]
    Le = {}    # cobertura minima de categoria c para estacion e en periodo p   -> Le[e,c,p]
    As = {}    # disponibilidad maxima en mercado del suministro s en periodo p -> As[s,p]
    Us = {}    # vida util del suministro s en numero de periodos               -> Us[s]
    R0 = {}    # retiro inicial programado de suministro s en estacion e                -> R0[e,s,p]
    De = {}    # (nuevo) demanda conocida del suministro s en estacion e en periodo p   -> De[e,s,p]
    ae = {}    # compatibilidad estacion-suministro (binario)                   -> ae[e,s]
    Sc = {}    # subconjunto de suministros por categoria c                     -> Sc[c]
    m_s = {}    # compra minima del suministro s (reemplaza a Ms[s] al eliminar ze,s,p) -> m_s[s]
    M_s = {}    # compra maxima del suministro s (reemplaza a ms[s] al eliminar ze,s,p) -> M_s[s]

    # ---- Estaciones ----
    with open('estaciones.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for fila in reader:
            if not fila or not fila[0].strip(): continue
            e = int(fila[0])
            E.append(e)
            te[e] = int(fila[1])
            Cape[e] = float(fila[2])

    # ---- Suministros ----
    # CAMBIO: se eliminan ms y Ms (compra minima/maxima) al quitar ze,s,p
    with open('suministros.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for fila in reader:
            if not fila or not fila[0].strip(): continue
            s = int(fila[0])
            S.append(s)
            cs[s] = float(fila[1])
            hs[s] = float(fila[2])
            vs[s] = float(fila[3])
            Us[s] = int(fila[4])
            m_s[s] = int(fila[5])
            M_s[s] = int(fila[6])

    # ---- Periodos y presupuesto ----
    with open('presupuesto.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for fila in reader:
            if not fila or not fila[0].strip(): continue
            p = int(fila[0])
            P.append(p)
            Bp[p] = float(fila[1])

    # ---- Inventario maximo y minimo por tipologia ----
    with open('capacidad_tipologia.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for fila in reader:
            if not fila or not fila[0].strip(): continue
            t = int(fila[0])
            s = int(fila[1])
            Maxt[t,s] = float(fila[2])
            Mint[t,s] = float(fila[3])

    # ---- Inventario inicial ----
    with open('inventario_inicial.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        encabezado = next(reader)
        S_cols = [int(x) for x in encabezado[1:]]
        for fila in reader:
            if not fila or not fila[0].strip(): continue
            e = int(fila[0])
            for idx, s in enumerate(S_cols):
                I0[e,s] = float(fila[idx + 1])

    # ---- Retiro inicial programado ----
    # CAMBIO: R0 ahora tiene tres indices (e, s, p) consistente con su uso en restricciones
    with open('retiro_inicial.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for fila in reader:
            if not fila or not fila[0].strip(): continue
            e = int(fila[0])
            s = int(fila[1])
            p = int(fila[2])
            R0[e,s,p] = float(fila[3])

    # ---- Demanda por estacion, suministro y periodo ----
    # Formato: filas = estacion-suministro, columnas = periodos
    with open('demanda.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        encabezado = next(reader)
        P_cols = [int(x) for x in encabezado[2:]]
        for fila in reader:
            if not fila or not fila[0].strip(): continue
            e = int(fila[0])
            s = int(fila[1])
            for idx, p in enumerate(P_cols):
                De[e,s,p] = float(fila[idx + 2])

    # ---- Compatibilidad estacion-suministro ----
    with open('compatibilidad.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        encabezado = next(reader)
        S_cols = [int(x) for x in encabezado[1:]]
        for fila in reader:
            if not fila or not fila[0].strip(): continue
            e = int(fila[0])
            for idx, s in enumerate(S_cols):
                ae[e,s] = int(fila[idx + 1])

    # ---- Criticidad ----
    with open('criticidad.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        encabezado = next(reader)
        S_cols = [int(x) for x in encabezado[1:]]
        for fila in reader:
            if not fila or not fila[0].strip(): continue
            e = int(fila[0])
            for idx, s in enumerate(S_cols):
                we[e,s] = float(fila[idx + 1])

    # ---- Disponibilidad de mercado ----
    with open('disponibilidad.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        encabezado = next(reader)
        P_cols = [int(x) for x in encabezado[1:]]
        for fila in reader:
            if not fila or not fila[0].strip(): continue
            s = int(fila[0])
            for idx, p in enumerate(P_cols):
                As[s,p] = float(fila[idx + 1])

    # ---- Categorias y cobertura minima ----
    with open('categorias.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for fila in reader:
            if not fila or not fila[0].strip(): continue
            c = int(fila[0])
            s = int(fila[1])
            if c not in C:
                C.append(c)
                Sc[c] = []
            Sc[c].append(s)

    with open('cobertura_minima.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for fila in reader:
            if not fila or not fila[0].strip(): continue
            e = int(fila[0])
            c = int(fila[1])
            p = int(fila[2])
            Le[e,c,p] = float(fila[3])

    return (E, S, T, P, C,
            te, Bp, cs, hs, vs, Cape, Maxt, Mint,
            I0, we, Le, As, Us, R0, De, ae, Sc, m_s, M_s)