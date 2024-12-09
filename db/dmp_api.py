from models import *
from sqlalchemy import func
import os
from dotenv import load_dotenv
# from flask_sqlalchemy import SQLAlchemy
import sqlalchemy


# load_dotenv()
db = sqlalchemy()

class DmpAPIQueries:

    def get_issue_query():
        results = (
            db.session.query(
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
            .all()
        )
        
        return results
        
    def get_issue_owner(name):        
        response = DmpOrgs.query.filter_by(name=name).all()
        return response
    
    def get_actual_owner_query(owner):
        results = DmpIssues.query.filter(DmpIssues.repo_owner.like(f'%{owner}%')).all()
        results = [val.to_dict() for val in results]
        return results
    
     
    def get_dmp_issues(issue_id):        
        results = DmpIssues.query.filter_by(id=issue_id).all()
        results = [val.to_dict() for val in results]
        return results
        
        
    def get_dmp_issue_updates(dmp_issue_id):        
        results = DmpIssueUpdates.query.filter_by(dmp_id=dmp_issue_id).all()
        results = [val.to_dict() for val in results]
        return results
        
    
    def get_pr_data(dmp_issue_id):       
        pr_updates = DmpPrUpdates.query.filter_by(dmp_id=dmp_issue_id).all()
        pr_updates_dict = [pr_update.to_dict() for pr_update in pr_updates]
        return pr_updates_dict
        
  