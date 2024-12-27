import dotenv
import os
##
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, aliased      
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import DeclarativeMeta
from .models import Base, ContributorsRegistration,GithubClassroomData, IssueContributors
from sqlalchemy import delete, insert
from sqlalchemy import select, asc, desc,update, join
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import exists
from datetime import datetime
from sqlalchemy import cast, String ,and_
from sqlalchemy.dialects.postgresql import ARRAY
from .models import Issues, CommunityOrgs, PointSystem, PrHistory

# dotenv.load_dotenv(".env")


# def get_postgres_uri():
#     DB_HOST = os.getenv('POSTGRES_DB_HOST')
#     DB_NAME = os.getenv('POSTGRES_DB_NAME')
#     DB_USER = os.getenv('POSTGRES_DB_USER')
#     DB_PASS = os.getenv('POSTGRES_DB_PASS')

#     # DB_URL = os.getenv('DATABASE_URL')
#     # print('db')
#     return f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'

    
class ServerQueries:
    
    # def __init__(self):
    #     DATABASE_URL = get_postgres_uri()         
    #     # Initialize Async SQLAlchemy
    #     engine = create_async_engine(DATABASE_URL, echo=False,poolclass=NullPool)
    #     async_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    #     self.session = async_session
        
    # def get_instance():
    #     return PostgresORM()
            
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

    async def readAll(self,table_class):
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


    async def deleteComment(self,issue_id,table_name):
        try:
            table = self.get_class_by_tablename(table_name)
            async with self.session() as session:
                stmt = delete(table).where(table.issue_id == issue_id)
                await session.execute(stmt)
                await session.commit()
                
                return True
            
        except Exception as e:
            print(f"An error occurred - deleteComment: {e}")
            return False

    async def read(self, table, filters=None, select_columns=None, order=None, limit=None, offset=None):
        """
        Reads data from a table in the database using SQLAlchemy ORM.
        """
        try:
            table_class = self.get_class_by_tablename(table)
            
            # Select specific columns or all columns if None
            if select_columns:
                stmt = select([getattr(table_class, col) for col in select_columns])
            else:
                stmt = select(table_class)
            
            # Apply filters
            if filters:
                for column, condition in filters.items():
                    if isinstance(condition, tuple) and len(condition) == 2:
                        operation, value = condition
                        col_attr = getattr(table_class, column)
                        if operation == 'gt':
                            stmt = stmt.where(col_attr > value)
                        elif operation == 'lt':
                            stmt = stmt.where(col_attr < value)
                        elif operation == 'gte':
                            stmt = stmt.where(col_attr >= value)
                        elif operation == 'lte':
                            stmt = stmt.where(col_attr <= value)
                    else:
                        stmt = stmt.where(getattr(table_class, column) == condition)

            # Apply ordering
            if order:
                for column, direction in order.items():
                    if direction == 'asc':
                        stmt = stmt.order_by(asc(getattr(table_class, column)))
                    elif direction == 'desc':
                        stmt = stmt.order_by(desc(getattr(table_class, column)))

            # Apply limit
            if limit:
                stmt = stmt.limit(limit)
            
            # Apply offset
            if offset:
                stmt = stmt.offset(offset)

            async with self.session() as session:
                result = await session.execute(stmt)
                data = result.scalars().all()
            
            # Convert result to dictionary
            return [row.to_dict() for row in data]
        
        except Exception as e:
            print(f"An error occurred - read: {e}")
            return None
        
    
    async def add_discord_metrics(self, discord_metrics):
        try:
            async with self.session() as session:
                DiscordMetrics = self.get_class_by_tablename("discord_metrics")

                for metric in discord_metrics:
                    stmt = select(DiscordMetrics).where(DiscordMetrics.product_name == metric["product_name"])
                    result = await session.execute(stmt)
                    existing_record = result.scalars().first()

                    if existing_record:
                        update_stmt = (
                            update(DiscordMetrics)
                            .where(DiscordMetrics.product_name == metric["product_name"])
                            .values(
                                mentor_messages=metric["mentor_messages"],
                                contributor_messages=metric["contributor_messages"]
                            )
                            .returning(DiscordMetrics)
                        )
                        updated_data = await session.execute(update_stmt)
                        data = updated_data.scalars().first()
                    else:
                        new_record = DiscordMetrics(**metric)
                        session.add(new_record)
                        await session.commit()  
                        await session.refresh(new_record)
                        data = new_record

                await session.commit()
                return data

        except IntegrityError as e:
            print(f"An error occurred: {e}")
            await session.rollback()
            return None
        
    async def add_github_metrics(self, github_metrics):
        try:
            async with self.session() as session:
                for metric in github_metrics:
                    GithubMetrics = self.get_class_by_tablename("github_metrics")

                    # Check if the metric already exists in the database
                    stmt = select(GithubMetrics).where(GithubMetrics.product_name == metric["product_name"])
                    result = await session.execute(stmt)
                    existing_record = result.scalars().first()

                    if existing_record:
                        update_data = {key: value for key, value in metric.items() if key != "product_name"}
                        
                        update_stmt = (
                            update(GithubMetrics)
                            .where(GithubMetrics.product_name == metric["product_name"])
                            .values(update_data)
                            .returning(GithubMetrics)
                        )
                        updated_data = await session.execute(update_stmt)
                        data = updated_data.scalars().first()
                    else:
                        # Insert the new metric if it doesn't exist
                        new_record = GithubMetrics(**metric)
                        session.add(new_record)
                        await session.commit() 
                        await session.refresh(new_record)
                        data = new_record

                await session.commit()
                return data

        except IntegrityError as e:
            print(f"An error occurred: {e}")
            await session.rollback()
            return None
        
    async def check_exists(self,discord_id, assignment_id):
        try:
            # Construct the query for check exists
            async with self.session() as session:
                stmt = (
                    select(exists()
                        .where((GithubClassroomData.discord_id.is_(None)) | (GithubClassroomData.discord_id == discord_id))
                        .where(GithubClassroomData.assignment_id == assignment_id)
                    )
                )
                result = await session.execute(stmt)
                exists_result = result.scalar()

                return exists_result

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    async def save_classroom_records(self, data):
        try:
            async with self.session() as session:
                for record in data:
                    try:
                        new_record = GithubClassroomData(
                                    **record)
                        session.add(new_record)
                        
                        await session.commit()
                        print("Record inserting successfully!")
                    except Exception as e:
                        await session.rollback()
                        print("Error updating record:", e)
                
                return True
        except Exception as e:
            print(f"An error occurred  save_classroom_records: {e}")
            return False
        
    async def update_classroom_records(self, data):
        async with self.session() as session:
            for record in data:
                try:
                    stmt = (
                        update(GithubClassroomData).
                        where(
                            GithubClassroomData.assignment_id == record.get('assignment_id'),
                            GithubClassroomData.discord_id == cast(str(record.get('discord_id')),String)
                        ).
                        values(
                            assignment_name=record.get('assignment', {}).get('title'),
                            assignment_url=record.get('assignment', {}).get('classroom', {}).get('url'),
                            c4gt_points=record.get('c4gt_points'),
                            github_username=record.get('students', [{}])[0].get('login'),
                            points_available=record.get('points_available'),
                            points_awarded=record.get('points_awarded',0),
                            roster_identifier=record.get('roster_identifier',""),
                            starter_code_url=record.get('starter_code_url', record.get('repository', {}).get('html_url')),
                            student_repository_name=record.get('repository', {}).get('full_name'),
                            student_repository_url=record.get('repository', {}).get('html_url'),
                            submission_timestamp=record.get('submission_timestamsp', datetime.now()),
                            updated_at=record.get('updated_at')
                        )
                    )
                    result = await session.execute(stmt)
                    await session.commit()
                    print("Record updated successfully!")
                    return True
                except Exception as e:
                    await session.rollback()
                    print("Error updating record:", e)
                    return False
                        
    async def getdiscord_from_cr(self,github_url):
        try:
            Table = self.get_class_by_tablename("contributors_registration")
            async with self.session() as session:
                stmt = (select(Table.discord_id).where(Table.github_url == github_url))
                result = await session.execute(stmt)
                exists_result = result.scalar()

                return exists_result
        except Exception as e:
            print("Error - getdiscord_from_cr:", e)
            return None
                
    
    async def add_data(self, data: dict, table_name: str):
        try:
            table_class = self.get_class_by_tablename(table_name)            
            if not table_class:
                raise ValueError(f"Table class for {table_name} not found")
                    
            async with self.session() as session:
                new_record = table_class(**data)
                session.add(new_record)
                await session.commit()                
                await session.refresh(new_record)
                
                return new_record
        except Exception as e:
            print("Error - add_data:", e)
            return None
        
    async def insert_org(self, name):
        try:
            async with self.session() as session:
                table = self.get_class_by_tablename("community_orgs")
                if not table:
                    raise ValueError(f"No ORM class found for table community_orgs")
                
                stmt = insert(table).values(
                        name=name
                    ).returning(table)

                result = await session.execute(stmt)
            
                await session.commit()    
                inserted_record = result.fetchone() 
                print("inserted_record ", {"id": inserted_record[0], "name": inserted_record[1]})
                return {"id": inserted_record[0], "name": inserted_record[1]}
                    
        except Exception as e:
            print(f"Error in record_created_ticket method: {e}")
            return None
            

            
    async def check_record_exists(self, table_name, filter_column, filter_value):
        try:
            table_class = self.get_class_by_tablename(table_name)
            if not table_class:
                raise ValueError(f"No ORM class found for table '{table_name}'")

            async with self.session() as session:
                stmt = (
                    select(table_class)
                    .where(getattr(table_class, filter_column) == filter_value)
                )
                result = await session.execute(stmt)
                exists = result.scalars().first() is not None
                return True if exists else False
        except Exception as e:
            print(f"An error occurred - check_record_exists: {e}")
            return False
        
        
    async def delete(self,table_name, filter_column, filter_value):
        try:
            table = self.get_class_by_tablename(table_name)
            async with self.session() as session:
                stmt = delete(table).where(getattr(table, filter_column) == filter_value)
                await session.execute(stmt)
                await session.commit()                
                return True
            
        except Exception as e:
            print(f"An error occurred - delete: {e}")
            return False
    
        
    async def get_data(self,col_name,table_name,value,condition=None):
        try:
            Table = self.get_class_by_tablename(table_name)
            async with self.session() as session:
                stmt = (select(Table).where(getattr(Table, col_name) == value))
                # Execute the query
                result = await session.execute(stmt)
                exists_result = result.scalar()
                if exists_result:
                    return self.convert_dict(exists_result)
                else:
                    return None
            
        except Exception as e:
            print(f"An error occurred - get_data: {e}")
            return None
        
    async def checkIsTicket(self, issue_id):
        try:
            tables_to_check = ['issues']  

            async with self.session() as session:
                data = []
                for table_name in tables_to_check:
                    table_class = self.get_class_by_tablename(table_name)
                    if not table_class:
                        continue 
                    stmt = select(table_class).where(getattr(table_class, 'issue_id') == issue_id)
                    result = await session.execute(stmt)
                    records = result.scalars().all()
                    
                    if records:
                        data.extend(records)
                # Check if data was found in any of the tables
                if len(data) > 0:
                    return True
                else:
                    return False
        except Exception as e:
            print(f"An error occurred - check_is_ticket: {e}")
            return False
    
        
    async def record_created_ticket(self, data,table_name):
        try:
            async with self.session() as session:
                # Dynamically get the ORM class for the table
                table = self.get_class_by_tablename(table_name)
                
                # Build and execute the query to check if the issue_id already exists
                # stmt = select(table).where(table.issue_id == data['issue_id'])

                stmt = insert(table).values(
                    link=data['link'],
                    labels=cast(data['labels'], ARRAY(String)),  # Cast to ARRAY type
                    complexity=data['complexity'],
                    technology=data['technology'],
                    status=data['status'],
                    created_at=data['created_at'],
                    updated_at=data['updated_at'],
                    title=data['title'],
                    domain=data['domain'],
                    description=f"{data['description']}",
                    org_id=data['org_id'],
                    issue_id=data['issue_id'],
                    project_type=data['project_type']
                ).returning(table)

                result = await session.execute(stmt)
            
                await session.commit()
                    
                # inserted_record = await result.fetchone() 
                # print("inserted result ", inserted_record)
                return result
                    
        except Exception as e:
            print(f"Error in record_created_ticket method: {e}")
            return None


    async def record_updated_ticket(self, data, table_name):
        try:
            async with self.session() as session:
                # Dynamically get the ORM class for the table
                table = self.get_class_by_tablename(table_name)

                # Build the update query
                stmt = (
                    update(table)
                    .where(table.issue_id == data['issue_id'])  # Match the existing issue by issue_id
                    .values(
                        link=data['link'],
                        labels=cast(data['labels'], ARRAY(String)),  # Cast to ARRAY type
                        complexity=data['complexity'],
                        technology=data['technology'],
                        status=data['status'],
                        created_at=data['created_at'],
                        updated_at=data['updated_at'],
                        title=data['title'],
                        description=f"{data['description']}",
                        org_id=data['org_id']
                    )
                    .returning(table)  # Return the updated row(s)
                )

                # Execute the update statement
                result = await session.execute(stmt)

                # Commit the transaction
                await session.commit()
 
                return result
        except Exception as e:
            print(f"Error in record_updated_ticket method: {e}")
            return None


    async def update_data(self, data, col_name, table_name):
        try:
            table_class = self.get_class_by_tablename(table_name)
            
            async with self.session() as session:
                stmt = (
                    update(table_class)
                    .where(getattr(table_class, col_name) == data[col_name])
                    .values(**data)
                    .returning(table_class) 
                )
                
                result = await session.execute(stmt)
                await session.commit()

                updated_record = result.scalars().first()
                # Convert the updated record to a dictionary before returning
                return self.convert_dict(updated_record) if updated_record else None
                    
        except Exception as e:
            print(f"Error in update_data: {e}")
            return None


    async def update_pr_data(self, data, table_name):
        try:
            table_class = self.get_class_by_tablename(table_name)
            
            async with self.session() as session:
                new_pr_history = PrHistory(
                    created_at= data['created_at'],
                        api_url=data['api_url'],
                        html_url= data['html_url'],
                        raised_by= data['raised_by'],
                        raised_at=  data['raised_at'],
                        raised_by_username= data['raised_by_username'],
                        status= data['status'],
                        is_merged= data['is_merged'],
                        merged_by= data['merged_by'],
                        merged_at= data['merged_at'],
                        merged_by_username=  data['merged_by_username'],
                        pr_id= data['pr_id']
                )
                stmt = (
                    update(table_class)
                    .where(table_class.pr_id == data['pr_id'])  # Match the existing issue by issue_id
                    .values(
                        
                    )
                    .returning(table_class)  # Return the updated row(s)
                )

                # Execute the update statement
                result = await session.execute(stmt)

                # Commit the transaction
                await session.commit()

                # Optionally fetch the updated record(s)
                updated_record = result.fetchone()
                
                return updated_record if updated_record else None
                    
        except Exception as e:
            print(f"Error in update_data: {e}")
            return None


    async def update_pr_history(self, pr_id, data):
        try:
            async with self.session() as session:
                # Query for the existing record based on pr_id (or some unique identifier)
                stmt = select(PrHistory).where(PrHistory.pr_id == pr_id)
                result = await session.execute(stmt)
                pr_history_record = result.scalars().first()

                if pr_history_record:
                    # Update the fields with new values from data
                    pr_history_record.created_at = data['created_at']
                    pr_history_record.api_url = data['api_url']
                    pr_history_record.html_url = data['html_url']
                    pr_history_record.raised_by = data['raised_by']
                    pr_history_record.raised_at = data['raised_at']
                    pr_history_record.raised_by_username = data['raised_by_username']
                    pr_history_record.status = data['status']
                    pr_history_record.is_merged = data['is_merged']
                    pr_history_record.merged_by = data['merged_by']
                    pr_history_record.merged_at = None if data['merged_at'] is None else data['merged_at']
                    pr_history_record.merged_by_username = data['merged_by_username']
                    pr_history_record.ticket_url = data['ticket_url']
                    pr_history_record.ticket_complexity = data['ticket_complexity']

                    # Commit the changes to the database
                    await session.commit()

                    # Optionally refresh the object
                    await session.refresh(pr_history_record)

                    return pr_history_record
                else:
                    print(f"Record with pr_id {pr_id} not found")
                    return None

        except Exception as e:
            print(f"Error in update_pr_history: {e}")
            return None


    async def addPr(self, prData, issue_id):
        try:
            if issue_id:
                ticket = await self.get_data("issue_id","issues",issue_id,None)
                if len(ticket) ==0:
                    ticket = await self.get_data("issue_id","dmp_tickets",issue_id,None)

            for pr in prData:
                data = {
                    # "api_url":data["url"],
                    "html_url":pr["html_url"],
                    "pr_id":pr["pr_id"],
                    "raised_by":pr["raised_by"],
                    "raised_at":pr["raised_at"],
                    "raised_by_username":pr["raised_by_username"],
                    "status":pr["status"],
                    "is_merged":pr["is_merged"] if pr.get("is_merged") else None,
                    "merged_by":pr["merged_by"] if pr["merged_by"] else None,
                    "merged_by_username":pr["merged_by_username"] if pr.get("merged_by_username") else None,
                    "merged_at":pr["merged_at"] if pr.get("merged_at") else None,
                    "points": ticket[0]["ticket_points"] if issue_id else 0,
                    "ticket_url":ticket[0]["api_endpoint_url"] if issue_id else 0
                }
                resp = await self.add_data(data,"connected_prs")
                
            return True
        except Exception as e:
            print(f"Error in addPr: {e}")
            return None
        
        
    async def get_issue_from_issue_id(self,issue_id):
        try:
            async with self.session() as session:
                # Dynamically get the ORM class for the table
                table = self.get_class_by_tablename("issues")
               
                # Build and execute the query to check if the issue_id already exists
                stmt = select(table).where(table.issue_id == issue_id)
                result = await session.execute(stmt)
                issues = result.scalars().first()
                
                if issues:
                    return self.convert_dict(issues)
                return None
                                    
        except Exception as e:
            print(f"Error in get_issue_from_issue_id method: {e}")
            return None
        
    async def get_contributors_from_issue_id(self,issue_id):
        try:
            async with self.session() as session:
                # Dynamically get the ORM class for the table
                table = self.get_class_by_tablename("issue_contributors")
                
                # Build and execute the query to check if the issue_id already exists
                stmt = select(table).where(table.issue_id == issue_id)
                result = await session.execute(stmt)
                issues = result.scalars().all()
                
                if issues:
                    return self.convert_dict(issues)
                return None
                                    
        except Exception as e:
            print(f"Error in get_contributors_from_issue_id method: {e}")
            return None
        
    async def get_pointsby_complexity(self, complexity_type,type="Contributor"):
        try:
            async with self.session() as session:
                # Dynamically get the ORM class for the table
                table = self.get_class_by_tablename("points_mapping")
                
                # Build and execute the query with multiple conditions
                stmt = select(table).where(
                    and_(
                        table.complexity == complexity_type,
                        table.role == type
                    )
                )
                result = await session.execute(stmt)
                points = result.scalars().all()
                return points[0].points if points else 0

        except Exception as e:
            print(f"Error in get_pointsby_complexity method: {e}")
            return None
        
    async def upsert_point_transaction(self, issue_id, user_id, points,user_type="Contributor"):
        try:
            async with self.session() as session:
                table = self.get_class_by_tablename("point_transactions")
                column_map = {
                "Contributor": table.user_id,
                "Mentor": table.mentor_id, 
                }
                chosen_column = column_map.get(user_type)
                stmt = select(table).where(
                    and_(
                        table.issue_id == issue_id,
                        chosen_column == user_id
                    )
                )
                
                result = await session.execute(stmt)
                transaction = result.scalars().one_or_none()

                if transaction:
                    # Record exists, so update the points column
                    update_stmt = (
                        update(table)
                        .where(and_(table.issue_id == issue_id, table.user_id == user_id))
                        .values(point=points)
                    )
                    await session.execute(update_stmt)
                    await session.commit()
                    return True

                else:
                    # Record does not exist, so create a new one
                    new_transaction = table(issue_id=issue_id,point=points)
                    setattr(new_transaction, chosen_column.key, user_id)
                    session.add(new_transaction)
                    await session.commit()
                    return True

        except Exception as e:
            print(f"Error in upsert_point_transaction method: {e}")
            return None
        
    async def save_user_points(self, user_id, points,user_type="Contributor"):
        try:
            async with self.session() as session:
                table = self.get_class_by_tablename("user_points_mapping")
                column_map = {
                "Contributor": table.contributor,
                "Mentor": table.mentor_id, 
                }
                chosen_column = column_map.get(user_type)
                stmt = select(table).where(chosen_column == user_id)
                
                result = await session.execute(stmt)
                transaction = result.scalars().one_or_none()


                if transaction:
                    addon_points = points + transaction.points
                    update_stmt = (
                        update(table)
                        .where(chosen_column == user_id)
                        .values(points=addon_points)
                    )
                    await session.execute(update_stmt)
                    await session.commit()
                    return True

                else:
                    # Record does not exist, so create a new one
                    new_transaction = table(points=points)
                    setattr(new_transaction, chosen_column.key, user_id)
                    session.add(new_transaction)
                    await session.commit()
                    return True

        except Exception as e:
            print(f"Error in save_user_points method: {e}")
            return None
        

    async def deleteIssueComment(self, commentId):
        try:
            async with self.session() as session:
                # Dynamically get the ORM class for the table
                table = self.get_class_by_tablename("ticket_comments")
                
                # Build and execute the query with multiple conditions
                stmt = delete(table).where(
                   getattr(table, "id") == commentId
                )
                result = await session.execute(stmt)
                is_deleted = result.scalars().all()
                return is_deleted
        except Exception as e:
            print(f"Error in deleting issue comments: {e}")
            return None
        

    async def getUserLeaderBoardData(self):
        try:
            async with  self.session() as session:
                orgs_alias = aliased(CommunityOrgs)
                points_alias = aliased(PointSystem)
                
                # Join the Issues table with the CommunityOrgs and PointSystem
                stmt = (
                    select(Issues, orgs_alias, points_alias)
                    .join(orgs_alias, Issues.org_id == orgs_alias.id, isouter=True)  # Left join with CommunityOrgs
                    .join(points_alias, Issues.complexity == points_alias.complexity, isouter=True)  # Left join with PointSystem
                )
                
                # Execute the statement
                result = await session.execute(stmt)

                # Fetch all the results
                records = result.all()

                # Convert to dictionary format for readability (if needed)
                return [
                    {
                        'issue': issue.to_dict(),
                        'community_org': org.to_dict() if org else None,
                        'point_system': points.to_dict() if points else None
                    }
                    for issue, org, points in records
                ]
        except Exception as e:
            print('Exception occured while getting users leaderboard data ', e)
            return None


    async def get_joined_data_with_filters(self, filters=None):
        async with self.session() as session:
            # Aliases for the tables
            issues = aliased(Issues)
            orgs = aliased(CommunityOrgs)
            points = aliased(PointSystem)

            # Base query with the join
            query = select(
                issues,
                orgs,
                points
            ).join(
                orgs, issues.org_id == orgs.id
            ).join(
                points, points.complexity == issues.complexity
            )

            # If dynamic filters are provided, apply them
            if filters:
                filter_conditions = []
                for field, value in filters.items():
                    filter_conditions.append(getattr(issues, field) == value)

                query = query.where(and_(*filter_conditions))

            # Execute the query and return the results
            result = await session.execute(query)
            records = result.all()

            # Convert results to dictionaries if necessary
            return [dict(issue=record[0].to_dict(), org=record[1].to_dict(), points=record[2].to_dict()) for record in records]

    async def fetch_filtered_issues(self, filters):
        try:
            async with self.session() as session:
                # Start building the query by joining tables
                query = (
                        select(Issues, CommunityOrgs, PointSystem, IssueContributors, ContributorsRegistration)
                        .join(CommunityOrgs, Issues.org_id == CommunityOrgs.id)
                        .join(PointSystem, Issues.complexity == PointSystem.complexity)
                        .outerjoin(IssueContributors, Issues.id == IssueContributors.issue_id)
                        .outerjoin(ContributorsRegistration, IssueContributors.contributor_id == ContributorsRegistration.id) 
                        .where(Issues.complexity != 'Beginner')
                        .order_by(desc(Issues.id))
                    )
                
                # Prepare dynamic filter conditions
                conditions = []
                
                # Check if there are filters for Issues table
                if 'issues' in filters:
                    for field, value in filters['issues'].items():
                        conditions.append(getattr(Issues, field) == value)
                
                # Check if there are filters for CommunityOrgs table
                if 'org' in filters:
                    for field, value in filters['org'].items():
                        conditions.append(getattr(CommunityOrgs, field) == value)
                        
                # Check if there are filters for PointSystem table
                if 'points' in filters:
                    for field, value in filters['points'].items():
                        conditions.append(getattr(PointSystem, field) == value)
                
                # Apply filters (if any) to the query
                if conditions:
                    query = query.where(and_(*conditions))

                # Execute the query and fetch results
                result = await session.execute(query)
                rows = result.fetchall()

                # Process the result into a dictionary or a preferred format
                data = []
                for row in rows:
                    issue = row.Issues.to_dict()
                    org = row.CommunityOrgs.to_dict() if row.CommunityOrgs else None
                    point_system = row.PointSystem.to_dict()
                    contributors_registration = row.ContributorsRegistration.to_dict() if row.ContributorsRegistration else None
                    data.append({
                        'issue': issue,
                        'org': org,
                        'points': point_system,
                        'contributors_registration': contributors_registration
                    })

                return data

        except Exception as e:
            print(f"Error in fetch_filtered_issues: {e}")
            return None
            

    def add_github_user(self, user):
        data = self.client.table("contributors_registration").upsert(user, on_conflict=["github_id", "discord_id"]).execute()
        return data.data
                    
