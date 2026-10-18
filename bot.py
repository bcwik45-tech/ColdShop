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

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class ColdBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD_ID)
        await self.tree.sync(guild=MY_GUILD_ID)
        print("✅ Bot gotowy i zsynchronizowany!")

bot = ColdBot()

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Usuwanie ticketa za 5 sekund...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class LegitCheckView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.yes_count = 0

    @discord.ui.button(label="0", emoji="✅", style=discord.ButtonStyle.success, custom_id="legit_yes_btn")
    async def legit_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.yes_count += 1
        button.label = str(self.yes_count)
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("✅ Dziękujemy za głos!", ephemeral=True)

@bot.tree.command(name="setup_legitchecks", description="Panel legit check.")
@app_commands.checks.has_permissions(administrator=True)
async def setup_legitchecks(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(title="⭐ COLDSHOP × LEGIT CHECK", description="Kliknij ✅, aby wystawić opinię.", color=discord.Color.blue())
    await interaction.channel.send(embed=embed, view=LegitCheckView())
    await interaction.followup.send("✅ Stworzono panel!", ephemeral=True)

@bot.tree.command(name="feedback", description="Wysyła opinię.")
@app_commands.checks.has_permissions(administrator=True)
async def feedback(interaction: discord.Interaction):
    await interaction.response.send_message("⭐ Dziękujemy za zakupy w COLDSHOP!", ephemeral=True)

@bot.tree.command(name="drop", description="Minigra ze zniżką!")
async def drop(interaction: discord.Interaction):
    if interaction.channel_id != DROP_CHANNEL_ID:
        await interaction.response.send_message("❌ Zły kanał!", ephemeral=True)
        return
    win = random.randint(1, 100) <= 5
    if win:
        await interaction.response.send_message(f"🎉 {interaction.user.mention} wygrał 20% zniżki!")
    else:
        await interaction.response.send_message(f"❄️ Niestety {interaction.user.mention}, spróbuj ponownie.")

async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())