import os
import requests
import subprocess
import sys

from .gitignores import gitignores as gi

BOLD = "\033[1m"
END = "\033[0m"


class Pronit:
    token = None
    username = None
    name = None
    project_directory = None

    def __init__(self):
        self.load_token()
        if self.token:
            self.get_username()
            name_check = input(f"Is your GitHub username {BOLD}{self.username}{END}? (y/n)\n{BOLD}>{END} ")
            if name_check not in ["y", "yes"]:
                self.input_token()
        else:
            self.input_token()

    def input_token(self):
        self.token = input(f"Please enter your GitHub access token\n{BOLD}>{END} ")
        self.get_username()

        # save token in user directory
        pronit_directory = f"{os.path.expanduser('~')}/.pronit"
        if os.path.isdir(pronit_directory):
            with open(f"{pronit_directory}/token", "w+") as f:
                f.write(self.token)
        else:
            os.mkdir(pronit_directory)
            with open(f"{pronit_directory}/token", "w+") as f:
                f.write(self.token)

    def load_token(self):
        # load token from user directory
        pronit_directory = f"{os.path.expanduser('~')}/.pronit"
        if os.path.isdir(pronit_directory):
            if os.path.isfile(f"{pronit_directory}/token"):
                with open(f"{pronit_directory}/token", "r") as f:
                    self.token = f.read()

    def get_username(self):
        authorization = {"Authorization": f"Bearer {self.token}"}
        user = requests.get("https://api.github.com/user", headers=authorization).json()
        self.username = user['login']

    def create_project(self, name, description="", private=False):
        self.name = name

        # create project directory
        self.project_directory = f"{os.getcwd()}/{name}"
        os.mkdir(self.project_directory)
        os.chdir(self.project_directory)
        with open("README.md", "w+") as f:
            f.write(f"# {name}\n")
            f.write(description)

        # create GitHub repository
        authorization = {"Authorization": f"Bearer {self.token}"}
        data = {
            "name": name,
            "description": description,
            "private": private
        }
        requests.post("https://api.github.com/user/repos", headers=authorization, json=data)

        # git init
        subprocess.run(["git", "init", "-q"])
        subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{self.username}/{name}.git"])

    @staticmethod
    def add_gitignores(keys):
        for key in keys:
            if key.lower() in gi.keys():
                gitignore = \
                    requests.get(f"https://raw.githubusercontent.com/github/gitignore/main/{gi[key.lower()]}").text
                with open(".gitignore", "a+") as f:
                    f.write(f"{gitignore}\n")

    @staticmethod
    def add_license(index):
        if 0 <= index <= 2:
            licenses = ["mit", "apache-2.0", "gpl-3.0"]
            license_text = requests.get(f"https://api.github.com/licenses/{licenses[index]}").json()['body']
            with open("LICENSE", "w") as f:
                f.write(license_text)

    def finish(self, message="Initial commit"):
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", message, "-q"])
        subprocess.run(["git", "push", "-u", "origin", "master", "-q"])

        print(f"{BOLD}{self.name}{END} has been successfully initialized. "
              f"It is now live on https://github.com/{self.username}/{self.name}")


def main():
    if len(sys.argv) < 2:
        # get access token
        pronit = Pronit()

        # create project
        project_name = input(f"Please enter the project name\n{BOLD}>{END} ")
        while not project_name:
            project_name = input(f"Project name can not be empty. Please enter the project name\n{BOLD}>{END} ")
        project_description = input(f"Please enter a project description\n{BOLD}>{END} ")
        private_check = input(f"Should the project be private? (y/n)\n{BOLD}>{END} ")
        pronit.create_project(project_name, description=project_description, private=private_check in ["y", "yes"])

        # add .gitignores
        gitignore_keys = \
            input("Please enter comma separated the names of all languages or environments "
                  f"you want to include .gitignores for\n{BOLD}>{END} ")
        gitignore_keys = gitignore_keys.replace(" ", "").split(",")
        pronit.add_gitignores(gitignore_keys)

        # commit and push
        pronit.finish()
    elif sys.argv[1] in ["-m", "--minimal"]:
        # get access token
        pronit = Pronit()

        # create project
        project_name = input(f"Please enter the project name\n{BOLD}>{END} ")
        while not project_name:
            project_name = input(f"Project name can not be empty. Please enter the project name\n{BOLD}>{END} ")
        private_check = input(f"Should the project be private? (y/n)\n{BOLD}>{END} ")
        pronit.create_project(project_name, private=private_check in ["y", "yes"])

        # commit and push
        pronit.finish()
    elif sys.argv[1] in ["-e", "--extended"]:
        # get access token
        pronit = Pronit()

        # create project
        project_name = input(f"Please enter the project name\n{BOLD}>{END} ")
        while not project_name:
            project_name = input(f"Project name can not be empty. Please enter the project name\n{BOLD}>{END} ")
        project_description = input(f"Please enter a project description\n{BOLD}>{END} ")
        private_check = input(f"Should the project be private? (y/n)\n{BOLD}>{END} ")
        pronit.create_project(project_name, description=project_description, private=private_check in ["y", "yes"])

        # add .gitignores
        gitignore_keys = \
            input("Please enter comma separated the names of all languages or environments "
                  f"you want to include .gitignores for\n{BOLD}>{END} ")
        gitignore_keys = gitignore_keys.replace(" ", "").split(",")
        pronit.add_gitignores(gitignore_keys)

        # add license
        license_index = input("Please enter a number corresponding to your license of choice: "
                              "[0 - MIT, 1 - Apache 2.0, 2 - GNU GPLv3, 3 - None].\n"
                              f"For help choosing a license see https://choosealicense.com\n{BOLD}>{END} ")
        pronit.add_license(int(license_index))

        # enter commit message
        message_check = \
            input("Do you want to use a randomly selected commit message "
                  f"generated by https://whatthecommit.com? (y/n)\n{BOLD}>{END} ")
        if message_check in ["y", "yes"]:
            commit_message = requests.get("https://whatthecommit.com/index.txt").text
        else:
            commit_message = input(f"Please enter a commit message\n{BOLD}>{END} ")

        # commit and push
        if commit_message:
            pronit.finish(commit_message)
        else:
            pronit.finish()
    else:
        print("usage: pronit [-m | --minimal] [-e | --extended]")
