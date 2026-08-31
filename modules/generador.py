from io import BytesIO
from pathlib import Path
import re
import unicodedata

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_PLANTILLAS = RUTA_PROYECTO / "assets" / "plantillas"
RUTA_FUENTES = RUTA_PROYECTO / "assets" / "fonts"


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


MESES_ABREVIADOS = {
    1: "ene",
    2: "feb",
    3: "mar",
    4: "abr",
    5: "may",
    6: "jun",
    7: "jul",
    8: "ago",
    9: "sep",
    10: "oct",
    11: "nov",
    12: "dic",
}


PARTICULAS_MINUSCULAS = {
    "De",
    "Del",
    "La",
    "Las",
    "Los",
    "Y",
}


CONFIGURACION_PLANTILLAS = {
    "DIFARMER": {
        "archivo": "difarmer.png",
        "nombre": {
            "centro_x": 670,
            "centro_y": 290,
            "ancho_maximo": 510,
            "alto_maximo": 125,
            "tamano_inicial": 48,
            "tamano_minimo": 30,
            "interlineado": 3,
            "color": "#123A67",
        },
        "puesto": {
            "centro_x": 672,
            "centro_y": 380,
            "ancho_maximo": 470,
            "tamano_inicial": 22,
            "tamano_minimo": 15,
            "color": "#EAAF00",
        },
        "fecha": {
            "centro_x": 672,
            "centro_y": 430,
            "ancho_maximo": 470,
            "tamano_inicial": 24,
            "tamano_minimo": 17,
            "color": "#123A67",
        },
    },

    "FARMASI": {
        "archivo": "farmasi.png",
        "nombre": {
            "centro_x": 670,
            "centro_y": 265,
            "ancho_maximo": 510,
            "alto_maximo": 125,
            "tamano_inicial": 48,
            "tamano_minimo": 30,
            "interlineado": 3,
            "color": "#F58220",
        },
        "puesto": {
            "centro_x": 670,
            "centro_y": 365,
            "ancho_maximo": 470,
            "tamano_inicial": 22,
            "tamano_minimo": 15,
            "color": "#173D6D",
        },
        "fecha": {
            "centro_x": 670,
            "centro_y": 423,
            "ancho_maximo": 470,
            "tamano_inicial": 24,
            "tamano_minimo": 17,
            "color": "#173D6D",
        },
    },

    "PHARMACEUTIX": {
        "archivo": "pharmaceutix.png",
        "nombre": {
            "centro_x": 672,
            "centro_y": 264,
            "ancho_maximo": 520,
            "alto_maximo": 125,
            "tamano_inicial": 48,
            "tamano_minimo": 30,
            "interlineado": 3,
            "color": "#63388D",
        },
        "puesto": {
            "centro_x": 672,
            "centro_y": 361,
            "ancho_maximo": 430,
            "tamano_inicial": 22,
            "tamano_minimo": 15,
            "color": "#173D6D",
        },
        "fecha": {
            "centro_x": 672,
            "centro_y": 422,
            "ancho_maximo": 470,
            "tamano_inicial": 24,
            "tamano_minimo": 17,
            "color": "#63388D",
        },
    },

    "DABRA": {
        "archivo": "dabra.png",
        "nombre": {
            "centro_x": 665,
            "centro_y": 260,
            "ancho_maximo": 510,
            "alto_maximo": 125,
            "tamano_inicial": 48,
            "tamano_minimo": 30,
            "interlineado": 3,
            "color": "#C9282D",
        },
        "puesto": {
            "centro_x": 665,
            "centro_y": 363,
            "ancho_maximo": 440,
            "tamano_inicial": 22,
            "tamano_minimo": 15,
            "color": "#173D6D",
        },
        "fecha": {
            "centro_x": 665,
            "centro_y": 422,
            "ancho_maximo": 470,
            "tamano_inicial": 24,
            "tamano_minimo": 17,
            "color": "#173D6D",
        },
    },

    "BARANETOS": {
        "archivo": "baranetos.png",
        "nombre": {
            "centro_x": 670,
            "centro_y": 265,
            "ancho_maximo": 510,
            "alto_maximo": 125,
            "tamano_inicial": 48,
            "tamano_minimo": 30,
            "interlineado": 3,
            "color": "#63388D",
        },
        "puesto": {
            "centro_x": 670,
            "centro_y": 365,
            "ancho_maximo": 470,
            "tamano_inicial": 22,
            "tamano_minimo": 15,
            "color": "#4A9B44",
        },
        "fecha": {
            "centro_x": 670,
            "centro_y": 423,
            "ancho_maximo": 470,
            "tamano_inicial": 24,
            "tamano_minimo": 17,
            "color": "#4A9B44",
        },
    },
}


def limpiar_texto(valor):
    """
    Convierte el valor a texto y elimina espacios innecesarios.
    """

    if pd.isna(valor):
        return ""

    return " ".join(str(valor).strip().split())


def formato_titulo(valor):
    """
    Convierte textos escritos en mayúsculas a formato título.

    Ejemplo:
    JAVIER DE DIOS BOCANEGRA
    Javier de Dios Bocanegra
    """

    texto = limpiar_texto(valor)

    if not texto:
        return ""

    palabras = texto.lower().title().split()
    resultado = []

    for indice, palabra in enumerate(palabras):
        if indice > 0 and palabra in PARTICULAS_MINUSCULAS:
            resultado.append(palabra.lower())
        else:
            resultado.append(palabra)

    return " ".join(resultado)


def obtener_fecha_tarjeta(fecha_nacimiento, anio_actual):
    """
    Genera la fecha que aparecerá dentro de la tarjeta.
    """

    if pd.isna(fecha_nacimiento):
        return ""

    dia = int(fecha_nacimiento.day)
    mes = MESES[int(fecha_nacimiento.month)]

    return f"{dia:02d} de {mes} del {anio_actual}"


def obtener_fuente(negrita, tamano):
    """
    Obtiene Montserrat desde la carpeta assets/fonts.
    """

    if negrita:
        nombres = [
            "Montserrat-Bold.ttf",
            "Montserrat-SemiBold.ttf",
            "Antenna-Bold.ttf",
            "AntennaBold.ttf",
        ]
    else:
        nombres = [
            "Montserrat-Regular.ttf",
            "Antenna-Regular.ttf",
            "AntennaRegular.ttf",
        ]

    for nombre in nombres:
        ruta = RUTA_FUENTES / nombre

        if ruta.exists() and ruta.is_file():
            try:
                return ImageFont.truetype(
                    str(ruta),
                    size=int(tamano),
                )
            except OSError:
                continue

    raise FileNotFoundError(
        "No se encontró la fuente necesaria. "
        "Verifica que Montserrat-Bold.ttf y "
        "Montserrat-Regular.ttf estén dentro de assets/fonts."
    )


def medir_texto(draw, texto, fuente):
    """
    Mide el ancho y alto de un texto de una línea.
    """

    caja = draw.textbbox(
        (0, 0),
        texto,
        font=fuente,
    )

    ancho = caja[2] - caja[0]
    alto = caja[3] - caja[1]

    return ancho, alto


def medir_texto_multilinea(
    draw,
    texto,
    fuente,
    interlineado,
):
    """
    Mide el ancho y alto de un texto de varias líneas.
    """

    caja = draw.multiline_textbbox(
        (0, 0),
        texto,
        font=fuente,
        spacing=interlineado,
        align="center",
    )

    ancho = caja[2] - caja[0]
    alto = caja[3] - caja[1]

    return ancho, alto


def dividir_nombre_equilibrado(
    draw,
    nombre,
    fuente,
    ancho_maximo,
):
    """
    Divide un nombre largo en dos líneas equilibradas.
    """

    palabras = nombre.split()

    if len(palabras) <= 1:
        return nombre

    ancho_nombre, _ = medir_texto(
        draw,
        nombre,
        fuente,
    )

    if ancho_nombre <= ancho_maximo:
        return nombre

    mejor_texto = None
    mejor_diferencia = None

    for indice in range(1, len(palabras)):
        linea_1 = " ".join(palabras[:indice])
        linea_2 = " ".join(palabras[indice:])

        ancho_1, _ = medir_texto(
            draw,
            linea_1,
            fuente,
        )

        ancho_2, _ = medir_texto(
            draw,
            linea_2,
            fuente,
        )

        ancho_mayor = max(ancho_1, ancho_2)

        if ancho_mayor <= ancho_maximo:
            diferencia = abs(ancho_1 - ancho_2)

            if (
                mejor_diferencia is None
                or diferencia < mejor_diferencia
            ):
                mejor_diferencia = diferencia
                mejor_texto = f"{linea_1}\n{linea_2}"

    if mejor_texto:
        return mejor_texto

    punto_medio = max(
        1,
        len(palabras) // 2,
    )

    linea_1 = " ".join(
        palabras[:punto_medio]
    )

    linea_2 = " ".join(
        palabras[punto_medio:]
    )

    return f"{linea_1}\n{linea_2}"


def ajustar_nombre(
    draw,
    nombre,
    configuracion,
):
    """
    Ajusta el nombre al espacio disponible.
    """

    tamano_inicial = configuracion[
        "tamano_inicial"
    ]

    tamano_minimo = configuracion[
        "tamano_minimo"
    ]

    ancho_maximo = configuracion[
        "ancho_maximo"
    ]

    alto_maximo = configuracion[
        "alto_maximo"
    ]

    interlineado = configuracion[
        "interlineado"
    ]

    for tamano in range(
        tamano_inicial,
        tamano_minimo - 1,
        -1,
    ):
        fuente = obtener_fuente(
            negrita=True,
            tamano=tamano,
        )

        texto_ajustado = dividir_nombre_equilibrado(
            draw=draw,
            nombre=nombre,
            fuente=fuente,
            ancho_maximo=ancho_maximo,
        )

        ancho, alto = medir_texto_multilinea(
            draw=draw,
            texto=texto_ajustado,
            fuente=fuente,
            interlineado=interlineado,
        )

        if (
            ancho <= ancho_maximo
            and alto <= alto_maximo
        ):
            return texto_ajustado, fuente

    fuente = obtener_fuente(
        negrita=True,
        tamano=tamano_minimo,
    )

    texto_ajustado = dividir_nombre_equilibrado(
        draw=draw,
        nombre=nombre,
        fuente=fuente,
        ancho_maximo=ancho_maximo,
    )

    return texto_ajustado, fuente


def ajustar_texto_una_linea(
    draw,
    texto,
    ancho_maximo,
    tamano_inicial,
    tamano_minimo,
    negrita,
):
    """
    Reduce un texto gradualmente hasta que cabe.
    """

    for tamano in range(
        tamano_inicial,
        tamano_minimo - 1,
        -1,
    ):
        fuente = obtener_fuente(
            negrita=negrita,
            tamano=tamano,
        )

        ancho, _ = medir_texto(
            draw,
            texto,
            fuente,
        )

        if ancho <= ancho_maximo:
            return fuente

    return obtener_fuente(
        negrita=negrita,
        tamano=tamano_minimo,
    )


def dibujar_texto_centrado(
    draw,
    texto,
    centro_x,
    centro_y,
    fuente,
    color,
):
    """
    Dibuja un texto centrado horizontal y verticalmente.
    """

    caja = draw.textbbox(
        (0, 0),
        texto,
        font=fuente,
    )

    ancho = caja[2] - caja[0]
    alto = caja[3] - caja[1]

    posicion_x = centro_x - (ancho / 2)
    posicion_y = centro_y - (alto / 2) - caja[1]

    draw.text(
        (posicion_x, posicion_y),
        texto,
        font=fuente,
        fill=color,
    )


def dibujar_nombre_centrado(
    draw,
    texto,
    centro_x,
    centro_y,
    fuente,
    color,
    interlineado,
):
    """
    Dibuja un nombre centrado en una o dos líneas.
    """

    caja = draw.multiline_textbbox(
        (0, 0),
        texto,
        font=fuente,
        spacing=interlineado,
        align="center",
    )

    ancho = caja[2] - caja[0]
    alto = caja[3] - caja[1]

    posicion_x = centro_x - (ancho / 2)
    posicion_y = centro_y - (alto / 2) - caja[1]

    draw.multiline_text(
        (posicion_x, posicion_y),
        texto,
        font=fuente,
        fill=color,
        spacing=interlineado,
        align="center",
    )


def validar_plantilla(nombre_plantilla):
    """
    Comprueba que la plantilla exista.
    """

    if nombre_plantilla not in CONFIGURACION_PLANTILLAS:
        raise ValueError(
            f"No existe configuración para {nombre_plantilla}."
        )

    configuracion = CONFIGURACION_PLANTILLAS[
        nombre_plantilla
    ]

    ruta_plantilla = (
        RUTA_PLANTILLAS
        / configuracion["archivo"]
    )

    if not ruta_plantilla.exists():
        raise FileNotFoundError(
            "No se encontró la plantilla: "
            f"{ruta_plantilla}"
        )

    return configuracion, ruta_plantilla


def generar_tarjeta(
    nombre,
    puesto,
    fecha_nacimiento,
    nombre_plantilla,
    anio_actual,
):
    """
    Genera la tarjeta de cumpleaños en PNG.
    """

    configuracion, ruta_plantilla = validar_plantilla(
        nombre_plantilla
    )

    imagen = Image.open(
        ruta_plantilla
    ).convert("RGBA")

    if imagen.size != (960, 720):
        raise ValueError(
            f"La plantilla {nombre_plantilla} mide "
            f"{imagen.width} x {imagen.height}. "
            "El tamaño esperado es 960 x 720."
        )

    draw = ImageDraw.Draw(imagen)

    nombre_formateado = formato_titulo(
        nombre
    )

    puesto_formateado = formato_titulo(
        puesto
    )

    fecha_formateada = obtener_fecha_tarjeta(
        fecha_nacimiento=fecha_nacimiento,
        anio_actual=anio_actual,
    )

    configuracion_nombre = configuracion[
        "nombre"
    ]

    nombre_ajustado, fuente_nombre = ajustar_nombre(
        draw=draw,
        nombre=nombre_formateado,
        configuracion=configuracion_nombre,
    )

    dibujar_nombre_centrado(
        draw=draw,
        texto=nombre_ajustado,
        centro_x=configuracion_nombre[
            "centro_x"
        ],
        centro_y=configuracion_nombre[
            "centro_y"
        ],
        fuente=fuente_nombre,
        color=configuracion_nombre[
            "color"
        ],
        interlineado=configuracion_nombre[
            "interlineado"
        ],
    )

    configuracion_puesto = configuracion[
        "puesto"
    ]

    fuente_puesto = ajustar_texto_una_linea(
        draw=draw,
        texto=puesto_formateado,
        ancho_maximo=configuracion_puesto[
            "ancho_maximo"
        ],
        tamano_inicial=configuracion_puesto[
            "tamano_inicial"
        ],
        tamano_minimo=configuracion_puesto[
            "tamano_minimo"
        ],
        negrita=True,
    )

    dibujar_texto_centrado(
        draw=draw,
        texto=puesto_formateado,
        centro_x=configuracion_puesto[
            "centro_x"
        ],
        centro_y=configuracion_puesto[
            "centro_y"
        ],
        fuente=fuente_puesto,
        color=configuracion_puesto[
            "color"
        ],
    )

    configuracion_fecha = configuracion[
        "fecha"
    ]

    fuente_fecha = ajustar_texto_una_linea(
        draw=draw,
        texto=fecha_formateada,
        ancho_maximo=configuracion_fecha[
            "ancho_maximo"
        ],
        tamano_inicial=configuracion_fecha[
            "tamano_inicial"
        ],
        tamano_minimo=configuracion_fecha[
            "tamano_minimo"
        ],
        negrita=False,
    )

    dibujar_texto_centrado(
        draw=draw,
        texto=fecha_formateada,
        centro_x=configuracion_fecha[
            "centro_x"
        ],
        centro_y=configuracion_fecha[
            "centro_y"
        ],
        fuente=fuente_fecha,
        color=configuracion_fecha[
            "color"
        ],
    )

    salida = BytesIO()

    imagen.save(
        salida,
        format="PNG",
        optimize=True,
    )

    salida.seek(0)

    return salida


def primer_nombre(nombre_completo):
    """
    Obtiene únicamente el primer nombre.
    """

    nombre_limpio = formato_titulo(
        nombre_completo
    )

    if not nombre_limpio:
        return "Sin_nombre"

    return nombre_limpio.split()[0]


def limpiar_nombre_archivo(texto):
    """
    Limpia caracteres problemáticos del nombre de archivo.
    """

    texto = str(texto).strip()

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
        r"[^A-Za-z0-9_-]",
        "_",
        texto,
    )

    texto = re.sub(
        r"_+",
        "_",
        texto,
    )

    return texto.strip("_")


def crear_nombre_archivo(
    nombre_completo,
    fecha_nacimiento,
):
    """
    Crea el nombre final del PNG.

    Ejemplo:
    Javier_16_oct.png
    """

    nombre = primer_nombre(
        nombre_completo
    )

    nombre = limpiar_nombre_archivo(
        nombre
    )

    dia = int(
        fecha_nacimiento.day
    )

    mes = MESES_ABREVIADOS[
        int(fecha_nacimiento.month)
    ]

    return f"{nombre}_{dia:02d}_{mes}.png"
