import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="logscript",
    version="0.0.1",
    author="Matt Page",
    author_email="pagey101@hotmail.co.uk",
    description="Log event processor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pagey101/logscript",
    project_urls={
        "Bug Tracker": "https://github.com/pagey101/logscript/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires="sh"
)
