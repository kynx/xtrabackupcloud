"""Backup MySQL to the cloud
"""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="xtrabackupcloud",
    version="0.0.1",
    description="Backup MySQL to cloud-based object storage",
    long_description=long_description,
    url="http://github.com/kynx/xtrabackupcloud",
    author="Matt Kynaston",
    author_email="mattkyn@gmail.com",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Database Administrators',
        'Topic :: Database',
        'Topic :: System :: Archiving :: Backup',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    keywords="mysql mariadb percona database backup xtrabackup",
    extra_require={
        'rackspace': ['pyrax']
    },
    entry_points={
        'console_scripts': [
            'xtrabackupcloud=xtrabackupcloud:main'
        ]
    }
)
