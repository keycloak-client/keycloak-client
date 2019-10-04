# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    use_scm_version={
        "version_scheme": "post-release",
        "local_scheme": "node-and-timestamp",
    }
)
