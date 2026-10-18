import os
import random
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

DROP_CH = 1561325772587925514       # Kanał dropu
WELCOME_CH = 1557150071177347152   
VERIFY_ROLE_ID = 1456459830494630102  # Rola weryfikacji

# ID KATEGORII TICKETÓW
CAT_OWNER = 1561333304131715112
CAT_SUPPORT = 1539002224007712911

BANNER = "http://googleusercontent.com/generated_animated_image/15959043500870823950"
CHEAT_BANNER = "https://cdn.discordapp.com/attachments/1556342431903911966/1561373946010669137/a444a5e8-9b52-4784-a325-e81795221c2d.png"

# EMOTKI / NAKLEJKI STANDARDOWE
E_IPVANISH = "<:ipvanish:1561340558314709082>"
E_FIVEM = "<:fivem:1561340614828621906>"
E_CS2 = "<:cs2:1561340401523363892>"
E_DISCORD = "<:discord:1551370496199761942>"
E_STEAM = "<:steam:1561340474349068338>"
E_NEXHUB = "<:nexhub:1561341038441013368>"

PE_IPVANISH = discord.PartialEmoji(name="ipvanish", id=1561340558314709082)
PE_FIVEM = discord.PartialEmoji(name="fivem", id=1561340614828621906)
PE_CS2 = discord.PartialEmoji(name="cs2", id=1561340401523363892)
PE_DISCORD = discord.PartialEmoji(name="discord", id=1551370496199761942)
PE_STEAM = discord.PartialEmoji(name="steam", id=1561340474349068338)
PE_NEXHUB = discord.PartialEmoji(name="nexhub", id=1561341038441013368)

# NAKLEJKI DO CHEATÓW
E_RED = "<:redengine:1460317809925029999>"
E_KEYSER = "<:keyser:1460317939231363113>"
E_FAMAS = "<:famas:1460318239723880559>"
E_LUMIA = "<:lumia:1460318085381619753>"
E_SERYX = "<:seryx:1500494525716631552>" # Użyte zastępczo z ID Seryx/Certyfikatu według dostarczonych linków
E_ECHO = "<:echofun:1507649865453273129>"
E_AMBANI = "<:ambani:1460318202637844531>"
E_K3 = "<:k3project:1488629802201120850>"
E_WORM = "<:worm:1546599858306031626>"

PE_RED = discord.PartialEmoji(name="redengine", id=1460317809925029999)
PE_KEYSER = discord.PartialEmoji(name="keyser", id=1460317939231363113)
PE_FAMAS = discord.PartialEmoji(name="famas", id=1460318239723880559)
PE_LUMIA = discord.PartialEmoji(name="lumia", id=1460318085381619753)
PE_SERYX = discord.PartialEmoji(name="seryx", id=1500494525716631552)
PE_ECHO = discord.PartialEmoji(name="echofun", id=1507649865453273129)
PE_AMBANI = discord.PartialEmoji(name="ambani", id=1460318202637844531)
PE_K3 = discord.PartialEmoji(name="k3project", id=1488629802201120850)
PE_WORM = discord.PartialEmoji(name="worm", id=1546599858306031626)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class VeloxShopBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        try:
            await self.tree.sync()
            print("✅ [VELOX SHOP] Komendy zsynchronizowane globalnie!")
        except Exception as e:
            print(f"⚠️ Błąd synchronizacji komend: {e}")

bot = VeloxShopBot()

# --- AUTOMATYCZNE POWITANIA ---
@bot.event
async def on_member_join(member: discord.Member):
    ch = bot.get_channel(WELCOME_CH)
    if not ch:
        return
    
    member_count = member.guild.member_count
    created_at = member.created_at.strftime("%d.%m.%Y %H:%M:%S")
    joined_at = member.joined_at.strftime("%d.%m.%Y %H:%M:%S") if member.joined_at else "Brak"

    desc = (
        f"🎉 Hi {member.mention}\n"
        "Welcome to **Velox Shop**!\n"
        "Go check out our stuff!\n\n"
        f"**You're our {member_count} member!**\n\n"
        "**Member Info:**\n"
        f"🪪 **Discord account created:**\n`{created_at}`\n"
        f"👤 **Username:** {member.name}\n"
        f"📅 **Joined at:** `{joined_at}`"
    )

    embed = discord.Embed(title="New member!", description=desc, color=discord.Color.dark_embed())
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    embed.set_image(url=BANNER)

    await ch.send(embed=embed)

# --- WIDOKI I SYSTEM TICKETÓW ---
class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij", style=discord.ButtonStyle.danger, custom_id="close_t")
    async def close(self, inter: discord.Interaction, btn: discord.ui.Button):
        await inter.response.send_message("Usuwanie ticketa za 3 sekundy...", ephemeral=True)
        await asyncio.sleep(3)
        await inter.channel.delete()

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, inter: discord.Interaction, ticket_type: str, emoji: str):
        await inter.response.defer(ephemeral=True)
        guild = inter.guild
        user = inter.user

        roles_to_ping = []
        category_id = None
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        if ticket_type == "Owner":
            category_id = CAT_OWNER
            role_ids = [1456459709405204542, 1531428039676792903]
            for r_id in role_ids:
                role = guild.get_role(r_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    roles_to_ping.append(role.mention)
        
        elif ticket_type == "Support":
            category_id = CAT_SUPPORT
            role_ids = [1555007565405094030, 1523678008869650575, 1555614403540295750, 1531428039676792903, 1456459709405204542]
            for r_id in role_ids:
                role = guild.get_role(r_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    roles_to_ping.append(role.mention)

        elif ticket_type == "Partnership":
            category_id = CAT_OWNER
            role_ids = [1456459709405204542, 1531428039676792903]
            for r_id in role_ids:
                role = guild.get_role(r_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    roles_to_ping.append(role.mention)

        elif ticket_type == "Shop":
            category_id = CAT_SUPPORT
            role_ids = [1456459709405204542]
            for r_id in role_ids:
                role = guild.get_role(r_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    roles_to_ping.append(role.mention)

        elif ticket_type == "Recruitment":
            category_id = CAT_SUPPORT
            role_ids = [1456459709405204542, 1531428039676792903]
            for r_id in role_ids:
                role = guild.get_role(r_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    roles_to_ping.append(role.mention)

        category = guild.get_channel(category_id) if category_id else None
        ch_name = f"{emoji}-ticket-{ticket_type.lower()}-{user.name.lower()}"

        ch = await guild.create_text_channel(
            name=ch_name,
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"Ticket: {ticket_type.upper()}",
            description=(
                f"Witaj {user.mention}!\n"
                "Administracja wkrótce odpowie na Twoje zgłoszenie.\n\n"
                "Aby zamknąć ten kanał, kliknij przycisk poniżej."
            ),
            color=discord.Color.blue()
        )
        
        ping_content = f"{user.mention} " + " ".join(roles_to_ping)
        await ch.send(content=ping_content, embed=embed, view=CloseView())
        await inter.followup.send(f"✅ Stworzono ticket: {ch.mention}", ephemeral=True)

    @discord.ui.button(label="Shop", emoji="🛒", style=discord.ButtonStyle.success, custom_id="t_shop")
    async def shop_btn(self, inter: discord.Interaction, btn: discord.ui.Button):
        await self.create_ticket(inter, "Shop", "🛒")

    @discord.ui.button(label="Owner", emoji="👑", style=discord.ButtonStyle.secondary, custom_id="t_owner")
    async def owner_btn(self, inter: discord.Interaction, btn: discord.ui.Button):
        await self.create_ticket(inter, "Owner", "👑")

    @discord.ui.button(label="Support", emoji="❓", style=discord.ButtonStyle.primary, custom_id="t_support")
    async def support_btn(self, inter: discord.Interaction, btn: discord.ui.Button):
        await self.create_ticket(inter, "Support", "❓")

    @discord.ui.button(label="Recruitment", emoji="📄", style=discord.ButtonStyle.danger, custom_id="t_recruitment")
    async def recruit_btn(self, inter: discord.Interaction, btn: discord.ui.Button):
        await self.create_ticket(inter, "Recruitment", "📄")

    @discord.ui.button(label="Partnership", emoji="🤝", style=discord.ButtonStyle.secondary, custom_id="t_partnership")
    async def partner_btn(self, inter: discord.Interaction, btn: discord.ui.Button):
        await self.create_ticket(inter, "Partnership", "🤝")

# --- PANEL ZAKUPU (EPHEMERAL) ---
class PurchaseSelect(discord.ui.Select):
    def __init__(self, placeholder: str, options: list):
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)

    async def callback(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True)
        product_variant = self.values[0]
        category = inter.guild.get_channel(CAT_SUPPORT)
        ch = await inter.guild.create_text_channel(
            name=f"🛒-ticket-{inter.user.name.lower()}",
            category=category,
            overwrites={
                inter.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                inter.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                inter.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )
        embed = discord.Embed(
            title="Ticket: SHOP",
            description=(
                f"Witaj {inter.user.mention}!\n"
                f"Otworzyłeś ticket zakupowy dla: **{product_variant}**.\n"
                "Administracja wkrótce odpowie na Twoje zgłoszenie.\n\n"
                "Aby zamknąć ten kanał, kliknij przycisk poniżej."
            ),
            color=discord.Color.blue()
        )
        role_shop = inter.guild.get_role(1456459709405204542)
        ping = role_shop.mention if role_shop else ""
        await ch.send(content=f"{inter.user.mention} {ping}", embed=embed, view=CloseView())
        await inter.followup.send(f"✅ Stworzono ticket: {ch.mention}", ephemeral=True)

# --- GŁÓWNE MENU BUNDLE / PRODUKTÓW ---
class ShopSelect(discord.ui.Select):
    def __init__(self, placeholder: str, options: list):
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)

    async def callback(self, inter: discord.Interaction):
        product_name = self.values[0]
        
        if product_name in ["IP Vanish", "IP Vanish VPN"]:
            desc = (
                "» **Ceny:**\n"
                f"> {E_IPVANISH} **Year** ✖️ **€1 / 4.5zł**\n\n"
                "» **Krótki Opis:**\n"
                "> ✅ » Full Access\n"
                "> ✅ » Gotowy do użycia"
            )
            embed = discord.Embed(title=f"IPVAN$SH {E_IPVANISH}", description=desc, color=discord.Color.blue())
            embed.set_image(url=BANNER)
            p_options = [discord.SelectOption(label="IP Vanish - €1 / 4.5 zł", value="IP Vanish - Year", description="Year", emoji=PE_IPVANISH)]
            v = discord.ui.View(timeout=None)
            v.add_item(PurchaseSelect(placeholder="❌ × Purchase Product | Zakup Produkt", options=p_options))
            await inter.response.send_message(embed=embed, view=v, ephemeral=True)

        elif product_name in ["NexHub", "NexHub VPN"]:
            desc = (
                "» **Ceny:**\n"
                f"> {E_NEXHUB} **1 Day** ✖️ **€1.7 / 7.5zł**\n"
                f"> {E_NEXHUB} **7 Days** ✖️ **€4.3 / 18.5zł**\n"
                f"> {E_NEXHUB} **Month** ✖️ **€8.6 / 37zł**\n"
                f"> {E_NEXHUB} **3 Months** ✖️ **€17.3 / 74.5zł**\n\n"
                "» **Krótki Opis:**\n"
                "> ✅ » Działa na ShootGG & Clowns.Cool\n"
                "> ✅ » 100+ Krai\n"
                "> ✅ » Gotowy do użycia\n"
                "> ✅ » Optymalny i szybki"
            )
            embed = discord.Embed(title=f"NEXHUB VPN {E_NEXHUB}", description=desc, color=discord.Color.blue())
            embed.set_image(url=BANNER)
            p_options = [
                discord.SelectOption(label="Nexhub - €1.7 / 7.5 zł", value="NexHub - 1 Day", description="1 Day", emoji=PE_NEXHUB),
                discord.SelectOption(label="Nexhub - €4.3 / 18.5 zł", value="NexHub - 7 Days", description="7 Days", emoji=PE_NEXHUB),
                discord.SelectOption(label="Nexhub - €8.6 / 37 zł", value="NexHub - Month", description="Month", emoji=PE_NEXHUB),
                discord.SelectOption(label="Nexhub - €17.3 / 74.5 zł", value="NexHub - 3 Months", description="3 Months", emoji=PE_NEXHUB)
            ]
            v = discord.ui.View(timeout=None)
            v.add_item(PurchaseSelect(placeholder="❌ × Purchase Product | Zakup Produkt", options=p_options))
            await inter.response.send_message(embed=embed, view=v, ephemeral=True)

        elif product_name in ["FiveM Ready", "FiveM Bundle"]:
            desc = (
                "» **Ceny:**\n"
                f"> {E_FIVEM} **Zwykłe Bundle** ✖️ **€0.24 / 1.00zł**\n"
                f"> {E_FIVEM} **Aged Bundle** ✖️ **€0.35 / 1.50zł**\n\n"
                "» **Krótki Opis:**\n"
                "> ✅ » Pakiet Rockst$r + Dsc + St$am\n"
                "> ✅ » Full Access\n"
                "> ✅ » Gotowy do użycia\n"
                "> ✅ » Działający"
            )
            embed = discord.Embed(title=f"FIVEM BUNDLE {E_FIVEM}", description=desc, color=discord.Color.blue())
            embed.set_image(url=BANNER)
            p_options = [
                discord.SelectOption(label="Zwykłe Bundle - €0.24 / 1.00zł", value="FiveM Zwykłe Bundle", description="Zwykłe Bundle", emoji=PE_FIVEM),
                discord.SelectOption(label="Aged Bundle - €0.35 / 1.50zł", value="FiveM Aged Bundle", description="Aged Bundle", emoji=PE_FIVEM)
            ]
            v = discord.ui.View(timeout=None)
            v.add_item(PurchaseSelect(placeholder="❌ × Purchase Product | Zakup Produkt", options=p_options))
            await inter.response.send_message(embed=embed, view=v, ephemeral=True)

        elif product_name in ["D1scörd", "D1scörd Bundle"]:
            desc = (
                "» **Ceny:**\n"
                f"> {E_DISCORD} **x3** ✖️ **€0.70 / 3zł**\n"
                f"> {E_DISCORD} **x10** ✖️ **€1.9 / 8zł**\n\n"
                "» **Krótki Opis:**\n"
                "> ✅ » Full Access\n"
                "> ✅ » Gotowy do użycia\n"
                "> ✅ » Działające"
            )
            embed = discord.Embed(title=f"DISCORD BUNDLE {E_DISCORD}", description=desc, color=discord.Color.blue())
            embed.set_image(url=BANNER)
            p_options = [
                discord.SelectOption(label="Discord Bundle - €0.70 / 2.99 zł", value="Discord Bundle x3", description="3 acc Discord", emoji=PE_DISCORD),
                discord.SelectOption(label="Discord Bundle - €1.87 / 7.99 zł", value="Discord Bundle x10", description="10 acc Discord", emoji=PE_DISCORD)
            ]
            v = discord.ui.View(timeout=None)
            v.add_item(PurchaseSelect(placeholder="❌ × Purchase Product | Zakup Produkt", options=p_options))
            await inter.response.send_message(embed=embed, view=v, ephemeral=True)

        # --- OBSŁUGA CHEATÓW FIVE-M (CENY PODWYŻSZONE O 3 ZŁ) ---
        elif product_name == "Red Engine":
            desc = (
                "» **Ceny:**\n"
                f"> {E_RED} **7 Days** ✖️ **€14 / 60zł**\n"
                f"> {E_RED} **1 Month** ✖️ **€25 / 102zł**\n"
                f"> {E_RED} **Lifetime** ✖️ **€40 / 173zł**\n\n"
                "» **Krótki Opis:**\n"
                "> ✅ » Premium Menu\n"
                "> ✅ » Opcję pod Trolling\n"
                "> ✅ » Gotowy do użycia\n"
                "> ✅ » Najlepszy z Executorów\n"
                "> ✅ » Event Logger\n"
                "> ✅ » Lua Executor"
            )
            embed = discord.Embed(title=f"REDENGINE {E_RED}", description=desc, color=discord.Color.blue())
            embed.set_image(url=CHEAT_BANNER)
            p_options = [
                discord.SelectOption(label="Red Engine - €14 / 60 zł", value="Red Engine Weekly", emoji=PE_RED),
                discord.SelectOption(label="Red Engine - €25 / 102 zł", value="Red Engine Month", emoji=PE_RED),
                discord.SelectOption(label="Red Engine - €40 / 173 zł", value="Red Engine Lifetime", emoji=PE_RED)
            ]
            v = discord.ui.View(timeout=None)
            v.add_item(PurchaseSelect(placeholder="❌ × Purchase Product | Zakup Produkt", options=p_options))
            await inter.response.send_message(embed=embed, view=v, ephemeral=True)

        elif product_name == "Keyser":
            desc = (
                "» **Ceny:**\n"
                f"> {E_KEYSER} **1 Day** ✖️ **€5 / 23zł**\n"
                f"> {E_KEYSER} **7 Days** ✖️ **€10 / 43zł**\n"
                f"> {E_KEYSER} **1 Month** ✖️ **€14 / 62zł**\n"
                f"> {E_KEYSER} **Lifetime** ✖️ **€35 / 151zł**\n\n"
                "» **Krótki Opis:**\n"
                "> ✅ » Wbudowany Sp00fer\n"
                "> ✅ » Opcję pod Trolling\n"
                "> ✅ » Free Cam z Opcjami\n"
                "> ✅ » Kill Everyone\n"
                "> ✅ » Kill Player\n"
                "> ✅ » Event Executor & Logger"
            )
            embed = discord.Embed(title=f"KEYSER {E_KEYSER}", description=desc, color=discord.Color.blue())
            embed.set_image(url=CHEAT_BANNER)
            p_options = [
                discord.SelectOption(label="Keyser - €5 / 23 zł", value="Keyser 1 Day", emoji=PE_KEYSER),
                discord.SelectOption(label="Keyser - €10 / 43 zł", value="Keyser 7 Days", emoji=PE_KEYSER),
                discord.SelectOption(label="Keyser - €14 / 62 zł", value="Keyser 1 Month", emoji=PE_KEYSER),
                discord.SelectOption(label="Keyser - €35 / 151 zł", value="Keyser Lifetime", emoji=PE_KEYSER)
            ]
            v = discord.ui.View(timeout=None)
            v.add_item(PurchaseSelect(placeholder="❌ × Purchase Product | Zakup Produkt", options=p_options))
            await inter.response.send_message(embed=embed, view=v, ephemeral=True)

        elif product_name == "Famas":
            desc = (
                "» **Ceny:**\n"
                f"> {E_FAMAS} **7 Days** ✖️ **€7 / 33zł**\n"
                f"> {E_FAMAS} **1 Month** ✖️ **€14 / 63zł**\n"
                f"> {E_FAMAS} **Lifetime** ✖️ **€32 / 142zł**\n\n"
                "» **Krótki Opis:**\n"
                "> ✅ » Electron & Fiveguard bypassy\n"
                "> ✅ » Crashowanie Graczy\n"
                "> ✅ » Dobre pod Trolling (dużo opcji)\n"
                "> ✅ » Jest niewykrywalny na Clowns.cool & Shoot.gg\n"
                "> ✅ » Lauch Player i inne\n"
                "> ✅ » Dumper & Executor\n"
                "> ✅ » Bardzo łatwe do respienia rzeczy\n"
                "> ✅ » Znajduje ci Antych$ta"
            )
            embed = discord.Embed(title=f"FAMAS {E_FAMAS}", description=desc, color=discord.Color.blue())
            embed.set_image(url=CHEAT_BANNER)
            p_options = [
                discord.SelectOption(label="Famas - €7 / 33 zł", value="Famas Weekly", emoji=PE_FAMAS),
                discord.SelectOption(label="Famas - €14 / 63 zł", value="Famas Monthly", emoji=PE_FAMAS),
                discord.SelectOption(label="Famas - €32 / 142 zł", value="Famas Lifetime", emoji=PE_FAMAS)
            ]
            v = discord.ui.View(timeout=None)
            v.add_item(PurchaseSelect(placeholder="❌ × Purchase Product | Zakup Produkt", options=p_options))
            await inter.response.send_message(embed=embed, view=v, ephemeral=True)

        elif product_name == "Lumia":
            desc = (
                "» **Ceny:**\n"
                f"> {E_LUMIA} **1 Day** ✖️ **€4.5 / 23zł**\n"
                f"> {E_LUMIA} **7 Days** ✖️ **€8.5 / 40zł**\n"
                f"> {E_LUMIA} **1 Month** ✖️ **€17 / 77zł**\n"
                f"> {E_LUMIA} **Lifetime** ✖️ **€43 / 188zł**\n\n"
                "» **Krótki Opis:**\n"
                "> ✅ » Crash Everyone\n"
                "> ✅ » Masa Troll Opcji\n"
                "> ✅ » Gotowy do użycia\n"
                "> ✅ » Kill Everyone oraz inne\n"
                "> ✅ » Bypassy na antych$atach\n"
                "> ✅ » Lazer Eyes"
            )
            embed = discord.Embed(title=f"LUMIA MENU {E_LUMIA}", description=desc, color=discord.Color.blue())
            embed.set_image(url=CHEAT_BANNER)
            p_options = [
                discord.SelectOption(label="Lumia - €4.5 / 23 zł", value="Lumia 1 Day", emoji=PE_LUMIA),
                discord.SelectOption(label="Lumia - €8.5 / 40 zł", value="Lumia 7 Days", emoji=PE_LUMIA),
                discord.SelectOption(label="Lumia - €17 / 77 zł", value="Lumia 1 Month", emoji=PE_LUMIA),
                discord.SelectOption(label="Lumia - €43 / 188 zł", value="Lumia Lifetime", emoji=PE_LUMIA)
            ]
            v = discord.ui.View(timeout=None)
            v.add_item(PurchaseSelect(placeholder="❌ × Purchase Product | Zakup Produkt", options=p_options))
            await inter.response.send_message(embed=embed, view=v, ephemeral=True)

        elif product_name == "Seryx":
            desc = (
                "» **Ceny:**\n"
                f"> {E_SERYX} **7 Days** ✖️ **€10 / 45zł**\n"
                f"> {E_SERYX} **1 Month** ✖️ **€15 / 67zł**\n"
                f"> {E_SERYX} **Lifetime** ✖️ **€26 / 113zł**\n\n"
                "» **Krótki Opis:**\n"
                "> ✅ » Wbudowany Sp00fer\n"
                "> ✅ » Silent Aim & Aimbot\n"
                "> ✅ » Freecam z Shoot Vehicle\n"
                "> ✅ » Spawn Aut oraz Broni\n"
                "> ✅ » Zrobiony pod PVP\n"
                "> ✅ » Ładne Visualsy\n"
                "> ✅ » Resource Stoper"
            )
            embed = discord.Embed(title=f"SERYX {E_SERYX}", description=desc, color=discord.Color.blue())
            embed.set_image(url=CHEAT_BANNER)
            p_options = [
                discord.SelectOption(label="Seryx - €10 / 45 zł", value="Seryx 7 Days", emoji=PE_SERYX),
                discord.SelectOption(label="Seryx - €15 / 67 zł", value="Seryx 1 Month", emoji=PE_SERYX),
                discord.SelectOption(label="Seryx - €26 / 113 zł", value="Seryx Lifetime", emoji=PE_SERYX)
            ]
            v = discord.ui.View(timeout=None)
            v.add_item(PurchaseSelect(placeholder="❌ × Purchase Product | Zakup Produkt", options=p_options))
            await inter.response.send_message(embed=embed, view=v, ephemeral=True)

        elif product_name == "Echo.fun":
            desc = (
                "» **Ceny:**\n"
                f"> {E_ECHO} **7 Days** ✖️ **€5 / 23zł**\n"
                f"> {E_ECHO} **1 Month** ✖️ **€13 / 57zł**\n"
                f"> {E_ECHO} **Lifetime** ✖️ **€43 / 182zł**\n\n"
                "» **Krótki Opis:**\n"
                "> ✅ » 100% Niewykrywalne Hitboxy (Wszystkie serwery)\n"
                "> ✅ » Niewykrywalny Silent Aim\n"
                "> ✅ » Idealne pod Shootgg & Clowns\n"
                "> ✅ » Idealne ESPY\n"
                "> ✅ » Lua Executor\n"
                "> ✅ » Prosty w konfiguracji"
            )
            embed = discord.Embed(title=f"ECHOFUN {E_ECHO}", description=desc, color=discord.Color.blue())
            embed.set_image(url=CHEAT_BANNER)
            p_options = [
                discord.SelectOption(label="Echo - €5 / 23 zł", value="Echo Weekly", emoji=PE_ECHO),
                discord.SelectOption(label="Echo - €13 / 57 zł", value="Echo Monthly", emoji=PE_ECHO),
                discord.SelectOption(label="Echo - €43 / 182 zł", value="Echo Lifetime", emoji=PE_ECHO)
            ]
            v = discord.ui.View(timeout=None)
            v.add_item(PurchaseSelect(placeholder="❌ × Purchase Product | Zakup Produkt", options=p_options))
            await inter.response.send_message(embed=embed, view=v, ephemeral=True)

        elif product_name == "Ambani":
            desc = (
                "» **Ceny:**\n"
                f"> {E_AMBANI} **7 Days** ✖️ **€9.5 / 43zł**\n"
                f"> {E_AMBANI} **1 Month** ✖️ **€14 / 63zł**\n"
                f"> {E_AMBANI} **Lifetime** ✖️ **€33 / 143zł**\n\n"
                "» **Krótki Opis:**\n"
                "> ✅ » Dobry ESP\n"
                "> ✅ » Troll Opcję\n"
                "> ✅ » Kill Player\n"
                "> ✅ » Kill Everyone i inne\n"
                "> ✅ » Event Logger & Executor"
            )
            embed = discord.Embed(title=f"AMBANI {E_AMBANI}", description=desc, color=discord.Color.blue())
            embed.set_image(url=CHEAT_BANNER)
            p_options = [
                discord.SelectOption(label="Ambani - €9.5 / 43 zł", value="Ambani Weekly", emoji=PE_AMBANI),
                discord.SelectOption(label="Ambani - €14 / 63 zł", value="Ambani Month", emoji=PE_AMBANI),
                discord.SelectOption(label="Ambani - €33 / 143 zł", value="Ambani Lifetime", emoji=PE_AMBANI)
            ]
            v = discord.ui.View(timeout=None)
            v.add_item(PurchaseSelect(placeholder="❌ × Purchase Product | Zakup Produkt", options=p_options))
            await inter.response.send_message(embed=embed, view=v, ephemeral=True)

        elif product_name == "K3 Project":
            desc = (
                "» **Ceny:**\n"
                f"> {E_K3} **7 Days** ✖️ **€5 / 23zł**\n"
                f"> {E_K3} **1 Month** ✖️ **€9 / 39zł**\n"
                f"> {E_K3} **3 Months** ✖️ **€17 / 75zł**\n"
                f"> {E_K3} **Lifetime** ✖️ **€30 / 129zł**\n\n"
                "» **Krótki Opis:**\n"
                "> ✅ » External\n"
                "> ✅ » Wbudowany Sp00fer\n"
                "> ✅ » Jest niewykrywalny na Clowns.cool & ShootGG\n"
                "> ✅ » Resources Stopper\n"
                "> ✅ » Weapon Spawner"
            )
            embed = discord.Embed(title=f"K3 PROJECT {E_K3}", description=desc, color=discord.Color.blue())
            embed.set_image(url=CHEAT_BANNER)
            p_options = [
                discord.SelectOption(label="K3 - €5 / 23 zł", value="K3 7 Days", emoji=PE_K3),
                discord.SelectOption(label="K3 - €9 / 39 zł", value="K3 1 Month", emoji=PE_K3),
                discord.SelectOption(label="K3 - €17 / 75 zł", value="K3 3 Months", emoji=PE_K3),
                discord.SelectOption(label="K3 - €30 / 129 zł", value="K3 Lifetime", emoji=PE_K3)