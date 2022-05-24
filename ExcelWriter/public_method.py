import os, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from datetime import date
import pandas as pd

load_dotenv(verbose=True)

SERVER_ID = os.environ.get('SERVER_ID')
SERVER_PW = os.environ.get('SERVER_PW')

BASE_URL = 'http://127.0.0.1:8000/api/repos'

headers = {
    'Content-Type' : 'application/json'
}
server_auth = HTTPBasicAuth(SERVER_ID, SERVER_PW)

def get_from_server(url: str) -> dict|list[dict]:
    res = requests.get(url=url, headers=headers, auth=server_auth)
    try: res.raise_for_status()
    except: print(url, headers, res.text)
    return res.json()

def get_branches(org: str, repo: str) -> list[str]:
    url = f'{BASE_URL}/{org}/{repo}'
    return get_from_server(url)['branches']

def get_commits(org: str, repo: str, branch: str, since: str, until: str) -> list[dict]:
    url = f'{BASE_URL}/{org}/{repo}/commits/{branch}?since={since}&&until={until}'
    return get_from_server(url)

def get_all_commits(org: str, repo: str, since: str, until: str) -> pd.DataFrame:
    commits = []
    for branch in get_branches(org, repo):
        _commits = get_commits(org, repo, branch, since, until)
        for commit in _commits:
            _date: str = commit['date'][:10]
            
            
            commits.append({
                'sha' : commit['sha'],
                'repo' : commit['repo'],
                'branch' : commit['branch'],
                'date' : commit['date'],
                'weeknum': date(*map(int, _date.split('-'))).isocalendar().week,
                'name' : commit['user']['name'],
                'email' : commit['user']['email'],
                'additions' : commit['stats']['additions'],
                'deletions' : commit['stats']['deletions'],
                'amount_of_changes' : commit['stats']['amount_of_changes'],
                'total_changes' : commit['stats']['total_changes'],
            })
    return pd.DataFrame.from_dict(data=commits)