import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name="mailnotify",
    version="0.0.1",
    url="https://github.com/sumnerevans/mailnotify",
    description="A small program that notifies when mail has arrived in ~/Mail",
    author="Sumner Evans",
    author_email="inquiries@sumnerevans.com",
    license="GPL3",
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: End Users/Desktop",
        "Operating System :: POSIX",
        "Topic :: Communications :: Email :: Mail Transport Agents",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.8",
    ],
    keywords="email notify",
    packages=["mailnotify"],
    install_requires=["watchdog", "PyGObject"],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and
    # allow pip to create the appropriate form of executable for the target
    # platform.
    entry_points={"console_scripts": ["mailnotify=mailnotify.__main__:main"]},
)
