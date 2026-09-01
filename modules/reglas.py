import re
import unicodedata

import pandas as pd


SUCURSALES_DIFARMER = {
    "CULIACAN",
    "MATRIZ",
    "LEON",
    "MEXICALI",
    "PUEBLA",
    "QUERETARO",
    "TORREON",
}


SUCURSALES_FARMASI = {
    "OFICINA",
    "BUGAMBILIAS",
    "5 DE MAYO",
    "ALTURAS DEL SUR",
    "AMERICAS",
    "ASENTAMIENTOS HUMANOS",
    "BACHIGUALATO",
    "BENITO JUAREZ (GUAMUCHIL)",
    "BENJAMIN HILL 2",
    "CAMINO REAL",
    "CANADAS",
    "CHAPULTEPEC",
    "CHULAVISTA",
    "CIMA",
    "COLINAS",
    "CUBRES",
    "CUMBRES",
    "CUMBRES DEL SUR",
    "ENRIQUE CABRERA",
    "ESTANCIA",
    "ESTHELA ORTIZ",
    "GUADALUPE VICTORIA",
    "HUIZACHES",
    "JUAN LIRA",
    "LA CONQUISTA",
    "LAS QUINTAS",
    "LAS TORRES",
    "LIMA",
    "LOMA DE RODRIGUERA",
    "LOS ANGELES",
    "LOS ANGELES 2",
    "MANUEL ESTRADA",
    "MAQUIO CLOUTHIER",
    "MARGARITA",
    "MONT BLANC",
    "NUEVA DARITZY",
    "OROZCO",
    "PALMITO DOS",
    "PATRIA",
    "PERICOS",
    "PERISUR",
    "PROGRESO",
    "REVOLUCION",
    "SAN JOSE MARIA",
    "SAN MARCOS",
    "SANALONA",
    "SANTA FE",
    "TERRANOVA",
    "TERRONES",
    "VILLA BONITA",
    "VILLA JUAREZ",
    "VILLAS DE GUADIANA",
    "ZAPATA",
    "ZONA 1",
    "ZONA 2",
    "ZONA 3",
    "ZONA 4",
    "ZONA 5",
    "ZONA 6",
}


PUESTOS_EXCLUIDOS = {
    "AGENTE DE VENTAS",
}


def limpiar_codigos_excel(texto):
    """
    Elimina códigos y caracteres invisibles provenientes de Excel.

    Ejemplos:
    MEXICALI_x000D_ -> MEXICALI
    OFICINA_x000A_ -> OFICINA
    """

    texto = str(texto)

    codigos_excel = [
        "_x000D_",
        "_x000d_",
        "_x000A_",
        "_x000a_",
        "_x0009_",
        "_x000B_",
        "_x000b_",
    ]

    for codigo in codigos_excel:
        texto = texto.replace(
            codigo,
            " ",
        )

    texto = texto.replace(
        "\r",
        " ",
    )

    texto = texto.replace(
        "\n",
        " ",
    )

    texto = texto.replace(
        "\t",
        " ",
    )

    return texto


def normalizar_para_comparar(valor):
    """
    Normaliza un texto para realizar comparaciones confiables.

    La función:
    - Elimina códigos ocultos de Excel
    - Elimina saltos de línea y tabulaciones
    - Convierte el texto a mayúsculas
    - Elimina acentos
    - Corrige espacios repetidos
    - Quita espacios al principio y al final
    """

    if pd.isna(valor):
        return ""

    texto = limpiar_codigos_excel(
        valor
    )

    texto = texto.strip().upper()

    texto = unicodedata.normalize(
        "NFKD",
        texto,
    )

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(
            caracter
        )
    )

    texto = re.sub(
        r"_X[0-9A-F]{4}_",
        " ",
        texto,
        flags=re.IGNORECASE,
    )

    texto = "".join(
        caracter
        if caracter.isprintable()
        else " "
        for caracter in texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip()


def contiene_texto(texto, expresion):
    """
    Comprueba si una expresión aparece dentro de un texto.
    """

    texto_normalizado = normalizar_para_comparar(
        texto
    )

    expresion_normalizada = normalizar_para_comparar(
        expresion
    )

    if not expresion_normalizada:
        return False

    return (
        expresion_normalizada
        in texto_normalizado
    )


def contiene_palabra_completa(texto, palabra):
    """
    Comprueba si una palabra independiente aparece en el texto.

    Ejemplos que sí coinciden con PX:
    AUXILIAR PX
    PX ENCARGADO
    ENCARGADO (PX)
    SUPERVISOR-PX

    Ejemplos que no coinciden:
    EXPERTO
    EXPEDICION
    """

    texto_normalizado = normalizar_para_comparar(
        texto
    )

    palabra_normalizada = normalizar_para_comparar(
        palabra
    )

    if not palabra_normalizada:
        return False

    patron = (
        r"(?<![A-Z0-9])"
        + re.escape(
            palabra_normalizada
        )
        + r"(?![A-Z0-9])"
    )

    return bool(
        re.search(
            patron,
            texto_normalizado,
        )
    )


def puesto_esta_excluido(puesto):
    """
    Indica si el puesto está dentro del catálogo
    de puestos que no deben recibir tarjeta.

    La comparación es exacta después de normalizar el texto.
    """

    puesto_normalizado = normalizar_para_comparar(
        puesto
    )

    return (
        puesto_normalizado
        in PUESTOS_EXCLUIDOS
    )


def determinar_plantilla(fila):
    """
    Determina la plantilla correspondiente al colaborador.

    Orden de evaluación:

    1. Puesto excluido
       AGENTE DE VENTAS no genera tarjeta.

    2. DABRA
       Departamento contiene TALLER.

    3. BARANETOS
       Departamento contiene BARANETOS.

    4. PHARMACEUTIX
       Puesto contiene la palabra independiente PX.
       No importa la empresa ni la sucursal.

    5. DIFARMER
       Empresa DIFARMER y sucursal autorizada.

    6. FARMASI
       Empresa OPEFAR y sucursal autorizada.
    """

    empresa = normalizar_para_comparar(
        fila.get(
            "Empresa",
            "",
        )
    )

    sucursal = normalizar_para_comparar(
        fila.get(
            "Sucursal",
            "",
        )
    )

    departamento = normalizar_para_comparar(
        fila.get(
            "Departamento",
            "",
        )
    )

    puesto = normalizar_para_comparar(
        fila.get(
            "Puesto",
            "",
        )
    )

    # Exclusión con máxima prioridad
    if puesto_esta_excluido(
        puesto
    ):
        return "SIN ASIGNAR"

    # Prioridad 1: DABRA
    if contiene_texto(
        departamento,
        "TALLER",
    ):
        return "DABRA"

    # Prioridad 2: BARANETOS
    if contiene_texto(
        departamento,
        "BARANETOS",
    ):
        return "BARANETOS"

    # Prioridad 3: PHARMACEUTIX
    # Basta con que el puesto contenga la palabra PX.
    if contiene_palabra_completa(
        puesto,
        "PX",
    ):
        return "PHARMACEUTIX"

    # Prioridad 4: DIFARMER
    if (
        empresa == "DIFARMER"
        and sucursal in SUCURSALES_DIFARMER
    ):
        return "DIFARMER"

    # Prioridad 5: FARMASI
    if (
        empresa == "OPEFAR"
        and sucursal in SUCURSALES_FARMASI
    ):
        return "FARMASI"

    return "SIN ASIGNAR"


def obtener_motivo_sin_asignar(fila):
    """
    Explica por qué un colaborador no recibió plantilla.
    """

    empresa = normalizar_para_comparar(
        fila.get(
            "Empresa",
            "",
        )
    )

    sucursal = normalizar_para_comparar(
        fila.get(
            "Sucursal",
            "",
        )
    )

    departamento = normalizar_para_comparar(
        fila.get(
            "Departamento",
            "",
        )
    )

    puesto = normalizar_para_comparar(
        fila.get(
            "Puesto",
            "",
        )
    )

    if puesto_esta_excluido(
        puesto
    ):
        return (
            "No se genera tarjeta para el puesto "
            "AGENTE DE VENTAS."
        )

    if not empresa:
        return "La empresa está vacía."

    if empresa not in {
        "DIFARMER",
        "OPEFAR",
    }:
        return (
            f"Empresa no reconocida: "
            f"{empresa}."
        )

    if not sucursal:
        return "La sucursal está vacía."

    if contiene_texto(
        departamento,
        "TALLER",
    ):
        return (
            "El departamento contiene TALLER "
            "y debería recibir la plantilla DABRA."
        )

    if contiene_texto(
        departamento,
        "BARANETOS",
    ):
        return (
            "El departamento contiene BARANETOS "
            "y debería recibir la plantilla BARANETOS."
        )

    if contiene_palabra_completa(
        puesto,
        "PX",
    ):
        return (
            "El puesto contiene la palabra PX "
            "y debería recibir la plantilla PHARMACEUTIX."
        )

    if empresa == "DIFARMER":
        return (
            f"La sucursal {sucursal} no está incluida "
            "en el catálogo de DIFARMER."
        )

    if empresa == "OPEFAR":
        return (
            f"La sucursal {sucursal} no está incluida "
            "en el catálogo de FARMASI."
        )

    return (
        "El registro no cumple ninguna regla "
        "de asignación."
    )
