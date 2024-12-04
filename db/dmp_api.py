from models import *
from sqlalchemy import func
import os
from dotenv import load_dotenv


# load_dotenv()
    

class DmpAPIQueries:
    
    # def get_postgres_uri():
    #     DB_HOST = os.getenv('POSTGRES_DB_HOST')
    #     DB_NAME = os.getenv('POSTGRES_DB_NAME')
    #     DB_USER = os.getenv('POSTGRES_DB_USER')
    #     DB_PASS = os.getenv('POSTGRES_DB_PASS')
        
    #     return f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'

    def get_issue_query():
        results = (
            db.session.query(
                DmpOrg.id.label('org_id'),
                DmpOrg.name.label('org_name'),
                func.json_agg(
                    func.json_build_object(
                        'id', DmpIssue.id,
                        'name', DmpIssue.title
                    )
                ).label('issues')
            )
            .outerjoin(DmpIssue, DmpOrg.id == DmpIssue.org_id)
            .group_by(DmpOrg.id)
            .order_by(DmpOrg.id)
            .all()
        )
        
        return results
        
    def get_issue_owner(name):        
        response = DmpOrg.query.filter_by(name=name).all()
        return response
    
    def get_actual_owner_query(owner):
        results = DmpIssue.query.filter(DmpIssue.repo_owner.like(f'%{owner}%')).all()
        results = [val.to_dict() for val in results]
        return results
    
     
    def get_dmp_issues(issue_id):        
        results = DmpIssue.query.filter_by(id=issue_id).all()
        results = [val.to_dict() for val in results]
        return results
        
        
    def get_dmp_issue_updates(dmp_issue_id):        
        results = DmpIssueUpdate.query.filter_by(dmp_id=dmp_issue_id).all()
        results = [val.to_dict() for val in results]
        return results
        
    
    def get_pr_data(dmp_issue_id):       
        pr_updates = Prupdates.query.filter_by(dmp_id=dmp_issue_id).all()
        pr_updates_dict = [pr_update.to_dict() for pr_update in pr_updates]
        return pr_updates_dict
        
  