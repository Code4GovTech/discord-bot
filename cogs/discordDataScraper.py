import json
import os
import sys
from asyncio import sleep
from datetime import datetime

import discord
from discord import Member
from discord.channel import TextChannel
from discord.ext import commands, tasks

from helpers.supabaseClient import SupabaseClient

with open("config.json") as config_file:
    config_data = json.load(config_file)

# CONSTANTS
CONTRIBUTOR_ROLE_ID = config_data["CONTRIBUTOR_ROLE_ID"]
INTRODUCTIONS_CHANNEL_ID = config_data["INTRODUCTIONS_CHANNEL_ID"]
ERROR_CHANNEL_ID = config_data["ERROR_CHANNEL_ID"]
TIME_DURATION = config_data["TIME_DURATION"]


class DiscordDataScaper(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        contributor = SupabaseClient().read(
            "discord_engagement", "contributor", message.author.id
        )
        print("message", len(message.content))
        if not contributor:
            SupabaseClient().insert(
                "discord_engagement",
                {
                    "contributor": message.author.id,
                    "has_introduced": False,
                    "total_message_count": 1,
                    "total_reaction_count": 0,
                },
            )
            return
        if len(message.content) > 20:
            if message.channel.id == INTRODUCTIONS_CHANNEL_ID:
                print("intro")
                SupabaseClient().update(
                    "discord_engagement",
                    {"has_introduced": True},
                    "contributor",
                    message.author.id,
                )
            SupabaseClient("discord_engagement").update(
                "discord_engagement",
                {"total_message_count": contributor[0]["total_message_count"] + 1},
                "contributor",
                message.author.id,
            )

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        contributor = SupabaseClient().read(
            "discord_engagement", "contributor", message.author.id
        )[0]
        if not contributor:
            SupabaseClient().insert(
                "discord_engagement",
                {
                    "contributor": message.author.id,
                    "has_introduced": False,
                    "total_message_count": 0,
                    "total_reaction_count": 1,
                },
            )
            return
        print("reaction")
        SupabaseClient().update(
            "discord_engagement",
            {"total_reaction_count": contributor["total_reaction_count"] + 1},
            "contributor",
            message.author.id,
        )

    @commands.command()
    async def add_engagement(self, ctx):
        await ctx.channel.send("started")

        def addEngagmentData(data):
            client = SupabaseClient()
            client.insert("discord_engagement", data)
            return

        guild = await self.bot.fetch_guild(
            os.getenv("SERVER_ID")
        )  # SERVER_ID Should be C4GT Server ID
        channels = await guild.fetch_channels()
        engagmentData = {}

        async for member in guild.fetch_members(limit=None):
            memberData = {
                "contributor": member.id,
                "has_introduced": False,
                "total_message_count": 0,
                "total_reaction_count": 0,
            }
            engagmentData[member.id] = memberData

        for channel in channels:
            print(channel.name)
            if isinstance(
                channel, TextChannel
            ):  # See Channel Types for info on text channels https://discordpy.readthedocs.io/en/stable/api.html?highlight=guild#discord.ChannelType
                async for message in channel.history(limit=None):
                    if message.author.id not in engagmentData.keys():
                        engagmentData[message.author.id] = {
                            "contributor": message.author.id,
                            "has_introduced": False,
                            "total_message_count": 0,
                            "total_reaction_count": 0,
                        }
                    if message.content == "":
                        continue
                    if len(message.content) > 20:
                        engagmentData[message.author.id]["total_message_count"] += 1
                        if message.channel.id == INTRODUCTIONS_CHANNEL_ID:
                            engagmentData[message.author.id]["has_introduced"] = True
                    if message.reactions:
                        engagmentData[message.author.id]["total_reaction_count"] += len(
                            message.reactions
                        )
        addEngagmentData(list(engagmentData.values()))
        print("Complete!", file=sys.stderr)
        return

    def valid_user(ctx):
        return ctx.author.id == 476285280811483140

    @commands.command()
    @commands.check(valid_user)
    async def enable_webhook(self, ctx):
        guild = await self.bot.fetch_guild(os.getenv("SERVER_ID"))
        channels = await guild.fetch_channels()
        enabled = [
            channel["channel_id"]
            for channel in SupabaseClient().read_all("discord_channels")
        ]
        for channel in channels:
            try:
                feedback = f"""Channel: {channel.name}\nCategory: {channel.category} """
                await ctx.send(feedback)
                if isinstance(channel, TextChannel) and channel.id not in enabled:
                    sleep(120)
                    webhook = await channel.create_webhook(name="New Ticket Alert")
                    feedback = f"""URL: {webhook.url}\n Token:{"Yes" if webhook.token else "No"}"""
                    await ctx.send(feedback)
                    SupabaseClient().insert(
                        "discord_channels",
                        {
                            "channel_id": channel.id,
                            "channel_name": channel.name,
                            "webhook": webhook.url,
                        },
                    )
            except Exception as e:
                await ctx.send(e)
                continue

    @commands.command()
    async def update_applicants(self, ctx):
        try:
            applicants_channel = self.bot.get_channel(1125359312370405396)
            await ctx.send("Channel Identified:" + applicants_channel.name)
            members = applicants_channel.members
            await ctx.send("Member List Count: " + str(len(members)))
            for member in members:
                try:
                    SupabaseClient().insert(
                        "applicant",
                        {"sheet_username": member.name, "discord_id": member.id},
                    )
                except Exception as e:
                    print(e)
                    continue
        except Exception as e:
            await ctx.send(e)
        await ctx.send("Completed")

    # command to run the message collector
    @commands.command()
    async def start_collecting_messages(self, ctx):
        if not self.collect_all_messages.is_running():
            self.collect_all_messages.start()
            print("Initiating message collection")
            await ctx.send("Message collection started.")
        else:
            await ctx.send("Message collection already in progress.")

    # command to stop the message collector
    @commands.command()
    async def stop_collecting_messages(self, ctx):
        if self.collect_all_messages.is_running():
            self.collect_all_messages.cancel()
            print("Stopping message collection")
            await ctx.send("Message collection stopped.")
        else:
            await ctx.send("Message collection is not running.")

    # recurring job to collect all the messages
    @tasks.loop(seconds=TIME_DURATION)
    async def collect_all_messages(self):
        print(f"Collecting all messages as of {datetime.now()}")
        await self.add_messages()

    async def add_messages(self):
        def addMessageData(data):
            client = SupabaseClient()
            client.insert("unstructured discord data", data)
            return

        def getLastMessageObject(channelId):
            last_message = SupabaseClient().read_by_order_limit(
                table="unstructured discord data",
                query_key="channel",
                query_value=channelId,
                order_column="id.desc",
            )  # fetching the record for the lastest message downloaded from a particular channel, the most recent message has the largest message_id
            if len(last_message) > 0:
                print(f"Last message details for {channelId} is {last_message[0]}")
                return discord.Object(id=last_message[0]["id"])
            else:
                print(f"No previous messages obtained for {channelId}")
                return None

        try:
            guild = await self.bot.fetch_guild(
                os.getenv("SERVER_ID")
            )  # SERVER_ID Should be C4GT Server ID
            channels = await guild.fetch_channels()

            for channel in channels:
                print(f"Downloading messages for '{channel.name}' channel")
                if isinstance(
                    channel, TextChannel
                ):  # See Channel Types for info on text channels https://discordpy.readthedocs.io/en/stable/api.html?highlight=guild#discord.ChannelType
                    messages = []
                    last_message_object = getLastMessageObject(channel.id)
                    # fetching only the messages after the last message id, if None, then all the messages are fetched
                    async for message in channel.history(
                        limit=None, after=last_message_object
                    ):
                        if message.content == "":
                            continue
                        msg_data = {
                            "channel": channel.id,
                            "channel_name": channel.name,
                            "text": message.content,
                            "author": message.author.id,
                            "author_name": message.author.name,
                            "author_roles": message.author.roles
                            if isinstance(message.author, Member)
                            else [],
                            "sent_at": str(message.created_at),
                            "id": message.id,
                        }
                        messages.append(msg_data)
                    print(f"{len(messages)} new messages found ")
                    addMessageData(messages)
                else:
                    print(f"{channel.name} not a text channel")
            print(f"Downloaded all messages as of {datetime.now()}")
        except Exception as e:
            error_channel = await guild.fetch_channel(ERROR_CHANNEL_ID)
            error_message = f"Error occurred while downloading messages: {e}"
            await error_channel.send(error_message)
            print(error_message)


async def setup(bot):
    await bot.add_cog(DiscordDataScaper(bot))
