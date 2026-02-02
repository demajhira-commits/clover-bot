import os
import re
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

NORMAL_ROLE_ID = 1467862590670639249
MODDED_ROLE_ID = 1467868524197183508

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

tree = bot.tree

# user_id -> {"normal": code, "modded": code}
active_lobbies = {}

CODE_REGEX = re.compile(r"^[A-Z]{6}$")


def clean_code(code: str) -> str | None:
    code = code.strip().upper()
    return code if CODE_REGEX.match(code) else None


@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")


# ---------- HOST NORMAL ----------
@tree.command(name="host", description="Host a normal Among Us lobby")
@app_commands.describe(code="6-letter lobby code")
async def host(interaction: discord.Interaction, code: str):
    code = clean_code(code)
    if not code:
        return await interaction.response.send_message(
            "❌ Invalid code. Use **6 letters** like `HHHIGG`.",
            ephemeral=True
        )

    user_lobbies = active_lobbies.setdefault(interaction.user.id, {})
    if "normal" in user_lobbies:
        return await interaction.response.send_message(
            "🚫 You’re already hosting a **normal** lobby!",
            ephemeral=True
        )

    user_lobbies["normal"] = code

    role = interaction.guild.get_role(NORMAL_ROLE_ID)
    ping = role.mention if role else ""

    embed = discord.Embed(
        title="🛸 Lobby Hosted!",
        description=f"{ping}\nHosted by {interaction.user.mention}",
    )
    embed.add_field(
        name="Join code",
        value=f"`{code}`",  # <-- TAP TO COPY WORKS
        inline=False
    )
    embed.set_footer(text="Use /endhost to close your lobby")

    await interaction.response.send_message(embed=embed)


# ---------- HOST MODDED ----------
@tree.command(name="modhost", description="Host a modded Among Us lobby")
@app_commands.describe(code="6-letter lobby code")
async def modhost(interaction: discord.Interaction, code: str):
    code = clean_code(code)
    if not code:
        return await interaction.response.send_message(
            "❌ Invalid code. Use **6 letters** like `HHHIGG`.",
            ephemeral=True
        )

    user_lobbies = active_lobbies.setdefault(interaction.user.id, {})
    if "modded" in user_lobbies:
        return await interaction.response.send_message(
            "🚫 You’re already hosting a **modded** lobby!",
            ephemeral=True
        )

    user_lobbies["modded"] = code

    role = interaction.guild.get_role(MODDED_ROLE_ID)
    ping = role.mention if role else ""

    embed = discord.Embed(
        title="🧪 Modded Lobby Hosted!",
        description=f"{ping}\nHosted by {interaction.user.mention}",
    )
    embed.add_field(
        name="Join code",
        value=f"`{code}`",
        inline=False
    )
    embed.set_footer(text="Use /endhost to close your lobby")

    await interaction.response.send_message(embed=embed)


# ---------- END HOST ----------
@tree.command(name="endhost", description="End your hosted lobby/lobbies")
async def endhost(interaction: discord.Interaction):
    user_lobbies = active_lobbies.pop(interaction.user.id, None)

    if not user_lobbies:
        return await interaction.response.send_message(
            "❌ You are not hosting any lobbies.",
            ephemeral=True
        )

    ended = ", ".join(user_lobbies.keys())
    await interaction.response.send_message(
        f"✅ {interaction.user.mention} ended their **{ended}** lobby/lobbies."
    )


# ---------- MY LOBBY ----------
@tree.command(name="mylobby", description="Check your active lobby")
async def mylobby(interaction: discord.Interaction):
    user_lobbies = active_lobbies.get(interaction.user.id)

    if not user_lobbies:
        return await interaction.response.send_message(
            "❌ You are not hosting any lobbies currently.",
            ephemeral=True
        )

    lines = []
    if "normal" in user_lobbies:
        lines.append(f"🛸 Normal: `{user_lobbies['normal']}`")
    if "modded" in user_lobbies:
        lines.append(f"🧪 Modded: `{user_lobbies['modded']}`")

    await interaction.response.send_message("\n".join(lines), ephemeral=True)

bot.run(TOKEN)


