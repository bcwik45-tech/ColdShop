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

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), HealthCheckHandler).serve_forever()

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
        print("✅ Komendy Slash zostały w pełni zsynchronizowane!")

bot = ColdBot()

# --- SYSTEM TICKETÓW ---
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
        options = [discord.SelectOption(label=f"{product_name} - {price_text}", value="buy_now", description="Kliknij, aby otworzyć ticket zakupu", emoji="🛡️")]
        super().__init__(placeholder="❌ × Purchase Product | Zakup Produkt", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        user = interaction.user
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ticket_channel = await guild.create_text_channel(name=f"ticket-{user.name.lower()}", overwrites=overwrites)
        embed = discord.Embed(title=f"❄️ COLDSHOP — Ticket: {self.product_name}", description=f"Witaj {user.mention}!\nOtworzyłeś ticket zakupowy dla **{self.product_name}**.", color=discord.Color.blue())
        await ticket_channel.send(content=f"{user.mention}", embed=embed, view=CloseTicketView())
        await interaction.followup.send(f"✅ Stworzono ticket: {ticket_channel.mention}", ephemeral=True)

class PurchaseView(discord.ui.View):
    def __init__(self, product_name: str, price_text: str):
        super().__init__(timeout=None)
        self.add_item(PurchaseSelect(product_name, price_text))

# --- LEGIT CHECK SYSTEM ---
class LegitCheckView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.yes_count = 0
        self.no_count = 0

    @discord.ui.button(label="0", emoji="✅", style=discord.ButtonStyle.success, custom_id="legit_yes_btn")
    async def legit_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.yes_count += 1
        button.label = str(self.yes_count)
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("✅ Dziękujemy za pozytywny głos!", ephemeral=True)

    @discord.ui.button(label="0", emoji="❌", style=discord.ButtonStyle.danger, custom_id="legit_no_btn")
    async def legit_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.no_count += 1
        button.label = str(self.no_count)
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("Dziękujemy za oddanie głosu.", ephemeral=True)

# --- SELEKTORY ---
class BundleOnlySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Discord Account", description="Konto Discord", emoji="💬"),
            discord.SelectOption(label="Steam Account", description="Konto Steam", emoji="🎮"),
            discord.SelectOption(label="Rockstar Account", description="Konto Rockstar", emoji="⭐")
        ]
        super().__init__(placeholder="❌ × Wybierz konto", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        embed = discord.Embed(title=f"{selected} 📦", description="Pełen dostęp, natychmiastowa realizacja.", color=discord.Color.blue())
        embed.set_image(url=BUNDLE_IMAGE_URL)
        await interaction.response.send_message(embed=embed, view=PurchaseView(product_name=selected, price_text="Kup teraz"), ephemeral=True)

class VpnOnlySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="IP Vanish", description="Cena: €1 / 4.5zł (Year)", emoji="🛡️"),
            discord.SelectOption(label="NexHub", description="NexHub VPN", emoji="🌐")
        ]
        super().__init__(placeholder="❌ × Wybierz VPN", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        embed = discord.Embed(title=f"{selected} VPN 🛡️", description="Pełny dostęp roczny.", color=discord.Color.blue())
        embed.set_image(url=BANNER_URL)
        await interaction.response.send_message(embed=embed, view=PurchaseView(product_name=selected, price_text="Kup teraz"), ephemeral=True)

class ShopOnlySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Citizen", description="Customowe postacie FiveM", emoji="🌅"),
            discord.SelectOption(label="Soundpacks", description="Paczki dźwięków", emoji="🔊")
        ]
        super().__init__(placeholder="❌ × Wybierz dodatek", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        embed = discord.Embed(title=f"{selected} 🎮", description="Otwórz ticket, aby dokonać zakupu.", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, view=PurchaseView(product_name=selected, price_text="Sprawdź"), ephemeral=True)

# --- KOMENDY SETUPU ---
@bot.tree.command(name="feedback", description="Wysyła prośbę o opinię.")
@app_commands.checks.has_permissions(administrator=True)
async