import re
import unicodedata


# Las claves se escriben:
# - En minúsculas
# - Sin acentos
#
# Los valores contienen la escritura que aparecerá
# dentro de la plantilla.
#
# Ejemplo:
# "jose": "José"


CORRECCIONES_NOMBRES = {
    "aaron": "Aarón",
    "abdon": "Abdón",
    "abel": "Abel",
    "abelardo": "Abelardo",
    "abigail": "Abigail",
    "abraham": "Abraham",
    "adan": "Adán",
    "adela": "Adela",
    "adelaida": "Adelaida",
    "adelina": "Adelina",
    "adriana": "Adriana",
    "adrian": "Adrián",
    "agustin": "Agustín",
    "agustina": "Agustina",
    "alberto": "Alberto",
    "alejandra": "Alejandra",
    "alejandro": "Alejandro",
    "alexis": "Alexis",
    "alfonso": "Alfonso",
    "alfredo": "Alfredo",
    "alicia": "Alicia",
    "alma": "Alma",
    "alonso": "Alonso",
    "alvaro": "Álvaro",
    "amador": "Amador",
    "amalia": "Amalia",
    "amanda": "Amanda",
    "america": "América",
    "amparo": "Amparo",
    "ana": "Ana",
    "anabel": "Anabel",
    "anahi": "Anahí",
    "andrea": "Andrea",
    "andres": "Andrés",
    "angel": "Ángel",
    "angela": "Ángela",
    "angelica": "Angélica",
    "angeles": "Ángeles",
    "antonio": "Antonio",
    "antonia": "Antonia",
    "antio": "Antío",
    "araceli": "Araceli",
    "aracely": "Aracely",
    "aranzazu": "Aránzazu",
    "armando": "Armando",
    "arnulfo": "Arnulfo",
    "arturo": "Arturo",
    "asuncion": "Asunción",
    "augusto": "Augusto",
    "aurelio": "Aurelio",
    "aurora": "Aurora",
    "azucena": "Azucena",
    "barbara": "Bárbara",
    "beatriz": "Beatriz",
    "belen": "Belén",
    "benito": "Benito",
    "benjamin": "Benjamín",
    "berenice": "Berenice",
    "bernabe": "Bernabé",
    "bernardo": "Bernardo",
    "blanca": "Blanca",
    "brenda": "Brenda",
    "bruno": "Bruno",
    "camila": "Camila",
    "candelaria": "Candelaria",
    "carina": "Carina",
    "carla": "Carla",
    "carlos": "Carlos",
    "carmen": "Carmen",
    "carolina": "Carolina",
    "catalina": "Catalina",
    "cecilia": "Cecilia",
    "celeste": "Celeste",
    "cesar": "César",
    "christian": "Christian",
    "cinthia": "Cinthia",
    "clara": "Clara",
    "claudia": "Claudia",
    "claudio": "Claudio",
    "concepcion": "Concepción",
    "consuelo": "Consuelo",
    "cristian": "Cristian",
    "cristina": "Cristina",
    "cristobal": "Cristóbal",
    "dalia": "Dalia",
    "damian": "Damián",
    "daniel": "Daniel",
    "daniela": "Daniela",
    "david": "David",
    "debora": "Débora",
    "demetrio": "Demetrio",
    "diana": "Diana",
    "diego": "Diego",
    "dolores": "Dolores",
    "domingo": "Domingo",
    "donato": "Donato",
    "edgar": "Edgar",
    "edith": "Edith",
    "eduardo": "Eduardo",
    "efrain": "Efraín",
    "elena": "Elena",
    "eleuterio": "Eleuterio",
    "elia": "Elia",
    "elias": "Elías",
    "elisa": "Elisa",
    "elizabeth": "Elizabeth",
    "elvira": "Elvira",
    "emanuel": "Emanuel",
    "emiliano": "Emiliano",
    "emilio": "Emilio",
    "emmanuel": "Emmanuel",
    "enrique": "Enrique",
    "erendira": "Eréndira",
    "erica": "Érica",
    "erika": "Érika",
    "ernesto": "Ernesto",
    "esmeralda": "Esmeralda",
    "esperanza": "Esperanza",
    "esteban": "Esteban",
    "estefania": "Estefanía",
    "eugenia": "Eugenia",
    "eugenio": "Eugenio",
    "eusebio": "Eusebio",
    "eva": "Eva",
    "evangelina": "Evangelina",
    "ezequiel": "Ezequiel",
    "fabian": "Fabián",
    "fabio": "Fabio",
    "fatima": "Fátima",
    "fausto": "Fausto",
    "felipe": "Felipe",
    "felix": "Félix",
    "fernanda": "Fernanda",
    "fernando": "Fernando",
    "fidel": "Fidel",
    "flor": "Flor",
    "florencia": "Florencia",
    "francisco": "Francisco",
    "francisca": "Francisca",
    "gabriel": "Gabriel",
    "gabriela": "Gabriela",
    "genaro": "Genaro",
    "genesis": "Génesis",
    "gerardo": "Gerardo",
    "german": "Germán",
    "geronimo": "Gerónimo",
    "gilberto": "Gilberto",
    "gloria": "Gloria",
    "gonzalo": "Gonzalo",
    "graciela": "Graciela",
    "gregorio": "Gregorio",
    "guadalupe": "Guadalupe",
    "gustavo": "Gustavo",
    "hector": "Héctor",
    "heriberto": "Heriberto",
    "herminia": "Herminia",
    "herminio": "Herminio",
    "hilda": "Hilda",
    "hipolito": "Hipólito",
    "hortencia": "Hortensia",
    "hortensia": "Hortensia",
    "humberto": "Humberto",
    "ignacio": "Ignacio",
    "iliana": "Iliana",
    "ines": "Inés",
    "irene": "Irene",
    "irma": "Irma",
    "isaac": "Isaac",
    "isabel": "Isabel",
    "isabela": "Isabela",
    "isaias": "Isaías",
    "ismael": "Ismael",
    "ivan": "Iván",
    "jacinto": "Jacinto",
    "jacqueline": "Jacqueline",
    "jaime": "Jaime",
    "javier": "Javier",
    "jazmin": "Jazmín",
    "jeronimo": "Jerónimo",
    "jesus": "Jesús",
    "jhoana": "Jhoana",
    "joaquin": "Joaquín",
    "jose": "José",
    "josefina": "Josefina",
    "josue": "Josué",
    "juan": "Juan",
    "juana": "Juana",
    "judith": "Judith",
    "julia": "Julia",
    "julian": "Julián",
    "juliana": "Juliana",
    "julio": "Julio",
    "karina": "Karina",
    "karla": "Karla",
    "lara": "Lara",
    "laura": "Laura",
    "lazaro": "Lázaro",
    "leon": "León",
    "leonardo": "Leonardo",
    "leopoldo": "Leopoldo",
    "leticia": "Leticia",
    "lidia": "Lidia",
    "liliana": "Liliana",
    "lilia": "Lilia",
    "lorena": "Lorena",
    "lorenzo": "Lorenzo",
    "lucas": "Lucas",
    "lucia": "Lucía",
    "luciano": "Luciano",
    "lucila": "Lucila",
    "lucio": "Lucio",
    "lucrecia": "Lucrecia",
    "luis": "Luis",
    "luisa": "Luisa",
    "luz": "Luz",
    "magdalena": "Magdalena",
    "manuel": "Manuel",
    "manuela": "Manuela",
    "marcela": "Marcela",
    "marcelino": "Marcelino",
    "marcelo": "Marcelo",
    "marco": "Marco",
    "marcos": "Marcos",
    "margarita": "Margarita",
    "maria": "María",
    "mariana": "Mariana",
    "maribel": "Maribel",
    "maricela": "Maricela",
    "marisela": "Marisela",
    "marisol": "Marisol",
    "martha": "Martha",
    "martin": "Martín",
    "matias": "Matías",
    "mauricio": "Mauricio",
    "maximiliano": "Maximiliano",
    "maximo": "Máximo",
    "mayra": "Mayra",
    "melanie": "Melanie",
    "melchor": "Melchor",
    "mercedes": "Mercedes",
    "micaela": "Micaela",
    "miguel": "Miguel",
    "minerva": "Minerva",
    "miriam": "Miriam",
    "mirna": "Mirna",
    "monica": "Mónica",
    "nadia": "Nadia",
    "nancy": "Nancy",
    "natalia": "Natalia",
    "natividad": "Natividad",
    "nazario": "Nazario",
    "nestor": "Néstor",
    "nicolas": "Nicolás",
    "noe": "Noé",
    "noemi": "Noemí",
    "norma": "Norma",
    "octavio": "Octavio",
    "ofelia": "Ofelia",
    "olga": "Olga",
    "omar": "Omar",
    "oralia": "Oralia",
    "orlando": "Orlando",
    "oscar": "Óscar",
    "osvaldo": "Osvaldo",
    "pablo": "Pablo",
    "paloma": "Paloma",
    "paola": "Paola",
    "patricia": "Patricia",
    "paulina": "Paulina",
    "pedro": "Pedro",
    "pilar": "Pilar",
    "porfirio": "Porfirio",
    "priscila": "Priscila",
    "rafael": "Rafael",
    "ramiro": "Ramiro",
    "ramon": "Ramón",
    "raul": "Raúl",
    "rebeca": "Rebeca",
    "refugio": "Refugio",
    "regina": "Regina",
    "remedios": "Remedios",
    "rene": "René",
    "renee": "Renée",
    "reyna": "Reyna",
    "ricardo": "Ricardo",
    "rigoberto": "Rigoberto",
    "rita": "Rita",
    "roberto": "Roberto",
    "rocio": "Rocío",
    "rogelio": "Rogelio",
    "roman": "Román",
    "romina": "Romina",
    "romulo": "Rómulo",
    "rosa": "Rosa",
    "rosalia": "Rosalía",
    "rosario": "Rosario",
    "ruben": "Rubén",
    "salvador": "Salvador",
    "salomon": "Salomón",
    "samanta": "Samanta",
    "samantha": "Samantha",
    "samuel": "Samuel",
    "sandra": "Sandra",
    "santiago": "Santiago",
    "sara": "Sara",
    "saul": "Saúl",
    "sebastian": "Sebastián",
    "serafin": "Serafín",
    "sergio": "Sergio",
    "silvia": "Silvia",
    "socorro": "Socorro",
    "sofia": "Sofía",
    "sonia": "Sonia",
    "susana": "Susana",
    "tamara": "Tamara",
    "teresa": "Teresa",
    "tomas": "Tomás",
    "ulises": "Ulises",
    "valentin": "Valentín",
    "valentina": "Valentina",
    "vanessa": "Vanessa",
    "veronica": "Verónica",
    "vicente": "Vicente",
    "victor": "Víctor",
    "victoria": "Victoria",
    "virginia": "Virginia",
    "ximena": "Ximena",
    "yadira": "Yadira",
    "yolanda": "Yolanda",
    "yuridia": "Yuridia",
    "zacarias": "Zacarías",
}


CORRECCIONES_APELLIDOS = {
    "acevedo": "Acevedo",
    "acosta": "Acosta",
    "aguilar": "Aguilar",
    "aguirre": "Aguirre",
    "alanis": "Alanís",
    "alarcon": "Alarcón",
    "alba": "Alba",
    "alcantar": "Alcántar",
    "alcantara": "Alcántara",
    "alcaraz": "Alcaraz",
    "aleman": "Alemán",
    "alfaro": "Alfaro",
    "almaraz": "Almaraz",
    "alonso": "Alonso",
    "altamirano": "Altamirano",
    "alvarez": "Álvarez",
    "amador": "Amador",
    "andrade": "Andrade",
    "angulo": "Angulo",
    "aragon": "Aragón",
    "aranda": "Aranda",
    "araujo": "Araujo",
    "arellano": "Arellano",
    "arenas": "Arenas",
    "arias": "Arias",
    "armendariz": "Armendáriz",
    "arroyo": "Arroyo",
    "arteaga": "Arteaga",
    "avila": "Ávila",
    "aviles": "Avilés",
    "ayala": "Ayala",
    "baez": "Báez",
    "balderas": "Balderas",
    "banda": "Banda",
    "bañuelos": "Bañuelos",
    "banuelos": "Bañuelos",
    "barrera": "Barrera",
    "barron": "Barrón",
    "bautista": "Bautista",
    "becerra": "Becerra",
    "beltran": "Beltrán",
    "benitez": "Benítez",
    "bernal": "Bernal",
    "blanco": "Blanco",
    "bravo": "Bravo",
    "briseño": "Briseño",
    "briseno": "Briseño",
    "bustamante": "Bustamante",
    "bustos": "Bustos",
    "cabrera": "Cabrera",
    "calderon": "Calderón",
    "camacho": "Camacho",
    "campos": "Campos",
    "cano": "Cano",
    "cantu": "Cantú",
    "cardenas": "Cárdenas",
    "carmona": "Carmona",
    "carranza": "Carranza",
    "carrasco": "Carrasco",
    "carrillo": "Carrillo",
    "casas": "Casas",
    "castañeda": "Castañeda",
    "castaneda": "Castañeda",
    "castellanos": "Castellanos",
    "castillo": "Castillo",
    "castro": "Castro",
    "cervantes": "Cervantes",
    "chavez": "Chávez",
    "cisneros": "Cisneros",
    "contreras": "Contreras",
    "corona": "Corona",
    "coronado": "Coronado",
    "cordova": "Córdova",
    "cortes": "Cortés",
    "cortez": "Cortez",
    "covarrubias": "Covarrubias",
    "cruz": "Cruz",
    "cuevas": "Cuevas",
    "davila": "Dávila",
    "deanda": "de Anda",
    "delacruz": "de la Cruz",
    "deleo": "de Leo",
    "delgado": "Delgado",
    "diaz": "Díaz",
    "dominguez": "Domínguez",
    "duarte": "Duarte",
    "duran": "Durán",
    "elias": "Elías",
    "enriquez": "Enríquez",
    "escamilla": "Escamilla",
    "escobar": "Escobar",
    "esparza": "Esparza",
    "espinosa": "Espinosa",
    "espinoza": "Espinoza",
    "estrada": "Estrada",
    "farias": "Farías",
    "fernandez": "Fernández",
    "fierro": "Fierro",
    "figueroa": "Figueroa",
    "flores": "Flores",
    "fonseca": "Fonseca",
    "franco": "Franco",
    "fuentes": "Fuentes",
    "galindo": "Galindo",
    "gallardo": "Gallardo",
    "gallegos": "Gallegos",
    "galvan": "Galván",
    "garcia": "García",
    "garza": "Garza",
    "gaytan": "Gaytán",
    "gil": "Gil",
    "giron": "Girón",
    "godinez": "Godínez",
    "gomez": "Gómez",
    "gonzalez": "González",
    "gracia": "Gracia",
    "granados": "Granados",
    "guajardo": "Guajardo",
    "guerra": "Guerra",
    "guerrero": "Guerrero",
    "guevara": "Guevara",
    "gutierrez": "Gutiérrez",
    "guzman": "Guzmán",
    "haros": "Haros",
    "heredia": "Heredia",
    "hernandez": "Hernández",
    "herrera": "Herrera",
    "hidalgo": "Hidalgo",
    "holguin": "Holguín",
    "huerta": "Huerta",
    "ibañez": "Ibáñez",
    "ibanez": "Ibáñez",
    "ibarra": "Ibarra",
    "iglesias": "Iglesias",
    "jara": "Jara",
    "jauregui": "Jáuregui",
    "jimenez": "Jiménez",
    "juarez": "Juárez",
    "lara": "Lara",
    "ledesma": "Ledesma",
    "leon": "León",
    "leyva": "Leyva",
    "limon": "Limón",
    "lira": "Lira",
    "loera": "Loera",
    "lomas": "Lomas",
    "lopez": "López",
    "lozano": "Lozano",
    "lucero": "Lucero",
    "luna": "Luna",
    "macias": "Macías",
    "maldonado": "Maldonado",
    "manriquez": "Manríquez",
    "marin": "Marín",
    "mariscal": "Mariscal",
    "marquez": "Márquez",
    "martinez": "Martínez",
    "martin": "Martín",
    "mata": "Mata",
    "medina": "Medina",
    "mejia": "Mejía",
    "mendez": "Méndez",
    "mendoza": "Mendoza",
    "mercado": "Mercado",
    "miranda": "Miranda",
    "molina": "Molina",
    "monroy": "Monroy",
    "montaño": "Montaño",
    "montano": "Montaño",
    "montañez": "Montañez",
    "montanez": "Montañez",
    "montero": "Montero",
    "montes": "Montes",
    "mora": "Mora",
    "morales": "Morales",
    "moreno": "Moreno",
    "mota": "Mota",
    "muñoz": "Muñoz",
    "munoz": "Muñoz",
    "murillo": "Murillo",
    "nava": "Nava",
    "navarro": "Navarro",
    "negrete": "Negrete",
    "nieto": "Nieto",
    "nuñez": "Núñez",
    "nunez": "Núñez",
    "ocampo": "Ocampo",
    "ochoa": "Ochoa",
    "ojeda": "Ojeda",
    "olguin": "Olguín",
    "olivares": "Olivares",
    "olvera": "Olvera",
    "ontiveros": "Ontiveros",
    "orozco": "Orozco",
    "ortega": "Ortega",
    "ortiz": "Ortiz",
    "osuna": "Osuna",
    "pacheco": "Pacheco",
    "padilla": "Padilla",
    "palacios": "Palacios",
    "pantoja": "Pantoja",
    "parra": "Parra",
    "partida": "Partida",
    "patiño": "Patiño",
    "patino": "Patiño",
    "peña": "Peña",
    "pena": "Peña",
    "peralta": "Peralta",
    "perea": "Perea",
    "perez": "Pérez",
    "pineda": "Pineda",
    "plascencia": "Plascencia",
    "ponce": "Ponce",
    "prieto": "Prieto",
    "puente": "Puente",
    "quintero": "Quintero",
    "quiroz": "Quiroz",
    "ramirez": "Ramírez",
    "ramos": "Ramos",
    "rendon": "Rendón",
    "renteria": "Rentería",
    "resendiz": "Reséndiz",
    "reyes": "Reyes",
    "reyna": "Reyna",
    "rios": "Ríos",
    "rivera": "Rivera",
    "rocha": "Rocha",
    "rodriguez": "Rodríguez",
    "rojas": "Rojas",
    "roman": "Román",
    "romero": "Romero",
    "rosales": "Rosales",
    "rubio": "Rubio",
    "ruiz": "Ruiz",
    "saavedra": "Saavedra",
    "salas": "Salas",
    "salazar": "Salazar",
    "salgado": "Salgado",
    "salinas": "Salinas",
    "sanchez": "Sánchez",
    "sandoval": "Sandoval",
    "santana": "Santana",
    "santiago": "Santiago",
    "santillan": "Santillán",
    "santos": "Santos",
    "sauceda": "Sauceda",
    "saucedo": "Saucedo",
    "sepulveda": "Sepúlveda",
    "serrano": "Serrano",
    "silva": "Silva",
    "solano": "Solano",
    "solis": "Solís",
    "soria": "Soria",
    "soto": "Soto",
    "suarez": "Suárez",
    "tapia": "Tapia",
    "tellez": "Téllez",
    "teran": "Terán",
    "torres": "Torres",
    "tovar": "Tovar",
    "trejo": "Trejo",
    "treviño": "Treviño",
    "trevino": "Treviño",
    "trujillo": "Trujillo",
    "urbina": "Urbina",
    "uribe": "Uribe",
    "valdez": "Valdez",
    "valencia": "Valencia",
    "vargas": "Vargas",
    "vazquez": "Vázquez",
    "vega": "Vega",
    "vela": "Vela",
    "velasco": "Velasco",
    "velez": "Vélez",
    "velazquez": "Velázquez",
    "verdugo": "Verdugo",
    "villa": "Villa",
    "villalobos": "Villalobos",
    "villanueva": "Villanueva",
    "villarreal": "Villarreal",
    "zamora": "Zamora",
    "zapata": "Zapata",
    "zarate": "Zárate",
    "zavala": "Zavala",
    "zepeda": "Zepeda",
    "zuñiga": "Zúñiga",
    "zuniga": "Zúñiga",
}


PARTICULAS_MINUSCULAS = {
    "de",
    "del",
    "la",
    "las",
    "los",
    "y",
    "e",
    "da",
    "das",
    "do",
    "dos",
    "van",
    "von",
}


def quitar_acentos(texto):
    """
    Convierte letras acentuadas a su forma base.

    Ejemplos:
    José -> Jose
    Núñez -> Nunez
    García -> Garcia
    """

    texto_normalizado = unicodedata.normalize(
        "NFKD",
        str(texto),
    )

    return "".join(
        caracter
        for caracter in texto_normalizado
        if not unicodedata.combining(caracter)
    )


def clave_palabra(palabra):
    """
    Prepara una palabra para buscarla dentro del diccionario.

    La clave final:
    - Está en minúsculas
    - No contiene acentos
    - No contiene signos de puntuación
    """

    texto = quitar_acentos(palabra)
    texto = texto.lower().strip()

    return re.sub(
        r"[^a-zñ]",
        "",
        texto,
    )


def separar_puntuacion(palabra):
    """
    Separa signos situados antes y después de una palabra.

    Ejemplo:
    "(JOSE)" -> "(", "JOSE", ")"
    """

    coincidencia = re.match(
        (
            r"^("
            r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ]*"
            r")("
            r".*?"
            r")("
            r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ]*"
            r")$"
        ),
        palabra,
    )

    if not coincidencia:
        return "", palabra, ""

    return coincidencia.groups()


def aplicar_mayuscula_inicial(texto):
    """
    Coloca mayúscula inicial sin modificar los acentos.

    Ejemplos:
    jose -> Jose
    josé -> José
    """

    if not texto:
        return ""

    return texto[0].upper() + texto[1:].lower()


def corregir_palabra(
    palabra,
    diccionario_principal,
    diccionario_secundario=None,
):
    """
    Corrige una palabra buscando primero en el diccionario principal.

    Si la palabra no está en el diccionario principal, también puede
    buscarla dentro de un diccionario secundario.
    """

    prefijo, contenido, sufijo = separar_puntuacion(
        palabra
    )

    if not contenido:
        return palabra

    clave = clave_palabra(contenido)

    if clave in diccionario_principal:
        correccion = diccionario_principal[clave]

    elif (
        diccionario_secundario is not None
        and clave in diccionario_secundario
    ):
        correccion = diccionario_secundario[clave]

    else:
        correccion = aplicar_mayuscula_inicial(
            contenido
        )

    return (
        f"{prefijo}"
        f"{correccion}"
        f"{sufijo}"
    )


def corregir_nombre_completo(nombre_completo):
    """
    Corrige nombres y apellidos mediante los diccionarios.

    Reglas:
    1. Las primeras dos palabras significativas se tratan
       principalmente como nombres.
    2. Las palabras restantes se tratan principalmente
       como apellidos.
    3. Las partículas como de, del, la, los y las
       permanecen en minúsculas.
    4. Cuando una palabra no se encuentra en su catálogo principal,
       también se busca en el catálogo secundario.
    5. Si la palabra no aparece en ningún catálogo, se conserva
       en formato de mayúscula inicial.
    """

    if nombre_completo is None:
        return ""

    texto = " ".join(
        str(nombre_completo).strip().split()
    )

    if not texto:
        return ""

    palabras = texto.split()
    resultado = []

    palabras_significativas = 0

    for indice, palabra in enumerate(palabras):
        clave = clave_palabra(palabra)

        if (
            clave in PARTICULAS_MINUSCULAS
            and indice > 0
        ):
            resultado.append(clave)
            continue

        if palabras_significativas < 2:
            palabra_corregida = corregir_palabra(
                palabra=palabra,
                diccionario_principal=(
                    CORRECCIONES_NOMBRES
                ),
                diccionario_secundario=(
                    CORRECCIONES_APELLIDOS
                ),
            )

        else:
            palabra_corregida = corregir_palabra(
                palabra=palabra,
                diccionario_principal=(
                    CORRECCIONES_APELLIDOS
                ),
                diccionario_secundario=(
                    CORRECCIONES_NOMBRES
                ),
            )

        resultado.append(
            palabra_corregida
        )

        palabras_significativas += 1

    return " ".join(resultado)


def obtener_cambios_nombre(nombre_original):
    """
    Devuelve el nombre original, el nombre corregido
    y una indicación de si hubo cambios.

    Esta función puede utilizarse posteriormente para mostrar
    una tabla de revisión dentro de Streamlit.
    """

    nombre_original_limpio = " ".join(
        str(nombre_original).strip().split()
    )

    nombre_corregido = corregir_nombre_completo(
        nombre_original_limpio
    )

    cambio = (
        nombre_original_limpio
        != nombre_corregido
    )

    return {
        "Nombre original": nombre_original_limpio,
        "Nombre corregido": nombre_corregido,
        "Tuvo corrección": cambio,
    }
