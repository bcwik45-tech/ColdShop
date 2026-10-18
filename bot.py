import os
import random
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ID dozwolonego kanału dla komendy /drop
DROP_CHANNEL_ID = 1561163117726011533

# Link do baneru COLDSHOP do użycia w banach / embedach
BANNER_URL = "http://googleusercontent.com/generated_animated_image/15959043500870823950"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class ColdBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Komendy Slash zostały zsynchronizowane!")

bot = ColdBot()

# --- 1. SYSTEM TICKETÓW & ZAKUPÓW ---

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
            description=f"Witaj {user.mention}!\nOtworzyłeś ticket zakupowy dla **{self.product_name}**.\nZaraz dołączy do Ciebie ktoś z administracji.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(content=f"{user.mention}", embed=ticket_embed)
        
        await interaction.response.send_message(
            f"✅ Stworzono Twój ticket: {ticket_channel.mention}", ephemeral=True
        )

class PurchaseView(discord.ui.View):
    def __init__(self, product_name: str, price_text: str):
        super().__init__(timeout=None)
        self.add_item(PurchaseSelect(product_name, price_text))


# --- 2. DEDYKOWANE PANELE SELEKCJI (BUNDLES / VPN) ---

class BundleOnlySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="FiveM Ready Bundle", description="Zobacz ofertę paczki FiveM.", emoji="⭐"),
            discord.SelectOption(label="CS2 Prime + Steam Bundle", description="Zobacz ofertę konta CS2 z grą.", emoji="🎮"),
            discord.SelectOption(label="Ultimate Gamer Bundle", description="Pełen pakiet kont i dodatków.", emoji="📦"),
        ]
        super().__init__(
            placeholder="❌ × Click to select | Kliknij aby wybrać",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        embed = discord.Embed(
            title=f"{selected} 📦",
            description=f"» **Cena:** Do uzgodnienia w zgłoszeniu\n» **Zawartość:** Pełen dostęp, natychmiastowa realizacja.",
            color=discord.Color.from_rgb(0, 162, 232)
        )
        view = PurchaseView(product_name=selected, price_text="Kup teraz")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class VpnOnlySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="IP Vanish", description="Cena: €1 / 4.5zł (Year)", emoji="🛡️"),
            discord.SelectOption(label="NexHub VPN", description="Zobacz ofertę NexHub VPN", emoji="🌐"),
            discord.SelectOption(label="Windscribe VPN", description="Zobacz ofertę Windscribe VPN", emoji="🌀"),
        ]
        super().__init__(
            placeholder="❌ × Click to select | Kliknij aby wybrać",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        if selected == "IP Vanish":
            embed = discord.Embed(
                title="IPVAN$SH 🛡️",
                color=discord.Color.from_rgb(0, 162, 232)
            )
            embed.add_field(name="» Ceny:", value="🛡️ **Year × €1 / 4.5zł**", inline=False)
            embed.add_field(name="» Krótki Opis:", value="✅ » Full Access\n✅ » Gotowy do użycia", inline=False)
            embed.set_footer(text="COLDSHOP • System VPN")
            view = PurchaseView(product_name="IPVanish VPN", price_text="€1 / 4.5 zł")
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            embed = discord.Embed(
                title=f"{selected} 🛡️",
                description="» **Cena:** 5 PLN / Rok\n» **Dostęp:** Pełny dostęp do konta.",
                color=discord.Color.from_rgb(0, 162, 232)
            )
            view = PurchaseView(product_name=selected, price_text="5 PLN")
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# --- 3. KOMENDY SETUPU PANELÓW ---

@bot.tree.command(name="setup_bundle", description="Ustawia panel z ofertami Bundles.")
@app_commands.checks.has_permissions(administrator=True)
async def setup_bundle(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📦 COLDSHOP × BUNDLE PRODUCTS 📦",
        description="Poniżej znajdziesz wszystkie dostępne paczki kont i usług w atrakcyjnych cenach!",
        color=discord.Color.from_rgb(0, 162, 232)
    )
    embed.add_field(
        name="Dostępne Bundles:",
        value="• ⭐ × **FiveM Ready Bundle**\n• 🎮 × **CS2 Prime + Steam Bundle**\n• 📦 × **Ultimate Gamer Bundle**",
        inline=False
    )
    embed.set_footer(text="COLDSHOP • Wybierz produkt z menu poniżej")
    view = discord.ui.View(timeout=None)
    view.add_item(BundleOnlySelect())
    
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Panel Bundle wysłany!", ephemeral=True)


@bot.tree.command(name="setup_vpn", description="Ustawia panel z ofertami VPN.")
@app_commands.checks.has_permissions(administrator=True)
async def setup_vpn(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛡️ COLDSHOP × VPN SERVICES 🛡️",
        description="Wybierz interesujący Cię program VPN z listy poniżej, aby poznać cennik i złożyć zamówienie.",
        color=discord.Color.from_rgb(0, 162, 232)
    )
    embed.add_field(
        name="Dostępne VPN-y:",
        value="• 🛡️ × **IP Vanish**\n• 🌐 × **NexHub**\n• 🌀 × **Windscribe**",
        inline=False
    )
    embed.set_footer(text="COLDSHOP • System Sprzedaży VPN")
    view = discord.ui.View(timeout=None)
    view.add_item(VpnOnlySelect())
    
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Panel VPN wysłany!", ephemeral=True)


# --- 4. KOMENDA /SAY (WIADOMOŚĆ W RAMCE EMBED) ---

@bot.tree.command(name="say", description="Wysyła ramkę ogłoszeniową (Embed) z wybranym tekstem.")
@app_commands.checks.has_permissions(administrator=True)
async def say(interaction: discord.Interaction, message: str, title: str = None, footer: str = "Bot • Ad made by px7.nj"):
    embed = discord.Embed(
        title=title if title else "",
        description=message,
        color=discord.Color.from_rgb(47, 49, 54)
    )
    if footer:
        embed.set_footer(text=footer)

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Wiadomość wysłana!", ephemeral=True)


# --- 5. KOMENDY BANOWANIA MODERACYJNEGO (/BANDC & /UNBANDC) ---

@bot.tree.command(name="bandc", description="Banuje użytkownika i wysyła powiadomienie w ramce kaskadowej.")
@app_commands.checks.has_permissions(ban_members=True)
async def bandc(interaction: discord.Interaction, user: discord.User, reason: str = "Brak powodu"):
    try:
        await interaction.guild.ban(user, reason=reason)
    except Exception as e:
        await interaction.response.send_message(f"❌ Nie udało się zbanować użytkownika: {e}", ephemeral=True)
        return

    embed = discord.Embed(
        title="🔨 User has been banned for life",
        color=discord.Color.red()
    )
    embed.add_field(name="👤 User", value=user.mention, inline=True)
    embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=True)
    embed.add_field(name="🛡️ Administrator", value=interaction.user.mention, inline=False)
    embed.add_field(name="📝 Reason", value=f"```\n{reason}\n```", inline=False)
    
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=f"COLDSHOP Security • Today at {discord.utils.utcnow().strftime('%H:%M')}")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="unbandc", description="Odbanowuje użytkownika na podstawie jego ID.")
@app_commands.checks.has_permissions(ban_members=True)
async def unbandc(interaction: discord.Interaction, user_id: str, reason: str = "Odbanowanie"):
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user, reason=reason)
    except Exception as e:
        await interaction.response.send_message(f"❌ Nie znaleziono zbanowanego użytkownika o podanym ID lub wystąpił błąd: {e}", ephemeral=True)
        return

    embed = discord.Embed(
        title="🔓 User has been unbanned",
        color=discord.Color.green()
    )
    embed.add_field(name="👤 User", value=f"{user.name} ({user.mention})", inline=True)
    embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=True)
    embed.add_field(name="🛡️ Administrator", value=interaction.user.mention, inline=False)
    embed.add_field(name="📝 Reason", value=f"```\n{reason}\n```", inline=False)
    embed.set_footer(text=f"COLDSHOP Security • Today at {discord.utils.utcnow().strftime('%H:%M')}")

    await interaction.response.send_message(embed=embed)


# --- 6. KOMENDA /DROP (MINIGRA) ---

@bot.tree.command(name="drop", description="Szanse na wygranie zniżki 20% do sklepu!")
async def drop(interaction: discord.Interaction):
    if interaction.channel_id != DROP_CHANNEL_ID:
        await interaction.response.send_message(
            f"❌ Ta komenda działa tylko na wskazanym kanale: <#{DROP_CHANNEL_ID}>!", 
            ephemeral=True
        )
        return

    win = random.randint(1, 100) <= 5

    if win:
        embed = discord.Embed(
            title="🎉 GRATULACJE! WYGRAŁEŚ ZNIŻKĘ!",
            description=f"🔥 {interaction.user.mention} trafił **5% szans** i wylosował **ZNIŻKĘ -20%** na dowolny zakup w **COLDSHOP**!\n\nZrób screena tej wiadomości i otwórz ticket w sklepie, aby odebrać rabat!",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="❄️ COLDSHOP DROP — BRAK TRAFIENIA",
            description=f"Niestety {interaction.user.mention}, tym razem się nie udało! Spróbuj ponownie później.",
            color=discord.Color.dark_gray()
        )
        await interaction.response.send_message(embed=embed)

bot.run(TOKEN)