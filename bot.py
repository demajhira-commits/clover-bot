import os
import re
import discord
from discord.ext import commands

PREFIX = "cl!"
HOSTED_ROLE_ID = 1467862590670639249  # your Hosted Lobbies role ID

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

active_lobbies = {}  # user_id -> code


def clean_lobby_code(code: str) -> str:
    code = code.strip().upper()
    return code if re.fullmatch(r"[A-Z]{6}", code) else ""


class CopyCodeView(discord.ui.View):
    def init(self, code: str):
        super().init(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="Copy code",
                emoji="📋",
                style=discord.ButtonStyle.secondary,
                copy_text=code
            )
        )


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    embed = discord.Embed(
        title="Clover Bot Commands",
        description=f"Prefix: {PREFIX}",
    )
    embed.add_field(
        name=f"{PREFIX}host <CODE>",
        value=f"Host a lobby.\nExample: {PREFIX}host HHHIGG",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}endhost",
        value="End your currently hosted lobby.",
        inline=False
    )
    embed.add_field(
        name=f"{PREFIX}mylobby",
        value="Shows your hosted lobby code (if any).",
        inline=False
    )
    await ctx.send(embed=embed)


@bot.command(name="host")
@commands.cooldown(1, 10, commands.BucketType.user)
async def host_cmd(ctx: commands.Context, code: str):
    lobby_code = clean_lobby_code(code)
    if not lobby_code:
        return await ctx.send(
            f"❌ Invalid code. Use 6 letters like {PREFIX}host HHHIGG."
        )

    active_lobbies[ctx.author.id] = lobby_code

    ping_text = ""
    if HOSTED_ROLE_ID and ctx.guild:
        role = ctx.guild.get_role(HOSTED_ROLE_ID)
        if role:
            ping_text = role.mention + " "

    embed = discord.Embed(
        title="🛸 Lobby Hosted!",
        description=f"{lobby_code} lobby hosted by {ctx.author.mention}",
    )
    embed.add_field(name="Join code", value=f"{lobby_code}", inline=False)
    embed.set_footer(text=f"Use {PREFIX}endhost to close your lobby.")

    await ctx.send(ping_text, embed=embed, view=CopyCodeView(lobby_code))


@host_cmd.error
async def host_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Slow down! Try again in {error.retry_after:.1f}s.")
    else:
        raise error


@bot.command(name="endhost")
async def endhost_cmd(ctx: commands.Context):
    if ctx.author.id not in active_lobbies:
        return await ctx.send("You’re not hosting a lobby right now.")
    code = active_lobbies.pop(ctx.author.id)
    await ctx.send(f"✅ {ctx.author.mention} ended lobby {code}.")


@bot.command(name="mylobby")
async def mylobby_cmd(ctx: commands.Context):
    code = active_lobbies.get(ctx.author.id)
    if not code:
        return await ctx.send("You’re not hosting a lobby right now.")
    await ctx.send(f"🛸 Your active lobby code is {code}.")


bot.run(os.getenv("DISCORD_TOKEN"))
