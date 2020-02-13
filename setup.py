import setuptools

with open("Pypi.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="distinctiveness",
    version="0.0.10",
    author="Andrea Fronzetti Colladon",
    author_email="a@andreafc.com",
    description="A Python package to calculate Distinctiveness Centrality",
    long_description=long_description,
    license="MIT",
    long_description_content_type="text/markdown",
    url="https://github.com/iandreafc/distinctiveness",
    packages=setuptools.find_packages(),
    install_requires=['networkx', 'numpy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)