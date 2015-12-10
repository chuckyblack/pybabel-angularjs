from setuptools import setup, find_packages

setup(
    name="pybabel-angularjs",
    version="0.1.0",
    author="Sebastien Fievet",
    author_email="sebastien@shore.li",
    url="https://bitbucket.org/shoreware/pybabel-angularjs",
    description="An AngularJS extractor for Babel",
    #long_description=open('README.rst').read(),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=['babel'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'babel.extractors': [
            'angularjs=pybabel_angularjs.extractor:extract_angularjs',
        ],
    },
    license="Apache Software License",
    keywords="angularjs gettext babel",
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

