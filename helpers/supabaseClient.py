import os

from discord import Member, User
from supabase import Client, create_client
from helpers.roleHelpers import lookForChapterRoles, lookForGenderRoles
from dotenv import load_dotenv            
from sqlalchemy import create_engine,select,desc,update,delete
from sqlalchemy.orm import sessionmaker
from models import *

load_dotenv()


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

            
class PostgresClient:
    def __init__(self):
        DB_HOST = os.getenv('POSTGRES_DB_HOST')
        DB_NAME = os.getenv('POSTGRES_DB_NAME')
        DB_USER = os.getenv('POSTGRES_DB_USER')
        DB_PASS = os.getenv('POSTGRES_DB_PASS')
        
        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}')
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def convert_dict(self,data):
        try:
            if type(data) == list:
                data = [val.to_dict() for val in data]
            else:
                return [data.to_dict()]
            
            return data
        except Exception as e:
            print(e)
            raise Exception
        
    def getStatsStorage(self, fileName):
        return self.client.storage.from_("c4gt-github-profile").download(fileName)

    
    def logVCAction(self,user, action):
        try:
            new_log = VcLogs(discord_id=user.id, discord_name=user.name, option=action)
            self.session.add(new_log)
            self.session.commit()
            return self.convert_dict(new_log)
        except Exception as e:
            self.session.rollback()
            print("Error logging VC action:", e)
            return None
    
    def getLeaderboard(self, id: int):        
        data = self.session.query(Leaderboard).where(Leaderboard.discord_id == id).all()
        return self.convert_dict(data)

    
    def read(self, table_class, query_key, query_value, columns=None):
        try:
            stmt = select(table_class)           
            stmt = stmt.where(getattr(table_class, query_key) == query_value)
            
            if columns:
                stmt = stmt.with_only_columns(*(getattr(table_class, col) for col in columns))
                result = self.session.execute(stmt)
                rows = result.fetchall()
                column_names = [col.name for col in stmt.columns]
                data = [dict(zip(column_names, row)) for row in rows]
                return data
                                
            result = self.session.execute(stmt)
            return self.convert_dict(result.scalars().all())

        except Exception as e:
            print(f"Error reading data from table '{table_class}':", e)
            return None
        
      

    def read_by_order_limit(self, table_class, query_key, query_value, order_column, order_by=False, limit=1, columns="*"):
        try:
            stmt = select(table_class)
            stmt = stmt.where(getattr(table_class, query_key) == query_value)
            if order_by:
                stmt = stmt.order_by(desc(getattr(table_class, order_column)))
            else:
                stmt = stmt.order_by(getattr(table_class, order_column))
            
            stmt = stmt.limit(limit)            
            if columns != "*":
                stmt = stmt.with_only_columns(*(getattr(table_class, col) for col in columns))
            
            result = self.session.execute(stmt)
            results = result.fetchall()
            
            # Convert results to list of dictionaries
            column_names = [col['name'] for col in result.keys()]
            data = [dict(zip(column_names, row)) for row in results]
            
            return data
        
        except Exception as e:
            print("Error reading data:", e)
            return None

    def read_all(self, table):       
        data = self.session.query(table).all()
        return self.convert_dict(data)

    def update(self, table_class, update_data, query_key, query_value):
        try:
            stmt = (
                update(table_class)
                .where(getattr(table_class, query_key) == query_value)
                .values(update_data)
                .returning(*[getattr(table_class, col) for col in update_data.keys()])  # Return updated columns
            )
            
            result = self.session.execute(stmt)
            self.session.commit()
            updated_record = result.fetchone() 
            
            if updated_record:
                updated_record_dict = dict(zip(result.keys(), updated_record))
                return updated_record_dict
            else:
                return None
        except Exception as e:
            import pdb;pdb.set_trace()
            print("Error updating record:", e)
            return None


    def insert(self, table, data):
        try:
            new_record = table(**data)
            self.session.add(new_record)
            self.session.commit()
            return new_record.to_dict() 
        except Exception as e:
            print("Error inserting data:", e)
            self.session.rollback()  # Rollback in case of error
            return None

    
    def memberIsAuthenticated(self, member: Member):
        data = self.session.query(ContributorsRegistration).where(ContributorsRegistration.discord_id == member.id).all()
        if data:
            return True
        else:
            return False

    def addChapter(self, roleId: int, orgName: str, type: str):
        try:
            existing_record = self.session.query(Chapters).filter_by(discord_role_id=roleId).first()

            if existing_record:
                existing_record.type = type
                existing_record.org_name = orgName
            else:
                new_record = Chapters(discord_role_id=roleId, type=type, org_name=orgName)
                self.session.add(new_record)

            self.session.commit()
            return existing_record.to_dict() if existing_record else new_record.to_dict()
        except Exception as e:
            print("Error adding or updating chapter:", e)
            return None

    
    def deleteChapter(self,roleId: int):
        try:
            # Build the delete statement
            stmt = delete(Chapters).where(Chapters.discord_role_id == roleId)
            result = self.session.execute(stmt)
            self.session.commit()
            return True if result.rowcount else False
        except Exception as e:
            print("Error deleting chapter:", e)
            return None
        
    def updateContributor(self, contributor: Member, table_class=None):
        try:
            if table_class == None:
                table_class = ContributorsDiscord
            chapters = lookForChapterRoles(contributor.roles)
            gender = lookForGenderRoles(contributor.roles)

            # Prepare the data to be upserted
            update_data = {
                "discord_id": contributor.id,
                "discord_username": contributor.name,
                "chapter": chapters[0] if chapters else None,
                "gender": gender,
                "joined_at": contributor.joined_at,
            }

            existing_record = self.session.query(table_class).filter_by(discord_id=contributor.id).first()

            if existing_record:
                stmt = (
                    update(table_class)
                    .where(table_class.discord_id == contributor.id)
                    .values(update_data)
                )
                self.session.execute(stmt)
            else:
                new_record = table_class(**update_data)
                self.session.add(new_record)

            # Commit the transaction
            self.session.commit()
            return True
        except Exception as e:
            print("Error updating contributor:", e)
            return False


    def updateContributors(self, contributors: [Member], table_class):
        try:
            for contributor in contributors:
                chapters = lookForChapterRoles(contributor.roles)
                gender = lookForGenderRoles(contributor.roles)
                update_data = {
                    "discord_id": contributor.id,
                    "discord_username": contributor.name,
                    "chapter": chapters[0] if chapters else None,
                    "gender": gender,
                    "joined_at": contributor.joined_at,
                }
                existing_record = self.session.query(table_class).filter_by(discord_id=contributor.id).first()

                if existing_record:
                    stmt = (
                        update(table_class)
                        .where(table_class.discord_id == contributor.id)
                        .values(update_data)
                    )
                    self.session.execute(stmt)
                else:
                    new_record = table_class(**update_data)
                    self.session.add(new_record)

            self.session.commit()
            return True
        except Exception as e:
            print("Error updating contributors:", e)
            return False

    
    def deleteContributorDiscord(self, contributorDiscordIds, table_class=None):
        try:
            if table_class == None:
                table_class = ContributorsDiscord
            stmt = delete(table_class).where(table_class.discord_id.in_(contributorDiscordIds))
            self.session.execute(stmt)
            self.session.commit()
            
            return True
        except Exception as e:
            print("Error deleting contributors:", e)
            self.session.rollback()
            return False
        
    

    def read_all_active(self, table):      
        if table == "contributors_discord":
            table = ContributorsDiscord 
        data = self.session.query(table).where(table.is_active == True).all()
        return self.convert_dict(data)
    
    def invalidateContributorDiscord(self, contributorDiscordIds):
        table = "contributors_discord"
        for id in contributorDiscordIds:
            self.client.table(table).update({'is_active': 'false'}).eq('discord_id', id).execute()
