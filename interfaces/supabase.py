import os
from supabase import create_client, Client
from discord import Member, User
from helpers import lookForCollegeRoles, lookForGenderRoles

class SupabaseInterface:
    def __init__(self, table, url=None, key=None) -> None:

        self.supabase_url = url if url else os.getenv("SUPABASE_URL")
        self.supabase_key = key if key else os.getenv("SUPABASE_KEY")
        self.table = table
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    def read(self, query_key, query_value, columns="*"):
        data = self.client.table(self.table).select(columns).eq(query_key, query_value).execute()
        #data.data returns a list of dictionaries with keys being column names and values being row values
        return data.data

    def read_by_order_limit(self, query_key, query_value, order_column, order_by=False, limit=1, columns="*"):
        data = self.client.table(self.table).select(columns).eq(query_key, query_value).order(order_column).limit(limit).execute()
        return data.data
    
    def read_all(self):
        data = self.client.table(self.table).select("*").execute()
        return data.data
        
    def update(self, update, query_key, query_value):
        data = self.client.table(self.table).update(update).eq(query_key, query_value).execute()
        return data.data

    def insert(self, data):
        data = self.client.table(self.table).insert(data).execute()
        return data.data
    
    def memberIsAuthenticated(self, member: Member | User):
        data = self.client.table("contributors").select("*").eq("discord_id", member.id).execute().data
        if data:
            return True
        else:
            return False
    
    def addChapter(self, orgName:str, type:str):
        data = self.client.table("chapters").insert(
            {
                "type": type,
                "org_name": orgName
            }
        ).execute()
    
    def updateContributor(self, contributor: Member):
        table = "__contributors"

        chapters = lookForCollegeRoles(contributor.roles)

        self.client.table(table).upsert({
            "discord_id":contributor.id,
            "discord_username": contributor.name,
            "chapter": chapters[0] if chapters else None,
            "gender": lookForGenderRoles(contributor.roles)
        }).execute()



    ''' 
    def saveMemberAsContributor(self, member: Member|User):
        self.client.table("contributors").insert({
            "discord_id": member.id,
            "discord_username": member.name
        })'''