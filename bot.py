import os
import random
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

MY_GUILD = discord.Object(id=1561157589511839898)
DROP_CH = 1561163117726011533
BANNER = "http://googleusercontent.com/generated_animated_image/15959043500870823950"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        print("✅ Bot gotowy i zsynchronizowany!")

bot = Bot()

class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Zamknij", style=discord.ButtonStyle.danger, custom_id="close_t")
    async def close(self, inter: discord.Interaction, btn: discord.ui.Button):
        await inter.response.send_message("Usuwanie ticketa...", ephemeral=True)
        await asyncio.sleep(3)
        await inter.channel.delete()

class ShopSelect(discord.ui.Select):
    def __init__(self, name):
        super().__init__(placeholder=f"Wybierz {name}", options=[discord.SelectOption(label="Kup teraz", value="buy", emoji="🛡️")])
        self.name = name
    async def callback(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True)
        ch = await inter.guild.create_text_channel(name=f"ticket-{inter.user.name}", overwrites={
            inter.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            inter.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            inter.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        })
        await ch.send(f"{inter.user.mention}", embed=discord.Embed(title=f"Ticket: {self.name}", color=discord.Color.blue()), view=CloseView())
        await inter.followup.send(f"Stworzono: {ch.mention}", ephemeral=True)

class LegitView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.y, self.n = 0, 0
    @discord.ui.button(label="0", emoji="✅", style=discord.ButtonStyle.success, custom_id="leg_y")
    async def yes(self, inter: discord.Interaction, btn: discord.ui.Button):
        self.y += 1
        btn.label = str(self.y)
        await inter.response.edit_message(view=self)
        await inter.followup.send("Dzięki za głos!", ephemeral=True)
    @discord.ui.button(label="0", emoji="❌", style=discord.ButtonStyle.danger, custom_id="leg_n")
    async def no(self, inter: discord.Interaction, btn: discord.ui.Button):
        self.n += 1
        btn.label = str(self.n)
        await inter.response.edit_message(view=self)
        await inter.followup.send("Dzięki za głos!", ephemeral=True)

@bot.tree.command(name="setup_legitchecks", description="Panel legit")
@app_commands.checks.has_permissions(administrator=True)
async def sl(inter: discord.Interaction):
    await inter.response.defer(ephemeral=True)
    embed = discord.Embed(title="⭐ COLDSHOP × LEGIT CHECK", description="Kliknij ✅ lub ❌", color=discord.Color.blue())
    embed.set_image(url=BANNER)
    await inter.channel.send(embed=embed, view=LegitView())
    await inter.followup.send("Gotowe!", ephemeral=True)

@bot.tree.command(name="setup_vpn", description="Panel VPN")
@app_commands.checks.has_permissions(administrator=True)
async def svpn(inter: discord.Interaction):
    await inter.response.defer(ephemeral=True)
    v = discord.ui.View(timeout=None)
    v.add_item(ShopSelect("VPN"))
    await inter.channel.send(embed=discord.Embed(title="🛡️ VPN", color=discord.Color.blue()), view=v)
    await inter.followup.send("Gotowe!", ephemeral=True)

@bot.tree.command(name="setup_bundle", description="Panel Bundle")
@app_commands.checks.has_permissions(administrator=True)
async def sb(inter: discord.Interaction):
    await inter.response.defer(ephemeral=True)
    v = discord.ui.View(timeout=None)
    v.add_item(ShopSelect("Bundle"))
    await inter.channel.send(embed=discord.Embed(title="📦 Bundle", color=discord.Color.blue()), view=v)
    await inter.followup.send("Gotowe!", ephemeral=True)

@bot.tree.command(name="setup_shop", description="Sklep")
@app_commands.checks.has_permissions(administrator=True)
async def sshop(inter: discord.Interaction):
    await inter.response.defer(ephemeral=True)
    v = discord.ui.View(timeout=None)
    v.add_item(ShopSelect("Sklep"))
    await inter.channel.send(embed=discord.Embed(title="🛒 Sklep", color=discord.Color.blue()), view=v)
    await inter.followup.send("Gotowe!", ephemeral=True)

@bot.tree.command(name="feedback", description="Opinia")
@app_commands.checks.has_permissions(administrator=True)
async def fb(inter: discord.Interaction):
    await inter.response.send_message("⭐ Dziękujemy za zakupy w COLDSHOP!", ephemeral=True)

@bot.tree.command(name="drop", description="Drop")
async def dp(inter: discord.Interaction):
    if inter.channel_id != DROP_CH:
        await inter.response.send_message("❌ Zły kanał!", ephemeral=True)
        return
    if random.randint(1, 100) <= 5:
        await inter.response.send_message(f"🎉 {inter.user.mention} wygrał 20% zniżki!")
    else:
        await inter.response.send_message(f"❄️ Niestety {inter.user.mention}, spróbuj ponownie.")

bot.run(TOKEN)