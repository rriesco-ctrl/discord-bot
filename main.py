import discord
from discord.ext import commands
import os
import asyncio
import random
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
GIVEAWAY_DURATION = int(os.getenv("GIVEAWAY_DURATION", 86400))  # segundos, default 24h

panel_sent = False

# { message_id: set(user_ids) }
sorteo_participantes: dict[int, set[int]] = {}

@bot.event
async def on_ready():
    global panel_sent
    if panel_sent:
        return
    
    print(f"Bot conectado como {bot.user}")
    
    guild = bot.get_guild(DISCORD_GUILD_ID)
    if not guild:
        print(f"No se encontró el servidor {DISCORD_GUILD_ID}")
        return
    
    # Obtener el primer canal de texto
    text_channel = None
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            text_channel = channel
            break
    
    if not text_channel:
        print("No hay canales de texto disponibles")
        return
    
    # Crear el embed del panel
    embed = discord.Embed(
        title="📋 Panel de Sorteos y Ventas",
        description="Selecciona una opción:",
        color=discord.Color.blue()
    )
    
    # Crear los botones
    view = discord.ui.View(timeout=None)
    
    async def sorteos_callback(interaction: discord.Interaction):
        modal = SorteosModal()
        await interaction.response.send_modal(modal)
    
    async def vender_callback(interaction: discord.Interaction):
        modal = VenderModal()
        await interaction.response.send_modal(modal)
    
    btn_sorteos = discord.ui.Button(label="🎁 Sorteos", style=discord.ButtonStyle.green)
    btn_sorteos.callback = sorteos_callback
    
    btn_vender = discord.ui.Button(label="💰 Vender", style=discord.ButtonStyle.blurple)
    btn_vender.callback = vender_callback
    
    view.add_item(btn_sorteos)
    view.add_item(btn_vender)
    
    await text_channel.send(embed=embed, view=view)
    panel_sent = True
    print(f"Panel enviado en {text_channel.name}")

class ParticiparView(discord.ui.View):
    """View persistente con el botón Participar para un sorteo activo."""

    def __init__(self, message_id: int):
        super().__init__(timeout=None)
        self.message_id = message_id

    @discord.ui.button(label="🎟️ Participar", style=discord.ButtonStyle.green, custom_id="participar")
    async def participar(self, interaction: discord.Interaction, button: discord.ui.Button):
        participantes = sorteo_participantes.get(self.message_id)

        if participantes is None:
            # El sorteo ya finalizó
            await interaction.response.send_message(
                "⏰ Este sorteo ya ha finalizado.", ephemeral=True
            )
            return

        if interaction.user.id in participantes:
            await interaction.response.send_message(
                "✅ Ya estás participando en este sorteo.", ephemeral=True
            )
            return

        participantes.add(interaction.user.id)
        total = len(participantes)
        await interaction.response.send_message(
            f"🎟️ ¡Te has registrado! Ahora hay **{total}** participante{'s' if total != 1 else ''}.",
            ephemeral=True,
        )


async def finalizar_sorteo(
    message: discord.Message,
    nombre: str,
    premio: str,
    duracion: int,
):
    """Espera `duracion` segundos y luego elige un ganador al azar."""
    await asyncio.sleep(duracion)

    participantes = sorteo_participantes.pop(message.id, None)

    # Deshabilitar el botón en el mensaje original
    view_cerrada = discord.ui.View()
    btn_cerrado = discord.ui.Button(
        label="🔒 Sorteo finalizado", style=discord.ButtonStyle.grey, disabled=True
    )
    view_cerrada.add_item(btn_cerrado)

    try:
        await message.edit(view=view_cerrada)
    except discord.HTTPException:
        pass

    if not participantes:
        await message.channel.send(
            f"😔 El sorteo **{nombre}** ha finalizado pero **nadie participó**. "
            "No hay ganador esta vez."
        )
        return

    ganador_id = random.choice(list(participantes))
    ganador = message.guild.get_member(ganador_id)
    mencion = ganador.mention if ganador else f"<@{ganador_id}>"

    embed_ganador = discord.Embed(
        title="🏆 ¡Tenemos un ganador!",
        description=f"El sorteo **{nombre}** ha finalizado.",
        color=discord.Color.gold(),
    )
    embed_ganador.add_field(name="🎁 Premio", value=premio, inline=False)
    embed_ganador.add_field(name="🥇 Ganador", value=mencion, inline=False)
    embed_ganador.add_field(
        name="👥 Participantes totales", value=str(len(participantes)), inline=False
    )
    embed_ganador.set_footer(text="¡Felicitaciones!")

    await message.channel.send(
        f"@everyone 🎉 {mencion} ¡ganaste el sorteo!", embed=embed_ganador
    )


class SorteosModal(discord.ui.Modal, title="Crear Sorteo"):
    nombre = discord.ui.TextInput(label="Nombre del sorteo", placeholder="Ej: PlayStation 5")
    descripcion = discord.ui.TextInput(label="Descripción", style=discord.TextStyle.long)
    premio = discord.ui.TextInput(label="Premio", placeholder="Ej: $500")
    duracion_horas = discord.ui.TextInput(
        label="Duración (horas)",
        placeholder="Ej: 24  — deja vacío para usar el valor por defecto",
        required=False,
        max_length=4,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Resolver duración: campo del modal → variable de entorno → 24 h
        try:
            duracion = int(self.duracion_horas.value.strip()) * 3600
        except (ValueError, AttributeError):
            duracion = GIVEAWAY_DURATION

        horas = duracion // 3600
        fin = datetime.utcnow() + timedelta(seconds=duracion)
        timestamp = discord.utils.format_dt(fin, style="R")  # "en X horas"

        embed = discord.Embed(
            title=f"🎁 {self.nombre.value}",
            description=self.descripcion.value,
            color=discord.Color.gold(),
        )
        embed.add_field(name="🏆 Premio", value=self.premio.value, inline=False)
        embed.add_field(name="⏰ Finaliza", value=timestamp, inline=False)
        embed.add_field(name="👥 Participantes", value="0", inline=False)
        embed.set_footer(text=f"Creado por {interaction.user} • Duración: {horas}h")

        # Respuesta diferida para poder obtener el mensaje enviado
        await interaction.response.defer()
        msg = await interaction.followup.send(
            "@everyone", embed=embed, wait=True
        )

        # Registrar el sorteo y adjuntar el botón
        sorteo_participantes[msg.id] = set()
        view = ParticiparView(msg.id)
        await msg.edit(view=view)

        # Lanzar el temporizador en background
        asyncio.create_task(
            finalizar_sorteo(msg, self.nombre.value, self.premio.value, duracion)
        )

class VenderModal(discord.ui.Modal, title="Crear Venta"):
    producto = discord.ui.TextInput(label="Producto", placeholder="Ej: iPhone 15")
    precio = discord.ui.TextInput(label="Precio", placeholder="Ej: $800")
    descripcion = discord.ui.TextInput(label="Descripción", style=discord.TextStyle.long)
    
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"💰 {self.producto.value}",
            description=self.descripcion.value,
            color=discord.Color.green()
        )
        embed.add_field(name="Precio", value=self.precio.value, inline=False)
        embed.set_footer(text=f"Vendedor: {interaction.user}")
        
        await interaction.response.send_message(f"@everyone\n\n{embed.title}", embed=embed)

bot.run(DISCORD_TOKEN)
