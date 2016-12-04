
import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

packages = {
	'algolib': 'algolib/',
}

setup(
    name = "algolib",
    version = "0.0.1",
    author = "Artem Fokin",
    author_email = "ar.fokin@gmail.com",
    description = ("Implementation of various algorithms."),
    license = "MIT",
    keywords = "algorithm",
    packages=packages,
    package_dirs=packages,
    long_description=read('README'),
)
