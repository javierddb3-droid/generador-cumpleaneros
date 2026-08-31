from datetime import date, datetime
import calendar

import pandas as pd
import streamlit as st


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
    Elimina espacios al inicio y al final de los encabezados.
    """
    return str(nombre_columna).strip()


def convertir_fecha_excel(valor):
    """
    Convierte diferentes tipos de fechas a un valor datetime.

    Acepta:
    - Fechas reales de Excel
    - Fechas escritas como texto
    - Números de serie de Excel
    - Valores datetime de Python o pandas
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
        except (ValueError, TypeError, OverflowError):
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
    except (ValueError, TypeError):
        pass

    return pd.to_datetime(
        texto,
        errors="coerce",
        dayfirst=True,
    )


def leer_archivo_excel(archivo):
    """
    Lee la primera hoja del Excel, limpia los encabezados
    y convierte FechaNacimiento.
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
    Devuelve las columnas requeridas que no están en la base.
    """

    return [
        columna
        for columna in COLUMNAS_REQUERIDAS
        if columna not in dataframe.columns
    ]


def normalizar_texto(valor):
    """
    Limpia espacios y convierte texto a mayúsculas
    para realizar comparaciones.
    """

    if pd.isna(valor):
        return ""

    return " ".join(str(valor).strip().upper().split())


def formato_titulo(valor):
    """
    Convierte datos escritos en mayúsculas a formato título.

    Ejemplo:
    JORGE LUIS ANTÍO MÁRQUEZ
    Jorge Luis Antío Márquez
    """

    if pd.isna(valor):
        return ""

    texto = " ".join(str(valor).strip().split())

    return texto.lower().title()


def formato_fecha_tarjeta(fecha_nacimiento):
    """
    Genera la fecha que aparecerá en la tarjeta,
    utilizando el año actual.
    """

    if pd.isna(fecha_nacimiento):
        return ""

    dia = fecha_nacimiento.day
    mes = MESES_MINUSCULAS[fecha_nacimiento.month]
    anio_actual = datetime.now().year

    return f"{dia:02d} de {mes} del {anio_actual}"


def filtrar_cumpleaneros(
    dataframe,
    empresa_seleccionada,
    numero_mes,
    modalidad,
    dia_seleccionado=None,
):
    """
    Filtra colaboradores por empresa, mes y opcionalmente día.
    """

    resultado = dataframe.copy()

    resultado = resultado[
        resultado["FechaNacimiento"].notna()
    ].copy()

    if empresa_seleccionada != "Todas":
        resultado = resultado[
            resultado["Empresa"].apply(normalizar_texto)
            == empresa_seleccionada
        ].copy()

    resultado = resultado[
        resultado["FechaNacimiento"].dt.month == numero_mes
    ].copy()

    if modalidad == "Día específico":
        resultado = resultado[
            resultado["FechaNacimiento"].dt.day
            == dia_seleccionado
        ].copy()

    resultado = resultado.sort_values(
        by=["FechaNacimiento", "Nombre"],
        ascending=[True, True],
    )

    return resultado


st.title("🎂 Generador de plantillas de cumpleaños")

st.write(
    """
    Carga la base de datos, selecciona el periodo y revisa
    los colaboradores antes de generar las tarjetas.
    """
)

st.warning(
    "La base se utiliza temporalmente durante la sesión. "
    "No se guarda dentro del repositorio de GitHub."
)

archivo_excel = st.file_uploader(
    "Selecciona la base de datos en Excel",
    type=["xlsx"],
    help="El archivo debe contener las columnas requeridas.",
)

if archivo_excel is None:
    st.info("Carga un archivo Excel para comenzar.")

else:
    try:
        df = leer_archivo_excel(archivo_excel)

        columnas_faltantes = obtener_columnas_faltantes(df)

        if columnas_faltantes:
            st.error(
                "El archivo no contiene todas las columnas requeridas."
            )

            st.write("### Columnas faltantes")

            for columna in columnas_faltantes:
                st.write(f"- {columna}")

            st.write("### Columnas encontradas")
            st.write(list(df.columns))

        else:
            st.success("El archivo Excel se cargó correctamente.")

            total_registros = len(df)
            fechas_validas = int(
                df["FechaNacimiento"].notna().sum()
            )
            fechas_invalidas = int(
                df["FechaNacimiento"].isna().sum()
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
                        registros_invalidos[columnas_errores],
                        use_container_width=True,
                        hide_index=True,
                    )

            st.divider()

            st.subheader("1. Selecciona los filtros")

            empresas_disponibles = (
                df["Empresa"]
                .dropna()
                .apply(normalizar_texto)
                .loc[lambda serie: serie != ""]
                .sort_values()
                .unique()
                .tolist()
            )

            opciones_empresa = ["Todas"] + empresas_disponibles

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
                    options=list(MESES.values()),
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
                            range(1, ultimo_dia_mes + 1)
                        ),
                    )
                else:
                    st.info(
                        f"Se incluirán todos los cumpleaños "
                        f"de {nombre_mes.lower()}."
                    )

            cumpleaneros = filtrar_cumpleaneros(
                dataframe=df,
                empresa_seleccionada=empresa_seleccionada,
                numero_mes=numero_mes,
                modalidad=modalidad,
                dia_seleccionado=dia_seleccionado,
            )

            st.divider()

            st.subheader("2. Revisa los colaboradores encontrados")

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

            else:
                st.success(
                    f"Se encontraron {len(cumpleaneros)} "
                    f"colaboradores."
                )

                vista_resultados = cumpleaneros[
                    [
                        "Empresa",
                        "Sucursal",
                        "Nombre",
                        "Departamento",
                        "Puesto",
                        "FechaNacimiento",
                    ]
                ].copy()

                vista_resultados["Nombre"] = (
                    vista_resultados["Nombre"]
                    .apply(formato_titulo)
                )

                vista_resultados["Puesto"] = (
                    vista_resultados["Puesto"]
                    .apply(formato_titulo)
                )

                vista_resultados[
                    "Fecha para tarjeta"
                ] = cumpleaneros[
                    "FechaNacimiento"
                ].apply(formato_fecha_tarjeta)

                vista_resultados[
                    "FechaNacimiento"
                ] = cumpleaneros[
                    "FechaNacimiento"
                ].dt.strftime("%d/%m/%Y")

                vista_resultados = vista_resultados.rename(
                    columns={
                        "FechaNacimiento": "Fecha original",
                    }
                )

                st.dataframe(
                    vista_resultados,
                    use_container_width=True,
                    hide_index=True,
                )

                st.info(
                    "En el siguiente paso asignaremos automáticamente "
                    "DIFARMER, FARMASI, PHARMACEUTIX, DABRA o "
                    "BARANETOS a cada colaborador."
                )

    except Exception as error:
        st.error("No fue posible procesar el archivo Excel.")

        st.exception(error)

        st.info(
            "Verifica que el archivo sea un Excel válido con extensión "
            ".xlsx y que no esté protegido con contraseña."
        )
