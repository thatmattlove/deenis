from distutils.core import setup

import sys
import shutil

if sys.version_info < (3, 6):
    sys.exit("Python 3.6+ is required.")

shutil.copyfile("bin/deenis.py", "bin/deenis")

with open("README.md", "r") as ld:
    long_description = ld.read()

setup(
    name="Deenis",
    version="0.0.1",
    author="Matt Love",
    author_email="matt@allroads.io",
    description="A Python 3 DNS Module & CLI Tool to Automate Boring DNS Tasks",
    url="https://github.com/checktheroads/deenis",
    python_requires=">=3.6.2",
    packages=["deenis"],
    install_requires=[
        "click>=6.7",
        "diskcache>=3.1.1",
        "logzero>=1.5.0",
        "requests>=2.21.0",
        "toml>=0.10.0",
    ],
    license="Do What The F*ck You Want To Public License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=["bin/deenis"],
)
