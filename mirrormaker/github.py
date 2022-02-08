import requests

# GitHub user authentication token
token = ''

# GitHub username (under this user namespace the mirrors will be created)
user = ''

target_forks = False


def get_repos():
    """Finds all public GitHub repositories (which are not forks) of authenticated user.

    Returns:
     - List of public GitHub repositories.
    """

    url = 'https://api.github.com/user/repos?type=public'
    headers = {'Authorization': f'Bearer {token}'}

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    # Return only non forked repositories unless target_forks is set
    return [x for x in r.json() if not x['fork'] or target_forks]


def repo_exists(github_repos, repo_slug):
    """Checks if a repository with a given slug exists among the public GitHub repositories.

    Args:
     - github_repos: List of GitHub repositories.
     - repo_slug: Repository slug (usually in a form of path with a namespace, eg: "username/reponame").

    Returns:
     - True if repository exists, False otherwise.
    """

    return any(repo['full_name'] == repo_slug for repo in github_repos)


def create_repo(gitlab_repo):
    """Creates GitHub repository based on a metadata from given GitLab repository.

    Args:
     - gitlab_repo: GitLab repository which metadata (ie. name, description etc.) is used to create the GitHub repo.

    Returns:
     - JSON representation of created GitHub repo.
    """

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
