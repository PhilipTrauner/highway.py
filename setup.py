import os
from setuptools import setup, find_packages
from sys import version_info


description = "Asynchronous, route based, and data type preserving network protocol."


setup(
	name="highway.py",
	version="0.1",
	author="Philip Trauner",
	author_email="philip.trauner@aol.com",
	url="https://github.com/PhilipTrauner/highway.py",
	packages=find_packages(),
	description=description,
	install_requires=["ws4py"],
	license="MIT",
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Programming Language :: Python :: 3.4",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
	],
	keywords=["networking", "asynchronous", "data type preserving"]
)
