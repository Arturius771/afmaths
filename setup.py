from pathlib import Path
from setuptools import setup, find_packages

setup(
    name="afmaths",
    version="2.1.0",
    package_dir={"": "lib"},
    packages=find_packages(where="lib"),
    author="Artur Foden",
    description="A suite of mathematical functions",
    long_description=Path("readme.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/Arturius771/afmaths",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.12",
    install_requires=[
        "astronomy_types>=2.1.0",
    ],
)
