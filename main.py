import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

class SorteosModal(discord.ui.Modal, title="Crear Sorteo"):
    nombre = discord.ui.TextInput(label="Nombre del sorteo", placeholder="Ej: PlayStation 5")
    descripcion = discord.ui.TextInput(label="Descripción", style=discord.TextStyle.long)
    premio = discord.ui.TextInput(label="Premio", placeholder="Ej: $500")
    
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"🎁 {self.nombre.value}",
            description=self.descripcion.value,
            color=discord.Color.gold()
        )
        embed.add_field(name="Premio", value=self.premio.value, inline=False)
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
