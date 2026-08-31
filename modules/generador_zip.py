from datetime import datetime
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd

from modules.generador import (
    crear_nombre_archivo,
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


def limpiar_valor(valor):
    """
    Convierte un valor a texto limpio.

    Si el valor está vacío o es NaN, devuelve una cadena vacía.
    """

    if pd.isna(valor):
        return ""

    return " ".join(
        str(valor).strip().split()
    )


def validar_registro(fila):
    """
    Comprueba que un registro tenga los datos necesarios
    para generar una tarjeta.

    Devuelve:
    - True y una cadena vacía si el registro es válido.
    - False y el motivo si el registro no es válido.
    """

    nombre = limpiar_valor(
        fila.get("Nombre", "")
    )

    puesto = limpiar_valor(
        fila.get("Puesto", "")
    )

    fecha_nacimiento = fila.get(
        "FechaNacimiento",
        pd.NaT,
    )

    plantilla = limpiar_valor(
        fila.get("Plantilla asignada", "")
    ).upper()

    if not nombre:
        return False, "El nombre está vacío."

    if not puesto:
        return False, "El puesto está vacío."

    if pd.isna(fecha_nacimiento):
        return False, (
            "La fecha de nacimiento está vacía "
            "o no es válida."
        )

    if not plantilla:
        return False, "La plantilla está vacía."

    if plantilla == "SIN ASIGNAR":
        return False, (
            "El colaborador no tiene una "
            "plantilla asignada."
        )

    if plantilla not in CARPETAS_PLANTILLAS:
        return False, (
            f"La plantilla {plantilla} "
            "no está reconocida."
        )

    return True, ""


def nombre_sin_extension(nombre_archivo):
    """
    Elimina la extensión .png de un nombre de archivo.
    """

    if nombre_archivo.lower().endswith(".png"):
        return nombre_archivo[:-4]

    return nombre_archivo


def crear_nombre_unico(
    nombre_archivo,
    carpeta,
    nombres_utilizados,
):
    """
    Evita que dos archivos con el mismo nombre se sobrescriban.

    Ejemplo:
    Javier_16_oct.png
    Javier_16_oct_2.png
    Javier_16_oct_3.png
    """

    clave_original = (
        carpeta,
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
            f"{nombre_base}_{consecutivo}.png"
        )

        nueva_clave = (
            carpeta,
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

    meses = {
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

    nombre_mes = meses.get(
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
    nombre_archivo,
):
    """
    Crea el registro de control para una tarjeta generada.
    """

    fecha_nacimiento = fila.get(
        "FechaNacimiento"
    )

    return {
        "Estado": "Generada",
        "Empresa": limpiar_valor(
            fila.get("Empresa", "")
        ),
        "Sucursal": limpiar_valor(
            fila.get("Sucursal", "")
        ),
        "Nombre": formato_titulo(
            fila.get("Nombre", "")
        ),
        "Puesto": formato_titulo(
            fila.get("Puesto", "")
        ),
        "FechaNacimiento": (
            fecha_nacimiento.strftime(
                "%d/%m/%Y"
            )
            if not pd.isna(fecha_nacimiento)
            else ""
        ),
        "Plantilla": plantilla,
        "Archivo": nombre_archivo,
        "Motivo": "",
    }


def crear_registro_error(
    fila,
    motivo,
):
    """
    Crea el registro de control para una tarjeta omitida.
    """

    fecha_nacimiento = fila.get(
        "FechaNacimiento",
        pd.NaT,
    )

    plantilla = limpiar_valor(
        fila.get(
            "Plantilla asignada",
            "",
        )
    )

    return {
        "Estado": "Omitida",
        "Empresa": limpiar_valor(
            fila.get("Empresa", "")
        ),
        "Sucursal": limpiar_valor(
            fila.get("Sucursal", "")
        ),
        "Nombre": formato_titulo(
            fila.get("Nombre", "")
        ),
        "Puesto": formato_titulo(
            fila.get("Puesto", "")
        ),
        "FechaNacimiento": (
            fecha_nacimiento.strftime(
                "%d/%m/%Y"
            )
            if not pd.isna(fecha_nacimiento)
            and hasattr(
                fecha_nacimiento,
                "strftime",
            )
            else ""
        ),
        "Plantilla": plantilla,
        "Archivo": "",
        "Motivo": motivo,
    }


def crear_reporte_csv(registros):
    """
    Crea un archivo CSV con el resultado del proceso.

    El archivo utiliza UTF-8 con BOM para que Excel
    reconozca correctamente acentos y caracteres especiales.
    """

    columnas = [
        "Estado",
        "Empresa",
        "Sucursal",
        "Nombre",
        "Puesto",
        "FechaNacimiento",
        "Plantilla",
        "Archivo",
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

    dataframe = dataframe[columnas]

    return dataframe.to_csv(
        index=False,
        encoding="utf-8-sig",
    )


def generar_zip_tarjetas(
    dataframe,
    anio_actual=None,
    callback_progreso=None,
):
    """
    Genera todas las tarjetas y las guarda en un ZIP.

    El ZIP contiene exactamente cinco carpetas:
    - DIFARMER
    - FARMASI
    - PHARMACEUTIX
    - DABRA
    - BARANETOS

    Cada carpeta contiene los PNG correspondientes.

    También agrega:
    - reporte_generacion.csv

    Parámetros:
    - dataframe:
      Base filtrada con los colaboradores.
    - anio_actual:
      Año que aparecerá dentro de las tarjetas.
    - callback_progreso:
      Función opcional para actualizar una barra de progreso.

    Devuelve un diccionario con:
    - zip_bytes
    - total_registros
    - total_generadas
    - total_omitidas
    - registros_generados
    - registros_omitidos
    - resumen_plantillas
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
            "Faltan columnas necesarias para "
            f"generar las tarjetas: {columnas_texto}"
        )

    salida_zip = BytesIO()

    nombres_utilizados = set()

    registros_generados = []
    registros_omitidos = []
    todos_los_registros = []

    resumen_plantillas = {
        plantilla: 0
        for plantilla in CARPETAS_PLANTILLAS
    }

    total_registros = len(
        dataframe
    )

    with ZipFile(
        salida_zip,
        mode="w",
        compression=ZIP_DEFLATED,
    ) as archivo_zip:

        # Crear las cinco carpetas aunque alguna quede vacía.
        for carpeta in CARPETAS_PLANTILLAS:
            archivo_zip.writestr(
                f"{carpeta}/",
                "",
            )

        for posicion, (_, fila) in enumerate(
            dataframe.iterrows(),
            start=1,
        ):
            try:
                registro_valido, motivo = (
                    validar_registro(fila)
                )

                if not registro_valido:
                    registro_error = (
                        crear_registro_error(
                            fila=fila,
                            motivo=motivo,
                        )
                    )

                    registros_omitidos.append(
                        registro_error
                    )

                    todos_los_registros.append(
                        registro_error
                    )

                else:
                    plantilla = limpiar_valor(
                        fila[
                            "Plantilla asignada"
                        ]
                    ).upper()

                    tarjeta = generar_tarjeta(
                        nombre=fila["Nombre"],
                        puesto=fila["Puesto"],
                        fecha_nacimiento=fila[
                            "FechaNacimiento"
                        ],
                        nombre_plantilla=plantilla,
                        anio_actual=anio_actual,
                    )

                    nombre_archivo_base = (
                        crear_nombre_archivo(
                            nombre_completo=fila[
                                "Nombre"
                            ],
                            fecha_nacimiento=fila[
                                "FechaNacimiento"
                            ],
                        )
                    )

                    nombre_archivo = crear_nombre_unico(
                        nombre_archivo=(
                            nombre_archivo_base
                        ),
                        carpeta=plantilla,
                        nombres_utilizados=(
                            nombres_utilizados
                        ),
                    )

                    ruta_dentro_zip = (
                        f"{plantilla}/"
                        f"{nombre_archivo}"
                    )

                    archivo_zip.writestr(
                        ruta_dentro_zip,
                        tarjeta.getvalue(),
                    )

                    registro_generado = (
                        crear_registro_generado(
                            fila=fila,
                            plantilla=plantilla,
                            nombre_archivo=(
                                nombre_archivo
                            ),
                        )
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

            except Exception as error:
                motivo_error = (
                    f"{type(error).__name__}: "
                    f"{str(error)}"
                )

                registro_error = (
                    crear_registro_error(
                        fila=fila,
                        motivo=motivo_error,
                    )
                )

                registros_omitidos.append(
                    registro_error
                )

                todos_los_registros.append(
                    registro_error
                )

            if callback_progreso is not None:
                porcentaje = (
                    posicion / total_registros
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

    salida_zip.seek(0)

    return {
        "zip_bytes": salida_zip.getvalue(),
        "total_registros": total_registros,
        "total_generadas": len(
            registros_generados
        ),
        "total_omitidas": len(
            registros_omitidos
        ),
        "registros_generados": (
            registros_generados
        ),
        "registros_omitidos": (
            registros_omitidos
        ),
        "resumen_plantillas": (
            resumen_plantillas
        ),
    }
