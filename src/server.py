from quart import Quart, request, redirect
import asyncio
from token_manager import get_user_tokens, get_github_id, persist_tokens, get_discord_id
import discord
import traceback
import os

app = Quart('')
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

@app.before_serving
async def before_serving():
  loop = asyncio.get_event_loop()
  await client.login(os.getenv("DISCORD_TOKEN"))
  loop.create_task(client.connect())

@app.route('/', methods=['GET'])
async def home():
  try:
    # code = request.args["code"]
    # user_tokens = get_user_tokens(code)
    # discord_id = get_discord_id(user_tokens['access_token'])
    # github_id = get_github_id(user_tokens['access_token'])
    # persist_tokens(user_tokens['access_token'], user_tokens['refresh_token'], github_id, discord_id)

    user = await client.fetch_user(637512076084117524)
    await user.send("You have been added to the list of contributors!")
    return redirect("https://discord.com/channels/973851473131761674")
  except Exception as e:
    print(traceback.format_exc())
    return {"status": "Failed to Register"}

app.run(host='0.0.0.0', port=8080, debug=True)