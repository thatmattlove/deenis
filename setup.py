from distutils.core import setup

import sys

if sys.version_info < (3, 6, 2):
    sys.exit("Python < 3.6.2 is required.")

setup(
    name="Deenis",
    version="0.0.1",
    python_requires=">=3.6.2",
    packages=["deenis"],
    license="BSD 3-Clause Clear License",
    long_description=open("README.md").read(),
)
