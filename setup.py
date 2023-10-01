from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='goodgit',
    version='0.1.2',
    packages=find_packages(),
    description = 'Git; for humans',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author = 'Shubham Gupta • Saket Gupta',
    author_email = 'shubhastro2@gmail.com',
    install_requires=[
            'requests',
            'GitPython',
            'questionary',
            'rich',
        ],
)