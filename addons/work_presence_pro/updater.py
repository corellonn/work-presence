import git
import os

REPO="/app"

def check_updates():

    repo=git.Repo(REPO)

    origin=repo.remotes.origin

    origin.fetch()

    if repo.head.commit != origin.refs.main.commit:

        repo.git.pull()
