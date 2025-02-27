from setuptools import setup, find_packages

setup(
    name="pyworlds",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "tkinter",  # Usually comes with Python
    ],
    python_requires=">=3.7",
    
    # Metadata
    author="Your Name",
    author_email="your.email@example.com",
    description="A space-based strategy game inspired by OGame and Astro Empires",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="game, strategy, space, ogame, astro-empires",
    url="https://github.com/yourusername/pyworlds",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Strategy",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
) 