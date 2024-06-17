from setuptools import setup, find_packages

setup(
    name='picli',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests==2.31.0',
        'keyring==25.2.1'
    ],
    entry_points={
        'console_scripts': [
            'picli=picli.__main__:main',
        ],
    },
    author='William Simpson',
    description='A simple CLI tool for OSISoft\'s PI System',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/williamdoesdev/picli',
)
