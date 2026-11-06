import os
import datetime
import threading
from flask import Flask
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# --- SERWER HTTP (Musi być na głównym wątku dla Rendera) ---
app = Flask('')

@app.route('/', methods=['GET', 'HEAD'])
def home():
    return "Bot is active and running!", 200

@app.route('/health', methods=['GET', 'HEAD'])
def health():
    return "OK", 200

# --- KONFIGURACJA BOTA ---
BANNER_URL = "https://cdn.discordapp.com/attachments/1566913978515464246/1567544191456776314/banner_zayro.png?ex=6aec90ca&is=6aeb3f4a&hm=4c752e67ec46147355292cf08789814fab80d5e9745a772253fc392af52ef55d&"

WELCOME_CHANNEL_ID = 1566913703767707670
BOOST_CHANNEL_ID = 1566923418228760606
AUTO_ROLE_ID = 1566920586968563773

TICKET_COMMAND_CHANNEL_ID = 1566913978515464246
TICKET_PANEL_CHANNEL_ID = 1567547750155952198
TICKET_ISSUES_CHANNEL_ID = 1566918887235260516

CATEGORY_OWNER = 1567544808870780928
CATEGORY_SUPPORT = 1567545250656948314
CATEGORY_PARTNER = 1567545665167560775

E_WELCOME = ["<:w1:1567540850873999371>", "<:w2:1567541120861470740>", "<:w3:1567541279565291580>", "<:w4:1567541402370318427>", "<:w5:1567541561330376704>"]
E_BOOST = ["<:b1:1567546207876939876>", "<:b2:1567546347429830836>", "<:b3:1567546492657602671>", "<:b4:1567546612773949510>"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket_btn_v13")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Zamykanie ticketu za 5 sekund...")
        await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=5))
        await interaction.channel.delete()

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Owner", description="ticket with a matter for the config owners", emoji="👑", value="owner"),
            discord.SelectOption(label="Support", description="Support ticket for help in our config server", emoji="❓", value="support"),
            discord.SelectOption(label="Partner", description="Ticket for partnership", emoji="🤝", value="partner"),
        ]
        super().__init__(placeholder="Select category", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu_v13")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        val = self.values[0]

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        role_ids = []
        category_id = None
        title_name = ""

        if val == "owner":
            role_ids = [1566919540242260150, 1566919770589110272]
            category_id = CATEGORY_OWNER
            title_name = "OWNER"
        elif val == "support":
            role_ids = [1566920179185877153, 1566919962268930058, 1566919770589110272, 1566919540242260150]
            category_id = CATEGORY_SUPPORT
            title_name = "SUPPORT"
        elif val == "partner":
            role_ids = [1566919540242260150, 1566919770589110272]
            category_id = CATEGORY_PARTNER
            title_name = "PARTNERSHIP"

        for r_id in role_ids:
            role = guild.get_role(r_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        category = guild.get_channel(category_id)
        ticket_channel = await guild.create_text_channel(
            name=f"{val}-{user.name}",
            category=category,
            overwrites=overwrites
        )

        await interaction.response.send_message(f"Twój ticket został utworzony: {ticket_channel.mention}", ephemeral=True)

        pings = f"{user.mention} " + " ".join([f"<@&{r}>" for r in role_ids])

        embed = discord.Embed(color=discord.Color.dark_grey())
        embed.description = (
            f"**• {title_name} 🛒**\n\n"
            f"**Open date:** {discord.utils.utcnow().strftime('%d %B %Y, %H:%M')}\n"
            f"**Opening user:** {user.mention}\n\n"
            f"**Description:** Please