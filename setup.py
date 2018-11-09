from setuptools import setup


setup(
    name='processcontroller',
    versioning='distance',
    setup_requires='setupmeta',
    url='https://yourlabs.io/oss/processcontroller',
    description='Alternative pexpect for linux and python3',
    author='Thomas Mignot',
    author_email='tmig@yourlabs.org',
    license='MIT',
    keywords='pexpect subprocess',
    python_requires='>=3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
    ],
)
