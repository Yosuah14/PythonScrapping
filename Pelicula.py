from bs4 import BeautifulSoup
import requests
from datetime import datetime

# Define la clase Pelicula para almacenar información sobre películas
class Pelicula:
    def __init__(self, titulo, fecha_lanzamiento, imagen, generos, sinopsis, director, reparto,rate):
        # Inicializa los atributos de la película
        self.titulo = titulo
        self.fecha_lanzamiento = fecha_lanzamiento
        self.imagen = imagen
        self.generos = generos
        self.sinopsis = sinopsis
        self.director = director
        self.reparto = reparto
        self.rate = rate

    def imprimir_info(self):
        # Método para imprimir información sobre la peli
        print(f"Título: {self.titulo}")
        print(f"Fecha de lanzamiento: {self.fecha_lanzamiento}")
        print(f"Imagen: {self.imagen}")
        print(f"Géneros: {', '.join(self.generos)}")
        print(f"Sinopsis: {self.sinopsis}")
        print(f"Director: {self.director}")
        print(f"Reparto: {', '.join(self.reparto)}")
        print(f"Valoración: {self.rate}")
        print()

    @classmethod
    def obtener_peliculas_desde_url(cls):
        # Método de clase para obtener información de películas desde Filmaffinity
        url = 'https://www.filmaffinity.com/es/rdcat.php?id=upc_th_es'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')  # Analiza el HTML de la página

        movie_cards = soup.find_all('div', class_='movie-card')  # Encuentra todas los carteles de película

        peliculas = []  # Lista para almacenar objetos Pelicula

        for movie_card in movie_cards:
            #coge la id de la peli
            data_movie_id = movie_card.get('data-movie-id')
            if data_movie_id:
                # como el url de la peli es siempre el mismo mas el id se mete
                movie_url = f"https://www.filmaffinity.com/es/film{data_movie_id}.html"
                response_movie = requests.get(movie_url)
                soup_movie = BeautifulSoup(response_movie.content, 'html.parser')
                rate_container = soup_movie.find('div', {'id': 'movie-rat-avg'})
                if rate_container:
                    rate = rate_container.text.strip()  # Obtener la valoración
                else:
                    rate = "No disponible"  # Manejo en caso de no encontrar la valoración

                # Con la nueva direccion nos metemos en la informacion de la pelicula
                movie_info = soup_movie.find('dl', class_='movie-info')
                if movie_info:
                    # Extrae información detallada de la película (título, fecha, géneros, sinopsis, etc.)
                    title = movie_info.find('dt', string='Título original').find_next('dd').text.strip()
                    year = movie_info.find('dt', string='Año').find_next('dd').text.strip()
                    release_date_day = soup_movie.find('div', id='movie-categories').strong.get_text(strip=True)
                    # Como la fecha aparece arriba a la derecha del cartel de dos formas distintas
                    if "/" in release_date_day:
                        # A esta no le añadimos el year de la pelcula ya que ya se puede sacar del formato en el que viene 13/10/2023
                        release_date = f"{release_date_day}"
                    else:
                        #Aqui si lo añadimos
                        release_date = f"{release_date_day} {year}"
                    #Convertimos la fecha segun el formato
                    release_date = convertir_fecha(release_date, year)
                    #Sacamos todos los generos
                    genres = [genre.text for genre in
                              movie_info.find('dt', string='Género').find_next('dd').find_all('a')]
                    synopsis = movie_info.find('dt', string='Sinopsis').find_next('dd').text.strip()
                    director = movie_info.find('dt', string='Dirección').find_next('dd').text.strip()
                    #Comprobamos si tiene actores y sacamos todos los que participan
                    reparto_block = movie_info.find('dt', string='Reparto')
                    if reparto_block:
                        actor_links = reparto_block.find_next('dd').find_all('a', title=True)
                        actor_names = [actor['title'] for actor in actor_links]
                    else:
                        actor_names = ["Información del reparto no encontrada"]
                    #Sacamos la imagen
                    movie_main_image = soup_movie.find('div', id='movie-main-image-container')
                    if movie_main_image:
                        image_url = movie_main_image.find('img')['src']
                        # Crea un objeto Pelicula con los datos recopilados y lo agrega a la lista de películas
                        nueva_pelicula = cls(title, release_date, image_url, genres, synopsis, director, actor_names,rate)
                        peliculas.append(nueva_pelicula)

        return peliculas  # Devuelve la lista de películas obtenidas

def convertir_fecha(release_date, year):
    # Función para convertir la fecha al formato datetime
    if "/" in release_date:
        # Si tiene barras
        formato = "%d/%m/%Y"
        fecha_datetime = datetime.strptime(release_date, formato)
    else:
        # Sin tiene un formato distinto como 28 de noviembre 2023
        partes_fecha = release_date.split()
        # Dividimos la cadena en 4 la posicon 1 como es el "de" no lo tenemos en cuenta
        dia = partes_fecha[0]
        mes = partes_fecha[2]
        # Traducimos el mes para que lo interprete %B que es el nombre del mes completo y segun la documentacion tiene que estar en ingles
        mes = traducir_mes(mes)
        release_date = f"{dia} de {mes} {year}"
        fecha_datetime = datetime.strptime(release_date, '%d de %B %Y')

    return fecha_datetime

def traducir_mes(mes):
    # Función para traducir nombres de meses de español a inglés para que %B lo reconozca
    equivalencias = {
        "enero": "January",
        "febrero": "February",
        "marzo": "March",
        "abril": "April",
        "mayo": "May",
        "junio": "June",
        "julio": "July",
        "agosto": "August",
        "septiembre": "September",
        "octubre": "October",
        "noviembre": "November",
        "diciembre": "December"
    }

    return equivalencias.get(mes.lower(), mes)



