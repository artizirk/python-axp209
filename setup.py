from setuptools import setup

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="axp209",
    version="0.0.2",
    author="Arti Zirk",
    author_email="arti.zirk@gmail.com",
    description="axp209 is a pure python library for getting information from AXP209 Power Management Unit",
    license="MIT",
    keywords=['sunxi', 'cubietruck', 'cubieboard', 'axp209', 'python', 'i2c', 'CHIP', 'linux'],
    url="https://github.com/artizirk/python-axp209",
    py_modules=['axp209'],
    long_description=long_description,
    install_requires=['smbus2 >= 0.1.3'],
    entry_points={'console_scripts': ['axp209 = axp209:main']},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 2',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
