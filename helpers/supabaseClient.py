import os

from discord import Member, User
from supabase import Client, create_client

from helpers.roleHelpers import lookForChapterRoles, lookForGenderRoles


class SupabaseClient:
    def __init__(self, url=None, key=None) -> None:
        self.supabase_url = url if url else os.getenv("SUPABASE_URL")
        self.supabase_key = key if key else os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def read(self, table, query_key, query_value, columns="*"):
        data = (
            self.client.table(table)
            .select(columns)
            .eq(query_key, query_value)
            .execute()
        )
        # data.data returns a list of dictionaries with keys being column names and values being row values
        return data.data

    def read_by_order_limit(
        self,
        table,
        query_key,
        query_value,
        order_column,
        order_by=False,
        limit=1,
        columns="*",
    ):
        data = (
            self.client.table(table)
            .select(columns)
            .eq(query_key, query_value)
            .order(order_column)
            .limit(limit)
            .execute()
        )
        return data.data

    def read_all(self, table):
        data = self.client.table(table).select("*").execute()
        return data.data

    def update(self, table, update, query_key, query_value):
        data = (
            self.client.table(table).update(update).eq(query_key, query_value).execute()
        )
        return data.data

    def insert(self, table, data):
        data = self.client.table(table).insert(data).execute()
        return data.data

    def memberIsAuthenticated(self, member: Member | User):
        data = (
            self.client.table("contributors_registration")
            .select("*")
            .eq("discord_id", member.id)
            .execute()
            .data
        )
        if data:
            return True
        else:
            return False

    def addChapter(self, orgName: str, type: str):
        data = (
            self.client.table("chapters")
            .upsert({"type": type, "org_name": orgName}, on_conflict="org_name")
            .execute()
        )
        return data.data

    def updateContributor(self, contributor: Member):
        table = "contributors_discord"

        chapters = lookForChapterRoles(contributor.roles)
        gender = lookForGenderRoles(contributor.roles)

        self.client.table(table).upsert(
            {
                "discord_id": contributor.id,
                "discord_username": contributor.name,
                "chapter": chapters[0] if chapters else None,
                "gender": gender,
                "joined_at": contributor.joined_at.isoformat(),
            },
            on_conflict="discord_id",
        ).execute()
