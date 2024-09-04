from setuptools import setup, find_packages

setup(
    name='2gpt',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,  # Ensure package data (like config.json) is included
    package_data={
        'twogpt': ['config.json'],  # Specify that config.json is included in the twogpt package
    },
    install_requires=[],  # Add any dependencies here
    entry_points={
        'console_scripts': [
            '2gpt=twogpt.core:main',  # Adds `2gpt` command to the CLI
        ],
    },
    author='krausality',
    author_email='krausality42@gmail.com',
    description='A CLI tool for generating an `allfiles.txt` report of a directory, with inclusion and exclusion rules managed through a `.gptignore` file and a centralized config.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/krausality/2gpt',  # Update this if hosting the package
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.9',
)
