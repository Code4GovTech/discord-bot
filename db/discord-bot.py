import os

# from discord import Member
from dotenv import load_dotenv            
from sqlalchemy import create_engine,select,desc,update,delete
from sqlalchemy.orm import sessionmaker
from .models import *
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# load_dotenv()

class DiscordBotQueries:
    # def __init__(self):
    #     DB_HOST = os.getenv('POSTGRES_DB_HOST')
    #     DB_NAME = os.getenv('POSTGRES_DB_NAME')
    #     DB_USER = os.getenv('POSTGRES_DB_USER')
    #     DB_PASS = os.getenv('POSTGRES_DB_PASS')
        
    #     engine = create_async_engine(f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}')
    #     async_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    #     self.session = async_session
    
    # def get_instance():
    #     return PostgresClient()

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
        
    def get_class_by_tablename(self,tablename):
        try:
            for cls in Base.registry._class_registry.values():
                if isinstance(cls, DeclarativeMeta):
                    if hasattr(cls, '__tablename__') and cls.__tablename__ == tablename:
                        return cls
            return None
        except Exception as e:
            print(f"ERROR get_class_by_tablename - {e}")
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

    async def read_all(self,table_class):
        try:
            table = self.get_class_by_tablename(table_class)
            # Query all records from the specified table class            
            async with self.session() as session:
                stmt = select(table)
                result = await session.execute(stmt)                
                
                data = result.scalars().all()
                result = self.convert_dict(data)
            return result
        except Exception as e:
            print(f"An error occurred -read_all_from_table : {e}")
            return None

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
        
    async def updateContributor(self, contributor: Member, table_class=None):
        try:
            async with self.session() as session:
                if table_class == None:
                    table_class = ContributorsDiscord
                chapters = lookForRoles(contributor.roles)["chapter_roles"]
                gender = lookForRoles(contributor.roles)["gender"]

                # Prepare the data to be upserted
                update_data = {
                    "discord_id": contributor.id,
                    "discord_username": contributor.name,
                    "chapter": chapters[0] if chapters else None,
                    "gender": gender,
                    "joined_at": contributor.joined_at,
                }

                stmt = select(ContributorsDiscord).where(ContributorsDiscord.discord_id == contributor.id)
                result = await session.execute(stmt)
                existing_record = result.scalars().first()

                # existing_record = self.session.query(table_class).filter_by(discord_id=contributor.id).first()

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
                chapters = lookForRoles(contributor.roles)["chapter_roles"]
                gender = lookForRoles(contributor.roles)["gender"]
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
