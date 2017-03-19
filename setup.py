from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']


setup(
    name='Mopidy-WebLibrary',
    version=get_version('mopidy_weblibrary/__init__.py'),
    url='https://github.com/fbarresi/Mopidy-WebLibrary',
    license='Apache License, Version 2.0',
    author='Federico Barresi',
    author_email='fede.barresi@gmail.com',
    description='Mopidy extension for editing the music library in a web interface',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 1.1.0',
    ],
    entry_points={
        'mopidy.ext': [
            'weblibrary = mopidy_weblibrary:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
