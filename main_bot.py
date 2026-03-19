import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

print(f"Starting Bot1...")

Token=os.getenv("Discord_Token1")

intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix="=",intents=intents)
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync() 
    print("bot permission:",list(bot.guilds)[0].me.guild_permissions)


slots = []
scrim_open=False
scrim_info={}
Max_slots=0
room_channel = None
slot_message = None


def create_scrim_info(game,time,host,max_slot,channel_name,user):

    embed = discord.Embed(title=f"🔥 {game} Scrims is now open 🔥",
                          description=f"Host: {host}\nTime: {time}\nSlots: {max_slot}\nChannel: {channel_name}\n",
                          color=discord.Color.gold())
    embed.set_footer(text=f"Scrim opened by {user}",icon_url=user.avatar.url if user.avatar else None)
    return embed

@bot.event

async def on_message(message):
    global scrim_open
    global slots
    global slot_message

    team = message.content

    if message.author.bot:
        return
    if not scrim_open:
        await message.channel.send(f" {team} Sorry Scrims are not started yet")
        return
    if "@" in message.content:
        if len(slots) >= Max_slots:
            await message.channel.send("Sorry, all slots are filled. Please wait for the next scrim.")

            embed = discord.Embed(title=f"✅ Scrim is Full 🔥",description=f"All slots have been filled.",color=discord.Color.green())
            final_text =""
            for i, team in enumerate(slots):
                final_text += f"Slot {i+1}: {team}\n"

            embed.add_field(name="Registered Teams:", value=final_text, inline=False)
            await room_channel.send(embed=embed)
            await room_channel.send(f" # IDP will be given here, please maitain the slotlist, else you will be kicked out of the lobby, Thank you!!")
            return
        if team in slots:
            await message.channel.send(f"{team} is already registered.")
            return 
        slots.append(team)
        slot_number = len(slots)

        

        if room_channel is None:
            await message.channel.send("Error: Room channel not found. Please contact the administrator.")
            return
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel = True
        overwrite.send_messages = True
        await room_channel.set_permissions(message.author,overwrite=overwrite)
        await message.add_reaction("✅")
        await room_channel.send(f"Welcome, {team}!")

        return
    else:
        await message.channel.send(f" {team} Invalid team name. Please use a valid team name.") 


@bot.tree.command(name="ping",description="Check if the Bot is working!!")
async def ping(interaction: discord.interactions):
    await interaction.response.send_message("Bot is working, PURO CHUMU😘 !!")


@bot.tree.command(name="open",description="Open a new Scim(s)")
async def open(interaction : discord.interactions, game: str,time:str,host:str,slots:int,channel_name: str):
    await interaction.response.defer()
    global scrim_open
    global Max_slots
    global scrim_info
    global room_channel
    global slot_message

    scrim_open = True
    Max_slots = slots
    
    guild = interaction.guild
    overwrites = {guild.default_role:discord.PermissionOverwrite(view_channel=False),guild.me:discord.PermissionOverwrite(view_channel=True)}
    room_channel = await guild.create_text_channel(name=channel_name,overwrites=overwrites)
    await room_channel.send(embed=create_scrim_info(game, time, host, slots, channel_name,interaction.user))
    await interaction.followup.send(f"Scrims opened succesfully")

@bot.tree.command(name="slotlist",description="see the currrent slotlist")
async def open(interaction : discord.Interaction):
    if not scrim_open:
        await interaction.response.send_message(f" Sorry Scrims are not started yet")
        return

    slot_text = ""
    for i in range(Max_slots):
        if i < len(slots):
            slot_text += f"Slot {i+1}: {slots[i]}\n"
        else:
            slot_text += f"Slot {i+1}: Slot still available❤\n"

    embed = discord.Embed(title=f"🔥 Current Slotlist 🔥",description=f" {slot_text} ",color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)
@bot.tree.command(name="close",description="Close the registration")
async def close(interaction : discord.Interaction):
    global scrim_open
    global slots
    global Max_slots

    if not scrim_open:
        await interaction.response.send_message(f" Sorry Scrims are already closed!!")
        return

    scrim_open = False
    slots = []
    Max_slots = 0
    embed=discord.Embed(title=f"Scrims Closed",description=f"Scrim registration is now closed. Good luck to all participants!",color=discord.Color.red())
    await interaction.response.send_message(embed=embed)
@bot.tree.command(name="cancel",description="Cancel your registration")
async def cancel(interaction : discord.Interaction,team_name:str):
    await interaction.response.defer()
    global slots
    global slot_message

    if not scrim_open:
        await interaction.response.send_message(f" Sorry Scrims are not started yet")
        return

    found_team = None

    if team_name in slots:
        slots.remove(team_name)

    await interaction.followup.send(f"Your registration for {team_name} has been cancelled.")


if __name__ == "__main__":
    print(f"Bot is now running...")
bot.run(Token)