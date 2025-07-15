import discord
import aiohttp
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_USER_LOGIN = os.getenv("TWITCH_USER_LOGIN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

access_token = None
is_live = False
live_message = None

async def get_twitch_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as resp:
            data = await resp.json()
            return data["access_token"]

async def check_live():
    global access_token, is_live, live_message
    if not access_token:
        access_token = await get_twitch_token()

    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {access_token}"
    }

    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USER_LOGIN}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            stream = data["data"]
            channel = client.get_channel(CHANNEL_ID)

            if stream and not is_live:
                is_live = True
                live_message = await channel.send(f"🔴 {TWITCH_USER_LOGIN} est en live ! https://twitch.tv/{TWITCH_USER_LOGIN}")
            elif not stream and is_live:
                is_live = False
                if live_message:
                    await live_message.delete()
                    live_message = None

async def loop():
    await client.wait_until_ready()
    while not client.is_closed():
        await check_live()
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")
    client.loop.create_task(loop())

client.run(TOKEN)
