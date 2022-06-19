
# code = str((ctx.message.content).split()[1])
import requests
from db import conn, cur
import os

def get_user_tokens(code):
    data = {
        'client_id': os.getenv("CLIENT_ID"),
        'client_secret': os.getenv("CLIENT_SECRET"),
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': os.getenv("REDIRECT_URI")
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post("https://discord.com/api/v10/oauth2/token", data=data, headers=headers)
    print(data, headers, response)
    user_access_token = response.json()['access_token']
    user_refresh_token = response.json()['refresh_token']
    return {
        "access_token": user_access_token, 
        "refresh_token": user_refresh_token
    }

def get_github_id(user_access_token):
  github_connection_response = requests.get("https://discord.com/api/v10/users/@me/connections",headers={'Authorization': 'Bearer ' + user_access_token})
  git_id = ""
  for connect in github_connection_response.json():
    if connect['type'] == "github":
        git_id = connect['name']
        return git_id

def get_discord_id(user_access_token):
    discord_connection_response = requests.get("https://discord.com/api/v10/users/@me",headers={'Authorization': 'Bearer ' + user_access_token})
    return discord_connection_response.json()['id']

def persist_tokens(user_access_token, user_refresh_token, github_id, discord_id):
    print(user_access_token, user_refresh_token, github_id, discord_id)
    cur.execute(f"INSERT INTO public.contributors (Discord_id, Github_id, Access_token, Refresh_token) \
        VALUES ('{discord_id}','{github_id}','{user_access_token}','{user_refresh_token}')")
    cur.execute(f"INSERT INTO public.contributions (Discord_id, Github_id) \
        VALUES ('{discord_id}','{github_id}')")
    conn.commit()