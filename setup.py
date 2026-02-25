#!/usr/bin/env python3
"""Setup script for SoulHub CLI"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='soulhub-cli',
    version='1.0.0',
    author='rblake2320',
    author_email='',
    description='All-in-One AI Memory & Deployment System',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/rblake2320/soulhub-cli',
    py_modules=['soulhub_cli'],
    install_requires=[
        'click>=8.0',
        'requests>=2.28',
        'tigs>=0.1.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'black>=22.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'soulhub=soulhub_cli:cli',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
)
