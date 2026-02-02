import os
import re
import discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")

NORMAL_ROLE_ID = 1467862590670639249
MODDED_ROLE_ID = 1467868524197183508

intents = discord.Intents.default()
intents.message_content=True 
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# user_id -> {"normal": str | None, "modded": str | None}
active_lobbies = {}

def clean_code(code: str) -> str | None:
    code = code.strip().upper()
    return code if re.fullmatch(r"[A-Z]{6}", code) else None

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

@tree.command(name="help", description="Show Clover Bot commands")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Clover Bot Commands",
        description="Use slash commands below 👇"
    )
    embed.add_field(name="/host CODE", value="Host a normal lobby", inline=False)
    embed.add_field(name="/modhost CODE", value="Host a modded lobby", inline=False)
    embed.add_field(name="/endhost", value="End your lobby", inline=False)
    embed.add_field(name="/mylobby", value="Show your lobby", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="host", description="Host a normal lobby")
@app_commands.describe(code="6-letter lobby code")
async def host(interaction: discord.Interaction, code: str):
    code = clean_code(code)
    if not code:
        return await interaction.response.send_message(
            "❌ Invalid code. Use 6 letters like `HHHIGG`.", ephemeral=True
        )

    user = active_lobbies.setdefault(interaction.user.id, {"normal": None, "modded": None})

    if user["normal"]:
        return await interaction.response.send_message(
            f"🚨 You are already hosting a normal lobby: `{user['normal']}`",
            ephemeral=True
        )

    user["normal"] = code

    role = interaction.guild.get_role(NORMAL_ROLE_ID) if interaction.guild else None
    ping = role.mention if role else ""

    embed = discord.Embed(
        title="🛸 Lobby Hosted!",
        description=f"{interaction.user.mention} is hosting a lobby"
    )
    embed.add_field(name="Join code", value=f"`{code}`", inline=False)
    embed.set_footer(text="Use /endhost to close your lobby")

    await interaction.response.send_message(content=ping, embed=embed)

@tree.command(name="modhost", description="Host a modded lobby")
@app_commands.describe(code="6-letter lobby code")
async def modhost(interaction: discord.Interaction, code: str):
    code = clean_code(code)
    if not code:
        return await interaction.response.send_message(
            "❌ Invalid code. Use 6 letters like `HHHIGG`.", ephemeral=True
        )

    user = active_lobbies.setdefault(interaction.user.id, {"normal": None, "modded": None})

    if user["modded"]:
        return await interaction.response.send_message(
            f"🚨 You are already hosting a modded lobby: `{user['modded']}`",
            ephemeral=True
        )

    user["modded"] = code

    role = interaction.guild.get_role(MODDED_ROLE_ID) if interaction.guild else None
    ping = role.mention if role else ""

    embed = discord.Embed(
        title="🧪 Modded Lobby Hosted!",
        description=f"{interaction.user.mention} is hosting a modded lobby"
    )
    embed.add_field(name="Join code", value=f"`{code}`", inline=False)
    embed.set_footer(text="Use /endhost to close your lobby")
    await interaction.response.send_message(content=ping, embed=embed)

@tree.command(name="endhost", description="End your lobby")
async def endhost(interaction: discord.Interaction):
    user = active_lobbies.get(interaction.user.id)

    if not user or (not user["normal"] and not user["modded"]):
        return await interaction.response.send_message(
            "❌ You are not hosting any lobbies.", ephemeral=True
        )

    ended = []
    if user["normal"]:
        ended.append(user["normal"])
        user["normal"] = None
    if user["modded"]:
        ended.append(user["modded"])
        user["modded"] = None

    await interaction.response.send_message(
        f"✅ Ended lobby/lobbies: {', '.join(f'`{c}`' for c in ended)}"
    )

@tree.command(name="mylobby", description="Show your active lobby")
async def mylobby(interaction: discord.Interaction):
    user = active_lobbies.get(interaction.user.id)

    if not user or (not user["normal"] and not user["modded"]):
        return await interaction.response.send_message(
            "❌ You are not hosting any lobbies.", ephemeral=True
        )

    msg = []
    if user["normal"]:
        msg.append(f"🛸 Normal lobby: `{user['normal']}`")
    if user["modded"]:
        msg.append(f"🧪 Modded lobby: `{user['modded']}`")

    await interaction.response.send_message("\n".join(msg), ephemeral=True)

client.run(TOKEN)



