import requests
import os, sys, dotenv
import json

dotenv.load_dotenv()


class GithubAPI:
    def __init__(self, repo):
        url_components = repo.split('/')
        self.owner = url_components[3]
        self.repo = url_components[4]
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {os.getenv("GithubPAT")}'
        }
    
    def get_repo_commits(self):
        url =  f'https://api.github.com/repos/{self.owner}/{self.repo}/commits'
        return requests.get(url, headers=self.headers).json()
    
    def get_commit_count(self):
        contributors = self.get_contributors()
        print(contributors, type(contributors))
        commit_count = 0
        for contributor in contributors:
            print("""THIS IS CONTRIBUTOR""", contributor)
            commit_count+=contributor['contributions']
        return commit_count
    
    def get_latest_repo_commit(self):
        return self.get_commits()[0]
    
    def get_json(self, dict):
        return json.dumps(dict)
    
    def get_issues(self, status, page):
        params={
            "state":status,
            "since":"2023-06-08T00:00:00Z",
            "per_page":100,
            "page":page
            }
        url = f'https://api.github.com/repos/{self.owner}/{self.repo}/issues'
        return requests.get(url, headers=self.headers, params=params).json()
    
    def get_issue_comments(self, issue_number):
        params={
            "since":"2023-05-01T00:00:00Z", #cutoff date for metrics
            }

        url=f"https://api.github.com/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
        
        return requests.get(url, headers=self.headers, params=params).json()

    
    def get_pull_requests(self, status, page):
        params = {
            "state":status,
            "per_page":100,
            "page":page
        }
        url = f'https://api.github.com/repos/{self.owner}/{self.repo}/pulls'
        return requests.get(url, headers=self.headers, params={"state":status}).json()
    
    def get_issue_count(self):
        open_count = len(self.get_issues('open'))
        closed_count = len(self.get_issues('closed'))

        return (open_count, closed_count)
    
    def get_pull_request_count(self):
        open_count = len(self.get_pull_requests('open'))
        closed_count = len(self.get_pull_requests('closed'))

        return (open_count, closed_count)


    def get_contributors(self):
        url = f'https://api.github.com/repos/{self.owner}/{self.repo}/contributors'
        return requests.get(url, headers=self.headers).json()



owner = 'ChakshuGautam'
repo = 'cQube-POCs'
url =  f'https://api.github.com/repos/{owner}/{repo}/commits'

# # r = requests.get(url, headers=headers)
# # # sys.stdout.write(r.text)
# # print(r.json()[0]["commit"]["author"]["date"], r.json()[-1]["commit"]["author"]["date"])
# tester = GithubAPI('https://github.com/ChakshuGautam/cQube-ingestion')
# print(tester.get_commit_count())
# print(tester.get_pull_requests('open'))
# print(tester.get_json(tester.get_contributors()))