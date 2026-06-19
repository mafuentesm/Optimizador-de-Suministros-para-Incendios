from gurobipy import GRB, Model, quicksum
from data_reader import leer_datos
from data_validator import validar_demanda

def main():
    #  Carga de Datos 
    (E, S, T, P, C,
     te, Bp, cs, hs, vs, Cape, Maxt, Mint,
     I0, we, Le, As, Us, R0, De, ae, Sc, m_s, M_s) = leer_datos()

    # Indice de cada periodo en la lista P (para acceso por posicion)
    idx_p = {p: i for i, p in enumerate(P)}
    p0    = P[0]  # primer periodo

    #  Validacion de supuesto de demanda factible 
    # Comprueba que De[e,s,p] <= stock maximo acumulable en cada (e,s,p).
    validar_demanda(E, S, P, I0, De, As, ae, R0)

    model = Model()
    model.setParam("TimeLimit", 120)
    model.setParam("OutputFlag", 1)

    # --------- Variables de decision ---------

    # x[e,s,p]: cantidad comprada del suministro s para la estacion e en el periodo p
    x = model.addVars(E, S, P, vtype=GRB.CONTINUOUS, lb=0, name="x")

    # I[e,s,p]: inventario del suministro s en la estacion e al final del periodo p
    I = model.addVars(E, S, P, vtype=GRB.CONTINUOUS, lb=0, name="I")

    # u[e,s,p]: deficit del suministro s en la estacion e durante el periodo p
    u = model.addVars(E, S, P, vtype=GRB.CONTINUOUS, lb=0, name="u")

    z = model.addVars(E, S, P, vtype=GRB.BINARY, lb=0, name="z")

    # R[e,s,p]: unidades del suministro s retiradas de la estacion e en el periodo p por vida util
    R = model.addVars(E, S, P, vtype=GRB.CONTINUOUS, lb=0, name="R")

    # --------- Funcion Objetivo ---------
    obj = quicksum(we[e,s] * u[e,s,p] for e in E for s in S for p in P)
    model.setObjective(obj, GRB.MINIMIZE)

    # --------- Restricciones ---------

    # (2) Restriccion presupuestaria
    # Costo total de compra + almacenamiento no supera el presupuesto del periodo
    model.addConstrs(
        (quicksum(cs[s] * x[e,s,p] for e in E for s in S) +
         quicksum(hs[s] * I[e,s,p] for e in E for s in S) <= Bp[p]
         for p in P),
        name="presupuesto"
    )

    # (3) Balance de inventario en el primer periodo
    # CAMBIO: d[e,s,p0] reemplazado por el parametro De[e,s,p0]
    model.addConstrs(
        (I[e,s,p0] == I0[e,s] + x[e,s,p0] - De[e,s,p0] - R0.get((e,s,p0), 0)
         for e in E for s in S),
        name="balance_p1"
    )

    # (4) Balance de inventario para periodos p > 1
    # CAMBIO: d[e,s,p] reemplazado por el parametro De[e,s,p]
    model.addConstrs(
        (I[e,s,p] == I[e,s, P[idx_p[p]-1]] + x[e,s,p] - De[e,s,p] - R[e,s,p]
         for e in E for s in S for p in P if p != p0),
        name="balance_p"
    )

    # (5) Inventario minimo con captura de deficit
    # Si el inventario no alcanza el minimo, u[e,s,p] absorbe la brecha
    model.addConstrs(
        (I[e,s,p] + u[e,s,p] >= Mint[te[e], s]
         for e in E for s in S for p in P),
        name="inventario_minimo"
    )

    # (6) Capacidad volumetrica de almacenamiento por estacion
    model.addConstrs(
        (quicksum(vs[s] * I[e,s,p] for s in S) <= Cape[e]
         for e in E for p in P),
        name="capacidad_volumetrica"
    )

    # (7) Capacidad maxima de inventario por tipologia de cuartel
    model.addConstrs(
        (I[e,s,p] <= Maxt[te[e], s]
         for e in E for s in S for p in P),
        name="capacidad_tipologia"
    )

    # (8) Cobertura minima por categoria de suministro
    model.addConstrs(
        (quicksum(I[e,s,p] for s in Sc[c]) >= Le[e,c,p]
         for e in E for c in C for p in P),
        name="cobertura_categoria"
    )

    # (9) Disponibilidad maxima en el mercado nacional por suministro y periodo
    model.addConstrs(
        (quicksum(x[e,s,p] for e in E) <= As[s,p]
         for s in S for p in P),
        name="disponibilidad_mercado"
    )

    # (10) Compatibilidad estacion-suministro
    # Si ae[e,s] = 0 la estacion no puede comprar ese suministro
    model.addConstrs(
        (x[e,s,p] <= As[s,p] * ae[e,s]
         for e in E for s in S for p in P),
        name="compatibilidad"
    )

    # (11) Retiro por vida util en periodos iniciales
    model.addConstrs(
        (R[e,s,p] == R0.get((e,s,p), 0)
         for e in E for s in S for p in P
         if idx_p[p] < Us[s]),
        name="retiro_inicial"
    )

    # (12) Retiro por vida util para periodos donde el lote ya vence
    model.addConstrs(
        (R[e,s,p] >= x[e,s, P[idx_p[p] - Us[s]]]
                     - quicksum(De[e,s, P[k]] for k in range(idx_p[p] - Us[s] + 1, idx_p[p] + 1))
         for e in E for s in S for p in P
         if idx_p[p] > Us[s]),
        name="retiro_vida_util"
    )

    # (13) cota superior para retiro por vida util: no se puede retirar mas de lo que se compra del lote que vence
    model.addConstrs(
        (R[e,s,p] <=  x[e,s, P[idx_p[p] - Us[s]]]
         for e in E for s in S for p in P
         if idx_p[p] > Us[s]),
        name="retiro_no_negativo"
    )

    # (14) activacion_compra: si se compra algo del suministro s para la estacion e en el periodo p, entonces z[e,s,p] = 1
    model.addConstrs(
        (x[e,s,p] <= M_s[s] * z[e,s,p]
         for e in E for s in S for p in P),
        name="activacion_compra"
    )

    # (15) compra_minima: si z[e,s,p] = 1 entonces se debe comprar al menos m_s[s] unidades del suministro s para la estacion e en el periodo p
    model.addConstrs(
        (x[e,s,p] >= m_s[s] * z[e,s,p]
         for e in E for s in S for p in P),
        name="compra_minima"
    )

    # ------- Optimizacion ---------
    model.optimize()

    # ------- Manejo de Soluciones -----
    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
        estado = "OPTIMO" if model.status == GRB.OPTIMAL else "LIMITE DE TIEMPO"
        print("-"*50)
        print(f"Estado: {estado}")
        print("-"*50)
        print(f"Valor objetivo: {model.ObjVal:.4f}")
        print(f"Tiempo de ejecucion: {model.Runtime:.4f} segundos\n")

        print("=> Compras realizadas por periodo:")
        for p in P:
            hay_compra = False
            for e in E:
                for s in S:
                    if x[e,s,p].x > 0.01:
                        if not hay_compra:
                            print(f"\n  Periodo {p}:")
                            hay_compra = True
                        print(f"    - Estacion {e} | Suministro {s}: {x[e,s,p].x:.2f} unidades")

        print("\n=> Deficit por periodo (solo si > 0):")
        for p in P:
            for e in E:
                for s in S:
                    if u[e,s,p].x > 0.01:
                        print(f"  Periodo {p} | Estacion {e} | Suministro {s}: "
                              f"deficit = {u[e,s,p].x:.2f} unidades")

        print("\n=> Retiros por vencimiento de vida util (solo si > 0):")
        for p in P:
            for e in E:
                for s in S:
                    if R[e,s,p].x > 0.01:
                        print(f"  Periodo {p} | Estacion {e} | Suministro {s}: "
                              f"retiro = {R[e,s,p].x:.2f} unidades")

        print("\n=> Inventario final por periodo:")
        for p in P:
            print(f"\n  Periodo {p}:")
            for e in E:
                for s in S:
                    if I[e,s,p].x > 0.01:
                        print(f"    - Estacion {e} | Suministro {s}: "
                              f"{I[e,s,p].x:.2f} unidades en inventario")
        print("-"*50)
    else:
        print("\nEstado: Infactible o No Acotado.")

if __name__ == "__main__":
    main()