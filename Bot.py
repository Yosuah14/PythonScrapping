import os
import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from Pelicula import Pelicula  # Asegúrate de importar correctamente tu clase Pelicula

async def mostrar_peliculas(ctx):
    try:
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
    except Exception as e:
        print(f"Error al mostrar películas: {e}")

async def enviar_mensaje_discord():
    try:
        from dotenv import load_dotenv
        load_dotenv()
        TOKEN = os.getenv('DISCORD_TOKEN')
        CODE_CHANNEL_ID = 1172568042916565014

        if TOKEN:
            intents = discord.Intents.default()
            intents.messages = True  # Activa la intención de mensajes

            # Crear una instancia del bot de Discord
            bot = commands.Bot(command_prefix='!', intents=intents)

            @bot.event
            async def on_ready():
                print(f'Logged in as {bot.user.name}')

                # Obtener el canal de Discord por ID
                canal = bot.get_channel(CODE_CHANNEL_ID)
                if canal:
                    print(f"Encontrado el canal con ID {CODE_CHANNEL_ID}")

                    # Enviar el mensaje en el canal especificado
                    await mostrar_peliculas(canal)

                    # Agregar una pequeña espera antes de cerrar la conexión
                    await asyncio.sleep(5)

                    # Cerrar la conexión del bot
                    await bot.close()
                else:
                    print(f"No se encontró el canal con ID {CODE_CHANNEL_ID}.")
            # Iniciar el bot con el token
            await bot.start(TOKEN)
        else:
            print("No se encontró el token en las variables de entorno. Por favor, verifica la configuración del token.")
    except Exception as e:
        print(f"Error al enviar mensaje a Discord: {e}")

# Llama a la función asíncrona para enviar el mensaje
async def ejecutar_programa():
    await enviar_mensaje_discord()

if __name__ == "__main__":
    asyncio.run(ejecutar_programa())