from setuptools import setup, find_packages
from PyWeChatSpy import __version__


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
    python_requires='>=3.5.0',
    author="veikai",
    author_email="veikai@126.com",
    description="A spy program that helps people make better use of WeChat",
    url='https://github.com/veikai/PyWeChatSpy.git',
    license="apache2",
    platforms="win32"
)
