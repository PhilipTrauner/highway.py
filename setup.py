import os
from setuptools import setup, find_packages
from sys import version_info


description = "Asynchronous, route based, and data type preserving network protocol."
long_description = """
============
highway.py
============

.. image:: https://cloud.githubusercontent.com/assets/9287847/26756438/93c1ff54-48a2-11e7-981e-37aeb7b2383c.png
   :height: 150px
   :alt: highway banner
   :align: center


**highway** is a *lightweight*, *route-based* and *data-type
preserving* network protocol framework built on top of *WebSockets*. It facilitates routes as a means of data transmission.
"""

setup(
	name="highway.py",
	version="0.2.2",
	author="Philip Trauner",
	author_email="philip.trauner@arztpraxis.io",
	url="https://github.com/PhilipTrauner/highway.py",
	packages=find_packages(),
	description=description,
	long_description=long_description,
	install_requires=[
		"websockets==3.4",
		"ujson==1.35"
	],
	license="MIT",
	classifiers=[
		"Development Status :: 4 - Beta",
		"Programming Language :: Python :: 3.6",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
	],
	keywords=["networking", "asynchronous", "data type preserving"]
)
