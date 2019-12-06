import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="distinctivenesscentrality",
    version="0.0.1",
    author="Andrea Fronzetti Colladon",
    author_email="andrea.fronzetticolladon@unipg.it",
    description="A Python package to calculate Distinctiveness Centrality in networks",
    long_description=long_description,
    license="MIT",
    long_description_content_type="text/markdown",
    url="https://github.com/iandreafc/distinctiveness-centrality",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)