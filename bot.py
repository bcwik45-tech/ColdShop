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


# --- 2. DEDYKOWANE PANELA SELEKCJI (BUNDLES / VPN) ---

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


class VpnOnlySelect(discord.ui