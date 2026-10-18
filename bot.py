import os
import random
import datetime
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Serwer HTTP dla Railway (sprawia że usługa ma status Online)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

MY_GUILD_ID = discord.Object(id=1561157589511839898)
DROP_CHANNEL_ID = 1561163117726011533

BANNER_URL = "http://googleusercontent.com/generated_animated_image/15959043500870823950"
BUNDLE_IMAGE_URL = "http://googleusercontent.com/generated_animated_image/15959043500870823950"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class ColdBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD_ID)
        await self.tree.sync(guild=MY_GUILD_ID)
        print("✅ Komendy Slash zostały zsynchronizowane!")

bot = ColdBot()

# --- 1. TICKET SYSTEM ---

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Ticket zostanie usunięty za 5 sekund...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class PurchaseSelect(discord.ui.Select):
    def __init__(self, product_name: str, price_text: str):
        self.product_name = product_name
        options = [
            discord.SelectOption(
                label=f"{product_name} - {price_text}",
                value="buy_now",
                description="Kliknij, aby otworzyć ticket zakupu",
                emoji="🛡️"
            )
        ]
        super().__init__(
            placeholder="❌ × Purchase Product | Zakup Produkt",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        user = interaction.user
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel_name = f"ticket-{user.name.lower()}"
        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        
        ticket_embed = discord.Embed(
            title=f"❄️ COLDSHOP — Ticket: {self.product_name}",
            description=f"Witaj {user.mention}!\nOtworzyłeś ticket zakupowy dla **{self.product_name}**.\nZaraz dołączy do Ciebie ktoś z administracji.\n\nAby zamknąć zgłoszenie, kliknij poniższy przycisk:",
            color=discord.Color.blue()
        )
        if guild.icon:
            ticket_embed.set_thumbnail(url=guild.icon.url)
        
        await ticket_channel.send(content=f"{user.mention}", embed=ticket_embed, view=CloseTicketView())
        await interaction.followup.send(f"✅ Stworzono Twój ticket: {ticket_channel.mention}", ephemeral=True)

class PurchaseView(discord.ui.View):
    def __init__(self, product_name: str, price_text: str):
        super().__init__(timeout=None)
        self.add_item(PurchaseSelect(product_name, price_text))

# --- 2. LEGIT CHECK SYSTEM ---

class LegitCheckView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.positive_count = 0
        self.negative_count = 0
        self.voted_users = set()

    @discord.ui.button(label="0", emoji="✅", style=discord.ButtonStyle.success, custom_id="legit_yes_btn")
    async def