import click
import requests
from pprint import pprint


@click.command()
@click.option('--github-token', required=True, help='GitHub token')
@click.option('--gitlab-token', required=True, help='GitLab token')
@click.option('--github-user', help='GitHub username. If not provided your GitLab username will be used.')
@click.option('--dry-run', is_flag=True, help="If enabled, GitHub repositories and GitLab mirrors won't be created")
def mirrormaker(github_token, gitlab_token, github_user, dry_run):
    click.echo('Getting your public GitLab repositories')
    gitlab_repos = get_gitlab_repos(gitlab_token)

    if not gitlab_repos:
        click.echo('There are no public repositories in your GitLab account. Exiting now.')
        return

    click.echo('Getting your public GitHub repositories')
    github_repos = get_github_repos(github_token)

    # actions is a list of gitlab repos and actions to perform
    # eg: {'gitlab_repo: '', 'create_github': True, 'create_mirror': True}
    actions = []

    with click.progressbar(gitlab_repos, label='Checking if mirrors already exist', show_eta=False) as bar:
        for gitlab_repo in bar:
            action = process_gitlab_repo(gitlab_token, gitlab_repo, github_repos)
            actions.append(action)

    # Print summary of action to perform
    for action in actions:
        if action["create_github"] and action["create_mirror"]:
            message = 'will create GitHub repository and mirror'
        elif not action["create_github"] and action["create_mirror"]:
            message = 'will create only mirror (GitHub repository already created)'
        elif action["create_github"] and not action["create_mirror"]:
            message = 'will create only GitHub repo (mirror already configured)'
        else:
            message = 'already mirrored'

        click.echo(f'{action["gitlab_repo"]["path_with_namespace"]:40} {message}')

    if dry_run:
        click.echo('Run without the --dry-run flag to actually create repositories and mirrors. Exiting now.')
        return

    # Performing the actions
    for action in actions:
        if action["create_github"]:
            click.echo(f'Creating GitHub repository: {action["gitlab_repo"]["name"]}')
            create_github_repo(github_token, action["gitlab_repo"])

        if action["create_mirror"]:
            click.echo(f'Creating mirror: {action["gitlab_repo"]["name"]}')
            create_mirror(gitlab_token, github_token, action["gitlab_repo"], github_user)


def process_gitlab_repo(gitlab_token, gitlab_repo, github_repos):
    action = {'gitlab_repo': gitlab_repo, 'create_github': True, 'create_mirror': True}

    mirrors = get_mirrors(gitlab_token, gitlab_repo)
    if mirror_exist(github_repos, mirrors):
        action['create_github'] = False
        action['create_mirror'] = False
        return action

    if github_repo_exists(github_repos, gitlab_repo['path_with_namespace']):
        action['create_github'] = False

    return action


def get_gitlab_repos(gitlab_token):
    url = f'https://gitlab.com/api/v4/projects?visibility=public&owned=true&archived=false'
    headers = {'Authorization': f'Bearer {gitlab_token}'}

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    return r.json()


def get_github_repos(github_token):
    url = 'https://api.github.com/user/repos?type=public'
    headers = {'Authorization': f'Bearer {github_token}'}

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    # Return only non forked repositories
    return [x for x in r.json() if not x['fork']]


def get_mirrors(gitlab_token, gitlab_repo):
    url = f'https://gitlab.com/api/v4/projects/{gitlab_repo["id"]}/remote_mirrors'
    headers = {'Authorization': f'Bearer {gitlab_token}'}

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    return r.json()


def mirror_exist(github_repos, mirrors):
    # Check if any of the mirrors points to any of public github repos
    for mirror in mirrors:
        if any(mirror['url'] and mirror['url'].endswith(f'{repo["full_name"]}.git') for repo in github_repos):
            return True

    return False


def github_repo_exists(github_repos, repo_slug):
    return any(repo['full_name'] == repo_slug for repo in github_repos)


def create_github_repo(github_token, gitlab_repo):
    url = 'https://api.github.com/user/repos'
    headers = {'Authorization': f'Bearer {github_token}'}

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


def create_mirror(gitlab_token, github_token, gitlab_repo, github_user):
    url = f'https://gitlab.com/api/v4/projects/{gitlab_repo["id"]}/remote_mirrors'
    headers = {'Authorization': f'Bearer {gitlab_token}'}

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


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter, unexpected-keyword-arg
    mirrormaker(auto_envvar_prefix='MIRRORMAKER')
