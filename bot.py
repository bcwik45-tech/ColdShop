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


# --- 2. DEDYKOWANE PANEL SELEKCJI (BUNDLES / VPN) ---

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
    await interaction.response.send_message("✅ Panel Bundle wysłany!", ephemeral=