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
    "ASENTAMIENTOS",
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


def normalizar_para_comparar(valor):
    """
    Normaliza un texto para realizar comparaciones.

    La función:
    - Convierte a mayúsculas
    - Elimina acentos
    - Elimina espacios duplicados
    - Elimina espacios al inicio y al final
    """

    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    texto = unicodedata.normalize(
        "NFKD",
        texto,
    )

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip()


def contiene_palabra(texto, palabra):
    """
    Comprueba si una palabra o expresión aparece dentro del texto.
    """

    texto_normalizado = normalizar_para_comparar(texto)
    palabra_normalizada = normalizar_para_comparar(palabra)

    return palabra_normalizada in texto_normalizado


def comienza_con(texto, prefijo):
    """
    Comprueba si un texto comienza con un prefijo.
    """

    texto_normalizado = normalizar_para_comparar(texto)
    prefijo_normalizado = normalizar_para_comparar(prefijo)

    return texto_normalizado.startswith(prefijo_normalizado)


def determinar_plantilla(fila):
    """
    Determina qué plantilla corresponde a un colaborador.

    Orden de prioridad:
    1. DABRA
    2. BARANETOS
    3. PHARMACEUTIX
    4. DIFARMER
    5. FARMASI
    """

    empresa = normalizar_para_comparar(
        fila.get("Empresa", "")
    )

    sucursal = normalizar_para_comparar(
        fila.get("Sucursal", "")
    )

    departamento = normalizar_para_comparar(
        fila.get("Departamento", "")
    )

    puesto = normalizar_para_comparar(
        fila.get("Puesto", "")
    )

    # Prioridad 1: DABRA
    if contiene_palabra(departamento, "TALLER"):
        return "DABRA"

    # Prioridad 2: BARANETOS
    if contiene_palabra(departamento, "BARANETOS"):
        return "BARANETOS"

    # Prioridad 3: PHARMACEUTIX
    if (
        empresa == "DIFARMER"
        and comienza_con(sucursal, "PX")
        and contiene_palabra(puesto, "PX")
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
    Explica por qué un registro no recibió plantilla.
    """

    empresa = normalizar_para_comparar(
        fila.get("Empresa", "")
    )

    sucursal = normalizar_para_comparar(
        fila.get("Sucursal", "")
    )

    departamento = normalizar_para_comparar(
        fila.get("Departamento", "")
    )

    puesto = normalizar_para_comparar(
        fila.get("Puesto", "")
    )

    if not empresa:
        return "La empresa está vacía."

    if empresa not in {"DIFARMER", "OPEFAR"}:
        return f"Empresa no reconocida: {empresa}"

    if not sucursal:
        return "La sucursal está vacía."

    if empresa == "DIFARMER":
        if comienza_con(sucursal, "PX"):
            if not contiene_palabra(puesto, "PX"):
                return (
                    "La sucursal comienza con PX, pero el puesto "
                    "no contiene PX."
                )

        return (
            f"La sucursal {sucursal} no está incluida en el "
            "catálogo de DIFARMER."
        )

    if empresa == "OPEFAR":
        return (
            f"La sucursal {sucursal} no está incluida en el "
            "catálogo de FARMASI."
        )

    if departamento:
        return (
            "El departamento no coincide con TALLER ni BARANETOS."
        )

    return "El registro no cumple ninguna regla de plantilla."
