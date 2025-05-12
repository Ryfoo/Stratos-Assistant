import discord
import json
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View
from datetime import datetime
import os
from dotenv import load_dotenv
from scores import get_scores, save_scores, add_point

# Intents & Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

LOG_CHANNEL_ID = 1370777995383537695

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

# --- MATCH BUTTONS VIEW ---
class MatchButtons(View):
    def __init__(self, team1, team2, link, reporter, chat_room, timeout=900): # 15 minutes as a duration
        super().__init__(timeout=timeout)
        self.team1 = team1
        self.team2 = team2
        self.link = link
        self.revealed = False
        self.chat_room = chat_room
        self.reporter = reporter
        self.submitted = False
        self.match_ended = False

    @discord.ui.button(label="Reveal Problem", style=discord.ButtonStyle.primary)
    async def reveal_problem(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.revealed:
            await interaction.response.send_message("Problem has already been revealed.", ephemeral=True)
            return

        self.revealed = True
        await interaction.response.send_message(f"🧠 Problem link: {self.link}", ephemeral=True)
        await self.chat_room.send("🔓 Problem has been revealed! Timer starts now.")
        self.bot_loop = asyncio.create_task(self.match_timeout())

    @discord.ui.button(label="Submit Solution", style=discord.ButtonStyle.success)
    async def submit_solution(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.match_ended:
            await interaction.response.send_message("⚠️ Match already ended.", ephemeral=True)
            return

        user_roles = interaction.user.roles
        awarded_team = None

        if self.team1 in user_roles:
            add_point(str(self.team1.id))
            awarded_team = self.team1
        elif self.team2 in user_roles:
            add_point(str(self.team2.id))
            awarded_team = self.team2
        else:
            await interaction.response.send_message("⛔ You are not part of either team.", ephemeral=True)
            return

        self.submitted = True
        self.match_ended = True

        await interaction.response.send_message(
            f"✅ Submission received. Point awarded to **{awarded_team.name}**!", ephemeral=True
        )

        await self.chat_room.send(
            f"🏁 **{interaction.user.display_name}** submitted the solution.\n"
            f"🎉 Point awarded to **{awarded_team.name}**!"
        )

        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"✅ {interaction.user} submitted a solution. Point awarded to **{awarded_team.name}**."
            )

    async def match_timeout(self):
        await asyncio.sleep(self.timeout)
        if not self.submitted and not self.match_ended:
            self.match_ended = True
            await self.chat_room.send("⌛ Time is up! No team submitted a solution. No points awarded.")
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(f"⏱️ Match between **{self.team1.name}** and **{self.team2.name}** ended with no submission.")


# --- STARTMATCH COMMAND ---
@bot.tree.command(name="startmatch", description="Start a coding match between two teams")
@app_commands.describe(
    team1="Role of Team 1",
    team2="Role of Team 2",
    chat_room="Channel where match will take place",
    link="Problem link (Codewars, LeetCode, etc.)"
)
async def startmatch(interaction: discord.Interaction, team1: discord.Role, team2: discord.Role, chat_room: discord.TextChannel, link: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ You must be an admin to use this command.", ephemeral=True)
        return
    await chat_room.send(
        f"🚨 **Match Started!**\n"
        f"🔴 {team1.mention} vs 🔵 {team2.mention}\n"
        f"🧠 Problem: 🔒🔒🔒\n"
        f"🕐 First to submit gets the point. Good luck!"
    )

    view = MatchButtons(team1, team2, link, interaction.user, chat_room)
    await chat_room.send(view=view)

    await interaction.response.send_message("✅ Match started!", ephemeral=True)

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(
            f"📜 Match started between **{team1.name}** and **{team2.name}** in {chat_room.mention}. Problem: {link}"
        )

# --- CLEAR CHAT COMMAND ---
@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    if amount < 1:
        await ctx.send("Please specify a number greater than 0.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"Deleted {len(deleted)-1} messages.", delete_after=3)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please provide a valid number of messages to delete.")
    else:
        await ctx.send("An error occurred.")

# --- ROLE-BASED ACCESS CHECK ---
@bot.check
async def global_check(ctx):
    allowed_roles = [1370765495195668533, 1370774173030285434]
    user_roles = [role.id for role in ctx.author.roles]
    return any(role in allowed_roles for role in user_roles)


# --- RESET SCORE ----

@bot.tree.command(name="reset_scores", description="Reset all team scores")
async def reset_scores(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ You must be an admin to use this command.", ephemeral=True)
        return

    scores = get_scores()
    for team_id, data in scores.get("teams", {}).items():
        data["points"] = 0
        data["eliminated"] = False
    save_scores(scores)

    await interaction.response.send_message("✅ Scores reset.", ephemeral=True)

# ---- SYNC METHOD ------

@bot.tree.command(name="sync_now", description="Force sync slash commands to this server (admin only)")
async def sync_now(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ You must be an admin to use this command.", ephemeral=True)
        return

    try:
        synced = await bot.tree.sync(guild=interaction.guild)
        await interaction.response.send_message(f"Synced {len(synced)} command(s) to this server.", ephemeral=True)
        print(f"✅ Slash commands synced to guild {interaction.guild.id}")
    except Exception as e:
        await interaction.response.send_message("❌ Failed to sync commands.", ephemeral=True)
        print(f"❌ Sync failed: {e}")

# --- LOCKING ROLES -----

@bot.event
async def on_member_update(before, after):
    # Role IDs for team roles (replace these with the actual IDs of your team roles)
    team_role_ids = [1370766001259548774, 1370766197460566228, 1370766303509479514, 1370766348392730685,1370766400636850336, 1370766434656845917, 1370766521873207316 , 1370766555545075863, 1370766590123049011 ,  1370766662864867478 , 1370766700131385404 , 1370766728652652645, 1370766758461571115 , 1370766792821313629 ,  1370766832268476496 , 1370766877667622983 ]  # Use your actual Team Role IDs here
    locked_role_id = 1371094936513941654
    
    # Get the Locked role object using its ID
    locked_role = discord.utils.get(after.guild.roles, id=locked_role_id)

    # Loop through the roles of the member
    for role in after.roles:
        if role.id in team_role_ids:
            # If the user has a team role, assign the "Locked" role if they don't already have it
            if locked_role not in after.roles:
                await after.add_roles(locked_role)
                await after.send(f"You've been locked to your team role: {role.name}.")
                break  # Stop checking once the "Locked" role has been added


# --- ENV SETUP ---
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(DISCORD_TOKEN)
