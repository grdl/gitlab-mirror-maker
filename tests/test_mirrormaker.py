import responses
import mirrormaker
from mirrormaker import github
from mirrormaker import gitlab


@responses.activate
def test_filter_forked_repos():
    resp_json = [{'name': 'repo_1', 'fork': True},
                 {'name': 'repo_2', 'fork': False}]

    responses.add(responses.GET, 'https://api.github.com/user/repos?type=public',
                  json=resp_json, status=200)

    github_repos = github.get_repos()

    assert len(github_repos) == 1
    assert github_repos[0]['name'] == 'repo_2'


@responses.activate
def test_filter_no_repos():
    responses.add(responses.GET, 'https://api.github.com/user/repos?type=public',
                  json=[], status=200)

    github_repos = github.get_repos()

    assert len(github_repos) == 0


def test_mirror_exists():
    mirrors = [{'url': 'https://*****:*****@github.com/grdl/one.git'}]
    github_repos = [{'full_name': 'grdl/one'},
                    {'full_name': 'grdl/two'}]

    assert gitlab.mirror_target_exists(github_repos, mirrors) == True

    mirrors = []
    github_repos = [{'full_name': 'grdl/one'}]

    assert gitlab.mirror_target_exists(github_repos, mirrors) == False

    mirrors = [{'url': 'https://*****:*****@github.com/grdl/one.git'}]
    github_repos = [{'full_name': 'grdl/two'}]

    assert gitlab.mirror_target_exists(github_repos, mirrors) == False

    mirrors = []
    github_repos = []

    assert gitlab.mirror_target_exists(github_repos, mirrors) == False

    mirrors = [{'url': 'https://*****:*****@github.com/grdl/one.git'}]
    github_repos = []

    assert gitlab.mirror_target_exists(github_repos, mirrors) == False

    mirrors = [{'url': 'https://*****:*****@github.com/grdl/one.git'},
               {'url': 'https://*****:*****@github.com/grdl/two.git'}]
    github_repos = [{'full_name': 'grdl/two'},
                    {'full_name': 'grdl/three'}]

    assert gitlab.mirror_target_exists(github_repos, mirrors) == True


def test_github_repo_exists():
    github_repos = [{'full_name': 'grdl/one'},
                    {'full_name': 'grdl/two'}]

    slug = 'grdl/one'

    assert github.repo_exists(github_repos, slug) == True

    slug = 'grdl/three'

    assert github.repo_exists(github_repos, slug) == False

    assert github.repo_exists([], slug) == False
