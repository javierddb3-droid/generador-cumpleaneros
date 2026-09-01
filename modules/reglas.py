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


def limpiar_codigos_excel(texto):
    """
    Elimina códigos y caracteres invisibles provenientes de Excel.

    Ejemplos:
    MEXICALI_x000D_ -> MEXICALI
    CULIACAN_x000A_ -> CULIACAN
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
    Normaliza texto para realizar comparaciones confiables.

    La función:
    - Elimina códigos ocultos de Excel
    - Elimina saltos de línea y tabulaciones
    - Convierte el texto a mayúsculas
    - Elimina acentos
    - Corrige espacios repetidos
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

    return (
        expresion_normalizada
        in texto_normalizado
    )


def contiene_palabra_completa(texto, palabra):
    """
    Comprueba si una palabra independiente aparece dentro del texto.

    Esta función evita que PX coincida accidentalmente con
    una secuencia de letras dentro de otra palabra.

    Ejemplos válidos:
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

    patron = (
        r"(?<![A-Z0-9])"
        + re.escape(palabra_normalizada)
        + r"(?![A-Z0-9])"
    )

    return bool(
        re.search(
            patron,
            texto_normalizado,
        )
    )


def comienza_con(texto, prefijo):
    """
    Comprueba si un texto comienza con el prefijo indicado.
    """

    texto_normalizado = normalizar_para_comparar(
        texto
    )

    prefijo_normalizado = normalizar_para_comparar(
        prefijo
    )

    return texto_normalizado.startswith(
        prefijo_normalizado
    )


def determinar_plantilla(fila):
    """
    Determina la plantilla correspondiente al colaborador.

    Orden de prioridad:

    1. DABRA
       Si Departamento contiene TALLER.

    2. BARANETOS
       Si Departamento contiene BARANETOS.

    3. PHARMACEUTIX
       Si Puesto contiene la palabra PX.
       No importa la empresa ni la sucursal.

    4. DIFARMER
       Si Empresa es DIFARMER y la sucursal pertenece
       al catálogo de DIFARMER.

    5. FARMASI
       Si Empresa es OPEFAR y la sucursal pertenece
       al catálogo de FARMASI.
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
    # Se asigna cuando el puesto contiene la palabra PX,
    # sin importar empresa o sucursal.
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
            "El departamento corresponde a TALLER "
            "y debería recibir DABRA."
        )

    if contiene_texto(
        departamento,
        "BARANETOS",
    ):
        return (
            "El departamento corresponde a BARANETOS "
            "y debería recibir BARANETOS."
        )

    if contiene_palabra_completa(
        puesto,
        "PX",
    ):
        return (
            "El puesto contiene PX y debería recibir "
            "PHARMACEUTIX."
        )

    if empresa == "DIFARMER":
        return (
            f"La sucursal {sucursal} no está incluida "
            "en el catálogo de DIFARMER y el puesto "
            "no contiene PX."
        )

    if empresa == "OPEFAR":
        return (
            f"La sucursal {sucursal} no está incluida "
            "en el catálogo de FARMASI y el puesto "
            "no contiene PX."
        )

    return (
        "El registro no cumple ninguna regla "
        "de asignación."
    )
    return (
        "El registro no cumple ninguna regla "
        "de asignación."
    )
