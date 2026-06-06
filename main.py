import discord
from discord.ext import commands
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

panel_sent = False

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

MADRID_TZ = ZoneInfo("Europe/Madrid")

class SorteosModal(discord.ui.Modal, title="Crear Sorteo"):
    nombre = discord.ui.TextInput(label="Nombre del sorteo", placeholder="Ej: PlayStation 5")
    descripcion = discord.ui.TextInput(label="Descripción", style=discord.TextStyle.long)
    premio = discord.ui.TextInput(label="Premio", placeholder="Ej: $500")
    duracion = discord.ui.TextInput(
        label="Duración (en segundos)",
        placeholder="Ej: 86400 (= 24 horas)",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            segundos = int(self.duracion.value)
            if segundos <= 0:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "❌ La duración debe ser un número entero positivo de segundos.",
                ephemeral=True,
            )
            return

        ahora = datetime.now(tz=MADRID_TZ)
        fin = ahora + timedelta(seconds=segundos)
        fin_str = fin.strftime("%d/%m/%Y %H:%M:%S (hora España)")

        embed = discord.Embed(
            title=f"🎁 {self.nombre.value}",
            description=self.descripcion.value,
            color=discord.Color.gold()
        )
        embed.add_field(name="Premio", value=self.premio.value, inline=False)
        embed.add_field(name="⏰ Finaliza el", value=fin_str, inline=False)
        embed.set_footer(text=f"Creado por {interaction.user}")

        await interaction.response.send_message(f"@everyone\n\n{embed.title}", embed=embed)

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
