from setuptools import setup
import os

def package_files(directory):
	paths = []
	for path, directories, file_names in os.walk(directory):
		for filename in file_names:
			paths.append(os.path.join('..', path, filename))
	return paths

extra_files = package_files('sheetclient')

setup(
	name='sheetclient',
	version='1.0',
	packages=['sheetclient'],
	package_data={'': extra_files},
	dependency_links=[
		'https://github.com/guldfisk/secretresources/tarball/master#egg=secretresources-1.0',
	],
	install_requires=[
		'secretresources',
		'requests',
		'apiclient',
		'oauth2client',
		'httplib2',
	]
)
