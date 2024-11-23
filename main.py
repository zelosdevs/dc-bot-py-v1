
import discord
from discord import app_commands
from discord.ext import commands

BOT_TOKEN = "YOUR_TOKEN"

# Bot konfiguráció
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            application_id="YOUR_APPLICATION_ID" # Hogyha csak egy szerveren szeretnéd használni!
        )
        self.tree = app_commands.CommandTree(self)
        self.welcome_channel_id = None  # Welcome csatorna ID-ja

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# Események
@bot.event
async def on_ready():
    print(f"Bejelentkezve mint: {bot.user}")
    print(f"Slash parancsok szinkronizálva!")

@bot.event
async def on_member_join(member: discord.Member):
    if bot.welcome_channel_id:
        channel = bot.get_channel(bot.welcome_channel_id)
        if channel:
            await channel.send(f"Üdvözlünk a szerveren, {member.mention}! 🎉")

# Welcome rendszer
@bot.tree.command(name="setwelcomechannel", description="Beállítja az üdvözlő csatornát.")
@app_commands.describe(channel="A kívánt üdvözlő csatorna")
@app_commands.checks.has_permissions(administrator=True)
async def set_welcome_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    bot.welcome_channel_id = channel.id
    await interaction.response.send_message(f"Üdvözlő csatorna beállítva: {channel.mention}")

@bot.tree.command(name="removewelcomechannel", description="Eltávolítja az üdvözlő csatornát.")
@app_commands.checks.has_permissions(administrator=True)
async def remove_welcome_channel(interaction: discord.Interaction):
    bot.welcome_channel_id = None
    await interaction.response.send_message("Üdvözlő csatorna eltávolítva.")

# Ticket rendszer
class TicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Nyiss egy ticketet", style=discord.ButtonStyle.green)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        # Ticket csatorna létrehozása
        ticket_channel = await guild.create_text_channel(
            f"ticket-{interaction.user.name}",
            category=category
        )
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

        # Ticket embed megjelenítése Close gombbal
        view = TicketCloseView(ticket_channel)
        embed = discord.Embed(
            title="Ticket",
            description="Ha végeztél, kattints a **Close** gombra a ticket lezárásához.",
            color=discord.Color.orange()
        )
        await ticket_channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Ticket létrehozva itt: {ticket_channel.mention}", ephemeral=True)

class TicketCloseView(discord.ui.View):
    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket lezárása folyamatban...", ephemeral=True)
        await self.channel.delete()

@bot.tree.command(name="ticket", description="Ticket panel létrehozása.")
@app_commands.checks.has_permissions(manage_channels=True)
async def ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Ticket Rendszer",
        description="Kattints a gombra, hogy új ticketet hozz létre.",
        color=discord.Color.blurple()
    )
    view = TicketPanel()
    await interaction.response.send_message(embed=embed, view=view)

# Bot indítása
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
