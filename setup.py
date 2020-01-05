from codecs import open
from os import path

from setuptools import setup

# Get the long description from the README
with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='etsyterms',
    version='0.1.0',
    description='Analyze the top terms used by Etsy shops',
    long_description=long_description,
    author='Chris Campo',
    author_email='ccampo.progs@gmail.com',
    install_requires=[
        'requests==2.22.0',
        'scikit-learn==0.22',
        'backoff==1.10.0',
        'tabulate==0.8.6'
    ],
    packages=['etsyterms'],
    entry_points={
        'console_scripts': ['etsyterms=etsyterms.cli:main']
    },
)
