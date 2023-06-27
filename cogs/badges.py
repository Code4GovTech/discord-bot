from typing import Optional
from discord.ext import commands
import discord
from utils.db import SupabaseInterface
import asyncio

class BadgeModal(discord.ui.Modal, title = "Your Badges"):
    select = discord.ui.Select(placeholder="Choose Badge Type", options=["Points Based", "Achievement Based"])

    async def on_timeout(self, interaction):
        return


class BadgeContents:
    def __init__(self, name) -> None:
        apprentinceDesc = f'''Welcome *{name}*!!
 
        
Congratulations! 🎉 You have taken the first step to join & introduce yourself to this awesome community and earned the **Apprentice Badge**! 🎓 This badge shows that you are eager to learn and grow with our community! 😎 We are so happy to have you here and we can’t wait to see what you will create and solve! 🚀'''
        converseDesc = f'''Well done *{name}*! 👏
    You have engaged on the C4GT  discord community  with 10  or more messages and earned the **Converser Badge!** 💬 This badge shows that you are a friendly and helpful member of our community! 😊 '''
        rockstarDesc = f'''Amazing *{name}*! 🙌
    
    You have received 5 upvotes on your message and earned the **Rockstar Badge!** 🌟 You add so much value to our community and we are grateful for your contribution! 💖 
    
    Please keep up the good work and share your expertise with us! 🙌
    '''
        enthusiastDesc = f'''Wohoo *{name}*!!!

You have solved your first C4GT ticket !

You have earned merged your first pull request and earned a** C4GT Enthusiast Badge**!🥳 

This badge shows that you are a valuable member of our community and that you are ready to take on more challenges! 😎

But don’t stop here! There are more badges and rewards waiting for you! 🎁 The next badge is **Rising Star**, and you can get it by solving more issues and winning 30 points! 💯
'''
        risingStarDesc = f'''Hey *{name}*!!!

You are on fire! 🔥 You have earned 30 points and reached a new level of excellence! 🙌 You have earned the **C4GT Rising Star badge!** 🌟
 
This badge shows that you are a brilliant problem-solver and a leader in our community! 😎 You have impressed us all with your skills and passion! 🥰

But there’s more to come! There are more badges and rewards for you to unlock! 🎁 The next badge is **Wizard**, and you can get it by earning 60 points! 💯
        '''
        
        
        self.apprenticeBadge = discord.Embed(title="Apprentice Badge", description=apprentinceDesc)
        self.converserBadge = discord.Embed(title="Converser Badge", description=converseDesc)
        self.rockstarBadge = discord.Embed(title="Rockstar Badge", description=rockstarDesc)
        self.enthusiastBadge = discord.Embed(title="Enthusiast Badge", description=enthusiastDesc)
        self.risingStarBadge = discord.Embed(title="Rising Star Badge", description=risingStarDesc)
        
        self.apprenticeBadge.set_image(url="https://raw.githubusercontent.com/Code4GovTech/discord-bot/main/assets/Apprentice.png")
        self.converserBadge.set_image(url='https://raw.githubusercontent.com/Code4GovTech/discord-bot/main/assets/Converser.png')
        self.rockstarBadge.set_image(url='https://raw.githubusercontent.com/Code4GovTech/discord-bot/main/assets/Rockstar.png')
        self.enthusiastBadge.set_image(url='https://raw.githubusercontent.com/Code4GovTech/discord-bot/main/assets/Enthusiast.png')
        self.risingStarBadge.set_image(url='https://raw.githubusercontent.com/Code4GovTech/discord-bot/main/assets/RisingStar.png')
    
    def get_user_badges(self, discord_id):
        userBadges = {
            "points": [],
            "achievements": []
        }

        discordMemberData = SupabaseInterface("discord_engagement").read("contributor", discord_id)
        if discordMemberData:
            if discordMemberData[0]["total_message_count"]>10:
                userBadges["achievements"].append(self.converserBadge)
            if discordMemberData[0]["total_reaction_count"]>5:
                userBadges["achievements"].append(self.rockstarBadge)
            if discordMemberData[0]["has_introduced"]:
                userBadges["achievements"].append(self.apprenticeBadge)
        contributorData = SupabaseInterface("contributors").read(query_key="discord_id", query_value=discord_id)
        if contributorData:
            github_id = contributorData[0]["github_id"]
            prData = {
                "raised": SupabaseInterface(table="pull_requests").read(query_key="raised_by", query_value=github_id),
                "merged":SupabaseInterface(table="pull_requests").read(query_key="merged_by", query_value=github_id)
            }
            points = 0
            for action in prData.keys():
                prs = prData[action]
                for pr in prs:
                    points+=pr["points"]
            if len(prData["raised"])+len(prData["merged"])>0:
                userBadges["points"].append(self.enthusiastBadge)
            if points>=30:
                userBadges["points"].append(self.risingStarBadge)
        if not discordMemberData and not contributorData:
            return None
        return userBadges




class Badges(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.command()
    async def my_badges(self, ctx):
        #Check if this happens in DM
        if isinstance(ctx.channel, discord.DMChannel):
            #Get available badges
            user_badges = BadgeContents(ctx.author.name).get_user_badges(ctx.author.id)
            if not user_badges:
                await ctx.channel.send("Oops! It seems you aren' registered!")
            else:
                if user_badges["points"] and user_badges["achievements"]:
                    embed = discord.Embed(title="Badge Type", description="What badge type do you want to view?", color=discord.Color.blue())
                    embed.set_footer(text="Please react with 📈 for Points Based Badges or 🥳 Achievements Based Badges .")
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('📈')
                    await message.add_reaction('🥳') 
                    def check(reaction, user):
                        return user == ctx.message.author and str(reaction.emoji) in ['📈', '🥳']
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                    except asyncio.TimeoutError:
                        await ctx.send("You took too long to respond.")
                    else:
                        if str(reaction.emoji) == '📈':
                            for badge in user_badges["points"]:
                                await ctx.send(embed=badge)
                        elif str(reaction.emoji) == '🥳':
                            for badge in user_badges["achievements"]:
                                await ctx.send(embed=badge)
                else:
                    if user_badges["points"]:
                        for badge in user_badges["points"]:
                                await ctx.send(embed=badge)
                    if user_badges["achievements"]:
                        for badge in user_badges["achievements"]:
                                await ctx.send(embed=badge)
                    else:
                        await ctx.send("Oops, you have no badges yet.")
                        


            





async def setup(bot):
    await bot.add_cog(Badges(bot))