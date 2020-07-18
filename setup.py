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
            "Launcher.exe",
            "1644691589/WeChatSpy.dll"
        ]
    },
    python_requires='>=3.8.0',
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
