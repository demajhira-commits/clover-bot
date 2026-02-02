import os
import re
import discord
from discord.ext import commands

# =====================
# CONFIG
# =====================
PREFIX = "cl!"

HOSTED_ROLE_ID = 1467862590670639249
MODDED_ROLE_ID = 1467868524197183508

TOKEN = os.getenv("DISCORD_TOKEN")

# =====================
# BOT SETUP
# =====================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

active_lobbies = {}  # user_id -> (code, modded_bool)

# =====================
# HELPERS
# =====================
def clean_lobby_code(code: str) -> str | None:
    code = code.strip().upper()
    return code if re.fullmatch(r"[A-Z]{6}", code) else None


class CopyCodeView(discord.ui.View):
    def __init__(self, code: str):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="Copy code",
                emoji="📋",
                style=discord.ButtonStyle.secondary,
                copy_text=code
            )
        )

# =====================
# EVENTS
# =====================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# =====================
# COMMANDS
# =====================
@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I am alive 🤖")

@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="Clover Bot Commands",
        description=f"Prefix: `{PREFIX}`"
    )
    embed.add_field(
        name=f"{PREFIX}host <CODE>",
        value=f"Host a normal lobby\nExample: `{PREFIX}host HHHIGG`",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}hostmod <CODE>",
        value="Host a **modded** lobby",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}endhost",
        value="End your hosted lobby",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}mylobby",
        value="Show your current lobby",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
async def host(ctx, code: str):
    await _host_lobby(ctx, code, modded=False)

@bot.command()
async def hostmod(ctx, code: str):
    await _host_lobby(ctx, code, modded=True)

async def _host_lobby(ctx, code: str, modded: bool):
    lobby_code = clean_lobby_code(code)
    if not lobby_code:
        await ctx.send("❌ Code must be **6 letters** (example: HHHIGG)")
        return

    active_lobbies[ctx.author.id] = (lobby_code, modded)

    role_ping = ""
    if ctx.guild:
        role_id = MODDED_ROLE_ID if modded else HOSTED_ROLE_ID
        role = ctx.guild.get_role(role_id)
        if role:
            role_ping = role.mention

    embed = discord.Embed(
        title="🛸 Lobby Hosted!",
        description=f"Lobby hosted by {ctx.author.mention}"
    )
    embed.add_field(name="Join code", value=f"`{lobby_code}`", inline=False)
    embed.set_footer(text=f"Use {PREFIX}endhost to close your lobby")

    # IMPORTANT: ping must be OUTSIDE the embed
    await ctx.send(
        content=role_ping,
        embed=embed,
        view=CopyCodeView(lobby_code)
    )

@bot.command()
async def endhost(ctx):
    if ctx.author.id not in active_lobbies:
        await ctx.send("You are not hosting a lobby.")
        return

    code, _ = active_lobbies.pop(ctx.author.id)
    await ctx.send(f"✅ {ctx.author.mention} ended lobby `{code}`.")

@bot.command()
async def mylobby(ctx):
    data = active_lobbies.get(ctx.author.id)
    if not data:
        await ctx.send("You are not hosting a lobby.")
        return

    code, modded = data
    tag = "🧪 Modded" if modded else "🎮 Normal"
    await ctx.send(f"{tag} lobby code: `{code}`")

# =====================
# RUN
# =====================
bot.run(TOKEN)
