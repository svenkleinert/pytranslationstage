import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytranslationstage", # Replace with your own username
    version="0.0.1",
    author="Sven Kleinert",
    author_email="kleinert@iqo.uni-hannover.de",
    description="python translation stage library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.iqo.uni-hannover.de/morgner/pytranslationstage",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
