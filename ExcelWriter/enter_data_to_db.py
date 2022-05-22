import json
import requests, os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv


load_dotenv(verbose=True)

GH_TOKEN = os.environ.get('GH_TOKEN')
SERVER_ID = os.environ.get('SERVER_ID')
SERVER_PW = os.environ.get('SERVER_PW')
ORG = 'ajou-assignment'
REPO = 'seat-assignment'
BASE_URL = 'https://api.github.com'
BRANCH = 'main'

server_headers = {
    'Content-Type' : 'application/json'
}
server_auth = HTTPBasicAuth(SERVER_ID, SERVER_PW)

gh_headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': f'token {GH_TOKEN}',
}

commit_url = f'{BASE_URL}/repos/{ORG}/{REPO}/commits'

page = 1
commits:list[dict] = []
detail_commits: list[dict] = []

while True:
    try: 
        _commits: list = requests.get(url=f'{commit_url}?sha={BRANCH}&&page={page}&&per_page=30', headers=gh_headers).json()
        commits.extend(_commits)
    except: pass
    finally:
        page += 1
        if _commits.__len__() < 30: break

for commit in commits:
    sha = commit['sha']
    _commit: dict = requests.get(url=f'{commit_url}/{sha}', headers=gh_headers).json()

    if _commit.get('sha', None): detail_commits.append(_commit)

for commit in detail_commits:
    payload = {
        "sha": commit['sha'],
        "name": commit['commit']['author']['name'],
        "email": commit['commit']['author']['email'],
        "date": commit['commit']['author']['date'][0:16],
        "additions": commit['stats']['additions'],
        "deletions": commit['stats']['deletions'],
    }
    try:
        res = requests.post(f'http://127.0.0.1:8000/api/repos/{ORG}/{REPO}/commits/{BRANCH}', headers=server_headers, auth=server_auth, json=payload)
    except: pass
    finally: res.json()
    


