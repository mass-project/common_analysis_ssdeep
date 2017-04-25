import os
import subprocess
from setuptools import setup, find_packages
from common_analysis_ssdeep import __version__


setup(
    name="common_analysis_ssdeep",
    version=__version__,
    packages=find_packages(),
    install_requires=[
        'common_analysis_base',
        'common_helper_files'
    ]
)
