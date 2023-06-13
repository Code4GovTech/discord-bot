import sys, os

from utils.db import SupabaseInterface

class Project:
    def __init__(self, data=None, name=None) -> None:
        if name is not None:
            data = SupabaseInterface(table="projects").read(query_key="name",query_value=name)[0]
        self.name = data["name"]
        self.desc = data["description"]
        self.repository = data['repository']
        self.contributor = data['contributor']
        self.mentor = data['mentor']
        self.product = data['product']
        self.issue_page_url = data['issue_page_url']
    
    @classmethod
    def is_project(project_name):
        db_client = SupabaseInterface(table="projects")
        data = db_client.read(query_key="name", query_value=project_name)
        if len(data)==1:
            return True
        if len(data)>1:
            raise Exception("Project name should be unique but recieved multiple items for this name.")
        return False
    
    @classmethod
    def get_all_projects(cls):
        db_client = SupabaseInterface(table="projects")
        data = db_client.read_all()
        return data
    

        


# test = Project(name='test')