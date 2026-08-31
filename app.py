import streamlit as st


st.set_page_config(
    page_title="Generador de Cumpleañeros",
    page_icon="🎂",
    layout="wide",
)


st.title("🎂 Generador de plantillas de cumpleaños")

st.write(
    """
    Esta aplicación permitirá cargar una base de datos en Excel,
    filtrar a los colaboradores por fecha de cumpleaños y generar
    automáticamente las tarjetas correspondientes.
    """
)

st.success("La aplicación se inició correctamente.")

st.info(
    "En los siguientes pasos agregaremos la carga del Excel, "
    "los filtros y la generación de las tarjetas."
)
