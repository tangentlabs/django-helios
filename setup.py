from setuptools import setup

setup(
    name='django-helios',
    version='0.0.1',
    url='https://github.com/AndrewIngram/django-helios',
    description="Opinionated Solr-based search for Django",
    long_description=open('README.rst', 'r').read(),
    license="MIT",
    author="Andrew Ingram",
    author_email="andy@andrewingram.net",
    packages=['helios'],
    package_dir={'': '.'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python']
)