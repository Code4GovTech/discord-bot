import discord
import os
from discord.ext import commands, tasks
import time, csv
from utils.db import SupabaseInterface
from utils.api import GithubAPI

CONTRIBUTOR_ROLE_ID = 973852365188907048

class Badges():
    def __init__(self, name) -> None:
        apprentinceDesc = f'''Welcome *{name}*!!
 
Congratulations! 🎉 You have taken the first step to join & introduce yourself to this awesome community and earned the **Apprentice Badge**! 🎓 This badge shows that you are eager to learn and grow with our community! 😎 We are so happy to have you here and we can’t wait to see what you will create and solve! 🚀'''
        converseDesc = f'''Well done *{name}*! 👏
    You have engaged on the C4GT  discord community  with 10  or more messages and earned the **Converser Badge!** 💬 This badge shows that you are a friendly and helpful member of our community! 😊 '''
        rockstarDesc = f'''Amazing *{name}*! 🙌
    You have received 5 upvotes on your message and earned the **Rockstar Badge!** 🌟 You add so much value to our community and we are grateful for your contribution! 💖 
    Please keep up the good work and share your expertise with us! 🙌
    '''
        
        
        self.apprenticeBadge = discord.Embed(title="Apprentice Badge", description=apprentinceDesc)
        self.converseBadge = discord.Embed(title="Converse Badge", description=converseDesc)
        self.rockstarBadge = discord.Embed(title="Rockstar Badge", description=rockstarDesc)
        
        self.apprenticeBadge.set_image(url="https://raw.githubusercontent.com/Code4GovTech/discord-bot/main/assets/Apprentice.png")
        self.converseBadge.set_image(url='https://raw.githubusercontent.com/Code4GovTech/discord-bot/main/assets/Converser.png')
        self.rockstarBadge.set_image(url='https://raw.githubusercontent.com/Code4GovTech/discord-bot/main/assets/Rockstar.png')





#This is a Discord View that is a set of UI elements that can be sent together in a message in discord.
#This view send a link to Github Auth through c4gt flask app in the form of a button.
class AuthenticationView(discord.ui.View):
    def __init__(self, discord_userdata):
        super().__init__()
        button = discord.ui.Button(label='Authenticate Github', style=discord.ButtonStyle.url, url=f'{os.getenv("FLASK_HOST")}/authenticate/{discord_userdata}')
        self.add_item(button)
        self.message = None

class UserHandler(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        # self.update_contributors.start()

    #Executing this command sends a link to Github OAuth App via a Flask Server in the DM channel of the one executing the command 
    @commands.command(aliases=['join'])
    async def join_as_contributor(self, ctx):
        #create a direct messaging channel with the one who executed the command
        dmchannel = ctx.author.dm_channel if ctx.author.dm_channel else await ctx.author.create_dm()
        userdata = str(ctx.author.id)
        view = AuthenticationView(userdata)
        await dmchannel.send("Please authenticate your github account to register for Code for GovTech 2023", view=view)

    @commands.command(aliases=["badges"])
    async def list_badges(self, ctx):

        converseDesc = f'''Well done *{ctx.author.name}*! 👏
    You have engaged on the C4GT  discord community  with 10  or more messages and earned the **Converser Badge!** 💬 This badge shows that you are a friendly and helpful member of our community! 😊 '''
        converseEmbed = discord.Embed(title="Converse Badge", description=converseDesc)
        converseEmbed.set_image(url="https://raw.githubusercontent.com/KDwevedi/testing_for_github_app/main/WhatsApp%20Image%202023-06-20%20at%202.57.12%20PM.jpeg")

        rockstarDesc = f'''Amazing *{ctx.author.name}*! 🙌
    You have received 5 upvotes on your message and earned the **Rockstar Badge!** 🌟 You add so much value to our community and we are grateful for your contribution! 💖 
    Please keep up the good work and share your expertise with us! 🙌
    '''
        reactionsEmbed = discord.Embed(title="Rockstar Badge", description=rockstarDesc)
        reactionsEmbed.set_image(url="https://raw.githubusercontent.com/KDwevedi/testing_for_github_app/main/WhatsApp%20Image%202023-06-20%20at%202.57.12%20PM.jpeg")


        await ctx.channel.send(embed=converseEmbed)
        await ctx.channel.send(embed=reactionsEmbed)


        return
    
    @tasks.loop(minutes=10)
    async def update_contributors(self):
        contributors = SupabaseInterface("contributors").read_all()
        guild = await self.bot.fetch_guild(os.getenv("SERVER_ID"))
        contributor_role = guild.get_role(CONTRIBUTOR_ROLE_ID)
        for contributor in contributors:
            member = await guild.fetch_member(contributor["discord_id"])
            if contributor_role not in member.roles:
                #Give Contributor Role
                await member.add_roles([contributor_role])
            #add to discord engagement
            SupabaseInterface("discord_engagement").insert({"contributor": member.id})
        
        #update engagement
        for contributor in contributors:
            contributorData = SupabaseInterface("discord_engagement").read("contributor", contributor["discord_id"])
            member = await guild.fetch_member(contributorData["contributor"])
            dmchannel = member.dm_channel if member.dm_channel else await member.create_dm()
            dmchannel
            

        return
    
    @update_contributors.before_loop
    async def before_update_loop(self):
        await self.bot.wait_until_ready()

    
    @commands.command(aliases=["my_points"])
    async def get_points(self, ctx):

        discord_id = ctx.author.id
        contributor = SupabaseInterface(table="contributors").read(query_key="discord_id", query_value=discord_id)
        print(contributor)
        github_id = contributor[0]["github_id"]
        prs_raised = SupabaseInterface(table="pull_requests").read(query_key="raised_by", query_value=github_id)
        prs_merged = SupabaseInterface(table="pull_requests").read(query_key="merged_by", query_value=github_id)
        raise_points = 0
        merge_points = 0
        for pr in prs_raised:
            raise_points+=pr["points"]
        for pr in prs_raised:
            merge_points+=pr["points"]

        text = f'''
        Hey {ctx.author.name}

**You have a total of {raise_points+merge_points} points**🌟 

▶️**Points Basis PRs accepted - {raise_points} points**🔥 

▶️ **Points as per PRs reviewed - {merge_points} points**🙌 

Woah, awesome! Get coding and earn more points to get a spot on the leaderboard📈'''
        await ctx.channel.send(text)
    
     
async def setup(bot):
    await bot.add_cog(UserHandler(bot))