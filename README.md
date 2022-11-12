# Pronit
Pronit (**pro**ject i**nit**) is a tool that helps you speed up your development process by automating the initialization of new projects.

It will:
- create a local repository
- create a GitHub repository using the GitHub API
- add a `README.md` file with the project name and description
- add `.gitignore` templates for languages / environments you use
- add a `LICENSE` of you choice
- commit and push files with a custom commit message

## Installing
1. Install Python 3.7 (or newer)
2. Install Git 2.33 (or newer)
3. You might need to install [pipx](https://github.com/pypa/pipx#install-pipx)
4. Install Pronit
```
git clone https://github.com/jmaen/pronit
cd pronit
pipx install .
```

## Usage
```
pronit [-m | --minimal] [-e | --extended]
```

- Without any options, Pronit will ask for name, description, visibility and languages / environments to include in the `.gitignore`.
- `--minimal`:
The bare minimum to get your project up and running as fast as possible. Only asks for name and visibility.
- `--extended`:
Includes everything from the default option, plus selection of a license and custom commit message.
