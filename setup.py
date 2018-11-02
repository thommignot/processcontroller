from setuptools import setup
import os


# Utility function to read the README file.
# Used for the long_description. It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSION = '0.0.1'


setup(
    name='processcontroller',
    version=VERSION if '@' not in VERSION else 'dev',
    description='Replacement for pexpect',
    author='Thomas Mignot',
    author_email='tmig@yourlabs.org',
    url='https://github.com/thommignot/processcontroller',
    packages=['processcontroller'],
    include_package_data=True,
    long_description=read('README.rst'),
    license='MIT',
    keywords='pexpect subprocess',
    python_requires='>=3',
)
