import discord
import os
from discord.ext import commands, tasks
import time, csv
from utils.db import SupabaseInterface
from utils.api import GithubAPI

CONTRIBUTOR_ROLE_ID = 973852365188907048
NON_CONTRIBUTOR_ROLES = [973852321870118914, 976345770477387788, 973852439054782464]
NON_CONTRIBUTOR_MEMBERS = [704738663883472967, 703157062825410590, 697080616046559352, 694445371816149062, 677090546694619168, 662243718354698240, 637512076084117524, 636277951540887553, 599878601143222282, 476285280811483140, 459239263192612874, 365127154847186945, 314379504157982721, 291548601228722177, 280019116755124226, 262810519184998400, 222905396610859010, 761623930531741788, 760775460178755614, 759107287322329128, 753909213859938385, 749287051035148328, 730733764891770950, 727567753246146633, 722313444325457921, 720297291105304627, 712557512926298153, 788670744120786976, 805863967284920352, 804299931543535626, 902553914916896808, 882206400074358835, 1016564507394457663, 1010140041789571072, 1008331310806335618, 989823092283035678, 987081239892750376, 986500267858083860, 986245349129740338, 973537784537186304, 971297678401089556, 969115972059406376, 967973710617247796, 965956645895147610, 963733651529531444, 961904402459947018, 961529037610713098, 961283715382775818, 960435521786617856, 948478097508954122, 937569989689487420, 936118598102028319, 935911019828641812, 933651897502535690, 1087744252408246373, 1086529617013252167, 1083352549660307466, 1079268207917027348, 1077912548571095092, 1075013295221768213, 1070737923483389972, 1059343450312544266, 1052565902748553236, 1050037458286420099, 1049311176716206164, 1045238281740230656, 1044876122191581194, 1044532981857001502, 1043440759061352588, 1042682119035568178, 1039880103934570517, 1037956974039535636, 1036590822201757696, 1024552723280052294, 1018398460598308915, 1108763601231171594, 1108657717100429312, 1108649642633199636, 1108649434251792514, 1108649344242040883, 1108649032978538497, 1108618174477369426, 1108613175697481749, 1108269782668681276, 1107943353632432208, 1107933295930511431, 1107927044962144286, 1107910689370165248, 1107899551974686831, 1107656943809593395, 1107618486232039454, 1107555866422562926, 1107504062175391815, 1101892125328679024, 1100365706362626098, 1099938102555975690, 1098923182439796818, 1093415042860466268, 1091224095770816552, 1120262010752471112, 1115908663207530577, 1115622606440239184, 1115538129672224880, 1115537984972931173, 1115171977934688296, 1114795277518389391]


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
        # self.update_contributors.start()

    #Executing this command sends a link to Github OAuth App via a Flask Server in the DM channel of the one executing the command 
    @commands.command(aliases=['join'])
    async def join_as_contributor(self, ctx):
        #create a direct messaging channel with the one who executed the command
        if isinstance(ctx.channel, discord.DMChannel):
            userdata = str(ctx.author.id)
            view = AuthenticationView(userdata)
            await ctx.send("Please authenticate your github account to register in the C4GT Community", view=view)
        # Command logic for DMs
        else:
        # Command logic for other channels (e.g., servers, groups)
            await ctx.send("Please use this command in Bot DMs.")
        # Command logic for DMs
        userdata = str(ctx.author.id)
        view = AuthenticationView(userdata)
        # await dmchannel.send("Please authenticate your github account to register for Code for GovTech 2023", view=view)

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
    
    # @commands.command()
    # async def give_badges(self, ctx):
    #     self.give_discord_badges.start()


    
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
        # for contributor in contributors:
        #     contributorData = SupabaseInterface("discord_engagement").read("contributor", contributor["discord_id"])[0]
        #     member = await guild.fetch_member(contributorData["contributor"])
        #     print(f"-----Contributor-----{member.name}-------")
        #     badges = Badges(member.name)
        #     if contributorData:
        #         if contributorData["total_message_count"]>10 and not contributorData["converserBadge"]:
        #             SupabaseInterface("discord_engagement").update({"converserBadge":True},"contributor", contributorData["contributor"])
        #             dmchannel = member.dm_channel if member.dm_channel else await member.create_dm()
        #             await dmchannel.send(embed=badges.converseBadge)
        #         if contributorData["total_reaction_count"]>5 and not contributorData["rockstarBadge"]:
        #             SupabaseInterface("discord_engagement").update({"rockstarBadge":True},"contributor", contributorData["contributor"])
        #             dmchannel = member.dm_channel if member.dm_channel else await member.create_dm()
        #             await dmchannel.send(embed=badges.rockstarBadge)
        #         if contributorData["has_introduced"] and not contributorData["apprenticeBadge"]:
        #             SupabaseInterface("discord_engagement").update({"apprenticeBadge":True},"contributor", contributorData["contributor"])
        #             dmchannel = member.dm_channel if member.dm_channel else await member.create_dm()
        #             await dmchannel.send(embed=badges.apprenticeBadge)
        #     github_id = contributor["github_id"]
        #     prData = {
        #         "raised": SupabaseInterface(table="pull_requests").read(query_key="raised_by", query_value=github_id),
        #         "merged":SupabaseInterface(table="pull_requests").read(query_key="merged_by", query_value=github_id)
        #     }
        #     points = 0
        #     for action in prData.keys():
        #         prs = prData[action]
        #         for pr in prs:
        #             points+=pr["points"]
        #     if len(prData["raised"])+len(prData["merged"])>0and not contributorData["enthusiastBadge"]:
        #         SupabaseInterface("discord_engagement").update({"enthusiastBadge":True},"contributor", contributorData["contributor"])
        #         await dmchannel.send(embed=Badges(member.name, points=points).enthusiastBadge)
        #     if points>=30 and not contributorData["risingStarBadge"]:
        #         SupabaseInterface("discord_engagement").update({"risingStarBadge":True},"contributor", contributorData["contributor"])
        #         await dmchannel.send(embed=badges.risingStarBadge)

            



                
            

        return
    
    @update_contributors.before_loop
    async def before_update_loop(self):
        print("starting auto-badge")
        await self.bot.wait_until_ready()

    async def read_members_csv(self, file_path):
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip the header row

            rows = []
            count = 0
            for row in reader:
                rows.append(row)
                count += 1
                if count == 10:
                    yield rows
                    rows = []
                    count = 0

            if rows:
                yield rows
    
    # @commands.command()
    # async def announce(self, ctx):
    #     guild = await self.bot.fetch_guild(os.getenv("SERVER_ID")) #SERVER_ID Should be C4GT Server ID
    #     file_path = "members.csv"
    #     async for batch in self.read_members_csv(file_path):
    #         for row in batch:
    #             member = await guild.fetch_member(row[0])
    #             print(member.name)
    #             dmchannel = await member.create_dm()
    #             time.sleep(10)
    #         print("---")
        
        # count = 0
        # non_con_members = []
        # async for member in guild.fetch_members(limit=None):
        #     # dmchannel = member.dm_channel if member.dm_channel else await member.create_dm()
        #     announcement = await Announcement(member).create_embed()
        #     # await dmchannel.send(embed=announcement)
        #     count +=1
        #     print(member.name)
        #     if any(role.id in NON_CONTRIBUTOR_ROLES for role in member.roles):
        #         non_con_members.append(member.id)
        # print(non_con_members)
        # print(count)


    # @commands.command()
    # async def announce(self, ctx):
    #     guild = await self.bot.fetch_guild(os.getenv("SERVER_ID"))
    #     members = []
    #     async for member in guild.fetch_members(limit=None):
    #         members.append(member.id)

    #     # Save members to a CSV file
    #     file_path = "members.csv"
    #     with open(file_path, mode="w", newline="\n", encoding="utf-8") as file:
    #         writer = csv.writer(file)
    #         writer.writerow(["Member id"])  # Write header row
    #         writer.writerows(zip(members))  # Write member names

    #     print(f"Members saved to {file_path}")
        

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
        raiseTicketComplexity = {
            "low":0,
            "medium": 0,
            "high":0
        }
        mergeTicketComplexity = {
            "low": 0,
            "medium": 0,
            "high": 0
        }
        for pr in prs_raised:
            raise_points+=pr["points"]
            if pr["points"] == 10:
                raiseTicketComplexity["low"]+=1
            if pr["points"] == 20:
                raiseTicketComplexity["medium"]+=1
            if pr["points"] == 30:
                raiseTicketComplexity["high"]+=1
        for pr in prs_merged:
            merge_points+=pr["points"]
            if pr["points"] == 10:
                mergeTicketComplexity["low"]+=1
            if pr["points"] == 20:
                mergeTicketComplexity["medium"]+=1
            if pr["points"] == 30:
                mergeTicketComplexity["high"]+=1

        text = f'''
        Hey {ctx.author.name}

**You have a total of {raise_points+merge_points} points**🌟 

▶️ **Points Basis PRs accepted - {raise_points} points**🔥 

Number of tickets solved - {len(prs_raised)}
Points on tickets with low complexity - {raiseTicketComplexity["low"]*10} points
Points on tickets with medium complexity - {raiseTicketComplexity["medium"]*20} points
Points of tickets with high complexity - {raiseTicketComplexity["high"]*30} points

▶️ **Points as per PRs reviewed - {merge_points} points**🙌 

Number of tickets reviewed - {len(prs_merged)}
Points on tickets with low complexity - {mergeTicketComplexity["low"]*10} points
Points on tickets with medium complexity - {mergeTicketComplexity["medium"]*20} points
Points of tickets with high complexity - {mergeTicketComplexity["high"]*30} points

Get coding and earn more points to get a spot on the leaderboard📈'''
        await ctx.channel.send(text)
    
     
async def setup(bot):
    await bot.add_cog(UserHandler(bot))