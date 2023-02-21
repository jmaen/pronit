import argparse
from enum import Enum
import json
import os
import pkgutil
from prompt_toolkit import print_formatted_text as print, prompt, HTML
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
import requests
import subprocess


class Mode(Enum):
    DEFAULT, MINIMAL, EXTENDED = range(3)


STYLE = Style.from_dict({
    "highlight": "bold",
    "success": "ansigreen bold",
    "error": "ansired bold",
    "url": "underline"
})
INPUT = "<highlight>></highlight>"


def load_token():
    # load token from user directory
    pronit_directory = f"{os.path.expanduser('~')}/.pronit"
    if os.path.isdir(pronit_directory):
        if os.path.isfile(f"{pronit_directory}/token"):
            with open(f"{pronit_directory}/token", "r") as f:
                return f.read()


def save_token(token):
    # save token in user directory
    pronit_directory = f"{os.path.expanduser('~')}/.pronit"
    if os.path.isdir(pronit_directory):
        with open(f"{pronit_directory}/token", "w+") as f:
            f.write(token)
    else:
        os.mkdir(pronit_directory)
        with open(f"{pronit_directory}/token", "w+") as f:
            f.write(token)


def check_user(token):
    authorization = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://api.github.com/user", headers=authorization)
    if response.status_code == 200:
        return response.json()["login"]


def create_project(token, name, description, private):
    description = description or ""

    # create project directory
    project_directory = f"{os.getcwd()}/{name}"
    if os.path.isdir(project_directory):
        print(HTML("<error>This project already exists</error>"), style=STYLE)
        exit()
    os.mkdir(project_directory)
    os.chdir(project_directory)
    with open("README.md", "w+") as f:
        f.write(f"# {name}\n")
        f.write(description)

    # create GitHub repository
    authorization = {"Authorization": f"Bearer {token}"}
    data = {"name": name, "description": description, "private": private}
    response = requests.post(
        "https://api.github.com/user/repos", headers=authorization, json=data
    )
    if response.status_code == 201:
        print(HTML("<success>GitHub repository has been created</success>"), style=STYLE)
    else:
        print(HTML("<error>Failed to create GitHub repository</error>"), style=STYLE)
        exit()


def load_gitignores():
    data = pkgutil.get_data(__name__, "data/gitignores.json")
    return json.loads(data.decode())


def add_gitignores(keys, gitignores):
    for key in keys:
        if key.lower() in gitignores.keys():
            response = requests.get(
                f"https://raw.githubusercontent.com/github/gitignore/main/{gitignores[key.lower()]}"
            )
            if response.status_code == 200:
                gitignore = response.text
                with open(".gitignore", "a+") as f:
                    f.write(f"{gitignore}\n")


def add_license(index):
    if 0 <= index <= 4:
        licenses = ["mit", "apache-2.0", "gpl-3.0", "bsd-3-clause", "unlicense"]
        response = requests.get(f"https://api.github.com/licenses/{licenses[index]}")
        if response.status_code == 200:
            license_text = response.json()["body"]
            with open("LICENSE", "w") as f:
                f.write(license_text)


def initialize_project(name, username, message):
    message = message or "Initial commit"

    # initialize git
    result = subprocess.run("git init -q".split())
    check_result(result, "Failed to initialize local repository")
    result = subprocess.run(
        f"git remote add origin https://github.com/{username}/{name}.git".split()
    )
    check_result(result, "Failed to add remote")

    # add, commit and push files
    result = subprocess.run("git add .".split())
    check_result(result, "Failed to add files")
    result = subprocess.run(["git", "commit", "-m", message, "-q"])
    check_result(result, "Failed to commit files")
    result = subprocess.run(
        "git config --get init.defaultBranch".split(), capture_output=True, text=True
    )
    check_result(result, "Failed to get default branch from config")
    result = subprocess.run(f"git push -u origin {result.stdout} -q".split())
    check_result(result, "Failed to push files to remote")

    print(
        HTML(f"<success>{name} has been successfully initialized. "
        f"It is now live on <url>https://github.com/{username}/{name}</url></success>"),
        style=STYLE
    )


def open_project():
    result = subprocess.run("code .".split(), shell=True)
    check_result(
        result,
        "Failed to open project with Visual Studio Code. Is it correctly installed?",
    )


def check_result(result, message):
    if result.returncode != 0:
        print(HTML(f"<error>{message}</error>"), style=STYLE)
        exit()


def main():
    # parse arguments
    parser = argparse.ArgumentParser(
        prog="pronit", description="A tool that automates project initialization"
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-m", "--minimal", action="store_true", help="run Pronit in minimal mode"
    )
    mode_group.add_argument(
        "-e", "--extended", action="store_true", help="run Pronit in extended mode"
    )
    parser.add_argument(
        "-c",
        "--code",
        action="store_true",
        help="open the project in Visual Studio Code",
    )
    args = vars(parser.parse_args())

    # set mode
    mode = Mode.DEFAULT
    if args["minimal"]:
        mode = Mode.MINIMAL
    elif args["extended"]:
        mode = Mode.EXTENDED

    # get GitHub access token
    token = load_token()
    if not token:
        token = prompt(
            HTML(f"Please enter your GitHub access token\n{INPUT} "),
            style=STYLE
        )
        while not check_user(token):
            token = prompt(
                HTML(f"That token is invalid. Please enter your GitHub access token\n{INPUT} "),
                style=STYLE
            )
    username = check_user(token)

    # confirm token
    token_check = prompt(
        HTML(f"You are registered as <highlight>{username}</highlight>. "
        f"Do you want to change your GitHub access token? (y/n)\n{INPUT} "),
        style=STYLE
    )
    if token_check in ["y", "yes"]:
        token = prompt(
            HTML(f"Please enter your GitHub access token\n{INPUT} "),
            style=STYLE
        )
        username = check_user(token)
        while not username:
            token = prompt(
                HTML(f"That token is invalid. Please enter your GitHub access token\n{INPUT} "),
                style=STYLE
            )
            username = check_user(token)

    # create project
    name = prompt(HTML(f"Please enter the project name\n{INPUT} "), style=STYLE)
    name = "".join(name.split())
    while not name:
        name = prompt(
            HTML(f"Project name can not be empty. Please enter the project name\n{INPUT} "),
            style=STYLE
        )
        name = "".join(name.split())
    description = None
    if mode != Mode.MINIMAL:
        description = prompt(HTML(f"Please enter a project description\n{INPUT} "), style=STYLE)
    private_check = prompt(HTML(f"Should the project be private? (y/n)\n{INPUT} "), style=STYLE)
    create_project(token, name, description, private_check in ["y", "yes"])

    # add gitignores
    if mode != Mode.MINIMAL:
        gitignores = load_gitignores()
        keys = prompt(
            HTML("Please enter the names of all languages or platforms "
            f"you want to apply to the .gitignore (comma separated)\n{INPUT} "),
            completer=WordCompleter(gitignores.keys()),
            style=STYLE
        )
        keys = keys.replace(" ", "").split(",")
        add_gitignores(keys, gitignores)

    # add license
    if mode == Mode.EXTENDED:
        index = prompt(
            HTML("Please enter a number corresponding to your license of choice: "
            "[0 - MIT, 1 - Apache 2.0, 2 - GNU GPLv3, 3 - BSD 3-Clause, 4 - Unlicense]. "
            f"For help choosing a license see <url>https://choosealicense.com</url>\n{INPUT} "),
            style=STYLE
        )
        if index in ["0", "1", "2", "3", "4"]:
            add_license(int(index))

    # initialize project
    message = None
    if mode == Mode.EXTENDED:
        message = prompt(HTML(f"Please enter a commit message\n{INPUT} "), style=STYLE)
    initialize_project(name, username, message)

    # open Visual Studio Code
    if args["code"]:
        open_project()
