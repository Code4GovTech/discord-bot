from typing import Optional
import discord
from discord.ext import commands
import os, sys
import asyncio
from discord.utils import MISSING
import dotenv

#Since there are user defined packages, adding current directory to python path
current_directory = os.getcwd()
sys.path.append(current_directory)

dotenv.load_dotenv(".env")

# class GithubAuthModal(discord.ui.Modal):
# def __init__(self, *,userID, title: str = None, timeout: float | None = None, custom_id: str = None) -> None:
#     super().__init__(title=title, timeout=timeout, custom_id=custom_id)
#     self.add_item(discord.ui.Button(label='Authenticate Github', style=discord.ButtonStyle.url, url=f'https://github-app.c4gt.samagra.io/authenticate/{userID}'))

class AuthenticationView(discord.ui.View):
    def __init__(self, discord_userdata):
        super().__init__()
        self.timeout = None
        button = discord.ui.Button(label='Authenticate Github', style=discord.ButtonStyle.url, url=f'https://github-app.c4gt.samagra.io/authenticate/{discord_userdata}')
        self.add_item(button)
        self.message = None

class RegistrationModal(discord.ui.Modal):
    def __init__(self, *, title: str = None, timeout: float | None = None, custom_id: str = None) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
    name = discord.ui.TextInput(label='Please Enter Your Name')
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Thanks! Now register your Github",view=AuthenticationView(interaction.user.id), ephemeral=True)

class RegistrationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.button(label="Register", style=discord.enums.ButtonStyle.blurple, custom_id='registration_view:blurple')
    async def reg(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RegistrationModal(title="Contributor Registration", custom_id="registration:modal")
        await interaction.response.send_modal(modal)

class C4GTBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('!'), intents=intents)
    
    async def setup_hook(self) -> None:
        # Register the persistent view for listening here.
        # Note that this does not send the view to any message.
        # In order to do this you need to first send a message with the View, which is shown below.
        # If you have the message_id you can also pass it as a keyword argument, but for this example
        # we don't have one.
        self.add_view(RegistrationView())

client = C4GTBot()

@client.command(aliases=['registration'])
async def registerAsContributor(ctx, channel: discord.TextChannel):
    # guild = ctx.guild
    # channelID = 1167054801385820240
    # channel = guild.get_channel_or_thread(channelID)
    await channel.send("Please register using Github to sign up as a C4GT Contributor", view=RegistrationView())
        

#alert message on commandline that bot has successfully logged in

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

#load cogs
async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with client:
        await load()
        await client.start(os.getenv("TESTING_TOKEN"))


asyncio.run(main())


        


