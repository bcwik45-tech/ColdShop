import os
import random
import datetime
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Mikro-serwer HTTP tylko po to, żeby Railway widział ruch i trzymał status "Online"
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ColdShop Bot is Online!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Uruchomienie serwera WWW w tle
threading.Thread(target=run_web_server, daemon=True).start()

# ID Twojego serwera Discord
MY_GUILD_ID = discord.Object(id=1561157589511839898)
DROP_CHANNEL_ID = 1561163117726011533

BANNER_URL = "http://googleusercontent.com/generated_animated_image/15959043500870823950"
BUNDLE_IMAGE_URL = "http://googleusercontent.com/generated_animated_image/15959043500870823950"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class ColdBot(discord.ext.commands.Bot):
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
async def setup_legitchecks(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="⭐ COLDSHOP × LEGIT CHECK PANEL",
        description="Kliknij poniższy przycisk **✅**, aby potwierdzić udaną transakcję i naszą wiarygodność!",
        color=discord.Color.blue()
    )
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="COLDSHOP • Rejestr Ocen")
    
    view = LegitCheckView()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.followup.send("✅ Panel Legit Check stworzony!", ephemeral=True)

@bot.tree.command(name="setup_bundle", description="Ustawia panel z paczkami i kontami.")
@app_commands.checks.has_permissions(administrator=True)
async def setup_bundle(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="⭐ COLDSHOP × FIVEM & ACCOUNTS",
        description="Accounts **available** from us:",
        color=discord.Color.blue()
    )
    embed.add_field(name="Dostępne:", value="• 💬 × **Discord Account**\n• 🎮 × **Steam Account**\n• ⭐ × **Rockstar Account**", inline=False)
    embed.set_image(url=BUNDLE_IMAGE_URL)
    embed.set_footer(text="COLDSHOP • FiveM & Bundles")
    
    view = discord.ui.View(timeout=None)
    view.add_item(BundleOnlySelect())
    
    await interaction.channel.send(embed=embed, view=view)
    await interaction.followup.send("✅ Panel Bundle wysłany!", ephemeral=True)

@bot.tree.command(name="setup_vpn", description="Ustawia panel VPN.")
@app_commands.checks.has_permissions(administrator=True)
async def setup_vpn(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="🛡️ COLDSHOP × VPN SERVICES",
        description="Wybierz sprawdzony VPN z listy poniżej:",
        color=discord.Color.blue()
    )
    embed.add_field(name="Dostępne:", value="• 🛡️ × **IP Vanish**\n• 🌐 × **NexHub**", inline=False)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="COLDSHOP • VPN")
    
    view = discord.ui.View(timeout=None)
    view.add_item(VpnOnlySelect())
    
    await interaction.channel.send(embed=embed, view=view)
    await interaction.followup.send("✅ Panel VPN wysłany!", ephemeral=True)

@bot.tree.command(name="setup_shop", description="Ustawia sklep (Citizen i Soundpacks).")
@app_commands.checks.has_permissions(administrator=True)
async def setup_shop(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="🛒 COLDSHOP × ADDONS & MODS",
        description="Wybierz interesującą Cię kategorię dodatków do gry:",
        color=discord.Color.blue()
    )
    embed.add_field(name="Oferta:", value="• 🌅 × **Citizen** (Customowe postacie)\n• 🔊 × **Soundpacks** (Paczki dźwięków)", inline=False)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="COLDSHOP • Sklep")
    
    view = discord.ui.View(timeout=None)
    view.add_item(ShopOnlySelect())
    
    await interaction.channel.send(embed=embed, view=view)
    await interaction.followup.send("✅ Panel Shop wysłany!", ephemeral=True)

@bot.tree.command(name="setup_custombot", description="Ustawia panel zamówień na niestandardowe boty.")
@app_commands.checks.has_permissions(administrator=True)
async def setup_custombot(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="⚙️ CUSTOM DISCORD BOTS / BOTY NA ZAMÓWIENIE",
        description=(
            "**ENG**\n"
            "Custom Discord Bots — Python/JS\n"
            "Moderation • tickets • API integrations • any commands you want\n"
            "Clean code, fast delivery, optional 24/7 hosting.\n"
            "Price depends on complexity — ⁠・tickets ---> SHOP .\n\n"
            "--------------------------------------------------\n\n"
            "**PL**\n"
            "Customowe Boty Discord — Python/JS\n"
            "Moderacja • tickety • integracje API • dowolne komendy\n"
            "Czysty kod, szybka realizacja, również opcjonalny hosting 24/7.\n"
            "Cena zależy od trudności — otwórz ticket!"
        ),
        color=discord.Color.blue()
    )
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="COLDSHOP • Custom Bots")
    
    view = PurchaseView(product_name="Custom Bot Discord", price_text="Wycena indywidualna")
    await interaction.channel.send(embed=embed, view=view)
    await interaction.followup.send("✅ Panel Custom Bot wysłany!", ephemeral=True)

# --- 5. KOMENDY INNE (/SAY, /BANDC, /UNBANDC, /DROP) ---

@bot.tree.command(name="say", description="Wysyła ramkę ogłoszeniową.")
@app_commands.checks.has_permissions(administrator=True)
async def say(interaction: discord.Interaction, message: str, title: str = None, footer: str = "Bot • Ad made by px7.nj"):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(title=title if title else "", description=message, color=discord.Color.dark_grey())
    if footer:
        embed.set_footer(text=footer)
    await interaction.channel.send(embed=embed)
    await interaction.followup.send("✅ Wiadomość wysłana!", ephemeral=True)

@bot.tree.command(name="bandc", description="Banuje użytkownika.")
@app_commands.checks.has_permissions(ban_members=True)
async def bandc(interaction: discord.Interaction, user: discord.User, reason: str = "Brak powodu"):
    await interaction.response.defer()
    try:
        await interaction.guild.ban(user, reason=reason)
    except Exception as e:
        await interaction.followup.send(f"❌ Błąd: {e}", ephemeral=True)
        return

    embed = discord.Embed(title="🔨 User has been banned for life", color=discord.Color.red())
    embed.add_field(name="👤 User", value=user.mention, inline=True)
    embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=True)
    embed.add_field(name="🛡️ Administrator", value=interaction.user.mention, inline=False)
    embed.add_field(name="📝 Reason", value=f"```\n{reason}\n```", inline=False)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=f"COLDSHOP Security • {discord.utils.utcnow().strftime('%H:%M')}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="unbandc", description="Odbanowuje użytkownika.")
@app_commands.checks.has_permissions(ban_members=True)
async def unbandc(interaction: discord.Interaction, user_id: str, reason: str = "Odbanowanie"):
    await interaction.response.defer()
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user, reason=reason)
    except Exception as e:
        await interaction.followup.send(f"❌ Błąd: {e}", ephemeral=True)
        return

    embed = discord.Embed(title="🔓 User has been unbanned", color=discord.Color.green())
    embed.add_field(name="👤 User", value=f"{user.name} ({user.mention})", inline=True)
    embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=True)
    embed.set_footer(text=f"COLDSHOP Security • {discord.utils.utcnow().strftime('%H:%M')}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="drop", description="Minigra ze zniżką 20%!")
async def drop(interaction: discord.Interaction):
    if interaction.channel_id != DROP_CHANNEL_ID:
        await interaction.response.send_message(f"❌ Tylko na kanale <#{DROP_CHANNEL_ID}>!", ephemeral=True)
        return

    win = random.randint(1, 100) <= 5
    if win:
        embed = discord.Embed(
            title="🎉 GRATULACJE! WYGRAŁEŚ ZNIŻKĘ!",
            description=f"🔥 {interaction.user.mention} trafił **5% szans** i wylosował **ZNIŻKĘ -20%** w **COLDSHOP**!",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="❄️ COLDSHOP DROP — BRAK TRAFIENIA",
            description=f"Niestety {interaction.user.mention}, spróbuj ponownie później.",
            color=discord.Color.dark_gray()
        )
        await interaction.response.send_message(embed=embed)

# --- 6. URUCHOMIENIE BOTA ---

async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())