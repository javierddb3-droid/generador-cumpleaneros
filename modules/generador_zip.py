from datetime import datetime
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
import re
import unicodedata

import pandas as pd

from modules.generador import (
    crear_nombre_archivo,
    formato_nombre,
    formato_titulo,
    generar_tarjeta,
)


CARPETAS_PLANTILLAS = [
    "DIFARMER",
    "FARMASI",
    "PHARMACEUTIX",
    "DABRA",
    "BARANETOS",
]


MESES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}


def limpiar_valor(valor):
    """
    Convierte un valor a texto limpio.

    Elimina espacios repetidos, saltos de línea y tabulaciones.
    """

    if pd.isna(valor):
        return ""

    texto = str(valor)

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

    return " ".join(
        texto.strip().split()
    )


def quitar_acentos(texto):
    """
    Elimina acentos de un texto para utilizarlo
    de manera segura como nombre de carpeta.
    """

    texto = unicodedata.normalize(
        "NFKD",
        str(texto),
    )

    return "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )


def normalizar_para_comparar(valor):
    """
    Normaliza un valor para realizar comparaciones.

    Ejemplo:
    OFICINA_x000D_ se convierte en OFICINA.
    """

    texto = limpiar_valor(
        valor
    )

    texto = quitar_acentos(
        texto
    )

    texto = texto.upper()

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip()


def limpiar_nombre_carpeta(valor):
    """
    Convierte una sucursal en un nombre seguro para carpeta.

    Ejemplos:
    ALTURAS DEL SUR -> ALTURAS_DEL_SUR
    LEÓN -> LEON
    BENITO JUAREZ (GUAMUCHIL)
    -> BENITO_JUAREZ_GUAMUCHIL
    """

    texto = limpiar_valor(
        valor
    )

    texto = quitar_acentos(
        texto
    )

    texto = texto.upper()

    texto = re.sub(
        r"[^A-Z0-9_-]",
        "_",
        texto,
    )

    texto = re.sub(
        r"_+",
        "_",
        texto,
    )

    texto = texto.strip(
        "_"
    )

    if not texto:
        return "SIN_SUCURSAL"

    return texto


def determinar_ruta_carpeta(
    plantilla,
    sucursal,
):
    """
    Determina la ruta de carpetas para una tarjeta.

    Para DIFARMER, PHARMACEUTIX, DABRA y BARANETOS:
    PLANTILLA/SUCURSAL/

    Para FARMASI:
    FARMASI/FARMACIAS/SUCURSAL/
    o
    FARMASI/OFICINA/SUCURSAL/
    """

    plantilla_limpia = normalizar_para_comparar(
        plantilla
    )

    sucursal_comparacion = normalizar_para_comparar(
        sucursal
    )

    sucursal_carpeta = limpiar_nombre_carpeta(
        sucursal
    )

    if plantilla_limpia == "FARMASI":
        if sucursal_comparacion == "OFICINA":
            return (
                "FARMASI/"
                "OFICINA/"
                f"{sucursal_carpeta}"
            )

        return (
            "FARMASI/"
            "FARMACIAS/"
            f"{sucursal_carpeta}"
        )

    return (
        f"{plantilla_limpia}/"
        f"{sucursal_carpeta}"
    )


def validar_registro(fila):
    """
    Comprueba que el registro tenga los datos necesarios
    para generar la tarjeta.
    """

    nombre = limpiar_valor(
        fila.get(
            "Nombre",
            "",
        )
    )

    puesto = limpiar_valor(
        fila.get(
            "Puesto",
            "",
        )
    )

    sucursal = limpiar_valor(
        fila.get(
            "Sucursal",
            "",
        )
    )

    fecha_nacimiento = fila.get(
        "FechaNacimiento",
        pd.NaT,
    )

    plantilla = normalizar_para_comparar(
        fila.get(
            "Plantilla asignada",
            "",
        )
    )

    if not nombre:
        return (
            False,
            "El nombre está vacío.",
        )

    if not puesto:
        return (
            False,
            "El puesto está vacío.",
        )

    if not sucursal:
        return (
            False,
            "La sucursal está vacía.",
        )

    if pd.isna(
        fecha_nacimiento
    ):
        return (
            False,
            "La fecha de nacimiento está vacía "
            "o no es válida.",
        )

    if not plantilla:
        return (
            False,
            "La plantilla está vacía.",
        )

    if plantilla == "SIN ASIGNAR":
        return (
            False,
            "El colaborador no tiene una plantilla asignada.",
        )

    if plantilla not in CARPETAS_PLANTILLAS:
        return (
            False,
            f"La plantilla {plantilla} no está reconocida.",
        )

    return (
        True,
        "",
    )


def nombre_sin_extension(
    nombre_archivo,
):
    """
    Elimina la extensión PNG.
    """

    if nombre_archivo.lower().endswith(
        ".png"
    ):
        return nombre_archivo[:-4]

    return nombre_archivo


def crear_nombre_unico(
    nombre_archivo,
    ruta_carpeta,
    nombres_utilizados,
):
    """
    Evita que dos archivos con el mismo nombre
    se sobrescriban dentro de la misma carpeta.

    Ejemplo:
    Javier_16_oct.png
    Javier_16_oct_2.png
    Javier_16_oct_3.png
    """

    clave_original = (
        ruta_carpeta.lower(),
        nombre_archivo.lower(),
    )

    if clave_original not in nombres_utilizados:
        nombres_utilizados.add(
            clave_original
        )

        return nombre_archivo

    nombre_base = nombre_sin_extension(
        nombre_archivo
    )

    consecutivo = 2

    while True:
        nuevo_nombre = (
            f"{nombre_base}_"
            f"{consecutivo}.png"
        )

        nueva_clave = (
            ruta_carpeta.lower(),
            nuevo_nombre.lower(),
        )

        if nueva_clave not in nombres_utilizados:
            nombres_utilizados.add(
                nueva_clave
            )

            return nuevo_nombre

        consecutivo += 1


def crear_nombre_zip(
    numero_mes,
    anio_actual,
):
    """
    Crea el nombre del ZIP descargable.

    Ejemplo:
    Cumpleaneros_octubre_2026.zip
    """

    nombre_mes = MESES.get(
        int(numero_mes),
        "mes",
    )

    return (
        f"Cumpleaneros_"
        f"{nombre_mes}_"
        f"{anio_actual}.zip"
    )


def crear_registro_generado(
    fila,
    plantilla,
    ruta_carpeta,
    nombre_archivo,
):
    """
    Crea un registro de control para una tarjeta generada.
    """

    fecha_nacimiento = fila.get(
        "FechaNacimiento",
        pd.NaT,
    )

    return {
        "Estado": "Generada",
        "Empresa": limpiar_valor(
            fila.get(
                "Empresa",
                "",
            )
        ),
        "Sucursal": limpiar_valor(
            fila.get(
                "Sucursal",
                "",
            )
        ),
        "Nombre": formato_nombre(
            fila.get(
                "Nombre",
                "",
            )
        ),
        "Puesto": formato_titulo(
            fila.get(
                "Puesto",
                "",
            )
        ),
        "FechaNacimiento": (
            fecha_nacimiento.strftime(
                "%d/%m/%Y"
            )
            if not pd.isna(
                fecha_nacimiento
            )
            else ""
        ),
        "Plantilla": plantilla,
        "Carpeta": ruta_carpeta,
        "Archivo": nombre_archivo,
        "Ruta completa": (
            f"{ruta_carpeta}/"
            f"{nombre_archivo}"
        ),
        "Motivo": "",
    }


def crear_registro_error(
    fila,
    motivo,
):
    """
    Crea un registro de control para una tarjeta omitida.
    """

    fecha_nacimiento = fila.get(
        "FechaNacimiento",
        pd.NaT,
    )

    plantilla = normalizar_para_comparar(
        fila.get(
            "Plantilla asignada",
            "",
        )
    )

    sucursal = limpiar_valor(
        fila.get(
            "Sucursal",
            "",
        )
    )

    ruta_carpeta = ""

    if plantilla in CARPETAS_PLANTILLAS:
        ruta_carpeta = determinar_ruta_carpeta(
            plantilla=plantilla,
            sucursal=sucursal,
        )

    return {
        "Estado": "Omitida",
        "Empresa": limpiar_valor(
            fila.get(
                "Empresa",
                "",
            )
        ),
        "Sucursal": sucursal,
        "Nombre": formato_nombre(
            fila.get(
                "Nombre",
                "",
            )
        ),
        "Puesto": formato_titulo(
            fila.get(
                "Puesto",
                "",
            )
        ),
        "FechaNacimiento": (
            fecha_nacimiento.strftime(
                "%d/%m/%Y"
            )
            if (
                not pd.isna(
                    fecha_nacimiento
                )
                and hasattr(
                    fecha_nacimiento,
                    "strftime",
                )
            )
            else ""
        ),
        "Plantilla": plantilla,
        "Carpeta": ruta_carpeta,
        "Archivo": "",
        "Ruta completa": "",
        "Motivo": motivo,
    }


def crear_reporte_csv(
    registros,
):
    """
    Crea el reporte CSV que se incluirá dentro del ZIP.
    """

    columnas = [
        "Estado",
        "Empresa",
        "Sucursal",
        "Nombre",
        "Puesto",
        "FechaNacimiento",
        "Plantilla",
        "Carpeta",
        "Archivo",
        "Ruta completa",
        "Motivo",
    ]

    if registros:
        dataframe = pd.DataFrame(
            registros
        )

    else:
        dataframe = pd.DataFrame(
            columns=columnas
        )

    for columna in columnas:
        if columna not in dataframe.columns:
            dataframe[columna] = ""

    dataframe = dataframe[
        columnas
    ]

    return dataframe.to_csv(
        index=False,
        encoding="utf-8-sig",
    )


def agregar_carpeta_zip(
    archivo_zip,
    ruta_carpeta,
    carpetas_creadas,
):
    """
    Agrega una carpeta al ZIP solo si todavía no existe.
    """

    ruta = ruta_carpeta.strip(
        "/"
    )

    partes = ruta.split(
        "/"
    )

    ruta_acumulada = ""

    for parte in partes:
        ruta_acumulada = (
            f"{ruta_acumulada}"
            f"{parte}/"
        )

        if ruta_acumulada not in carpetas_creadas:
            archivo_zip.writestr(
                ruta_acumulada,
                "",
            )

            carpetas_creadas.add(
                ruta_acumulada
            )


def generar_zip_tarjetas(
    dataframe,
    anio_actual=None,
    callback_progreso=None,
):
    """
    Genera todas las tarjetas y las organiza por:

    1. Plantilla
    2. Tipo de unidad, solamente en FARMASI
    3. Sucursal

    Ejemplos:

    DIFARMER/CULIACAN/Javier_16_oct.png

    PHARMACEUTIX/PX_CULIACAN/
    Javier_16_oct.png

    FARMASI/FARMACIAS/BUGAMBILIAS/
    Javier_16_oct.png

    FARMASI/OFICINA/OFICINA/
    Javier_16_oct.png
    """

    if anio_actual is None:
        anio_actual = datetime.now().year

    if dataframe is None:
        raise ValueError(
            "No se recibió una base de datos."
        )

    if dataframe.empty:
        raise ValueError(
            "No hay colaboradores para generar."
        )

    columnas_necesarias = [
        "Sucursal",
        "Nombre",
        "Puesto",
        "FechaNacimiento",
        "Plantilla asignada",
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_necesarias
        if columna not in dataframe.columns
    ]

    if columnas_faltantes:
        columnas_texto = ", ".join(
            columnas_faltantes
        )

        raise ValueError(
            "Faltan columnas necesarias para generar "
            f"las tarjetas: {columnas_texto}"
        )

    salida_zip = BytesIO()

    nombres_utilizados = set()
    carpetas_creadas = set()

    registros_generados = []
    registros_omitidos = []
    todos_los_registros = []

    resumen_plantillas = {
        plantilla: 0
        for plantilla in CARPETAS_PLANTILLAS
    }

    resumen_sucursales = {}

    total_registros = len(
        dataframe
    )

    with ZipFile(
        salida_zip,
        mode="w",
        compression=ZIP_DEFLATED,
    ) as archivo_zip:

        # Crear las cinco carpetas principales.
        for plantilla in CARPETAS_PLANTILLAS:
            agregar_carpeta_zip(
                archivo_zip=archivo_zip,
                ruta_carpeta=plantilla,
                carpetas_creadas=carpetas_creadas,
            )

        # Crear las dos divisiones principales de FARMASI.
        agregar_carpeta_zip(
            archivo_zip=archivo_zip,
            ruta_carpeta="FARMASI/FARMACIAS",
            carpetas_creadas=carpetas_creadas,
        )

        agregar_carpeta_zip(
            archivo_zip=archivo_zip,
            ruta_carpeta="FARMASI/OFICINA",
            carpetas_creadas=carpetas_creadas,
        )

        for posicion, (_, fila) in enumerate(
            dataframe.iterrows(),
            start=1,
        ):
            try:
                registro_valido, motivo = validar_registro(
                    fila
                )

                if not registro_valido:
                    registro_error = crear_registro_error(
                        fila=fila,
                        motivo=motivo,
                    )

                    registros_omitidos.append(
                        registro_error
                    )

                    todos_los_registros.append(
                        registro_error
                    )

                else:
                    plantilla = normalizar_para_comparar(
                        fila[
                            "Plantilla asignada"
                        ]
                    )

                    sucursal = limpiar_valor(
                        fila[
                            "Sucursal"
                        ]
                    )

                    ruta_carpeta = determinar_ruta_carpeta(
                        plantilla=plantilla,
                        sucursal=sucursal,
                    )

                    agregar_carpeta_zip(
                        archivo_zip=archivo_zip,
                        ruta_carpeta=ruta_carpeta,
                        carpetas_creadas=carpetas_creadas,
                    )

                    tarjeta = generar_tarjeta(
                        nombre=fila[
                            "Nombre"
                        ],
                        puesto=fila[
                            "Puesto"
                        ],
                        fecha_nacimiento=fila[
                            "FechaNacimiento"
                        ],
                        nombre_plantilla=plantilla,
                        anio_actual=anio_actual,
                    )

                    nombre_archivo_base = crear_nombre_archivo(
                        nombre_completo=fila[
                            "Nombre"
                        ],
                        fecha_nacimiento=fila[
                            "FechaNacimiento"
                        ],
                    )

                    nombre_archivo = crear_nombre_unico(
                        nombre_archivo=nombre_archivo_base,
                        ruta_carpeta=ruta_carpeta,
                        nombres_utilizados=nombres_utilizados,
                    )

                    ruta_dentro_zip = (
                        f"{ruta_carpeta}/"
                        f"{nombre_archivo}"
                    )

                    archivo_zip.writestr(
                        ruta_dentro_zip,
                        tarjeta.getvalue(),
                    )

                    registro_generado = crear_registro_generado(
                        fila=fila,
                        plantilla=plantilla,
                        ruta_carpeta=ruta_carpeta,
                        nombre_archivo=nombre_archivo,
                    )

                    registros_generados.append(
                        registro_generado
                    )

                    todos_los_registros.append(
                        registro_generado
                    )

                    resumen_plantillas[
                        plantilla
                    ] += 1

                    if ruta_carpeta not in resumen_sucursales:
                        resumen_sucursales[
                            ruta_carpeta
                        ] = 0

                    resumen_sucursales[
                        ruta_carpeta
                    ] += 1

            except Exception as error:
                motivo_error = (
                    f"{type(error).__name__}: "
                    f"{str(error)}"
                )

                registro_error = crear_registro_error(
                    fila=fila,
                    motivo=motivo_error,
                )

                registros_omitidos.append(
                    registro_error
                )

                todos_los_registros.append(
                    registro_error
                )

            if callback_progreso is not None:
                porcentaje = (
                    posicion
                    / total_registros
                )

                callback_progreso(
                    porcentaje,
                    posicion,
                    total_registros,
                )

        reporte_csv = crear_reporte_csv(
            todos_los_registros
        )

        archivo_zip.writestr(
            "reporte_generacion.csv",
            reporte_csv.encode(
                "utf-8-sig"
            ),
        )

    salida_zip.seek(
        0
    )

    return {
        "zip_bytes": salida_zip.getvalue(),
        "total_registros": total_registros,
        "total_generadas": len(
            registros_generados
        ),
        "total_omitidas": len(
            registros_omitidos
        ),
        "registros_generados": registros_generados,
        "registros_omitidos": registros_omitidos,
        "resumen_plantillas": resumen_plantillas,
        "resumen_sucursales": resumen_sucursales,
    }
