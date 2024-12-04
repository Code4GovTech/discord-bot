from sqlalchemy.future import select
from models import *
from sqlalchemy import update
# from app import async_session
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from sqlalchemy.orm import aliased
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound


class DmpCronQueries:
    
    # def get_postgres_uri():
    #     DB_HOST = os.getenv('POSTGRES_DB_HOST')
    #     DB_NAME = os.getenv('POSTGRES_DB_NAME')
    #     DB_USER = os.getenv('POSTGRES_DB_USER')
    #     DB_PASS = os.getenv('POSTGRES_DB_PASS')
        
    #     return f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
    
    async def get_timestamp(async_session, model, col_name: str, col: str, value):
        try:
            # Construct the ORM query
            query = select(getattr(model, col_name)).filter(getattr(model, col) == value)
            
            # Execute the query and fetch the result
            async with async_session() as session:
                result = await session.execute(query)
                return result.scalar()
            
        except NoResultFound:
            return None
        except Exception as e:
            print(f"An error occurred: get_column_value {e}")
            return None
                            
    async def get_all_dmp_issues(async_session):
        try:
            async with async_session() as session:
                # Alias for the DmpOrg table to use in the JSON_BUILD_OBJECT
                dmp_org_alias = aliased(DmpOrg)

                # Build the query
                query = (
                    select(
                        DmpIssue,
                        func.json_build_object(
                            'created_at', dmp_org_alias.created_at,
                            'description', dmp_org_alias.description,
                            'id', dmp_org_alias.id,
                            'link', dmp_org_alias.link,
                            'name', dmp_org_alias.name,
                            'repo_owner', dmp_org_alias.repo_owner
                        ).label('dmp_orgs')
                    )
                    .outerjoin(dmp_org_alias, DmpIssue.org_id == dmp_org_alias.id)
                    .filter(DmpIssue.org_id.isnot(None))
                    .order_by(DmpIssue.id)
                )
                
                # Execute the query and fetch results
                result = await session.execute(query)
                rows = result.fetchall()
                
                # Convert results to dictionaries
                data = []
                for row in rows:
                    issue_dict = row._asdict()  # Convert row to dict
                    dmp_orgs = issue_dict.pop('dmp_orgs')  # Extract JSON object from row
                    issue_dict['dmp_orgs'] = dmp_orgs
                    issue_dict.update(issue_dict['DmpIssue'].to_dict())
                    # Add JSON object back to dict
                    del issue_dict['DmpIssue']
                    data.append(issue_dict)
                    
            return data
            
        except Exception as e:
            print(e)
            raise Exception
        
    async def update_dmp_issue(async_session,issue_id: int, update_data: dict):
        try:
            async with async_session() as session:
                async with session.begin():
                    # Build the update query
                    query = (
                        update(DmpIssue)
                        .where(DmpIssue.id == issue_id)
                        .values(**update_data)
                    )
                    
                    # Execute the query
                    await session.execute(query)
                    await session.commit()
                return True
            
        except Exception as e:
            return False
            
    
    async def upsert_data_orm(async_session, update_data):        
        try:

            async with async_session() as session:
                async with session.begin():
                   
                    # Define the insert statement
                    stmt = insert(DmpIssueUpdate).values(**update_data)

                    # Define the update statement in case of conflict
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['comment_id'],
                        set_={
                            'body_text': stmt.excluded.body_text,
                            'comment_link': stmt.excluded.comment_link,
                            'comment_api': stmt.excluded.comment_api,
                            'comment_updated_at': stmt.excluded.comment_updated_at,
                            'dmp_id': stmt.excluded.dmp_id,
                            'created_by': stmt.excluded.created_by,
                            'created_at': stmt.excluded.created_at
                        }
                    )

                    # Execute the statement
                    await session.execute(stmt)
                    await session.commit()
                    
            return True
                    
        except Exception as e:            
            print(e)
            return False        
        

    
    async def upsert_pr_update(async_session, pr_update_data):
        try:
            async with async_session() as session:
                async with session.begin():
                    pr_update_data['pr_updated_at'] = datetime.fromisoformat(pr_update_data['pr_updated_at']).replace(tzinfo=None) if pr_update_data['pr_updated_at'] else None
                    pr_update_data['merged_at'] = datetime.fromisoformat(pr_update_data['merged_at']).replace(tzinfo=None) if pr_update_data['merged_at'] else None
                    pr_update_data['closed_at'] = datetime.fromisoformat(pr_update_data['closed_at']).replace(tzinfo=None) if pr_update_data['closed_at'] else None

                    # Prepare the insert statement
                    stmt = insert(Prupdates).values(**pr_update_data)

                    # Prepare the conflict resolution strategy
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['pr_id'],  # Assuming `pr_id` is the unique key
                        set_={
                            'status': stmt.excluded.status,
                            'merged_at': stmt.excluded.merged_at,
                            'closed_at': stmt.excluded.closed_at,
                            'pr_updated_at': stmt.excluded.pr_updated_at,
                            'dmp_id': stmt.excluded.dmp_id,
                            'created_at': stmt.excluded.created_at,
                            'title': stmt.excluded.title,
                            'link': stmt.excluded.link
                        }
                    )
                    # Execute and commit the transaction
                    await session.execute(stmt)
                    await session.commit()
                    
                return True
            
        except Exception as e:
            print(e)
            return False
        
        
    
    async def update_dmp_week_update(async_session, update_data):
        try:          
            async with async_session() as session:
                async with session.begin():
                    # Define the filter conditions
                    stmt = (
                        select(DmpWeekUpdate)
                        .where(
                            DmpWeekUpdate.week == update_data['week'],
                            DmpWeekUpdate.dmp_id == update_data['dmp_id']
                        )
                    )

                    # Fetch the row that needs to be updated
                    result = await session.execute(stmt)
                    dmp_week_update = result.scalars().first()

                    if dmp_week_update:
                        # Update the fields with the values from update_data
                        for key, value in update_data.items():
                            setattr(dmp_week_update, key, value)

                        # Commit the changes
                        await session.commit()
                return True
        except Exception as e:
            print(e)
            return False
        
    
    
    async def get_week_updates(async_session, dmp_id, week):
        try:
            async with async_session() as session:
                # Build the ORM query
                stmt = select(DmpWeekUpdate).where(
                    DmpWeekUpdate.dmp_id == dmp_id,
                    DmpWeekUpdate.week == week
                )
                # Execute the query
                result = await session.execute(stmt)
                
                # Fetch all matching rows
                week_updates = result.scalars().all()
                

            return True if len(week_updates)>0 else False
        
        except Exception as e:
            return False    
        
    
    
    async def insert_dmp_week_update(async_session, update_data):
        try:
            async with async_session() as session:
                async with session.begin():
                    # Define the insert statement
                    stmt = insert(DmpWeekUpdate).values(**update_data)

                    # Execute the statement
                    await session.execute(stmt)
                    await session.commit()

                return True

        except Exception as e:
            print(e)
            return False
        
    
