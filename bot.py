import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Crear el bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} ha iniciado sesión')
    try:
        synced = await bot.tree.sync()
        print(f"Se sincronizaron {len(synced)} comandos")
    except Exception as e:
        print(e)

@bot.tree.command(name="invitacion", description="Envía una invitación a todos los miembros del servidor")
async def invitacion(interaction: discord.Interaction):
    """
    Comando slash para enviar invitaciones a todos los miembros del servidor
    """
    # Verificar que el usuario tiene permisos de administrador
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Solo los administradores pueden usar este comando",
            ephemeral=True
        )
        return
    
    # Responder inmediatamente para que no expire
    await interaction.response.send_message(
        f"📨 Enviando invitaciones a todos los miembros...",
        ephemeral=False
    )
    
    # Obtener todos los miembros del servidor
    guild = interaction.guild
    members = guild.members
    
    enviados = 0
    fallidos = 0
    
    # Mensaje con invitación
    mensaje = "⚽️ Unete a la liga futbote y disfruta de tus goles\n\nhttps://discord.gg/wxnCTt2dMg"
    
    # Enviar DM a cada miembro
    for member in members:
        # No enviar al bot mismo
        if member.bot:
            continue
        
        try:
            await member.send(mensaje)
            enviados += 1
            
            # Pequeña pausa para no spamear
            await asyncio.sleep(0.5)
            
        except discord.Forbidden:
            fallidos += 1
            print(f"No se pudo enviar DM a {member}")
        except Exception as e:
            fallidos += 1
            print(f"Error enviando DM a {member}: {e}")
    
    # Mensaje final
    mensaje_final = (
        f"✅ **Proceso completado**\n"
        f"📨 Enviados: {enviados}\n"
        f"❌ Fallidos: {fallidos}"
    )
    
    # Editar el mensaje inicial con los resultados
    await interaction.edit_original_response(content=mensaje_final)

# Comando de prueba
@bot.tree.command(name="ping", description="Comprueba si el bot está en línea")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! {round(bot.latency * 1000)}ms")

# Obtener token de la variable de entorno
token = os.getenv('MTUzMDYyNzY1ODAwMDQ5ODg1MA.Gqx_0o.ggVinskBAj1nRSEHptGjHBQcx5bdoG2JpC_QNE')

if not token:MTUzMDYyNzY1ODAwMDQ5ODg1MA.Gqx_0o.ggVinskBAj1nRSEHptGjHBQcx5bdoG2JpC_QNE
    print("❌ Error: No se encontró DISCORD_TOKEN")
    exit(1)
else:
    bot.run(MTUzMDYyNzY1ODAwMDQ5ODg1MA.Gqx_0o.ggVinskBAj1nRSEHptGjHBQcx5bdoG2JpC_QNE)
