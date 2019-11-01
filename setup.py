# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


docs = ["sphinx", "sphinx_rtd_theme"]
extensions = ["flask", "starlette", "djanog"]
complete = docs + extensions


setup(
    use_scm_version={
        "version_scheme": "post-release",
        "local_scheme": "node-and-timestamp",
    },
    extra_requires={"docs": docs, "extensions": extensions, "complete": complete},
)
