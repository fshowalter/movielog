from setuptools import setup

setup(
    name="movielog",
    version="1.0",
    packages=["movielog", "movielog.cli"],
    entry_points={"console_scripts": ["movielog = movielog.cli.main:prompt"]},
)
