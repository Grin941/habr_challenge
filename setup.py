from setuptools import setup, find_packages

__version__ = '0.1.0'


setup(
    name='Habrahabr challenge',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    version=__version__,

    description='Print 3 most popular nouns from Habr feed article titles.',
    url='https://github.com/Grin941/habr_challenge',
    licence='MIT',
    author='Grinenko Alexander',
    author_email='labamifi@gmail.com',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
)
