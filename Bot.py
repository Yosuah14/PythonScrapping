import os
import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from Pelicula import Pelicula  # Asegúrate de importar correctamente tu clase Pelicula

async def mostrar_peliculas(ctx):
    # Lógica para mostrar películas
    peliculas = Pelicula.obtener_peliculas_desde_url_python()
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    peliculas_hoy = [peli for peli in peliculas if peli.fecha_lanzamiento.strftime('%Y-%m-%d') == fecha_actual]

    if peliculas_hoy:
        peliculas_ordenadas = sorted(peliculas_hoy, key=lambda x: x.rate, reverse=True)
        mensaje_peliculas = f"Películas lanzadas hoy ({fecha_actual}) ordenadas por puntuación:\n"
        for peli in peliculas_ordenadas:
            mensaje_peliculas += f"**{peli.titulo}** - Puntuación: {peli.rate}\n"
    else:
        mensaje_peliculas = f"No hay películas lanzadas hoy ({fecha_actual})."

    # Enviar el mensaje
    await ctx.send(mensaje_peliculas)

async def enviar_mensaje_discord():
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    code_channel = 845032532814987295

    if TOKEN:
        intents = discord.Intents.default()
        # Crear una instancia del bot de Discord
        bot = commands.Bot(command_prefix='!', intents=intents)
        # Configurar el comando !peliculas para que llame a la función mostrar_peliculas
        bot.add_command(commands.Command(mostrar_peliculas, name='peliculas'))
        # Iniciar el bot
        await bot.start(TOKEN)
        # Esperar a que el bot esté listo antes de enviar el mensaje
        await bot.wait_until_ready()
        # Obtener el canal de Discord por ID
        canal = bot.get_channel(code_channel)
        if canal:
            # Enviar el mensaje en el canal especificado
            await mostrar_peliculas(canal)
        else:
            print(f"No se encontró el canal con ID {code_channel}.")
        # Cerrar la conexión del bot
        await bot.close()
    else:
        print("No se encontró el token en las variables de entorno. Por favor, verifica la configuración del token.")

# Llama a la función asíncrona para enviar el mensaje
async def ejecutar_programa():
    await enviar_mensaje_discord()

if __name__ == "__main__":
    asyncio.run(ejecutar_programa())