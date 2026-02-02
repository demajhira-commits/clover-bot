import os
import re
import discord
from discord.ext import commands

# ====== SETTINGS ======
PREFIX = "cl!"

HOSTED_ROLE_ID = 1467862590670639249   # Hosted Lobbies ping
MODDED_ROLE_ID = 1467868524197183508   # Modded Lobbies ping

# ====== BOT SETUP ======
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# store active lobby per user (resets if bot restarts)
active_lobbies = {}  # user_id -> {"code": "ABCDEF", "type": "normal"/"modded"}

# ====== HELPERS ======
def clean_lobby_code(code: str) -> str:
    code = code.strip().upper()
    return code if re.fullmatch(r"[A-Z]{6}", code) else ""

def get_ping_text(ctx: commands.Context, lobby_type: str) -> str:
    """Returns role mention if possible, otherwise empty string."""
    if not ctx.guild:
        return ""

    role_id = HOSTED_ROLE_ID if lobby_type == "normal" else MODDED_ROLE_ID
    role = ctx.guild.get_role(role_id)
    if not role:
        return ""

    # Safer: only ping if role is mentionable OR bot has permission to mention roles
    # (Even if it's not mentionable, sometimes bots with perms can still mention - but this avoids headaches)
    if role.mentionable:
        return role.mention + " "
    return ""

def lobby_embed(code: str, host: discord.Member, lobby_type: str) -> discord.Embed:
    title = "🛸 Lobby Hosted!" if lobby_type == "normal" else "🧩 Modded Lobby Hosted!"
    embed = discord.Embed(
        title=title,
        description=f"Lobby hosted by {host.mention}",
    )
    embed.add_field(name="Join code", value=f"```{code}```", inline=False)  # easy copy
    embed.set_footer(text=f"Use {PREFIX}endhost to close your lobby.")
    return embed

# ====== EVENTS ======
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (prefix: {PREFIX})")

@bot.event
async def on_command_error(ctx, error):
    # Ignore unknown commands
    if isinstance(error, commands.CommandNotFound):
        return

    # Cooldown message
    if isinstance(error, commands.CommandOnCooldown):
        return await ctx.send(f"⏳ Slow down! Try again in {error.retry_after:.1f}s.")
# Missing argument message
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send(f"❌ Missing info. Try `{PREFIX}{ctx.command} <CODE>`")

    # Show other errors safely (won’t crash Railway)
    await ctx.send(f"❌ Error: `{type(error).__name__}` — {error}")

# ====== COMMANDS ======
@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    embed = discord.Embed(
        title="Clover Bot Commands",
        description=f"Prefix: `{PREFIX}`",
    )
    embed.add_field(
        name=f"{PREFIX}host <CODE>",
        value="Host a normal Among Us lobby.\nExample: `cl!host HHHIGG`",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}mhost <CODE>",
        value="Host a **modded** lobby.\nExample: `cl!mhost HHHIGG`",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}mylobby",
        value="Shows your current hosted lobby (if any).",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}endhost",
        value="End your currently hosted lobby.",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command(name="host")
@commands.cooldown(1, 5, commands.BucketType.user)
async def host_cmd(ctx: commands.Context, code: str):
    lobby_code = clean_lobby_code(code)
    if not lobby_code:
        return await ctx.send(f"❌ Invalid code. Use 6 letters like `{PREFIX}host HHHIGG`.")

    active_lobbies[ctx.author.id] = {"code": lobby_code, "type": "normal"}

    ping = get_ping_text(ctx, "normal")
    embed = lobby_embed(lobby_code, ctx.author, "normal")
    await ctx.send(content=ping, embed=embed)

@bot.command(name="mhost")
@commands.cooldown(1, 5, commands.BucketType.user)
async def modded_host_cmd(ctx: commands.Context, code: str):
    lobby_code = clean_lobby_code(code)
    if not lobby_code:
        return await ctx.send(f"❌ Invalid code. Use 6 letters like `{PREFIX}mhost HHHIGG`.")

    active_lobbies[ctx.author.id] = {"code": lobby_code, "type": "modded"}

    ping = get_ping_text(ctx, "modded")
    embed = lobby_embed(lobby_code, ctx.author, "modded")
    await ctx.send(content=ping, embed=embed)

@bot.command(name="mylobby")
async def mylobby_cmd(ctx: commands.Context):
    data = active_lobbies.get(ctx.author.id)
    if not data:
        return await ctx.send("You’re not hosting a lobby right now.")

    lobby_type = data["type"]
    code = data["code"]
    label = "modded" if lobby_type == "modded" else "normal"
    await ctx.send(f"🛸 Your active **{label}** lobby code is `{code}`.")

@bot.command(name="endhost")
async def endhost_cmd(ctx: commands.Context):
    data = active_lobbies.pop(ctx.author.id, None)
    if not data:
        return await ctx.send("You’re not hosting a lobby right now.")

    await ctx.send(f"✅ {ctx.author.mention} ended lobby **{data['code']}**.")

# ====== RUN ======
token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError("DISCORD_TOKEN environment variable is missing.")
bot.run(token
)
