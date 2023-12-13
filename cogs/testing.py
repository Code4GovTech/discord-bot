from typing import Optional, Union

import discord
from discord.emoji import Emoji
from discord.enums import ButtonStyle
from discord.ext import commands
from discord.partial_emoji import PartialEmoji
from discord.utils import MISSING
from utils.db import SupabaseInterface


async def on_button_click(interaction: discord.Interaction):
    # Get the Discord username of the person who pressed the button
    username = interaction.user.name
    print(username)

    # Create a modal
    modal = discord.ui.Modal(title="Testing Panel")
    modal.add_item(discord.ui.TextInput(label="Link"))

    # Add a button to the modal that links to Google
    modal.add_item(
        discord.ui.Button(label="Go to Google", url="https://www.google.com")
    )

    # Add a button to the modal to close it
    modal.add_item(discord.ui.Button(label="Close"))

    # Show the modal to the user
    await interaction.response.send_modal(modal)

    # After the modal closes, send an ephemeral message to the user with their Discord ID
    ephemeral_message = f"Your Discord ID is {interaction.user.id}"
    await interaction.channel.send(ephemeral_message, ephemeral=True)


class Questionnaire(discord.ui.Modal, title="Questionnaire Response"):
    name = discord.ui.TextInput(label="Name")
    answer = discord.ui.TextInput(label="Answer", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Thanks for your response, {self.name}!, Your answer is {self.answer}",
            ephemeral=True,
        )


async def click(interaction: discord.Interaction):
    # modal = InteractionModal()
    # await interaction.response.send_message("You Pressed the Button!!!")
    modal = Questionnaire()
    await interaction.response.send_modal(modal)


class TestingPanel(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout = None

        # create a textbox
        self.add_item(
            discord.ui.Select(
                placeholder="CHOOSE",
                options=[
                    discord.SelectOption(label=f"{x}", value=f"{x}")
                    for x in [1, 2, 3, 4]
                ],
            )
        )

        # Create a button
        self.press_me_button = discord.ui.Button(label="Press me")
        self.press_me_button.callback = click

        modal = Questionnaire()

        # Add the button to the view
        self.add_item(self.press_me_button)

    # Handle the button press event


class InteractionModal(discord.ui.Modal):
    def __init__(
        self, *, title: str = ..., timeout: float | None = None, custom_id: str = ...
    ) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)

        self.add_item(discord.ui.TextInput(label="Enter your Name"))
        self.add_item(
            discord.ui.TextInput(label="Long Input", style=discord.TextStyle.long)
        )


class TestingModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def newjoin(self, interaction: discord.Interaction):
        button = discord.ui.Button(
            style=ButtonStyle.green, label="Authenticate with Github"
        )
        view = discord.ui.View()
        view.add_item(button)
        await interaction.response.send_message(
            "Auuthenticate your Github", view=view, ephemeral=True
        )

    @commands.command()
    async def arrowrow(self, ctx):
        text_input_1 = discord.ui.TextInput(
            label="Text 1", placeholder="Text Input 1", min_length=1, max_length=25
        )
        text_input_2 = discord.ui.TextInput(
            label="Text 2", placeholder="Text Input 2", min_length=1, max_length=25
        )

        select_input = discord.ui.Select(
            placeholder="Select Input",
            options=[
                discord.SelectOption(label="Option 1", value="1"),
                discord.SelectOption(label="Option 2", value="2"),
                discord.SelectOption(label="Option 3", value="3"),
            ],
        )

        user_select_input = discord.ui.UserSelect(placeholder="User Select Input")

        button = discord.ui.Button(style=discord.ButtonStyle.primary, label="Submit")

        row = discord.ActionRow(
            [text_input_1, text_input_2, select_input, user_select_input, button]
        )

        await ctx.send("Here's your arrowrow:", components=[row])

    # Create a Discord command
    @commands.command()
    async def testing_panel(self, ctx):
        # Create a view
        view = TestingPanel()

        # Send the view to the user
        await ctx.send("Testing Panel", view=view)


async def setup(bot):
    await bot.add_cog(TestingModule(bot))
