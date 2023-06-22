import discord
import os
from discord.ext import commands, tasks
import time, csv
from utils.db import SupabaseInterface
from utils.api import GithubAPI

CONTRIBUTOR_ROLE_ID = 973852365188907048

class Badges:
    def __init__(self, name, points=0) -> None:
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

You have earned {points} points and earned a** C4GT Enthusiast Badge**!🥳 

This badge shows that you are a valuable member of our community and that you are ready to take on more challenges! 😎

But don’t stop here! There are more badges and rewards waiting for you! 🎁 The next badge is **Rising Star**, and you can get it by solving more issues and winning 30 points! 💯
'''
        risingStarDesc = f'''Hey *{name}*!!!

You are on fire! 🔥 You have earned 30 points and reached a new level of excellence! 🙌 You have earned the **C4GT Rising Star badge!** 🌟
 
This badge shows that you are a brilliant problem-solver and a leader in our community! 😎 You have impressed us all with your skills and passion! 🥰

But there’s more to come! There are more badges and rewards for you to unlock! 🎁 The next badge is **Wizard**, and you can get it by earning 60 points! 💯
        '''
        
        
        self.apprenticeBadge = discord.Embed(title="Apprentice Badge", description=apprentinceDesc)
        self.converseBadge = discord.Embed(title="Converser Badge", description=converseDesc)
        self.rockstarBadge = discord.Embed(title="Rockstar Badge", description=rockstarDesc)
        self.enthusiastBadge = discord.Embed(title="Enthusiast Badge", description=enthusiastDesc)
        self.risingStarBadge = discord.Embed(title="Rising Star Badge", description=risingStarDesc)
        
        self.apprenticeBadge.set_image(url="https://raw.githubusercontent.com/Code4GovTech/discord-bot/main/assets/Apprentice.png")
        self.converseBadge.set_image(url='https://raw.githubusercontent.com/Code4GovTech/discord-bot/main/assets/Converser.png')
        self.rockstarBadge.set_image(url='https://raw.githubusercontent.com/Code4GovTech/discord-bot/main/assets/Rockstar.png')
        self.enthusiastBadge.set_image(url='https://raw.githubusercontent.com/Code4GovTech/discord-bot/main/assets/Enthusiast.png')
        self.risingStarBadge.set_image(url='https://raw.githubusercontent.com/Code4GovTech/discord-bot/main/assets/RisingStar.png')

class Announcement:
    def __init__(self, member):
        self.member = member

    async def create_embed(self):
        embed = discord.Embed(
            title=f"Hey {self.member.name}!",
            description=f'''
If you submitted a proposal and did not make it to the C4GT mentoring program  or you missed the deadline for applying, worry not!

**We have launched the C4GT Community Program Today!**🚀 🚀 

Through this program you can contribute to multiple projects, build your skills & get exclusive rewards & goodies. 

How will the Community Program work?🤔  
- **Explore Projects** 📋 - Explore [projects](https://www.codeforgovtech.in/community-projects) as per your skills, interest in the domain & more.
- **Get Coding** 💻  - Interact with mentors for clarity if required & solve the project
- **Points & Rewards** 🎁 - On each PR merged, you will get points. These points will give you badges & C4GT goodies. Read more about the point system [here](https://github.com/Code4GovTech/C4GT/wiki/Point-System-for-Contributors)

How can you participate?
- **Link Discord & GitHub** 🤝 - Use this [link]({os.getenv('FLASK_HOST')}/authenticate/{self.member.id})  to connect these platforms, so we can track your activity & calculate points
- **Explore Issues Listed** 🖥️ - Keep an eye on our project page as more issues will be released every week. 
- **Ask Questions** ❓ - Ask away your queries on the #c4gtcommunitychannel

So what are you waiting for? Let's get started!!''',
            color=0x00FFFF
        )

        # embed.add_field(name="How will the Community Program work?🤔",
        #                 value="- **Explore Projects** 📋 - Explore [projects](https://c4gt-ccbp-projects.vercel.app/) as per your skills, interest in the domain & more.\n- **Get Coding** 💻 - Interact with mentors for clarity if required & solve the project\n- **Points & Rewards** 🎁 - On each PR merged, you will get points. These points will give you badges & C4GT goodies. Read more about the point system [here](https://github.com/Code4GovTech/C4GT/wiki/Point-System-for-Contributors)")

        # embed.add_field(name="How can you participate?",
        #                 value=f"- **Link Discord & GitHub** 🤝 - Use this [link]({os.getenv('''FLASK_HOST''')}/authenticate/{self.member.id}) to connect these platforms, so we can track your activity & calculate points\n- **Explore Issues Listed** 🖥️ - Keep an eye on our project page as more issues will be released every week.\n- **Ask Questions** ❓ - Ask away your queries on the #c4gtcommunitychannel")
        # embed.add_field(name="So what are you waiting for? Let's get started!!", value='')
        return embed

        





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
        self.update_contributors.start()

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
    
    @commands.command()
    async def give_badges(self, ctx):
        self.give_discord_badges.start()

    @tasks.loop(minutes=15)
    async def give_discord_badges(self):
        contributors = SupabaseInterface("discord_engagement").read_all()
        guild = await self.bot.fetch_guild(os.getenv("SERVER_ID"))
        for contributorData in contributors:
            member = await guild.fetch_member(contributorData["contributor"])
            print(member.name)
            badges = Badges(member.name)
            dmchannel = member.dm_channel if member.dm_channel else await member.create_dm()
            if contributorData["total_message_count"]>10 and not contributorData["converserBadge"]:
                SupabaseInterface("discord_engagement").update({"converserBadge":True},"contributor", contributorData["contributor"])
                await dmchannel.send(embed=badges.converseBadge)
            if contributorData["total_reaction_count"]>5 and not contributorData["rockstarBadge"]:
                SupabaseInterface("discord_engagement").update({"rockstarBadge":True},"contributor", contributorData["contributor"])
                await dmchannel.send(embed=badges.rockstarBadge)
            if contributorData["has_introduced"] and not contributorData["apprenticeBadge"]:
                SupabaseInterface("discord_engagement").update({"apprenticeBadge":True},"contributor", contributorData["contributor"])
                await dmchannel.send(embed=badges.apprenticeBadge)
        print("DONE")

    
    @tasks.loop(minutes=10)
    async def update_contributors(self):
        contributors = SupabaseInterface("contributors").read_all()
        guild = await self.bot.fetch_guild(os.getenv("SERVER_ID"))
        contributor_role = guild.get_role(CONTRIBUTOR_ROLE_ID)
        for contributor in contributors:
            member = await guild.fetch_member(contributor["discord_id"])
            if contributor_role not in member.roles:
                #Give Contributor Role
                await member.add_roles(contributor_role)
            #add to discord engagement
            # SupabaseInterface("discord_engagement").insert({"contributor": member.id})
        
        #update engagement
        for contributor in contributors:
            contributorData = SupabaseInterface("discord_engagement").read("contributor", contributor["discord_id"])[0]
            member = await guild.fetch_member(contributorData["contributor"])
            dmchannel = member.dm_channel if member.dm_channel else await member.create_dm()
            print(f"-----Contributor-----{member.name}-------")
            badges = Badges(member.name)
            if contributorData:
                if contributorData["total_message_count"]>10 and not contributorData["converserBadge"]:
                    SupabaseInterface("discord_engagement").update({"converserBadge":True},"contributor", contributorData["contributor"])
                    await dmchannel.send(embed=badges.converseBadge)
                if contributorData["total_reaction_count"]>5 and not contributorData["rockstarBadge"]:
                    SupabaseInterface("discord_engagement").update({"rockstarBadge":True},"contributor", contributorData["contributor"])
                    await dmchannel.send(embed=badges.rockstarBadge)
                if contributorData["has_introduced"] and not contributorData["apprenticeBadge"]:
                    SupabaseInterface("discord_engagement").update({"apprenticeBadge":True},"contributor", contributorData["contributor"])
                    await dmchannel.send(embed=badges.apprenticeBadge)
            github_id = contributor["github_id"]
            prData = {
                "raised": SupabaseInterface(table="pull_requests").read(query_key="raised_by", query_value=github_id),
                "merged":SupabaseInterface(table="pull_requests").read(query_key="merged_by", query_value=github_id)
            }
            points = 0
            for action in prData.keys():
                prs = prData[action]
                for pr in prs:
                    points+=pr["points"]
            if len(prData["raised"])+len(prData["merged"])>0and not contributorData["enthusiastBadge"]:
                SupabaseInterface("discord_engagement").update({"enthusiastBadge":True},"contributor", contributorData["contributor"])
                await dmchannel.send(embed=Badges(member.name, points=points).enthusiastBadge)
            if points>=30and not contributorData["risingStarBadge"]:
                SupabaseInterface("discord_engagement").update({"risingStarBadge":True},"contributor", contributorData["contributor"])
                await dmchannel.send(embed=badges.risingStarBadge)

            



                
            

        return
    
    @update_contributors.before_loop
    async def before_update_loop(self):
        print("starting auto-badge")
        await self.bot.wait_until_ready()
    
    @commands.command()
    async def announce(self, ctx):
        guild = await self.bot.fetch_guild(os.getenv("SERVER_ID")) #SERVER_ID Should be C4GT Server ID
        count = 0
        async for member in guild.fetch_members(limit=None):
            dmchannel = member.dm_channel if member.dm_channel else await member.create_dm()
            announcement = await Announcement(member).create_embed()
            await dmchannel.send(embed=announcement)
            count +=1
            print(member.name)
        print(count)
        

    @commands.command(aliases=["point_system_breakdown", "point_system"])
    async def point_breakdown(self, ctx):
        message =f'''Hey **{ctx.author.name}**

Points are allocated on the following basis:bar_chart: :

:arrow_forward: **Number of PRs accepted** 

:rocket:  **10 points per ticket are given** 
:rocket: **Get more points for complex tickets**

- 1x for Low Complexity 
- 2x for Medium Complexity
- 3x for High Complexity

:arrow_forward: **Number of PRs reviewed** 

:rocket: **10 points per ticket for those who have been made a maintainer to review PRs** 
:rocket:  **Get more points for complex tickets**

- 1x for Low Complexity 
- 2x for Medium Complexity
- 3x for High Complexity
''' 
        await ctx.channel.send(message)

    
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