import setuptools

setuptools.setup(
    name="Pronit",
    description="A tool that automates project initialization",
    version="1.0",
    author="Jannik Mänzer",
    url="https://github.com/jmaen/pronit",
    install_requires=["requests"],
    entry_points={
        "console_scripts": ["pronit=pronit.pronit:main"]
    }
)
