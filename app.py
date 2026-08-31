import streamlit as st
import pandas as pd


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


def limpiar_nombre_columna(nombre_columna):
    """
    Elimina espacios al inicio y al final de los encabezados.
    """
    return str(nombre_columna).strip()


def convertir_fecha_excel(valor):
    """
    Convierte diferentes tipos de fechas a un valor datetime.

    La función acepta:
    - Fechas reales de Excel
    - Fechas escritas como texto
    - Números de serie de Excel
    - Valores datetime de pandas
    """

    if pd.isna(valor):
        return pd.NaT

    # Si pandas u openpyxl ya lo reconocieron como fecha
    if isinstance(valor, (pd.Timestamp,)):
        return valor

    # Intentar detectar números de serie de Excel
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

    # Si el valor es texto, pero contiene un número de Excel
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

    # Intentar convertir fechas escritas con día primero
    return pd.to_datetime(
        texto,
        errors="coerce",
        dayfirst=True,
    )


def leer_archivo_excel(archivo):
    """
    Lee la primera hoja del Excel, limpia los encabezados
    y convierte la columna FechaNacimiento.
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
    Devuelve las columnas requeridas que no se encontraron.
    """

    return [
        columna
        for columna in COLUMNAS_REQUERIDAS
        if columna not in dataframe.columns
    ]


st.title("🎂 Generador de plantillas de cumpleaños")

st.write(
    """
    Carga la base de datos de colaboradores para validar su estructura
    y revisar las fechas de nacimiento antes de generar las tarjetas.
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

            st.write("## Vista previa de la base")

            columnas_vista_previa = [
                "Empresa",
                "Sucursal",
                "Nombre",
                "Departamento",
                "Puesto",
                "FechaNacimiento",
            ]

            st.dataframe(
                df[columnas_vista_previa].head(50),
                use_container_width=True,
                hide_index=True,
            )

            if fechas_invalidas > 0:
                st.warning(
                    "Algunos registros tienen una fecha de nacimiento "
                    "vacía o que no pudo interpretarse."
                )

                registros_invalidos = df[
                    df["FechaNacimiento"].isna()
                ].copy()

                columnas_errores = [
                    "Empresa",
                    "Sucursal",
                    "Nombre",
                    "FechaNacimientoOriginal",
                ]

                st.write("## Registros con fecha inválida")

                st.dataframe(
                    registros_invalidos[columnas_errores],
                    use_container_width=True,
                    hide_index=True,
                )

            st.write("## Empresas encontradas")

            empresas = (
                df["Empresa"]
                .dropna()
                .astype(str)
                .str.strip()
                .str.upper()
                .sort_values()
                .unique()
                .tolist()
            )

            st.write(empresas)

            st.write("## Sucursales encontradas")

            sucursales = (
                df["Sucursal"]
                .dropna()
                .astype(str)
                .str.strip()
                .sort_values()
                .unique()
                .tolist()
            )

            st.write(
                f"Se encontraron {len(sucursales)} sucursales diferentes."
            )

            with st.expander("Ver catálogo de sucursales"):
                for sucursal in sucursales:
                    st.write(f"- {sucursal}")

    except Exception as error:
        st.error("No fue posible procesar el archivo Excel.")

        st.exception(error)

        st.info(
            "Verifica que el archivo sea un Excel válido con extensión "
            ".xlsx y que no esté protegido con contraseña."
        )
