from setuptools import setup, find_packages
import pathlib
import os

here = pathlib.Path(__file__).parent.resolve()

with open(os.path.join(here, 'README.md'), 'r',encoding='UTF-8') as mdFile:
    long_description = mdFile.read()

setup(
    name='dynamic-links', 
    version='0.2.2', 
    packages=find_packages(), 
    url='https://github.com/picpic2013/dlframe-back', 
    license='MIT', 
    author='PIC', 
    author_email='picpic2019@gmail.com', 
    description='a calculation framework', 
    long_description=long_description, 
    long_description_content_type="text/markdown",
    python_requires=">=3.10, <4", 
    install_requires=[
        'websockets>=10.3', 'numpy', 'Pillow'
    ]
)
