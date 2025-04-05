import os
import time
from discord import Client, Intents, Message, TextChannel

TOKEN = os.getenv('DISCORD_TOKEN')

# {channel_id: cooldown_minutes}
CHANNEL_SETTINGS = {}

intents = Intents.default()
intents.message_content = True
intents.members = True

client = Client(intents=intents)
user_cooldowns = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

    # Check if message is a command
    if message.content.startswith('/silencer'):
        await handle_command(message)
        return

    # Skip if channel not configured
    if message.channel.id not in CHANNEL_SETTINGS:
        return

    channel_cooldown = CHANNEL_SETTINGS[message.channel.id]
    user_id = message.author.id
    current_time = time.time()

    if user_id in user_cooldowns.get(message.channel.id, {}):
        last_post_time = user_cooldowns[message.channel.id][user_id]
        elapsed_minutes = (current_time - last_post_time) / 60

        if elapsed_minutes < channel_cooldown:
            remaining_minutes = channel_cooldown - elapsed_minutes
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, please wait {remaining_minutes:.1f} minutes before posting again in this channel.",
                delete_after=10
            )
            return

    # Initialize channel in cooldown tracker if needed
    if message.channel.id not in user_cooldowns:
        user_cooldowns[message.channel.id] = {}
    
    user_cooldowns[message.channel.id][user_id] = current_time

async def handle_command(message: Message):
    """Process admin commands"""
    if not message.author.guild_permissions.administrator:
        return

    parts = message.content.split()
    
    if len(parts) < 2:
        # Show help
        await message.channel.send(
            "**Silencer Bot Commands:**\n"
            "`/silencer add #channel 5` - Set 5 min cooldown in channel\n"
            "`/silencer remove #channel` - Remove channel restrictions\n"
            "`/silencer list` - Show current settings"
        )
        return
    
    if parts[1] == "list":
        if not CHANNEL_SETTINGS:
            await message.channel.send("No channels are currently configured")
            return
            
        settings = "\n".join(
            f"<#{cid}>: {cooldown} minutes" 
            for cid, cooldown in CHANNEL_SETTINGS.items()
        )
        await message.channel.send(f"**Current Settings:**\n{settings}")
    
    elif parts[1] == "add" and len(parts) >= 4:
        try:
            channel_id = int(parts[2].strip('<#>'))
            cooldown = float(parts[3])
            CHANNEL_SETTINGS[channel_id] = cooldown
            await message.channel.send(
                f"Configured <#{channel_id}> with {cooldown} minute cooldown"
            )
        except (ValueError, IndexError):
            await message.channel.send("Invalid format. Use: `/silencer add #channel minutes`")
    
    elif parts[1] == "remove" and len(parts) >= 3:
        channel_id = int(parts[2].strip('<#>'))
        if channel_id in CHANNEL_SETTINGS:
            del CHANNEL_SETTINGS[channel_id]
            if channel_id in user_cooldowns:
                del user_cooldowns[channel_id]
            await message.channel.send(f"Removed restrictions from <#{channel_id}>")
        else:
            await message.channel.send("This channel isn't configured")

client.run(TOKEN)