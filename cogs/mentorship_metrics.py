from discord.ext import commands
import re, sys,json, os
import requests
from fuzzywuzzy import fuzz
from utils.db import SupabaseInterface
import mistune



def parse_markdown_for_urls(markdown):
  """Parses a Markdown file for all URLs.

  Args:
    markdown_file: The path to the Markdown file.

  Returns:
    A list of all URLs found in the Markdown file.
  """
  parser = mistune.Markdown()
  html_text = parser.reset().convert(markdown)

  urls = []
  for match in re.findall(r"(https?://\S+)", html_text):
    urls.append(match)

  return urls

def return_ast(md):
    markdown = mistune.create_markdown(renderer=None)
    return markdown(md)

def find_urls(obj, urls):
  """Finds all URLs in a nested object.

  Args:
    obj: The nested object to search.
    urls: A list to store the URLs found.
  """

  if isinstance(obj, dict):
    if "url" in obj:
      urls.append(obj["url"])
    for value in obj.values():
      find_urls(value, urls)
  elif isinstance(obj, list):
    for value in obj:
      find_urls(value, urls)

md = '''---
title: Week 1
author: Manas Sivakumar  
---

## Milestones
- Fix Bash Script to Generate Docker File
- GitHub Action to Build and Push Images to ghcr.io

## Screenshots / Videos 

## Contributions
- [Bash Script](https://github.com/Samagra-Development/ai-tools/issues/118)
- [Github Worflow](https://github.com/Samagra-Development/ai-tools/issues/132)
- [GitHub Workflow](https://github.com/Samagra-Development/ai-tools/issues/120)

## Learnings
Exposure to Github Actions and Access Permissions in Github Repository. '''

files = [
    "2023-07-07.md",
    "2023-07-14.md",
    "2023-07-21.md",
    "2023-07-28.md",
    "2023-08-04.md",
    "2023-08-11.md",
    "2023-08-18.md",
    "2023-08-25.md",
    "2023-09-01.md"
]

# directories = {
#     "ABDM":{
#         "CONSENT_MANAGEMENT": [],
#         "Loinc-India": [],
#         "Subscription-management": [],
#     },
#     "AI Tools": {
#         "Deployment Optimization": [],
#         "Document Uploader": [],
#         "Neural Coref": [],
#         "Dictionary Augmented Transformers":[]
#     },
#     "Avni": {
#         "Canned Analytics": []
#     },
#     "Bahmni":{
#         "Ability to book an appointment via WhatsApp": [],
#         "Patient Portal": [],
#         "Standalone Document Upload Module": [],
#     },
#     "BeckN": {
#         "BAP Backend SDK & Boilerplate UI": [],
#         "BPP Backend SDK & Boilerplate UI": [],
#         "Backn Smart Policy Infrastructure": [],
#         "Beckn Certification Suite": [],
#         "Beckn DSEP - Scaling and Resilience Implementation": [],
#         "Beckn Energy Interface": [],
#         "Beckn Mobility Interface": [],
#         "Beckn in a box": [],
#         "Beckn-enabled-Reputation-Infrasructure": [],
#         "Decentralized Health Protocol": [],
#         "QR Code Generation and Interpretation": [],
#         "Synapse": [],
#     },
#     "CARE": {
#         "Adding typesafety to teleicu middleware": [],
#         "Cypress Test for All Major Functionalities of CARE": [],
#         "List and Detail Serializer": [],
#         "Live Camera Feed Enhancement": [],
#         "RedesignDoctorNotes": []
#     },
#     "CORD Network":{
#        "IntegrationWithSunbirdRC": []

#     },
#     "DDP": {
#         "Airbyte connector for Avni": [],
#         "Set up a monitoring system": []  
#     },
#     "DIGIT": {
#         "JWT based Authentication and Authorization": [],
#         "Jurisdiction Based Workflow": [],
#         "Redesign and rewrite of MDMS": [],
#         "Vehicle Tracker": [],
#     },
#     "DIKSHA": {
#         "Discovering Tutors and Mentor using DSEP protocol": [],
#         "Learner Passbook integration with Sunbird ED Apps":[],
#         "Story":[],
#     },
#     "DevOps Pipeline": {
#         "Build v2 of devops pipeline": []
#     },
#     "Doc Generator": {
#         "Creating an UI": [],
#         "Upgrade Doc-Gen to use Templater": []
#     },
#     "Farmstack": {
#         "API Builder": []
#     },
#     "Glific": {
#         "Glific Mobile": [],
#         "Integrate with a subscription based billing system": []
#     },
#     "Health Claims Exchange": {
#         "Build Javascript SDK for HCX Participant System to help in integrating with HCX": [],
#         "Python SDK": []
#     },
#     "Karmayogi": {
#         "Competency Passbook for Officials": [],
#         "Integrate the Content translation UI into iGOT Karamayogi": [],
#         "Discovering Mentors and Training Institutes": [],
#         "Integrate the Content translation UI into iGOT Karamayogi": [],
#         "LLMs for Question Answering 1": [],
#         "LLMs for Question Answering 2": []
#     },
#     "ODK Extension Collection": {
#         "Get form response as JSON and Send response to Custom Server": [],
#         "Publish extensions as a library on maven central": []
#     },
#     "QuML": {
#         "Enhanced QuML player": []
#     },
#     "Quiz Creator": {
#        "Quiz Creator": []
#     },
#     "Solve Ninja Chatbot": {
#         "Voice-to-text Integration": []
#     },
#     "Sunbird DevOps": {
#        "Code and Container Security": []

#     },
#     "Sunbird ED": {
#         "Review Enhancement": [],
#         "Search Widget or Discovery": [],
#         "Support for Optional Material in Course": [],
#         "content detail page as widget": []
#     },
#     "Sunbird Knowlg": {
#        "One click installation in aws": []
    
#     },
#     "Sunbird Lern": {
#         "Integrate with non-Keycloak authentication system": [],
#         "Mocking Integration Points": []
#     },
#     "Sunbird Obsrv": {
#         "Enhance Sunbird Ed Data Pipeline to Operate on Sunbird Obsrv": [],
#         "revampTheObsrvSink": []
#     },
#     "Sunbird RC": {
#         "Admin Portal to Build Registry and Credentialing Platform": [],
#         "Credential Sharing Consent and Share Credentials": [],
#         "Starter pack location master": []
#     },
#     "Sunbird Saral": {
#         "Saral-Layout and ROI generation": []
#     },
#     "Sunbird UCI": {
#         "Telemetry Dashboard": [],
#         "Refactoring Components": []
#     },
#     "Sunbird inQuiry": {
#         "Auto generates questions in QuML": [],
#         "Embedding QuML player": [],
#         "Match The Following Type Questions Implementation": [],
#         "audio-upload-feature": []
#     },
#     "Template creation portal": {
#         "Template creation portal": []
#     },
#     "Text2SQL": {

#     },
#     "TrustBot and POSHpal": {

#     },
#     "TrustIn":{

#     },
#     "Unnati":{

#     },
#     "WarpSQL":{
#         "Plugins, Disaster Recovery, Benchmarking": []
#     },
#     "Workflow":{
#         "Workflow":[]
#     },
#     "Yaus": {
#         "Frontend And Deep Linking": []
#     },
#     "cQube": {
#         "Input File Validator": [],
#         "cQubeChat": []
#     }
# }

testText = '''
---
title: Week 7
author: Suyash Gau
---

## Milestones
- [ ] Give the description about Milestone 1
- [ ] Give the description about Milestone 2
- [ ] Give the description about Milestone 3
- [ ] Give the description about Milestone 4

## Screenshots / Videos 

## Contributions

## Learnings'''


def getPR(PRurl):
    components = PRurl.split('/')
    owner, repo,number = components[-4], components[-3], components[-1]
    url = url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{number}'

    headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {os.getenv("GITHUB_PAT")}'
        }
    
    try:
        response = requests.get(url, headers=headers)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return response.json()
        else:
            # If the request was not successful, raise an exception or return None.
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occurred during the request (e.g., connection error, timeout).
        print(f"An error occurred: {e}")
        return None
   
def send_get_request(url):
    headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {os.getenv("GITHUB_PAT")}'
        }
    try:
        response = requests.get(url, headers=headers)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return response.text
        else:
            # If the request was not successful, raise an exception or return None.
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occurred during the request (e.g., connection error, timeout).
        print(f"An error occurred: {e}")
        return None
    
def generate_file_tree():
    result = send_get_request("https://api.github.com/repos/Code4GovTech/c4gt-milestones/contents/docs/2023?ref=main")
    # print(result)
    productFolders = json.loads(result)
    folderStruct = dict()
    for pFolder in productFolders:
        folderStruct[pFolder["name"]] = dict()
        projectFolders = json.loads(send_get_request(pFolder["url"]))
        for project in projectFolders:
            # print(project, type(project))
            if isinstance(project, dict) and project["type"] == "dir":
                folderStruct[pFolder["name"]][project["name"]] = list()
    return folderStruct

def is_default_text(markdown):
    defaultText = '''---
title: Week 1
author: Yashi Gupta  
---

## Milestones
- [ ] Give the description about Milestone 1
- [ ] Give the description about Milestone 2
- [ ] Give the description about Milestone 3
- [ ] Give the description about Milestone 4

## Screenshots / Videos 

## Contributions

## Learnings'''

    if fuzz.ratio(markdown, defaultText)>90 :
        return True
    return False
    


def isPrUrl(url):
    # if a url ends in 'pull/number' it's a pull request
    pattern = r"pull/\d+$"
    match = re.search(pattern, url)
    return match is not None

def addPullRequest(pull, project):
    p = {
                            "pr_url": pull["url"],
                            "pr_id": pull["id"],
                            "pr_node_id": pull["node_id"],
                            "html_url": pull["html_url"],
                            "status": pull["state"],
                            "title": pull["title"],
                            "raised_by_username": pull["user"]["login"],
                            "raised_by_id": pull["user"]["id"],
                            "body": pull["body"],
                            "created_at": pull["created_at"],
                            "updated_at": pull["updated_at"],
                            "closed_at": pull["closed_at"],
                            "merged_at": pull["merged_at"],
                            "assignees": pull["assignees"],
                            "requested_reviewers": pull["requested_reviewers"],
                            "labels": pull["labels"],
                            "review_comments_url": pull["review_comments_url"],
                            "comments_url": pull["comments_url"],
                            "repository_id": pull["base"]["repo"]["id"],
                            "repository_owner_name": pull["base"]["repo"]["owner"]["login"],
                            "repository_owner_id": pull["base"]["repo"]["owner"]["id"],
                            "repository_url": pull["base"]["repo"]["html_url"],
                            "merged_by_username":pull["merged_by"]["login"] if pull.get("merged_by") else None,
                            "merged_by_id":pull["merged_by"]["id"] if pull.get("merged_by") else None,
                            "merged": pull["merged"] if pull.get("merged") else None,
                            "number_of_commits": pull["commits"],
                            "number_of_comments": pull["comments"] ,
                            "lines_of_code_added": pull["additions"] ,
                            "lines_of_code_removed": pull["deletions"] ,
                            "number_of_files_changed": pull["changed_files"],
                            "project_folder_label": project

                    }
    try:
        SupabaseInterface("mentorship_program_website_pull_request").insert(p)
    except Exception:
        try:
          SupabaseInterface("mentorship_program_website_pull_request").update(p, "pr_id", p["pr_id"])
        except Exception as e:
           print(e)

def insertMilestones(data):
    try:
        SupabaseInterface("mentorship_program_website_has_updated").insert(data)
    except Exception as e:
        try:
          SupabaseInterface("mentorship_program_website_has_updated").update(data, "project_folder", data["project_folder"])
        except Exception as e:
          print(e)
          return



class MentorshipMetrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def update_mentorship_data(self, ctx):
       await ctx.send("scanning latest file structure in repository...")
       directories = generate_file_tree()

       productNumber = 1
       for product, projects in directories.items():
        await ctx.send(f'{product}: {productNumber}/{len(directories.keys())}')
        productNumber+=1
        for project in projects.keys():
            count = 1
            data = {
                    "project_folder": project,
                    "product": product,
                    "all_links": []
                }
            for filename in files:
                url = f'https://raw.githubusercontent.com/Code4GovTech/c4gt-milestones/main/docs/2023/{product}/{project}/updates/{filename}'
                url = requests.utils.quote(url, safe='/:')
                # await ctx.send(project)
                print(project)
                markdown = send_get_request(url)
                if is_default_text(markdown=markdown):
                    data[f"week{count}_is_default_text"] =True
                else:
                    data[f"week{count}_is_default_text"]=False
                urls = []
                find_urls(return_ast(markdown), urls)
                data["all_links"]+=urls
                for url in urls:
                    print(url, isPrUrl(url))
                    if isPrUrl(url):
                        pull = getPR(url)
                        print(pull)
                        try:
                            addPullRequest(pull, project)
                        except Exception as e:
                            print(e)
                            continue
                count+=1
                
                    
            insertMilestones(data)

async def setup(bot):
    await bot.add_cog(MentorshipMetrics(bot))

# directories = generate_file_tree()

# productNumber = 1
# for product, projects in directories.items():
# # await ctx.send(f'{product}: {productNumber}/{len(directories.keys())}')
#     productNumber+=1
#     for project in projects.keys():
#         count = 1
#         data = {
#                 "project_folder": project,
#                 "product": product,
#                 "all_links": []
#             }
#         for filename in files:
#             url = f'https://raw.githubusercontent.com/Code4GovTech/c4gt-milestones/main/docs/2023/{product}/{project}/updates/{filename}'
#             url = requests.utils.quote(url, safe='/:')
#             # await ctx.send(project)
#             print(project)
#             markdown = send_get_request(url)
#             if is_default_text(markdown=markdown):
#                 data[f"week{count}_is_default_text"] =True
#             else:
#                 data[f"week{count}_is_default_text"]=False
#             urls = []
#             find_urls(return_ast(markdown), urls)
#             data["all_links"]+=urls
#             for url in urls:
#                 print(url, isPrUrl(url))
#                 if isPrUrl(url):
#                     pull = getPR(url)
#                     print(pull)
#                     try:
#                         addPullRequest(pull, project)
#                     except Exception as e:
#                         print(e)
#                         continue
#             count+=1
            
                
#         insertMilestones(data)
