from setuptools import setup, find_packages

__version__ = '0.1.0'


setup(
    name='Habrahabr challenge',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    version=__version__,
)
