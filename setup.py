from setuptools import setup, find_packages

setup(
    name="pyworld",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pytest>=8.3.4",
    ],
    python_requires=">=3.8",
) 