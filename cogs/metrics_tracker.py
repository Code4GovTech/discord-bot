# #Track metrics on github and discord and update the database accordingly
# #Implement using: https://discordpy.readthedocs.io/en/stable/ext/tasks/index.html?highlight=tasks#
from discord.ext import commands, tasks
from discord import Embed
import aiohttp, json
from utils.db import SupabaseInterface
# from discord import Member
# from discord.channel import TextChannel
# from datetime import time, datetime
# from models.product import Product
# from models.project import Project
# from utils.api import GithubAPI
# from utils.db import SupabaseInterface
# import requests, json
# import os, dateutil.parser


# async def getCetificate(name, badge):
#     url = 'http://139.59.20.91:5000/rcw/credential'
#     headers = {
#         'Content-Type': 'application/json'
#     }
#     data = {
#         "type": ["Test Credential"],
#         "subject": {
#             "id": "did:C4GT:test",
#             "username": f"{name}",
#             "badge": f"{badge}"
#         },
#         "schema": "cllbzgfor000ytj151nu7km4t",
#         "tags": ["Tag 1"],
#         "templateId": "cllbzglwa0010tj15104dtgc8"
#     }
    
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, headers=headers, json=data) as response:
#             if response.status == 201:
#                 resp_data = await response.json()
#                 return json.loads(resp_data)
#             else:
#                 print(f"Failed to fetch credential. Status code: {response.status}")
class MetricsTracker(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

#     @commands.command()
#     async def my_certificates(self, ctx):
        
#         noCertsEmbed = Embed(title='', description=f'''Hey {ctx.author.name}

# You have currently not earned any C4GT certificates yet!
# But don’t worry, all you need to do is collect 50 DPG points and get a Rising Star :stars: badge by solving issue tickets to become eligible for your first certificate. **Get coding now!!**:computer: 

# **Discover issue tickets [here](https://www.codeforgovtech.in/community-program-projects).**
# ''')
#         oneCertEmbed = Embed(
#         title="Congratulations!", 
#         description=f"Hey {ctx.author.mention}\n\n"
#                     "You have earned a C4GT certificate for being an **active DPG contributor and earning 50 DPG points!** :partying_face:\n\n"
#                     "Click [here](http://139.59.20.91:9000/c4gt/Kanav%20Dwevedi_Enthusiast%20Badge.pdf) to access your certificate :page_with_curl:",
#         color=0x00ff00  # You can choose any color
#     )

#         contributor_data = SupabaseInterface("contributors").read("discord_id", ctx.author.id)
#         if len(contributor_data)==0:
#             ctx.send("Use the !join command to register to obtain certificates")
#             return
        
#         [contributor] = contributor_data
#         name = contributor["github_url"].split('/')[-1]

#         user = SupabaseInterface("github_profile_data").read("discord_id", ctx.author.id)
#         data = user[0]
#         data["points"] = 70
#         if data["points"] <50 :
#             await ctx.send(embed=noCertsEmbed)
#         elif data["points"]>=50 and data["points"]<100:

#             # resp = await getCetificate(name, "Enthusiast Badge")
#             oneCertEmbed = Embed(
#         title="Congratulations!", 
#         description=f"Hey {ctx.author.mention}\n\n"
#                     "You have earned a C4GT certificate for being an **active DPG contributor and earning 50 DPG points!** :partying_face:\n\n"
#                     "Click [here](http://139.59.20.91:9000/c4gt/Kanav%20Dwevedi_Enthusiast%20Badge.pdf) to access your certificate :page_with_curl:",
#         color=0x00ff00  # You can choose any color
#     )
#             await ctx.send(embed=oneCertEmbed)

        

    
    @commands.command()
    async def points(self, ctx):
        await ctx.send(f'''Hey {ctx.author}

**You have a total of 140 points**🌟 

▶️ **Points Basis PRs accepted - 60 points**🔥 

Number of tickets solved - 3
Points on tickets with low complexity - 10 points
Points on tickets with medium complexity - 20 points
Points of tickets with high complexity - 30 points

▶️ **Points as per PRs reviewed - 80 points**🙌 

Number of tickets reviewed - 4
Points on tickets with low complexity - 10 points
Points on tickets with medium complexity - 40 points
Points of tickets with high complexity - 30 points

Get coding and earn more points to get a spot on the leaderboard📈''')


    
    
    
#     #Command to assign a channel to a product
#     @commands.command(aliases=['product','assign', 'assign channel', 'add channel'])
#     #@commands.has_any_role([])
#     @commands.has_permissions(administrator=True)
#     async def assign_channel_to_product(self, ctx, product_name=None):

#         #Check if product name was given
#         if product_name is None:
#             await ctx.channel.send("This command expects the name of the product as an argument like '!assign <product name>'")
#             return

#         #Check if channel is a valid type
#         if str(ctx.channel.type) not in ['text']:
#             await ctx.channel.send("Only text channels may be assigned to products")
#             return
        

#         #Check if given product name 
#         if not Product.is_product(product_name):
#             await ctx.channel.send(f"{product_name} is not a valid product name. Please try again.")
#             return
        
        
#         product = Product(name=product_name)
#         product.assign_channel(ctx.channel.id)
#         await ctx.channel.send(f"Channel successfully assigned to product {product_name}")
#         return
    
#     #error handling for assigning channel to product
#     @assign_channel_to_product.error
#     async def handle_assignment_error(self, ctx, error):
#         pass

#     # async def get_discord_metrics(self):
#     #     # print(1)
#     #     products = Product.get_all_products()

#     #     print(products)

#     #     discord_metrics = {
#     #         "measured_at": datetime.now(),
#     #         "metrics": dict()
#     #     }

#     #     # print(2)

#     #     for product in products:
#     #         # print(3)
#     #         discord_metrics["metrics"][product['name']] = {
#     #             "mentor_messages": 0,
#     #             "contributor_messages": 0
#     #         }
#     #         channel_id = product["channel"]
#     #         channel = await self.bot.fetch_channel(channel_id)
            
#     #         async for message in channel.history(limit=None):
#     #             # print(4)
#     #             if not isinstance(message.author, Member):
#     #                 # print(5)
#     #                 continue
#     #             if any(role.name.lower() == 'mentor' for role in message.author.roles):
#     #                 discord_metrics["metrics"][product["name"]]['mentor_messages'] +=1
                
#     #             if any(role.name.lower() == 'contributor' for role in message.author.roles):
#     #                 discord_metrics["metrics"][product['name']]['contributor_messages'] +=1
#     #     # print(6)
                
#     #     r = requests.post(f"""{os.getenv("FLASK_HOST")}/metrics/discord""", json=json.dumps(discord_metrics, indent=4, default=str))
#     #     # print(r.json())

#     #     #Store metrics

        
    
#     # async def get_github_metrics(self):

#     #     #Get all projects in the db
#     #     projects = Project.get_all_projects()

#     #     github_metrics = {
#     #         "updated_at": datetime.now(),
#     #         "metrics": dict()
#     #     }

#     #     for project in projects:
#     #         url_components = str(project['repository']).split('/')
#     #         url_components = [component for component in url_components if component != '']
#     #         # print(url_components)
#     #         [protocol, host, repo_owner, repo_name] = url_components
#     #         api = GithubAPI(owner=repo_owner, repo=repo_name)

#     #         (open_prs, closed_prs) = api.get_pull_request_count()
#     #         (open_issues, closed_issues) = api.get_issue_count()


#     #         github_metrics["metrics"][project["product"]] = {
#     #             "project": project["name"],
#     #             "repository": project["repository"],
#     #             "number_of_commits":  api.get_commit_count(),
#     #             "open_prs": open_prs,
#     #             "closed_prs": closed_prs,
#     #             "open_issues": open_issues,
#     #             "closed_issues": closed_issues
#     #         }
#     #     r = requests.post(f"""{os.getenv("FLASK_HOST")}/metrics/github""", json=json.dumps(github_metrics, indent=4, default=str))
#     #     # print(r.json())
        
#     #     # await ctx.channel.send(github_metrics)

#     #     return
    
#     # @tasks.loop(seconds=20.0)
#     # async def record_metrics(self):
#     #     # print('recording started')
#     #     await self.get_discord_metrics()
#     #     # print('discord done')
#     #     # await self.get_github_metrics()
#     #     # print('metrics recorded')

#     # @commands.command(aliases=['metrics'])
#     # # @tasks.loop(seconds=10.0)
#     # async def update_metrics_periodically(self, ctx, args):
#     #     if args == 'start':
#     #         self.record_metrics.start()
#     #         # await self.get_github_metrics()
            
#     #     elif args == 'stop':
#     #         self.record_metrics.stop()
        

#     #     return
    


async def setup(bot):
    await bot.add_cog(MetricsTracker(bot))
