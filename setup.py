from setuptools import setup, find_packages
from PyWeChatSpy import __version__

with open("README.md", "r", encoding="utf8") as rf:
    readme = rf.read()

setup(
    name="PyWeChatSpy",
    version=__version__,
    packages=find_packages(),
    package_data={
        "PyWeChatSpy": [
            "SpyK.exe",
            "1660944441/WeChatSpy3.0.dll",
            "proto/*"
        ]
    },
    python_requires='>=3.8.0',
    install_requires=[
        "protobuf==3.11.3",
        "requests",
        "lxml"
    ],
    author="veikai",
    author_email="veikai@126.com",
    description="A spy program that helps people make better use of WeChat",
    long_description=readme,
    long_description_content_type="text/markdown",
    url='https://github.com/veikai/PyWeChatSpy.git',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
    ]
)
