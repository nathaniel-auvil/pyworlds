from setuptools import setup, find_packages

setup(
    name="pyworlds",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "tkinter",
        "Pillow"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 