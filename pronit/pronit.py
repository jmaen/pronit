import os
import requests
import subprocess
import sys

from .gitignores import gitignores as gi

BOLD = "\033[1m"
UNDERLINE = "\033[4m" 
RED = "\033[31;1m"
GREEN = "\033[32;1m"
END = "\033[0m"


class Pronit:
    token = None
    username = None
    name = None
    project_directory = None

    def __init__(self):
        self.load_token()
        if not self.token:
            self.input_token()
            return

        if not self.get_username():
            self.input_token()
            return
        
        name_check = input(f"You are registered as {BOLD}{self.username}{END}. "
                            "If that's not you or you want to change your access token "
                            f"enter {BOLD}n{END}, otherwise continue with {BOLD}y{END}\n{BOLD}>{END} ")
        if name_check not in ["y", "yes"]:
            self.input_token()

    def input_token(self):
        self.token = input(f"Please enter your GitHub access token\n{BOLD}>{END} ")
        while not self.get_username():
            self.token = input(f"That token is invalid. Please enter your GitHub access token\n{BOLD}>{END} ")

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
        response = requests.get("https://api.github.com/user", headers=authorization)
        if response.status_code == 200:
            self.username = response.json()['login']
            return True
        else:
            return False

    def create_project(self, name, description="", private=False):
        self.name = name

        # create project directory
        self.project_directory = f"{os.getcwd()}/{name}"
        if os.path.isdir(self.project_directory):
            print(f"{RED}This project already exists{END}")
            exit()
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
        response = requests.post("https://api.github.com/user/repos", headers=authorization, json=data)
        if response.status_code == 201:
            print(f"{GREEN}Github repository has been created{END}")
        else:
            print(f"{RED}Failed to create GitHub repository{END}")
            exit()

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

        print(f"{GREEN}{BOLD}{self.name}{END}{GREEN} has been successfully initialized. "
              f"It is now live on {UNDERLINE}https://github.com/{self.username}/{self.name}{END}")


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
            input("Please enter the names of all languages or platforms "
                  f"you want to apply to the .gitignore (comma separated)\n{BOLD}>{END} ")
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
            input("Please enter the names of all languages or platforms "
                  f"you want to apply to the .gitignore (comma separated)\n{BOLD}>{END} ")
        gitignore_keys = gitignore_keys.replace(" ", "").split(",")
        pronit.add_gitignores(gitignore_keys)

        # add license
        license_index = input("Please enter a number corresponding to your license of choice: "
                              "[0 - MIT, 1 - Apache 2.0, 2 - GNU GPLv3, 3 - None]. "
                              f"For help choosing a license see {UNDERLINE}https://choosealicense.com{END}\n{BOLD}>{END} ")
        pronit.add_license(int(license_index))

        # enter commit message
        message_check = \
            input("Do you want to use a randomly selected commit message "
                  f"generated by {UNDERLINE}https://whatthecommit.com{END}? (y/n)\n{BOLD}>{END} ")
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
        print("Usage: pronit [-m | --minimal] [-e | --extended]")
