from distutils.core import setup

import sys
import shutil

if sys.version_info < (3, 6, 2):
    sys.exit("Python < 3.6.2 is required.")

shutil.copyfile("bin/deenis.py", "bin/deenis")

setup(
    name="Deenis",
    version="0.0.1",
    python_requires=">=3.6.2",
    packages=["deenis"],
    install_requires=[
        "click>=6.7",
        "diskcache>=3.1.1",
        "logzero>=1.5.0",
        "requests>=2.21.0",
        "toml>=0.10.0",
    ],
    license="BSD 3-Clause Clear License",
    long_description=open("README.md").read(),
    scripts=["bin/deenis"],
)
