import os
import re
import discord
from discord.ext import commands

# ===== CONFIG =====
PREFIX = "cl!"

NORMAL_ROLE_ID = 1467862590670639249
MODDED_ROLE_ID = 1467868524197183508

AUTO_REPLY_TIMESTAMP = "<t:1770060600:t>"
LOBBY_CHANNEL_NAME = "<#1467841323678699582>"

# ==================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

# user_id -> {"type": "normal/modded", "code": "XXXXXX"}
active_lobbies = {}


def clean_code(code: str) -> str | None:
    code = code.strip().upper()
    return code if re.fullmatch(r"[A-Z]{6}", code) else None


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# ================== HELP ==================
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Clover Bot Commands",
        description=f"Prefix: `{PREFIX}`"
    )

    embed.add_field(
        name=f"`{PREFIX}host CODE`",
        value="Host a **normal** lobby\nExample:\n```cl!host HHHIGG```",
        inline=False
    )

    embed.add_field(
        name=f"`{PREFIX}modhost CODE`",
        value="Host a **modded** lobby\n```cl!modhost HHHIGG```",
        inline=False
    )

    embed.add_field(
        name=f"`{PREFIX}endhost`",
        value="End your hosted lobby",
        inline=False
    )

    embed.add_field(
        name=f"`{PREFIX}mylobby`",
        value="Show your active lobby",
        inline=False
    )

    await ctx.send(embed=embed)


# ================== HOST ==================
async def do_host(ctx, code: str, lobby_type: str):
    lobby_code = clean_code(code)
    if not lobby_code:
        await ctx.send("❌ Invalid code. Use **6 letters** like:\n```HHHIGG```")
        return

    existing = active_lobbies.get(ctx.author.id)

    if existing and existing["type"] == lobby_type:
        await ctx.send(
            f"⚠️ You are already hosting a **{lobby_type}** lobby!\n"
            f"Code:\n```{existing['code']}```"
        )
        return

    active_lobbies[ctx.author.id] = {
        "type": lobby_type,
        "code": lobby_code
    }

    role_id = NORMAL_ROLE_ID if lobby_type == "normal" else MODDED_ROLE_ID
    role = ctx.guild.get_role(role_id) if ctx.guild else None
    ping = role.mention if role else ""

    embed = discord.Embed(
        title="🛸 Lobby Hosted!",
        description=f"Hosted by {ctx.author.mention}"
    )

    embed.add_field(
        name="Join Code",
        value=f"```{lobby_code}```",
        inline=False
    )

    embed.set_footer(text=f"Use {PREFIX}endhost to close your lobby")

    await ctx.send(content=ping, embed=embed)


@bot.command()
async def host(ctx, code: str):
    await do_host(ctx, code, "normal")


@bot.command()
async def modhost(ctx, code: str):
    await do_host(ctx, code, "modded")


# ================== END ==================
@bot.command()
async def endhost(ctx):
    if ctx.author.id not in active_lobbies:
        await ctx.send("❌ You are not hosting any lobbies currently.")
        return

    ended = active_lobbies.pop(ctx.author.id)
    await ctx.send(
        f"✅ {ctx.author.mention} ended their **{ended['type']}** lobby."
    )


# ================== MY LOBBY ==================
@bot.command()
async def mylobby(ctx):
    lobby = active_lobbies.get(ctx.author.id)
    if not lobby:
        await ctx.send("❌ You are not hosting any lobbies currently.")
        return

    await ctx.send(
        f"🛸 Your **{lobby['type']}** lobby code:\n```{lobby['code']}```"
    )


# ================== AUTO REPLY ==================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if "is someone hosting" in message.content.lower():
        await message.channel.send(
            f"We usually host at {AUTO_REPLY_TIMESTAMP},\n"
            f"but you can always check {LOBBY_CHANNEL_NAME} for current lobbies!"
        )# ================== RUN ==================
bot.run(os.getenv("DISCORD_TOKEN"))
