from setuptools import setup, find_packages

setup(
    name='django-helios',
    version='0.0.6',
    url='https://github.com/AndrewIngram/django-helios',
    description="Opinionated Solr-based search for Django",
    long_description=open('README.rst', 'r').read(),
    license="MIT",
    author="Andrew Ingram",
    author_email="andy@andrewingram.net",
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python']
)
