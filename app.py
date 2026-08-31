from datetime import date, datetime
import calendar

import pandas as pd
import streamlit as st

from modules.generador import (
    crear_nombre_archivo,
    formato_titulo,
    generar_tarjeta,
)
from modules.generador_zip import (
    crear_nombre_zip,
    generar_zip_tarjetas,
)
from modules.reglas import (
    determinar_plantilla,
    obtener_motivo_sin_asignar,
)


st.set_page_config(
    page_title="Generador de Cumpleañeros",
    page_icon="🎂",
    layout="wide",
)


COLUMNAS_REQUERIDAS = [
    "Empresa",
    "Sucursal",
    "Nombre",
    "Departamento",
    "Puesto",
    "FechaNacimiento",
]


MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


MESES_MINUSCULAS = {
    numero: nombre.lower()
    for numero, nombre in MESES.items()
}


def limpiar_nombre_columna(nombre_columna):
    """
    Elimina espacios al inicio y al final
    de los encabezados.
    """

    return str(nombre_columna).strip()


def convertir_fecha_excel(valor):
    """
    Convierte distintos formatos de fecha.

    Reconoce:
    - Fechas propias de Excel
    - Números de serie de Excel
    - Fechas escritas como texto
    - Fechas de Python y pandas
    """

    if pd.isna(valor):
        return pd.NaT

    if isinstance(valor, pd.Timestamp):
        return valor

    if isinstance(valor, (datetime, date)):
        return pd.Timestamp(valor)

    if isinstance(valor, (int, float)):
        try:
            return pd.to_datetime(
                valor,
                unit="D",
                origin="1899-12-30",
                errors="coerce",
            )

        except (
            ValueError,
            TypeError,
            OverflowError,
        ):
            return pd.NaT

    texto = str(valor).strip()

    if not texto:
        return pd.NaT

    try:
        numero = float(texto)

        if 1 <= numero <= 100000:
            return pd.to_datetime(
                numero,
                unit="D",
                origin="1899-12-30",
                errors="coerce",
            )

    except (
        ValueError,
        TypeError,
    ):
        pass

    return pd.to_datetime(
        texto,
        errors="coerce",
        dayfirst=True,
    )


def leer_archivo_excel(archivo):
    """
    Lee la primera hoja del Excel y convierte
    la columna FechaNacimiento.
    """

    dataframe = pd.read_excel(
        archivo,
        engine="openpyxl",
        sheet_name=0,
    )

    dataframe.columns = [
        limpiar_nombre_columna(columna)
        for columna in dataframe.columns
    ]

    if "FechaNacimiento" in dataframe.columns:
        dataframe["FechaNacimientoOriginal"] = dataframe[
            "FechaNacimiento"
        ]

        dataframe["FechaNacimiento"] = dataframe[
            "FechaNacimiento"
        ].apply(convertir_fecha_excel)

    return dataframe


def obtener_columnas_faltantes(dataframe):
    """
    Devuelve las columnas obligatorias que
    no se encontraron.
    """

    return [
        columna
        for columna in COLUMNAS_REQUERIDAS
        if columna not in dataframe.columns
    ]


def normalizar_texto(valor):
    """
    Normaliza un texto para realizar comparaciones.
    """

    if pd.isna(valor):
        return ""

    return " ".join(
        str(valor).strip().upper().split()
    )


def formato_fecha_tarjeta(fecha_nacimiento):
    """
    Crea la fecha visible dentro de la tarjeta.
    """

    if pd.isna(fecha_nacimiento):
        return ""

    dia = int(fecha_nacimiento.day)

    mes = MESES_MINUSCULAS[
        int(fecha_nacimiento.month)
    ]

    anio_actual = datetime.now().year

    return (
        f"{dia:02d} de {mes} del {anio_actual}"
    )


def filtrar_cumpleaneros(
    dataframe,
    empresa_seleccionada,
    numero_mes,
    modalidad,
    dia_seleccionado=None,
):
    """
    Filtra la base por empresa, mes y día.
    """

    resultado = dataframe.copy()

    resultado = resultado[
        resultado["FechaNacimiento"].notna()
    ].copy()

    if empresa_seleccionada != "Todas":
        resultado = resultado[
            resultado["Empresa"].apply(
                normalizar_texto
            ) == empresa_seleccionada
        ].copy()

    resultado = resultado[
        resultado["FechaNacimiento"].dt.month
        == numero_mes
    ].copy()

    if modalidad == "Día específico":
        resultado = resultado[
            resultado["FechaNacimiento"].dt.day
            == dia_seleccionado
        ].copy()

    resultado = resultado.sort_values(
        by=[
            "FechaNacimiento",
            "Nombre",
        ],
        ascending=[
            True,
            True,
        ],
    )

    return resultado


def asignar_plantillas(dataframe):
    """
    Asigna una plantilla y el resultado
    de la validación a cada registro.
    """

    resultado = dataframe.copy()

    resultado["Plantilla asignada"] = resultado.apply(
        determinar_plantilla,
        axis=1,
    )

    resultado["Resultado de validación"] = resultado.apply(
        lambda fila: (
            obtener_motivo_sin_asignar(fila)
            if fila["Plantilla asignada"] == "SIN ASIGNAR"
            else "Plantilla asignada correctamente."
        ),
        axis=1,
    )

    return resultado


def crear_vista_resultados(dataframe):
    """
    Prepara la tabla visible de colaboradores.
    """

    columnas = [
        "Empresa",
        "Sucursal",
        "Nombre",
        "Departamento",
        "Puesto",
        "FechaNacimiento",
        "Plantilla asignada",
        "Resultado de validación",
    ]

    vista = dataframe[columnas].copy()

    vista["Nombre"] = vista[
        "Nombre"
    ].apply(formato_titulo)

    vista["Puesto"] = vista[
        "Puesto"
    ].apply(formato_titulo)

    vista["Fecha para tarjeta"] = dataframe[
        "FechaNacimiento"
    ].apply(formato_fecha_tarjeta)

    vista["FechaNacimiento"] = dataframe[
        "FechaNacimiento"
    ].dt.strftime("%d/%m/%Y")

    vista = vista.rename(
        columns={
            "FechaNacimiento": "Fecha original",
        }
    )

    return vista


def crear_etiqueta_colaborador(indice, fila):
    """
    Crea la etiqueta del selector de vista previa.
    """

    nombre = formato_titulo(
        fila.get("Nombre", "")
    )

    sucursal = str(
        fila.get("Sucursal", "")
    ).strip()

    plantilla = fila.get(
        "Plantilla asignada",
        "",
    )

    fecha = fila[
        "FechaNacimiento"
    ].strftime("%d/%m")

    return (
        f"{indice} | {nombre} | "
        f"{fecha} | {sucursal} | {plantilla}"
    )


def limpiar_resultados_anteriores():
    """
    Elimina resultados generados anteriormente
    cuando cambia el archivo o los filtros.
    """

    claves = [
        "resultado_zip",
        "nombre_zip",
        "firma_zip",
    ]

    for clave in claves:
        if clave in st.session_state:
            del st.session_state[clave]


st.title(
    "🎂 Generador de plantillas de cumpleaños"
)

st.write(
    """
    Carga la base de colaboradores, selecciona el periodo,
    revisa las asignaciones y genera las tarjetas en un ZIP.
    """
)

st.warning(
    "La base de datos se utiliza temporalmente durante "
    "la sesión. No se guarda dentro del repositorio."
)


archivo_excel = st.file_uploader(
    "Selecciona la base de datos en Excel",
    type=["xlsx"],
    help=(
        "El archivo debe contener las columnas "
        "Empresa, Sucursal, Nombre, Departamento, "
        "Puesto y FechaNacimiento."
    ),
)


if archivo_excel is None:
    st.info(
        "Carga un archivo Excel para comenzar."
    )

    st.stop()


try:
    df = leer_archivo_excel(
        archivo_excel
    )

except Exception as error:
    st.error(
        "No fue posible leer el archivo Excel."
    )

    st.exception(error)

    st.info(
        "Verifica que el archivo tenga extensión .xlsx, "
        "que no esté protegido con contraseña y que sea "
        "un archivo válido de Excel."
    )

    st.stop()


columnas_faltantes = obtener_columnas_faltantes(
    df
)


if columnas_faltantes:
    st.error(
        "El archivo no contiene todas las "
        "columnas necesarias."
    )

    st.write(
        "### Columnas faltantes"
    )

    for columna in columnas_faltantes:
        st.write(
            f"- {columna}"
        )

    st.write(
        "### Columnas encontradas"
    )

    st.write(
        list(df.columns)
    )

    st.stop()


st.success(
    "El archivo Excel se cargó correctamente."
)


total_registros = len(df)

fechas_validas = int(
    df["FechaNacimiento"]
    .notna()
    .sum()
)

fechas_invalidas = int(
    df["FechaNacimiento"]
    .isna()
    .sum()
)


columna_1, columna_2, columna_3 = st.columns(3)


columna_1.metric(
    "Total de registros",
    total_registros,
)

columna_2.metric(
    "Fechas válidas",
    fechas_validas,
)

columna_3.metric(
    "Fechas inválidas o vacías",
    fechas_invalidas,
)


if fechas_invalidas > 0:
    with st.expander(
        "Ver registros con fecha inválida"
    ):
        registros_invalidos = df[
            df["FechaNacimiento"].isna()
        ].copy()

        columnas_errores = [
            "Empresa",
            "Sucursal",
            "Nombre",
            "FechaNacimientoOriginal",
        ]

        st.dataframe(
            registros_invalidos[
                columnas_errores
            ],
            use_container_width=True,
            hide_index=True,
        )


st.divider()

st.subheader(
    "1. Selecciona los filtros"
)


empresas_disponibles = (
    df["Empresa"]
    .dropna()
    .apply(normalizar_texto)
    .loc[
        lambda serie:
        serie != ""
    ]
    .sort_values()
    .unique()
    .tolist()
)


opciones_empresa = (
    ["Todas"]
    + empresas_disponibles
)


columna_empresa, columna_modalidad = st.columns(2)


with columna_empresa:
    empresa_seleccionada = st.selectbox(
        "Empresa matriz",
        options=opciones_empresa,
        index=0,
    )


with columna_modalidad:
    modalidad = st.radio(
        "Periodo de cumpleaños",
        options=[
            "Mes completo",
            "Día específico",
        ],
        horizontal=True,
    )


columna_mes, columna_dia = st.columns(2)

mes_actual = datetime.now().month


with columna_mes:
    nombre_mes = st.selectbox(
        "Mes",
        options=list(
            MESES.values()
        ),
        index=mes_actual - 1,
    )


numero_mes = next(
    numero
    for numero, nombre in MESES.items()
    if nombre == nombre_mes
)


dia_seleccionado = None


with columna_dia:
    if modalidad == "Día específico":
        anio_actual = datetime.now().year

        ultimo_dia_mes = calendar.monthrange(
            anio_actual,
            numero_mes,
        )[1]

        dia_seleccionado = st.selectbox(
            "Día",
            options=list(
                range(
                    1,
                    ultimo_dia_mes + 1,
                )
            ),
        )

    else:
        st.info(
            "Se incluirán todos los cumpleaños "
            f"de {nombre_mes.lower()}."
        )


cumpleaneros = filtrar_cumpleaneros(
    dataframe=df,
    empresa_seleccionada=(
        empresa_seleccionada
    ),
    numero_mes=numero_mes,
    modalidad=modalidad,
    dia_seleccionado=(
        dia_seleccionado
    ),
)


cumpleaneros = asignar_plantillas(
    cumpleaneros
)


st.divider()

st.subheader(
    "2. Revisa los colaboradores encontrados"
)


if modalidad == "Mes completo":
    descripcion_filtro = (
        f"Mes completo: {nombre_mes}"
    )

else:
    descripcion_filtro = (
        f"{dia_seleccionado:02d} de "
        f"{nombre_mes.lower()}"
    )


st.write(
    f"**Empresa:** {empresa_seleccionada}  \n"
    f"**Periodo:** {descripcion_filtro}"
)


if cumpleaneros.empty:
    st.warning(
        "No se encontraron colaboradores que coincidan "
        "con los filtros seleccionados."
    )

    st.stop()


st.success(
    f"Se encontraron {len(cumpleaneros)} colaboradores."
)


vista_resultados = crear_vista_resultados(
    cumpleaneros
)


st.dataframe(
    vista_resultados,
    use_container_width=True,
    hide_index=True,
)


st.write(
    "### Resumen por plantilla"
)


resumen_plantillas = (
    cumpleaneros[
        "Plantilla asignada"
    ]
    .value_counts()
    .rename_axis("Plantilla")
    .reset_index(
        name="Cantidad"
    )
)


st.dataframe(
    resumen_plantillas,
    use_container_width=True,
    hide_index=True,
)


registros_asignados = cumpleaneros[
    cumpleaneros[
        "Plantilla asignada"
    ] != "SIN ASIGNAR"
].copy()


registros_sin_asignar = cumpleaneros[
    cumpleaneros[
        "Plantilla asignada"
    ] == "SIN ASIGNAR"
].copy()


columna_asignados, columna_no_asignados = st.columns(2)


columna_asignados.metric(
    "Tarjetas listas para generar",
    len(registros_asignados),
)


columna_no_asignados.metric(
    "Registros sin plantilla",
    len(registros_sin_asignar),
)


if not registros_sin_asignar.empty:
    st.error(
        f"Hay {len(registros_sin_asignar)} "
        "colaboradores sin una plantilla asignada."
    )

    columnas_sin_asignar = [
        "Empresa",
        "Sucursal",
        "Nombre",
        "Departamento",
        "Puesto",
        "Resultado de validación",
    ]

    with st.expander(
        "Ver colaboradores sin plantilla",
        expanded=True,
    ):
        st.dataframe(
            registros_sin_asignar[
                columnas_sin_asignar
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.warning(
        "Los registros sin plantilla no se incluirán "
        "en los archivos PNG."
    )

else:
    st.success(
        "Todos los colaboradores encontrados tienen "
        "una plantilla asignada."
    )


if registros_asignados.empty:
    st.error(
        "No hay registros válidos para generar tarjetas."
    )

    st.stop()


st.divider()

st.subheader(
    "3. Genera una vista previa"
)


registros_vista = registros_asignados.reset_index(
    drop=True
)


opciones_colaboradores = {}


for indice, fila in registros_vista.iterrows():
    etiqueta = crear_etiqueta_colaborador(
        indice=indice + 1,
        fila=fila,
    )

    opciones_colaboradores[
        etiqueta
    ] = indice


etiqueta_seleccionada = st.selectbox(
    "Colaborador para vista previa",
    options=list(
        opciones_colaboradores.keys()
    ),
)


indice_seleccionado = opciones_colaboradores[
    etiqueta_seleccionada
]


colaborador = registros_vista.iloc[
    indice_seleccionado
]


nombre_colaborador = formato_titulo(
    colaborador["Nombre"]
)


puesto_colaborador = formato_titulo(
    colaborador["Puesto"]
)


fecha_colaborador = formato_fecha_tarjeta(
    colaborador[
        "FechaNacimiento"
    ]
)


plantilla_colaborador = colaborador[
    "Plantilla asignada"
]


columna_datos_1, columna_datos_2 = st.columns(2)


with columna_datos_1:
    st.write(
        f"**Nombre:** {nombre_colaborador}"
    )

    st.write(
        f"**Puesto:** {puesto_colaborador}"
    )

    st.write(
        f"**Fecha:** {fecha_colaborador}"
    )


with columna_datos_2:
    st.write(
        f"**Plantilla:** {plantilla_colaborador}"
    )

    st.write(
        f"**Sucursal:** {colaborador['Sucursal']}"
    )

    st.write(
        f"**Empresa matriz:** {colaborador['Empresa']}"
    )


if st.button(
    "Generar vista previa",
    type="secondary",
    use_container_width=True,
):
    try:
        tarjeta = generar_tarjeta(
            nombre=colaborador[
                "Nombre"
            ],
            puesto=colaborador[
                "Puesto"
            ],
            fecha_nacimiento=colaborador[
                "FechaNacimiento"
            ],
            nombre_plantilla=(
                plantilla_colaborador
            ),
            anio_actual=datetime.now().year,
        )

        nombre_archivo = crear_nombre_archivo(
            nombre_completo=colaborador[
                "Nombre"
            ],
            fecha_nacimiento=colaborador[
                "FechaNacimiento"
            ],
        )

        st.session_state[
            "tarjeta_previa"
        ] = tarjeta.getvalue()

        st.session_state[
            "nombre_tarjeta_previa"
        ] = nombre_archivo

        st.session_state[
            "colaborador_previo"
        ] = etiqueta_seleccionada

    except Exception as error:
        st.error(
            "No fue posible generar la vista previa."
        )

        st.exception(error)


if (
    "tarjeta_previa" in st.session_state
    and "nombre_tarjeta_previa" in st.session_state
    and st.session_state.get(
        "colaborador_previo"
    ) == etiqueta_seleccionada
):
    st.image(
        st.session_state[
            "tarjeta_previa"
        ],
        caption=st.session_state[
            "nombre_tarjeta_previa"
        ],
        use_container_width=True,
    )

    st.download_button(
        label="Descargar esta tarjeta PNG",
        data=st.session_state[
            "tarjeta_previa"
        ],
        file_name=st.session_state[
            "nombre_tarjeta_previa"
        ],
        mime="image/png",
        use_container_width=True,
    )


st.divider()

st.subheader(
    "4. Genera todas las tarjetas"
)


st.write(
    """
    La aplicación generará un PNG por colaborador y
    preparará un archivo ZIP con cinco carpetas:
    DIFARMER, FARMASI, PHARMACEUTIX, DABRA y BARANETOS.
    """
)


st.info(
    "Los archivos duplicados recibirán automáticamente "
    "un consecutivo, por ejemplo: Javier_16_oct_2.png."
)


firma_archivo = (
    archivo_excel.name,
    getattr(
        archivo_excel,
        "size",
        0,
    ),
)


firma_filtros = (
    firma_archivo,
    empresa_seleccionada,
    numero_mes,
    modalidad,
    dia_seleccionado,
    len(cumpleaneros),
)


if (
    "firma_zip" in st.session_state
    and st.session_state[
        "firma_zip"
    ] != firma_filtros
):
    limpiar_resultados_anteriores()


if st.button(
    "Generar todas las tarjetas y preparar ZIP",
    type="primary",
    use_container_width=True,
):
    barra_progreso = st.progress(
        0,
        text="Preparando las tarjetas...",
    )

    texto_progreso = st.empty()


    def actualizar_progreso(
        porcentaje,
        posicion,
        total,
    ):
        """
        Actualiza la barra de progreso de Streamlit.
        """

        porcentaje_entero = int(
            porcentaje * 100
        )

        barra_progreso.progress(
            porcentaje_entero,
            text=(
                f"Generando tarjeta "
                f"{posicion} de {total}"
            ),
        )

        texto_progreso.caption(
            f"Avance: {porcentaje_entero}%"
        )


    try:
        resultado_zip = generar_zip_tarjetas(
            dataframe=cumpleaneros,
            anio_actual=datetime.now().year,
            callback_progreso=(
                actualizar_progreso
            ),
        )

        nombre_zip = crear_nombre_zip(
            numero_mes=numero_mes,
            anio_actual=datetime.now().year,
        )

        st.session_state[
            "resultado_zip"
        ] = resultado_zip

        st.session_state[
            "nombre_zip"
        ] = nombre_zip

        st.session_state[
            "firma_zip"
        ] = firma_filtros

        barra_progreso.progress(
            100,
            text="Proceso terminado.",
        )

        texto_progreso.success(
            "Las tarjetas se generaron correctamente."
        )

    except Exception as error:
        barra_progreso.empty()
        texto_progreso.empty()

        st.error(
            "No fue posible generar el archivo ZIP."
        )

        st.exception(error)


if (
    "resultado_zip" in st.session_state
    and "nombre_zip" in st.session_state
    and st.session_state.get(
        "firma_zip"
    ) == firma_filtros
):
    resultado = st.session_state[
        "resultado_zip"
    ]

    st.write(
        "## Resultado de la generación"
    )

    columna_total, columna_generadas, columna_omitidas = (
        st.columns(3)
    )

    columna_total.metric(
        "Registros procesados",
        resultado[
            "total_registros"
        ],
    )

    columna_generadas.metric(
        "Tarjetas generadas",
        resultado[
            "total_generadas"
        ],
    )

    columna_omitidas.metric(
        "Registros omitidos",
        resultado[
            "total_omitidas"
        ],
    )


    resumen_final = pd.DataFrame(
        [
            {
                "Plantilla": plantilla,
                "Tarjetas generadas": cantidad,
            }
            for plantilla, cantidad
            in resultado[
                "resumen_plantillas"
            ].items()
        ]
    )


    st.write(
        "### Tarjetas por carpeta"
    )


    st.dataframe(
        resumen_final,
        use_container_width=True,
        hide_index=True,
    )


    if resultado[
        "total_generadas"
    ] > 0:
        st.download_button(
            label="⬇️ Descargar ZIP con todas las tarjetas",
            data=resultado[
                "zip_bytes"
            ],
            file_name=st.session_state[
                "nombre_zip"
            ],
            mime="application/zip",
            type="primary",
            use_container_width=True,
        )

        st.success(
            "El ZIP contiene las cinco carpetas de "
            "plantillas y el archivo reporte_generacion.csv."
        )

    else:
        st.error(
            "No se generó ninguna tarjeta. Revisa "
            "el reporte de registros omitidos."
        )


    if resultado[
        "registros_omitidos"
    ]:
        st.warning(
            f"Se omitieron "
            f"{resultado['total_omitidas']} "
            "registros durante la generación."
        )

        reporte_omitidos = pd.DataFrame(
            resultado[
                "registros_omitidos"
            ]
        )

        with st.expander(
            "Ver registros omitidos",
            expanded=True,
        ):
            st.dataframe(
                reporte_omitidos,
                use_container_width=True,
                hide_index=True,
            )
