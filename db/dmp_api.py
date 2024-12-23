from models import *
from sqlalchemy import func
import os
from dotenv import load_dotenv
# from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.future import select


class DmpAPIQueries:

    async def get_issue_query(async_session):
        try:
            async with async_session() as session:
                results = await session.execute(
                    select(
                        DmpOrgs.id.label('org_id'),
                        DmpOrgs.name.label('org_name'),
                        func.json_agg(
                            func.json_build_object(
                                'id', DmpIssues.id,
                                'name', DmpIssues.title
                            )
                        ).label('issues')
                    )
                    .outerjoin(DmpIssues, DmpOrgs.id == DmpIssues.org_id)
                    .group_by(DmpOrgs.id)
                    .order_by(DmpOrgs.id)
                )

                # Extract results as a list of dictionaries if needed
                data = results.all()
            
            return data
        except Exception as e:
            print(f"An error occurred: get_column_value {e}")
            return None
        
        
    async def get_issue_owner(async_session, name): 
        try:       
            async with async_session() as session:
                response = await session.execute(
                    select(DmpOrgs).filter_by(name=name)
                )
            results = response.scalars().all()
            return results
        except Exception as e:
            print(f"An error occurred: get_column_value {e}")
            return None
    
    async def get_actual_owner_query(async_session, owner):
        try:
            async with async_session() as session:
                response = await session.execute(
                    select(DmpIssues).filter(DmpIssues.repo_owner.like(f'%{owner}%'))
                )
            results = response.scalars().all()  # Fetch all matching rows as objects
            results = [val.to_dict() for val in results]  # Convert objects to dicts
            return results
        except Exception as e:
                print(f"An error occurred: get_column_value {e}")
                return None
    
     
    async def get_dmp_issues(async_session, issue_id):
        try:           
            async with async_session() as session:
                response = await session.execute(
                    select(DmpIssues).filter_by(id=issue_id)
                )
            results = response.scalars().all()  # Fetch all matching rows as objects
            results = [val.to_dict() for val in results]  # Convert objects to dicts
            return results
        except Exception as e:
            print(f"An error occurred: get_column_value {e}")
            return None
        
        
    async def get_dmp_issue_updates(async_session, dmp_issue_id):
        try:
            async with async_session() as session:
                response = await session.execute(
                    select(DmpIssueUpdates).filter_by(dmp_id=dmp_issue_id)
            )
            results = response.scalars().all()  # Fetch all matching rows as objects
            results = [val.to_dict() for val in results]  # Convert objects to dicts
            return results
        except Exception as e:
            print(f"An error occurred: get_column_value {e}")
            return None
        
    
    async def get_pr_data(async_session, dmp_issue_id):
        try:       
            async with async_session() as session:
                response = await session.execute(
                    select(DmpPrUpdates).filter_by(dmp_id=dmp_issue_id)
                )
            pr_updates = response.scalars().all()  # Fetch all matching rows as objects
            pr_updates_dict = [pr_update.to_dict() for pr_update in pr_updates]  # Convert objects to dicts
            return pr_updates_dict
        except Exception as e:
            print(f"An error occurred: get_column_value {e}")
            return None
        
  