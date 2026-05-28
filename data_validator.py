def validar_demanda(E, S, P, I0, De, As, ae, R0):
    """
    Verifica el supuesto: De[e,s,p] <= stock disponible acumulado hasta p.
 
    El stock maximo acumulable hasta el periodo p es:
        I0[e,s]
        + sum_{q=1}^{p} As[s,q] * ae[e,s]   <- maximo comprable (mercado x compatibilidad)
        - sum_{q=1}^{p} R0[e,s,q]            <- retiros programados del inventario inicial
 
    Si la demanda acumulada supera este techo en algun (e,s,p), el modelo
    sera infactible por construccion. Se reportan todos los casos antes de
    llamar a Gurobi para facilitar la correccion de los datos.
    """
    errores = []
 
    for e in E:
        for s in S:
            demanda_acum   = 0.0
            compra_max_acum = 0.0
            retiro_acum    = 0.0
 
            for p in P:
                demanda_acum    += De.get((e, s, p), 0.0)
                compra_max_acum += As.get((s, p), 0.0) * ae.get((e, s), 0)
                retiro_acum     += R0.get((e, s, p), 0.0)
 
                stock_max_neto = I0.get((e, s), 0.0) + compra_max_acum - retiro_acum
 
                if demanda_acum > stock_max_neto + 1e-6:  # tolerancia numerica
                    errores.append(
                        f"  [e={e}, s={s}, p={p}] "
                        f"demanda acumulada ({demanda_acum:.2f}) "
                        f"> stock maximo neto ({stock_max_neto:.2f})"
                    )
 
    if errores:
        print("=" * 55)
        print("ERROR: supuesto de demanda factible VIOLADO.")
        print("Casos inconsistentes detectados:")
        for err in errores:
            print(err)
        print("=" * 55)
        raise ValueError(
            "Datos inconsistentes: corrige demanda.csv o disponibilidad.csv "
            "antes de optimizar."
        )
 
    print("Validacion de demanda: OK.")