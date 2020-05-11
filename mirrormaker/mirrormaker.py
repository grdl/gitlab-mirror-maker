import click
import requests
from . import __version__
from . import gitlab
from . import github


@click.command()
@click.version_option(version=__version__)
@click.option('--github-token', required=True, help='GitHub token')
@click.option('--gitlab-token', required=True, help='GitLab token')
@click.option('--github-user', help='GitHub username. If not provided your GitLab username will be used.')
@click.option('--dry-run', is_flag=True, help="If enabled, GitHub repositories and GitLab mirrors won't be created")
def mirrormaker(github_token, gitlab_token, github_user, dry_run):
    github.token = github_token
    gitlab.token = gitlab_token

    click.echo('Getting your public GitLab repositories')
    gitlab_repos = gitlab.get_repos()
    if not gitlab_repos:
        click.echo('There are no public repositories in your GitLab account. Exiting now.')
        return

    click.echo('Getting your public GitHub repositories')
    github_repos = github.get_repos()

    # actions specifies what needs to be performed on a GitLab repo to create a mirror
    # eg: {'gitlab_repo: '', 'create_github': True, 'create_mirror': True}
    actions = []

    with click.progressbar(gitlab_repos, label='Checking mirrors status', show_eta=False) as bar:
        for gitlab_repo in bar:
            action = check_mirror_status(gitlab_repo, github_repos)
            actions.append(action)

    # Print a summary of actions to perform
    click.echo('\nYour repositories mirrors status summary:')
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

    # Perform the actions
    with click.progressbar(actions, label='Creating mirrors', show_eta=False) as bar:
        for action in bar:
            if action["create_github"]:
                github.create_repo(action["gitlab_repo"])

            if action["create_mirror"]:
                gitlab.create_mirror(github_token, action["gitlab_repo"], github_user)

    click.echo('Done!')


def check_mirror_status(gitlab_repo, github_repos):
    action = {'gitlab_repo': gitlab_repo, 'create_github': True, 'create_mirror': True}

    mirrors = gitlab.get_mirrors(gitlab_repo)
    if gitlab.mirror_exists(github_repos, mirrors):
        action['create_github'] = False
        action['create_mirror'] = False
        return action

    if github.repo_exists(github_repos, gitlab_repo['path_with_namespace']):
        action['create_github'] = False

    return action


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter, unexpected-keyword-arg
    mirrormaker(auto_envvar_prefix='MIRRORMAKER')
