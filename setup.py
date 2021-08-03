import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytranslationstage", # Replace with your own username
    version="1.1.0",
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
    install_requires=[
        "pyvisa>=1.11",
        #"pyside2>=5.14.1", #toggle if you want to use pyside2 instead of PyQt5
        "PyQt5>=5.12.3",
        "numpy>=1.18.1",
        "pyvisa-py>=0.5.0",
        "pyserial>=3.5",
    ],
    entry_points={
        "console_scripts":[ "TranslationStageGUI = pytranslationstage.main_simple_TS_gui:main", "WedgeTranslationGUI = pytranslationstage.main_wedge_gui:main" ]
    },

    python_requires='>=3.6',
)
