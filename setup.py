from setuptools import find_packages, setup

setup(
    name="movielog",
    version="1.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["movielog = movielog.cli.__main__.:main"]},
)
