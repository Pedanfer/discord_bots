import os
import time
from discord import Client, Intents, Message, TextChannel

TOKEN = os.environ.get('DISCORD_TOKEN')

# Set the cooldown time in seconds (e.g., 5 minutes = 300 seconds)
COOLDOWN_TIME = 300

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

    user_id = message.author.id

    if user_id in user_cooldowns:
        last_post_time = user_cooldowns[user_id]
        time_elapsed = time.time() - last_post_time

        if time_elapsed < COOLDOWN_TIME:
            remaining_time = COOLDOWN_TIME - time_elapsed
            await Message.delete(message)
            await TextChannel.send(message.channel, f"{message.author.mention}, please wait {remaining_time:.2f} seconds before posting again.", delete_after=5)
            return

    user_cooldowns[user_id] = time.time()

Client.run(client, TOKEN)