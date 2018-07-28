import os

from setuptools import setup, find_packages

from grepmx import __version__


readme_path = os.path.join(os.path.dirname(__file__), "README.rst")
with open(readme_path) as fp:
    long_description = fp.read()

setup(
    name='grepmx',
    version=__version__,
    url='https://github.com/JohnDoee/grepmx',
    author='Anders Jensen',
    author_email='johndoee@tidalstream.org',
    description='Grep lines from files based on found MX',
    license='MIT',
    packages=find_packages(),
    install_requires=['dnspython'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
   ],
    entry_points={ 'console_scripts': [
        'grepmx = grepmx.__main__:main',
    ]},
)
