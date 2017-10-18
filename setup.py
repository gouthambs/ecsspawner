import re
import os
from distutils.core import setup
from setuptools import find_packages
import ast

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open(pjoin(here, 'ecsspawner', '__init__.py'),'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

with open('./requirements.txt') as test_reqs_txt:
    requirements = list(iter(test_reqs_txt))

long_description = open('README.rst').read()


setup(
    name='ecsspawner',
    version=version,
    long_description=long_description,
    description="""
                ECSSpawner: A spawner for JupyterHub that uses Amazon ECS service
                """,
    url='https://github.com/gouthambs/ecsspawner',
    # Author details
    author='Goutham Balaraman',
    author_email='gouthaman.balaraman@gmail.com',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['Interactive', 'Interpreter', 'Shell', 'Web'],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=requirements,
    extras_require={},
)