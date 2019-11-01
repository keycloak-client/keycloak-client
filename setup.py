# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


# extras
docs = ["sphinx", "sphinx_rtd_theme"]
extensions = ["flask", "starlette", "django"]
complete = docs + extensions


setup(
    use_scm_version={
        "version_scheme": "post-release",
        "local_scheme": "node-and-timestamp",
    },
    extras_require={"complete": complete, "docs": docs, "extensions": extensions},
)
