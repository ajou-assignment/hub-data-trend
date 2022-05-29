import requests, os
from datetime import date
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from public_method import (
    post_org,
    post_repo,
    post_branch,
    post_commit
)


load_dotenv(verbose=True)

GH_TOKEN = os.environ.get('GH_TOKEN')
SERVER_ID = os.environ.get('SERVER_ID')
SERVER_PW = os.environ.get('SERVER_PW')
ORG = 'facebook'#'ajou-assignment'
REPO = 'react'#'seat-assignment'
BASE_URL = 'https://api.github.com'
BRANCH = 'main'
CREATE_AT = '2021-03-01'

server_headers = {
    'Content-Type' : 'application/json'
}
server_auth = HTTPBasicAuth(SERVER_ID, SERVER_PW)

gh_headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': f'token {GH_TOKEN}',
}
org_url = f'{BASE_URL}/repos'
commit_url = f'{BASE_URL}/repos/{ORG}/{REPO}/commits'

page = 1
commits:list[dict] = []
detail_commits: list[dict] = []
#_commits: list = requests.get(url=f'{commit_url}?sha={BRANCH}&&page={page}&&per_page=30', headers=gh_headers).json()
post_org(ORG)
post_repo(ORG, REPO)
post_branch(ORG, REPO, BRANCH, CREATE_AT)

while True:
    try: 
        _commits: list = requests.get(url=f'{commit_url}?sha={BRANCH}&&page={page}&&per_page=30', headers=gh_headers).json()
        commits.extend(_commits)
    except: pass
    finally:
        page += 1
        last_commit_date = _commits[-1]['commit']['author']['date'][0:10]
        
        if _commits.__len__() < 30: 
            break
        
        if date(*map(int, last_commit_date.split('-'))) < date(*map(int, CREATE_AT.split('-'))):
            break

for commit in commits:
    sha = commit['sha']
    _commit: dict = requests.get(url=f'{commit_url}/{sha}', headers=gh_headers).json()

    if _commit.get('sha', None): detail_commits.append(_commit)

for commit in detail_commits:
    try:
        print("진행중")
        post_commit(ORG, REPO, BRANCH,
            sha=commit['sha'],
            name=commit['commit']['author']['name'],
            email=commit['commit']['author']['email'],
            date=commit['commit']['author']['date'][0:16],
            additions=commit['stats']['additions'],
            deletions=commit['stats']['deletions'],
        )
    except: pass
    


