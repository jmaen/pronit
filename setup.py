from setuptools import setup

setup(
    name="Pronit",
    description="A tool that automates project initialization",
    version="1.0",
    author="Jannik Mänzer",
    url="https://github.com/jmaen/pronit",
    install_requires=["requests", "prompt_toolkit"],
    packages=["pronit"],
    include_package_data=True,
    entry_points={
        "console_scripts": ["pronit=pronit.pronit:main"]
    }
)
