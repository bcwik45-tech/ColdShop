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

# Serwer HTTP utrzymujący proces w stanie aktywnym na Railway
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ColdShop Bot is Online!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# ID serwera Discord do natychmiastowej synchronizacji
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
    async def legit_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voted_users:
            await interaction.response.send_message("❌ Oddałeś już swój głos w tym panelu!", ephemeral=True)
            return

        self.voted_users.add(interaction.user.id)
        self.positive_count += 1
        button.label = str(self.positive_count)
        
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("✅ Dziękujemy za potwierdzenie wiarygodności (Legit Check)!", ephemeral=True)

    @discord.ui.button(label="0", emoji="❌", style=discord.ButtonStyle.danger, custom_id="legit_no_btn")
    async def legit_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voted_users:
            await interaction.response.send_message("❌ Oddałeś już swój głos w tym panelu!", ephemeral=True)
            return

        self.voted_users.add(interaction.user.id)
        self.negative_count += 1
        button.label = str(self.negative_count)
        
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("Dziękujemy za oddanie głosu.", ephemeral=True)

# --- 3. SELEKTORY PRODUKTÓW ---

class BundleOnlySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Discord Account", description="Zobacz ofertę kont Discord.", emoji="💬"),
            discord.SelectOption(label="Steam Account", description="Zobacz ofertę kont Steam.", emoji="🎮"),
            discord.SelectOption(label="Rockstar Account", description="Zobacz ofertę kont Rockstar.", emoji="⭐")
        ]
        super().__init__(placeholder="❌ × Wybierz konto", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        embed = discord.Embed(
            title=f"{selected} 📦",
            description="» **Cena:** Do uzgodnienia w zgłoszeniu\n» **Zawartość:** Pełen dostęp, natychmiastowa realizacja.",
            color=discord.Color.blue()
        )
        embed.set_image(url=BUNDLE_IMAGE_URL)
        view = PurchaseView(product_name=selected, price_text="Kup teraz")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class VpnOnlySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="IP Vanish", description="Cena: €1 / 4.5zł (Year)", emoji="🛡️"),
            discord.SelectOption(label="NexHub", description="NexHub VPN", emoji="🌐")
        ]
        super().__init__(placeholder="❌ × Wybierz VPN", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        embed = discord.Embed(
            title=f"{selected} VPN 🛡️",
            description="» **Cena:** Atrakcyjna oferta\n» **Dostęp:** Pełny dostęp roczny.",
            color=discord.Color.blue()
        )
        embed.set_image(url=BANNER_URL)
        view = PurchaseView(product_name=selected, price_text="Kup teraz")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ShopOnlySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Citizen", description="Customowe postacie i modele FiveM", emoji="🌅"),
            discord.SelectOption(label="Soundpacks", description="Paczki dźwięków i audio", emoji="🔊")
        ]
        super().__init__(placeholder="❌ × Wybierz dodatek", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        embed = discord.Embed(
            title=f"{selected} 🎮",
            description=f"» **Produkt:** {selected}\n» Otwórz ticket, aby dokonać zakupu.",
            color=discord.Color.blue()
        )
        view = PurchaseView(product_name=selected, price_text="Sprawdź")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# --- 4. KOMENDY SETUPU & FEEDBACK ---

@bot.tree.command(name="feedback", description="Wysyła prośbę o wystawienie opinii po zakupie.")
@app_commands.checks.has_permissions(administrator=True)
async def feedback(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="⭐ COLDSHOP × FEEDBACK & OPINIE",
        description="Dziękujemy za zakupy w naszym sklepie!\nZostaw ocenę na naszym kanale **#・legit-check** / **#reviews**.",
        color=discord.Color.blue()
    )
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="COLDSHOP • Dziękujemy za zaufanie!")
    await interaction.channel.send(embed=embed)
    await interaction.followup.send("✅ Wiadomość feedback wysłana!", ephemeral=True)

@bot.tree.command(name="setup_legitchecks", description="Ustawia panel do oceniania i liczenia Legit Checków.")
@app_commands.checks.has_permissions(administrator=True)
async def