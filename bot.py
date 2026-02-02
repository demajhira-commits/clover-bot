import os
import re
import discord
from discord.ext import commands

PREFIX = "cl!"

HOSTED_ROLE_ID = 1467862590670639249
MODDED_ROLE_ID = 1467868524197183508

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

active_lobbies = {}  # user_id -> (code, is_modded)


def clean_lobby_code(code: str) -> str:
    code = code.strip().upper()
    return code if re.fullmatch(r"[A-Z]{6}", code) else ""


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    embed = discord.Embed(
        title="Clover Bot Commands",
        description=f"Prefix: `{PREFIX}`",
    )
    embed.add_field(
        name=f"{PREFIX}host <CODE>",
        value=f"Host a normal lobby\nExample: `{PREFIX}host HHHIGG`",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}modhost <CODE>",
        value=f"Host a modded lobby",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}endhost",
        value="End your hosted lobby",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}mylobby",
        value="Show your active lobby",
        inline=False
    )
    await ctx.send(embed=embed)


async def send_lobby(ctx, code, is_modded):
    active_lobbies[ctx.author.id] = (code, is_modded)

    role_ping = ""
    role_id = MODDED_ROLE_ID if is_modded else HOSTED_ROLE_ID

    if ctx.guild:
        role = ctx.guild.get_role(role_id)
        if role:
            role_ping = role.mention + " "

    embed = discord.Embed(
        title="🛸 Lobby Hosted!",
        description=f"Lobby hosted by {ctx.author.mention}",
    )

    embed.add_field(
        name="Join code (tap to copy)",
        value=f"```{code}```",
        inline=False
    )

    embed.set_footer(text=f"Use {PREFIX}endhost to close your lobby.")

    await ctx.send(role_ping, embed=embed)


@bot.command(name="host")
async def host_cmd(ctx: commands.Context, code: str):
    lobby_code = clean_lobby_code(code)
    if not lobby_code:
        return await ctx.send("❌ Use a valid 6-letter code.")

    await send_lobby(ctx, lobby_code, is_modded=False)


@bot.command(name="modhost")
async def modhost_cmd(ctx: commands.Context, code: str):
    lobby_code = clean_lobby_code(code)
    if not lobby_code:
        return await ctx.send("❌ Use a valid 6-letter code.")

    await send_lobby(ctx, lobby_code, is_modded=True)


@bot.command(name="endhost")
async def endhost_cmd(ctx: commands.Context):
    if ctx.author.id not in active_lobbies:
        return await ctx.send("You are not hosting a lobby.")

    code, _ = active_lobbies.pop(ctx.author.id)
    await ctx.send(f"✅ {ctx.author.mention} ended lobby `{code}`.")


@bot.command(name="mylobby")
async def mylobby_cmd(ctx: commands.Context):
    data = active_lobbies.get(ctx.author.id)
    if not data:
        return await ctx.send("You are not hosting a lobby.")

    code, is_modded = data
    lobby_type = "Modded" if is_modded else "Normal"
    await ctx.send(f"🛸 **{lobby_type} lobby code:** ```{code}```")


bot.run(os.getenv("DISCORD_TOKEN"))
