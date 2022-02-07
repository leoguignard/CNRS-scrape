from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='CNRS-scholar-scrape',
    version='0.1',
    description='A small script to kind of scrape CNRS applicants from Google Scholar',
    long_description=long_description,
    url='https://github.com/leoguignard/CNRS-results',
    author='Leo Guignard',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=['scholarly', 'pandas', 'jupyter', 'seaborn', 'matplotlib'],
)
