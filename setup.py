from setuptools import setup, find_packages

setup(
    name="benchtop",
    version="0.0.1",
    url="https://github.com/sbillaudelle/benchtop",
    author="Sebastian Billaudelle",
    author_email="sebastian@ini.uzh.ch",
    description="A collection of wrappers for PyVISA-compatible lab equipment",
    packages=find_packages(),    
    install_requires=["numpy >= 1.11.1", "pyvisa >= 1.11"],
)
