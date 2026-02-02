import os
import re
import discord
from discord import app_commands
from discord.ext import commands

# ===== CONFIG =====
TOKEN = os.getenv("DISCORD_TOKEN")

HOSTED_ROLE_ID = 1467862590670639249      # normal lobbies
MODDED_ROLE_ID = 1467868524197183508      # modded lobbies

TIME_TEXT = "<t:1770060600:t>"
LOBBY_CHANNEL_NAME = "<#1467841323678699582>"  # just text shown in auto reply

# ===== INTENTS =====
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=None, intents=intents)

# ===== STORAGE =====
normal_lobbies = {}   # user_id -> code
modded_lobbies = {}   # user_id -> code

# ===== HELPERS =====
def clean_code(code: str) -> str:
    code = code.strip().upper()
    return code if re.fullmatch(r"[A-Z]{6}", code) else ""

class CopyCodeView(discord.ui.View):
    def __init__(self, code: str):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="Copy lobby code",
                style=discord.ButtonStyle.secondary,
                emoji="📋",
                custom_id="copy_code"
            )
        )
        self.code = code

    @discord.ui.button(label="Copy lobby code", style=discord.ButtonStyle.secondary, emoji="📋")
    async def copy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"```{self.code}```",
            ephemeral=True
        )

# ===== EVENTS =====
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if "is someone hosting" in message.content.lower():
        await message.channel.send(
            f"We usually host at {TIME_TEXT}, "
            f"but you can always check {LOBBY_CHANNEL_NAME} for current lobbies!"
        )

# ===== SLASH COMMANDS =====
@bot.tree.command(name="help", description="Show Clover Bot commands")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="Clover Bot Commands")
    embed.add_field(name="/host <CODE>", value="Host a normal lobby", inline=False)
    embed.add_field(name="/modhost <CODE>", value="Host a modded lobby", inline=False)
    embed.add_field(name="/endhost", value="End your hosted lobby", inline=False)
    embed.add_field(name="/mylobby", value="Show your active lobby", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="host", description="Host a normal lobby")
@app_commands.describe(code="6-letter lobby code")
async def host_cmd(interaction: discord.Interaction, code: str):
    code = clean_code(code)
    if not code:
        return await interaction.response.send_message(
            "❌ Invalid code. Use 6 letters like `HHHIGG`.",
            ephemeral=True
        )

    normal_lobbies[interaction.user.id] = code

    role = interaction.guild.get_role(HOSTED_ROLE_ID)
    ping = role.mention if role else ""

    embed = discord.Embed(
        title="🛸 Lobby Hosted!",
        description=f"Lobby hosted by {interaction.user.mention}"
    )
    embed.add_field(name="Join code", value=f"```{code}```", inline=False)

    await interaction.response.send_message(
        content=ping,
        embed=embed,
        view=CopyCodeView(code)
    ) @bot.tree.command(name="modhost", description="Host a modded lobby")
@app_commands.describe(code="6-letter lobby code")
async def modhost_cmd(interaction: discord.Interaction, code: str):
    code = clean_code(code)
    if not code:
        return await interaction.response.send_message(
            "❌ Invalid code. Use 6 letters like `HHHIGG`.",
            ephemeral=True
        )

    modded_lobbies[interaction.user.id] = code

    role = interaction.guild.get_role(MODDED_ROLE_ID)
    ping = role.mention if role else ""

    embed = discord.Embed(
        title="🧩 Modded Lobby Hosted!",
        description=f"Modded lobby hosted by {interaction.user.mention}"
    )
    embed.add_field(name="Join code", value=f"```{code}```", inline=False)

    await interaction.response.send_message(
        content=ping,
        embed=embed,
        view=CopyCodeView(code)
    )

@bot.tree.command(name="endhost", description="End your hosted lobby")
async def endhost_cmd(interaction: discord.Interaction):
    removed = False

    if interaction.user.id in normal_lobbies:
        del normal_lobbies[interaction.user.id]
        removed = True

    if interaction.user.id in modded_lobbies:
        del modded_lobbies[interaction.user.id]
        removed = True

    if not removed:
        return await interaction.response.send_message(
            "You are not hosting any lobbies currently.",
            ephemeral=True
        )

    await interaction.response.send_message(
        f"✅ {interaction.user.mention} ended their lobby."
    )

@bot.tree.command(name="mylobby", description="Show your active lobby")
async def mylobby_cmd(interaction: discord.Interaction):
    normal = normal_lobbies.get(interaction.user.id)
    modded = modded_lobbies.get(interaction.user.id)

    if not normal and not modded:
        return await interaction.response.send_message(
            "You are not hosting any lobbies currently.",
            ephemeral=True
        )

    msg = ""
    if normal:
        msg += f"🛸 Normal lobby: ```{normal}```\n"
    if modded:
        msg += f"🧩 Modded lobby: ```{modded}```"

    await interaction.response.send_message(msg, ephemeral=True)

# ===== RUN =====
bot.run(TOKEN)
