
from bs4 import BeautifulSoup
from Pelicula import Pelicula
import requests
import os
import shutil
import json
# Definimos el directorio donde se almacenarán las imágenes
directorio_imagenes = 'imagenes_peliculas'
# Esta función guarda la información de las películas en un archivo JSON y descargara las imágenes.
def guardar_peliculas_en_json(peliculas, directorio_imagenes='imagenes_peliculas'):
    # Comprobamos si el directorio de las imágenes ya existe, si no, lo creamos
    if not os.path.exists(directorio_imagenes):
        os.makedirs(directorio_imagenes)

    # Si ya existe el archivo 'datospeliculas.json', lo eliminamos
    if os.path.exists('datospeliculas.json'):
        os.remove('datospeliculas.json')

    # Creamos un diccionario extra para almacenar todos los diccionarios de películas
    diccionario_general = {"resultados": []}

    # Abrimos el archivo JSON para escritura y guardamos la información de las películas
    with open('datospeliculas.json', 'w') as archivo:
        for peli in peliculas:
            # Creamos un diccionario con la información de cada película
            peli_dict = {
                "Título": peli.titulo,
                "Fecha de lanzamiento": peli.fecha_lanzamiento.strftime('%Y-%m-%d'),
                "Imagen": peli.imagen,
                "Géneros": peli.generos,
                "Sinopsis": peli.sinopsis,
                "Director": peli.director,
                "Reparto": peli.reparto,
                "Valoracion": peli.rate
            }

            # Agregamos cada película a la lista del diccionario extra
            diccionario_general["peliculas"].append(peli_dict)

            # Descargamos y guardamos la imagen en el directorio de imágenes
            imagen_local = f"{directorio_imagenes}/{peli.titulo.replace(' ', '_')}.jpg"
            with open(imagen_local, 'wb') as img_file:
                img_file.write(requests.get(peli.imagen).content)  # Descargamos y escribimos la imagen
                print(f"Imagen descargada: {imagen_local}")  # Imprimimos la ruta de la imagen descargada

        # Escribimos el diccionario extra en el archivo JSON
        json.dump(diccionario_general, archivo)

# Esta función elimina el directorio de imágenes si existe

def limpiar_directorio():
    if os.path.exists(directorio_imagenes):
        shutil.rmtree(directorio_imagenes)

# Función principal
def main():
    TOKEN = os.environ.get('DISCORD_TOKEN')
    limpiar_directorio()  # Limpiamos el directorio de imágenes antes de descargar las nuevas películas para que no se repitan
    peliculas = Pelicula.obtener_peliculas_desde_url()  # Obtenemos las películas desde una URL
    YOUR_CHANNEL_ID = '845032532814987295'

    while True:
        print("------ MENÚ ------")
        print("1. Mostrar películas ordenadas por fecha de lanzamiento (más reciente a más antigua)")
        print("2. Mostrar películas ordenadas por puntuacion")
        print("3. Mostrar películas ordenadas por genero")
        print("4. Mostrar mejores películas del año ordenadas por puntuacion")
        print("5. Salir")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            # Ordenamos las películas por fecha de lanzamiento (de más reciente a más antigua) y las imprimimos
            peliculas_ordenadas = sorted(peliculas, key=lambda x: x.fecha_lanzamiento, reverse=True)
            for peli in peliculas_ordenadas:
                peli.imprimir_info()
        elif opcion == "2":
            # Crear un diccionario para almacenar las películas por día
            peliculas_por_dia = {}

            for peli in peliculas:
                fecha_peli = peli.fecha_lanzamiento.strftime('%Y-%m-%d')
                # Si el día ya está en el diccionario, agregamos la película a la lista correspondiente
                if fecha_peli in peliculas_por_dia:
                    peliculas_por_dia[fecha_peli].append((peli.titulo, peli.rate))
                # Si no existe el día, creamos una nueva lista con la película
                else:
                    peliculas_por_dia[fecha_peli] = [(peli.titulo, peli.rate)]

            # Ordenar las películas por su puntuación (rate) de mayor a menor en cada día
            for fecha, peliculas in peliculas_por_dia.items():
                # Ordenar las películas por su puntuación (rate) de mayor a menor
                peliculas_por_dia[fecha] = sorted(peliculas, key=lambda x: x[1], reverse=True)

            # Mostrar la información organizada por día, con películas ordenadas por su puntuación
            for fecha, peliculas in peliculas_por_dia.items():
                print(f"Fecha: {fecha}")
                for peli_info in peliculas:
                    print(f"Película: {peli_info[0]}, Puntuación: {peli_info[1]}")
        elif opcion == "3":
            # Creamos un diccionario para almacenar las películas por género
            peliculas_por_genero = {}

            # Iteramos a través de todas las películas
            for peli in peliculas:
                # Comprobamos si hay géneros para la película
                if peli.generos:
                    # Tomamos solo el primer género de la lista (puedes cambiar esta lógica si lo deseas)
                    primer_genero = peli.generos[0]

                    # Si el género ya está en el diccionario, agregamos la película a la lista correspondiente
                    if primer_genero in peliculas_por_genero:
                        peliculas_por_genero[primer_genero].append(peli.titulo)
                    # Si el género no está en el diccionario, creamos una nueva lista con el título de la película
                    else:
                        peliculas_por_genero[primer_genero] = [peli.titulo]

            # Mostramos los títulos de las películas organizadas por género
            for genero, titulos in peliculas_por_genero.items():
                print(f"--- Películas de género {genero} ---")
                for titulo in titulos:
                    print(titulo)
        elif opcion == "4":
            i=0
            x=0
            url = 'https://www.filmaffinity.com/es/ranking.php?rn=ranking_2023_topmovies'
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            movie_cards = soup.find_all('ul', id='top-movies')

            for card in movie_cards:
                div_titles = card.find_all('div', class_='mc-title')
                ratings = card.find_all('div', class_='avg-rating')

                for divtitle in div_titles:
                    title = divtitle.find('a')
                    titles = title.text.strip()
                    print(f'Título: {titles}')
                    for rate in ratings:
                        if x==i:
                            print(f'Rating: {rate.text.strip()}')
                            print("--------------")
                            i=i+1
                            x = 0
                            break
                        else:
                             x=x+1

        elif opcion == "5":
            print("Saliendo del programa...")
            guardar_peliculas_en_json(peliculas)  # Guardamos la información de las películas en un archivo JSON
            break  # Finaliza el bucle o la ejecución del programa


#  ejecutamos el main

main()
#845032532814987295