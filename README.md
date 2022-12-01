# Pronit
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/jmaen/pronit/blob/master/LICENSE)
[![code style: black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)

Pronit (**pro**ject i**nit**) is a tool that helps you speed up your development process by automating the initialization of new projects.

Pronit will:
- create a local repository
- create a GitHub repository using the GitHub API
- add a `README.md` file with the project name and description
- add `.gitignore` templates for languages or platforms you use
- add a `LICENSE` of your choice
- commit and push files with a custom commit message
- open the project in Visual Studio Code

## Installing
1. Install Python 3.7 (or newer)
2. Install Git 2.33 (or newer)
3. Install [pipx](https://github.com/pypa/pipx#install-pipx)
4. Install Pronit
```
git clone https://github.com/jmaen/pronit
cd pronit
pipx install .
```

## Usage
```
pronit [-h] [-m | -e] [-c]
```

- Without any options, Pronit will ask for name, description, visibility and languages / environments to include in the `.gitignore`.
- `-h, --help`:
Display usage info.
- `-m, --minimal`:
The bare minimum to get your project up and running as fast as possible. Only asks for name and visibility.
- `-e, --extended`:
Includes everything from the default option, plus selection of a license and custom commit message.
- `-c, --code`:
Open the project in Visual Studio Code.
