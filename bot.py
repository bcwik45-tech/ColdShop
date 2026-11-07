import os
import time
import threading
import requests
from flask import Flask
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# --- SERWER HTTP ---
app = Flask('')

@app.route('/', methods=['GET', 'HEAD'])
def home():
    return "Bot is active and running!", 200

@app.route('/health', methods=['GET', 'HEAD'])
def health():
    return "OK", 200

# --- KONFIGURACJA BOTA ---
BANNER_URL = "https://cdn.discordapp.com/attachments/1566913978515464246/1567544191456776314/banner_zayro.png"

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

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket_btn_v21")
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
        super().__init__(placeholder="Select category", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu_v21")

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

        embed = discord.Embed(color=discord.Color.dark_embed())
        embed.description = (
            f"**• {title_name} 🛒**\n\n"
            f"**Open date:** {discord.utils.utcnow().strftime('%d %B %Y, %H:%M')}\n"
            f"**Opening user:** {user.mention}\n\n"
            "**Description:** Please give us details about your reason to open this ticket.\n"
            "Click the button below to close the ticket."
        )
        await ticket_channel.send(content=pings, embed=embed, view=CloseTicketView())

class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Zalogowano jako: {bot.user}")

@bot.event
async def on_member_join(member: discord.Member):
    auto_role = member.guild.get_role(AUTO_ROLE_ID)
    if auto_role:
        try:
            await member.add_roles(auto_role, reason="Automatyczna ranga po wejściu na serwer.")
        except Exception as e:
            print(f"Błąd nadawania auto-rangi: {e}")

    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        emojis_str = " ".join(E_WELCOME)
        embed = discord.Embed(
            description=(
                f"# New user joined us! 🙂\n\n"
                f"{emojis_str}\n\n"
                f"**Hi {member.mention} We're glad to have you here!**\n"
                f"> Go check out our fivem stuff!\n"
                f"> Don't forget to read the rules!\n"
                f"> **You're our {member.guild.member_count} member!**\n\n"
                f"📢 **User Information**\n"
                f"▫️ **Discord account created:** `{member.created_at.strftime('%Y-%m-%d %H:%M:%S')}`\n"
                f"▫️ **Username:** `{member.name}`\n"
                f"▫️ **Joined at:** `{member.joined_at.strftime('%Y-%m-%d %H:%M:%S')}`"
            ),
            color=discord.Color.dark_embed()
        )
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text="Zayro")
        await channel.send(embed=embed)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if (not before.premium_since and after.premium_since):
        channel = after.guild.get_channel(BOOST_CHANNEL_ID)
        if channel:
            boost_emojis = " ".join(E_BOOST)
            embed = discord.Embed(
                title="💎 New server Boost!",
                description=(
                    f"{after.mention} **BOOST!**\n"
                    f"> thanks for boosting our server!\n"
                    f"> *Go check out our booster zone!*\n\n"
                    f"🚀 **Boost level**\n"
                    f"▫️ **Server Boost level:** `{after.guild.premium_tier}`\n"
                    f"▫️ **Boost count:** `{after.guild.premium_subscription_count}`\n\n"
                    f"{boost_emojis}"
                ),
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            embed.set_image(url=BANNER_URL)
            embed.set_footer(text="Zayro")
            await channel.send(embed=embed)

@bot.tree.command(name="ticket", description="Wysyła panel ticketów na kanal docelowy.")
async def ticket_cmd(interaction: discord.Interaction):
    if interaction.channel_id != TICKET_COMMAND_CHANNEL_ID:
        return await interaction.response.send_message("Tej komendy możesz użyć tylko na przeznaczonym do tego kanale!", ephemeral=True)

    target_channel = interaction.guild.get_channel(TICKET_PANEL_CHANNEL_ID)
    if not target_channel:
        return await interaction.response.send_message("Nie znaleziono kanału docelowego dla panelu!", ephemeral=True)

    embed = discord.Embed(
        title="Tickets",
        description=(
            "**Ticket Owner**\n*Open if you have a demand to the owners*\n\n"
            "**Ticket Support**\n*Open if you need any help*\n\n"
            "**Ticket Partner**\n*Open if you want to collaborate with us.*\n\n"
            f"┃ **For any issues, text on** <#{TICKET_ISSUES_CHANNEL_ID}>"
        ),
        color=discord.Color.dark_embed()
    )
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="Zayro")

    await interaction.response.send_message("Panel ticketów został wysłany!", ephemeral=True)
    await target_channel.send(embed=embed, view=TicketPanelView())

@bot.tree.command(name="bandc", description="Banuje użytkownika i wysyła log z bannerem.")
@app_commands.checks.has_permissions(ban_members=True)
async def bandc(interaction: discord.Interaction, user: discord.User, reason: str = "Brak powodu"):
    await interaction.guild.ban(user, reason=reason)
    embed = discord.Embed(title="🔨 User has been banned for life", color=discord.Color.red())
    embed.add_field(name="👤 User:", value=user.mention, inline=False)
    embed.add_field(name="🆔 ID:", value=f"`{user.id}`", inline=False)
    embed.add_field(name="🛡️ Administrator:", value=interaction.user.mention, inline=False)
    embed.add_field(name="📝 Reason:", value=f"```\n{reason}\n```", inline=False)
    embed.set_image(url=BANNER_URL)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unbandc", description="Odbanowuje użytkownika i wysyła log z bannerem.")
@app_commands.checks.has_permissions(ban_members=True)
async def unbandc(interaction: discord.Interaction, user_id: str, reason: str = "Brak powodu"):
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user, reason=reason)
    embed = discord.Embed(title="🔓 User has been unbanned", color=discord.Color.green())
    embed.add_field(name="👤 User:", value=user.mention, inline=False)
    embed.add_field(name="🆔 ID:", value=f"`{user.id}`", inline=False)
    embed.add_field(name="🛡️ Administrator:", value=interaction.user.mention, inline=False)
    embed.add_field(name="📝 Reason:", value=f"```\n{reason}\n```", inline=False)
    embed.set_image(url=BANNER_URL)
    await interaction.response.send_message(embed=embed)

def run_bot():
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)

def self_ping():
    time.sleep(30)
    while True:
        try:
            requests.get("https://coldshop-9byh.onrender.com", timeout=10)
        except:
            pass
        time.sleep(300)

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    ping_thread = threading.Thread(target=self_ping)
    ping_thread.daemon = True
    ping_thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)