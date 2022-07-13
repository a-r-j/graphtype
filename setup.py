import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read().replace("```py", "```")

setuptools.setup(
    name="graphtype",
    version="0.1.0",
    author="Arian Jamasb",
    author_email="arian@jamasb.io",
    description="Enforce graph, node and edge attribute types on NetworkX Graphs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/a-r-j/graphtype",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
    ],
)
