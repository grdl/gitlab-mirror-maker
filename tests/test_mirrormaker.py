import responses
import mirrormaker


@responses.activate
def test_filter_forked_repos():
    resp_json = [{'name': 'repo_1', 'fork': True},
                 {'name': 'repo_2', 'fork': False}]

    responses.add(responses.GET, 'https://api.github.com/user/repos?type=public',
                  json=resp_json, status=200)

    github_repos = mirrormaker.get_github_repos('')

    assert len(github_repos) == 1
    assert github_repos[0]['name'] == 'repo_2'


@responses.activate
def test_filter_no_repos():
    responses.add(responses.GET, 'https://api.github.com/user/repos?type=public',
                  json=[], status=200)

    github_repos = mirrormaker.get_github_repos('')

    assert len(github_repos) == 0


def test_mirror_exists():
    mirrors = [{'url': 'https://*****:*****@github.com/grdl/one.git'}]
    github_repos = [{'full_name': 'grdl/one'},
                    {'full_name': 'grdl/two'}]

    assert mirrormaker.mirror_exist(github_repos, mirrors) == True

    mirrors = []
    github_repos = [{'full_name': 'grdl/one'}]

    assert mirrormaker.mirror_exist(github_repos, mirrors) == False

    mirrors = [{'url': 'https://*****:*****@github.com/grdl/one.git'}]
    github_repos = [{'full_name': 'grdl/two'}]

    assert mirrormaker.mirror_exist(github_repos, mirrors) == False

    mirrors = []
    github_repos = []

    assert mirrormaker.mirror_exist(github_repos, mirrors) == False

    mirrors = [{'url': 'https://*****:*****@github.com/grdl/one.git'}]
    github_repos = []

    assert mirrormaker.mirror_exist(github_repos, mirrors) == False

    mirrors = [{'url': 'https://*****:*****@github.com/grdl/one.git'},
               {'url': 'https://*****:*****@github.com/grdl/two.git'}]
    github_repos = [{'full_name': 'grdl/two'},
                    {'full_name': 'grdl/three'}]

    assert mirrormaker.mirror_exist(github_repos, mirrors) == True


def test_github_repo_exists():
    github_repos = [{'full_name': 'grdl/one'},
                    {'full_name': 'grdl/two'}]

    slug = 'grdl/one'

    assert mirrormaker.github_repo_exists(github_repos, slug) == True

    slug = 'grdl/three'

    assert mirrormaker.github_repo_exists(github_repos, slug) == False

    assert mirrormaker.github_repo_exists([], slug) == False
