import requests

token = ''


def get_repos():
    url = 'https://api.github.com/user/repos?type=public'
    headers = {'Authorization': f'Bearer {token}'}

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    # Return only non forked repositories
    return [x for x in r.json() if not x['fork']]


def repo_exists(github_repos, repo_slug):
    return any(repo['full_name'] == repo_slug for repo in github_repos)


def create_repo(gitlab_repo):
    url = 'https://api.github.com/user/repos'
    headers = {'Authorization': f'Bearer {token}'}

    data = {
        'name': gitlab_repo['path'],
        'description': f'{gitlab_repo["description"]} [mirror]',
        'homepage': gitlab_repo['web_url'],
        'private': False,
        'has_wiki': False,
        'has_projects': False
    }

    try:
        r = requests.post(url, json=data, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    return r.json()
