import os
import subprocess
from setuptools import setup, find_packages


setup(
    name="common_analysis_ssdeep",
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'common_analysis_base',
        'common_helper_files'
    ]
)
