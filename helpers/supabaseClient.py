import os

from discord import Member, User
from supabase import Client, create_client

from helpers.roleHelpers import lookForRoles

class SupabaseClient:
    def __init__(self, url=None, key=None) -> None:
        self.supabase_url = url if url else os.getenv("SUPABASE_URL")
        self.supabase_key = key if key else os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def getStatsStorage(self, fileName):
        return self.client.storage.from_("c4gt-github-profile").download(fileName)

    def logVCAction(self, user, action):
        return (
            self.client.table("vc_logs")
            .insert(
                {"discord_id": user.id, "discord_name": user.name, "option": action}
            )
            .execute()
        )

    def getLeaderboard(self, id: int):
        data = (
            self.client.table("leaderboard").select("*").eq("discord_id", id).execute()
        )
        return data.data

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

    def read_all_active(self, table):
        data = self.client.table(table).select("*").eq('is_active', 'true').execute()
        return data.data

    def update(self, table, update, query_key, query_value):
        data = (
            self.client.table(table).update(update).eq(query_key, query_value).execute()
        )
        return data.data

    def insert(self, table, data):
        data = self.client.table(table).insert(data).execute()
        return data.data

    def memberIsAuthenticated(self, member: Member):
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

    def addChapter(self, roleId: int, orgName: str, type: str):
        data = (
            self.client.table("chapters")
            .upsert(
                {"discord_role_id": roleId, "type": type, "org_name": orgName},
                on_conflict="discord_role_id",
            )
            .execute()
        )
        return data.data

    def deleteChapter(self, roleId: int):
        data = (
            self.client.table("chapters")
            .delete()
            .eq("discord_role_id", roleId)
            .execute()
        )
        return data.data

    def updateContributor(self, contributor: Member):
        table = "contributors_discord"

        user_roles = lookForRoles(contributor.roles)

        self.client.table(table).upsert(
            {
                "discord_id": contributor.id,
                "discord_username": contributor.name,
                "chapter": user_roles["chapter_roles"][0] if user_roles["chapter_roles"] else None,
                "gender": user_roles["gender"],
                "joined_at": contributor.joined_at.isoformat(),
                "country": user_roles["country"],
                "city": user_roles["city"],
                "experience": user_roles["experience"]
            },
            on_conflict="discord_id",
        ).execute()

    def updateContributors(self, contributors: [Member]):
        table = "contributors_discord"
        data = []
        for contributor in contributors:
            user_roles = lookForRoles(contributor.roles)
            chapters = user_roles["chapter_roles"]
            gender = user_roles["gender"]
            data.append(
                {
                    "discord_id": contributor.id,
                    "discord_username": contributor.name,
                    "chapter": chapters[0] if chapters else None,
                    "gender": gender,
                    "joined_at": contributor.joined_at.isoformat(),
                    "is_active": 'true'
                }
            )

        self.client.table(table).upsert(
            data,
            on_conflict="discord_id",
        ).execute()

    def deleteContributorDiscord(self, contributorDiscordIds):
        table = "contributors_discord"
        for id in contributorDiscordIds:
            self.client.table(table).delete().eq("discord_id", id).execute()

    def invalidateContributorDiscord(self, contributorDiscordIds):
        table = "contributors_discord"
        for id in contributorDiscordIds:
            self.client.table(table).update({'is_active': 'false'}).eq('discord_id', id).execute()
