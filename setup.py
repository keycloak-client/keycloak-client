# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='keycloak',
    version='1.3.0',
    description='Keycloak client',
    long_description='Client application to interact with Keycloak server',
    url='https://github.com/akhilputhiry/keycloak-client',
    author='Akhil Lawrence',
    author_email='akhilputhiry@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3.6'
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'cryptography==2.6.1',
        'pyjwt==1.7.1',
        'requests==2.21.0',
    ],
)
