import argparse
from enum import Enum
import os
import requests
import subprocess

from .gitignores import gitignores as gi


class Mode(Enum):
    DEFAULT, MINIMAL, EXTENDED = range(3)


FORMAT = {
    "highlight": "\033[1m",
    "end": "\033[0m",
    "success": "\033[32;1m",
    "error": "\033[31;1m",
    "url": "\033[4m"
}


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
        return response.json()['login']


def create_project(token, name, description, private):
    description = description or ""

    # create project directory
    project_directory = f"{os.getcwd()}/{name}"
    if os.path.isdir(project_directory):
        print(f"{FORMAT['error']}This project already exists{FORMAT['end']}")
        exit()
    os.mkdir(project_directory)
    os.chdir(project_directory)
    with open("README.md", "w+") as f:
        f.write(f"# {name}\n")
        f.write(description)

    # create GitHub repository
    authorization = {"Authorization": f"Bearer {token}"}
    data = {
        "name": name,
        "description": description,
        "private": private
    }
    response = requests.post("https://api.github.com/user/repos", headers=authorization, json=data)
    if response.status_code == 201:
        print(f"{FORMAT['success']}Github repository has been created{FORMAT['end']}")
    else:
        print(f"{FORMAT['error']}Failed to create GitHub repository{FORMAT['end']}")
        exit()


def add_gitignores(keys):
    for key in keys:
        if key.lower() in gi.keys():
            response = requests.get(f"https://raw.githubusercontent.com/github/gitignore/main/{gi[key.lower()]}")
            if response.status_code == 200:
                gitignore = response.text
                with open(".gitignore", "a+") as f:
                    f.write(f"{gitignore}\n")


def add_license(index):
    if 0 <= index <= 2:
        licenses = ["mit", "apache-2.0", "gpl-3.0"]
        response = requests.get(f"https://api.github.com/licenses/{licenses[index]}")
        if response.status_code == 200:
            license_text = response.json()['body']          
            with open("LICENSE", "w") as f:
                f.write(license_text)


def initialize_project(name, username, message):
    message = message or "Initial commit"

    # initialize git
    result = subprocess.run("git init -q".split())
    check_result(result, "Failed to initialize local repository")
    result = subprocess.run(f"git remote add origin https://github.com/{username}/{name}.git".split())
    check_result(result, "Failed to add remote")

    # add, commit and push files
    result = subprocess.run("git add .".split())
    check_result(result, "Failed to add files")
    result = subprocess.run(["git", "commit", "-m", message, "-q"])
    check_result(result, "Failed to commit files")
    result = subprocess.run("git config --get init.defaultBranch".split(), capture_output=True, text=True)
    check_result(result, "Failed to get default branch from config")
    result = subprocess.run(f"git push -u origin {result.stdout} -q".split())
    check_result(result, "Failed to push files to remote")

    print(f"{FORMAT['success']}{FORMAT['highlight']}{name}{FORMAT['end']}{FORMAT['success']} "
          "has been successfully initialized. "
          f"It is now live on {FORMAT['url']}https://github.com/{username}/{name}{FORMAT['end']}")


def open_project():
    result = subprocess.run("code .".split(), shell=True)
    check_result(result, "Failed to open project with Visual Studio Code. Is it correctly installed?")


def check_result(result, message):
    if result.returncode != 0:
        print(f"{FORMAT['error']}{message}{FORMAT['end']}")
        exit()


def main():
    # parse arguments
    parser = argparse.ArgumentParser(
        prog="pronit",
        description="A tool that automates project initialization"
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("-m", "--minimal", action="store_true", help="run Pronit in minimal mode")
    mode_group.add_argument("-e", "--extended", action="store_true", help="run Pronit in extended mode")
    parser.add_argument("-c", "--code", action="store_true", help="open the project in Visual Studio Code")
    args = vars(parser.parse_args())

    # set mode
    mode = Mode.DEFAULT
    if args['minimal']:
        mode = Mode.MINIMAL
    elif args['extended']:
        mode = Mode.EXTENDED

    # get GitHub access token
    token = load_token()
    if not token:
        token = input(f"Please enter your GitHub access token\n{FORMAT['highlight']}>{FORMAT['end']} ")
        while not check_user(token):
            token = input(f"That token is invalid. Please enter your GitHub access token\n{FORMAT['highlight']}>{FORMAT['end']} ")
    username = check_user(token)

    # confirm token
    token_check = input(f"You are registered as {FORMAT['highlight']}{username}{FORMAT['end']}. "
                        f"Do you want to change your GitHub access token? (y/n)\n{FORMAT['highlight']}>{FORMAT['end']} ")
    if token_check in ["y", "yes"]:
        token = input(f"Please enter your GitHub access token\n{FORMAT['highlight']}>{FORMAT['end']} ")
        username = check_user(token)
        while not username:
            token = input(f"That token is invalid. Please enter your GitHub access token\n{FORMAT['highlight']}>{FORMAT['end']} ")
            username = check_user(token)

    # create project
    name = input(f"Please enter the project name\n{FORMAT['highlight']}>{FORMAT['end']} ")
    name = "".join(name.split())
    while not name:
        name = input(f"Project name can not be empty. "
                             "Please enter the project name\n{FORMAT['highlight']}>{FORMAT['end']} ")
        name = "".join(name.split())
    description = None
    if mode != Mode.MINIMAL:
        description = input(f"Please enter a project description\n{FORMAT['highlight']}>{FORMAT['end']} ")
    private_check = input(f"Should the project be private? (y/n)\n{FORMAT['highlight']}>{FORMAT['end']} ")
    create_project(token, name, description, private_check in ["y", "yes"])

    # add gitignores
    if mode != Mode.MINIMAL:
        keys = \
        input("Please enter the names of all languages or platforms "
              f"you want to apply to the .gitignore (comma separated)\n{FORMAT['highlight']}>{FORMAT['end']} ")
        keys = keys.replace(" ", "").split(",")
        add_gitignores(keys)

    # add license
    if mode == Mode.EXTENDED:
        index = input("Please enter a number corresponding to your license of choice: "
                            "[0 - MIT, 1 - Apache 2.0, 2 - GNU GPLv3, 3 - None]. "
                            f"For help choosing a license see {FORMAT['url']}https://choosealicense.com{FORMAT['end']}"
                            f"\n{FORMAT['highlight']}>{FORMAT['end']} ")
        add_license(int(index))

    # initialize project
    message = None
    if mode == Mode.EXTENDED:
        message = input(f"Please enter a commit message\n{FORMAT['highlight']}>{FORMAT['end']} ")
    initialize_project(name, username, message)

    # open Visual Studio Code
    if args['code']:
        open_project()
