import os
from numpy.distutils.core import setup, Extension

setup(
    name = "brushcutter",
    version = "1.0",
    author = "Raphael Dussin",
    author_email = "raphael.dussin@gmail.com",
    description = ("A package to create boundary conditions for MOM6 " ),
    license = "GPLv3",
    keywords = "ocean boundary conditions",
    url = "",
    packages=['brushcutter']
)


