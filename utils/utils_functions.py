from datetime import datetime, timedelta

def contar_sabados_en_bimestre(bimestre):
    fecha_actual = datetime.now()
    # Calcular el primer día del bimestre
    mes_inicio = (bimestre-1) * 2 + 1
    primer_dia_bimestre = fecha_actual.replace(month=mes_inicio, day=1)

    # Contar sábados desde el inicio del bimestre hasta hoy
    contador = 0
    dia_actual = primer_dia_bimestre

    while dia_actual <= fecha_actual:
        if dia_actual.weekday() == 5:  # 5 = Sábado
            contador += 1
        dia_actual += timedelta(days=1)

    return contador
