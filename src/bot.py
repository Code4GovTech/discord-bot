import discord
from discord.ext import commands
import requests
import os
from requests.auth import HTTPBasicAuth
from db import conn, cur
import time

# Loading environment variables 
# load_dotenv()

# ----------- SETTING UP THE CLIENT -----------
client = discord.Client()
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="!", intents = intents)
client.remove_command("help")
# Buttons ext - "https://github.com/LLimeOn/discord_py_buttons"


# ------------- ENVIRONMENT VARIABLES ----------
WELCOME_CHANNEL= os.getenv('CHANNEL_ID')
API_ENDPOINT = os.getenv('API_ENDPOINT')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
token = os.getenv('PERSONAL_TOKEN')

# ------------- When Bot is ready ---------------
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

# -------------- Welcome-Function ---------------
@client.event
async def on_member_join(member):
  channel = client.get_channel(WELCOME_CHANNEL)
  embed1 = discord.Embed(title=f"ANNOUNCEMENT GUYS !",description=f"Welcome {member.mention}!",color=0x9208ea)
  await channel.send(embed=embed1)
  
  embed2 = discord.Embed(title=f"WELCOME TO OUR SERVER !",description=f"{member.mention} Please follow the rules and regulations and please register to our bot 'PULSE' to access the rest of our server! Have Fun!",color=0x9208ea)
  embed2.set_author(name="PULSE", url="https://github.com/Code4GovTech/discord-bot#c4gt-discord-bot", icon_url="https://raw.githubusercontent.com/ArshpreetS/Pulse/main/images/pulse.png?token=GHSAT0AAAAAABVIOJBGDJZAQGVPH7YS7CBSYU4ON2Q")
  await member.send(embed=embed2)

# ----------- When Someone Messages ----------
@client.event
async def on_message(message):
  discordId = message.author.id
  cur.execute(f"Update public.contributors set message_counter = message_counter + 1 where discord_id = '{discordId}'")
  conn.commit()
  await client.process_commands(message)

# ------------ Someone Reacted ---------------
@client.event
async def on_raw_reaction_add(reaction):
  discordId = reaction.user_id
  cur.execute(f"Update public.contributors set reaction_counter = reaction_counter + 1 where discord_id = '{discordId}'")
  conn.commit()

# --------------------------------------- COMMANDS ------------------------------------------------------

# ------------- Help-Function --------------
@client.command(aliases = ["HELP","Help"])
async def help(ctx):
	await ctx.send("Hello There! I am Pulse!\n \
    Get yourself register by typing `!register`\n \
      Check all projects using `!projects`\n \
        Check user Profiles using `!userInfo` ")
# --------------------------------------------

# -------------- UserInfo-embed ---------------
@client.command()
async def userInfo(ctx):
  if(ctx.message.mentions):
    target = ctx.message.mentions[0]
  else:
    target = ctx.author

  embed = discord.Embed(
      title = f"{target.name} #{target.discriminator}",
      colour = 0x9208ea
    )


# CONTRIBUTION INFO
  git_id = "Not Registered"
  commits = 0
  pr = 0
  issues = 0
  cur.execute(f"Select * from public.contributions where discord_id = '{target.id}'")
  responseUser = cur.fetchall()
  if responseUser != []:
    git_id = responseUser[0][1]
    commits = responseUser[0][2]
    pr = responseUser[0][3]
    issues = responseUser[0][4]

# MESSAGING INFO
  messageCounter = 0
  reactionCounter = 0
  cur.execute(f"Select * from public.contributors where discord_id = '{target.id}'")
  responseUser = cur.fetchall()
  if responseUser != []:
    messageCounter = responseUser[0][4]
    reactionCounter = responseUser[0][5]
  
  fields = [("User ID", target.name,True),
            ("Github ID", git_id,True),
            ("Server Joined", target.joined_at.strftime('%d/%m/%Y  %H:%M:%S'),False),
            ("Commits",commits,True),
            ("PRs",pr,True),
            ("Issues",issues,True),
            ("Messages",messageCounter,False),
            ("Reactions",reactionCounter,True),
  ]

  for name,value,inline in fields:
    embed.add_field(name=name, value=value, inline=inline)

  embed.set_author(name="USER-INFO", url="https://github.com/Code4GovTech/discord-bot#c4gt-discord-bot", icon_url="https://raw.githubusercontent.com/ArshpreetS/Pulse/main/images/pulse.png?token=GHSAT0AAAAAABVIOJBGDJZAQGVPH7YS7CBSYU4ON2Q")
  embed.set_footer(text=f"{target.name}'s Info")
  embed.set_thumbnail(url=f"{target.avatar_url}")
    
  
  await ctx.send(embed=embed)

# ---------------------------------------------------------


# ----------------- Register Function ----------------------
@client.command()
async def register(ctx):
  user = await client.fetch_user(ctx.message.author.id)
  embed = discord.Embed(
      title = f"{ctx.message.author.name}",
      colour = 0x9208ea
    )
  # Section 1 -> Opening The link
  embed.add_field(name="REGISTRATION", value="To get yourself register with Code4Gov - You must go to the [link](https://discord.com/api/oauth2/authorize?client_id=982859834355499088&redirect_uri=https%3A%2F%2Fbot.c4gt.samagra.io&response_type=code&scope=identify%20connections%20email)", inline=False)
  # Sharing the code -> 
  embed.add_field(name="Share The Code", value="You must share the code with us using the command `!code <YOUR CODE>`",inline=False)
 
  embed.set_author(name="REGISTRATION", url="https://github.com/Code4GovTech/discord-bot#c4gt-discord-bot", icon_url="https://raw.githubusercontent.com/ArshpreetS/Pulse/main/images/pulse.png?token=GHSAT0AAAAAABVIOJBGDJZAQGVPH7YS7CBSYU4ON2Q")
  
  await user.send(embed=embed)
# ------------------------------------------------------------------------

# -------------- Add the Code ----------------
@client.command()
async def code(ctx):
  code = str((ctx.message.content).split()[1])
  
  data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_URI
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  response = requests.post("https://discord.com/api/v10/oauth2/token", data=data, headers=headers)
  
  access_token = response.json()['access_token']
  refresh_token = response.json()['refresh_token']
  response2 = requests.get("https://discord.com/api/v10/users/@me/connections",headers={'Authorization': 'Bearer ' + access_token})
  print(response2.json())
  git_id = ""
  d_id = ctx.message.author.id
  for connect in response2.json():
    if connect['type'] == "github":
      git_id = connect['name']
      break
  if (git_id == ""):
    ctx.send("Your Discord ID isn't connected to github account yet!\n Please do that first")
  else:
    cur.execute(f"INSERT INTO public.contributors (Discord_id,Github_id,Access_token,Refresh_token) \
  		VALUES ('{d_id}','{git_id}','{access_token}','{refresh_token}')")
    cur.execute(f"INSERT INTO public.contributions (Discord_id,Github_id) \
      VALUES ('{d_id}','{git_id}')")
    conn.commit()
    await ctx.send(f"{git_id}... You are registered!")
    var = discord.utils.get(ctx.message.guild.roles, name = "accessTest")
    await ctx.message.author.add_roles(var)
# -------------------------------------------------------------------------------------------------------------


# ----------------- Listing Projects --------------------
@client.command()
async def projects(ctx):
  embed = discord.Embed(
      title = "Choose Project",
      colour = 0x9208ea
    )
  
  # Getting the data from the database
  cur.execute("Select * from public.projects order by name")
  showProjects = ""
  S_no = 1
  rows = cur.fetchall()
  for i in rows:
    showProjects = showProjects + f"{S_no}. " + i[0] + "\n"
    S_no += 1


  # Section 1 -> Opening The link
  embed.add_field(name="Repositories", value=showProjects, inline=False)
  embed.add_field(name="Specific Repo", value="Choose the repo using `!projectInfo <repo_number>`",inline=False)
  embed.add_field(name="Unassigned Issues", value="Get all Unassigned issues using `!issues <repo_number>`",inline=False)
  embed.set_author(name="Code4Gov", url="https://github.com/Code4GovTech/discord-bot#c4gt-discord-bot", icon_url="https://raw.githubusercontent.com/ArshpreetS/Pulse/main/images/pulse.png?token=GHSAT0AAAAAABVIOJBGDJZAQGVPH7YS7CBSYU4ON2Q")
  await ctx.send(embed=embed)

# ------------------------------------------------------------------

# ------------- Issues -------------------
@client.command()
async def issues(ctx):
  response = ctx.message.content.split()[1]
   # Fetching the correct data
  cur.execute(f"Select * from public.projects order by name")
  allProjects = cur.fetchall()
  target = allProjects[int(response) - 1]

  # Github API CALL
  apiIssue = "https://api.github.com/repos" "/" + target[2].split("/")[-2] + "/" + target[1] + "/" + "issues"
  apiResponse = requests.get(apiIssue)

  # Create an Embed
  embed = discord.Embed(
      title = f"Unassigned Issues in {target[0]}",
      colour = 0x9208ea
    )
  for obj in apiResponse.json():
    if (len(obj["assignees"]) == 0) and not ("pull_request" in obj):
      embed.add_field(name=f"{ obj['title'] }", value=f"Created by { obj['user']['login'] } \n **[link]({obj['html_url']})**",inline=False)

  embed.set_author(name="Code4Gov", url="https://github.com/Code4GovTech/discord-bot#c4gt-discord-bot", icon_url="https://raw.githubusercontent.com/ArshpreetS/Pulse/main/images/pulse.png?token=GHSAT0AAAAAABVIOJBGDJZAQGVPH7YS7CBSYU4ON2Q")
  
  await ctx.send(embed=embed)
# -------------------------------------------

# ------------- Project Infos ---------------
@client.command()
async def projectInfo(ctx):
  response = ctx.message.content.split()[1]
  
  # Fetching the correct data
  cur.execute(f"Select * from public.projects order by name")
  allProjects = cur.fetchall()
  target = allProjects[int(response) - 1]

  

  embed = discord.Embed(
      title = f"Code4Gov",
      colour = 0x9208ea
    )
  embed.add_field(name="Documentation",value=f"[Link]({target[3]})",inline=False)
  embed.add_field(name="Repo",value=f"[{target[1]}]({target[2]})")
  embed.add_field(name=f"Learning Path",value=target[4],inline=False)
 
  embed.set_author(name=f"{target[0]}", url=f"", icon_url="https://raw.githubusercontent.com/ArshpreetS/Pulse/main/images/pulse.png?token=GHSAT0AAAAAABVIOJBGDJZAQGVPH7YS7CBSYU4ON2Q")
  embed.set_footer(text=f"{target[0]}'s Info")
  await ctx.send(embed=embed)
# ---------------------------------------------

# --------------- Commits adder Function --------------
def addCommits():
  cur.execute("select distinct repo_name, repo_url from public.projects")
  allProjects = cur.fetchall()

  for project in allProjects:
    print(f"{project[0]} and {project[1]}")
    apiURL = "https://api.github.com/repos/" + project[1].split("/")[-2] + "/" + project[0] + "/commits"
    apiResponse = requests.get(apiURL,auth=HTTPBasicAuth('ArshpreetS', token))
    for commit in apiResponse.json():
      id = commit["sha"]
      if commit["author"] != None:
        user = commit["author"]["login"] 
      else:
        user = ""
      message = commit["commit"]["message"]
      date = commit["commit"]["author"]["date"]
      date = date[:10]
      cur.execute(f"select * from commits where commit_id = '{id}'")
      responseCommits = cur.fetchall()
      if (responseCommits == []):
        cur.execute(f'''INSERT INTO public.commits (Commit_id,Git_id,Date,Message,Repo) \
          VALUES ('{id}','{user}','{date}','{message.replace("'","")}','{project[0]}')''')
        cur.execute(f"UPDATE public.contributions SET commits = commits + 1 where github_id = '{user}'")
    time.sleep(5)
  conn.commit()
# ---------------------------------------------------------



# --------------------- PR adder Function -------------------
def addPRs():
  cur.execute("select distinct repo_name, repo_url from public.projects")
  allProjects = cur.fetchall()

  for project in allProjects:
    print(f"{project[0]} and {project[1]}")
    apiURL = "https://api.github.com/repos/" + project[1].split("/")[-2] + "/" + project[0] + "/pulls?state=all"
    apiResponse = requests.get(apiURL,auth=HTTPBasicAuth('ArshpreetS', token))
    for pull in apiResponse.json():
      id = pull["number"]
      if pull["head"]["repo"] == None:
        repoName = ""
      else:
        repoName = pull["head"]["repo"]["name"]
      user = pull["user"]["login"]
      title = pull["title"]
      message = pull["body"]
      if message != None:
        message = message.replace("'"," ")
      if title != None:
        title = title.replace("'"," ")
      cur.execute(f"Select * from public.pullrequests where id = '{id}' and repo = '{repoName}'")
      responsePull = cur.fetchall()
      if (responsePull == []):
        cur.execute(f'''Insert into public.pullrequests (id,repo,git_user,message,title) \
          values ('{id}','{repoName}','{user}','{ message }','{title}')''')
        cur.execute(f"Update public.contributions set pr = pr + 1 where github_id = '{user}'")
    time.sleep(5)
  conn.commit()
# --------------------------------------------------------------------


# --------------------- Issues adder Function ------------------------
def addissues():
  cur.execute("select distinct repo_name, repo_url from public.projects")
  allProjects = cur.fetchall()

  for project in allProjects:
    print(f"{project[0]} and {project[1]}")
    apiURL = "https://api.github.com/repos/" + project[1].split("/")[-2] + "/" + project[0] + "/issues?state=all"
    apiResponse = requests.get(apiURL,auth=HTTPBasicAuth('ArshpreetS', token))
    for issue in apiResponse.json():
      if 'pull_request' in issue:
        continue
      id = issue["number"]
      repoName = project[0]
      user = issue["user"]["login"]
      title = issue["title"]
      message = issue["body"]
      if message != None:
        message = message.replace("'"," ")
      if title != None:
        title = title.replace("'"," ")
      cur.execute(f"Select * from public.issues where id = '{id}' and repo = '{repoName}'")
      responsePull = cur.fetchall()
      if (responsePull == []):
        cur.execute(f'''Insert into public.issues (id,repo,git_user,message,title) \
          values ('{id}','{repoName}','{user}','{ message }','{title}')''')
        cur.execute(f"Update public.contributions set issues = issues + 1 where github_id = '{user}'")
    time.sleep(3)
  conn.commit()
# --------------------------------------------------------------------


# ---------------------- DM message --------------------------
@client.command()
async def dm(ctx):
  user = await client.fetch_user(ctx.message.author.id)
  await user.send(" ".join((ctx.message.content).split()[1:]))
# ------------------------------------------------------------


# client.run(os.getenv("DISCORD_TOKEN"))
