# GitLab Mirror Maker

GitLab Mirror Maker is a small tool written in Python that automatically mirrors your public repositories from GitLab to GitHub.

![Example](./example.svg)


# Why?

- Maybe you like GitLab better but the current market favors developers with a strong GitHub presence?
- Maybe as a form of backup?
- Or maybe you have other reasons... :wink:


# Installation

Install with pip or pipx:
```
pip install gitlab-mirror-maker
```

There's also a Docker image available:
```
docker run registry.gitlab.com/grdl/gitlab-mirror-maker 
```


# Usage

Run: `gitlab-mirror-maker --github-token xxx --gitlab-token xxx`

See [Authentication](#authentication) below on how to get the authentication tokens.

### Environment variables

Instead of using cli flags you can provide configuration via environment variables with the `MIRRORMAKER_` prefix:
```
export MIRRORMAKER_GITHUB_TOKEN xxx
export MIRRORMAKER_GITLAB_TOKEN xxx

gitlab-mirror-maker
```

### Dry run

Run with `--dry-run` flag to only print the summary and don't make any changes.

### Full synopsis

```
Usage: gitlab-mirror-maker [OPTIONS] [REPO]

  Set up mirroring of repositories from GitLab to GitHub.

  By default, mirrors for all repositories owned by the user will be set up.

  If the REPO argument is given, a mirror will be set up for that repository
  only. REPO can be either a simple project name ("myproject"), in which
  case its namespace is assumed to be the current user, or the path of a
  project under a specific namespace ("mynamespace/myproject").

Options:
  --version                 Show the version and exit.
  --github-token TEXT       GitHub authentication token  [required]
  --gitlab-token TEXT       GitLab authentication token  [required]
  --github-user TEXT        GitHub username. If not provided, your GitLab
                            username will be used by default.

  --dry-run / --no-dry-run  If enabled, a summary will be printed and no
                            mirrors will be created.

  --help                    Show this message and exit.
```

# How it works?

GitLab Mirror Maker uses the [remote mirrors API](https://docs.gitlab.com/ee/api/remote_mirrors.html) to create [push mirrors](https://docs.gitlab.com/ee/user/project/repository/repository_mirroring.html#pushing-to-a-remote-repository-core) of your GitLab repositories.

For each public repository in your GitLab account a new GitHub repository is created using the same name and description. It also adds a `[mirror]` suffix at the end of the description and sets the website URL the original GitLab repo. See [the mirror of this repo](https://github.com/grdl/gitlab-mirror-maker) as an example.

Once the mirror is created it automatically updates the target GitHub repository every time changes are pushed to the original GitLab repo.

### What is mirrored?

Only public repositories are mirrored to avoid publishing something private.

Only the commits, branches and tags are mirrored. No other repository data such as issues, pull requests, comments, wikis etc. are mirrored.


# Authentication

GitLab Mirror Maker needs authentication tokens for both GitLab and GitHub to be able to create mirrors.

### How to get the GitLab token?

- Click on your GitLab user -> Settings -> Access Tokens
- Pick a name for your token and choose the `api` scope
- Click `Create personal access token` and save it somewhere secure
- Do not share it! It grants full access to your account!

Here's more information about [GitLab personal tokens](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).

### How to get the GitHub token?

- Click on your GitHub user -> Settings -> Developer settings -> Personal access tokens -> Generate new token
- Pick a name for your token and choose the `public_repo` scope
- Click `Generate token` and save it somewhere secure

Here's more information about [GitHub personal tokens](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).


# Automate with GitLab CI

Instead of running the tool manually you may want to schedule it to run periodically with GitLab CI to make sure that any new repositories are automatically mirrored.

Here's a `.gitlab-ci.yml` snippet you can use:
```yaml
job:
  image: python:3.8-alpine
  script:
    - pip install gitlab-mirror-maker
    - gitlab-mirror-maker
  only:
    - schedules

```

Here's more info about creating [scheduled pipelines with GitLab CI](https://docs.gitlab.com/ee/ci/pipelines/schedules.html).
