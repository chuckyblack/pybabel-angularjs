# coding=utf-8

from setuptools import setup, find_packages

setup(
    name="pybabel-angularjs",
    version="1.3.5",
    author="Jaromír Pufler",
    author_email="jaromir.pufler@gmail.com",
    url="https://github.com/chuckyblack/pybabel-angularjs",
    description="An AngularJS extractor for Babel",
    long_description=open('README.md').read(),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=['babel', 'beautifulsoup4'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'babel.extractors': [
            'angularjs=pybabel_angularjs.extractor:extract_angularjs',
        ],
    },
    license="Apache Software License",
    keywords="angularjs gettext babel i18n translate",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Internationalization",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
)
