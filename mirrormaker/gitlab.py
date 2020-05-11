import requests

token = ''


def get_repos():
    url = f'https://gitlab.com/api/v4/projects?visibility=public&owned=true&archived=false'
    headers = {'Authorization': f'Bearer {token}'}

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    return r.json()


def get_mirrors(gitlab_repo):
    url = f'https://gitlab.com/api/v4/projects/{gitlab_repo["id"]}/remote_mirrors'
    headers = {'Authorization': f'Bearer {token}'}

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    return r.json()


def mirror_exists(github_repos, mirrors):
    # Check if any of the mirrors points to any of public github repos
    for mirror in mirrors:
        if any(mirror['url'] and mirror['url'].endswith(f'{repo["full_name"]}.git') for repo in github_repos):
            return True

    return False


def create_mirror(github_token, gitlab_repo, github_user):
    url = f'https://gitlab.com/api/v4/projects/{gitlab_repo["id"]}/remote_mirrors'
    headers = {'Authorization': f'Bearer {token}'}

    # If github-user is not provided use the gitlab username
    if not github_user:
        github_user = gitlab_repo['owner']['username']

    data = {
        'url': f'https://{github_user}:{github_token}@github.com/{github_user}/{gitlab_repo["path"]}.git',
        'enabled': True
    }

    try:
        r = requests.post(url, json=data, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    return r.json()
