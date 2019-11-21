"""
Author: Sverchkov Evgeniy
email: u02249@gmail.com
This script using App Center API which do
a.      Receive and build all app branches
b.      Print a report in the following format:
"""
import requests
import json
import click
from iso8601 import parse_date

# list of routes to api
paths = {
    "branches": "/v0.1/apps/{owner_name}/{app_name}/branches",
    "branch_log": "https://appcenter.ms/users/{owner_name}/apps/{app_name}/build/branches/{branch_name}/builds/{build_id}",
    "add_build_config": "/v0.1/apps/{owner_name}/{app_name}/branches/{branch}/config",
    "create_build": "/v0.1/apps/{owner_name}/{app_name}/branches/{branch}/builds"
}


def _url(path):
    """get full url"""
    return "https://api.appcenter.ms" + path


def get_build_config(config_file):
    """read json config file with build settings"""
    with open(config_file) as file:
        data = json.load(file)
        return data


def get_branches(app_name, owner_name, token, include_active=True):
    """get all branches of app"""
    headers = {
        "accept": "application/json",
        "X-API-Token": token
    }
    path = paths["branches"].format(owner_name=owner_name, app_name=app_name)
    params = {"includeInactive": "true" if include_active else "false"}
    response = requests.get(url=_url(path), params=params, headers=headers)
    return response.json()


def get_last_build_of_branches(app_name, owner_name, token, include_active=True):
    """get the list of branches which have had build"""
    res = get_branches(app_name=app_name, owner_name=owner_name, token=token, include_active=include_active)
    return [b["lastBuild"] for b in res if "lastBuild" in b]


def get_log_link(app_name, owner_name, branch_name="", build_id=1):
    """Get a link to the log file. user must be logged in to open this link"""
    log_link = paths["branch_log"].format(app_name=app_name,
                                          owner_name=owner_name,
                                          branch_name=branch_name,
                                          build_id=build_id)
    return log_link


def print_result(app_name, owner_name, res):
    """print table in console"""
    print("Branch name".ljust(15),
          "Build status".ljust(15),
          "Duration".ljust(15),
          "Link to build logs".ljust(100))
    for r in res:
        branch_name = r["sourceBranch"]
        build_state = r["result"] if r["status"] == "completed" else r["status"]
        duration = "" if not "finishTime" in r else parse_date(r["finishTime"]) - parse_date(r["startTime"])
        link = get_log_link(app_name, owner_name, branch_name=branch_name, build_id=r["id"])
        print(branch_name.ljust(15), build_state.ljust(15), str(duration).ljust(15), link.ljust(100))


def add_new_config(app_name, owner_name, token, branch_name, config_file="./build_config.json"):
    """adding new config to build"""
    HEADERS = {
        "accept": "application/json",
        "X-API-Token": token
    }
    url = _url(paths["add_build_config"].format(app_name=app_name,
                                                owner_name=owner_name,
                                                branch=branch_name))
    config = get_build_config(config_file=config_file)
    resp = requests.post(url=url, json=config, headers=HEADERS)
    return resp


def change_config(app_name, owner_name, token, branch_name, config_file="./build_config.json"):
    """if config exist you can change it"""
    HEADERS = {
        "accept": "application/json",
        "X-API-Token": token
    }
    url = _url(paths["add_build_config"].format(app_name=app_name,
                                                owner_name=owner_name,
                                                branch=branch_name))
    config = get_build_config(config_file=config_file)
    resp = requests.put(url=url, json=config, headers=HEADERS)
    return resp


def start_build(app_name, owner_name, token, branch_name):
    """start build of branch"""

    HEADERS = {
        "accept": "application/json",
        "X-API-Token": token
    }
    url = _url(paths["create_build"].format(app_name=app_name,
                                            owner_name=owner_name,
                                            branch=branch_name))
    res = requests.post(url, headers=HEADERS)
    if res.status_code == 200:
        data = res.json()
        print("Build No {buildNumber} of branch {sourceBranch} added".format(
            buildNumber=data["buildNumber"],
            sourceBranch=data["sourceBranch"]))
    else:
        print(res.content)

# ================= cli using click lib ==================================
@click.group()
def main():
    """
    A simple script that creates a new config and starts the build of all branches.
    If the config is empty then it sends new config from the file build_config.json
    exepmples
    python appcenter_builds.py print --app_name {app name} --owner_name {account name} --token {your full access token}
    python appcenter_builds.py print --app_name {app name} --owner_name {account name} \
    --token {your full access token} --config_file {path to config file}
    """
    pass


@click.command(name="print")
@click.option("--token", help="token with full access")
@click.option("--app_name", help="app name")
@click.option("--owner_name", help="owner name")
def print_builds_result(app_name, owner_name, token):
    builds = get_last_build_of_branches(app_name=app_name, owner_name=owner_name, token=token)
    print_result(app_name, owner_name, builds)


@click.command(name="start_build")
@click.option("--token", help="token with full access")
@click.option("--app_name", help="app name")
@click.option("--owner_name", help="owner name")
@click.option("--config_file", help="json build config file")
def start_build_all(token, app_name, owner_name, config_file):
    for b in get_branches(app_name=app_name, owner_name=owner_name, token=token):
        branch_name = b["branch"]["name"]
        if not b["configured"]:
            add_new_config(app_name=app_name,
                           owner_name=owner_name,
                           token=token,
                           branch_name=branch_name,
                           config_file=config_file)
        start_build(app_name=app_name, owner_name=owner_name, token=token, branch_name=branch_name)

    print('for view result start this script with command "print"')


main.add_command(print_builds_result)
main.add_command(start_build_all)
if __name__ == "__main__":
    main()
