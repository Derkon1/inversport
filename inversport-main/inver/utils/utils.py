def formato_cop(valor):
    try:
        valor_redondeado = round(valor, 2)
        entero = int(valor_redondeado)
        decimal = int(round((valor_redondeado - entero) * 100))
        entero_str = f"{entero:,}".replace(",", ".")
        return f"${entero_str},{decimal:02d}"
    except:
        return "$0,00"


def parsear_cop(texto):
    try:
        limpio = texto.replace("$", "").replace(".", "").replace(",", ".")
        return float(limpio)
    except:
        return 0.0